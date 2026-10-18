#!/usr/bin/env python3
"""SEO de /miami-jet-ski-rentals (EN): título, H1, tabla comparativa con precios reales, guía, FAQ + JSON-LD.
Fuentes: data/miami-jetski.json (operadores y precios FareHarbor), fh_avail/*.csv (nombre de empresa), slug-map.js.
Idempotente: reemplaza los bloques marcados con <!-- SEO-JS:... --> si ya existen."""
import io, re, json, csv, glob, html, os, statistics
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DOM = 'https://miamijetskiboatrentals.com'
F = 'es/miami-jet-ski-rentals.html'
e = lambda s: html.escape(str(s), quote=True)

ops = json.load(open('data/miami-jetski.json'))
sm = json.loads(re.search(r'=\s*(\{.*\})', open('slug-map.js').read(), re.S).group(1))
comp = {}
for f in glob.glob('fh_avail/*.csv'):
    for r in csv.DictReader(open(f, encoding='utf-8', errors='replace')):
        if r.get('item_id'): comp[r['item_id']] = (r.get('company_name') or '').strip()
P = {}
pf = sorted(glob.glob('tools-data/fh-prices-*.json'))
if pf: P = json.load(open(pf[-1]))
PRICE_DATE = re.search(r'(\d{4}-\d{2}-\d{2})', pf[-1]).group(1) if pf else ''

def iid(o): return re.search(r'(?:/items/|^[^/:]+/)(\d+)', o['link']).group(1)
def fhlink(o):
    l = o['link']
    if l.startswith('http'): return l
    sn, i = l.split('/', 1)
    return 'https://fareharbor.com/embeds/book/%s/items/%s/?asn=fhdn&asn-ref=miamistylerentals&ref=miamistylerentals&bookable-only=yes&full-items=yes&marketplace=yes&flow=no&branding=no' % (sn, i)
def money(p): return ('$%d' % p) if float(p) == int(p) else ('$%.2f' % p)

rows = []
for o in ops:
    i = iid(o); c = comp.get(i) or ''
    rows.append(dict(o=o, slug=sm.get(o['id']), company=c, price=float(o['price']) if o.get('price') else None,
                     label=(P.get(i, {}).get('label') or '').strip(), rating=float(o.get('rating') or 0), reviews=int(o.get('reviews') or 0),
                     area=o.get('zl') or 'Miami'))
rows.sort(key=lambda r: (-r['rating'], -r['reviews']))
N = len(rows)
priced = [r['price'] for r in rows if r['price']]
lo, hi, med = min(priced), max(priced), statistics.median(priced)
areas = {}
for r in rows: areas[r['area']] = areas.get(r['area'], 0) + 1
area_txt = ', '.join('%s (%d)' % (a, n) for a, n in sorted(areas.items(), key=lambda x: -x[1]))
tot_rev = sum(r['reviews'] for r in rows)
avg = sum(r['rating'] * r['reviews'] for r in rows) / max(tot_rev, 1)

def disp(r):
    n = r['o']['name'].strip()
    if r['company'] and r['company'].lower()[:10] not in n.lower(): return '%s — %s' % (r['company'], n)
    return n

# ---------- bloques ----------
table_rows = ''.join(
    '<tr><td><a href="/%s">%s</a><div class="cmp-sub">%s</div></td><td>%s</td><td>%s</td><td>%s</td><td><a class="cmp-book" href="%s" data-fh-name="%s" data-fh-price="%s" rel="nofollow sponsored" target="_blank">Reservar</a></td></tr>' % (
        r['slug'], e(r['company'] or r['o']['name']), e(r['o']['name'] if r['company'] else ''), e(r['area']),
        ('<strong>%s</strong><div class="cmp-sub">%s</div>' % (money(r['price']), e(r['label'][:34]))) if r['price'] else 'Ver precios',
        ('★ %.1f <span class="cmp-sub">(%s)</span>' % (r['rating'], format(r['reviews'], ','))) if r['reviews'] else '—',
        e(fhlink(r['o'])), e(r['o']['name']), int(r['price'] or 0))
    for r in rows)
COMPARE = '''<!-- SEO-JS:compare --><section id="compare"><div class="wrap" style="max-width:1000px">
<h2>Precios de alquiler de jet ski en Miami</h2>
<p class="sec-sub">Precio de partida del alquiler base de cada operador, tomado de su calendario de reservas de FareHarbor el %s. Entre los %d operadores con precio publicado, el alquiler empieza entre <strong>%s y %s</strong> (mediana %s). Impuestos, cargos y depósitos reembolsables se muestran al pagar.</p>
<div style="overflow-x:auto;margin-top:18px"><table class="cmp-table"><thead><tr><th>Operador</th><th>Zona</th><th>Desde</th><th>Valoración</th><th></th></tr></thead><tbody>%s</tbody></table></div>
</div></section><!-- /SEO-JS:compare -->''' % (PRICE_DATE, len(priced), money(lo), money(hi), money(med), table_rows)

GUIDE = '''<!-- SEO-JS:guide --><section style="background:var(--bg2)"><div class="wrap" style="max-width:820px">
<h2>Dónde montar en jet ski en Miami</h2>
<p class="sec-sub">Los %d operadores de esta página salen de estas zonas: %s.</p>
<h3>Biscayne Bay y Downtown Miami</h3><p>La mayoría de los alquileres salen de marinas cerca de Bayside Marketplace y el Venetian Causeway. El recorrido cruza Biscayne Bay con vistas al skyline del centro, Star Island y las islas de los causeways. La bahía es resguardada, por eso es la opción habitual para quien monta por primera vez.</p>
<h3>Miami Beach, Sunny Isles y Haulover</h3><p>Al norte de South Beach, los operadores salen de la zona de Haulover Inlet y del Intracoastal cerca de Sunny Isles. Hay paradas en bancos de arena y más mar abierto cuando sube el viento.</p>
<h3>Key Biscayne</h3><p>Los alquileres cerca del Rickenbacker Causeway van hacia las aguas de Key Biscayne, con calas más tranquilas y vistas hacia la ciudad.</p>
<h2 style="margin-top:34px">Normas para jet ski en Florida</h2>
<ul class="guide-list">
<li><strong>Edad:</strong> hay que tener al menos 18 años para alquilar una moto acuática y al menos 14 para conducirla.</li>
<li><strong>Formación náutica:</strong> quien haya nacido el 1 de enero de 1988 o después necesita la tarjeta Florida Boating Safety Education ID, o un certificado temporal, para conducir una embarcación de 10 hp o más. Los operadores de alquiler pueden emitir el certificado temporal tras un examen corto antes de salir.</li>
<li><strong>Chaleco salvavidas:</strong> todos a bordo deben llevar un chaleco no inflable aprobado por la Guardia Costera de EE. UU., y quien conduce debe llevar enganchado el cordón de corte del motor.</li>
<li><strong>Solo de día:</strong> no se pueden usar motos acuáticas desde media hora después de la puesta de sol hasta media hora antes del amanecer.</li>
<li><strong>Zonas de baja velocidad y manatíes:</strong> partes de Biscayne Bay son de velocidad reducida; quédate dentro de la zona que te indique el operador.</li>
</ul>
<p class="guide-src">Resumen de la normativa náutica de Florida; consulta el texto oficial en la <a href="https://myfwc.com/boating/" rel="nofollow noopener" target="_blank">Florida Fish and Wildlife Conservation Commission</a>.</p>
<h2 style="margin-top:34px">Consejos antes de reservar</h2>
<ul class="guide-list">
<li>Por la mañana el agua de la bahía suele estar más tranquila; por la tarde hay más oleaje cuando entra la brisa.</li>
<li>Comprueba si el precio es para una o dos personas, y si es paseo libre o tour guiado.</li>
<li>La mayoría pide un depósito reembolsable y un documento con foto al llegar; preséntate 15 minutos antes.</li>
</ul>
</div></section><!-- /SEO-JS:guide -->''' % (N, area_txt)

top5 = rows[:5]
faq = [
    ('¿Cuáles son los alquileres de jet ski mejor valorados en Miami?',
     'Por valoración de clientes, las mejores opciones ahora son: ' + '; '.join('%s (%.1f★, %s reseñas)' % (disp(r), r['rating'], format(r['reviews'], ',').replace(',', '.')) for r in top5) + '.',
     '<p>Por valoración de clientes, las mejores opciones ahora son:</p><ul>' + ''.join('<li><a href="/%s">%s</a> (%.1f★, %s reseñas)</li>' % (r['slug'], e(disp(r)), r['rating'], format(r['reviews'], ',').replace(',', '.')) for r in top5) + '</ul>'),
    ('¿Cuánto cuesta alquilar un jet ski en Miami?',
     'Entre %d operadores de Miami con precio publicado, el alquiler base empieza entre %s y %s (mediana %s), normalmente por una hora y una persona. Impuestos, cargos y un depósito reembolsable se añaden al pagar.' % (len(priced), money(lo), money(hi), money(med)), None),
    ('¿Necesito licencia para alquilar un jet ski en Miami?',
     'No necesitas licencia náutica. Quien haya nacido el 1 de enero de 1988 o después necesita la tarjeta Florida Boating Safety Education ID o un certificado temporal, que los operadores pueden emitir tras un examen corto antes de salir.', None),
    ('¿Qué edad mínima hay que tener para alquilar o conducir un jet ski en Florida?',
     'Hay que tener 18 años para alquilar y al menos 14 para conducir. Lleva un documento con foto; los menores normalmente pueden ir de pasajeros.', None),
    ('¿Desde dónde salen los jet skis en Miami?',
     'Los operadores de esta página salen de %s, sobre todo cerca de Bayside Marketplace y el Venetian Causeway en Biscayne Bay, Haulover y Sunny Isles al norte, y Key Biscayne.' % area_txt, None),
    ('¿Se puede montar en jet ski de noche en Miami?',
     'No. La ley de Florida no permite usar motos acuáticas desde media hora después de la puesta de sol hasta media hora antes del amanecer.', None),
    ('¿Puedo cancelar mi reserva de jet ski?',
     'Las condiciones de cancelación varían según el operador. Verás la política exacta antes de pagar y recibirás confirmación inmediata al reservar por FareHarbor.', None),
]
faq_html = '<!-- SEO-JS:faq --><div class="faq" style="margin-top:20px">' + ''.join(
    '<details%s><summary>%s</summary>%s</details>' % (' open' if k < 2 else '', e(q), h if h else '<p>%s</p>' % e(a)) for k, (q, a, h) in enumerate(faq)) + '</div><!-- /SEO-JS:faq -->'
faq_ld = {'@context': 'https://schema.org', '@type': 'FAQPage', 'mainEntity': [{'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': a}} for q, a, h in faq]}
itemlist = {'@context': 'https://schema.org', '@type': 'ItemList', 'name': 'Alquiler de jet ski en Miami', 'numberOfItems': N,
            'itemListElement': [{'@type': 'ListItem', 'position': k + 1, 'url': '%s/%s' % (DOM, r['slug']), 'name': disp(r)} for k, r in enumerate(rows)]}
CSS = '<style id="seo-js-css">.cmp-table{width:100%;border-collapse:collapse;font-size:.92rem}.cmp-table th{text-align:left;color:var(--muted);font-weight:600;padding:10px 8px;border-bottom:1px solid rgba(0,210,255,.15)}.cmp-table td{padding:12px 8px;border-bottom:1px solid rgba(255,255,255,.06);vertical-align:top}.cmp-table td a{color:#00d2ff;text-decoration:none;font-weight:600}.cmp-sub{color:var(--muted);font-size:.78rem;font-weight:400;margin-top:2px}.cmp-book{display:inline-block;background:#00d2ff;color:#040d1a!important;padding:6px 14px;border-radius:50px;font-size:.8rem}.guide-list{margin:12px 0 0 18px;line-height:1.7}.guide-list li{margin-bottom:6px}.guide-src{color:var(--muted);font-size:.82rem;margin-top:10px}.guide-src a{color:#00d2ff}section h3{margin-top:18px;font-size:1.05rem}</style>'

t = io.open(F, encoding='utf-8').read(); o = t
title = 'Alquiler de Jet Ski en Miami (2026): %d operadores y precios' % N
desc = 'Alquiler de jet ski en Miami desde %s. Compara %d operadores verificados en Biscayne Bay, Miami Beach, Haulover y Key Biscayne con precios en vivo y reserva inmediata.' % (money(lo), N)
t = re.sub(r'<title>[^<]*</title>', '<title>%s</title>' % e(title), t, 1)
for k, v in [('name="description"', desc), ('property="og:title"', title), ('name="twitter:title"', title), ('property="og:description"', desc), ('name="twitter:description"', desc)]:
    t = re.sub(r'(<meta %s content=")[^"]*(")' % re.escape(k), lambda m: m.group(1) + e(v) + m.group(2), t, 1)
t = re.sub(r'<h1>.*?</h1>', '<h1>Alquiler de Jet Ski en <span class="hl">Miami</span></h1>', t, 1, flags=re.S)
t = re.sub(r'(<p class="sub">)[^<]*(</p>)', r'\g<1>Compara %d operadores de jet ski verificados en Biscayne Bay, Miami Beach, Haulover y Key Biscayne — precios en vivo desde %s y reserva online inmediata.\2' % (N, money(lo)), t, 1)
# tabla + guía tras las tarjetas
t = re.sub(r'<!-- SEO-JS:compare -->.*?<!-- /SEO-JS:compare -->|<!-- SEO-JS:guide -->.*?<!-- /SEO-JS:guide -->', '', t, flags=re.S)
m = re.search(r'<div class="grid" id="cards"></div>\s*</div></section>', t)
assert m
t = t[:m.end()] + '\n' + COMPARE + '\n' + GUIDE + t[m.end():]
# sección "Where these... based"
t = re.sub(r'(<h2>[^<]*</h2><p[^>]*>)Los \d+ operadores verificados[^<]*(</p>)', r'\g<1>Los %d operadores verificados de esta página se reparten así: %s.\2' % (N, area_txt), t, 1)
t = re.sub(r'(<h3[^>]*>Mejor valorados ahora mismo</h3>\s*<ul[^>]*>).*?(</ul>)', lambda m: m.group(1) + ''.join('<li><a href="/%s">%s</a> — ⭐ %.1f · %s reseñas · %s</li>' % (r['slug'], e(disp(r)), r['rating'], format(r['reviews'], ','), e(r['area'])) for r in top5) + m.group(2), t, 1, flags=re.S)
t = re.sub(r'En conjunto acumulan [\d.,]+ reseñas, con una valoración media de [\d.,]+ sobre 5\.', 'En conjunto acumulan %s reseñas, con una valoración media de %s sobre 5.' % (format(tot_rev, ',').replace(',', '.'), ('%.1f' % avg).replace('.', ',')), t, 1)
# FAQ visible
if '<!-- SEO-JS:faq -->' in t:
    t = re.sub(r'<!-- SEO-JS:faq -->.*?<!-- /SEO-JS:faq -->', faq_html, t, 1, flags=re.S)
elif '<div class="faq"' in t:
    t = re.sub(r'<div class="faq" style="margin-top:20px">.*?</details> </div>', faq_html, t, 1, flags=re.S)
else:
    t = t.replace('</div></section><footer>', '</div></section><section><div class="wrap" style="max-width:760px"> <h2>Preguntas frecuentes sobre jet ski en Miami</h2> ' + faq_html + ' </div></section><footer>', 1)
t = t.replace('Dónde están estos motos acuáticas', 'Dónde están estas motos acuáticas')
# JSON-LD: Product agregado -> ItemList; FAQ regenerado
def ld(m):
    try: j = json.loads(m.group(1))
    except Exception: return m.group(0)
    if j.get('@type') == 'Product' or j.get('@type') == 'ItemList': return '<script type="application/ld+json">%s</script>' % json.dumps(itemlist, ensure_ascii=False)
    if j.get('@type') == 'FAQPage': return '<script type="application/ld+json">%s</script>' % json.dumps(faq_ld, ensure_ascii=False)
    return m.group(0)
t = re.sub(r'<script type="application/ld\+json">(.*?)</script>', ld, t, flags=re.S)
t = re.sub(r'<small>[^<]*(?:[Cc]ancelaci[oó]n gratu?i?t?a?s?|Free cancellation)[^<]*</small>', '<small>Precios en vivo · Confirmación inmediata</small>', t)
t = re.sub(r'Compara (?:los|a los) 2[01] operadores', 'Compara los %d operadores' % N, t)
t = re.sub(r'Compara 2[01] operadores verificados', 'Compara %d operadores verificados' % N, t)
if 'id="seo-js-css"' not in t: t = t.replace('</head>', CSS + '</head>', 1)
io.open(F, 'w', encoding='utf-8').write(t)
print('ok', N, 'operadores | precios', money(lo), '-', money(hi), 'mediana', money(med), '| cambiado:', t != o)
