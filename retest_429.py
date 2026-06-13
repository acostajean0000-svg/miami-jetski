#!/usr/bin/env python3
"""
retest_429.py — re-test los ops 429 (rate-limited) con backoff.

El check_operator_freshness inicial usó 20 workers paralelos lo cual
triggeó FareHarbor rate limit (429). Este re-test usa 0 concurrency
con 1.5s delay para evitar el rate limit y obtener status real.

Uso:
    python3 retest_429.py            # re-test todos los 429 del reporte
"""
import json, time, sys, os
from urllib.request import Request, build_opener
from urllib.error import HTTPError

if not os.path.exists('operator_freshness_report.json'):
    print('❌ Falta operator_freshness_report.json — corre check_operator_freshness.command primero')
    sys.exit(1)

report = json.load(open('operator_freshness_report.json'))
to_retest = [r for r in report if r['status'] == 429]

if not to_retest:
    print('No hay ops 429 para re-testear.')
    sys.exit(0)

print(f'Re-testeando {len(to_retest)} ops 429 (1.5s entre requests, ~{len(to_retest)*2}s total)...')
print()

results = []
for i, r in enumerate(to_retest):
    op = build_opener()
    req = Request(r['link'], headers={'User-Agent': 'Mozilla/5.0 RetestBot/1.0'}, method='HEAD')
    try:
        resp = op.open(req, timeout=10)
        status = resp.status
    except HTTPError as e:
        status = e.code
    except Exception:
        status = 0
    results.append({'id': r['id'], 'name': r['name'], 'status': status, 'link': r['link']})
    print(f'  [{i+1}/{len(to_retest)}] [{status}] {r["id"]:<8} {r["name"][:55]}')
    time.sleep(1.5)

# Resumen
from collections import Counter
c = Counter(x['status'] for x in results)
print(f'\n{"="*50}')
print(f'  RE-TEST FINAL')
print(f'{"="*50}')
for s, n in c.most_common():
    print(f'  {s:<10} {n}')

dead = [x for x in results if x['status'] in (404, 410)]
recovered = [x for x in results if x['status'] == 200]
still_429 = [x for x in results if x['status'] == 429]

print(f'\n  Recuperados (200):     {len(recovered)}')
print(f'  Realmente muertos:     {len(dead)}')
print(f'  Aun 429 (FH lento):    {len(still_429)}')

if dead:
    print(f'\nOps a eliminar:')
    for d in dead:
        print(f'  {d["id"]:<8} {d["name"][:60]}')

with open('retest_429_results.json', 'w') as f:
    json.dump(results, f, indent=2)
print(f'\nGuardado: retest_429_results.json')
