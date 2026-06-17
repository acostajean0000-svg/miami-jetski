#!/usr/bin/env python3
"""
merge_proposed_ops.py — mergea ops aprobadas de proposed_new_ops.json a operators.json.

Para cada op aprobada, genera entries con el schema correcto:
  - id auto-generado (próximo disponible según cat prefix)
  - link FareHarbor embed completo
  - photo: scrape después con scrape_fareharbor_photos.js
  - price: parsear desde FH (TODO automático)
  - lat/lng: dejar 0,0 (humano edita después)

Uso:
    # Listar candidatos aprobables
    python3 merge_proposed_ops.py --list

    # Mergear shortnames específicos
    python3 merge_proposed_ops.py --approve shortname1,shortname2

    # Mergear todos los proposed (¡cuidado!)
    python3 merge_proposed_ops.py --approve-all

    # Solo dry run (no escribe)
    python3 merge_proposed_ops.py --approve-all --dry-run
"""
from __future__ import annotations
import json, sys, argparse, re, shutil, datetime as dt

# Mapeo cat → prefijo ID
CAT_PREFIX = {
    'jetski':'js', 'boat':'bt', 'yacht':'yh', 'fishing':'fi', 'snorkel':'ws',
    'sunset':'su', 'watersports':'ws', 'atv':'at', 'golfcart':'gc', 'aerial':'ae',
    'tour':'to', 'bikerental':'br', 'slingshot':'sl', 'exotic':'ex', 'jetcar':'jc',
    'airboat':'aw', 'hotel':'ht', 'golf':'gl', 'wildlife':'wl', 'mayan_cenote':'mc',
    'culinary':'cl', 'ghost':'gh', 'themepark':'tp', 'walking_tour':'wt',
    'lei':'lg', 'segway':'sg', 'zipline':'zl', 'nightlife':'nl', 'villa':'vl',
    'restaurant':'rs', 'shuttle':'sh', 'flowers':'fl',
}

ZONE_TO_CITY = {
    'miami': ('Miami', 'FL', 'US', 25.7617, -80.1918),
    'broward': ('Fort Lauderdale', 'FL', 'US', 26.1224, -80.1373),
    'keys': ('Florida Keys', 'FL', 'US', 24.5551, -81.7800),
    'palmbeach': ('Palm Beach', 'FL', 'US', 26.7056, -80.0364),
    'nefl': ('Jacksonville', 'FL', 'US', 30.3322, -81.6557),
    'space': ('Cocoa Beach', 'FL', 'US', 28.3922, -80.6077),
    'orlando': ('Orlando', 'FL', 'US', 28.5383, -81.3792),
    'gulf': ('Naples', 'FL', 'US', 26.1420, -81.7948),
    'westfl': ('Naples', 'FL', 'US', 26.1420, -81.7948),
    'hawaii': ('Honolulu', 'HI', 'US', 21.3099, -157.8581),
    'cancun': ('Cancún', 'QR', 'MX', 21.1619, -86.8515),
    'puntacana': ('Punta Cana', 'LA', 'DO', 18.5601, -68.3725),
    'unknown': ('Unknown', '', '', 0, 0),
}


def next_id(existing_ids, prefix):
    """Encuentra el próximo ID disponible."""
    used = set()
    pat = re.compile(rf'^{prefix}(\d+)$')
    for op_id in existing_ids:
        m = pat.match(op_id)
        if m: used.add(int(m.group(1)))
    return f'{prefix}{max(used)+1 if used else 1}'


def build_op(proposal, item, op_id, ops_existing_count):
    """Construye una entry para operators.json desde un item del proposal."""
    cat = proposal['guessed_cat']
    zone = proposal['guessed_zone']
    city, region, country, lat, lng = ZONE_TO_CITY.get(zone, ZONE_TO_CITY['unknown'])
    shortname = proposal['shortname']

    fh_link = (
        f'https://fareharbor.com/embeds/book/{shortname}/items/{item["id"]}/'
        '?asn=fhdn&asn-ref=miamistylerentals&ref=miamistylerentals'
        '&bookable-only=yes&full-items=yes&marketplace=yes&flow=no'
    )

    return {
        'id': op_id,
        'name': item['name'],
        'addr': f'{city}, {region}, {country}'.strip(', '),
        'zone': zone,
        'zl': city,
        'cat': cat,
        'price': 100,  # placeholder — humano actualiza
        'lat': lat,
        'lng': lng,
        'photo': None,  # scrape después con scrape_fareharbor_photos.js
        'link': fh_link,
        'pax': 6,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--list', action='store_true', help='Listar candidatos aprobables')
    parser.add_argument('--approve', help='Shortnames separados por coma')
    parser.add_argument('--approve-all', action='store_true', help='Aprobar todos')
    parser.add_argument('--dry-run', action='store_true', help='No escribir cambios')
    args = parser.parse_args()

    try:
        prop = json.load(open('proposed_new_ops.json'))
    except FileNotFoundError:
        print('❌ Falta proposed_new_ops.json. Corre discover_fareharbor_ops.py primero.')
        sys.exit(1)

    new_ops = prop.get('new_ops', [])
    print(f'═══ Proposals: {len(new_ops)} new ops ═══\n')

    if args.list:
        print(f'{"Shortname":<25} {"Items":<7} {"Cat":<12} {"Zone":<12} {"Name"}')
        print('─' * 100)
        for o in new_ops:
            print(f'{o["shortname"]:<25} {o["item_count"]:<7} {o["guessed_cat"]:<12} {o["guessed_zone"]:<12} {o["company_name"][:35]}')
        return

    # Determinar qué aprobar
    if args.approve_all:
        approved = {o['shortname'] for o in new_ops}
    elif args.approve:
        approved = {s.strip().lower() for s in args.approve.split(',')}
    else:
        print('Usa --list, --approve <names>, o --approve-all')
        return

    to_add = [o for o in new_ops if o['shortname'] in approved]
    print(f'Aprobados: {len(to_add)}\n')

    if not to_add: return

    # Cargar operators.json
    ops = json.load(open('operators.json'))
    existing_ids = {o['id'] for o in ops}

    # Construir set de (shortname, item_id) ya existentes para detectar duplicados
    existing_items = set()
    for o in ops:
        link = o.get('link', '')
        sm = re.search(r'fareharbor\.com/(?:embeds/book/)?([a-z0-9][a-z0-9-]+)', link, re.I)
        im = re.search(r'/items/(\d+)', link)
        if sm and im:
            existing_items.add((sm.group(1).lower(), im.group(1)))

    new_entries = []
    skipped_dupes = 0
    for proposal in to_add:
        prefix = CAT_PREFIX.get(proposal['guessed_cat'], 'to')
        shortname = proposal['shortname'].lower()
        for item in proposal['items']:
            # Skip si ya existe (shortname, item_id)
            if (shortname, item['id']) in existing_items:
                skipped_dupes += 1
                continue
            op_id = next_id(existing_ids, prefix)
            existing_ids.add(op_id)
            entry = build_op(proposal, item, op_id, len(ops))
            new_entries.append(entry)
            existing_items.add((shortname, item['id']))

    if skipped_dupes:
        print(f'⚠️  {skipped_dupes} items ya existían en operators.json (skip)')

    print(f'Total nuevos items a agregar: {len(new_entries)}')
    print('\nMuestra (primeros 5):')
    for e in new_entries[:5]:
        print(f'  {e["id"]:<8} cat={e["cat"]:<10} zone={e["zone"]:<10} {e["name"][:50]}')

    if args.dry_run:
        print('\n(DRY RUN — no se escribió nada)')
        return

    # Backup + escribir
    ts = dt.datetime.utcnow().strftime('%Y%m%d-%H%M%S')
    shutil.copy2('operators.json', f'operators.json.bak-{ts}')
    shutil.copy2('operators-slim.json', f'operators-slim.json.bak-{ts}')

    ops.extend(new_entries)
    with open('operators.json', 'w') as f:
        json.dump(ops, f, ensure_ascii=False, separators=(',', ':'))

    # Sincronizar slim (mismo schema, sin metadata extra)
    slim = json.load(open('operators-slim.json'))
    slim.extend(new_entries)
    with open('operators-slim.json', 'w') as f:
        json.dump(slim, f, ensure_ascii=False, separators=(',', ':'))

    print(f'\n✓ {len(new_entries)} ops agregados a operators.json + operators-slim.json')
    print(f'✓ Backups: .bak-{ts}')
    print(f'\nPróximos pasos:')
    print('  1. Corre scrape_fareharbor_photos.js para extraer las fotos reales')
    print('  2. Revisa los nuevos ops en operators.json y ajusta:')
    print('     - price (los actuales son placeholders de $100)')
    print('     - lat/lng exactos (los actuales son centros de zona)')
    print('     - addr completa con dirección real')
    print('  3. Regenera HTMLs para los nuevos slugs')
    print('  4. Regenera /data/X.json + sitemaps')


if __name__ == '__main__':
    main()
