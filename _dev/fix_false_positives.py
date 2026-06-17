#!/usr/bin/env python3
"""
fix_false_positives.py — corregir miscategorizaciones detectadas en auditoría.

Movimientos:
  walking_tour → culinary  (8 ops con "food" en el nombre)
  restaurant   → culinary  (5 ops tequila tasting)
  themepark    → hotel     (13 ops Hilton/Wyndham:Park)
  hotel        → ghost     (3 ops Asylum/Mortuary/Class Room — haunted attractions)
  wildlife     → boat      (1 op Sandbar Safari)

Uso:
    python3 fix_false_positives.py            # dry run
    python3 fix_false_positives.py --apply
"""
from __future__ import annotations
import json, re, sys, shutil, datetime as dt
from collections import Counter

DRY_RUN = '--apply' not in sys.argv

# (from_cat, to_cat, patrón)
MOVES = [
    ('walking_tour', 'culinary', re.compile(r'(?<!no )(?<!\()\bfood\b|\bdonut\b|\btaste of\b', re.I)),
    ('restaurant',   'culinary', re.compile(r'\btequila tasting\b|\btasting (?:and|&) (?:pairing|mixology)\b', re.I)),
    ('themepark',    'hotel',    re.compile(r'\b(?:hilton|wyndham|marriott|renaissance|holiday inn|hyatt|sheraton|hampton|ramada|courtyard|crowne plaza|comfort inn|residence inn|fairfield)\b.*[:\-]', re.I)),
    ('hotel',        'ghost',    re.compile(r'\b(?:asylum|mortuary|haunted)\b.*all rooms', re.I)),
    ('hotel',        'ghost',    re.compile(r'\bthe class room adventure\b', re.I)),
    ('wildlife',     'boat',     re.compile(r'\bsandbar safari\b', re.I)),
]

ops = json.load(open('operators.json'))
print(f'Total ops: {len(ops)}')

moves_log = []
for o in ops:
    cur = o.get('cat')
    name = o.get('name', '')
    for from_cat, to_cat, pat in MOVES:
        if cur == from_cat and pat.search(name):
            moves_log.append((o['id'], from_cat, to_cat, name))
            if not DRY_RUN:
                o['cat'] = to_cat
            break

# Resumen
by_change = Counter((f, t) for _, f, t, _ in moves_log)
print(f'\n═ Movimientos {"(DRY RUN)" if DRY_RUN else "APLICADOS"} ═')
for (f, t), n in by_change.most_common():
    print(f'  {f:<14} → {t:<10} {n:>3} ops')
print(f'  Total: {len(moves_log)}')

print(f'\nDetalle:')
for op_id, f, t, name in moves_log:
    print(f'  {op_id:<8} {f:>12} → {t:<10}  {name[:65]}')

if DRY_RUN:
    print('\nRe-corre con --apply')
    sys.exit(0)

# Aplicar
ts = dt.datetime.utcnow().strftime('%Y%m%d-%H%M%S')
shutil.copy2('operators.json', f'operators.json.bak-{ts}')
with open('operators.json', 'w') as f:
    json.dump(ops, f, ensure_ascii=False, separators=(',', ':'))

slim = json.load(open('operators-slim.json'))
slim_by_id = {o['id']: o for o in slim}
for op_id, _, to_cat, _ in moves_log:
    if op_id in slim_by_id:
        slim_by_id[op_id]['cat'] = to_cat
shutil.copy2('operators-slim.json', f'operators-slim.json.bak-{ts}')
with open('operators-slim.json', 'w') as f:
    json.dump(slim, f, ensure_ascii=False, separators=(',', ':'))

print(f'\n✓ Aplicado. Backups: {ts}')

# Distribución final
ops2 = json.load(open('operators.json'))
dist = Counter(o.get('cat') for o in ops2)
print('\nDistribución final:')
for c, n in dist.most_common():
    print(f'  {c:<15} {n:>5}')
