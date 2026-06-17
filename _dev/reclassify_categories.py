#!/usr/bin/env python3
"""
reclassify_categories.py — reclasificar operadores 'tour' a categorías nuevas:
  hotel, nightlife, restaurant, shuttle

Detecta por keywords + excepciones para evitar falsos positivos.

Uso:
    python3 reclassify_categories.py            # dry run
    python3 reclassify_categories.py --apply    # escribir
"""
from __future__ import annotations
import json, re, sys, shutil, datetime as dt
from collections import Counter

DRY_RUN = '--apply' not in sys.argv

# Patrones de inclusión (palabras clave POSITIVAS que sugieren la categoría)
INCLUDE = {
    'golf': [
        r'\bgolf course\b', r'\bgolf club\b', r'\btee.?time\b',
        r'\bgolf\b(?! cart)',
    ],
    'mayan_cenote': [
        r'\bcenote\b', r'\bchichen.?itza\b', r'\btulum (?:ruins?|archaeological)\b',
        r'\bmayan (?:ruins?|tour|civilization)\b', r'\bcoba\b',
        r'\bxcaret\b', r'\bxel.?ha\b', r'\bxenotes?\b',
        r'\bek balam\b', r'\bpopol vuh\b', r'\bisla mujeres ruins?\b',
    ],
    'wildlife': [
        r'\bwhale (?:watching|watch|tour|safari|cruise)\b',
        r'\bdolphin (?:watch|watching|tour|sighting|encounter|safari)\b',
        r'\bmanatee (?:tour|encounter|swim|safari|cruise|adventure)\b',
        r'\bsea turtle (?:tour|encounter|safari)\b',
        r'\bturtle (?:tour|safari|encounter)\b',
        r'\bshark (?:tour|encounter|safari|cage)\b',
        r'\bbird watching\b', r'\bbird (?:tour|safari)\b',
        r'\bsafari\b(?! truck)(?! buggy)',
        r'\bwildlife (?:tour|watch|encounter)\b',
        r'\beco safari\b',
    ],
    'culinary': [
        r'\btequila tasting\b', r'\bcooking class\b', r'\bculinary\b',
        r'\bwine (?:tasting|tour|experience|crawl)\b',
        r'\bfood (?:tour|tasting|experience|crawl|walk)\b',
        r'\bcheese tour\b', r'\bchocolate (?:tour|tasting|making)\b',
        r'\bbeer (?:tasting|tour|crawl)\b', r'\bbrewery tour\b',
        r'\bmixology\b', r'\bsommelier\b',
        r'\btasting (?:experience|tour|menu)\b',
    ],
    'ghost': [
        r'\bghost (?:tour|hunt|walk|cruise)\b',
        r'\bhaunted (?:tour|history|cemetery)\b',
        r'\bparanormal\b',
        r'\bpub crawl\b',
    ],
    'hotel': [
        r'\bhotel\b', r'\bresort\b', r'\binn\b', r'\bsuite\b',
        r'\b(king|queen|double|twin) bed\b', r'\bbedroom\b',
        r'\bcondo\b', r'\bapartment\b', r'\bairbnb\b', r'\blodge\b',
        r'\bmotel\b', r'\broom with\b', r'\bstandard room\b',
        r'\bdeluxe room\b', r'\bsuperior room\b', r'\bjunior suite\b',
        r'\bvilla rental\b', r'\bovernight stay\b',
        r'\bcheck.?in\b', r'\bcheckout\b',
        r'\bnight\(s\)\b', r'\b\d+ nights?\b',
        r'\bbungalow\b', r'\bcabin\b', r'\bcabana\b',
    ],
    'nightlife': [
        r'\bnightclub\b', r'\bcoco bongo\b', r'\bbongo\b',
        r'\bse[ñn]or frogs\b', r'\bcarlos.?n.?charlies\b',
        r'\bmandala\b', r'\bcongo bar\b', r'\bmaroca\b',
        r'\bareia beach club\b', r'\bla vaquita\b', r'\bdady.?o\b',
        r'\bdady rock\b', r'\bnightlife\b', r'\bnight club\b',
        r'\bnight tour\b(?! kayak)(?! paddle)',
        r'\bopen bar\b(?! cruise)(?! sail)(?! charter)(?! tour)',
        r'\bvip table\b', r'\bbottle service\b', r'\bcover charge\b',
        r'\bvip ultra experience\b', r'\bpremium open bar\b',
        r'\bdisco\b(?! ride)',
    ],
    'restaurant': [
        r'\brestaurant\b', r'\bdinner reservation\b',
        r'\bsteakhouse\b', r'\bbrunch\b(?! cruise)(?! sail)',
        r'\bdining experience\b', r'\bcaf[eé] reservation\b',
    ],
    'shuttle': [
        r'^shuttle\b', r'\bshuttle service\b',
        r'\bairport transfer\b', r'\bairport pickup\b',
        r'\bairport\s+to\s+(?:downtown|hotel zone|riviera|puerto|playa)\b',
        r'\b(?:downtown|hotel zone|riviera|puerto|playa)\s+(?:from|to)\s+airport\b',
        r'^airport\s*/', r'^[A-Z\w-]+\s+airport\s+to\b',
        r'\bair shuttle\b',
        r'\bone[- ]way trip\b', r'\bround trip transfer\b',
        r'\bone[- ]way ride\b', r'\bairport.* to (?:hotel|resort|zone)\b',
        r'\b(?:hotel|resort) zone.* to airport\b',
        r'\b(?:pickup|drop[- ]off|drop off) (?:service|transfer)\b',
        r'\bvan rental\b', r'\bprivate transfer\b',
        r'^transportation$', r'^transportation \b',
    ],
}

# Patrones de EXCLUSIÓN (si match, NO reclasificar — falsos positivos)
EXCLUDE = {
    'shuttle': [
        r'\bspace shuttle\b',     # Space Shuttle Excursions = tour del Kennedy
        r'\bno transportation\b', # "Park Entree (No transportation)"
        r'\bno trans\b',          # variantes "(no trans)"
        r'\bwithout transportation\b',
        r'\bshuttle.*tour\b',     # algo como "shuttle bus tour"
    ],
    'restaurant': [
        r'\bcafé tour\b', r'\bcafe tour\b',
        r'\brestaurant tour\b',
    ],
    'hotel': [
        r'\bhotel pickup\b',
        r'\bhotel pick[- ]?up\b',
        r'\bhotel transfer\b',
        r'\bfrom (?:your )?hotel\b',
        r'\bvilla park\b',
        r'\bhotel zone\b',          # "Cancun airport to hotel zone" = shuttle, no hotel
        r'\bairport.*hotel\b',
        r'\bshuttle.*hotel\b',
        r'\btransfer.*hotel\b',
    ],
    'nightlife': [
        r'\bopen bar (?:cruise|sail|catamaran|boat|charter|tour|party boat)\b',
        r'\bbongo drum\b',  # Bongo drumming, no Coco Bongo
    ],
}


def classify(name: str) -> str | None:
    name_l = name.lower()
    for cat in ('shuttle', 'mayan_cenote', 'golf', 'wildlife', 'culinary', 'ghost', 'nightlife', 'restaurant', 'hotel'):
        # Primero: ¿hay match positivo?
        if not any(re.search(p, name_l) for p in INCLUDE[cat]):
            continue
        # Segundo: ¿está excluido?
        if any(re.search(p, name_l) for p in EXCLUDE.get(cat, [])):
            continue
        return cat
    return None


# ── Aplicar ────────────────────────────────────────────────────────────
ops = json.load(open('operators.json'))
tour_ops = [o for o in ops if o.get('cat') == 'tour']
print(f'Operadores actualmente en cat=tour: {len(tour_ops)}')

changes = {'golf': [], 'wildlife': [], 'mayan_cenote': [], 'culinary': [], 'ghost': [], 'shuttle': [], 'hotel': [], 'nightlife': [], 'restaurant': []}
for o in tour_ops:
    new_cat = classify(o.get('name', ''))
    if new_cat:
        changes[new_cat].append(o)

# Resumen
print('═' * 60)
print('  RECLASIFICACIÓN  ' + ('(DRY RUN)' if DRY_RUN else '(APLICADA)'))
print('═' * 60)
for cat, lst in changes.items():
    print(f'  tour → {cat:<12} {len(lst):>4} ops')
total = sum(len(v) for v in changes.values())
print(f'  Total reclasificados: {total} (de {len(tour_ops)} tours)')
print()

# Muestra por categoría
for cat, lst in changes.items():
    if lst:
        print(f'Sample {cat}:')
        for o in lst[:5]:
            print(f'  {o["id"]:<8} {o["name"][:65]}')
        print()

if DRY_RUN:
    print('Re-corre con --apply para escribir cambios')
    sys.exit(0)

# ── Escribir ───────────────────────────────────────────────────────────
ts = dt.datetime.utcnow().strftime('%Y%m%d-%H%M%S')
shutil.copy2('operators.json', f'operators.json.bak-{ts}')
for cat, lst in changes.items():
    for op in lst:
        op['cat'] = cat
with open('operators.json', 'w') as f:
    json.dump(ops, f, ensure_ascii=False, separators=(',', ':'))

# slim
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

print(f'✓ operators.json: {total} categorías actualizadas')
print(f'✓ operators-slim.json: {slim_updates} updates')
print(f'  Backups: operators.json.bak-{ts}')
print()

# Verificación
ops2 = json.load(open('operators.json'))
new_dist = Counter(o.get('cat') for o in ops2)
print('Distribución final de categorías:')
for c, n in new_dist.most_common():
    print(f'  {c:<15} {n:>5}')
