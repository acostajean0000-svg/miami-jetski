#!/usr/bin/env python3
"""update_op_photo.py — Safely update a single operator's photo.

Why this exists: 243 operator names are duplicated across 553 records, so the
old name-based card propagation routinely overwrote the wrong listing cards.
This script uses SLUG-ANCHORED matching: every listing card's
`<a class="op-detail-link" href="/SLUG">` is the canonical identifier.

Usage:
    python3 update_op_photo.py <SLUG> <HANDLE>
    python3 update_op_photo.py <SLUG> <FULL_FILESTACK_URL>

Examples:
    python3 update_op_photo.py top-line-watersports-parasailing-miami PHbSBACpQmStPYSbnUuk
    python3 update_op_photo.py top-line-watersports-parasailing-miami \
        'https://cdn.filestackcontent.com/rotate=deg:exif/.../PHbSBACpQmStPYSbnUuk'

The script:
  1) Resolves SLUG → operator id via slug-map.js.
  2) Updates operators.json + operators-slim.json with the standard
     /convert?... transform URL.
  3) Replaces filestack URLs on the operator's own static HTML page
     (top-level <img>, og:image, twitter:image only — NOT listing cards
     within the page).
  4) Updates listing-card images on OTHER HTML files by matching the
     `op-detail-link` href to this slug (id-equivalent), never by name.
"""
import argparse
import glob
import json
import os
import re
import sys

SUFFIX = "/convert?cache=true&compress=true&quality=90&format=webp&rotate=exif&w=1000&fit=max"
HANDLE_RE_LOOSE = re.compile(r'([A-Za-z0-9]{15,30})')
HANDLE_RE = re.compile(
    r'(?:filestackcontent\.com|filepicker\.io/api/file)/(?:[^/]+/)*?([A-Za-z0-9]{15,30})')

DETAIL_HREF_RE = re.compile(
    r'<a[^>]+class="op-detail-link"[^>]+href="/([^"\s#?]+)"', re.IGNORECASE)
ALT_HREF_RE = re.compile(
    r'<a[^>]+href="/([^"\s#?]+)"[^>]*class="op-detail-link"', re.IGNORECASE)
IMG_RE = re.compile(
    r'<img src="(https://(?:cdn\.filestackcontent\.com|www\.filepicker\.io/api/file)/[^"]+)"',
    re.IGNORECASE)

CARD_MARKERS = ['<div class="op-card ', '<div class="city-op-card">']


def extract_handle(handle_or_url):
    """Accept a bare handle or a full Filestack URL; return the handle."""
    if not handle_or_url:
        return None
    m = HANDLE_RE.search(handle_or_url)
    if m:
        return m.group(1)
    m = HANDLE_RE_LOOSE.match(handle_or_url.strip())
    return m.group(1) if m else None


def load_slug_map():
    sm = open('slug-map.js').read()
    m = re.search(r'_OP_SLUG_MAP\s*=\s*\{(.*?)\};', sm, re.DOTALL)
    id_to_slug = dict(re.findall(r'"([^"]+)":"([^"]+)"', m.group(1)))
    return id_to_slug, {slug: oid for oid, slug in id_to_slug.items()}


def find_blocks(html_str, marker):
    blocks = []
    cursor = 0
    while True:
        start = html_str.find(marker, cursor)
        if start < 0:
            break
        i = start + 1
        depth = 1
        while i < len(html_str) and depth > 0:
            ot = html_str.find('<div', i)
            ct = html_str.find('</div>', i)
            if ct < 0:
                break
            if ot < 0 or ot > ct:
                depth -= 1
                i = ct + len('</div>')
            else:
                depth += 1
                i = ot + len('<div')
        blocks.append((start, i))
        cursor = i
    return blocks


def update_own_page(fname, new_url):
    """Rewrite top-level filestack img on the operator's own page.

    Carefully avoids touching listing cards (op-card / city-op-card blocks)
    embedded on the same page.
    """
    if not os.path.exists(fname):
        return 0
    txt = open(fname).read()
    # Step 1: mask out card blocks so we don't clobber them
    card_ranges = []
    for marker in CARD_MARKERS:
        card_ranges.extend(find_blocks(txt, marker))
    card_ranges.sort()

    def in_card(pos):
        for s, e in card_ranges:
            if s <= pos < e:
                return True
        return False

    pattern = re.compile(
        r'https://(?:cdn\.filestackcontent\.com|www\.filepicker\.io/api/file)/[^"\'\s<>]+'
    )
    pieces = []
    cursor = 0
    replacements = 0
    for m in pattern.finditer(txt):
        if in_card(m.start()):
            continue
        pieces.append(txt[cursor:m.start()])
        pieces.append(new_url)
        cursor = m.end()
        replacements += 1
    pieces.append(txt[cursor:])
    new_txt = ''.join(pieces)
    if replacements == 0:
        # Fallback: at least update og:image / twitter:image
        for og_pat in (r'(<meta property="og:image" content=")[^"]*(")',
                       r'(<meta name="twitter:image" content=")[^"]*(")'):
            new_txt, n = re.subn(og_pat, rf'\1{new_url}\2', new_txt, count=1)
            replacements += n
    if new_txt != txt:
        open(fname, 'w').write(new_txt)
    return replacements


def propagate_cards(target_slug, new_url, target_handle, own_page):
    """Update listing-card <img> on every OTHER page that links to this slug."""
    fixes = 0
    files = 0
    for path in sorted(glob.glob('*.html')):
        if path == own_page:
            continue
        txt = open(path).read()
        all_blocks = []
        for marker in CARD_MARKERS:
            for s, e in find_blocks(txt, marker):
                all_blocks.append((s, e))
        all_blocks.sort()
        if not all_blocks:
            continue
        out = []
        last = 0
        changed = 0
        for s, e in all_blocks:
            out.append(txt[last:s])
            block = txt[s:e]
            href_m = DETAIL_HREF_RE.search(block) or ALT_HREF_RE.search(block)
            if href_m:
                card_slug = href_m.group(1).rstrip('/').replace('.html', '')
                if card_slug == target_slug:
                    img_m = IMG_RE.search(block)
                    if img_m:
                        card_h = extract_handle(img_m.group(1))
                        if card_h and card_h != target_handle:
                            block = IMG_RE.sub(
                                f'<img src="{new_url}"', block, count=1)
                            changed += 1
            out.append(block)
            last = e
        out.append(txt[last:])
        if changed:
            open(path, 'w').write(''.join(out))
            fixes += changed
            files += 1
    return fixes, files


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('slug')
    ap.add_argument('handle_or_url',
                    help='Bare handle or full filestack URL (transform-form OK)')
    ap.add_argument('--name', help='Also rename the operator')
    ap.add_argument('--cat', help='Also change category')
    args = ap.parse_args()

    handle = extract_handle(args.handle_or_url)
    if not handle:
        print(f"ERROR: could not extract handle from '{args.handle_or_url}'")
        return 1
    new_url = f"https://cdn.filestackcontent.com/{handle}{SUFFIX}"

    id_to_slug, slug_to_id = load_slug_map()
    oid = slug_to_id.get(args.slug)
    if not oid:
        print(f"ERROR: slug '{args.slug}' not found in slug-map.js")
        return 1

    ops_full = json.load(open('operators.json'))
    ops_slim = json.load(open('operators-slim.json'))
    op = next((o for o in ops_full if o['id'] == oid), None)
    if not op:
        print(f"ERROR: operator id {oid} not in operators.json")
        return 1

    print(f"Slug:     {args.slug}")
    print(f"Operator: {oid} {op.get('name','?')}")
    print(f"Old:      {(op.get('photo') or '')[:90]}")
    print(f"New:      {new_url[:90]}")

    op['photo'] = new_url
    if args.name:
        op['name'] = args.name
    if args.cat:
        op['cat'] = args.cat

    for o in ops_slim:
        if o['id'] == oid:
            o['photo'] = new_url
            if args.name:
                o['name'] = args.name
            if args.cat:
                o['cat'] = args.cat
            break

    json.dump(ops_full, open('operators.json', 'w'),
              ensure_ascii=False, separators=(',', ':'))
    json.dump(ops_slim, open('operators-slim.json', 'w'),
              ensure_ascii=False, separators=(',', ':'))

    own_page = f"{args.slug}.html"
    own_replacements = update_own_page(own_page, new_url)
    card_fixes, files_touched = propagate_cards(
        args.slug, new_url, handle, own_page)

    print(f"\nOwn page URL replacements (excluding listing cards): {own_replacements}")
    print(f"Listing cards updated: {card_fixes} across {files_touched} files")
    return 0


if __name__ == '__main__':
    sys.exit(main())
