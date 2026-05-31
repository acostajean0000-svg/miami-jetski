#!/usr/bin/env python3
"""
fix_body_copy.py — replace the templated Dominican-Republic body paragraph
that's currently bleeding onto ~2,177 operator pages across all zones.

The bad paragraph reads (with city varying):

  "A N-hour off-road adventure through {city}'s countryside on an ATV
   or buggy. Stops at a typical Dominican house, the Crystal Water Cave,
   and Macao Beach. Hotel pickup and drop-off included."

Crystal Water Cave and Macao Beach are landmarks in Punta Cana, Dominican
Republic — they should not appear on Key West, Miami, Hawaii, etc. pages.
Like the FAQ bug, this is leftover from a copy-template generator.

This script:
  1. For each operator HTML page, finds <p> tags containing "Crystal Water
     Cave" or "Macao Beach" or "Dominican house".
  2. If the operator is actually in Punta Cana, leaves it alone (DR landmarks
     are legitimate there).
  3. Otherwise replaces the bad paragraph with the operator's real `desc`
     from operators.json.
  4. Makes a backup of every modified file.

Idempotent.

Usage:
  python3 fix_body_copy.py            # dry run
  python3 fix_body_copy.py --apply
"""
import json, re, sys, os, glob, datetime as dt, shutil

DRY_RUN = '--apply' not in sys.argv

# Load operator map
slug_js = open('slug-map.js').read()
m = re.search(r'window\._OP_SLUG_MAP\s*=\s*(\{.*?\});?\s*$', slug_js, re.S)
slug_map = json.loads(m.group(1))                    # id -> slug
slug_to_id = {v: k for k, v in slug_map.items()}
ops = json.load(open('operators.json'))
op_by_id = {o['id']: o for o in ops}

# Marker phrases that indicate the bad DR template paragraph
DR_MARKERS = ('Crystal Water Cave', 'Macao Beach', 'typical Dominican house')

# A <p>...</p> regex (non-greedy)
P_TAG_RE = re.compile(r'<p\b[^>]*>(.*?)</p>', re.S)


def html_escape(text: str) -> str:
    return (text.replace('&', '&amp;')
                .replace('<', '&lt;')
                .replace('>', '&gt;'))


def process(path: str) -> dict:
    counters = {'changed': 0, 'paragraphs_replaced': 0,
                'skipped_no_op': 0, 'skipped_dr_op': 0}
    slug = os.path.splitext(os.path.basename(path))[0]
    if slug not in slug_to_id:
        counters['skipped_no_op'] = 1
        return counters
    op = op_by_id.get(slug_to_id[slug])
    if not op:
        counters['skipped_no_op'] = 1
        return counters

    # If the operator is actually in Punta Cana / DR, leave it alone
    if op.get('zone') in ('puntacana', 'capcana') or 'puntacana' in slug:
        counters['skipped_dr_op'] = 1
        return counters

    html = open(path).read()
    if not any(marker in html for marker in DR_MARKERS):
        return counters  # nothing to fix

    replacement_text = (op.get('desc') or '').strip()
    if not replacement_text:
        return counters

    def _sub(m):
        inner = m.group(1)
        if any(marker in inner for marker in DR_MARKERS):
            counters['paragraphs_replaced'] += 1
            return f'<p>{html_escape(replacement_text)}</p>'
        return m.group(0)

    new = P_TAG_RE.sub(_sub, html)
    if new != html:
        counters['changed'] = 1
        if not DRY_RUN:
            ts = dt.datetime.utcnow().strftime('%Y%m%d-%H%M%S')
            shutil.copy2(path, f'{path}.bak-{ts}')
            with open(path, 'w') as f:
                f.write(new)
    return counters


agg = {}
for f in sorted(glob.glob('*.html')):
    res = process(f)
    for k, v in res.items():
        agg[k] = agg.get(k, 0) + v

print('=' * 60)
print('BODY-COPY CLEANUP — ' + ('DRY RUN' if DRY_RUN else 'APPLIED'))
print('=' * 60)
print(f'Files changed:           {agg.get("changed", 0)}')
print(f'Paragraphs replaced:     {agg.get("paragraphs_replaced", 0)}')
print(f'Skipped (no operator):   {agg.get("skipped_no_op", 0)}')
print(f'Skipped (real DR op):    {agg.get("skipped_dr_op", 0)}')
if DRY_RUN:
    print('\nRe-run with --apply to write changes.')
