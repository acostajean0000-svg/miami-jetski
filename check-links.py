#!/usr/bin/env python3
"""
check-links.py — Live 404 checker for miamijetskiboatrentals.com
Usage:  python3 check-links.py [--workers 10] [--out results.json]
"""

import re, json, time, sys, argparse
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import defaultdict
import threading

BASE_URL   = "https://miamijetskiboatrentals.com"
SCRIPT_DIR = Path(__file__).parent
HEADERS    = {"User-Agent": "Mozilla/5.0 (LinkChecker/1.0)"}

# ── Collect every URL to test ────────────────────────────────────────────────
def collect_urls():
    urls = set()

    # 1. Sitemap
    sitemap = (SCRIPT_DIR / "sitemap.xml").read_text(errors="ignore")
    for loc in re.findall(r"<loc>(https://miamijetskiboatrentals\.com[^<]*)</loc>", sitemap):
        urls.add(loc.rstrip("/"))

    # 2. All slug-map slugs
    slug_js = (SCRIPT_DIR / "slug-map.js").read_text(errors="ignore")
    for op_id, slug in re.findall(r'"([^"]+)":"([^"]+)"', slug_js):
        urls.add(f"{BASE_URL}/{slug}")

    # 3. All <a href> links from HTML pages
    for fpath in SCRIPT_DIR.glob("*.html"):
        html = fpath.read_text(errors="ignore")
        for href in re.findall(r'href="/([a-z0-9][a-z0-9\-/]+)"', html):
            urls.add(f"{BASE_URL}/{href.rstrip('/')}")

    # 4. All absolute internal URLs in meta/JSON-LD
    for fpath in SCRIPT_DIR.glob("*.html"):
        html = fpath.read_text(errors="ignore")
        for url in re.findall(r'(https://miamijetskiboatrentals\.com/[a-z0-9][a-z0-9\-]+)', html):
            urls.add(url.rstrip("/"))

    # Remove homepage duplicates, sort
    urls = sorted(u for u in urls if u != BASE_URL and "?" not in u and "#" not in u)
    return urls

# ── Check a single URL ────────────────────────────────────────────────────────
def check_url(url):
    try:
        req = Request(url, headers=HEADERS, method="HEAD")
        resp = urlopen(req, timeout=10)
        return url, resp.status, None
    except HTTPError as e:
        return url, e.code, str(e.reason)
    except URLError as e:
        return url, 0, str(e.reason)
    except Exception as e:
        return url, -1, str(e)

# ── Main ─────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=15, help="Concurrent threads")
    parser.add_argument("--out", default="link-check-results.json", help="Output JSON file")
    parser.add_argument("--delay", type=float, default=0.05, help="Delay between requests (s)")
    args = parser.parse_args()

    print("Collecting URLs…")
    urls = collect_urls()
    print(f"Found {len(urls)} unique URLs to check\n")

    results = {"ok": [], "redirected": [], "broken": [], "error": []}
    lock = threading.Lock()
    done = [0]

    def worker(url):
        time.sleep(args.delay)
        return check_url(url)

    print(f"Checking {len(urls)} URLs with {args.workers} workers…\n")
    start = time.time()

    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        futures = {ex.submit(worker, u): u for u in urls}
        for fut in as_completed(futures):
            url, status, reason = fut.result()
            with lock:
                done[0] += 1
                pct = done[0] * 100 // len(urls)
                if done[0] % 100 == 0 or done[0] == len(urls):
                    elapsed = time.time() - start
                    print(f"  [{pct:3d}%] {done[0]}/{len(urls)}  ({elapsed:.0f}s)", end="\r")

            if status in (200, 204):
                results["ok"].append(url)
            elif status in (301, 302, 307, 308):
                results["redirected"].append({"url": url, "status": status})
            elif status == 404:
                results["broken"].append({"url": url, "status": 404})
            elif status == 0 or status == -1:
                results["error"].append({"url": url, "error": reason})
            else:
                results["broken"].append({"url": url, "status": status, "reason": reason})

    elapsed = time.time() - start
    print(f"\n\n{'='*55}")
    print(f"  Done in {elapsed:.1f}s")
    print(f"{'='*55}")
    print(f"  ✅ OK (2xx)       : {len(results['ok'])}")
    print(f"  ↪  Redirected     : {len(results['redirected'])}")
    print(f"  ❌ Broken (4xx/5xx): {len(results['broken'])}")
    print(f"  ⚠️  Errors          : {len(results['error'])}")
    print(f"{'='*55}\n")

    if results["broken"]:
        print("❌ BROKEN URLs:")
        for item in sorted(results["broken"], key=lambda x: x["url"]):
            print(f"  [{item['status']}] {item['url']}")

    if results["error"]:
        print("\n⚠️  CONNECTION ERRORS:")
        for item in sorted(results["error"], key=lambda x: x["url"])[:20]:
            print(f"  {item['url']}  —  {item['error']}")

    # Save full results
    out = SCRIPT_DIR / args.out
    with open(out, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nFull results saved to: {out}")

if __name__ == "__main__":
    main()
