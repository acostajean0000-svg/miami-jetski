#!/usr/bin/env python3
"""Genera items.json ({empresa: [item_id,...]}) a partir de operators.json para fh_price_sync.py."""
import json, re, collections, sys
d = json.load(open(sys.argv[1] if len(sys.argv) > 1 else 'operators.json'))
d = d if isinstance(d, list) else sum([v for v in d.values() if isinstance(v, list)], [])
by = collections.defaultdict(set)
for o in d:
    m = re.search(r'/embeds/book/([^/]+)/items/(\d+)', o.get('link') or '')
    if m: by[m.group(1)].add(int(m.group(2)))
json.dump({k: sorted(v) for k, v in sorted(by.items())}, open('items.json', 'w'))
print('empresas', len(by), 'items', sum(len(v) for v in by.values()))
