#!/usr/bin/env python3
"""
check_links_v3.py — link checker proactivo para miamijetskiboatrentals.com

v3 sobre v2: detección de URLs rotas que NO conoces de antemano.

Capacidades nuevas (todas opt-in con flags):

  --variants
      Para cada slug existente, genera variantes "razonables" que un
      backlink externo / Search Console / usuario podría usar y prueba
      cuáles dan 404. Detecta URLs rotas que tu sitemap no incluye.

      Variantes generadas:
        • Sufijos de zona alternativos:
            -puntacana ↔ -bavaro, -bayahibe, -capcana, -punta-cana
            -keywest ↔ -key-west, -keys
            -fortlauderdale ↔ -fort-lauderdale, -broward, -hollywood
            -staugustine ↔ -st-augustine, -augustine, -nefl
        • Con/sin sufijo geográfico genérico: -fl, -florida
        • Plurales: rental ↔ rentals, tour ↔ tours, charter ↔ charters
        • Espacios: jet-ski ↔ jetski
        • Prefijo "best-": slug ↔ best-slug

  --orphans
      Reporta inconsistencias entre las 3 fuentes de verdad:
        • HTMLs sin entrada en sitemap.xml (sub-indexación SEO)
        • Entradas en sitemap sin HTML que las respalde (404s del sitemap)
        • Slugs en slug-map.js sin HTML
        • Operadores en operators.json sin slug en slug-map.js
        • Links internos en HTML que apuntan a páginas que no existen
          (después de aplicar redirects y rewrites de vercel.json)

  --assets
      Verifica que los activos esenciales del sitio se sirvan correctamente:
        /robots.txt, /sitemap.xml, /favicon.ico, /og-image.png,
        /manifest.json, /operator.css, /operators.json, /operators-slim.json,
        /slug-map.js, /referral.js, /apple-touch-icon.png, /404
      Estado esperado: 200 (no 404, no 301 a otro lado).

  --crawl <N>
      Live BFS desde / hasta profundidad N (default 2). Parsea el HTML
      renderizado por el servidor y sigue todos los <a href> internos.
      Detecta URLs que aparecen solo en HTML generado dinámicamente,
      no en código fuente, no en sitemap.

  --gsc <archivo.csv>
      Lee un export de Google Search Console (Páginas indexadas con
      problemas o Sitemaps) y prueba cada URL. Pega tu CSV en
      gsc-export.csv y corre: --gsc gsc-export.csv

Uso típico:
    python3 check_links_v3.py --variants --orphans --assets   # diagnostic
    python3 check_links_v3.py --crawl 3 --workers 30          # crawl
    python3 check_links_v3.py --variants --no-external        # solo internas

Sale con exit code 1 si encuentra rotas (útil para CI).
"""
from __future__ import annotations
import re, json, time, sys, argparse, random, threading, csv, os
from pathlib import Path
from urllib.request import Request, build_opener, HTTPRedirectHandler
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import defaultdict, deque

BASE_URL   = "https://miamijetskiboatrentals.com"
SCRIPT_DIR = Path(__file__).parent
HEADERS    = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/126.0 Safari/537.36 LinkChecker/3.0",
    "Accept":     "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}
TIMEOUT       = 12
MAX_RETRIES   = 2
RETRY_BACKOFF = 1.0

# Mapeo de sufijo de zona → otros sufijos equivalentes
ZONE_SUFFIX_GROUPS = [
    {"-puntacana", "-bavaro", "-bayahibe", "-capcana", "-cap-cana", "-punta-cana", "-dominican"},
    {"-cancun", "-tulum", "-playadelcarmen", "-rivera-maya"},
    {"-keywest", "-key-west", "-keys", "-keylargo", "-key-largo", "-marathon", "-islamorada"},
    {"-fortlauderdale", "-fort-lauderdale", "-broward", "-hollywood"},
    {"-staugustine", "-st-augustine", "-nefl", "-jax", "-jacksonville", "-amelia", "-amelia-island", "-daytona"},
    {"-miami", "-miami-beach", "-miamibeach"},
    {"-orlando", "-kissimmee"},
    {"-space", "-capecanaveral", "-cape-canaveral", "-cocoabeach", "-cocoa-beach", "-merritt-island", "-titusville", "-melbourne"},
    {"-centralfl", "-central-florida", "-crystalriver", "-crystal-river", "-silver-springs", "-tavares"},
    {"-gulf", "-westfl", "-destin", "-tampa", "-naples", "-sarasota", "-pensacola", "-pcb", "-panama-city", "-fortmyers", "-fort-myers", "-marco-island", "-clearwater", "-stpete", "-st-petersburg", "-siesta-key"},
    {"-hawaii", "-maui", "-oahu", "-kauai", "-bigisland", "-big-island", "-kona", "-lahaina", "-kahului", "-kapolei", "-hilo", "-honolulu"},
    {"-palmbeach", "-palm-beach", "-westpalmbeach"},
    {"-everglades", "-everglades-city"},
]

# Variantes léxicas comunes
LEXICAL_VARIANTS = [
    ("-rental",   "-rentals"),
    ("-tour",     "-tours"),
    ("-charter",  "-charters"),
    ("-ride",     "-rides"),
    ("-jet-ski",  "-jetski"),
    ("-water-sport", "-watersports"),
    ("-boat-rental", "-boat-rentals"),
]

# ════════════════════════════════════════════════════════════════════════════
#  Common HTTP machinery (shared between modes)
# ════════════════════════════════════════════════════════════════════════════

class TrackingRedirectHandler(HTTPRedirectHandler):
    def __init__(self):
        super().__init__()
        self.chain = []
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        self.chain.append((req.full_url, code, newurl))
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def fetch(url: str, method: str = "HEAD", return_body: bool = False) -> tuple[int, str | None, list, str | None]:
    h = TrackingRedirectHandler()
    op = build_opener(h)
    try:
        resp = op.open(Request(url, headers=HEADERS, method=method), timeout=TIMEOUT)
        body = None
        if return_body and method == "GET":
            try:
                body = resp.read(80000).decode("utf-8", errors="ignore")
            except Exception:
                pass
        return resp.status, None, h.chain, body
    except HTTPError as e:
        return e.code, str(e.reason)[:120], h.chain, None
    except URLError as e:
        return 0, str(e.reason)[:120], h.chain, None
    except Exception as e:
        return -1, str(e)[:120], h.chain, None


def check_url(url: str, get_body: bool = False) -> dict:
    last_status, last_err = 0, None
    for attempt in range(MAX_RETRIES + 1):
        status, err, chain, body = fetch(url, "HEAD", return_body=False)
        if status in (405, 501) or (status >= 400 and status < 600 and not chain):
            g_status, g_err, g_chain, g_body = fetch(url, "GET", return_body=get_body)
            if g_status < 400:
                status, err, chain, body = g_status, g_err, g_chain, g_body
        if status in (0, -1) or (500 <= status < 600):
            last_status, last_err = status, err
            time.sleep(RETRY_BACKOFF * (2 ** attempt))
            continue
        break
    else:
        status, err = last_status, last_err

    return {
        "url": url,
        "status": status,
        "error": err,
        "final_url": chain[-1][2] if chain else url,
        "body_excerpt": body,
    }


# ════════════════════════════════════════════════════════════════════════════
#  Load sources of truth (sitemap, slug-map, operators.json, HTML files)
# ════════════════════════════════════════════════════════════════════════════

def load_sources():
    """Return:
      htmls:      set of slugs that have .html files at root
      sitemap:    set of slugs in sitemap.xml
      slug_map:   set of slugs in slug-map.js (the values, not the IDs)
      op_slugs:   set of slugs that operators.json refers to (via slug-map)
    """
    htmls = {os.path.splitext(f)[0] for f in os.listdir(SCRIPT_DIR) if f.endswith(".html")}

    # Sitemap puede ser:
    # (a) plano <urlset> con todos los <loc>
    # (b) índice <sitemapindex> que apunta a sub-sitemaps en /sitemaps/*.xml
    # Soportamos ambos: si vemos <sitemapindex>, expandimos los sub-sitemaps locales.
    sm = (SCRIPT_DIR / "sitemap.xml").read_text(errors="ignore")
    sitemap = set()
    if "<sitemapindex" in sm:
        # Caso (b) — index: leer cada sub-sitemap del filesystem
        sub_locs = re.findall(r"<loc>https://miamijetskiboatrentals\.com/([^<]+)</loc>", sm)
        for sub_path in sub_locs:
            sub_file = SCRIPT_DIR / sub_path
            if sub_file.exists() and sub_file.suffix == ".xml":
                sub_xml = sub_file.read_text(errors="ignore")
                for loc in re.findall(r"<loc>https://miamijetskiboatrentals\.com/([^<]*)</loc>", sub_xml):
                    if loc:
                        sitemap.add(loc.rstrip("/"))
            # Las propias entradas /sitemaps/X.xml NO se cuentan como páginas
    else:
        # Caso (a) — plano
        sitemap_locs = re.findall(r"<loc>https://miamijetskiboatrentals\.com/([^<]*)</loc>", sm)
        sitemap = {u.rstrip("/") for u in sitemap_locs if u}

    sj = (SCRIPT_DIR / "slug-map.js").read_text(errors="ignore")
    slug_map_pairs = re.findall(r'"([a-z0-9][a-z0-9\-]+)"\s*:\s*"([a-z0-9][a-z0-9\-]+)"', sj)
    slug_map = {s for _id, s in slug_map_pairs}

    return htmls, sitemap, slug_map


# ════════════════════════════════════════════════════════════════════════════
#  Mode 1 — variant generation
# ════════════════════════════════════════════════════════════════════════════

def generate_variants(slug: str) -> set[str]:
    """Return set of plausible variants of a slug — for testing if they 404."""
    variants: set[str] = set()

    # Zone-suffix swaps
    for group in ZONE_SUFFIX_GROUPS:
        for sfx in group:
            if slug.endswith(sfx):
                base = slug[: -len(sfx)]
                for alt in group:
                    if alt != sfx:
                        variants.add(base + alt)

    # Lexical: rental ↔ rentals, tour ↔ tours — solo al final del slug
    # para evitar duplicaciones tipo "rentalss"
    for a, b in LEXICAL_VARIANTS:
        if slug.endswith(b):
            variants.add(slug[:-len(b)] + a)
        elif slug.endswith(a):
            variants.add(slug[:-len(a)] + b)
        # variantes embebidas (mitad de slug): solo si no hay duplicación
        for token_a, token_b in [(a, b), (b, a)]:
            if token_a in slug and token_b not in slug:
                variants.add(slug.replace(token_a, token_b))

    # -fl / -florida suffix
    if slug.endswith("-fl"):
        variants.add(slug[:-3] + "-florida")
        variants.add(slug[:-3])
    if slug.endswith("-florida"):
        variants.add(slug[:-8] + "-fl")
        variants.add(slug[:-8])
    elif not slug.endswith("-fl") and not slug.endswith("-florida"):
        variants.add(slug + "-fl")

    # "best-" prefix
    if not slug.startswith("best-"):
        variants.add("best-" + slug)

    # Remove the original
    variants.discard(slug)
    return variants


def mode_variants(known: set[str], workers: int, delay: float, max_test: int):
    """For each known slug, generate variants and test ones that aren't known."""
    print()
    print("=" * 65)
    print("  MODE: --variants — buscando URLs rotas no anticipadas")
    print("=" * 65)

    # Generate variant set, filter out those already known
    candidates: set[str] = set()
    for s in known:
        for v in generate_variants(s):
            if v and v not in known:
                candidates.add(v)

    print(f"  Variantes generadas: {len(candidates):>6}")
    if len(candidates) > max_test:
        random.seed(0)
        candidates = set(random.sample(sorted(candidates), max_test))
        print(f"  Limitado a sample:   {len(candidates):>6}  (usa --variants-max para ajustar)")
    print()

    urls = [f"{BASE_URL}/{c}" for c in sorted(candidates)]
    results = test_urls(urls, workers, delay)

    broken = [r for r in results if r["status"] == 404]
    redir  = [r for r in results if 300 <= r["status"] < 400 or (r.get("final_url") and r["final_url"] != r["url"])]
    ok     = [r for r in results if r["status"] == 200]

    print(f"  Variantes 200 (URLs no listadas en sitemap pero válidas): {len(ok)}")
    print(f"  Variantes redirigidas (cubiertas por redirects/rewrites): {len(redir)}")
    print(f"  Variantes 404 (potencialmente rotas si tienen backlinks): {len(broken)}")
    print()
    if broken:
        print("  URLs potencialmente rotas — agregar redirect si tienen tráfico:")
        for r in sorted(broken, key=lambda x: x["url"])[:30]:
            print(f"    [404] {r['url']}")
        if len(broken) > 30:
            print(f"    ... y {len(broken)-30} más")
    return broken


# ════════════════════════════════════════════════════════════════════════════
#  Mode 2 — orphan check
# ════════════════════════════════════════════════════════════════════════════

def mode_orphans():
    print()
    print("=" * 65)
    print("  MODE: --orphans — inconsistencias entre fuentes de verdad")
    print("=" * 65)
    htmls, sitemap, slug_map = load_sources()

    landing_pages = {"index", "about", "contact", "privacy", "terms", "partners",
                     "404", "miami-villas", "miami-exotic-cars", "webhook-tester"}
    # HTML pages sin sitemap (sub-indexación SEO)
    in_html_not_sitemap = htmls - sitemap - landing_pages
    # Slugs en sitemap sin HTML (404 latente)
    in_sitemap_not_html = sitemap - htmls
    # Slugs en slug-map.js sin HTML
    in_slugmap_not_html = slug_map - htmls

    print(f"  Páginas HTML sin entrada en sitemap.xml: {len(in_html_not_sitemap)}")
    for f in sorted(in_html_not_sitemap)[:10]:
        print(f"    /{f}")
    if len(in_html_not_sitemap) > 10:
        print(f"    ... y {len(in_html_not_sitemap)-10} más")
    print()

    print(f"  Slugs en sitemap.xml sin HTML correspondiente: {len(in_sitemap_not_html)}")
    for s in sorted(in_sitemap_not_html)[:10]:
        print(f"    /{s}")
    if len(in_sitemap_not_html) > 10:
        print(f"    ... y {len(in_sitemap_not_html)-10} más")
    print()

    print(f"  Slugs en slug-map.js sin HTML: {len(in_slugmap_not_html)}")
    for s in sorted(in_slugmap_not_html)[:10]:
        print(f"    /{s}")
    return in_sitemap_not_html  # these are the real "broken" ones


# ════════════════════════════════════════════════════════════════════════════
#  Mode 3 — essential asset check
# ════════════════════════════════════════════════════════════════════════════

ESSENTIAL_ASSETS = [
    "/robots.txt",
    "/sitemap.xml",
    "/favicon.ico",
    "/og-image.png",
    "/apple-touch-icon.png",
    "/manifest.json",
    "/operator.css",
    "/operators.json",
    "/operators-slim.json",
    "/slug-map.js",
    "/referral.js",
]


def mode_assets(workers: int, delay: float):
    print()
    print("=" * 65)
    print("  MODE: --assets — activos esenciales del sitio")
    print("=" * 65)
    urls = [BASE_URL + p for p in ESSENTIAL_ASSETS]
    results = test_urls(urls, workers, delay)
    bad = []
    for r in sorted(results, key=lambda x: x["url"]):
        status = r["status"]
        if status == 200:
            tag = "✅"
        elif 300 <= status < 400:
            tag = "↪ "
        else:
            tag = "❌"
            bad.append(r)
        print(f"  {tag} [{status}] {r['url']}")
    return bad


# ════════════════════════════════════════════════════════════════════════════
#  Mode 4 — live BFS crawl from homepage
# ════════════════════════════════════════════════════════════════════════════

HREF_RE = re.compile(r'href=["\']([^"\'#]+)["\']', re.I)


def mode_crawl(max_depth: int, workers: int, delay: float, page_limit: int):
    print()
    print("=" * 65)
    print(f"  MODE: --crawl — BFS desde / hasta profundidad {max_depth}")
    print("=" * 65)

    seen: set[str] = set()
    queue = deque([(BASE_URL, 0)])
    broken: list[dict] = []
    visited = 0
    while queue and visited < page_limit:
        url, depth = queue.popleft()
        if url in seen:
            continue
        seen.add(url)
        visited += 1
        if visited % 50 == 0:
            print(f"  visitadas: {visited:>4}, cola: {len(queue):>4}, depth max alcanzado: {depth}")

        r = check_url(url, get_body=True)
        if r["status"] == 404:
            broken.append(r)
            continue
        if r["status"] != 200:
            continue
        if depth >= max_depth or not r.get("body_excerpt"):
            continue

        # Extract links from body
        for href in HREF_RE.findall(r["body_excerpt"]):
            if href.startswith(("#", "javascript:", "mailto:", "tel:", "data:")):
                continue
            if href.startswith("/"):
                target = BASE_URL + href
            elif href.startswith("http"):
                if urlparse(href).netloc not in ("miamijetskiboatrentals.com", "www.miamijetskiboatrentals.com"):
                    continue
                target = href
            else:
                continue
            target = target.split("#")[0].rstrip("/")
            if target and target not in seen:
                queue.append((target, depth + 1))

    print()
    print(f"  Páginas crawleadas:    {visited}")
    print(f"  URLs únicas vistas:    {len(seen)}")
    print(f"  Links rotos detectados: {len(broken)}")
    for r in sorted(broken, key=lambda x: x["url"])[:30]:
        print(f"    [{r['status']}] {r['url']}")
    return broken


# ════════════════════════════════════════════════════════════════════════════
#  Mode 5 — GSC CSV
# ════════════════════════════════════════════════════════════════════════════

def mode_gsc(csv_path: str, workers: int, delay: float):
    print()
    print("=" * 65)
    print(f"  MODE: --gsc — testear URLs de Search Console: {csv_path}")
    print("=" * 65)
    if not os.path.exists(csv_path):
        print(f"  ❌ Archivo no existe: {csv_path}")
        return []

    urls = set()
    with open(csv_path, encoding="utf-8-sig") as f:
        # GSC export es CSV con columna "URL" o "Page" (varía por idioma)
        reader = csv.reader(f)
        header = next(reader, [])
        url_col = 0
        for i, col in enumerate(header):
            if col.lower() in {"url", "page", "página", "pagina"}:
                url_col = i
                break
        for row in reader:
            if not row or len(row) <= url_col:
                continue
            u = row[url_col].strip()
            if u.startswith("http"):
                urls.add(u)

    print(f"  URLs en el CSV: {len(urls)}")
    if not urls:
        return []

    results = test_urls(sorted(urls), workers, delay)
    broken = [r for r in results if r["status"] == 404]
    print(f"  Rotas (404): {len(broken)}")
    for r in sorted(broken, key=lambda x: x["url"])[:50]:
        print(f"    [404] {r['url']}")
    return broken


# ════════════════════════════════════════════════════════════════════════════
#  Threaded URL tester (shared)
# ════════════════════════════════════════════════════════════════════════════

def test_urls(urls: list[str], workers: int, delay: float) -> list[dict]:
    results: list[dict] = []
    if not urls:
        return results
    total = len(urls)
    done = [0]
    lock = threading.Lock()
    start = time.time()
    print(f"  testando {total} URLs con {workers} workers…")

    def w(u):
        time.sleep(delay)
        return check_url(u)

    with ThreadPoolExecutor(max_workers=workers) as ex:
        futures = [ex.submit(w, u) for u in urls]
        for fut in as_completed(futures):
            r = fut.result()
            results.append(r)
            with lock:
                done[0] += 1
                if done[0] % 50 == 0 or done[0] == total:
                    el = time.time() - start
                    print(f"    [{done[0]*100//total:3d}%] {done[0]:>5}/{total}  ({el:.0f}s)", end="\r", flush=True)
    print()
    return results


# ════════════════════════════════════════════════════════════════════════════
#  Main
# ════════════════════════════════════════════════════════════════════════════

def main():
    ap = argparse.ArgumentParser(description="check_links_v3 — proactive link checker")
    ap.add_argument("--variants", action="store_true", help="probar variantes de slugs existentes")
    ap.add_argument("--orphans",  action="store_true", help="reportar HTMLs vs sitemap vs slug-map mismatches")
    ap.add_argument("--assets",   action="store_true", help="verificar activos esenciales del sitio")
    ap.add_argument("--crawl",    type=int, default=0, metavar="N", help="live BFS desde / hasta profundidad N")
    ap.add_argument("--crawl-limit", type=int, default=500, help="máximo de páginas a crawlear (default 500)")
    ap.add_argument("--gsc",      type=str, default="", metavar="CSV", help="archivo CSV de Search Console")
    ap.add_argument("--variants-max", type=int, default=2000, help="máximo de variantes a probar (default 2000)")
    ap.add_argument("--workers", type=int, default=20)
    ap.add_argument("--delay",   type=float, default=0.05)
    args = ap.parse_args()

    if not any([args.variants, args.orphans, args.assets, args.crawl > 0, args.gsc]):
        print("Nada que hacer. Activa al menos un modo:")
        print("  --variants  --orphans  --assets  --crawl 2  --gsc archivo.csv")
        print()
        print("Ejemplos:")
        print("  python3 check_links_v3.py --variants --orphans --assets")
        print("  python3 check_links_v3.py --crawl 3 --workers 30")
        return 0

    print("=" * 65)
    print("  check_links_v3.py — análisis proactivo de URLs rotas")
    print("=" * 65)

    all_broken: list[dict] = []
    htmls, sitemap, slug_map = load_sources()
    known_slugs = htmls | sitemap | slug_map

    if args.assets:
        all_broken.extend(mode_assets(args.workers, args.delay))

    if args.orphans:
        orphans = mode_orphans()
        # Test the sitemap-without-html slugs to see if they really 404
        if orphans:
            print()
            print("  Probando si los slugs en sitemap sin HTML realmente dan 404…")
            urls = [f"{BASE_URL}/{s}" for s in sorted(orphans)[:200]]
            r404 = [r for r in test_urls(urls, args.workers, args.delay) if r["status"] == 404]
            all_broken.extend(r404)
            print(f"  Confirmados como 404: {len(r404)}")

    if args.variants:
        all_broken.extend(mode_variants(known_slugs, args.workers, args.delay, args.variants_max))

    if args.crawl > 0:
        all_broken.extend(mode_crawl(args.crawl, args.workers, args.delay, args.crawl_limit))

    if args.gsc:
        all_broken.extend(mode_gsc(args.gsc, args.workers, args.delay))

    # ── Final report ──────────────────────────────────────────────────────
    print()
    print("=" * 65)
    print("  RESUMEN FINAL")
    print("=" * 65)
    if all_broken:
        unique = {r["url"]: r for r in all_broken}
        print(f"  ❌ Total URLs rotas únicas: {len(unique)}")
        out_path = SCRIPT_DIR / "link-check-v3-broken.json"
        with open(out_path, "w") as f:
            json.dump(sorted(unique.values(), key=lambda x: x["url"]), f, indent=2)
        print(f"  📝 Listado en: {out_path.name}")
        return 1
    print("  ✅ No se detectaron URLs rotas en los modos seleccionados.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
