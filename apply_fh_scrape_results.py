#!/usr/bin/env python3
"""Apply the photo handles scraped by scrape_fareharbor_photos.js into operators.json.

Strategy (safe by default):
  - For each operator, ONLY swap their current photo IF:
      (a) the operator's CURRENT photo handle is NOT in the scraped handle set
          (i.e., the photo we display doesn't belong to that booking page), AND
      (b) the scraped set has at least one handle we can use.
  - Picks the first scraped handle that ISN'T already used by 5+ other operators
    (avoid swapping into another generic placeholder).

Usage:
    python3 apply_fh_scrape_results.py                  # dry-run (preview)
    python3 apply_fh_scrape_results.py --apply          # actually write changes
    python3 apply_fh_scrape_results.py --apply --force  # overwrite even matching photos
    python3 apply_fh_scrape_results.py --report mismatch_report.txt
"""
import argparse
import json
import os
import re
import sys
from collections import Counter, defaultdict

HANDLE_RE = re.compile(
    r'(?:filestackcontent\.com|filepicker\.io/api/file)/(?:[^/]+/)*?([A-Za-z0-9]{15,30})'
)


def extract_handle(url: str):
    if not url:
        return None
    m = HANDLE_RE.search(url)
    return m.group(1) if m else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--input', default='fh_scrape_photos.json')
    ap.add_argument('--apply', action='store_true', help='write changes (default: dry-run)')
    ap.add_argument('--force', action='store_true', help='swap even if current matches')
    ap.add_argument('--report', help='write mismatch report to this path')
    ap.add_argument('--limit', type=int, default=0)
    args = ap.parse_args()

    if not os.path.exists(args.input):
        print(f"ERROR: {args.input} not found. Run scrape_fareharbor_photos.js first.")
        return 1

    scraped = json.load(open(args.input))
    ops = json.load(open('operators.json'))
    ops_slim = json.load(open('operators-slim.json'))

    # Count how many ops use each handle globally → avoid swapping INTO a popular generic
    global_handle_usage = Counter()
    for o in ops:
        h = extract_handle(o.get('photo', ''))
        if h:
            global_handle_usage[h] += 1

    SUFFIX = '/convert?cache=true&compress=true&quality=90&format=webp&rotate=exif&w=1000&fit=max'

    matched_already = 0
    swappable = []
    no_scraped = 0
    scraped_empty = 0

    for o in ops:
        sid = o['id']
        sc = scraped.get(sid)
        if not sc:
            no_scraped += 1
            continue
        scraped_handles = sc.get('handles', []) or []
        if not scraped_handles:
            scraped_empty += 1
            continue
        current_handle = extract_handle(o.get('photo', ''))
        if current_handle in scraped_handles and not args.force:
            matched_already += 1
            continue
        # Pick the first scraped handle that isn't already a popular shared one
        best = None
        for h in scraped_handles:
            if global_handle_usage[h] < 5:
                best = h
                break
        if not best:
            best = scraped_handles[0]
        swappable.append({
            'id': sid,
            'name': o.get('name', '?')[:50],
            'current': current_handle or '(none)',
            'new': best,
            'scraped_count': len(scraped_handles),
        })

    print(f"Operators with scraped data: {sum(1 for o in ops if o['id'] in scraped)}")
    print(f"  Photo already matches FH booking page: {matched_already}")
    print(f"  Scraped returned empty (couldn't capture photos): {scraped_empty}")
    print(f"  No scrape data for this operator: {no_scraped}")
    print(f"  ✅ Swappable to a real FH photo: {len(swappable)}")

    if args.report:
        with open(args.report, 'w') as f:
            f.write(f"Total swappable: {len(swappable)}\n\n")
            for s in swappable:
                f.write(f"{s['id']:6s} | {s['name']}\n")
                f.write(f"  current: {s['current']}\n")
                f.write(f"  new:     {s['new']}\n")
                f.write(f"  scraped: {s['scraped_count']} handles\n\n")
        print(f"  Report saved to {args.report}")

    if args.limit and len(swappable) > args.limit:
        swappable = swappable[:args.limit]
        print(f"  Limited to first {args.limit}")

    if not args.apply:
        print("\n(dry-run — pass --apply to write changes)")
        if swappable:
            print(f"\nFirst 5 swaps that WOULD happen:")
            for s in swappable[:5]:
                print(f"  {s['id']} {s['name']}")
                print(f"    {s['current']} → {s['new']}")
        return 0

    # APPLY
    by_id_full = {o['id']: o for o in ops}
    by_id_slim = {o['id']: o for o in ops_slim}
    for s in swappable:
        new_url = f"https://cdn.filestackcontent.com/{s['new']}{SUFFIX}"
        by_id_full[s['id']]['photo'] = new_url
        if s['id'] in by_id_slim:
            by_id_slim[s['id']]['photo'] = new_url
    json.dump(ops, open('operators.json', 'w'), ensure_ascii=False, separators=(',', ':'))
    json.dump(ops_slim, open('operators-slim.json', 'w'), ensure_ascii=False, separators=(',', ':'))
    print(f"\n✅ Wrote {len(swappable)} photo updates to operators.json + operators-slim.json")
    print(f"Now run: python3 verify_card_images.py --fix")
    print(f"  to propagate the new photos to listing/category page cards.")
    return 0


if __name__ == '__main__':
    sys.exit(main())
