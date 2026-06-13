#!/usr/bin/env python3
"""Elimina los 2 ops confirmados muertos + regenera data."""
import json, shutil, datetime as dt, os, re
from collections import defaultdict

DEAD = ['to2180', 'bt1567']

# Backup
ts = dt.datetime.utcnow().strftime('%Y%m%d-%H%M%S')
shutil.copy2('operators.json', 'operators.json.bak-' + ts)
shutil.copy2('operators-slim.json', 'operators-slim.json.bak-' + ts)
print('Backup creado: .bak-' + ts)

# Cargar y filtrar
ops = json.load(open('operators.json'))
slim = json.load(open('operators-slim.json'))
ops2 = [o for o in ops if o['id'] not in DEAD]
slim2 = [o for o in slim if o['id'] not in DEAD]

json.dump(ops2, open('operators.json', 'w'), ensure_ascii=False, separators=(',', ':'))
json.dump(slim2, open('operators-slim.json', 'w'), ensure_ascii=False, separators=(',', ':'))
print('Eliminados ' + str(len(DEAD)) + ' ops. Total: ' + str(len(ops)) + ' -> ' + str(len(ops2)))

# Regenerar data/*.json
by_zone = defaultdict(list)
for o in slim2:
    by_zone[o.get('zone', '')].append(o)

for z, lst in by_zone.items():
    if z and os.path.exists('data/' + z + '.json'):
        json.dump(lst, open('data/' + z + '.json', 'w'),
                  ensure_ascii=False, separators=(',', ':'))
        print('  ok data/' + z + '.json (' + str(len(lst)) + ' ops)')

# Eliminar HTMLs huerfanas
sm = open('slug-map.js').read()
for op_id in DEAD:
    m = re.search(r'"' + op_id + r'"\s*:\s*"([^"]+)"', sm)
    if m:
        slug = m.group(1)
        fp = slug + '.html'
        if os.path.exists(fp):
            os.remove(fp)
            print('  HTML eliminado: ' + fp)

print('Listo.')
