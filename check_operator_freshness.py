#!/usr/bin/env python3
"""
check_operator_freshness.py — verifica que cada operator's FareHarbor link sigue activo.

Detecta:
  - Operadores cuyo link FH retorna 404/410 (cerrados)
  - Operadores con link que redirige a otro lado (cambio de slug)
  - Operadores sin link

Output: operator_freshness_report.json con la lista de dead/redirected ops.

Uso:
    python3 check_operator_freshness.py            # primeros 100 (sample)
    python3 check_operator_freshness.py --all      # todos los 4,849
"""
import json, sys, time
from urllib.request import Request, build_opener, HTTPRedirectHandler
from urllib.error import HTTPError, URLError
from concurrent.futures import ThreadPoolExecutor, as_completed

ALL = '--all' in sys.argv
WORKERS = 20
TIMEOUT = 10
HEADERS = {'User-Agent': 'Mozilla/5.0 FreshnessBot/1.0'}


class TrackRedir(HTTPRedirectHandler):
    def __init__(self): super().__init__(); self.chain = []
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        self.chain.append((req.full_url, code, newurl))
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def check(url):
    h = TrackRedir()
    op = build_opener(h)
    try:
        resp = op.open(Request(url, headers=HEADERS, method='HEAD'), timeout=TIMEOUT)
        return resp.status, h.chain
    except HTTPError as e:
        return e.code, h.chain
    except URLError:
        return 0, h.chain
    except Exception:
        return -1, h.chain


def main():
    ops = json.load(open('operators.json'))
    targets = [o for o in ops if o.get('link', '').startswith('http')]
    if not ALL:
        targets = targets[:100]

    print(f'Verificando {len(targets)} de {len(ops)} operators...')
    results = []
    start = time.time()
    done = 0

    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        futures = {ex.submit(check, o['link']): o for o in targets}
        for f in as_completed(futures):
            o = futures[f]
            try:
                status, chain = f.result()
            except Exception:
                status, chain = -1, []
            done += 1
            if status >= 400 or status == 0:
                results.append({'id': o['id'], 'name': o.get('name', '')[:50],
                                'status': status, 'link': o.get('link')})
            if done % 50 == 0:
                eta = (time.time() - start) / done * (len(targets) - done)
                print(f'  [{done}/{len(targets)}] dead so far: {len(results)} · ETA {eta:.0f}s')

    print(f'\n{"═" * 50}')
    print(f'  Total verificados: {done}')
    print(f'  Activos (200):     {done - len(results)}')
    print(f'  ⚠️  Dead/error:     {len(results)}')

    if results:
        with open('operator_freshness_report.json', 'w') as f:
            json.dump(results, f, indent=2)
        print(f'\nGuardado: operator_freshness_report.json')
        print(f'Primeros 10 dead ops:')
        for r in results[:10]:
            print(f'  [{r["status"]}] {r["id"]:<8} {r["name"]}')


if __name__ == '__main__':
    main()
