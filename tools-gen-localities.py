#!/usr/bin/env python3
"""Genera landings de localidad (/{localidad}-activities) desde operators.json (campo zl).
Solo localidades con >= MIN operadores y sin página propia. Idempotente: reescribe las suyas."""
import io, re, json, os, glob, html as H, unicodedata, math, collections, subprocess

ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)
MIN = 15
MAXCARDS = 48
DOM = 'https://miamijetskiboatrentals.com'
PHOTO = 'https://cdn.filestackcontent.com/%s/convert?cache=true&compress=true&quality=85&format=webp&w=600&fit=max'
LINK = 'https://fareharbor.com/embeds/book/%s/items/%s/?asn=fhdn&asn-ref=miamistylerentals&ref=miamistylerentals&bookable-only=yes&full-items=yes&marketplace=yes&flow=no&branding=no'
CAT = {'boat':'Boat Rentals & Charters','jetski':'Jet Ski Rentals','tour':'Tours','fishing':'Fishing Charters','watersports':'Water Sports',
       'snorkel':'Snorkeling','sunset':'Sunset Cruises','yacht':'Yacht Charters','kayak':'Kayak & Paddle','bikerental':'Bike Rentals',
       'walking_tour':'Walking Tours','culinary':'Food & Drink Tours','wildlife':'Wildlife Tours','aerial':'Aerial Tours','ghost':'Ghost Tours',
       'atv':'ATV & Off-Road','zipline':'Zipline','golf':'Golf','golfcart':'Golf Cart Rentals','shuttle':'Transfers','themepark':'Attractions',
       'segway':'Segway Tours','slingshot':'Slingshot Rentals','sailing':'Sailing','parasail':'Parasailing','scuba':'Scuba Diving','exotic':'Exotic Car Rentals'}

def slugify(s):
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode()
    return re.sub(r'[^a-z0-9]+', '-', s.lower().split(',')[0]).strip('-')

def esc(s): return H.escape(str(s if s is not None else ''), quote=True)

def photo_url(p):
    if not p: return ''
    return p if str(p).startswith('http') else PHOTO % p

def fh_link(o):
    l = o.get('link') or ''
    if l.startswith('http'): return l
    if '/' in l:
        a, b = l.split('/', 1); return LINK % (a, b)
    return ''

# --- datos ---
ops = json.load(open('operators.json'))
ops = ops if isinstance(ops, list) else sum([v for v in ops.values() if isinstance(v, list)], [])
ops = [o for o in ops if isinstance(o, dict)]
slugmap = json.loads(re.search(r'=\s*(\{.*\})', io.open('slug-map.js', encoding='utf-8').read(), re.S).group(1))
pages = {os.path.splitext(f)[0] for f in glob.glob('*.html')}
# zona -> página de zona (la que hace fetch de data/{zone}.json y acaba en -activities)
zone_page = {}
for f in glob.glob('*-activities.html'):
    t = io.open(f, encoding='utf-8', errors='replace').read()
    m = re.search(r"fetch\(\s*['\"]\.?/?data/([a-z0-9-]+)\.json", t)
    if m and m.group(1) not in zone_page: zone_page[m.group(1)] = f[:-5]
zone_name = {}
for z, pg in zone_page.items():
    t = io.open(pg + '.html', encoding='utf-8', errors='replace').read()
    h = re.search(r'<h1[^>]*>(.*?)</h1>', t, re.S)
    zone_name[z] = re.sub(r'\s+(Activities|Tours).*$', '', re.sub(r'<[^>]+>', '', h.group(1)).strip()) if h else z

# --- bloques compartidos (de una ficha de referencia) ---
ref = io.open('sea-ray-46-miami.html', encoding='utf-8').read()
GTAG = re.search(r'<script>window\.dataLayer=window\.dataLayer\|\|\[\];function gtag\(\)[\s\S]*?</script>', ref).group(0)
TRACK = re.search(r'<script>function trackBookNow\(n,p,c\)[\s\S]*?</script>', ref).group(0)
MODAL = ref[ref.find('<!-- FH_BOOKING_MODAL_v2 -->'):ref.find('<!-- /FH_BOOKING_MODAL_v2 -->') + len('<!-- /FH_BOOKING_MODAL_v2 -->')]
MODAL_CSS = re.search(r'<style id="fh-modal-style">[\s\S]*?</style>', io.open('boat-rentals-florida.html', encoding='utf-8').read()).group(0)

CSS = """<style>
:root{--bg:#040d1a;--bg2:#081525;--card:#0a1e36;--line:rgba(0,210,255,.15);--teal:#00d2ff;--teal2:#00d4c8;--text:#e6f0fa;--muted:#8baabf;--dark:#040d1a}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--text);font-family:Inter,system-ui,-apple-system,Segoe UI,Roboto,sans-serif;line-height:1.55}
a{color:var(--teal)}nav{display:flex;align-items:center;justify-content:space-between;gap:12px;padding:14px 20px;background:rgba(4,13,26,.95);border-bottom:1px solid var(--line);position:sticky;top:0;z-index:20}
.nav-logo{font-weight:900;font-size:1.05rem;text-decoration:none;color:#fff}.nav-logo span{color:var(--teal)}
.trust-strip{display:flex;flex-wrap:wrap;gap:8px 22px;justify-content:center;padding:10px 16px;background:var(--bg2);font-size:.8rem;color:var(--muted);border-bottom:1px solid var(--line)}.trust-item b{color:#fff}
.bc{padding:14px 20px;font-size:.85rem;color:var(--muted)}.bc a{text-decoration:none}.bc .sep{margin:0 8px;opacity:.5}
main{max-width:1180px;margin:0 auto;padding:0 20px 40px}
.hero{padding:28px 0 18px}.hero h1{font-size:clamp(1.6rem,4vw,2.4rem);margin:0 0 10px;color:#fff;line-height:1.2}.hero p{color:var(--muted);max-width:760px;margin:0 0 14px}
.stats{display:flex;flex-wrap:wrap;gap:10px 22px;font-size:.92rem;color:var(--muted)}.stats strong{color:#fff}
.chips{display:flex;flex-wrap:wrap;gap:8px;margin:18px 0 8px}.chip{background:rgba(0,210,255,.08);border:1px solid var(--line);color:var(--teal);padding:6px 12px;border-radius:50px;font-size:.8rem;text-decoration:none}.chip:hover{background:rgba(0,210,255,.16)}
h2{color:#fff;font-size:1.25rem;margin:34px 0 14px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:16px}
.card{background:var(--card);border:1px solid var(--line);border-radius:14px;overflow:hidden;display:flex;flex-direction:column}
.card .ph{position:relative;height:160px;background:linear-gradient(135deg,#004b7a,#0a1e36)}.card .ph img{width:100%;height:100%;object-fit:cover;display:block}
.card .cat{position:absolute;top:10px;left:10px;background:rgba(4,13,26,.85);color:var(--teal);font-size:.7rem;font-weight:700;padding:4px 9px;border-radius:50px}
.card .body{padding:12px 14px 14px;display:flex;flex-direction:column;gap:6px;flex:1}
.card h3{margin:0;font-size:.98rem;line-height:1.3}.card h3 a{color:#fff;text-decoration:none}
.card .meta{font-size:.8rem;color:var(--muted)}.card .meta b{color:#ffd166}
.card .row{display:flex;align-items:center;justify-content:space-between;margin-top:auto;padding-top:8px}
.card .price{font-weight:800;color:var(--teal);font-size:1.05rem}.card .price small{font-weight:500;color:var(--muted);font-size:.75rem}
.btn-book{background:linear-gradient(135deg,var(--teal),var(--teal2));color:var(--dark);font-weight:800;padding:8px 14px;border-radius:50px;text-decoration:none;font-size:.85rem;white-space:nowrap}
.faq details{background:var(--bg2);border:1px solid var(--line);border-radius:10px;padding:12px 16px;margin-bottom:10px}.faq summary{cursor:pointer;font-weight:700;color:#fff}.faq p,.faq ul{color:var(--muted);margin:10px 0 0}.faq li{margin:4px 0}
.links{display:flex;flex-wrap:wrap;gap:8px}
footer{border-top:1px solid var(--line);padding:22px 20px;text-align:center;color:var(--muted);font-size:.85rem}
@media(max-width:600px){.card .ph{height:140px}main{padding:0 14px 30px}}
</style>"""

def build(loc, items):
    slug = slugify(loc) + '-activities'
    zone = collections.Counter(o.get('zone') for o in items).most_common(1)[0][0]
    zpage = zone_page.get(zone); zname = zone_name.get(zone, zone)
    url = '%s/%s' % (DOM, slug)
    prices = [float(o['price']) for o in items if o.get('price') and float(o['price']) > 0 and not str(o.get('id','')).startswith('to')]
    pmin = int(min(prices)) if prices else None
    rated = [o for o in items if o.get('rating')]
    avg = (sum(float(o['rating']) for o in rated) / len(rated)) if rated else None
    cats = collections.Counter(o.get('cat') for o in items if o.get('cat'))
    def score(o):
        r = float(o.get('rating') or 0); n = float(o.get('reviews') or 0)
        return r * math.log10(n + 1) + (1 if photo_url(o.get('photo')) else 0)
    cards = sorted(items, key=score, reverse=True)[:MAXCARDS]
    top5 = [o for o in cards if float(o.get('rating') or 0) >= 4.5 and float(o.get('reviews') or 0) >= 20][:5]
    n = len(items)
    title = '%s Activities & Water Sports — %d+ Operators (2026)' % (loc, n)
    if len(title) > 65: title = '%s Activities — %d+ Operators (2026)' % (loc, n)
    desc = 'Compare %d verified operators in %s%s — %s. ⭐ Instant booking via FareHarbor, free cancellation on most listings.' % (
        n, loc, (', %s' % zname if zname and zname.lower() not in loc.lower() else ''), ', '.join(CAT.get(c, c) for c, _ in cats.most_common(4)).lower())
    if len(desc) > 160: desc = desc[:157].rsplit(' ', 1)[0] + '…'
    og = next((photo_url(o.get('photo')) for o in cards if photo_url(o.get('photo'))), DOM + '/og-image.png')

    # tarjetas
    ch = []
    for o in cards:
        s = slugmap.get(o['id']); fh = fh_link(o)
        if not s or not fh: continue
        img = photo_url(o.get('photo'))
        price = int(float(o['price'])) if o.get('price') else 0
        rating = o.get('rating'); rev = o.get('reviews')
        cat = CAT.get(o.get('cat'), (o.get('cat') or '').title())
        ch.append('<article class="card"><div class="ph">%s<span class="cat">%s</span></div><div class="body"><h3><a href="/%s">%s</a></h3>'
                  '<div class="meta">%s📍 %s</div><div class="row"><span class="price">%s</span>'
                  '<a class="btn-book" href="%s" target="_blank" rel="noopener nofollow sponsored" data-fh-price="%s" data-fh-name="%s" onclick="event.stopPropagation();trackBookNow(\'%s\',\'%s\',\'%s\')">Book Now →</a></div></div></article>' % (
                  ('<img src="%s" alt="%s" loading="lazy" width="600" height="400" onerror="this.style.display=\'none\'">' % (esc(img), esc(o['name']))) if img else '',
                  esc(cat), s, esc(o['name']),
                  ('<b>★ %s</b> (%s reviews) · ' % (rating, rev)) if rating and rev else '', esc(o.get('addr') or loc),
                  ('From $%d' % price) if price else 'See prices',
                  esc(fh), price or '', esc(o['name']), esc(o['name']).replace("'", "\\'"), price or 0, esc(o.get('cat') or 'tour')))
    # chips de categoría -> landing de zona-categoría si existe
    chips = []
    for c, k in cats.most_common(10):
        cand = [p for p in pages if p.startswith(slugify(zname)) and c in p] if zname else []
        href = '/' + (cand[0] if cand else (zpage or ''))
        chips.append('<a class="chip" href="%s">%s (%d)</a>' % (href, esc(CAT.get(c, c)), k))
    # FAQ
    faq = []
    if len(top5) >= 3:
        li = '; '.join('<a href="%s/%s">%s</a> (%.1f★, %s reviews)' % (DOM, slugmap[o['id']], esc(o['name']), float(o['rating']), o['reviews']) for o in top5 if slugmap.get(o['id']))
        faq.append(('What are the best-rated activities in %s?' % loc, 'Based on customer ratings, the top-rated options right now are: %s.' % li))
    faq.append(('How much do activities in %s cost?' % loc, ('Prices start around $%d. ' % pmin if pmin else '') + 'Every card shows the operator\'s starting price; final pricing and availability are confirmed on the FareHarbor booking page.'))
    faq.append(('How do I book an activity in %s?' % loc, 'Pick an operator, tap Book Now and complete the reservation on FareHarbor — real-time availability, secure checkout and instant confirmation. Most operators offer free cancellation 24–48h before departure; check each listing\'s policy at checkout.'))
    faq_html = ''.join('<details%s><summary>%s</summary><p>%s</p></details>' % (' open' if i == 0 else '', esc(q), a.replace(DOM + '/', '/')) for i, (q, a) in enumerate(faq))
    # JSON-LD
    ld_list = {'@context': 'https://schema.org', '@type': 'ItemList', 'name': '%s activities' % loc, 'numberOfItems': len(ch),
               'itemListElement': [{'@type': 'ListItem', 'position': i + 1, 'name': o['name'], 'url': '%s/%s' % (DOM, slugmap[o['id']])}
                                   for i, o in enumerate([o for o in cards if slugmap.get(o['id']) and fh_link(o)][:len(ch)])]}
    bc = [{'@type': 'ListItem', 'position': 1, 'name': 'Home', 'item': DOM + '/'}]
    if zpage: bc.append({'@type': 'ListItem', 'position': 2, 'name': '%s Activities' % zname, 'item': '%s/%s' % (DOM, zpage)})
    bc.append({'@type': 'ListItem', 'position': len(bc) + 1, 'name': '%s Activities' % loc, 'item': url})
    ld_bc = {'@context': 'https://schema.org', '@type': 'BreadcrumbList', 'itemListElement': bc}
    ld_faq = {'@context': 'https://schema.org', '@type': 'FAQPage', 'mainEntity': [{'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': a}} for q, a in faq]}
    ld = ''.join('<script type="application/ld+json">%s</script>' % json.dumps(x, ensure_ascii=False) for x in (ld_list, ld_bc, ld_faq))

    html = '''<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><meta name="color-scheme" content="dark"><meta name="theme-color" content="#040d1a">
<title>%s</title><meta name="description" content="%s"><meta name="robots" content="index,follow"><link rel="canonical" href="%s">
<link rel="alternate" hreflang="en" href="%s"><link rel="alternate" hreflang="x-default" href="%s">
<meta property="og:type" content="website"><meta property="og:site_name" content="Miami Jetski &amp; Boat Rentals"><meta property="og:title" content="%s"><meta property="og:description" content="%s"><meta property="og:url" content="%s"><meta property="og:image" content="%s"><meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="%s"><meta name="twitter:description" content="%s"><meta name="twitter:image" content="%s">
<link rel="preconnect" href="https://cdn.filestackcontent.com"><link rel="preconnect" href="https://fareharbor.com">
%s%s%s%s
</head><body>
<nav><a href="/" class="nav-logo">💧 Florida<span>WaterSports</span></a><a href="/" aria-label="Home" style="display:inline-flex;align-items:center;gap:5px;background:rgba(0,210,255,.1);border:1px solid rgba(0,210,255,.3);color:#00d2ff;padding:6px 14px;border-radius:50px;font-size:.82rem;font-weight:700;text-decoration:none">🏠 Home</a></nav>
<div class="trust-strip" role="region" aria-label="Trust indicators"><div class="trust-item">🛡️ <b>Verified</b> Operators</div><div class="trust-item">🔒 <b>Secure</b> via FareHarbor</div><div class="trust-item">✓ <b>Free</b> Cancellation*</div><div class="trust-item">⚡ <b>Instant</b> Confirmation</div></div>
<div class="bc"><a href="/">Home</a>%s<span class="sep">›</span><span>%s</span></div>
<main>
<section class="hero"><h1>%s Activities &amp; Water Sports</h1><p>Compare <strong>%d</strong> verified operators in %s%s — %s. Instant booking via FareHarbor.</p>
<div class="stats"><span class="stat"><strong>%d</strong> operators</span>%s%s</div>
<div class="chips">%s</div></section>
<h2>Top operators in %s</h2>
<div class="grid">%s</div>
%s
<h2>Frequently asked questions</h2><div class="faq">%s</div>
</main>
<footer><p>© 2026 <a href="/">FloridaWaterSports</a> · %d+ operators in %s%s</p></footer>
%s%s
</body></html>''' % (
        esc(title), esc(desc), url, url, url, esc(title), esc(desc), url, esc(og), esc(title), esc(desc), esc(og),
        CSS, MODAL_CSS, GTAG, TRACK,
        ('<span class="sep">›</span><a href="/%s">%s</a>' % (zpage, esc(zname))) if zpage else '', esc(loc),
        esc(loc), n, esc(loc), (', %s' % esc(zname)) if zname and zname.lower() not in loc.lower() else '', ', '.join(CAT.get(c, c).lower() for c, _ in cats.most_common(4)),
        n, ('<span class="stat">From <strong>$%d</strong></span>' % pmin) if pmin else '', ('<span class="stat">⭐ <strong>%.1f</strong> avg rating</span>' % avg) if avg else '',
        ''.join(chips), esc(loc), ''.join(ch),
        ('<h2>More in %s</h2><div class="links"><a class="chip" href="/%s">All %s activities →</a></div>' % (esc(zname), zpage, esc(zname))) if zpage else '',
        faq_html, n, esc(loc), (' · <a href="/%s">%s</a>' % (zpage, esc(zname))) if zpage else '',
        ld, MODAL)
    return slug, html, zone

if __name__ == '__main__':
    by = collections.defaultdict(list)
    for o in ops:
        if o.get('zl'): by[o['zl'].strip()].append(o)
    made, skipped = [], []
    for loc, items in sorted(by.items(), key=lambda x: -len(x[1])):
        if len(items) < MIN: continue
        slug = slugify(loc) + '-activities'
        if slug in pages and not io.open(slug + '.html', encoding='utf-8', errors='replace').read().startswith('<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport"'):
            skipped.append((loc, 'ya existe ' + slug)); continue
        slug, html, zone = build(loc, items)
        io.open(slug + '.html', 'w', encoding='utf-8').write(html)
        made.append((loc, slug, len(items), zone))
    json.dump({'made': made, 'skipped': skipped}, open('/tmp/localities.json', 'w'))
    print('generadas:', len(made), '| omitidas (ya existen):', len(skipped))
