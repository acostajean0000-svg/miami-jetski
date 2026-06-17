#!/usr/bin/env python3
"""
apply_verified_shortnames.py — aplica los shortnames verificados a operators.json

Lee shortname_verified.json y actualiza los links de los ops cuyo bestMatch
tiene score >= threshold (default 0.5).

Uso:
    python3 apply_verified_shortnames.py            # dry run
    python3 apply_verified_shortnames.py --apply    # escribe
    python3 apply_verified_shortnames.py --apply --threshold 0.6
"""
from __future__ import annotations
import json, re, sys, shutil, datetime as dt
from collections import Counter

DRY_RUN = '--apply' not in sys.argv
THRESHOLD = 0.5
if '--threshold' in sys.argv:
    THRESHOLD = float(sys.argv[sys.argv.index('--threshold')+1])

verified = json.load(open('shortname_verified.json'))
ops = json.load(open('operators.json'))
slim = json.load(open('operators-slim.json'))
slim_by_id = {o['id']: o for o in slim}

# Stats
total = len(verified)
with_match = sum(1 for v in verified.values() if v.get('bestMatch'))
above_thresh = sum(1 for v in verified.values() if v.get('bestMatch') and v['bestMatch']['score'] >= THRESHOLD)
print(f'Verificados:                 {total}')
print(f'Con bestMatch:               {with_match}')
print(f'Con score >= {THRESHOLD}:        {above_thresh}')
print()

# Aplicar
URL_TEMPLATE = (
    'https://fareharbor.com/embeds/book/{sn}/?asn=fhdn&asn-ref=miamistylerentals'
    '&ref=miamistylerentals&full-items=yes&marketplace=yes&flow=no&branding=no'
)

changes = []
for op_id, v in verified.items():
    bm = v.get('bestMatch')
    if not bm or bm['score'] < THRESHOLD: continue

    new_shortname = bm['shortname']
    if new_shortname == v.get('currentShortname'): continue  # ya correcto

    op = next((o for o in ops if o['id'] == op_id), None)
    if not op: continue

    old_link = op.get('link', '')
    new_link = URL_TEMPLATE.format(sn=new_shortname)

    changes.append({
        'id': op_id,
        'name': op.get('name', '')[:50],
        'old_shortname': v.get('currentShortname'),
        'new_shortname': new_shortname,
        'score': bm['score'],
        'fh_name': bm.get('companyName', '')[:50],
    })

    if not DRY_RUN:
        op['link'] = new_link
        if op_id in slim_by_id:
            slim_by_id[op_id]['link'] = new_link

print(f'Cambios a aplicar: {len(changes)}')
print('\nMuestra (primeros 10):')
for c in changes[:10]:
    print(f'  {c["id"]:<8} {c["old_shortname"]:<25} → {c["new_shortname"]:<25} (score {c["score"]:.2f}) — {c["name"][:35]}')

if DRY_RUN:
    print('\nRe-corre con --apply para escribir')
else:
    ts = dt.datetime.utcnow().strftime('%Y%m%d-%H%M%S')
    shutil.copy2('operators.json', f'operators.json.bak-{ts}')
    shutil.copy2('operators-slim.json', f'operators-slim.json.bak-{ts}')
    with open('operators.json', 'w') as f:
        json.dump(ops, f, ensure_ascii=False, separators=(',', ':'))
    with open('operators-slim.json', 'w') as f:
        json.dump(slim, f, ensure_ascii=False, separators=(',', ':'))
    print(f'\n✓ Aplicado a operators.json + operators-slim.json')
    print(f'✓ Backups: .bak-{ts}')

# Mostrar shortnames más-corregidos
by_old = Counter(c['old_shortname'] for c in changes)
print('\nTop 10 shortnames más corregidos:')
for sn, n in by_old.most_common(10):
    print(f'  {n:>4} × {sn}')
