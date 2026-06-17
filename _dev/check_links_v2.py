#!/usr/bin/env python3
"""
check_links_v2.py — robust link checker for miamijetskiboatrentals.com

Por qué v2 sobre check-links.py:

  - Usa GET cuando HEAD falla (algunos CDNs/WAFs solo responden a GET).
  - Reintenta 2 veces en errores transitorios (timeout, 5xx, reset).
  - Sigue redirects y reporta la URL final + status final.
  - Extrae URLs de MUCHOS más patrones:
      href, src, srcset, action, formaction, content, data-href, data-url,
      'literales en JS', url(...) en CSS, <loc> en sitemap, "link" en
      operators.json, y destinos de redirect en vercel.json.
  - Valida los destinos de los 750+ redirects de vercel.json — un redirect
    que apunta a una página borrada también es un 404.
  - Opcionalmente prueba enlaces externos (FareHarbor / Filestack) con
    una muestra aleatoria configurable.
  - Reporte categorizado: ok / redirected_ok / broken_404 / server_error /
    connection_error / redirect_loop / empty_body.
  - Sale con exit code 1 si encuentra cualquier URL rota — útil para CI.

Uso:
    python3 check_links_v2.py                     # internas + vercel + 100 externas
    python3 check_links_v2.py --workers 30        # más rápido
    python3 check_links_v2.py --no-external       # saltar enlaces externos
    python3 check_links_v2.py --external-sample 500  # más muestra externa
    python3 check_links_v2.py --out report.json   # guardar a archivo distinto
"""
from __future__ import annotations
import re, json, time, sys, argparse, random, threading
from pathlib import Path
from urllib.request import urlopen, Request, build_opener, HTTPRedirectHandler
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlparse, unquote
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import defaultdict, Counter

BASE_URL   = "https://miamijetskiboatrentals.com"
SCRIPT_DIR = Path(__file__).parent
HEADERS    = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/126.0 Safari/537.36 LinkChecker/2.0",
    "Accept":     "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}
TIMEOUT       = 12          # seconds per request
MAX_RETRIES   = 2           # retries on 5xx / connection errors
RETRY_BACKOFF = 1.0         # seconds, doubled per retry

# Excluded from external testing — they always 4xx HEAD/GET from bots
EXTERNAL_SKIP_HOSTS = {
    "www.instagram.com", "instagram.com",
    "www.facebook.com", "facebook.com",
    "www.tiktok.com",   "tiktok.com",
    "twitter.com", "x.com",
    "wa.me",
    "mailto", "tel",
}

# ════════════════════════════════════════════════════════════════════════════
#  STEP 1 — Collect every URL we should test
# ════════════════════════════════════════════════════════════════════════════

URL_FROM_HREF     = re.compile(r'href=["\']([^"\'#]+)["\']', re.I)
URL_FROM_SRC      = re.compile(r'(?:src|formaction|action|data-href|data-url|data-fh-url)=["\']([^"\'#]+)["\']', re.I)
URL_FROM_SRCSET   = re.compile(r'srcset=["\']([^"\']+)["\']', re.I)
URL_FROM_CONTENT  = re.compile(r'content=["\'](https?://[^"\']+)["\']', re.I)
URL_FROM_LOC      = re.compile(r"<loc>([^<]+)</loc>", re.I)
URL_FROM_JS_LIT   = re.compile(r'["\'](/[a-zA-Z0-9][a-zA-Z0-9\-_/\.]*?)["\']')   # JS string starting with /
URL_FROM_CSSURL   = re.compile(r'url\(["\']?([^"\')]+)["\']?\)', re.I)
URL_FROM_FH_LINK  = re.compile(r'(https?://fareharbor\.com/[^"\'\s<>]+)')


def normalize(u: str) -> str:
    """Strip fragments / trailing slash so we don't test the same URL twice."""
    u = u.split("#", 1)[0]
    if u.endswith("/") and u != "/" and not u.endswith("://"):
        u = u.rstrip("/")
    return u


def is_internal(u: str) -> bool:
    if not u.startswith("http"):
        return True   # relative path → assumed internal
    return urlparse(u).netloc in {
        "miamijetskiboatrentals.com", "www.miamijetskiboatrentals.com",
    }


def to_absolute(u: str, base: str = BASE_URL) -> str | None:
    """Resolve a possibly-relative URL to absolute. Skip unsupported schemes."""
    u = u.strip()
    if not u or u.startswith(("javascript:", "data:", "blob:")):
        return None
    if u.startswith("mailto:") or u.startswith("tel:"):
        return None
    if u.startswith("//"):
        u = "https:" + u
    if u.startswith("http"):
        return u
    if u.startswith("/"):
        return base + u
    # relative path with no leading slash — treat as same-folder
    return base + "/" + u


def collect_urls() -> dict[str, set[str]]:
    """Return {internal: set, external: set, redirect_dests: set}."""
    internal:  set[str] = set()
    external:  set[str] = set()

    # 1) Sitemap.xml — these MUST all 200
    sitemap = (SCRIPT_DIR / "sitemap.xml").read_text(errors="ignore")
    for loc in URL_FROM_LOC.findall(sitemap):
        u = to_absolute(loc)
        if u and is_internal(u):
            internal.add(normalize(u))

    # 2) slug-map.js — every slug should resolve
    slug_js = (SCRIPT_DIR / "slug-map.js").read_text(errors="ignore")
    for slug in re.findall(r'"([a-z0-9][a-z0-9\-]+)"\s*:\s*"([a-z0-9][a-z0-9\-]+)"', slug_js):
        # slug-map maps op_id -> slug; we want the slugs (right side)
        internal.add(f"{BASE_URL}/{slug[1]}")

    # 3) operators.json — every operator's external `link` field (FareHarbor URL)
    try:
        ops = json.loads((SCRIPT_DIR / "operators.json").read_text(errors="ignore"))
        for op in ops:
            link = op.get("link")
            if link and isinstance(link, str):
                u = to_absolute(link)
                if u and not is_internal(u):
                    external.add(u)
    except Exception as e:
        print(f"WARN: couldn't read operators.json: {e}", file=sys.stderr)

    # 4) Every HTML file — extract every URL pattern
    html_files = list(SCRIPT_DIR.glob("*.html"))
    print(f"Scanning {len(html_files)} HTML files for URLs…", flush=True)
    for fpath in html_files:
        try:
            html = fpath.read_text(errors="ignore")
        except Exception:
            continue
        # Extract every URL pattern
        candidates: list[str] = []
        candidates.extend(URL_FROM_HREF.findall(html))
        candidates.extend(URL_FROM_SRC.findall(html))
        for srcset in URL_FROM_SRCSET.findall(html):
            for ss in srcset.split(","):
                ss = ss.strip().split()
                if ss: candidates.append(ss[0])
        candidates.extend(URL_FROM_CONTENT.findall(html))
        candidates.extend(URL_FROM_JS_LIT.findall(html))
        candidates.extend(URL_FROM_CSSURL.findall(html))

        for c in candidates:
            u = to_absolute(c)
            if not u:
                continue
            u = normalize(u)
            host = urlparse(u).netloc
            if any(skip in host or host == skip for skip in EXTERNAL_SKIP_HOSTS):
                continue
            if is_internal(u):
                internal.add(u)
            else:
                external.add(u)

    # 5) Filter junk — drop homepage, JS template literals, weird chars
    JUNK = ('${', '<%', '{%', '__', '#{', '\\')
    # Variables JS comunes (capturadas por el regex JS_LIT como "/s", "/x", etc.)
    JS_VAR_PATHS = {
        '/s', '/u', '/x', '/y', '/i', '/j', '/k', '/n', '/m', '/e', '/t',
        '/url', '/uri', '/src', '/href', '/key', '/val', '/value', '/id',
        '/o.photo', '/op.photo', '/op.link', '/op.name', '/op.price',
        '/o.link', '/o.name', '/op.id', '/op.cat', '/o.id',
    }
    def is_real(u):
        if u == BASE_URL: return False
        if not re.match(r"^https?://", u): return False
        if any(j in u for j in JUNK): return False
        parsed = urlparse(u)
        # Excluir hosts sin path (e.g. https://cdn.filestackcontent.com)
        if not parsed.path or parsed.path == '/': return False
        # Excluir JS-literals capturados como rutas
        if parsed.path in JS_VAR_PATHS: return False
        # Excluir rutas que parecen acceso a propiedades JS (op.photo, etc.)
        # Patrón: contiene un punto seguido de letras, sin extensión real
        if '.' in parsed.path:
            # Acepta solo extensiones de archivo reales
            valid_ext = re.search(r'\.(html|htm|json|js|css|png|jpe?g|gif|svg|webp|ico|xml|txt|pdf|mp4|webm)$', parsed.path, re.I)
            if not valid_ext:
                # Si tiene punto pero no es extensión válida, asumimos JS literal
                return False
        # Path debe empezar con letra/numero (no símbolo) y contener solo chars válidos URL
        if not re.match(r'^/[a-z0-9][a-zA-Z0-9\-_/.]*$', parsed.path): return False
        return True
    internal = {u for u in internal if is_real(u)}
    external = {u for u in external if u and re.match(r"^https?://", u)
                and not any(j in u for j in JUNK)
                and urlparse(u).path not in ('', '/')}

    # 6) vercel.json redirect destinations — every destination must resolve
    redirect_dests: set[str] = set()
    try:
        cfg = json.loads((SCRIPT_DIR / "vercel.json").read_text())
        for r in cfg.get("redirects", []):
            dest = r.get("destination", "")
            if not dest or dest.startswith(("http", "//")):
                continue
            # Saltar destinos parametrizados (e.g. "/:path*") — no se pueden
            # testear sin un valor real del source, dan falso positivo /x.
            if ":" in dest:
                continue
            redirect_dests.add(BASE_URL + dest)
    except Exception as e:
        print(f"WARN: couldn't read vercel.json: {e}", file=sys.stderr)

    return {"internal": internal, "external": external, "redirect_dests": redirect_dests}


# ════════════════════════════════════════════════════════════════════════════
#  STEP 2 — Check one URL (with retries, redirect-following, GET fallback)
# ════════════════════════════════════════════════════════════════════════════

class TrackingRedirectHandler(HTTPRedirectHandler):
    """Track redirect chain so we can report it."""
    def __init__(self):
        super().__init__()
        self.chain = []

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        self.chain.append((req.full_url, code, newurl))
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def fetch(url: str, method: str = "HEAD") -> tuple[int, str | None, list, int]:
    """
    Fetch URL with method (HEAD or GET).
    Returns (status, error_msg, redirect_chain, final_status).
    """
    handler = TrackingRedirectHandler()
    opener = build_opener(handler)
    req = Request(url, headers=HEADERS, method=method)
    try:
        resp = opener.open(req, timeout=TIMEOUT)
        body_len = 0
        if method == "GET":
            try:
                body_len = len(resp.read(2048))   # peek at first 2 KB
            except Exception:
                pass
        return resp.status, None, handler.chain, body_len
    except HTTPError as e:
        return e.code, str(e.reason)[:120], handler.chain, 0
    except URLError as e:
        return 0, str(e.reason)[:120], handler.chain, 0
    except Exception as e:
        return -1, str(e)[:120], handler.chain, 0


def check_url(url: str) -> dict:
    """
    Check a URL with HEAD, fall back to GET if HEAD returns 405/501/4xx-from-bots,
    retry transient errors. Return a result dict.
    """
    last_status, last_err, last_chain = 0, None, []

    for attempt in range(MAX_RETRIES + 1):
        # Try HEAD first
        status, err, chain, _ = fetch(url, method="HEAD")

        # HEAD sometimes 405/501 even when GET works → fall back
        if status in (405, 501) or (status >= 400 and status < 600 and not chain):
            g_status, g_err, g_chain, g_body = fetch(url, method="GET")
            # Prefer GET result if it's better
            if g_status < 400 or (g_status >= 500 and g_status < 600):
                status, err, chain = g_status, g_err, g_chain
            elif g_status != status:
                status, err, chain = g_status, g_err, g_chain

        # Transient → retry
        if status in (0, -1) or (status >= 500 and status < 600):
            last_status, last_err, last_chain = status, err, chain
            time.sleep(RETRY_BACKOFF * (2 ** attempt))
            continue
        break
    else:
        status, err, chain = last_status, last_err, last_chain

    return {
        "url": url,
        "status": status,
        "error": err,
        "redirect_chain": [{"from": c[0], "status": c[1], "to": c[2]} for c in chain],
        "final_url": chain[-1][2] if chain else url,
    }


def categorize(r: dict) -> str:
    s = r["status"]
    if s in (200, 204, 206):  return "ok"
    if s in (301, 302, 303, 307, 308):  return "redirected"   # rare: redirect with no Location
    if s == 404:  return "broken_404"
    if s == 410:  return "gone_410"
    if s in (401, 403):  return "auth_required"
    if 400 <= s < 500:    return "client_error"
    if 500 <= s < 600:    return "server_error"
    if s == 0:            return "connection_error"
    return "unknown"


# ════════════════════════════════════════════════════════════════════════════
#  STEP 3 — Run the audit
# ════════════════════════════════════════════════════════════════════════════

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=20)
    ap.add_argument("--out",     default="link-check-results.json")
    ap.add_argument("--delay",   type=float, default=0.05)
    ap.add_argument("--no-external", action="store_true",
                    help="Skip testing external (FareHarbor / Filestack / etc.) URLs")
    ap.add_argument("--external-sample", type=int, default=100,
                    help="How many random external URLs to test (default 100, 0 = all)")
    args = ap.parse_args()

    print("=" * 60)
    print(" check_links_v2.py — link checker for miamijetskiboatrentals.com")
    print("=" * 60)
    print()

    collected = collect_urls()
    internal       = sorted(collected["internal"])
    external       = sorted(collected["external"])
    redirect_dests = sorted(collected["redirect_dests"])

    print(f"Internal URLs found:         {len(internal):>5}")
    print(f"vercel.json redirect dests:  {len(redirect_dests):>5}")
    print(f"External URLs found:         {len(external):>5}")

    # Sample external if requested
    to_test_external: list[str] = []
    if not args.no_external and external:
        if args.external_sample > 0 and len(external) > args.external_sample:
            random.seed(42)
            to_test_external = random.sample(external, args.external_sample)
            print(f"  → testing sample of   {len(to_test_external):>5} external")
        else:
            to_test_external = external
            print(f"  → testing ALL         {len(to_test_external):>5} external")
    else:
        print(f"  → skipping external")

    # Dedupe redirect_dests against internal
    redirect_dests = [u for u in redirect_dests if u not in set(internal)]
    print(f"  + unique redirect dests:   {len(redirect_dests):>5}")

    all_to_test = list(dict.fromkeys(internal + redirect_dests + to_test_external))
    print(f"\nTotal unique URLs to check:  {len(all_to_test)}\n")

    # Threaded execution
    results: dict[str, list] = defaultdict(list)
    lock = threading.Lock()
    done = [0]
    total = len(all_to_test)
    start = time.time()

    def worker(u):
        time.sleep(args.delay)
        return check_url(u)

    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        futures = {ex.submit(worker, u): u for u in all_to_test}
        for fut in as_completed(futures):
            r = fut.result()
            cat = categorize(r)
            with lock:
                results[cat].append(r)
                done[0] += 1
                if done[0] % 50 == 0 or done[0] == total:
                    elapsed = time.time() - start
                    pct = done[0] * 100 // total
                    bad = (len(results["broken_404"]) + len(results["server_error"])
                           + len(results["connection_error"]) + len(results["client_error"]))
                    print(f"  [{pct:3d}%] {done[0]:>5}/{total}   ({elapsed:.0f}s)   "
                          f"✅ {len(results['ok'])}   ↪ {len(results['redirected'])}   "
                          f"❌ {bad}", end="\r", flush=True)

    elapsed = time.time() - start

    # ── Summary ───────────────────────────────────────────────────────────────
    print("\n\n" + "=" * 60)
    print(f"  Done in {elapsed:.0f}s")
    print("=" * 60)
    counts = {k: len(v) for k, v in results.items()}
    label = {
        "ok":               "✅ OK (2xx)",
        "redirected":       "↪  Redirected (3xx)",
        "broken_404":       "❌ 404 Not Found",
        "gone_410":         "🪦 410 Gone",
        "client_error":     "⚠️  Other 4xx",
        "auth_required":    "🔒 401/403",
        "server_error":     "💥 5xx Server Error",
        "connection_error": "🔌 Connection error",
        "unknown":          "❓ Unknown",
    }
    for k in ("ok", "redirected", "broken_404", "gone_410", "client_error",
              "auth_required", "server_error", "connection_error", "unknown"):
        if counts.get(k, 0):
            print(f"  {label[k]:<22} {counts[k]:>5}")
    print("=" * 60)

    # ── Print every broken URL ────────────────────────────────────────────────
    broken_categories = ("broken_404", "server_error", "connection_error", "client_error")
    has_broken = False
    for cat in broken_categories:
        items = results.get(cat, [])
        if not items: continue
        has_broken = True
        print(f"\n{label[cat]}:")
        for r in sorted(items, key=lambda x: x["url"]):
            err = f" — {r['error']}" if r["error"] else ""
            print(f"  [{r['status']:>3}] {r['url']}{err}")

    # ── Save ──────────────────────────────────────────────────────────────────
    out_path = SCRIPT_DIR / args.out
    with open(out_path, "w") as f:
        json.dump({
            "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "duration_s":   round(elapsed, 1),
            "counts":       counts,
            "results":      dict(results),
        }, f, indent=2)
    print(f"\n📝 Reporte completo guardado en: {out_path.name}")

    sys.exit(1 if has_broken else 0)


if __name__ == "__main__":
    main()
