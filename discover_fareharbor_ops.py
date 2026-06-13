#!/usr/bin/env python3
"""
discover_fareharbor_ops.py — descubrir NUEVOS operadores FareHarbor.

Cómo funciona:
  1. Lee shortnames existentes desde operators.json
  2. Acepta input de candidatos via:
     - Archivo (--input shortnames.txt, uno por línea)
     - O scrape automático (--auto) de competidores por zona
  3. Para cada shortname NUEVO:
     - Verifica que existe (https://fareharbor.com/{shortname}/)
     - Extrae items disponibles (https://fareharbor.com/embeds/book/{shortname}/items/)
     - Detecta categoría/precio/nombre
  4. Genera proposed_new_ops.json con todo organizado, listo para revisar

Uso:
    # Opción A: aportas lista de shortnames
    python3 discover_fareharbor_ops.py --input shortnames.txt

    # Opción B: auto-discovery via Tripadvisor (requiere Playwright)
    python3 discover_fareharbor_ops.py --auto --zone miami

    # Opción C: análisis sin crawlear (revisar candidatos)
    python3 discover_fareharbor_ops.py --check candidate1,candidate2,...

Después de revisar proposed_new_ops.json, ejecutar merge_proposed_ops.py
para agregar los aprobados al operators.json.
"""
from __future__ import annotations
import json, re, sys, argparse, time
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/126.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
}

FH_SHORTNAME_RE = re.compile(r'fareharbor\.com/(?:embeds/book/)?([a-z0-9][a-z0-9-]+)/?', re.I)
FH_BASE = 'https://fareharbor.com'

# Mapeo de zona → ciudades a buscar
ZONE_SEARCH_TERMS = {
    'miami':       ['Miami Beach', 'Miami', 'Brickell', 'Coconut Grove'],
    'broward':     ['Fort Lauderdale', 'Hollywood FL', 'Dania Beach'],
    'keys':        ['Key West', 'Marathon FL', 'Key Largo', 'Islamorada'],
    'palmbeach':   ['Palm Beach', 'West Palm Beach', 'Jupiter FL'],
    'nefl':        ['Jacksonville', 'St Augustine', 'Amelia Island'],
    'space':       ['Cocoa Beach', 'Cape Canaveral', 'Titusville'],
    'orlando':     ['Orlando FL', 'Kissimmee'],
    'gulf':        ['Naples FL', 'Marco Island', 'Fort Myers', 'Tampa', 'Destin', 'PCB'],
    'hawaii':      ['Maui', 'Oahu', 'Kauai', 'Big Island Hawaii', 'Honolulu'],
    'cancun':      ['Cancun', 'Playa del Carmen', 'Tulum', 'Riviera Maya'],
    'puntacana':   ['Punta Cana', 'Bavaro', 'Bayahibe'],
}


def load_existing_shortnames(path='operators.json'):
    """Extrae todos los shortnames FareHarbor desde operators.json."""
    ops = json.load(open(path))
    existing = set()
    for o in ops:
        link = o.get('link', '')
        m = FH_SHORTNAME_RE.search(link)
        if m:
            existing.add(m.group(1).lower())
    return existing


def fetch(url, timeout=10):
    """HTTP GET, returns (status, body) o (status, None) on error."""
    try:
        req = Request(url, headers=HEADERS)
        resp = urlopen(req, timeout=timeout)
        return resp.status, resp.read().decode('utf-8', errors='ignore')
    except HTTPError as e:
        return e.code, None
    except URLError:
        return 0, None
    except Exception:
        return -1, None


def verify_shortname(shortname):
    """Verifica shortname y devuelve dict con status detallado.

    Status possibles:
      ok             — existe + items extraídos
      exists_no_items — existe pero items requieren JS render (manual check)
      not_found      — 404, no existe
      forbidden      — 403, posible anti-bot — abrir en browser
      network_error  — timeout o conexión rota
    """
    # 1. Página principal
    url = f'{FH_BASE}/embeds/book/{shortname}/'
    status, html = fetch(url)

    if status == 0 or status == -1:
        return {'shortname': shortname, 'status': 'network_error', 'http_code': status, 'reason': 'Timeout o conexión rota'}
    if status == 404 or status == 410:
        # 404 en /embeds/book/X/ = shortname no existe (esa ruta SIEMPRE debe existir si la company existe)
        return {'shortname': shortname, 'status': 'not_found', 'http_code': status, 'reason': 'Shortname no existe en FareHarbor (puede ser typo)'}
    if status == 403:
        return {'shortname': shortname, 'status': 'forbidden', 'http_code': 403, 'reason': 'Bloqueado (anti-bot). Verifica manualmente en browser.'}
    if status != 200 or not html:
        return {'shortname': shortname, 'status': f'http_{status}', 'http_code': status, 'reason': f'HTTP {status}'}

    # Extraer items disponibles — múltiples patrones
    item_pattern_1 = re.compile(r'/items/(\d+)/?[^"]*"[^>]*>([^<]+)</a>', re.I)
    item_pattern_2 = re.compile(r'data-item-pk="(\d+)"[^>]*>([^<]+)<', re.I)
    item_pattern_3 = re.compile(r'"itemPk"\s*:\s*(\d+)\s*,\s*"name"\s*:\s*"([^"]+)"', re.I)
    item_pattern_4 = re.compile(r'"pk"\s*:\s*(\d+).*?"name"\s*:\s*"([^"]+)"', re.I)

    items = []
    seen_ids = set()
    for pattern in (item_pattern_1, item_pattern_2, item_pattern_3, item_pattern_4):
        for m in pattern.finditer(html):
            item_id = m.group(1)
            item_name = m.group(2).strip()
            if item_id and item_name and len(item_name) > 3 and item_id not in seen_ids:
                items.append({'id': item_id, 'name': item_name[:120]})
                seen_ids.add(item_id)
        if items: break

    # Nombre de empresa
    name_m = re.search(r'<title>([^<|]+)', html)
    company_name = name_m.group(1).strip() if name_m else shortname
    # Limpiar "Book Online - " prefix común
    company_name = re.sub(r'^(?:Book Online[\s\-—:]*)', '', company_name).strip()

    # Si no hay items pero la página existe, probablemente JS rendered
    if not items:
        return {
            'shortname': shortname,
            'status': 'exists_no_items',
            'http_code': 200,
            'company_name': company_name,
            'main_url': url,
            'reason': 'Existe pero items requieren render JS. Abre la URL para verificar manualmente.',
            'items': [],
            'item_count': 0,
            'guessed_cat': 'tour',
            'guessed_zone': 'unknown',
        }

    # Categoría/zona (heurística por keywords en items)
    all_text = (company_name + ' ' + ' '.join(i['name'] for i in items)).lower()
    cat = guess_cat(all_text)
    zone = guess_zone(all_text)

    return {
        'shortname': shortname,
        'status': 'ok',
        'http_code': 200,
        'company_name': company_name,
        'items': items[:20],
        'item_count': len(items),
        'guessed_cat': cat,
        'guessed_zone': zone,
        'main_url': url,
        'verified_at': time.strftime('%Y-%m-%d'),
    }


def guess_cat(text):
    """Heurística cat por keywords."""
    text = text.lower()
    rules = [
        ('jetski',     [r'jet ski', r'pwc', r'waverunner']),
        ('boat',       [r'boat (?:rental|charter)', r'pontoon', r'center console']),
        ('yacht',      [r'yacht', r'mega yacht', r'luxury charter']),
        ('fishing',    [r'fishing (?:charter|trip)', r'deep sea', r'inshore']),
        ('snorkel',    [r'snorkel', r'dive', r'scuba']),
        ('sunset',     [r'sunset (?:cruise|sail)']),
        ('atv',        [r'\batv\b', r'utv', r'side.by.side']),
        ('aerial',     [r'parasail', r'helicopter', r'skydiv']),
        ('bikerental', [r'bike rental', r'e.bike', r'bicycle']),
        ('watersports', [r'water sports', r'kayak', r'paddle ?board', r'sup']),
        ('airboat',    [r'airboat', r'everglades']),
        ('tour',       [r'tour', r'sightseeing', r'walking']),
    ]
    for cat, patterns in rules:
        if any(re.search(p, text) for p in patterns):
            return cat
    return 'tour'


def guess_zone(text):
    """Heurística zona por keywords geo."""
    text = text.lower()
    rules = [
        ('miami',       [r'miami beach', r'miami(?! beach)', r'south beach', r'brickell']),
        ('broward',     [r'fort lauderdale', r'broward', r'hollywood (?:fl|beach)']),
        ('keys',        [r'key west', r'marathon', r'key largo', r'islamorada']),
        ('palmbeach',   [r'palm beach', r'jupiter']),
        ('nefl',        [r'jacksonville', r'st\.? augustine', r'amelia island']),
        ('orlando',     [r'orlando', r'kissimmee', r'disney']),
        ('space',       [r'cocoa beach', r'cape canaveral', r'space coast']),
        ('westfl',      [r'naples', r'marco island', r'fort myers', r'tampa', r'destin', r'panama city']),
        ('hawaii',      [r'maui', r'oahu', r'kauai', r'kona', r'hawaii', r'honolulu']),
        ('cancun',      [r'cancun', r'playa del carmen', r'tulum', r'riviera maya']),
        ('puntacana',   [r'punta cana', r'bavaro', r'bayahibe']),
    ]
    for zone, patterns in rules:
        if any(re.search(p, text) for p in patterns):
            return zone
    return 'unknown'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', help='Archivo con shortnames (uno por línea)')
    parser.add_argument('--check', help='Lista comma-separated de shortnames')
    parser.add_argument('--all', action='store_true', help='Procesar todos los candidatos')
    args = parser.parse_args()

    print('═══ FareHarbor Discovery ═══\n')

    # Cargar existentes
    existing = load_existing_shortnames()
    print(f'Operadores existentes: {len(existing)} shortnames únicos')

    # Cargar candidatos
    candidates = set()
    if args.input:
        with open(args.input) as f:
            for line in f:
                # Soporta tanto shortname puro como URL completa
                line = line.strip()
                if not line: continue
                m = FH_SHORTNAME_RE.search(line)
                if m: candidates.add(m.group(1).lower())
                elif re.match(r'^[a-z0-9-]+$', line): candidates.add(line.lower())
    elif args.check:
        for s in args.check.split(','):
            candidates.add(s.strip().lower())
    else:
        print('\nUsa --input archivo.txt o --check shortname1,shortname2')
        print('\nFormato del archivo: un shortname (o URL FareHarbor) por línea, ej:')
        print('  aquafusionmiami')
        print('  https://fareharbor.com/embeds/book/sixfinskeywest/')
        print('  bruschiboatrental')
        return

    print(f'Candidatos a verificar: {len(candidates)}')

    # Filtrar solo los NUEVOS
    new_candidates = candidates - existing
    print(f'Ya existentes (skip): {len(candidates) - len(new_candidates)}')
    print(f'NUEVOS a verificar:   {len(new_candidates)}')

    if not new_candidates:
        print('\n✓ No hay shortnames nuevos. Nothing to do.')
        return

    # Verificar c/u en paralelo
    print(f'\nVerificando los {len(new_candidates)} nuevos shortnames...')
    new_ops = []           # ok + exists_no_items (ambos exist verified)
    fully_verified = []    # solo ok
    needs_manual = []      # exists_no_items
    not_found = []
    forbidden = []
    other_errors = []

    with ThreadPoolExecutor(max_workers=10) as ex:
        futures = {ex.submit(verify_shortname, s): s for s in new_candidates}
        done = 0
        for f in as_completed(futures):
            shortname = futures[f]
            try:
                result = f.result()
            except Exception as e:
                result = {'shortname': shortname, 'status': 'exception', 'reason': str(e)}
            done += 1
            st = result.get('status', '?')
            if st == 'ok':
                new_ops.append(result)
                fully_verified.append(shortname)
                print(f'  ✓ [{done}/{len(new_candidates)}] {shortname:<30} — {result["company_name"][:35]:<35} ({result["item_count"]} items, {result["guessed_cat"]}/{result["guessed_zone"]})')
            elif st == 'exists_no_items':
                new_ops.append(result)
                needs_manual.append(shortname)
                print(f'  ⚠ [{done}/{len(new_candidates)}] {shortname:<30} — EXISTE pero items via JS (revisar manualmente)')
            elif st == 'not_found':
                not_found.append(shortname)
                print(f'  ✗ [{done}/{len(new_candidates)}] {shortname:<30} — 404 NO EXISTE')
            elif st == 'forbidden':
                forbidden.append(shortname)
                print(f'  ⛔ [{done}/{len(new_candidates)}] {shortname:<30} — 403 BLOQUEADO (verifica en browser)')
            else:
                other_errors.append((shortname, result.get('reason', st)))
                print(f'  ❌ [{done}/{len(new_candidates)}] {shortname:<30} — {st}: {result.get("reason","?")[:50]}')

    # Resumen
    print(f'\n{"═"*70}')
    print(f'  RESUMEN:')
    print(f'  ✓ Verificados completos:    {len(fully_verified)}')
    print(f'  ⚠ Existen, revisar manual:  {len(needs_manual)}')
    print(f'  ✗ No encontrados (404):     {len(not_found)}')
    print(f'  ⛔ Bloqueados (403):         {len(forbidden)}')
    print(f'  ❌ Otros errores:           {len(other_errors)}')

    failures = not_found + forbidden + [s for s, _ in other_errors]

    # Agrupar por zona/cat
    from collections import Counter
    by_zone = Counter(o['guessed_zone'] for o in new_ops)
    by_cat = Counter(o['guessed_cat'] for o in new_ops)
    print(f'\n  Por zona:')
    for z, n in by_zone.most_common(): print(f'    {z:<12} {n}')
    print(f'\n  Por categoría:')
    for c, n in by_cat.most_common(): print(f'    {c:<12} {n}')

    # Guardar
    output = {
        'generated_at': time.strftime('%Y-%m-%d %H:%M:%S'),
        'existing_count': len(existing),
        'candidates_checked': len(candidates),
        'new_ops_found': len(new_ops),
        'fully_verified': fully_verified,
        'needs_manual_review': needs_manual,
        'not_found_404': not_found,
        'forbidden_403': forbidden,
        'other_errors': other_errors,
        'new_ops': sorted(new_ops, key=lambda o: (o.get('guessed_zone',''), o.get('guessed_cat',''))),
    }
    with open('proposed_new_ops.json', 'w') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print(f'\n✓ Reporte: proposed_new_ops.json')
    print(f'\nQUÉ HACER:')
    if fully_verified:
        print(f'  → {len(fully_verified)} listos para mergear:')
        print(f'    python3 merge_proposed_ops.py --list')
        print(f'    python3 merge_proposed_ops.py --approve {",".join(fully_verified[:3])}{"..." if len(fully_verified)>3 else ""}')
    if needs_manual:
        print(f'\n  → {len(needs_manual)} existen pero items son JS-rendered.')
        print(f'    Abre estas URLs en browser para confirmar items:')
        for s in needs_manual[:5]:
            print(f'      https://fareharbor.com/embeds/book/{s}/')
    if not_found:
        print(f'\n  → {len(not_found)} no existen (404). Verifica typos.')


if __name__ == '__main__':
    main()
