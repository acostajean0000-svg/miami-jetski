#!/usr/bin/env python3
"""
fix_body_copy_v2.py — round 2.

After v1 we found two more places the bad DR-template content lives on
non-Punta-Cana pages:

  (a) <div class="tags-row"> contains literal tags like
      "🏖️ Macao Beach", "💧 Cave Swim", "🌵 Off-road", "🏎️ ATV".
  (b) <ul class="highlights-list"> contains items like
      "Typical Dominican house visit", "Swim in the Crystal Water Cave",
      "Stop at Macao Beach", "Round-trip hotel transportation".

For each operator that is NOT in Punta Cana / Cap Cana:
  - Replaces the .tags-row content with tags derived from op.cat + op.zl.
  - Removes the entire .highlights-list block.

Idempotent: re-running is a no-op if the markers are already gone.

Usage:
  python3 fix_body_copy_v2.py            # dry run
  python3 fix_body_copy_v2.py --apply
"""
import json, re, sys, os, glob, datetime as dt, shutil

DRY_RUN = '--apply' not in sys.argv

slug_js = open('slug-map.js').read()
m = re.search(r'window\._OP_SLUG_MAP\s*=\s*(\{.*?\});?\s*$', slug_js, re.S)
slug_map = json.loads(m.group(1))
slug_to_id = {v: k for k, v in slug_map.items()}
ops = json.load(open('operators.json'))
op_by_id = {o['id']: o for o in ops}

DR_MARKERS = ('Crystal Water Cave', 'Macao Beach', 'typical Dominican house',
              'Typical Dominican house')

CAT_TAG = {
    'jetski':     ['🌊 Jet Ski', '🏝️ Water Sports'],
    'boat':       ['🚤 Boat Rental', '🌊 Cruise'],
    'fishing':    ['🎣 Fishing', '🚤 Charter'],
    'watersports':['🌊 Water Sports', '🏝️ Beach'],
    'slingshot':  ['🏁 Slingshot', '🚗 Drive'],
    'tour':       ['🗺️ Guided Tour', '🌟 Experience'],
    'jetcar':     ['🚙 Jet Car', '🌊 Water Sports'],
    'atv':        ['🏎️ ATV', '🌳 Off-road'],
    'golfcart':   ['🛺 Golf Cart', '🏖️ Beach Cruise'],
    'aerial':     ['🚁 Aerial', '📷 Scenic'],
    'bikerental': ['🚲 Bike Rental', '🌅 Sightseeing'],
    'scooter':    ['🛴 Scooter', '🌅 Sightseeing'],
}

TAGS_ROW_RE = re.compile(
    r'<div class="tags-row">(.*?)</div>',
    re.S,
)
HIGHLIGHTS_RE = re.compile(
    r'<ul class="highlights-list">.*?</ul>',
    re.S,
)


def process(path: str) -> dict:
    counters = {'changed': 0, 'tags_replaced': 0, 'highlights_stripped': 0,
                'skipped': 0}
    slug = os.path.splitext(os.path.basename(path))[0]
    if slug not in slug_to_id:
        counters['skipped'] = 1
        return counters
    op = op_by_id.get(slug_to_id[slug])
    if not op:
        counters['skipped'] = 1
        return counters

    # Skip real DR operators
    if op.get('zone') in ('puntacana', 'capcana') or 'puntacana' in slug:
        counters['skipped'] = 1
        return counters

    html = open(path).read()
    if not any(marker in html for marker in DR_MARKERS):
        return counters

    new = html

    # (a) Replace .tags-row content with operator-appropriate tags
    cat_tags = CAT_TAG.get(op.get('cat', ''), ['✨ Experience'])
    zone_tag = f'📍 {op.get("zl", "")}'.strip()
    new_tag_html = ''.join(
        f'<span class="tag">{t}</span>' for t in (cat_tags + [zone_tag]) if t.strip('📍 ')
    )

    def _tagsub(m):
        if any(marker in m.group(1) for marker in DR_MARKERS):
            counters['tags_replaced'] += 1
            return f'<div class="tags-row">{new_tag_html}</div>'
        return m.group(0)
    new = TAGS_ROW_RE.sub(_tagsub, new)

    # (b) Strip the entire .highlights-list block when it has DR markers
    def _hsub(m):
        if any(marker in m.group(0) for marker in DR_MARKERS):
            counters['highlights_stripped'] += 1
            return ''
        return m.group(0)
    new = HIGHLIGHTS_RE.sub(_hsub, new)

    if new != html:
        counters['changed'] = 1
        if not DRY_RUN:
            ts = dt.datetime.utcnow().strftime('%Y%m%d-%H%M%S')
            shutil.copy2(path, f'{path}.bak2-{ts}')
            with open(path, 'w') as f:
                f.write(new)
    return counters


agg = {}
for f in sorted(glob.glob('*.html')):
    res = process(f)
    for k, v in res.items():
        agg[k] = agg.get(k, 0) + v

print('=' * 60)
print('BODY-COPY V2 — ' + ('DRY RUN' if DRY_RUN else 'APPLIED'))
print('=' * 60)
print(f'Files changed:           {agg.get("changed", 0)}')
print(f'tags-row replaced:       {agg.get("tags_replaced", 0)}')
print(f'highlights-list removed: {agg.get("highlights_stripped", 0)}')
print(f'Skipped (no op / DR op): {agg.get("skipped", 0)}')
if DRY_RUN:
    print('\nRe-run with --apply.')
