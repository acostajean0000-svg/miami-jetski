#!/usr/bin/env python3
"""Verify every operator card image on every HTML page matches the operator's
canonical `photo` in operators.json.

Matching strategy (in order):
  1. Slug-anchored: parse the card's `<a class="op-detail-link" href="/SLUG">`
     and look up the operator id via slug-map.js → operators.json. This is the
     ONLY reliable identifier because 243 operator names are duplicated across
     553 records.
  2. Name fallback: only used when the card has no detail-link.

Comparison is on the filestack HANDLE (first 15–30 alnum segment after
filestackcontent.com/...), not the full URL — this avoids false positives
from `&` vs `&amp;` encoding differences.

Output:
- Summary table and detailed mismatches.
- `--json output_path` writes a structured report.
- Exit code 0 if every card matches, 1 otherwise.

Usage:
    python3 verify_card_images.py
    python3 verify_card_images.py --json card_mismatch.json
    python3 verify_card_images.py --fix
"""
import argparse
import glob
import html as html_lib
import json
import os
import re
import sys
from collections import defaultdict


# Each entry: (block-start marker, name-pattern for the displayed op-name)
CARD_MARKERS = [
    ('<div class="op-card ', r'<div class="op-name">([^<]+)</div>'),
    ('<div class="city-op-card">', r'<div class="city-op-name">([^<]+)</div>'),
]
IMG_RE = re.compile(
    r'<img src="(https://(?:cdn\.filestackcontent\.com|www\.filepicker\.io/api/file)/[^"]+)"',
    re.IGNORECASE,
)
# Most reliable card → operator identifier: the View-details link's slug
DETAIL_HREF_RE = re.compile(
    r'<a[^>]+class="op-detail-link"[^>]+href="/([^"\s#?]+)"', re.IGNORECASE)
ALT_HREF_RE = re.compile(
    r'<a[^>]+href="/([^"\s#?]+)"[^>]*class="op-detail-link"', re.IGNORECASE)
HANDLE_RE = re.compile(
    r'(?:filestackcontent\.com|filepicker\.io/api/file)/(?:[^/]+/)*?([A-Za-z0-9]{15,30})'
)


def find_blocks(html_str: str, marker: str):
    """Yield (start, end) indices of every top-level block beginning with `marker`."""
    blocks = []
    cursor = 0
    while True:
        start = html_str.find(marker, cursor)
        if start < 0:
            break
        i = start + 1
        depth = 1
        while i < len(html_str) and depth > 0:
            open_tag = html_str.find('<div', i)
            close_tag = html_str.find('</div>', i)
            if close_tag < 0:
                break
            if open_tag < 0 or open_tag > close_tag:
                depth -= 1
                i = close_tag + len('</div>')
            else:
                depth += 1
                i = open_tag + len('<div')
        blocks.append((start, i))
        cursor = i
    return blocks


def normalize_name(raw: str) -> str:
    """Normalize an HTML-encoded display name to lowercase for matching."""
    n = raw.strip()
    n = n.replace("\\'", "'")
    n = html_lib.unescape(n)
    return n.lower()


def extract_handle(url):
    if not url:
        return None
    m = HANDLE_RE.search(url)
    return m.group(1) if m else None


def load_slug_map():
    """Parse slug-map.js → {slug: id} dict."""
    try:
        sm = open('slug-map.js').read()
    except FileNotFoundError:
        return {}
    m = re.search(r'_OP_SLUG_MAP\s*=\s*\{(.*?)\};', sm, re.DOTALL)
    if not m:
        return {}
    id_to_slug = dict(re.findall(r'"([^"]+)":"([^"]+)"', m.group(1)))
    return {slug: oid for oid, slug in id_to_slug.items()}


def build_op_lookup(ops):
    """Return name → operator dict (fallback only)."""
    lookup = {}
    for o in ops:
        if not o.get('photo'):
            continue
        nm = (o.get('name') or '').strip()
        if not nm:
            continue
        key = normalize_name(nm)
        lookup.setdefault(key, o)
        for alt in (key.replace(' – ', ' - '), key.replace(' – ', ': '),
                    key.replace(' — ', ' - '), key.replace(' — ', ': ')):
            lookup.setdefault(alt, o)
    return lookup


def resolve_card_op(block, slug_to_id, by_id, name_lookup, name_str):
    """Identify the canonical operator for a card block.

    Returns (op_dict_or_None, source) where source ∈ {"slug","name",None}.
    """
    href_m = DETAIL_HREF_RE.search(block) or ALT_HREF_RE.search(block)
    if href_m:
        slug = href_m.group(1).rstrip('/').replace('.html', '')
        oid = slug_to_id.get(slug)
        if oid and oid in by_id:
            return by_id[oid], 'slug'
    # Fallback to name match (still ambiguous for duplicate names)
    op = name_lookup.get(normalize_name(name_str))
    if op:
        return op, 'name'
    return None, None


def scan_html(path, slug_to_id, by_id, name_lookup):
    """Yield card records with slug-anchored matching."""
    txt = open(path).read()
    for marker, name_pattern in CARD_MARKERS:
        for start, end in find_blocks(txt, marker):
            block = txt[start:end]
            name_m = re.search(name_pattern, block)
            if not name_m:
                continue
            name = name_m.group(1).strip()
            img_m = IMG_RE.search(block)
            card_img = img_m.group(1) if img_m else None
            op, source = resolve_card_op(block, slug_to_id, by_id, name_lookup, name)
            expected = (op or {}).get('photo')
            card_h = extract_handle(card_img)
            exp_h = extract_handle(expected)
            matched = bool(card_h and exp_h and card_h == exp_h)
            yield {
                'name': name,
                'card_img': card_img,
                'expected': expected,
                'matched': matched,
                'op_found': op is not None,
                'source': source,
                'op_id': (op or {}).get('id'),
            }


def apply_fix(path, slug_to_id, by_id, name_lookup):
    """Rewrite mismatched card images using slug-anchored matching."""
    txt = open(path).read()
    fixed = 0
    for marker, name_pattern in CARD_MARKERS:
        blocks = find_blocks(txt, marker)
        if not blocks:
            continue
        out = []
        last = 0
        for start, end in blocks:
            out.append(txt[last:start])
            block = txt[start:end]
            name_m = re.search(name_pattern, block)
            if name_m:
                op, _ = resolve_card_op(block, slug_to_id, by_id,
                                        name_lookup, name_m.group(1).strip())
                if op and op.get('photo'):
                    exp_h = extract_handle(op['photo'])
                    img_m = IMG_RE.search(block)
                    if img_m and exp_h:
                        card_h = extract_handle(img_m.group(1))
                        if card_h and card_h != exp_h:
                            block = IMG_RE.sub(
                                f'<img src="{op["photo"]}"', block, count=1)
                            fixed += 1
            out.append(block)
            last = end
        out.append(txt[last:])
        txt = ''.join(out)
    if fixed:
        open(path, 'w').write(txt)
    return fixed


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--json', help='write structured report to this path')
    ap.add_argument('--fix', action='store_true', help='write corrections in place')
    ap.add_argument('--missing-only', action='store_true',
                    help='only show cards whose operator was not found')
    ap.add_argument('--limit', type=int, default=50,
                    help='max mismatched cards to print (default 50)')
    args = ap.parse_args()

    ops = json.load(open('operators.json'))
    slug_to_id = load_slug_map()
    by_id = {o['id']: o for o in ops}
    name_lookup = build_op_lookup(ops)
    print(f"Loaded {len(ops):,} operators · "
          f"{len(slug_to_id):,} slug-keys · {len(name_lookup):,} name-keys")

    files = sorted(glob.glob('*.html'))
    total_cards = 0
    matched = 0
    mismatched = []
    orphan_ops = []
    no_image = []
    cards_by_file = defaultdict(int)
    source_counts = defaultdict(int)

    for path in files:
        for card in scan_html(path, slug_to_id, by_id, name_lookup):
            total_cards += 1
            cards_by_file[path] += 1
            source_counts[card['source']] += 1
            if not card['op_found']:
                orphan_ops.append({'file': path, **card})
                continue
            if not card['card_img']:
                no_image.append({'file': path, **card})
                continue
            if card['matched']:
                matched += 1
            else:
                mismatched.append({'file': path, **card})

    print(f"\nScanned {sum(1 for v in cards_by_file.values() if v):,} files with card structure")
    print(f"Total cards: {total_cards:,}  (slug-anchored: {source_counts['slug']:,}, "
          f"name-fallback: {source_counts['name']:,}, unresolved: {source_counts[None]:,})")
    print(f"  ✓ Matched: {matched:,}")
    print(f"  ✗ Mismatched (wrong img): {len(mismatched):,}")
    print(f"  ⚠ Orphan operator (no match in JSON): {len(orphan_ops):,}")
    print(f"  ⚠ Card without <img>: {len(no_image):,}")

    if args.fix and mismatched:
        files_with_mismatch = sorted(set(m['file'] for m in mismatched))
        print(f"\n--fix: rewriting cards across {len(files_with_mismatch)} files...")
        total_fixed = 0
        for path in files_with_mismatch:
            n = apply_fix(path, slug_to_id, by_id, name_lookup)
            total_fixed += n
            if n:
                print(f"  {path}: {n} fixes")
        print(f"\nTotal fixes applied: {total_fixed}")

    targets = orphan_ops if args.missing_only else mismatched
    label = ("Orphan operators (no match)"
             if args.missing_only else "Mismatched cards (image ≠ operator.photo)")
    if targets:
        print(f"\n=== {label} (first {args.limit}) ===")
        for r in targets[:args.limit]:
            print(f"  {r['file']}  [{r.get('source') or '-'}]  op={r.get('op_id') or '-'}")
            print(f"    name:     {r['name']}")
            print(f"    card_img: {(r.get('card_img') or '(none)')[:90]}")
            if not args.missing_only:
                print(f"    expected: {(r.get('expected') or '(none)')[:90]}")
            print()

    if args.json:
        report = {
            'summary': {
                'total_files_with_cards': sum(1 for v in cards_by_file.values() if v),
                'total_cards': total_cards,
                'matched': matched,
                'mismatched': len(mismatched),
                'orphan_ops': len(orphan_ops),
                'no_image': len(no_image),
                'source_counts': dict(source_counts),
            },
            'mismatched': mismatched,
            'orphan_ops': orphan_ops,
            'no_image': no_image,
        }
        with open(args.json, 'w') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print(f"\nReport written to {args.json}")

    return 0 if not mismatched else 1


if __name__ == '__main__':
    sys.exit(main())
