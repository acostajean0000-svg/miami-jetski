#!/usr/bin/env python3
"""
fix_shortnames.py — corrección sistémica de shortnames FareHarbor mal asignados.

Pipeline:
  1. Identifica ops con shortname compartido (>2 ops usando el mismo)
  2. Para cada op, genera candidatos de shortname desde su nombre
  3. Output: CSV/JSON con sugerencias para verificar via Playwright

Workflow:
  python3 fix_shortnames.py --analyze    # genera shortname_audit.json
  # Luego correr node verify_shortname_candidates.js para verificar via PW
  python3 fix_shortnames.py --apply      # aplica los verified
"""
from __future__ import annotations
import json, re, sys
from collections import Counter, defaultdict

ops = json.load(open('operators.json'))

# 1. Contar shortnames
shortnames = Counter()
for o in ops:
    m = re.search(r'/book/([^/?]+)', o.get('link', ''))
    if m: shortnames[m.group(1)] += 1

# Shared = usado por más de 2 ops
shared = {sn for sn, n in shortnames.items() if n > 2}
print(f'Shortnames compartidos por >2 ops: {len(shared)}')

# 2. Para cada op con shortname compartido, generar candidates desde el nombre
def name_to_candidates(name: str) -> list[str]:
    """Convierte nombre de op en lista de shortnames probables."""
    # Limpiar nombre
    n = re.sub(r'[\'"`®™©]', '', name.lower())
    n = re.sub(r'[^a-z0-9\s\-&]', ' ', n)

    # Quitar palabras comunes (item-specific, no company)
    STOPWORDS = {
        'tour','tours','rental','rentals','charter','charters','trip','trips',
        'experience','experiences','hour','hours','minute','minutes','day','days',
        'private','public','group','small','luxury','vip','premium','full','half',
        'and','the','at','in','on','for','to','from','of','by','with','a','an',
        '2','3','4','5','6','8','10','12','15','24','30',
        'amp','quot','39','x27', 'ft','foot',
    }

    words = [w for w in n.split() if w and w not in STOPWORDS and len(w) > 1]

    candidates = []

    # Candidate 1: full name joined
    if words:
        candidates.append(''.join(words[:4]))   # max 4 first words

    # Candidate 2: first 2 words joined
    if len(words) >= 2:
        candidates.append(''.join(words[:2]))

    # Candidate 3: first 3 words joined
    if len(words) >= 3:
        candidates.append(''.join(words[:3]))

    # Candidate 4: first word only
    if words:
        candidates.append(words[0])

    # Candidate 5: lookup if ZL (city) suffix in name
    # Pattern: "AcmeBoats — St. Pete" → acmeboats
    if '—' in name or ' - ' in name:
        first_part = re.split(r'\s*[—\-]\s*', name)[0]
        first_part_clean = re.sub(r'[^a-z0-9]+', '', first_part.lower())
        if first_part_clean and 3 <= len(first_part_clean) <= 25:
            candidates.append(first_part_clean)

    # Filtrar: solo válidos (3-25 chars alphanumeric)
    seen = set()
    valid = []
    for c in candidates:
        c = c[:25]
        if 3 <= len(c) <= 25 and re.match(r'^[a-z0-9-]+$', c) and c not in seen:
            seen.add(c)
            valid.append(c)
    return valid[:5]

# 3. Build audit list
audit = []
for o in ops:
    link = o.get('link', '')
    m = re.search(r'/book/([^/?]+)', link)
    if not m: continue
    current = m.group(1)
    if current not in shared: continue  # skip ops with unique shortnames (probably correct)

    candidates = name_to_candidates(o.get('name', ''))
    audit.append({
        'id': o['id'],
        'name': o.get('name', '')[:80],
        'cat': o.get('cat'),
        'zone': o.get('zone'),
        'current': current,
        'shared_with_ops': shortnames[current],
        'candidates': candidates,
    })

print(f'Total ops a auditar: {len(audit)}')
print(f'Total candidates a verificar: ~{sum(len(a["candidates"]) for a in audit)}')

# Por zona
by_zone = Counter(a['zone'] for a in audit)
print('\nDistribución por zona:')
for z, n in by_zone.most_common():
    print(f'  {z:<12} {n}')

# Por top compartido
top_shared = Counter(a['current'] for a in audit).most_common(10)
print('\nTop 10 shortnames más contaminados:')
for sn, n in top_shared:
    print(f'  {n:>4} × {sn}')

with open('shortname_audit.json', 'w') as f:
    json.dump(audit, f, ensure_ascii=False, indent=2)
print(f'\n✓ shortname_audit.json escrito ({len(audit)} ops)')
print('Próximo: node verify_shortname_candidates.js (verifica candidates via Playwright)')
