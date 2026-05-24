#!/usr/bin/env python3
"""Verify that every Book Now URL in operators.json returns HTTP 200 from FareHarbor.

Reads operators.json, hits each unique URL with HEAD (falls back to GET if HEAD
fails), reports per-URL status. Writes broken_urls.json with any failures so
you can fix them.

Usage:
    python3 verify_booking_urls.py

Optional flags:
    --sample N      Only test N URLs (random sample) instead of all
    --workers N     Parallel workers (default 8)
"""
import json, sys, time, argparse, concurrent.futures, urllib.request, urllib.error
from collections import Counter

BASE = "https://fareharbor.com"


def check(url, timeout=15):
    """Return (status_code, final_url_after_redirects). 0 on network error."""
    headers = {'User-Agent': 'Mozilla/5.0 (compatible; BookLinkCheck/1.0)'}
    for method in ('HEAD', 'GET'):
        try:
            req = urllib.request.Request(url, method=method, headers=headers)
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.status, resp.url
        except urllib.error.HTTPError as e:
            # 4xx / 5xx — return status
            if method == 'GET':
                return e.code, url
            # else try GET
        except (urllib.error.URLError, TimeoutError, ConnectionError) as e:
            if method == 'GET':
                return 0, url
    return 0, url


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--sample', type=int, default=0, help='test only N URLs')
    p.add_argument('--workers', type=int, default=8)
    args = p.parse_args()

    ops = json.load(open('operators.json'))
    # Group ops by URL so we don't test the same URL twice
    url_to_ids = {}
    for o in ops:
        link = o.get('link', '')
        if not link:
            continue
        url_to_ids.setdefault(link, []).append(o['id'])

    urls = list(url_to_ids.keys())
    if args.sample and args.sample < len(urls):
        import random
        random.seed(0)
        urls = random.sample(urls, args.sample)

    print(f"Checking {len(urls):,} unique URLs across {sum(len(ids) for ids in url_to_ids.values()):,} operator records...")
    print(f"Workers: {args.workers}")
    print()

    results = {}
    status_counts = Counter()
    started = time.time()

    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {pool.submit(check, url): url for url in urls}
        for i, future in enumerate(concurrent.futures.as_completed(futures), 1):
            url = futures[future]
            status, final = future.result()
            results[url] = status
            status_counts[status] += 1
            if i % 50 == 0 or i == len(urls):
                elapsed = time.time() - started
                rate = i / elapsed if elapsed > 0 else 0
                eta = (len(urls) - i) / rate if rate else 0
                print(f"  {i}/{len(urls)} done · {elapsed:.0f}s elapsed · {rate:.1f} req/s · ETA {eta:.0f}s", end='\r', flush=True)
    print()

    print(f"\nStatus code distribution:")
    for status, n in sorted(status_counts.items(), key=lambda x: -x[1]):
        label = {200: '✓ OK', 0: '✗ network error/timeout',
                 404: '✗ NOT FOUND', 301: 'redirect', 302: 'redirect',
                 403: 'forbidden', 500: 'server error'}.get(status, str(status))
        print(f"  {status} ({label}): {n:,}")

    # Affected operators
    broken = {url: status for url, status in results.items() if status >= 400 or status == 0}
    affected_ops = {oid for url in broken for oid in url_to_ids[url]}
    print(f"\nBroken/unreachable URLs: {len(broken):,}")
    print(f"Affected operator records: {len(affected_ops):,}")

    if broken:
        out = {
            'summary': {
                'total_urls': len(urls),
                'broken_urls': len(broken),
                'affected_operators': len(affected_ops),
            },
            'broken': [
                {'url': url, 'status': status, 'op_ids': url_to_ids[url]}
                for url, status in sorted(broken.items(), key=lambda kv: kv[1])
            ],
        }
        with open('broken_urls.json', 'w') as f:
            json.dump(out, f, indent=2)
        print(f"\nDetails written to broken_urls.json")

    return 0 if not broken else 1


if __name__ == '__main__':
    sys.exit(main())
