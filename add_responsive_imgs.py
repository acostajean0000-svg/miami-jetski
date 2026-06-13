#!/usr/bin/env python3
"""
add_responsive_imgs.py — agregar srcset/sizes a hero <img> de operator pages.

Filestack soporta `w=N` para resize. Generamos srcset con 400w/800w/1200w.
Mobile (narrow viewport) carga 400w (~30 KB vs 100 KB original).

Solo procesa operator pages (con <img loading="eager"> hero único).
"""
import re, glob

# Patrón: encontrar <img> hero (loading="eager" + filestack URL + w=1000)
HERO_RE = re.compile(
    r'(<img\s+src=")(https://cdn\.filestackcontent\.com/[A-Za-z0-9]+/convert\?[^"]*)w=1000([^"]*")(\s[^>]*loading="eager"[^>]*>)',
    re.I
)

updated = 0
total = 0
for fp in glob.glob('*.html'):
    if fp.endswith('-activities.html') or fp in ('index.html', '404.html', 'about.html', 'contact.html'):
        continue
    total += 1
    html = open(fp).read()

    new_html = HERO_RE.sub(
        lambda m: (
            f'{m.group(1)}{m.group(2)}w=800{m.group(3)} '
            f'srcset="{m.group(2)}w=400&fit=max 400w, {m.group(2)}w=800&fit=max 800w, {m.group(2)}w=1200&fit=max 1200w" '
            f'sizes="(max-width:600px) 100vw, (max-width:1200px) 800px, 1200px"'
            f'{m.group(4)}'
        ),
        html,
        count=1
    )
    if new_html != html:
        open(fp, 'w').write(new_html)
        updated += 1

print(f'Procesados: {total} operator pages')
print(f'Actualizados con srcset: {updated}')
