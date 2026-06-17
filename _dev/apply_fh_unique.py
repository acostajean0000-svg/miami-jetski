#!/usr/bin/env python3
from __future__ import annotations
"""
apply_fh_unique.py — aplica resultados del scrape garantizando fotos ÚNICAS.

Diferencia con apply_fh_scrape_results.py:
  • Reserva fotos: cada handle solo se asigna a UN operador
  • Procesa primero los ops con foto null, luego los con foto duplicada
  • Para cada operador objetivo:
      - Toma los handles scrapeados de su página de FareHarbor
      - Filtra los que YA están reservados por otro op
      - Picks el primero disponible
  • Si después de procesar todo aún quedan ops sin foto única, los reporta

Inputs:
  fh_scrape_photos.json — output del scrape_fareharbor_photos.js
  operators.json        — estado actual
  photo_targets.json    — lista de ops a procesar (opcional)

Uso:
    python3 apply_fh_unique.py            # dry run
    python3 apply_fh_unique.py --apply    # escribir cambios
"""
import json, re, sys, os, shutil, datetime as dt
from collections import Counter

DRY_RUN = '--apply' not in sys.argv

HANDLE_RE = re.compile(r'filestackcontent\.com/([A-Za-z0-9]{15,30})')
FILESTACK_BASE = 'https://cdn.filestackcontent.com/'
SUFFIX = '/convert?cache=true&compress=true&quality=90&format=webp&rotate=exif&w=1000&fit=max'


def handle_of(url: str) -> str | None:
    if not url: return None
    m = HANDLE_RE.search(url)
    return m.group(1) if m else None


# ── Cargar inputs ──────────────────────────────────────────────────────
if not os.path.exists('fh_scrape_photos.json'):
    print('❌ Falta fh_scrape_photos.json — primero corre node scrape_fareharbor_photos.js')
    sys.exit(1)

scraped = json.load(open('fh_scrape_photos.json'))
ops     = json.load(open('operators.json'))
op_by_id = {o['id']: o for o in ops}

print(f'Scraped data: {len(scraped)} operadores con resultados')
print(f'Total operadores en operators.json: {len(ops)}')

# ── Reservar handles ya en uso por ops NO objetivo ─────────────────────
# Identificar handles compartidos y huérfanos
shared = Counter(handle_of(o.get('photo', '')) for o in ops if handle_of(o.get('photo', '')))
uniquely_owned = {h for h, n in shared.items() if n == 1}
print(f'Handles ya únicos en uso:  {len(uniquely_owned)}')

# Set de handles ya tomados (no podemos asignarlos a otro op)
reserved: set[str] = set(uniquely_owned)

# ── Identificar ops objetivo (null o compartido) ───────────────────────
target_ops = []
for o in ops:
    h = handle_of(o.get('photo', ''))
    if not h or shared[h] > 1:
        target_ops.append(o)

print(f'Operadores objetivo: {len(target_ops)}')
print()

# Orden: null primero (mas urgente), luego ops con foto duplicada
target_ops.sort(key=lambda o: (handle_of(o.get('photo', '')) is not None, o['id']))

# ── Asignar handle único por op ────────────────────────────────────────
assigned = 0
skipped_no_data = 0
skipped_no_unique = 0
failures = []

for op in target_ops:
    op_id = op['id']
    sc = scraped.get(op_id)
    if not sc:
        skipped_no_data += 1
        continue
    handles = sc.get('handles', []) if isinstance(sc, dict) else sc
    if not handles:
        skipped_no_data += 1
        continue

    # Probar cada handle scrapeado, el primero no reservado gana
    chosen = None
    for h in handles:
        if h not in reserved:
            chosen = h
            break

    if not chosen:
        # Todos los handles del op ya están reservados — falla
        skipped_no_unique += 1
        failures.append({'id': op_id, 'name': op.get('name', ''), 'tried': handles[:5]})
        continue

    # Asignar
    new_url = FILESTACK_BASE + chosen + SUFFIX
    op['photo'] = new_url
    reserved.add(chosen)
    assigned += 1

# ── Resumen ────────────────────────────────────────────────────────────
print('═' * 60)
print('  ASIGNACIÓN' + ('  (DRY RUN)' if DRY_RUN else '  APLICADA'))
print('═' * 60)
print(f'  Asignadas (foto nueva única):    {assigned}')
print(f'  Sin datos scrapeados:            {skipped_no_data}')
print(f'  Sin handle disponible (colisión): {skipped_no_unique}')
print()

if failures:
    print('Operadores que necesitan más fotos (todas las suyas ya están reservadas):')
    for f in failures[:10]:
        print(f'  {f["id"]} - {f["name"][:50]}')
    if len(failures) > 10:
        print(f'  ... y {len(failures)-10} más')

if DRY_RUN:
    print('\nRe-corre con --apply para escribir cambios a operators.json + operators-slim.json')
    sys.exit(0)

# ── Aplicar ────────────────────────────────────────────────────────────
ts = dt.datetime.utcnow().strftime('%Y%m%d-%H%M%S')
shutil.copy2('operators.json', f'operators.json.bak-{ts}')
with open('operators.json', 'w') as f:
    json.dump(ops, f, ensure_ascii=False, separators=(',', ':'))

# operators-slim.json — sincronizar el campo photo
slim = json.load(open('operators-slim.json'))
slim_by_id = {o['id']: o for o in slim}
slim_updates = 0
for op in target_ops:
    if op['id'] in slim_by_id:
        slim_by_id[op['id']]['photo'] = op['photo']
        slim_updates += 1
shutil.copy2('operators-slim.json', f'operators-slim.json.bak-{ts}')
with open('operators-slim.json', 'w') as f:
    json.dump(slim, f, ensure_ascii=False, separators=(',', ':'))

print(f'\n✓ operators.json actualizado ({assigned} fotos nuevas)')
print(f'✓ operators-slim.json sincronizado ({slim_updates} updates)')
print(f'  Backups: operators.json.bak-{ts}, operators-slim.json.bak-{ts}')

# ── Verificación ────────────────────────────────────────────────────────
print('\n═ Verificación final ═')
ops2 = json.load(open('operators.json'))
nulls = sum(1 for o in ops2 if not o.get('photo'))
counts = Counter(handle_of(o.get('photo', '')) for o in ops2 if handle_of(o.get('photo', '')))
shared_after = sum(1 for c in counts.values() if c > 1)
print(f'Operadores sin foto:       {nulls}')
print(f'Fotos únicas en uso:        {len(counts)}')
print(f'Fotos compartidas todavía:  {shared_after}')
print(f'Top dupes:')
for h, c in counts.most_common(5):
    if c > 1: print(f'  {c}× {h}')
