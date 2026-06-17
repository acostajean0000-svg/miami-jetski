#!/usr/bin/env python3
"""
build_sitemap_index.py — divide sitemap.xml de 969KB en sub-sitemaps por zona.

Beneficios:
  - Google crawlea sitemaps en paralelo → indexación más rápida
  - Cada zona puede actualizarse independiente
  - Si una zona crece >50,000 URLs (limit de Google), ya está modular

Output:
  sitemap.xml          → sitemap INDEX (lista de sub-sitemaps)
  sitemaps/zone-X.xml  → sub-sitemap por zona
  sitemaps/static.xml  → páginas estáticas (about, contact, etc.)
  sitemaps/landing.xml → zone activity pages

Uso:
    python3 build_sitemap_index.py            # dry run
    python3 build_sitemap_index.py --apply
"""
from __future__ import annotations
import re, json, sys, os
from collections import defaultdict
from xml.sax.saxutils import escape

DRY_RUN = '--apply' not in sys.argv
DOMAIN = 'https://miamijetskiboatrentals.com'

def main():
    # Parse current sitemap
    sm = open('sitemap.xml').read()
    url_blocks = re.findall(r'<url>(.+?)</url>', sm, re.S)
    print(f'Parsing {len(url_blocks)} URLs del sitemap actual...')

    # Load ops + slug map
    ops = json.load(open('operators-slim.json'))
    zone_of_op = {o['id']: o.get('zone', 'misc') for o in ops}

    sm_js = open('slug-map.js').read()
    pairs = re.findall(r'"([^"]+)"\s*:\s*"([^"]+)"', sm_js)
    slug_to_op = {slug: op_id for op_id, slug in pairs}

    # Static URLs
    STATIC = {'about', 'contact', 'privacy', 'terms', 'partners',
              'jet-ski-rentals-miami', 'boat-rentals-florida',
              'everglades-tours-rentals', 'everglades-airboat-tours',
              'amelia-island-water-sports', 'cocoa-beach-water-sports',
              'daytona-beach-water-sports', 'jacksonville-water-sports',
              'new-smyrna-beach-water-sports', 'northeast-florida-water-sports',
              'space-coast-water-sports', 'st-augustine-water-sports'}

    # Group blocks
    by_bucket = defaultdict(list)
    for block in url_blocks:
        loc_m = re.search(r'<loc>([^<]+)</loc>', block)
        if not loc_m: continue
        url = loc_m.group(1)
        slug = url.replace(DOMAIN + '/', '').strip('/')

        # Homepage
        if not slug or url == DOMAIN + '/':
            by_bucket['static'].append(block)
            continue

        # Zone landing pages
        if slug.endswith('-activities'):
            by_bucket['landing'].append(block)
            continue

        # Static pages
        if slug in STATIC:
            by_bucket['static'].append(block)
            continue

        # Operator pages
        op_id = slug_to_op.get(slug)
        if op_id:
            zone = zone_of_op.get(op_id, 'misc')
            by_bucket[f'zone-{zone}'].append(block)
        else:
            by_bucket['misc'].append(block)

    print(f'\nDistribución en buckets:')
    for bucket in sorted(by_bucket.keys()):
        print(f'  {bucket:<20} {len(by_bucket[bucket]):>5}')

    # Build sub-sitemaps
    if not DRY_RUN:
        os.makedirs('sitemaps', exist_ok=True)

    sitemap_files = []
    for bucket, blocks in sorted(by_bucket.items()):
        filename = f'sitemaps/{bucket}.xml'
        content = '<?xml version="1.0" encoding="UTF-8"?>\n'
        content += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        for block in blocks:
            content += f'  <url>{block.strip()}</url>\n'
        content += '</urlset>\n'

        if not DRY_RUN:
            with open(filename, 'w') as f:
                f.write(content)

        sitemap_files.append(filename)
        # Hash size para logs
        sz_kb = len(content) / 1024
        print(f'  → {filename:<35} {sz_kb:>5.0f} KB · {len(blocks)} URLs')

    # Build sitemap index
    today = '2026-06-05'
    index = '<?xml version="1.0" encoding="UTF-8"?>\n'
    index += '<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for f in sorted(sitemap_files):
        index += '  <sitemap>\n'
        index += f'    <loc>{DOMAIN}/{f}</loc>\n'
        index += f'    <lastmod>{today}</lastmod>\n'
        index += '  </sitemap>\n'
    index += '</sitemapindex>\n'

    if not DRY_RUN:
        # Backup current sitemap.xml
        if os.path.exists('sitemap.xml'):
            os.rename('sitemap.xml', 'sitemap-flat.xml.bak')
        with open('sitemap.xml', 'w') as f:
            f.write(index)
        print(f'\n✓ sitemap.xml (NUEVO INDEX): {len(index)/1024:.1f} KB · {len(sitemap_files)} sub-sitemaps')
        print(f'✓ sitemap-flat.xml.bak (backup del antiguo plano)')
    else:
        print(f'\nINDEX final ({len(index)/1024:.1f} KB):')
        print(index[:800])
        print('...')
        print('\nRe-corre con --apply para escribir')


if __name__ == '__main__':
    main()
