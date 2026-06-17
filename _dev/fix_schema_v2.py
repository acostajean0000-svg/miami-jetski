#!/usr/bin/env python3
"""
fix_schema_v2.py — round 2.

After v1 we discovered the bogus content was ALSO in body HTML, not just JSON-LD:
  • Visible "What types of tours does Pink Party Boat offer?" FAQ section.
  • Visible "4.6 / 5.0 Based on 0 verified reviews" rating sidebar.
  • The (4.8, 25) rating pair in operators.json itself is a template default
    (1,323 operators share the exact same pair). Treat it as fake.

This pass:

  1. Drops the entire visible <h2>FAQ …</h2> section + the 5 .faq-item blocks
     that follow it, whenever any contain "Pink Party Boat".
  2. Drops the sidebar rating card whose copy says "Based on 0 verified reviews".
  3. Re-runs the JSON-LD aggregateRating drop for any block matching the fake
     (4.8, 25) template — these slipped through v1.

Idempotent.

Usage:
  python3 fix_schema_v2.py            # dry run
  python3 fix_schema_v2.py --apply
"""
import json, re, sys, os, glob

DRY_RUN = '--apply' not in sys.argv

FAKE_RATING_PAIRS = {(4.6, 0), (4.8, 25)}  # template defaults

# Operator map
slug_js = open('slug-map.js').read()
m = re.search(r'window\._OP_SLUG_MAP\s*=\s*(\{.*?\});?\s*$', slug_js, re.S)
slug_map = json.loads(m.group(1))
slug_to_id = {v: k for k, v in slug_map.items()}
ops = json.load(open('operators.json'))
op_by_id = {o['id']: o for o in ops}

# ── Body FAQ section killer ─────────────────────────────────────────────
# Match <h2>…FAQ…</h2> followed by any number of faq-item divs, as long as
# "Pink Party Boat" appears anywhere in that run.
BODY_FAQ_RE = re.compile(
    r'<h2[^>]*>\s*FAQ[^<]*</h2>\s*'
    r'(?:<div class="faq-item">.*?</div>\s*</div>\s*)+',
    re.S,
)

# ── Sidebar "Based on 0 verified reviews" rating card ───────────────────
FAKE_RATING_CARD_RE = re.compile(
    r'<div class="book-card"[^>]*>\s*'
    r'<div[^>]*>\s*&#?\w*?\s*Rating\s*</div>\s*'
    r'<div[^>]*>\s*[\d.]+\s*/\s*5\.0\s*</div>\s*'
    r'<div[^>]*>\s*Based on 0 verified reviews\s*</div>\s*'
    r'</div>',
    re.S,
)
# Looser fallback for emoji-prefixed Rating label
FAKE_RATING_CARD_RE_LOOSE = re.compile(
    r'<div class="book-card"[^>]*>\s*'
    r'<div[^>]*>[^<]*Rating\s*</div>\s*'
    r'<div[^>]*>[^<]*?\s*/\s*5\.0\s*</div>\s*'
    r'<div[^>]*>\s*Based on 0 verified reviews\s*</div>\s*'
    r'</div>',
    re.S,
)

# ── JSON-LD aggregateRating drop for fake (4.8, 25) ─────────────────────
SCRIPT_RE = re.compile(r'<script\s+type="application/ld\+json">(.*?)</script>', re.S)
AGG_RE = re.compile(r',?\s*"aggregateRating"\s*:\s*\{[^{}]*\}', re.S)


def patch_jsonld(block: str, op: dict) -> tuple[str, int]:
    """Drop aggregateRating from JSON-LD if op's (rating, reviews) is a fake pair."""
    pair = (op.get('rating'), op.get('reviews'))
    if pair not in FAKE_RATING_PAIRS:
        return block, 0
    new, n = AGG_RE.subn('', block, count=1)
    return new, n


def process(path: str) -> dict:
    counters = {'faq_stripped': 0, 'rating_card_stripped': 0,
                'agg_dropped': 0, 'changed': 0}

    slug = os.path.splitext(os.path.basename(path))[0]
    op = op_by_id.get(slug_to_id.get(slug, ''))
    html = open(path).read()
    original = html

    # 1. Strip visible FAQ section iff any item references the Pink template
    def _faq_sub(m):
        if 'Pink Party Boat' in m.group(0):
            counters['faq_stripped'] += 1
            return ''
        return m.group(0)
    html = BODY_FAQ_RE.sub(_faq_sub, html)

    # 2. Strip visible "Based on 0 verified reviews" sidebar card
    new_html, n = FAKE_RATING_CARD_RE_LOOSE.subn('', html)
    if n == 0:
        new_html, n = FAKE_RATING_CARD_RE.subn('', html)
    if n:
        counters['rating_card_stripped'] = n
        html = new_html

    # 3. Drop fake (4.8, 25) aggregateRating from JSON-LD
    if op:
        def _ldsub(m):
            body, dropped = patch_jsonld(m.group(1), op)
            counters['agg_dropped'] += dropped
            return f'<script type="application/ld+json">{body}</script>'
        html = SCRIPT_RE.sub(_ldsub, html)

    if html != original and not DRY_RUN:
        with open(path, 'w') as f:
            f.write(html)
    if html != original:
        counters['changed'] = 1
    return counters


agg = {}
for f in sorted(glob.glob('*.html')):
    res = process(f)
    for k, v in res.items():
        agg[k] = agg.get(k, 0) + v

print('=' * 60)
print('SCHEMA V2 — ' + ('DRY RUN' if DRY_RUN else 'APPLIED'))
print('=' * 60)
for k in ('changed', 'faq_stripped', 'rating_card_stripped', 'agg_dropped'):
    print(f'  {k:<24} {agg.get(k, 0)}')
if DRY_RUN:
    print('\nRe-run with --apply to write changes.')
