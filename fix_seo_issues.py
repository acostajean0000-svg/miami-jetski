#!/usr/bin/env python3
"""
fix_seo_issues.py — corrige 4 categorías de issues SEO:
  1. 2nd H1 → H2 (12 zone pages)
  2. Agrega og:title donde falte (21 pages)
  3. Acorta 2 titles >70 chars
  4. Acorta 39 descs >160 chars

Uso:
    python3 fix_seo_issues.py           # dry run
    python3 fix_seo_issues.py --apply
"""
from __future__ import annotations
import re, sys, glob, html as html_mod
from collections import defaultdict

DRY_RUN = '--apply' not in sys.argv

TITLE_RE = re.compile(r'(<title[^>]*>)([^<]*)(</title>)', re.I)
META_DESC_RE = re.compile(r'(<meta\s+(?:[^>]*?\s+)?name="description"\s+(?:[^>]*?\s+)?content=)"([^"]*)"', re.I)
OG_DESC_RE = re.compile(r'(<meta\s+(?:[^>]*?\s+)?property="og:description"\s+(?:[^>]*?\s+)?content=)"([^"]*)"', re.I)
OG_TITLE_RE = re.compile(r'<meta\s+(?:[^>]*?\s+)?property="og:title"\s+(?:[^>]*?\s+)?content="([^"]*)"', re.I)
H1_RE = re.compile(r'<h1([^>]*)>(.*?)</h1>', re.I|re.S)
HEAD_CLOSE_RE = re.compile(r'</head>', re.I)

stats = defaultdict(int)

def shorten_text(s, max_len):
    """Acorta sin cortar palabras. Limpia entidades HTML primero."""
    # Decodificar entidades para contar real
    decoded = html_mod.unescape(s)
    if len(decoded) <= max_len:
        return s
    # Trim word-boundary
    cut = decoded[:max_len].rsplit(' ', 1)[0].rstrip(' ·—-,;')
    # No volver a encodificar — perderíamos cambios. Mejor regenerar manual:
    return cut


def fix_file(fp):
    """Aplica los fixes a un archivo. Retorna el contenido nuevo o None si no hay cambios."""
    html = open(fp, encoding='utf-8', errors='ignore').read()
    orig = html

    # ── 1. Doble H1 → 2do como H2 ─────────────────────────────
    h1_matches = list(H1_RE.finditer(html))
    if len(h1_matches) >= 2:
        # Reemplazar el 2do H1 con H2, manteniendo atributos
        m = h1_matches[1]
        h1_full = m.group(0)
        h2_full = '<h2' + m.group(1) + '>' + m.group(2) + '</h2>'
        html = html[:m.start()] + h2_full + html[m.end():]
        stats['h1_to_h2'] += 1

    # ── 2. Acortar title >70 chars ────────────────────────────
    t = TITLE_RE.search(html)
    if t:
        title_text = t.group(2)
        decoded_t = html_mod.unescape(title_text)
        if len(decoded_t) > 70:
            new_t = shorten_text(title_text, 67)  # 67 + ellipsis padding
            if new_t != title_text:
                html = html[:t.start()] + t.group(1) + new_t + t.group(3) + html[t.end():]
                stats['title_shortened'] += 1

    # ── 3. Acortar desc >160 chars ────────────────────────────
    d = META_DESC_RE.search(html)
    if d:
        desc_text = d.group(2)
        decoded_d = html_mod.unescape(desc_text)
        if len(decoded_d) > 160:
            new_d = shorten_text(desc_text, 155)
            if new_d != desc_text:
                # Reemplazar TANTO meta description como og:description (sincronizado)
                html = html[:d.start()] + d.group(1) + '"' + new_d + '"' + html[d.end():]
                # Y og:description si tiene mismo texto
                od = OG_DESC_RE.search(html)
                if od and od.group(2) == desc_text:
                    html = html[:od.start()] + od.group(1) + '"' + new_d + '"' + html[od.end():]
                stats['desc_shortened'] += 1

    # ── 4. Agregar og:title si falta ──────────────────────────
    has_og_title = OG_TITLE_RE.search(html)
    if not has_og_title:
        # Tomar del <title>
        t = TITLE_RE.search(html)
        if t:
            title_for_og = t.group(2)
            # Inyectar antes de </head>
            og_tag = f'\n<meta property="og:title" content="{title_for_og}">'
            m = HEAD_CLOSE_RE.search(html)
            if m:
                html = html[:m.start()] + og_tag + '\n' + html[m.start():]
                stats['og_title_added'] += 1

    if html != orig:
        return html
    return None


# Run
files = sorted(glob.glob('*.html'))
print(f'Procesando {len(files)} HTMLs...\n')

changes = []
for fp in files:
    new_content = fix_file(fp)
    if new_content is not None:
        changes.append((fp, new_content))

print(f'═ FIXES {"(DRY RUN)" if DRY_RUN else "(APLICADOS)"} ═\n')
print(f'  Doble H1 → 2do como H2:    {stats["h1_to_h2"]}')
print(f'  Titles acortados:          {stats["title_shortened"]}')
print(f'  Descriptions acortadas:    {stats["desc_shortened"]}')
print(f'  og:title agregados:        {stats["og_title_added"]}')
print(f'\n  Archivos modificados:      {len(changes)}')

if not DRY_RUN:
    for fp, new in changes:
        with open(fp, 'w', encoding='utf-8') as f:
            f.write(new)
    print(f'\n✓ {len(changes)} archivos escritos')
else:
    print('\nRe-corre con --apply para escribir')
    if changes:
        print(f'\nSample (primeros 3):')
        for fp, _ in changes[:3]:
            print(f'  {fp}')
