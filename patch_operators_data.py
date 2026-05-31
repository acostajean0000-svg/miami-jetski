#!/usr/bin/env python3
"""
patch_operators_data.py — null out fake placeholder ratings in operators.json.

The "(4.6, 0)" and "(4.8, 25)" rating/reviews pairs appear on 3,438 and 1,323
operators respectively — every operator that shares those exact pairs is using
a template default, not real data.

This script:
  * Sets `rating = None` and `reviews = None` on every operator whose pair is
    one of the two known fake pairs.
  * Writes the patched data back to operators.json AND operators-slim.json.
  * Makes a timestamped backup of both files before modifying.
  * Skips anything that already has `rating: null`. Idempotent.

Effect on the live UI:
  - Operator card on homepage: rating star is hidden when rating is null.
  - JSON-LD on operator pages (after re-generation): aggregateRating block
    is omitted, which is what we already enforced at runtime in fix_schema.py.

Usage:
  python3 patch_operators_data.py            # dry run
  python3 patch_operators_data.py --apply    # write changes
"""
import json, sys, datetime as dt, os, shutil

DRY_RUN = '--apply' not in sys.argv
FAKE_PAIRS = {(4.6, 0), (4.8, 25)}


def patch(records: list[dict]) -> tuple[list[dict], int]:
    n = 0
    for o in records:
        pair = (o.get('rating'), o.get('reviews'))
        if pair in FAKE_PAIRS:
            o['rating'] = None
            o['reviews'] = None
            n += 1
    return records, n


def process(path: str) -> int:
    with open(path) as f:
        data = json.load(f)
    if not isinstance(data, list):
        print(f'{path}: top-level is not a list — skip')
        return 0
    data, n = patch(data)
    if n == 0:
        print(f'{path}: already clean (0 changes)')
        return 0
    if DRY_RUN:
        print(f'{path}: would null {n} fake-rating records')
        return n
    # backup
    ts = dt.datetime.utcnow().strftime('%Y%m%d-%H%M%S')
    bak = f'{path}.bak-{ts}'
    shutil.copy2(path, bak)
    with open(path, 'w') as f:
        json.dump(data, f, ensure_ascii=False, separators=(',', ':'))
    print(f'{path}: nulled {n} records  (backup: {bak})')
    return n


def main() -> int:
    total = 0
    for path in ('operators.json', 'operators-slim.json'):
        if os.path.exists(path):
            total += process(path)
    print()
    print('=' * 50)
    print('DRY RUN' if DRY_RUN else 'APPLIED')
    print(f'Total records affected: {total}')
    if DRY_RUN:
        print('Re-run with --apply to write changes.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
