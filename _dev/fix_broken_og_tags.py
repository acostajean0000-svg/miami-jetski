#!/usr/bin/env python3
"""
fix_broken_og_tags.py — repara og:title/og:description con quotes no escapadas.

Bug: el generator escribió:
  <meta property="og:title" content=""Bettsy" 60' Yacht - Daytime..."
        en lugar de
  <meta property="og:title" content="&quot;Bettsy&quot; 60' Yacht - Daytime...">

Estrategia: para cada archivo con HTML roto, reconstruir og:title y og:description
extrayendo del <title> y meta description que sí son válidos.

Uso:
    python3 fix_broken_og_tags.py           # dry run
    python3 fix_broken_og_tags.py --apply
"""
from __future__ import annotations
import re, sys, glob, html as html_mod
from collections import defaultdict

DRY_RUN = '--apply' not in sys.argv

TITLE_RE = re.compile(r'<title[^>]*>([^<]*)</title>', re.I)
META_DESC_RE = re.compile(r'<meta\s+(?:[^>]*?\s+)?name="description"\s+(?:[^>]*?\s+)?content="([^"]*(?:"[^"<>]+"[^"]*)*?)"\s*/?>', re.I)

# Patrones para detectar el bug
# Bug pattern: content=""TEXT_WITH_QUOTES"
BROKEN_OG_TITLE = re.compile(r'<meta\s+property="og:title"\s+content=""[^>]+>', re.I)
BROKEN_OG_DESC  = re.compile(r'<meta\s+property="og:description"\s+content=""[^>]+>', re.I)

# Para los pages sin og:title ni la versión rota: solo lo añadimos
HAS_OG_TITLE = re.compile(r'<meta\s+(?:[^>]*?\s+)?property="og:title"', re.I)
HAS_OG_DESC  = re.compile(r'<meta\s+(?:[^>]*?\s+)?property="og:description"', re.I)
HEAD_CLOSE   = re.compile(r'</head>', re.I)

stats = defaultdict(int)

def repair_file(fp):
    html = open(fp, encoding='utf-8', errors='ignore').read()
    orig = html
    changed = False

    # Extraer title y description "limpios" del archivo
    title_m = TITLE_RE.search(html)
    if not title_m:
        return None
    title_text = title_m.group(1).strip()
    # Escapar para uso en attribute
    title_attr = html_mod.escape(title_text, quote=True)

    # Description del meta name="description" (que parece estar OK porque usa &quot;)
    # Pero su contenido puede tener `"` directas si el generator falló también ahí
    # Para evitar romper más: usaremos title como og:description backup si falta
    desc_attr = title_attr  # fallback

    # Intentar extraer desc real con regex más permisiva
    d = re.search(r'<meta\s+name="description"\s+content="((?:[^"]|&quot;|&#x27;|&#34;|&\w+;)+)"', html, re.I)
    if d:
        desc_attr = d.group(1)
        # Verificar que sea válida (sin " sin escapar)
        # Decodificar para chequeo, pero mantener original si parece OK
        try:
            decoded = html_mod.unescape(desc_attr)
            if '"' in decoded and '&quot;' not in desc_attr:
                # Hay quotes no escapadas — re-escapar
                desc_attr = html_mod.escape(decoded, quote=True)
        except:
            pass

    # ── FIX 1: og:title roto → reemplazar ───────────
    bt = BROKEN_OG_TITLE.search(html)
    if bt:
        new_tag = f'<meta property="og:title" content="{title_attr}">'
        html = html[:bt.start()] + new_tag + html[bt.end():]
        stats['og_title_repaired'] += 1
        changed = True

    # ── FIX 2: og:description roto → reemplazar ──────
    bd = BROKEN_OG_DESC.search(html)
    if bd:
        new_tag = f'<meta property="og:description" content="{desc_attr}">'
        html = html[:bd.start()] + new_tag + html[bd.end():]
        stats['og_desc_repaired'] += 1
        changed = True

    # ── FIX 3: og:title ausente → agregar ───────────
    if not HAS_OG_TITLE.search(html):
        new_tag = f'\n<meta property="og:title" content="{title_attr}">\n'
        m = HEAD_CLOSE.search(html)
        if m:
            html = html[:m.start()] + new_tag + html[m.start():]
            stats['og_title_added'] += 1
            changed = True

    # ── FIX 4: og:description ausente → agregar ──────
    if not HAS_OG_DESC.search(html):
        new_tag = f'<meta property="og:description" content="{desc_attr}">\n'
        m = HEAD_CLOSE.search(html)
        if m:
            html = html[:m.start()] + new_tag + html[m.start():]
            stats['og_desc_added'] += 1
            changed = True

    return html if changed else None


files = sorted(glob.glob('*.html'))
print(f'Procesando {len(files)} HTMLs...\n')

changes = []
for fp in files:
    new = repair_file(fp)
    if new:
        changes.append((fp, new))

print(f'═ FIXES {"(DRY RUN)" if DRY_RUN else "(APLICADOS)"} ═')
print(f'  og:title reparados (eran rotos):    {stats["og_title_repaired"]}')
print(f'  og:title agregados (faltaban):       {stats["og_title_added"]}')
print(f'  og:description reparados (rotos):    {stats["og_desc_repaired"]}')
print(f'  og:description agregados (faltaban): {stats["og_desc_added"]}')
print(f'\n  Archivos modificados:                {len(changes)}')

if changes:
    print('\nMuestra (primeros 5):')
    for fp, _ in changes[:5]:
        print(f'  {fp}')

if not DRY_RUN:
    for fp, new in changes:
        with open(fp, 'w', encoding='utf-8') as f:
            f.write(new)
    print(f'\n✓ {len(changes)} archivos escritos')
else:
    print('\nRe-corre con --apply para escribir')
