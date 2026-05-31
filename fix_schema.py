#!/usr/bin/env python3
"""
fix_schema.py — surgical SEO schema cleanup.

For every operator HTML page (mapped via slug-map.js → operators.json):

  1. TouristAttraction JSON-LD block:
       - description   -> replaced with real `desc` from operators.json
       - aggregateRating -> dropped entirely when reviews == 0;
                            otherwise rewritten with real rating + reviews
       - priceRange    -> "From $<real price>"
       - Other fields (name, url, address, geo, image) are left alone.

  2. FAQPage JSON-LD block:
       - Removed wholesale when it contains the wrong "Pink Party Boat" template.

Pages whose slug doesn't map to an operator (landing pages, /about, /index,
zone pages, /404) are skipped entirely.

Usage:
  python3 fix_schema.py            # dry-run, prints counts only
  python3 fix_schema.py --apply    # writes changes in place
"""
import json, re, sys, os, glob, shutil, datetime as dt

DRY_RUN = '--apply' not in sys.argv

# ── Load operator data ─────────────────────────────────────────────────────
slug_js = open('slug-map.js').read()
m = re.search(r'window\._OP_SLUG_MAP\s*=\s*(\{.*?\});?\s*$', slug_js, re.S)
slug_map = json.loads(m.group(1))            # id -> slug
slug_to_id = {v: k for k, v in slug_map.items()}
ops = json.load(open('operators.json'))
op_by_id = {o['id']: o for o in ops}

# ── Regex helpers ──────────────────────────────────────────────────────────
SCRIPT_RE = re.compile(
    r'<script\s+type="application/ld\+json">(.*?)</script>',
    re.S
)
FAQ_PINK_RE = re.compile(
    r'<script\s+type="application/ld\+json">\s*\{[^<]*?Pink Party Boat[^<]*?\}\s*</script>\s*',
    re.S
)

def patch_tourist_attraction(block_text: str, op: dict) -> tuple[str, dict]:
    """Surgically rewrite description / aggregateRating / priceRange.
    Returns (new_block_text, {flag counts})."""
    flags = {'desc': 0, 'rating_dropped': 0, 'rating_rewritten': 0, 'price_fixed': 0}
    new = block_text

    # 1. description — only touch if it has the Pink Party Boat template
    if 'Pink Party Boat' in new:
        real_desc = op.get('desc', '').strip().replace('"', '\\"')
        new = re.sub(
            r'"description"\s*:\s*"[^"]*"',
            f'"description":"{real_desc}"',
            new,
            count=1,
        )
        flags['desc'] = 1

    # 2. aggregateRating
    reviews = int(op.get('reviews', 0) or 0)
    rating  = op.get('rating')
    rating_block_re = re.compile(
        r',?\s*"aggregateRating"\s*:\s*\{[^{}]*\}',
        re.S,
    )
    if reviews == 0:
        # drop the entire field if it's there
        if rating_block_re.search(new):
            new = rating_block_re.sub('', new, count=1)
            flags['rating_dropped'] = 1
    else:
        # rewrite with real numbers
        repl = (
            f',"aggregateRating":{{"@type":"AggregateRating",'
            f'"ratingValue":"{rating}","reviewCount":"{reviews}","bestRating":"5"}}'
        )
        if rating_block_re.search(new):
            new = rating_block_re.sub(repl, new, count=1)
            flags['rating_rewritten'] = 1

    # 3. priceRange "From $45" -> real
    price = op.get('price')
    if price is not None:
        price_str = f'{int(price)}' if float(price).is_integer() else f'{price}'
        new = re.sub(
            r'"priceRange"\s*:\s*"From \$45"',
            f'"priceRange":"From ${price_str}"',
            new,
            count=1,
        )
        # detect whether we changed anything
        if '"priceRange":"From $45"' not in block_text and f'"priceRange":"From ${price_str}"' in new:
            pass  # nothing to count
        if '"priceRange":"From $45"' in block_text and '"priceRange":"From $45"' not in new:
            flags['price_fixed'] = 1

    return new, flags


def process_file(path: str) -> dict:
    slug = os.path.splitext(os.path.basename(path))[0]
    if slug not in slug_to_id:
        return {'skipped_no_slug': 1}
    op = op_by_id.get(slug_to_id[slug])
    if not op:
        return {'skipped_no_op': 1}

    html = open(path).read()
    original = html

    counters = {'desc': 0, 'rating_dropped': 0, 'rating_rewritten': 0,
                'price_fixed': 0, 'faq_removed': 0}

    # Step A — patch TouristAttraction block(s)
    def _ta_sub(m):
        inner = m.group(1)
        if '"@type":"TouristAttraction"' not in inner:
            return m.group(0)
        new_inner, flags = patch_tourist_attraction(inner, op)
        for k, v in flags.items(): counters[k] += v
        return f'<script type="application/ld+json">{new_inner}</script>'
    html = SCRIPT_RE.sub(_ta_sub, html)

    # Step B — strip the entire Pink-Party-Boat FAQ <script>
    new_html, n_faq = FAQ_PINK_RE.subn('', html)
    if n_faq:
        counters['faq_removed'] = n_faq
        html = new_html

    if html != original and not DRY_RUN:
        with open(path, 'w') as f:
            f.write(html)

    counters['changed'] = 1 if html != original else 0
    return counters


# ── Main ───────────────────────────────────────────────────────────────────
files = sorted(glob.glob('*.html'))
agg = {'desc': 0, 'rating_dropped': 0, 'rating_rewritten': 0,
       'price_fixed': 0, 'faq_removed': 0, 'changed': 0,
       'skipped_no_slug': 0, 'skipped_no_op': 0, 'total': 0}
for f in files:
    res = process_file(f)
    for k, v in res.items():
        agg[k] = agg.get(k, 0) + v
    agg['total'] += 1

print('=' * 60)
print('SCHEMA CLEANUP — ' + ('DRY RUN (no files written)' if DRY_RUN else 'APPLIED'))
print('=' * 60)
print(f'HTML files scanned          : {agg["total"]}')
print(f'Skipped (no slug map)       : {agg["skipped_no_slug"]}')
print(f'Skipped (slug w/o operator) : {agg["skipped_no_op"]}')
print()
print(f'Files changed               : {agg["changed"]}')
print(f'  description rewritten     : {agg["desc"]}')
print(f'  aggregateRating dropped   : {agg["rating_dropped"]}')
print(f'  aggregateRating rewritten : {agg["rating_rewritten"]}')
print(f'  priceRange fixed          : {agg["price_fixed"]}')
print(f'  FAQ block removed         : {agg["faq_removed"]}')
print()
if DRY_RUN:
    print('Re-run with --apply to write changes.')
