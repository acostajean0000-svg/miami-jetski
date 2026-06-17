#!/usr/bin/env python3
"""
remove_zombies.py — remueve ops cuyos shortnames son zombies (FH page vacía).

Lee zombie_shortnames.json de detect_zombies.js y:
  1. Identifica todos los ops con shortname zombie
  2. Backup + remover de operators.json + operators-slim.json
  3. Regenera /data/*.json y slug-map files
  4. Remueve sus HTMLs huérfanos

Uso:
    python3 remove_zombies.py            # dry run
    python3 remove_zombies.py --apply    # ejecuta
"""
import json, sys, re, os, shutil, datetime as dt
from collections import defaultdict

DRY = '--apply' not in sys.argv

if not os.path.exists('zombie_shortnames.json'):
    print('❌ Falta zombie_shortnames.json — corre `node detect_zombies.js` primero')
    sys.exit(1)

results = json.load(open('zombie_shortnames.json'))
zombie_sns = [sn for sn, r in results.items() if r.get('zombie')]
print(f'Shortnames zombie: {len(zombie_sns)}')

ops = json.load(open('operators.json'))
slim = json.load(open('operators-slim.json'))

zombie_op_ids = set()
for o in ops:
    m = re.search(r'/book/([^/?]+)', o.get('link',''))
    if m and m.group(1) in zombie_sns:
        zombie_op_ids.add(o['id'])

print(f'Ops afectados:   {len(zombie_op_ids)}')

if not zombie_op_ids:
    print('Nada a remover.')
    sys.exit(0)

# Sample
print('\nMuestra (primeros 10):')
shown = 0
for o in ops:
    if o['id'] in zombie_op_ids:
        m = re.search(r'/book/([^/?]+)', o.get('link',''))
        sn = m.group(1) if m else '?'
        print(f'  [{o["id"]:<8}] {sn:<28} {o["name"][:50]}')
        shown += 1
        if shown >= 10: break

if DRY:
    print('\nRe-corre con --apply para ejecutar')
    sys.exit(0)

# Apply
ts = dt.datetime.utcnow().strftime('%Y%m%d-%H%M%S')
shutil.copy2('operators.json', f'operators.json.bak-{ts}')
shutil.copy2('operators-slim.json', f'operators-slim.json.bak-{ts}')

ops2 = [o for o in ops if o['id'] not in zombie_op_ids]
slim2 = [o for o in slim if o['id'] not in zombie_op_ids]
json.dump(ops2, open('operators.json','w'), ensure_ascii=False, separators=(',',':'))
json.dump(slim2, open('operators-slim.json','w'), ensure_ascii=False, separators=(',',':'))
print(f'\n✓ {len(ops)-len(ops2)} ops eliminados de operators.json + operators-slim.json')

# Regenerar data/*.json
by_zone = defaultdict(list)
for o in slim2: by_zone[o.get('zone','')].append(o)
for z, lst in by_zone.items():
    if z and os.path.exists(f'data/{z}.json'):
        json.dump(lst, open(f'data/{z}.json','w'), ensure_ascii=False, separators=(',',':'))
        print(f'  ✓ data/{z}.json ({len(lst)} ops)')

# Remover HTMLs huérfanos
sm_files = ['slug-map.js'] + [f'slug-map/{z}.js' for z in by_zone if os.path.exists(f'slug-map/{z}.js')]
removed_html = 0
for smf in sm_files:
    if not os.path.exists(smf): continue
    content = open(smf).read()
    for op_id in zombie_op_ids:
        m = re.search(r'"' + re.escape(op_id) + r'"\s*:\s*"([^"]+)"', content)
        if m:
            slug = m.group(1)
            fp = f'{slug}.html'
            if os.path.exists(fp):
                os.remove(fp)
                removed_html += 1

if removed_html:
    print(f'  ✓ {removed_html} HTMLs huérfanos eliminados')

print(f'\nBackups: .bak-{ts}')
print('Próximo: ./miamijetskiboat.command para deploy')
