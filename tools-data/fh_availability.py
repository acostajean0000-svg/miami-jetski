#!/usr/bin/env python3
"""Para los items que no devolvieron precio en la última extracción, averigua si tienen fechas disponibles.
1) price-preview con allow_unlisted_items=yes (por empresa, lotes de 40) -> precio + próxima fecha
2) los que sigan sin respuesta: next-bookable-availability por item -> próxima fecha o null
Salida: availability.json {item_id: {"next": "YYYY-MM-DD"|null, "price": float|null, "currency": str|null, "sn": str}}
Uso: python3 fh_availability.py operators.json fh-prices-AAAA-MM-DD.json   (reanudable vía availability.jsonl)"""
import json, re, sys, os, time, random, datetime, urllib.request, urllib.error, collections

UA = 'Mozilla/5.0 (compatible; miamijetskiboatrentals-price-sync/1.0; affiliate catalog refresh)'
NON_BASE = re.compile(r'infant|child|kid|toddler|baby|youth|junior|senior|student|military|fee|deposit|tip|gratuit|'
                      r'add[\s-]?on|upgrade|parking|insurance|waiver|photo|souvenir|tax|donation|extra|gift', re.I)
DELAY = 1.5

def get(url, tries=4):
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': UA, 'Accept': 'application/json'}), timeout=30) as r:
                return r.status, json.loads(r.read().decode('utf-8'))
        except urllib.error.HTTPError as e:
            if e.code in (400, 403, 404): return e.code, None
            time.sleep((20 if e.code == 429 else 5) * (i + 1))
        except Exception:
            time.sleep(5 * (i + 1))
    return 'error', None

def base_price(item):
    pr = item.get('price') or {}
    cts = ((pr.get('breakdown') or {}).get('customer_types')) or []
    good = [c for c in cts if (c.get('price') or 0) > 0 and not NON_BASE.search((c.get('singular') or '') + ' ' + (c.get('note') or ''))]
    if good: return min(c['price'] for c in good)
    allp = [c['price'] for c in cts if (c.get('price') or 0) > 0]
    return max(allp) if allp else (pr.get('high') or None)

def main():
    ops = json.load(open(sys.argv[1])); ops = ops if isinstance(ops, list) else sum([v for v in ops.values() if isinstance(v, list)], [])
    known = json.load(open(sys.argv[2]))
    miss = collections.defaultdict(set)
    for o in ops:
        m = re.search(r'/embeds/book/([^/]+)/items/(\d+)', o.get('link') or '')
        if m and m.group(2) not in known: miss[m.group(1)].add(int(m.group(2)))
    done = {}
    if os.path.exists('availability.jsonl'):
        for line in open('availability.jsonl'):
            try: r = json.loads(line); done[r['id']] = r
            except Exception: pass
    out = open('availability.jsonl', 'a')
    todo = {sn: sorted(i for i in ids if str(i) not in done) for sn, ids in miss.items()}
    todo = {k: v for k, v in todo.items() if v}
    print('items sin precio:', sum(len(v) for v in miss.values()), '| pendientes:', sum(len(v) for v in todo.values()), '| empresas:', len(todo), flush=True)
    today = datetime.date.today().isoformat()
    n = 0
    for sn, ids in todo.items():
        got = set()
        for b in range(0, len(ids), 40):
            chunk = ids[b:b + 40]
            st, j = get('https://fareharbor.com/api/embed/%s/price-preview/per-item/v2/?asn=fhdn&item_pks=%s&include_breakdown=yes&allow_unlisted_items=yes' % (sn, ','.join(map(str, chunk))))
            if j:
                dec = (j.get('details') or {}).get('currency_decimal_places', 2); cur = (j.get('details') or {}).get('currency')
                for it in j.get('items') or []:
                    p = base_price(it); d = ((it.get('availability') or {}).get('start_at') or '')[:10] or None
                    rec = {'id': str(it.get('id')), 'sn': sn, 'next': d, 'price': round(p / 10 ** dec, 2) if p else None, 'currency': cur, 'src': 'price-preview'}
                    out.write(json.dumps(rec) + '\n'); got.add(it.get('id'))
            time.sleep(DELAY + random.random())
        for i in ids:
            if i in got: continue
            st, j = get('https://fareharbor.com/api/embed/%s/next-bookable-availability/v1/?date=%s&item_pks=%d&asn=fhdn&allow_unlisted_items=yes' % (sn, today, i))
            if st == 'error': continue
            rec = {'id': str(i), 'sn': sn, 'next': (j or {}).get('next_available_date'), 'price': None, 'currency': None, 'src': 'next-bookable', 'status': st}
            out.write(json.dumps(rec) + '\n'); n += 1
            if n % 100 == 0: print(n, 'items consultados uno a uno', flush=True)
            time.sleep(DELAY + random.random())
        out.flush()
    out.close()
    res = {}
    for line in open('availability.jsonl'):
        r = json.loads(line); res[r['id']] = r
    json.dump(res, open('availability.json', 'w'))
    c = collections.Counter('con fechas' if r.get('next') else 'sin fechas' for r in res.values())
    print('FIN', dict(c), '| con precio nuevo:', sum(1 for r in res.values() if r.get('price')), flush=True)

if __name__ == '__main__':
    main()
