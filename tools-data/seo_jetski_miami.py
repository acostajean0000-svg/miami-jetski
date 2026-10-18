#!/usr/bin/env python3
"""SEO de /miami-jet-ski-rentals (EN): título, H1, tabla comparativa con precios reales, guía, FAQ + JSON-LD.
Fuentes: data/miami-jetski.json (operadores y precios FareHarbor), fh_avail/*.csv (nombre de empresa), slug-map.js.
Idempotente: reemplaza los bloques marcados con <!-- SEO-JS:... --> si ya existen."""
import io, re, json, csv, glob, html, os, statistics
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DOM = 'https://miamijetskiboatrentals.com'
F = 'miami-jet-ski-rentals.html'
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
    '<tr><td><a href="/%s">%s</a><div class="cmp-sub">%s</div></td><td>%s</td><td>%s</td><td>%s</td><td><a class="cmp-book" href="%s" data-fh-name="%s" data-fh-price="%s" rel="nofollow sponsored" target="_blank">Book</a></td></tr>' % (
        r['slug'], e(r['company'] or r['o']['name']), e(r['o']['name'] if r['company'] else ''), e(r['area']),
        ('<strong>%s</strong><div class="cmp-sub">%s</div>' % (money(r['price']), e(r['label'][:34]))) if r['price'] else 'See prices',
        ('★ %.1f <span class="cmp-sub">(%s)</span>' % (r['rating'], format(r['reviews'], ','))) if r['reviews'] else '—',
        e(fhlink(r['o'])), e(r['o']['name']), int(r['price'] or 0))
    for r in rows)
COMPARE = '''<!-- SEO-JS:compare --><section id="compare"><div class="wrap" style="max-width:1000px">
<h2>Miami jet ski rental prices compared</h2>
<p class="sec-sub">Starting price per operator for its base jet ski rental, taken from each live FareHarbor booking calendar on %s. Across the %d operators with a published price, rentals start between <strong>%s and %s</strong> (median %s). Taxes, fees and refundable deposits are shown at checkout.</p>
<div style="overflow-x:auto;margin-top:18px"><table class="cmp-table"><thead><tr><th>Operator</th><th>Area</th><th>From</th><th>Rating</th><th></th></tr></thead><tbody>%s</tbody></table></div>
</div></section><!-- /SEO-JS:compare -->''' % (PRICE_DATE, len(priced), money(lo), money(hi), money(med), table_rows)

GUIDE = '''<!-- SEO-JS:guide --><section style="background:var(--bg2)"><div class="wrap" style="max-width:820px">
<h2>Where to ride a jet ski in Miami</h2>
<p class="sec-sub">The %d operators on this page launch from three areas: %s.</p>
<h3>Biscayne Bay and Downtown Miami</h3><p>Most rentals leave from marinas around Bayside Marketplace and the Venetian Causeway. Rides cross Biscayne Bay with views of the downtown skyline, Star Island and the islands along the causeways. The bay is sheltered, which makes it the usual choice for first-time riders.</p>
<h3>Miami Beach, Sunny Isles and Haulover</h3><p>North of South Beach, operators run from the Haulover Inlet area and the Intracoastal near Sunny Isles. Expect sandbar stops and more open water when the wind picks up.</p>
<h3>Key Biscayne</h3><p>Rentals near the Rickenbacker Causeway head out to the waters around Key Biscayne, with calmer coves and views back toward the city.</p>
<h2 style="margin-top:34px">Jet ski rules in Florida</h2>
<ul class="guide-list">
<li><strong>Age:</strong> you must be at least 18 to rent a personal watercraft, and at least 14 to drive one.</li>
<li><strong>Boating education:</strong> anyone born on or after January 1, 1988 needs a Florida Boating Safety Education ID card, or a temporary certificate, to operate a vessel of 10 hp or more. Rental operators can issue the temporary certificate after a short test before your ride.</li>
<li><strong>Life jackets:</strong> everyone on a jet ski must wear a U.S. Coast Guard–approved, non-inflatable life jacket, and the driver must attach the engine cut-off lanyard.</li>
<li><strong>Daylight only:</strong> jet skis may not be operated from half an hour after sunset to half an hour before sunrise.</li>
<li><strong>No-wake and manatee zones:</strong> parts of Biscayne Bay are slow-speed zones; stay inside the riding area your operator shows you.</li>
</ul>
<p class="guide-src">Rules summarized from Florida boating law; check the <a href="https://myfwc.com/boating/" rel="nofollow noopener" target="_blank">Florida Fish and Wildlife Conservation Commission</a> for the official text.</p>
<h2 style="margin-top:34px">Tips before you book</h2>
<ul class="guide-list">
<li>Mornings usually have the calmest water on the bay; afternoons get choppier when the sea breeze builds.</li>
<li>Check whether the price is for one rider or two, and whether it is a free ride or a guided tour.</li>
<li>Most operators take a refundable damage deposit and ask for a photo ID at check-in; arrive 15 minutes early.</li>
</ul>
</div></section><!-- /SEO-JS:guide -->''' % (N, area_txt)

top5 = rows[:5]
faq = [
    ('What are the best-rated jet ski rentals in Miami?',
     'By customer rating, the top options right now are: ' + '; '.join('%s (%.1f★, %s reviews)' % (disp(r), r['rating'], format(r['reviews'], ',')) for r in top5) + '.',
     '<p>By customer rating, the top options right now are:</p><ul>' + ''.join('<li><a href="/%s">%s</a> (%.1f★, %s reviews)</li>' % (r['slug'], e(disp(r)), r['rating'], format(r['reviews'], ',')) for r in top5) + '</ul>'),
    ('How much does a jet ski rental cost in Miami?',
     'Across %d Miami operators with a published price, the base jet ski rental starts between %s and %s (median %s), usually for one hour with one rider. Taxes, fees and a refundable deposit are added at checkout.' % (len(priced), money(lo), money(hi), money(med)), None),
    ('Do I need a license to rent a jet ski in Miami?',
     'You do not need a boating license. Anyone born on or after January 1, 1988 needs a Florida Boating Safety Education ID card or a temporary certificate, which rental operators can issue after a short test before your ride.', None),
    ('What is the minimum age to rent or drive a jet ski in Florida?',
     'You must be 18 to rent a jet ski and at least 14 to drive one. Bring a photo ID; younger guests can usually ride as passengers.', None),
    ('Where do jet skis launch in Miami?',
     'The operators on this page launch from %s, mainly around Bayside Marketplace and the Venetian Causeway on Biscayne Bay, Haulover and Sunny Isles in the north, and Key Biscayne.' % area_txt, None),
    ('Can I ride a jet ski at night in Miami?',
     'No. Florida law does not allow jet skis to be operated from half an hour after sunset to half an hour before sunrise.', None),
    ('Can I cancel my jet ski booking?',
     'Cancellation terms vary by operator. You will see the exact policy before you pay, and you get instant confirmation when you book through FareHarbor.', None),
]
faq_html = '<!-- SEO-JS:faq --><div class="faq" style="margin-top:20px">' + ''.join(
    '<details%s><summary>%s</summary>%s</details>' % (' open' if k < 2 else '', e(q), h if h else '<p>%s</p>' % e(a)) for k, (q, a, h) in enumerate(faq)) + '</div><!-- /SEO-JS:faq -->'
faq_ld = {'@context': 'https://schema.org', '@type': 'FAQPage', 'mainEntity': [{'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': a}} for q, a, h in faq]}
itemlist = {'@context': 'https://schema.org', '@type': 'ItemList', 'name': 'Jet ski rentals in Miami', 'numberOfItems': N,
            'itemListElement': [{'@type': 'ListItem', 'position': k + 1, 'url': '%s/%s' % (DOM, r['slug']), 'name': disp(r)} for k, r in enumerate(rows)]}

CSS = '<style id="seo-js-css">.cmp-table{width:100%;border-collapse:collapse;font-size:.92rem}.cmp-table th{text-align:left;color:var(--muted);font-weight:600;padding:10px 8px;border-bottom:1px solid rgba(0,210,255,.15)}.cmp-table td{padding:12px 8px;border-bottom:1px solid rgba(255,255,255,.06);vertical-align:top}.cmp-table td a{color:#00d2ff;text-decoration:none;font-weight:600}.cmp-sub{color:var(--muted);font-size:.78rem;font-weight:400;margin-top:2px}.cmp-book{display:inline-block;background:#00d2ff;color:#040d1a!important;padding:6px 14px;border-radius:50px;font-size:.8rem}.guide-list{margin:12px 0 0 18px;line-height:1.7}.guide-list li{margin-bottom:6px}.guide-src{color:var(--muted);font-size:.82rem;margin-top:10px}.guide-src a{color:#00d2ff}section h3{margin-top:18px;font-size:1.05rem}</style>'

t = io.open(F, encoding='utf-8').read(); o = t
title = 'Jet Ski Rentals Miami (2026): Compare %d Operators & Prices' % N
desc = 'Jet ski rentals in Miami from %s. Compare %d verified operators in Biscayne Bay, Miami Beach, Haulover & Key Biscayne with live prices and instant booking.' % (money(lo), N)
t = re.sub(r'<title>[^<]*</title>', '<title>%s</title>' % e(title), t, 1)
for k, v in [('name="description"', desc), ('property="og:title"', title), ('name="twitter:title"', title), ('property="og:description"', desc), ('name="twitter:description"', desc)]:
    t = re.sub(r'(<meta %s content=")[^"]*(")' % re.escape(k), lambda m: m.group(1) + e(v) + m.group(2), t, 1)
t = re.sub(r'<h1>.*?</h1>', '<h1>Jet Ski Rentals in <span class="hl">Miami</span></h1>', t, 1, flags=re.S)
t = re.sub(r'(<p class="sub">)[^<]*(</p>)', r'\g<1>Compare %d verified jet ski operators on Biscayne Bay, Miami Beach, Haulover and Key Biscayne — live prices from %s and instant online booking.\2' % (N, money(lo)), t, 1)
# tabla + guía tras las tarjetas
t = re.sub(r'<!-- SEO-JS:compare -->.*?<!-- /SEO-JS:compare -->|<!-- SEO-JS:guide -->.*?<!-- /SEO-JS:guide -->', '', t, flags=re.S)
m = re.search(r'<div class="grid" id="cards"></div>\s*</div></section>', t)
assert m
t = t[:m.end()] + '\n' + COMPARE + '\n' + GUIDE + t[m.end():]
# sección "Where these... based"
t = re.sub(r'(<h2>Where these jet ski rentals are based</h2><p[^>]*>)[^<]*(</p>)', r'\g<1>The %d verified operators on this page break down like this: %s.\2' % (N, area_txt), t, 1)
t = re.sub(r'(<h3[^>]*>Highest rated right now</h3>\s*<ul[^>]*>).*?(</ul>)', lambda m: m.group(1) + ''.join('<li><a href="/%s">%s</a> — ⭐ %.1f · %s reviews · %s</li>' % (r['slug'], e(disp(r)), r['rating'], format(r['reviews'], ','), e(r['area'])) for r in top5) + m.group(2), t, 1, flags=re.S)
t = re.sub(r'Across these listings: [\d,]+ reviews, average rating [\d.]+ out of 5\.', 'Across these listings: %s reviews, average rating %.1f out of 5.' % (format(tot_rev, ','), avg), t, 1)
# FAQ visible
if '<!-- SEO-JS:faq -->' in t:
    t = re.sub(r'<!-- SEO-JS:faq -->.*?<!-- /SEO-JS:faq -->', faq_html, t, 1, flags=re.S)
else:
    t = re.sub(r'<div class="faq" style="margin-top:20px">.*?</details> </div>', faq_html, t, 1, flags=re.S)
# JSON-LD: Product agregado -> ItemList; FAQ regenerado
def ld(m):
    try: j = json.loads(m.group(1))
    except Exception: return m.group(0)
    if j.get('@type') == 'Product' or j.get('@type') == 'ItemList': return '<script type="application/ld+json">%s</script>' % json.dumps(itemlist, ensure_ascii=False)
    if j.get('@type') == 'FAQPage': return '<script type="application/ld+json">%s</script>' % json.dumps(faq_ld, ensure_ascii=False)
    return m.group(0)
t = re.sub(r'<script type="application/ld\+json">(.*?)</script>', ld, t, flags=re.S)
t = t.replace('<small>Free cancellation · Instant confirmation</small>', '<small>Live prices · Instant confirmation</small>')
t = re.sub(r'Compare all 2[01] Miami jet ski operators', 'Compare all %d Miami jet ski operators' % N, t)
if 'id="seo-js-css"' not in t: t = t.replace('</head>', CSS + '</head>', 1)
io.open(F, 'w', encoding='utf-8').write(t)
print('ok', N, 'operadores | precios', money(lo), '-', money(hi), 'mediana', money(med), '| cambiado:', t != o)
