#!/usr/bin/env python3
"""
add_operator_preloads.py — agregar preload hints en operator pages.

Objetivo: mejorar LCP (Largest Contentful Paint).

Para cada operator page:
  1. <link rel="preconnect" href="https://cdn.filestackcontent.com"> (DNS+TCP+TLS upfront)
  2. <link rel="preload" as="image" href="HERO_URL" fetchpriority="high"> (LCP element)
  3. <link rel="preconnect" href="https://fareharbor.com" crossorigin> (iframe que carga después)

Solo procesa operator pages (no zone activities ni statics).
Skip si ya tiene preload de imagen.

Uso:
    python3 add_operator_preloads.py            # dry run
    python3 add_operator_preloads.py --apply
"""
from __future__ import annotations
import re, sys, glob
from collections import defaultdict

DRY_RUN = '--apply' not in sys.argv

# Patrones
OG_IMAGE_RE = re.compile(r'<meta\s+property="og:image"\s+content="([^"]+)"', re.I)
HAS_PRELOAD_IMG = re.compile(r'<link[^>]+rel="preload"[^>]+as="image"', re.I)
HEAD_CLOSE = re.compile(r'</head>', re.I)
CHARSET_RE = re.compile(r'<meta\s+charset[^>]+>', re.I)

# Skip pages
SKIP = {'404.html', 'webhook-tester.html', 'about.html', 'contact.html',
        'privacy.html', 'terms.html', 'partners.html', 'index.html'}


def has_zone_landing(fp):
    return fp.endswith('-activities.html') or fp.endswith('-water-sports.html') or \
           fp == 'boat-rentals-florida.html' or fp == 'everglades-tours-rentals.html' or \
           fp == 'everglades-airboat-tours.html'


def fix_page(fp):
    if fp in SKIP or has_zone_landing(fp):
        return None, 'skip'

    html = open(fp).read()

    # ¿Tiene og:image?
    m = OG_IMAGE_RE.search(html)
    if not m:
        return None, 'no_og_image'
    hero_url = m.group(1)

    # ¿Ya tiene preload de imagen?
    if HAS_PRELOAD_IMG.search(html):
        return None, 'already_preloaded'

    # Determinar si la imagen viene de Filestack
    filestack = 'filestackcontent.com' in hero_url
    has_filestack_pc = 'preconnect" href="https://cdn.filestackcontent.com' in html
    has_fareharbor_pc = 'preconnect" href="https://fareharbor.com' in html

    # Construir bloque de preloads
    preloads = []
    if filestack and not has_filestack_pc:
        preloads.append('<link rel="preconnect" href="https://cdn.filestackcontent.com" crossorigin>')
    preloads.append(f'<link rel="preload" as="image" href="{hero_url}" fetchpriority="high">')
    # FareHarbor connection (booking iframe)
    if 'fareharbor.com' in html and not has_fareharbor_pc:
        preloads.append('<link rel="preconnect" href="https://fareharbor.com" crossorigin>')

    inject = '\n  ' + '\n  '.join(preloads) + '\n'

    # Insertar después de <meta charset>
    cm = CHARSET_RE.search(html)
    if cm:
        new_html = html[:cm.end()] + inject + html[cm.end():]
    else:
        # Fallback: justo antes de </head>
        hm = HEAD_CLOSE.search(html)
        if not hm:
            return None, 'no_head'
        new_html = html[:hm.start()] + inject + html[hm.start():]

    return new_html, f'ok ({len(preloads)} preloads)'


def main():
    files = sorted(glob.glob('*.html'))
    print(f'Procesando {len(files)} HTMLs...\n')

    stats = defaultdict(int)
    changes = []
    for fp in files:
        new, status = fix_page(fp)
        stats[status.split(' ')[0]] += 1
        if new:
            changes.append((fp, new))

    print(f'═ RESULTADO {"(DRY RUN)" if DRY_RUN else "(APLICADO)"} ═')
    for s, n in sorted(stats.items(), key=lambda x: -x[1]):
        print(f'  {s:<25} {n}')

    print(f'\nArchivos a modificar: {len(changes)}')

    if changes and DRY_RUN:
        print(f'\nSample (primeros 3):')
        for fp, new in changes[:3]:
            # Mostrar las líneas de preload
            preloads = re.findall(r'<link[^>]+rel="(?:preload|preconnect)"[^>]*>', new)
            print(f'\n  {fp}')
            for p in preloads:
                print(f'    {p[:100]}')

    if not DRY_RUN:
        for fp, new in changes:
            with open(fp, 'w') as f:
                f.write(new)
        print(f'\n✓ {len(changes)} archivos escritos')
    else:
        print('\nRe-corre con --apply para escribir')


if __name__ == '__main__':
    main()
