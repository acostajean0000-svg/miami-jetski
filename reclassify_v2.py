#!/usr/bin/env python3
"""
reclassify_v2.py — 2da ronda: 5 cats nuevas + 3 cleanups

Nuevas: themepark, walking_tour, lei, segway, zipline
Cleanups (mover ops mal categorizadas):
  - tour → boat   (Crab Island / Sandbar Florida)
  - tour → hotel  (Iberostar / All Rooms Are Private)
  - tour → yacht  (Build a Custom Trip — yates 30'-62')

Uso:
    python3 reclassify_v2.py            # dry run
    python3 reclassify_v2.py --apply    # escribir
"""
from __future__ import annotations
import json, re, sys, shutil, datetime as dt
from collections import Counter

DRY_RUN = '--apply' not in sys.argv

# Nuevas categorías
INCLUDE_NEW = {
    'themepark': [
        r'\bdisney\b', r'\bmagic kingdom\b', r'\banimal kingdom\b', r'\bepcot\b',
        r'\buniversal studios\b', r'\bislands of adventure\b', r'\bhollywood studios\b',
        r'\bseaworld\b', r'\bsea world\b', r'\bbusch gardens\b', r'\blegoland\b',
        r'\bvolcano bay\b', r'\bblizzard beach\b', r'\btyphoon lagoon\b',
        r'\bdiscovery cove\b', r'\bgatorland\b', r'\bicon park\b',
        r'\borlando eye\b', r'\bislands of adventure\b',
    ],
    'walking_tour': [
        r'\bwalking tour\b', r'\bhistor(?:ic|y|ical) (?:tour|walk|trail)\b',
        r'\bart deco\b', r'\bheritage tour\b', r'\bmuseum tour\b',
        r'\barchitectural tour\b', r'\barchitecture tour\b',
        r'\bwynwood\b.*\b(?:walk|art|tour)\b', r'\bstreet art\b',
        r'\blittle havana\b.*\btour\b',
    ],
    'lei': [
        r'\blei greeting\b', r'\bcustom lei\b', r'\borchid lei\b',
        r'\bplumeria lei\b', r'\bmaile lei\b', r'\bclassic.*lei\b',
        r'\blei (?:welcome|arrival)\b',
    ],
    'segway': [
        r'\bsegway\b',
    ],
    'zipline': [
        r'\bzip ?line\b', r'\bzip lines\b', r'\bcanopy tour\b',
        r'\bzip & \b',
    ],
}

EXCLUDE_NEW = {
    'themepark': [
        r'\bairport.*disney\b', r'\bdisney.*airport\b',   # shuttle a Disney
        r'\bdisney resort.*pickup\b', r'\bpickup.*disney\b',
        r'\bdisney spectacular\b',  # tour guiado externo
    ],
    'walking_tour': [
        r'\bfood (?:tour|walk)\b',  # ya es culinary
        r'\bghost (?:tour|walk)\b', # ya es ghost
        r'\bpub crawl\b',           # ya es ghost/nightlife
    ],
}

# Cleanups: ops mal en tour que pertenecen a otras cats existentes
CLEANUP_TO_BOAT = [
    r'\bcrab island\b', r'\bsandbar\b',
]

CLEANUP_TO_HOTEL = [
    r'\biberostar playa paraiso\b',
    r'^all rooms are\b', r'\ball rooms are private\b',
    r'^the (?:asylum|mortuary)-',  # esos son haunted hotels
]

CLEANUP_TO_YACHT = [
    r"build a custom trip\b",  # los nombres son tipo "53' Pardo - Build a Custom Trip"
]


def classify_new(name: str):
    """Orden importa: segway/zipline antes que walking_tour (un 'Art Deco Segway Tour' es segway, no walking)."""
    name_l = name.lower()
    for cat in ('segway', 'zipline', 'lei', 'themepark', 'walking_tour'):
        pats = INCLUDE_NEW[cat]
        if not any(re.search(p, name_l) for p in pats):
            continue
        if any(re.search(p, name_l) for p in EXCLUDE_NEW.get(cat, [])):
            continue
        return cat
    return None


def classify_cleanup(name: str):
    name_l = name.lower()
    for pat in CLEANUP_TO_BOAT:
        if re.search(pat, name_l): return 'boat'
    for pat in CLEANUP_TO_HOTEL:
        if re.search(pat, name_l): return 'hotel'
    for pat in CLEANUP_TO_YACHT:
        if re.search(pat, name_l): return 'yacht'
    return None


# ── Aplicar ─────────────────────────────────────────────
ops = json.load(open('operators.json'))
tour_ops = [o for o in ops if o.get('cat') == 'tour']
print(f'Operadores en cat=tour: {len(tour_ops)}')

changes = {'themepark': [], 'walking_tour': [], 'lei': [], 'segway': [], 'zipline': [],
           'boat': [], 'hotel': [], 'yacht': []}

for o in tour_ops:
    # Cleanups primero (más específicos)
    new_cat = classify_cleanup(o['name'])
    if not new_cat:
        new_cat = classify_new(o['name'])
    if new_cat:
        changes[new_cat].append(o)

print('═' * 60)
print('  RECLASIFICACIÓN v2  ' + ('(DRY RUN)' if DRY_RUN else '(APLICADA)'))
print('═' * 60)
print('  Nuevas categorías:')
for cat in ('themepark', 'walking_tour', 'lei', 'segway', 'zipline'):
    print(f'    tour → {cat:<14} {len(changes[cat]):>4}')
print('  Cleanups (mover a cats existentes):')
for cat in ('boat', 'hotel', 'yacht'):
    print(f'    tour → {cat:<14} {len(changes[cat]):>4}')
total = sum(len(v) for v in changes.values())
print(f'  Total reclasificados: {total}')
print()

for cat, lst in changes.items():
    if lst:
        print(f'Sample {cat}:')
        for o in lst[:6]:
            print(f'  {o["id"]:<8} {o["name"][:70]}')
        print()

if DRY_RUN:
    print('Re-corre con --apply para escribir cambios')
    sys.exit(0)

# Escribir
ts = dt.datetime.utcnow().strftime('%Y%m%d-%H%M%S')
shutil.copy2('operators.json', f'operators.json.bak-{ts}')
for cat, lst in changes.items():
    for op in lst:
        op['cat'] = cat
with open('operators.json', 'w') as f:
    json.dump(ops, f, ensure_ascii=False, separators=(',', ':'))

slim = json.load(open('operators-slim.json'))
slim_by_id = {o['id']: o for o in slim}
slim_updates = 0
for cat, lst in changes.items():
    for op in lst:
        if op['id'] in slim_by_id:
            slim_by_id[op['id']]['cat'] = cat
            slim_updates += 1
shutil.copy2('operators-slim.json', f'operators-slim.json.bak-{ts}')
with open('operators-slim.json', 'w') as f:
    json.dump(slim, f, ensure_ascii=False, separators=(',', ':'))

print(f'✓ operators.json: {total} updates')
print(f'✓ operators-slim.json: {slim_updates} updates')
print()

ops2 = json.load(open('operators.json'))
new_dist = Counter(o.get('cat') for o in ops2)
print('Distribución final:')
for c, n in new_dist.most_common():
    print(f'  {c:<15} {n:>5}')
