#!/usr/bin/env python3
"""
identify_photo_targets.py — selecciona los operadores que necesitan foto única.

Output: photo_targets.json con la lista de op IDs y sus URLs de FareHarbor.

Quiénes entran al target list:
  • Operadores con photo == null (480 ops)
  • Operadores que comparten foto con otro op (121 ops en 53 fotos duplicadas)

Total esperado: ~601 operadores.

Uso:
    python3 identify_photo_targets.py

Después correr (en tu Mac, no en Cowork):
    node scrape_fareharbor_photos.js --targets photo_targets.json
"""
import json, re
from collections import Counter

HANDLE_RE = re.compile(r'filestackcontent\.com/([A-Za-z0-9]{15,30})')

ops = json.load(open('operators.json'))

# Identificar handles compartidos
handle_count = Counter()
for o in ops:
    p = o.get('photo')
    if not p: continue
    m = HANDLE_RE.search(p)
    if m: handle_count[m.group(1)] += 1

shared_handles = {h for h, n in handle_count.items() if n > 1}
print(f'Fotos compartidas (≥2 ops):   {len(shared_handles)}')

# Construir target list
targets = []
for o in ops:
    p = o.get('photo')
    link = o.get('link')
    needs = False
    reason = ''
    if not p:
        needs = True
        reason = 'null'
    else:
        m = HANDLE_RE.search(p)
        if m and m.group(1) in shared_handles:
            needs = True
            reason = f'shared (used by {handle_count[m.group(1)]} ops)'
    if needs and link and 'fareharbor.com' in link:
        targets.append({
            'id':         o['id'],
            'name':       o.get('name', ''),
            'fh_url':     link,
            'cat':        o.get('cat', ''),
            'zone':       o.get('zone', ''),
            'reason':     reason,
            'current_photo': p,
        })

with open('photo_targets.json', 'w') as f:
    json.dump(targets, f, indent=2)

# Resumen
print(f'\n  Total targets:                 {len(targets)}')
from collections import Counter as C
by_reason = C(t['reason'].split(' ')[0] for t in targets)
print(f'    Sin foto (null):             {by_reason.get("null", 0)}')
print(f'    Compartida con otro op:      {sum(v for k,v in by_reason.items() if k!="null")}')
print()
by_cat = C(t['cat'] for t in targets)
print(f'  Por categoría:')
for c, n in by_cat.most_common(): print(f'    {c:<15} {n}')

print(f'\nGuardado en photo_targets.json — listo para pasar al scraper.')
print()
print('Próximo paso (correr EN TU MAC):')
print('  cd ~/miami-jetski-main')
print('  npm install playwright  # solo primera vez')
print('  npx playwright install chromium  # solo primera vez')
print('  node scrape_fareharbor_photos.js --targets photo_targets.json')
print()
print('Tarda ~30-45 minutos con concurrency=3.')
print('Resultado: fh_scrape_photos.json')
print('Después: python3 apply_fh_unique.py --apply')
