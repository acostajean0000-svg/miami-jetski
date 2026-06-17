#!/usr/bin/env python3
"""
patch_dup_photos.py — null the photo field on operators that share a heavily
reused image.

Right now 295 operators across 13 distinct photos share the same Filestack
image (one photo is on 77 operator cards). This looks farmed to Google and
reduces user trust.

The homepage already has a graceful fallback (category emoji + label) when
op.photo is null, so the cleanest fix is:

  - For any image used by >= 10 distinct operators, null the photo field on
    all of them. Their cards will show the category-emoji fallback instead.
  - Operators with a unique or low-shared photo are left alone.

Idempotent. Makes a timestamped backup of operators.json and operators-slim.json.

Usage:
  python3 patch_dup_photos.py            # dry run + report
  python3 patch_dup_photos.py --apply
"""
import json, re, sys, os, shutil, datetime as dt
from collections import Counter

DRY_RUN = '--apply' not in sys.argv
THRESHOLD = 10                                 # photos used by >= N ops get nulled

HANDLE_RE = re.compile(r'filestackcontent\.com/([A-Za-z0-9]{15,30})/')


def handle_of(url: str) -> str | None:
    if not url: return None
    m = HANDLE_RE.search(url)
    return m.group(1) if m else None


def process(path: str) -> int:
    if not os.path.exists(path):
        return 0
    data = json.load(open(path))
    if not isinstance(data, list):
        return 0

    counts = Counter(handle_of(o.get('photo', '')) for o in data if handle_of(o.get('photo', '')))
    over = {h for h, n in counts.items() if n >= THRESHOLD}

    n_nulled = 0
    for o in data:
        h = handle_of(o.get('photo', ''))
        if h in over:
            o['photo'] = None
            n_nulled += 1

    if not DRY_RUN and n_nulled:
        ts = dt.datetime.utcnow().strftime('%Y%m%d-%H%M%S')
        shutil.copy2(path, f'{path}.bak-{ts}')
        with open(path, 'w') as f:
            json.dump(data, f, ensure_ascii=False, separators=(',', ':'))

    print(f'{path}: {n_nulled} operators had photo nulled '
          f'({len(over)} distinct shared images over threshold of {THRESHOLD}+ uses)')
    if not DRY_RUN:
        print(f'  backup: {path}.bak-{ts}')
    return n_nulled


total = 0
for p in ('operators.json', 'operators-slim.json'):
    total += process(p)

print()
print('=' * 50)
print('DRY RUN' if DRY_RUN else 'APPLIED')
print(f'Total nulled (both files):  {total}')
if DRY_RUN:
    print('\nRe-run with --apply.')
