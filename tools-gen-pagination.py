#!/usr/bin/env python3
"""Paginación horneada para zonas con > 60 operadores: /{zona-page}/2 ... /{zona-page}/N
Página 1 = la página de zona existente (recibe la nav de paginación). 50 operadores por página."""
import io, re, json, os, glob, math, html as H, datetime, importlib.util
ROOT = os.path.dirname(os.path.abspath(__file__)); os.chdir(ROOT)
spec = importlib.util.spec_from_file_location('gl', os.path.join(ROOT, 'tools-gen-localities.py')); gl = importlib.util.module_from_spec(spec); spec.loader.exec_module(gl)
PER = 50; DOM = gl.DOM; esc = gl.esc

zone_page = {}
for f in glob.glob('*-activities.html'):
    t = io.open(f, encoding='utf-8', errors='replace').read()
    m = re.search(r"fetch\(\s*['\"]\.?/?data/([a-z0-9-]+)\.json", t)
    if m and m.group(1) not in zone_page: zone_page[m.group(1)] = f[:-5]

def score(o):
    r = float(o.get('rating') or 0); n = float(o.get('reviews') or 0)
    return r * math.log10(n + 1) + (1 if gl.photo_url(o.get('photo')) else 0)

def card(o, zname):
    s = gl.slugmap.get(o['id']); fh = gl.fh_link(o)
    if not s or not fh: return ''
    img = gl.photo_url(o.get('photo')); price = int(float(o['price'])) if o.get('price') else 0
    cat = gl.CAT.get(o.get('cat'), (o.get('cat') or '').title())
    return ('<article class="card"><div class="ph">%s<span class="cat">%s</span></div><div class="body"><h3><a href="/%s">%s</a></h3>'
            '<div class="meta">%s📍 %s</div><div class="row"><span class="price">%s</span>'
            '<a class="btn-book" href="%s" target="_blank" rel="noopener nofollow sponsored" data-fh-price="%s" data-fh-name="%s" onclick="event.stopPropagation();trackBookNow(\'%s\',\'%s\',\'%s\')">Book Now →</a></div></div></article>') % (
            ('<img src="%s" alt="%s" loading="lazy" width="600" height="400" onerror="this.style.display=\'none\'">' % (esc(img), esc(o['name']))) if img else '',
            esc(cat), s, esc(o['name']), ('<b>★ %s</b> (%s reviews) · ' % (o['rating'], o['reviews'])) if o.get('rating') and o.get('reviews') else '',
            esc(o.get('zl') or o.get('addr') or zname), ('From $%d' % price) if price else 'See prices',
            esc(fh), price or '', esc(o['name']), esc(o['name']).replace("'", "\\'"), price or 0, esc(o.get('cat') or 'tour'))

def nav(zpage, page, total):
    parts = []
    for k in range(1, total + 1):
        href = '/%s' % zpage if k == 1 else '/%s/%d' % (zpage, k)
        parts.append('<span class="pg cur" aria-current="page">%d</span>' % k if k == page else '<a class="pg" href="%s">%d</a>' % (href, k))
    prev = ('<a class="pg" rel="prev" href="%s">‹ Prev</a>' % ('/%s' % zpage if page == 2 else '/%s/%d' % (zpage, page - 1))) if page > 1 else ''
    nxt = ('<a class="pg" rel="next" href="/%s/%d">Next ›</a>' % (zpage, page + 1)) if page < total else ''
    return '<nav class="pagination" aria-label="Pagination">%s%s%s</nav>' % (prev, ''.join(parts), nxt)

PAG_CSS = '<style>.pagination{display:flex;flex-wrap:wrap;gap:6px;justify-content:center;margin:26px 0}.pg{display:inline-block;min-width:38px;text-align:center;padding:8px 10px;border-radius:8px;border:1px solid rgba(0,210,255,.15);color:#00d2ff;text-decoration:none;font-size:.9rem}.pg.cur{background:#00d2ff;color:#040d1a;font-weight:800}</style>'

made = []; today = datetime.date.today().isoformat()
for z, zpage in zone_page.items():
    dp = 'data/%s.json' % z
    if not os.path.exists(dp): continue
    ops = [o for o in json.load(open(dp)) if isinstance(o, dict) and gl.slugmap.get(o.get('id')) and gl.fh_link(o)]
    if len(ops) <= 60: continue
    ops.sort(key=score, reverse=True)
    total = math.ceil(len(ops) / PER)
    zt = io.open(zpage + '.html', encoding='utf-8').read()
    zname = gl.zone_name.get(z, z)
    os.makedirs(zpage, exist_ok=True)
    for page in range(2, total + 1):
        chunk = ops[(page - 1) * PER: page * PER]
        url = '%s/%s/%d' % (DOM, zpage, page)
        title = '%s Activities — Page %d of %d (%d+ Operators)' % (zname, page, total, len(ops))
        if len(title) > 65: title = '%s Activities — Page %d of %d' % (zname, page, total)
        desc = 'Page %d of %d: %d more verified operators in %s — boat rentals, tours, jet ski, fishing and water sports. Instant booking via FareHarbor.' % (page, total, len(chunk), zname)
        cards = ''.join(card(o, zname) for o in chunk)
        ld_list = {'@context': 'https://schema.org', '@type': 'ItemList', 'name': '%s activities — page %d' % (zname, page), 'numberOfItems': len(chunk),
                   'itemListElement': [{'@type': 'ListItem', 'position': (page - 1) * PER + i + 1, 'name': o['name'], 'url': '%s/%s' % (DOM, gl.slugmap[o['id']])} for i, o in enumerate(chunk)]}
        ld_bc = {'@context': 'https://schema.org', '@type': 'BreadcrumbList', 'itemListElement': [
            {'@type': 'ListItem', 'position': 1, 'name': 'Home', 'item': DOM + '/'},
            {'@type': 'ListItem', 'position': 2, 'name': '%s Activities' % zname, 'item': '%s/%s' % (DOM, zpage)},
            {'@type': 'ListItem', 'position': 3, 'name': 'Page %d' % page, 'item': url}]}
        ld = ''.join('<script type="application/ld+json">%s</script>' % json.dumps(x, ensure_ascii=False) for x in (ld_list, ld_bc))
        prev = '<link rel="prev" href="%s">' % ('%s/%s' % (DOM, zpage) if page == 2 else '%s/%s/%d' % (DOM, zpage, page - 1))
        nxt = ('<link rel="next" href="%s/%s/%d">' % (DOM, zpage, page + 1)) if page < total else ''
        html = '''<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><meta name="color-scheme" content="dark"><meta name="theme-color" content="#040d1a">
<title>%s</title><meta name="description" content="%s"><meta name="robots" content="index,follow"><link rel="canonical" href="%s">%s%s
<meta property="og:type" content="website"><meta property="og:title" content="%s"><meta property="og:description" content="%s"><meta property="og:url" content="%s"><meta property="og:image" content="%s/og-image.png">
<link rel="preconnect" href="https://cdn.filestackcontent.com"><link rel="preconnect" href="https://fareharbor.com">
%s%s%s%s%s
</head><body>
<nav><a href="/" class="nav-logo">💧 Florida<span>WaterSports</span></a><a href="/" aria-label="Home" style="display:inline-flex;align-items:center;gap:5px;background:rgba(0,210,255,.1);border:1px solid rgba(0,210,255,.3);color:#00d2ff;padding:6px 14px;border-radius:50px;font-size:.82rem;font-weight:700;text-decoration:none">🏠 Home</a></nav>
<div class="bc"><a href="/">Home</a><span class="sep">›</span><a href="/%s">%s Activities</a><span class="sep">›</span><span>Page %d</span></div>
<main>
<section class="hero"><h1>%s Activities — Page %d of %d</h1><p>Operators %d–%d of <strong>%d</strong> verified operators in %s, ranked by rating and reviews. <a href="/%s">Back to all %s activities, map and filters →</a></p></section>
%s
<div class="grid">%s</div>
%s
</main>
<footer><p>© 2026 <a href="/">FloridaWaterSports</a> · <a href="/%s">%s</a> · page %d of %d</p></footer>
%s%s
</body></html>''' % (esc(title), esc(desc), url, prev, nxt, esc(title), esc(desc), url, DOM,
                      gl.CSS, PAG_CSS, gl.MODAL_CSS, gl.GTAG, gl.TRACK,
                      zpage, esc(zname), page, esc(zname), page, total, (page - 1) * PER + 1, min(page * PER, len(ops)), len(ops), esc(zname), zpage, esc(zname),
                      nav(zpage, page, total), cards, nav(zpage, page, total), zpage, esc(zname), page, total, ld, gl.MODAL)
        io.open('%s/%d.html' % (zpage, page), 'w', encoding='utf-8').write(html)
        made.append('%s/%d' % (zpage, page))
    # nav en la página 1 (zona) + rel=next
    if 'class="pagination"' not in zt:
        blk = PAG_CSS + '<section id="more-pages" style="margin:26px 0"><h2>All %d operators in %s</h2><p style="color:#8baabf">Browse the complete list, 50 operators per page, ranked by rating.</p>%s</section>' % (len(ops), esc(zname), nav(zpage, 1, total))
        m = re.search(r'<h2[^>]*>[^<]*(?:Frequently|FAQ|Preguntas)', zt); pos = m.start() if m else zt.find('</main>')
        zt = zt[:pos] + blk + zt[pos:]
        zt = zt.replace('</head>', '<link rel="next" href="%s/%s/2"></head>' % (DOM, zpage), 1)
        io.open(zpage + '.html', 'w', encoding='utf-8').write(zt)
# sitemap
xml = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + ''.join('  <url><loc>%s/%s</loc><lastmod>%s</lastmod></url>\n' % (DOM, u, today) for u in made) + '</urlset>\n'
io.open('sitemaps/pagination.xml', 'w', encoding='utf-8').write(xml)
idx = io.open('sitemap.xml', encoding='utf-8').read()
if 'sitemaps/pagination.xml' not in idx:
    io.open('sitemap.xml', 'w', encoding='utf-8').write(idx.replace('</sitemapindex>', '  <sitemap><loc>%s/sitemaps/pagination.xml</loc><lastmod>%s</lastmod></sitemap>\n</sitemapindex>' % (DOM, today)))
print('páginas de paginación generadas:', len(made))
