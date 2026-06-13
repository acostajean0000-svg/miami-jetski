#!/usr/bin/env python3
"""
refactor_zone_pages.py — extrae el JSON inline de zone-activities HTMLs
y reemplaza con fetch('/data/X.json') al cargar.

Paso 1: regenerar /data/X.json desde operators-slim.json actualizado
Paso 2: reemplazar `const _ops = [...]` + `const r = { json: async () => _ops }`
         con `const r = await fetch('/data/'+DATA_KEY+'.json')`

Uso:
    python3 refactor_zone_pages.py            # dry run
    python3 refactor_zone_pages.py --apply
"""
from __future__ import annotations
import re, sys, json, glob, os
from collections import Counter, defaultdict

DRY_RUN = '--apply' not in sys.argv

# Mapeo: ZONE_KEY del HTML → archivo /data/X.json a cargar
DATA_MAP = {
    'broward':       'broward',
    'cancun':        'cancun',
    'daytona':       'nefl',         # subsection
    'gulf':          'gulf',
    'hawaii':        'hawaii',
    'jacksonville':  'nefl',         # subsection
    'keywest':       'keywest',
    'miami':         'miami',
    'nefl':          'nefl',
    'orlando':       'orlando',
    'palmbeach':     'palmbeach',
    'puntacana':     'puntacana',
    'space':         'space',
    'centralfl':     'centralfl',
    'everglades':    'everglades',
    'westfl':        'westfl',
}

# Patrón a reemplazar (encontrado en cada zone page)
INLINE_PATTERN = re.compile(
    r'const\s+_ops\s*=\s*\[\{[^]]+?\}\]\s*;\s*'
    r'const\s+r\s*=\s*\{\s*json:\s*async\s*\(\)\s*=>\s*_ops\s*\}\s*;',
    re.S
)


def regenerate_data_files():
    """Regenera /data/X.json desde operators-slim.json (incluye cats nuevas)."""
    ops = json.load(open('operators-slim.json'))
    print(f'Total ops en operators-slim.json: {len(ops)}')

    # Agrupar por zone
    by_zone = defaultdict(list)
    for o in ops:
        by_zone[o.get('zone', '')].append(o)

    print(f'\nRegenerando data files:')
    updates = 0
    for zone, lst in sorted(by_zone.items()):
        if not zone: continue
        fp = f'data/{zone}.json'
        existed = os.path.exists(fp)
        old_n = 0
        if existed:
            try: old_n = len(json.load(open(fp)))
            except: pass
        with open(fp, 'w') as f:
            json.dump(lst, f, ensure_ascii=False, separators=(',', ':'))
        new_n = len(lst)
        delta = new_n - old_n
        status = '+' if delta > 0 else ('=' if delta == 0 else '')
        print(f'  {fp:<30} {new_n:>5} ops  ({old_n} prev, {delta:+d})')
        updates += 1
    print(f'\nTotal: {updates} archivos regenerados')


def refactor_html(fp):
    """Refactoriza un HTML: extrae _ops inline y reemplaza con fetch."""
    html = open(fp).read()

    # Encontrar ZONE_KEY
    m = re.search(r'const ZONE_KEY\s*=\s*"([^"]+)"', html)
    if not m:
        return None, 'no_zone_key'
    zone_key = m.group(1)

    data_key = DATA_MAP.get(zone_key)
    if not data_key:
        return None, f'unknown_zone:{zone_key}'

    # Verificar que el data file existe
    if not os.path.exists(f'data/{data_key}.json'):
        return None, f'missing_data_file:{data_key}'

    # Buscar el patrón inline
    m = INLINE_PATTERN.search(html)
    if not m:
        return None, 'no_inline_pattern'

    # Reemplazo
    replacement = f"const r = await fetch('/data/{data_key}.json');"
    new_html = html[:m.start()] + replacement + html[m.end():]

    return new_html, f'ok:{data_key}'


def main():
    if not DRY_RUN:
        print('═ Paso 1: regenerar /data/X.json ═')
        regenerate_data_files()
        print()

    print('═ Paso 2: refactorizar HTMLs ═\n')
    files = sorted(glob.glob('*-activities.html'))

    results = []
    for fp in files:
        new_html, status = refactor_html(fp)
        results.append((fp, status, new_html))

    print(f'{"File":<45} {"Status":<25} {"Ahorro"}')
    print('─' * 90)
    total_saved = 0
    written = 0
    for fp, status, new_html in results:
        if new_html:
            saved = os.path.getsize(fp) - len(new_html)
            total_saved += saved
            print(f'{fp:<45} {status:<25} -{saved//1024} KB')
            if not DRY_RUN:
                with open(fp, 'w') as f:
                    f.write(new_html)
                written += 1
        else:
            print(f'{fp:<45} {status}')

    print(f'\nTotal ahorro HTML: {total_saved//1024} KB')
    print(f'Archivos {"a escribir" if DRY_RUN else "escritos"}: {written or len([r for r in results if r[2]])}')

    if DRY_RUN:
        print('\nRe-corre con --apply para escribir')


if __name__ == '__main__':
    main()
