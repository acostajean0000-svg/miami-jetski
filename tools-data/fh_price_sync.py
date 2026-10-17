#!/usr/bin/env python3
"""Lee el precio "desde" de cada item de FareHarbor con el mismo endpoint público que usa su calendario
(/api/embed/{empresa}/price-preview/per-item/v2/). No usa /embeds/book/ ni /api/v1/ (rutas excluidas en
robots.txt de FareHarbor). Ritmo lento a propósito (1 petición cada ~1,5 s, reintentos con espera).

Entrada:  items.json  {"empresa": [item_id, ...], ...}
Salida:   prices.jsonl (una línea por empresa/lote, reanudable) y prices.json (id_item -> resultado)
Uso:      python3 fh_price_sync.py items.json   (se puede relanzar: salta los lotes ya hechos)
"""
import json, os, re, sys, time, random, urllib.request, urllib.error

BATCH = 40
DELAY = 1.5
UA = 'Mozilla/5.0 (compatible; miamijetskiboatrentals-price-sync/1.0; affiliate catalog refresh)'
NON_BASE = re.compile(r'infant|child|kid|toddler|baby|youth|junior|senior|student|military|fee|deposit|tip|gratuit|'
                      r'add[\s-]?on|upgrade|parking|insurance|waiver|photo|souvenir|tax|donation|extra|gift', re.I)

def base_price(item):
    """Precio 'desde' para un adulto / reserva base. Devuelve (precio_en_unidades, etiqueta) o (None, motivo)."""
    pr = item.get('price') or {}
    cts = ((pr.get('breakdown') or {}).get('customer_types')) or []
    good = [c for c in cts if (c.get('price') or 0) > 0 and not NON_BASE.search((c.get('singular') or '') + ' ' + (c.get('note') or ''))]
    if good:
        c = min(good, key=lambda c: c['price']); return c['price'], c.get('singular') or ''
    allp = [c for c in cts if (c.get('price') or 0) > 0]
    if allp:  # solo hay tipos "no base": usar el más alto, nunca una tasa de $1-2
        c = max(allp, key=lambda c: c['price']); return c['price'], 'max:' + (c.get('singular') or '')
    if pr.get('high'): return pr['high'], 'high'
    return None, 'sin precio'

def get(url, tries=5):
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': UA, 'Accept': 'application/json'})
            with urllib.request.urlopen(req, timeout=30) as r:
                return r.status, json.loads(r.read().decode('utf-8'))
        except urllib.error.HTTPError as e:
            if e.code in (404, 403, 400): return e.code, None
            wait = 20 * (i + 1) if e.code == 429 else 5 * (i + 1)
        except Exception:
            wait = 5 * (i + 1)
        time.sleep(wait + random.random() * 3)
    return 'error', None

def main():
    items = json.load(open(sys.argv[1]))
    done = set()
    if os.path.exists('prices.jsonl'):
        for line in open('prices.jsonl'):
            try: r = json.loads(line); done.add((r['sn'], r['batch']))
            except Exception: pass
    out = open('prices.jsonl', 'a')
    jobs = [(sn, b, ids[b * BATCH:(b + 1) * BATCH]) for sn, ids in items.items() for b in range((len(ids) + BATCH - 1) // BATCH)]
    todo = [j for j in jobs if (j[0], j[1]) not in done]
    print('lotes totales', len(jobs), '| pendientes', len(todo), flush=True)
    t0 = time.time()
    for k, (sn, b, ids) in enumerate(todo, 1):
        url = 'https://fareharbor.com/api/embed/%s/price-preview/per-item/v2/?asn=fhdn&item_pks=%s&include_breakdown=yes' % (sn, ','.join(map(str, ids)))
        status, j = get(url)
        res = {}
        cur = None
        if j:
            det = j.get('details') or {}; cur = det.get('currency'); dec = det.get('currency_decimal_places', 2)
            for it in j.get('items') or []:
                p, lab = base_price(it)
                res[str(it.get('id'))] = {'price': (round(p / (10 ** dec), 2) if p else None), 'label': lab,
                                          'low': it.get('price', {}).get('low'), 'high': it.get('price', {}).get('high'),
                                          'date': (it.get('availability') or {}).get('start_at')}
        if status == 'error':  # no marcar como hecho: se reintenta en la próxima ejecución
            print('fallo de red en', sn, b, flush=True); time.sleep(DELAY); continue
        out.write(json.dumps({'sn': sn, 'batch': b, 'status': status, 'currency': cur, 'items': res, 'asked': ids}) + '\n'); out.flush()
        if k % 50 == 0:
            el = time.time() - t0; print('%d/%d lotes · %.0f min · ETA %.0f min' % (k, len(todo), el / 60, el / k * (len(todo) - k) / 60), flush=True)
        time.sleep(DELAY + random.random())
    out.close()
    # consolidar
    allp = {}
    for line in open('prices.jsonl'):
        r = json.loads(line)
        for iid, v in r['items'].items():
            v['currency'] = r['currency']; v['sn'] = r['sn']; allp[iid] = v
    json.dump(allp, open('prices.json', 'w'))
    print('FIN · items con precio:', sum(1 for v in allp.values() if v.get('price')), '| respuestas:', len(allp), flush=True)

if __name__ == '__main__':
    main()
