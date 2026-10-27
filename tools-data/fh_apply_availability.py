#!/usr/bin/env python3
"""Aplica el resultado de fh_availability.py (tools-data/fh-availability-AAAA-MM-DD.json):
- items con precio nuevo (USD, >= $8) -> se guarda el precio en todos los JSON de datos
- items sin fechas disponibles ("next": null) -> campo "noAvail": 1 y se mandan al final de cada lista
- después hay que ejecutar pin_partners.py (los socios vuelven arriba) y regenerar/aplicar HTML
Uso: python3 tools-data/fh_apply_availability.py tools-data/fh-availability-AAAA-MM-DD.json"""
import json, glob, io, re, os, sys
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
A = json.load(open(sys.argv[1]))
noav = {k for k, v in A.items() if not v.get('next')}
newp = {k: round(float(v['price']), 2) for k, v in A.items() if v.get('price') and v.get('currency') == 'USD' and float(v['price']) >= 8}
def iid(o):
    m = re.search(r'(?:/items/|^[^/:]+/)(\d+)', str(o.get('link') or ''))
    return m.group(1) if m else None
files = ['operators.json', 'operators-slim.json', 'operators-top.json'] + glob.glob('data/*.json') + glob.glob('data/cat/*.json')
st = {'precio': 0, 'sin_fechas': 0}
for f in files:
    raw = io.open(f, encoding='utf-8').read(); j = json.loads(raw); ch = [False]
    def fix(L):
        if not (isinstance(L, list) and L and isinstance(L[0], dict) and 'link' in L[0]): return L
        for o in L:
            i = iid(o)
            if i in newp and not o.get('price'):
                p = newp[i]; o['price'] = int(p) if p == int(p) else p; ch[0] = True; st['precio'] += 1
            flag = 1 if i in noav else 0
            if flag and not o.get('noAvail'): o['noAvail'] = 1; ch[0] = True; st['sin_fechas'] += 1
            if not flag and o.get('noAvail'): o.pop('noAvail'); ch[0] = True
        new = [o for o in L if not o.get('noAvail')] + [o for o in L if o.get('noAvail')]
        if [id(x) for x in new] != [id(x) for x in L]: ch[0] = True
        return new
    if isinstance(j, list): j = fix(j)
    else:
        for k, v in list(j.items()): j[k] = fix(v)
    if ch[0]:
        compact = '\n' not in raw.strip()[:2000]
        io.open(f, 'w', encoding='utf-8').write(json.dumps(j, ensure_ascii=False, separators=(',', ':')) if compact else json.dumps(j, ensure_ascii=False, indent=1))
print(st, '| items sin fechas en el archivo:', len(noav), '| con precio nuevo:', len(newp))
