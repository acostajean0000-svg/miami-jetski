#!/usr/bin/env python3
import json, os, re

import os as _os
BASE = _os.path.dirname(_os.path.abspath(__file__))

with open(f'{BASE}/operators.json') as f:
    ops_list = json.load(f)
ops_map = {o['id']: o for o in ops_list}

CDN = 'https://cdn.filestackcontent.com/'
THUMB_PFX = CDN + 'rotate=deg:exif/resize=width:500/quality=value:72/auto_image/compress/cache=expiry:max/'

def thumb(photo):
    if not photo:
        return THUMB_PFX + 'fYlRXu6pQ9yVGrTINaKj'
    if photo.startswith('https://www.filepicker.io/api/file/'):
        return THUMB_PFX + photo.split('/api/file/')[1]
    if photo.startswith(CDN + 'rotate=deg:exif'):
        return photo  # already full transform URL
    if photo.startswith(CDN):
        rest = photo[len(CDN):]
        if '/' not in rest:
            return THUMB_PFX + rest
        # Has some path like "convert?cache=..." - try to get handle from URL
        # These are like CDN/{handle}/convert?... → extract handle
        handle = rest.split('/')[0]
        if len(handle) >= 8 and handle.isalnum():
            return THUMB_PFX + handle
        return photo
    # Just a handle
    return THUMB_PFX + photo

def stars_html(rating):
    if rating >= 5.0: return '★★★★★'
    if rating >= 4.8: return '★★★★½'
    if rating >= 4.5: return '★★★★☆'
    if rating >= 4.2: return '★★★½☆'
    return '★★★☆☆'

RANK_EMOJIS = ['🥇','🥈','🥉','#4','#5','#6','#7']
RANK_CLASSES = ['gold','','','','','','']

def make_card(rank, op_id, desc, pros_list):
    o = ops_map[op_id]
    r = rank
    emoji = RANK_EMOJIS[r]
    cls = RANK_CLASSES[r]
    img = thumb(o['photo'])
    price_str = str(o['price']).replace('$','')
    try:
        price_val = float(price_str)
        price_display = f'From ${int(price_val):,}'
    except:
        price_display = f'From ${price_str}'
    reviews = o.get('reviews', 0)
    reviews_str = f'{reviews:,}' if reviews else '500+'
    stars = stars_html(o['rating'])
    addr = o.get('addr', o.get('zl', ''))
    pro_tags = ''.join(f'<span class="op-pro-tag">{p}</span>' for p in pros_list)
    num_class = f'op-rank-num {"gold" if cls=="gold" else ""}'
    return f'''
<div class="op-ranked">
  <div class="{num_class}">{emoji}</div>
  <div class="op-rank-img"><img src="{img}" alt="{o["name"]}" loading="lazy" onerror="this.parentElement.style.background=\'#0a2040\'"></div>
  <div class="op-rank-body">
    <div class="op-rank-name">{o["name"]}</div>
    <div class="op-rank-loc">📍 {addr}</div>
    <div class="op-rank-rating"><span class="op-rank-stars">{stars}</span> <strong style="color:#fff">{o["rating"]}</strong> <span style="color:var(--text-muted)">({reviews_str} reviews)</span></div>
    <div class="op-rank-desc">{desc}</div>
    <div class="op-rank-pros">{pro_tags}</div>
    <div class="op-rank-footer">
      <div class="op-rank-price">{price_display}</div>
      <a href="{o["link"]}" target="_blank" rel="noopener" class="op-rank-btn">Book Now →</a>
    </div>
  </div>
</div>'''

def make_table_row(rank, op_id, price_label, best_for):
    o = ops_map[op_id]
    emoji = RANK_EMOJIS[rank]
    reviews = o.get('reviews', 0)
    reviews_str = f'{reviews:,}' if reviews else '500+'
    return f'<tr><td>{emoji} {o["name"]}</td><td>{o.get("addr","").split(",")[0]}</td><td>{price_label}</td><td>⭐ {o["rating"]} ({reviews_str})</td><td>{best_for}</td></tr>'

CSS = '''<style>
:root{--dark:#040d1a;--dark2:#081525;--teal:#00d4c8;--teal2:#00eedd;--teal-dark:#00a89e;--teal-glow:rgba(0,212,200,.1);--border:rgba(255,255,255,.08);--card-bg:#0a1e35;--text-muted:#6b8fa8;--text-light:#c5d8e8;--gold:#f59e0b;--radius:14px;}
*{margin:0;padding:0;box-sizing:border-box;}
body{background:var(--dark);color:#fff;font-family:'Inter',sans-serif;line-height:1.7;}
a{text-decoration:none;color:inherit;}
.nav{position:fixed;top:0;left:0;right:0;z-index:100;padding:0 20px;background:rgba(8,21,37,.97);backdrop-filter:blur(12px);border-bottom:1px solid var(--border);}
.nav-inner{max-width:1100px;margin:0 auto;display:flex;align-items:center;justify-content:space-between;height:64px;}
.logo{display:flex;align-items:center;gap:10px;font-family:'Montserrat',sans-serif;font-weight:800;font-size:1rem;}
.logo span{color:var(--teal);}
.nav-links{display:flex;align-items:center;gap:22px;}
.nav-links a{color:var(--text-muted);font-size:.85rem;font-weight:600;transition:color .2s;}
.nav-links a:hover{color:#fff;}
.nav-cta{background:linear-gradient(135deg,var(--teal),var(--teal2));color:var(--dark)!important;padding:8px 20px;border-radius:50px;font-family:'Montserrat',sans-serif;font-weight:700!important;}
@media(max-width:600px){.nav-links{display:none;}}
.breadcrumb{padding:80px 20px 0;max-width:1100px;margin:0 auto;display:flex;align-items:center;gap:8px;font-size:.8rem;color:var(--text-muted);}
.breadcrumb a{color:var(--text-muted);}.breadcrumb a:hover{color:var(--teal);}
.article-hero{padding:28px 20px 52px;background:linear-gradient(135deg,#040d1a,#081525);}
.article-hero-inner{max-width:860px;margin:0 auto;}
.art-tag{display:inline-flex;align-items:center;gap:8px;background:var(--teal-glow);border:1px solid var(--teal-dark);color:var(--teal);font-family:'Montserrat',sans-serif;font-size:.7rem;font-weight:700;letter-spacing:2px;text-transform:uppercase;padding:5px 14px;border-radius:50px;margin-bottom:18px;}
.article-hero h1{font-family:'Montserrat',sans-serif;font-size:clamp(1.7rem,4vw,2.6rem);font-weight:900;line-height:1.2;margin-bottom:14px;}
.article-hero h1 .teal{color:var(--teal);}
.art-meta{display:flex;align-items:center;gap:16px;color:var(--text-muted);font-size:.82rem;flex-wrap:wrap;}
.article-body{max-width:860px;margin:0 auto;padding:48px 20px 80px;}
.article-body h2{font-family:'Montserrat',sans-serif;font-size:1.3rem;font-weight:800;margin:44px 0 14px;color:#fff;}
.article-body h2 .teal{color:var(--teal);}
.article-body h3{font-family:'Montserrat',sans-serif;font-size:1.05rem;font-weight:700;margin:28px 0 10px;color:var(--text-light);}
.article-body p{color:var(--text-light);margin-bottom:16px;line-height:1.8;}
.article-body ul{color:var(--text-light);margin:0 0 18px 22px;line-height:1.9;}
.article-body li{margin-bottom:5px;}
.article-body strong{color:#fff;}
.callout{background:var(--teal-glow);border:1px solid var(--teal-dark);border-radius:12px;padding:18px 20px;margin:24px 0;color:var(--text-light);}
.callout strong{color:var(--teal);}
.op-ranked{display:flex;gap:0;background:var(--card-bg);border:1.5px solid var(--border);border-radius:16px;overflow:hidden;margin-bottom:24px;transition:border-color .2s;}
.op-ranked:hover{border-color:var(--teal-dark);}
.op-rank-num{display:flex;align-items:center;justify-content:center;min-width:56px;background:rgba(0,212,200,.06);border-right:1px solid var(--border);font-family:'Montserrat',sans-serif;font-size:1.6rem;font-weight:900;color:var(--teal);flex-shrink:0;}
.op-rank-num.gold{color:var(--gold);background:rgba(245,158,11,.07);}
.op-rank-img{width:140px;flex-shrink:0;overflow:hidden;background:#0a1e35;}
.op-rank-img img{width:100%;height:100%;object-fit:cover;}
.op-rank-body{padding:16px 20px;flex:1;display:flex;flex-direction:column;gap:6px;}
.op-rank-name{font-family:'Montserrat',sans-serif;font-size:1rem;font-weight:800;color:#fff;}
.op-rank-loc{font-size:.78rem;color:var(--text-muted);}
.op-rank-rating{display:flex;align-items:center;gap:8px;font-size:.82rem;}
.op-rank-stars{color:var(--gold);letter-spacing:1px;}
.op-rank-desc{font-size:.82rem;color:var(--text-light);line-height:1.6;}
.op-rank-pros{display:flex;flex-wrap:wrap;gap:6px;margin-top:4px;}
.op-pro-tag{background:rgba(0,212,200,.07);border:1px solid rgba(0,212,200,.18);color:#7de8e2;padding:3px 10px;border-radius:50px;font-size:.7rem;font-weight:600;}
.op-rank-footer{display:flex;align-items:center;justify-content:space-between;margin-top:8px;flex-wrap:wrap;gap:8px;}
.op-rank-price{font-family:'Montserrat',sans-serif;font-weight:800;color:var(--teal);font-size:.92rem;}
.op-rank-btn{background:linear-gradient(135deg,var(--teal),var(--teal2));color:var(--dark);padding:8px 18px;border-radius:50px;font-weight:700;font-size:.8rem;white-space:nowrap;}
@media(max-width:640px){.op-ranked{flex-direction:column;}.op-rank-img{width:100%;height:140px;}.op-rank-num{min-width:100%;height:44px;border-right:none;border-bottom:1px solid var(--border);font-size:1rem;flex-direction:row;gap:8px;}}
.cmp-table{width:100%;border-collapse:collapse;margin:20px 0 32px;font-size:.85rem;}
.cmp-table th{background:rgba(0,212,200,.08);color:var(--teal);font-family:'Montserrat',sans-serif;padding:10px 14px;text-align:left;border-bottom:1px solid rgba(0,212,200,.2);}
.cmp-table td{padding:10px 14px;border-bottom:1px solid var(--border);color:var(--text-light);}
.cmp-table tr:hover td{background:rgba(255,255,255,.02);}
.art-cta{background:linear-gradient(135deg,#081525,#0a2040);border:1px solid rgba(0,212,200,.2);border-radius:18px;padding:32px;text-align:center;margin:40px 0;}
.art-cta h3{font-family:'Montserrat',sans-serif;font-size:1.3rem;font-weight:800;margin-bottom:10px;}
.art-cta p{color:var(--text-muted);margin-bottom:20px;font-size:.92rem;}
.btn-teal{display:inline-block;background:linear-gradient(135deg,var(--teal),var(--teal2));color:var(--dark);padding:14px 32px;border-radius:50px;font-family:'Montserrat',sans-serif;font-weight:800;font-size:.95rem;transition:opacity .2s;}
.btn-teal:hover{opacity:.85;}
footer{background:#030a14;border-top:1px solid var(--border);padding:24px 20px;}
.footer-inner{max-width:1100px;margin:0 auto;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px;}
.footer-copy{color:var(--text-muted);font-size:.78rem;}
.footer-links{display:flex;gap:20px;}
.footer-links a{color:var(--text-muted);font-size:.78rem;transition:color .2s;}
.footer-links a:hover{color:var(--teal);}
.related-links{display:flex;flex-wrap:wrap;gap:10px;margin:16px 0 32px;}
.related-link{background:var(--card-bg);border:1px solid var(--border);border-radius:50px;color:var(--text-light);padding:7px 16px;font-size:.8rem;transition:border-color .2s;}
.related-link:hover{border-color:var(--teal);color:var(--teal);}
</style>'''

NAV = '''<nav class="nav">
  <div class="nav-inner">
    <a href="/" class="logo"><div style="font-size:1.4rem">🌊</div><div>Miami <span>Jetski</span> &amp; Boat Rentals</div></a>
    <div class="nav-links">
      <a href="/">Home</a>
      <a href="/miami-activities">Miami</a>
      <a href="/key-west-activities">Key West</a>
      <a href="/cancun-activities">Cancún</a>
      <a href="/punta-cana-activities">Punta Cana</a>
      <a href="/miami-activities" class="nav-cta">Book Now</a>
    </div>
  </div>
</nav>'''

FOOTER = '''<footer>
  <div class="footer-inner">
    <p class="footer-copy">© 2026 Miami Jetski &amp; Boat Rentals. Referral platform — bookings via FareHarbor.</p>
    <div class="footer-links">
      <a href="/">Home</a>
      <a href="/miami-activities">Miami</a>
      <a href="/key-west-activities">Key West</a>
      <a href="/cancun-activities">Cancún</a>
    </div>
  </div>
</footer>'''

def build_page(p):
    title = p['title']
    meta = p['meta']
    og_url = p['og_url']
    first_op = ops_map[p['cards'][0]['id']]
    og_photo = CDN + 'rotate=deg:exif/resize=width:1200/quality=value:85/auto_image/compress/cache=expiry:max/'
    photo = first_op['photo']
    if photo.startswith('http'):
        if '/rotate=deg:exif' in photo:
            og_photo_full = photo
        else:
            rest = photo[len(CDN):]
            handle = rest.split('/')[0] if '/' in rest else rest
            og_photo_full = og_photo + handle
    else:
        og_photo_full = og_photo + photo

    # JSON-LD
    items_ld = ','.join([
        f'{{"@type":"ListItem","position":{i+1},"name":"{ops_map[c["id"]]["name"]}","url":"{ops_map[c["id"]]["link"]}"}}'
        for i, c in enumerate(p['cards'])
    ])
    faq_ld = ','.join([
        f'{{"@type":"Question","name":"{q}","acceptedAnswer":{{"@type":"Answer","text":"{a}"}}}}'
        for q, a in p['faqs']
    ])
    article_ld = f'{{"@context":"https://schema.org","@type":"Article","headline":"{title}","description":"{meta}","url":"{og_url}","datePublished":"2026-03-01","dateModified":"2026-05-14","author":{{"@type":"Organization","name":"Miami Jetski & Boat Rentals"}}}}'
    list_ld = f'{{"@context":"https://schema.org","@type":"ItemList","name":"{title}","url":"{og_url}","numberOfItems":{len(p["cards"])},"itemListElement":[{items_ld}]}}'
    faq_full_ld = f'{{"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{faq_ld}]}}'

    # Cards HTML
    cards_html = ''
    for i, c in enumerate(p['cards']):
        cards_html += make_card(i, c['id'], c['desc'], c['pros'])

    # Table
    table_rows = ''
    for i, c in enumerate(p['cards']):
        table_rows += make_table_row(i, c['id'], c.get('price_label',''), c.get('best_for',''))
    table_html = f'''<table class="cmp-table"><thead><tr><th>Operator</th><th>Location</th><th>Price</th><th>Rating</th><th>Best For</th></tr></thead><tbody>{table_rows}</tbody></table>'''

    # FAQ HTML
    faq_html = ''
    for q, a in p['faqs']:
        faq_html += f'<h3>{q}</h3><p>{a}</p>'

    # Related links
    related_html = '<div class="related-links">' + ''.join(
        f'<a href="{url}" class="related-link">{label}</a>' for label, url in p['related']
    ) + '</div>'

    bc_label = title.replace('"','&quot;')
    h1 = p['h1']
    tag = p['tag']
    location = p['location']
    intro = p['intro']
    quickpick = p['quickpick']
    cta_text = p['cta_text']
    cta_url = p['cta_url']

    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="color-scheme" content="dark">
  <meta name="viewport" content="width=device-width,initial-scale=1.0">
  <meta name="robots" content="index,follow">
  <link rel="icon" type="image/x-icon" href="/favicon.ico">
  <meta name="theme-color" content="#081525">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700;800;900&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
  <title>{title}</title>
  <meta name="description" content="{meta}">
  <link rel="canonical" href="{og_url}">
  <meta property="og:title" content="{title}">
  <meta property="og:description" content="{meta}">
  <meta property="og:type" content="article">
  <meta property="og:url" content="{og_url}">
  <meta property="og:image" content="{og_photo_full}">
  <meta name="twitter:card" content="summary_large_image">
  <script type="application/ld+json">{article_ld}</script>
  <script type="application/ld+json">{list_ld}</script>
  <script type="application/ld+json">{faq_full_ld}</script>
  <script async src="https://www.googletagmanager.com/gtag/js?id=G-09F6C7YC7B"></script>
  <script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}gtag('js',new Date());gtag('config','G-09F6C7YC7B');</script>
  {CSS}
</head>
<body>
{NAV}
<div class="breadcrumb">
  <a href="/">Home</a><span>›</span>
  <span>{bc_label}</span>
</div>
<header class="article-hero">
  <div class="article-hero-inner">
    <div class="art-tag">{tag}</div>
    <h1>{h1}</h1>
    <div class="art-meta">
      <span>🗓 Updated May 2026</span>
      <span>⏱ 6 min read</span>
      <span>📍 {location}</span>
    </div>
  </div>
</header>
<main class="article-body">
  <p>{intro}</p>
  <div class="callout"><strong>Quick pick:</strong> {quickpick}</div>
  {cards_html}
  <h2>Side-by-Side <span class="teal">Comparison</span></h2>
  {table_html}
  <div class="art-cta">
    <h3>{cta_text} 🌊</h3>
    <p>Browse real-time availability and instant FareHarbor booking.</p>
    <a href="{cta_url}" class="btn-teal">View All Operators →</a>
  </div>
  <h2>Frequently Asked <span class="teal">Questions</span></h2>
  {faq_html}
  <h2>Related <span class="teal">Guides</span></h2>
  {related_html}
</main>
{FOOTER}
</body>
</html>'''
    return html

# ─── PAGE DEFINITIONS ───────────────────────────────────────────────────────

PAGES = [

# 1
{
'filename': 'best-jet-ski-rentals-destin-florida.html',
'title': 'Best Jet Ski Rentals in Destin FL 2026 (Ranked & Reviewed)',
'meta': "The 5 best jet ski and waverunner rentals in Destin, FL — ranked by rating, price, and experience. Book instantly. Top operators from $95.",
'og_url': 'https://miamijetski.com/best-jet-ski-rentals-destin-florida.html',
'tag': '⭐ Top Picks · Destin',
'h1': 'Best <span class="teal">Jet Ski Rentals</span> in Destin 2026',
'location': 'Destin, FL',
'intro': "Destin's emerald-green Gulf waters make it one of the best places in America to ride a jet ski or waverunner. We ranked the top operators by rating, price, and location — whether you want calm Choctawhatchee Bay or wide-open Gulf water.",
'quickpick': "Discount Watersports is the #1 rated waverunner operator in Destin — 4.9 stars and nearly 2,000 reviews at the best price starting at $95. Power Up Watersports in nearby Fort Walton Beach matches the price with 4.8 stars and 976 reviews.",
'cta_text': 'See All Destin Water Activities',
'cta_url': '/miami-activities',
'cards': [
  {'id':'b570','desc':"Destin's top-rated waverunner operator with nearly 2,000 reviews. Multiple rental durations available in calm Destin Harbor and open Gulf water. Great for groups, solo riders, and families. All ages welcome with safety briefing included.",'pros':['Best Rating','Most Reviews','Destin Harbor','All Ages'],'price_label':'$95/hr','best_for':'Best overall value'},
  {'id':'b559','desc':"Fort Walton Beach's premier jet ski operator — same emerald-green Gulf water, slightly less crowded than Destin Harbor. 4.8 stars across 976 reviews. Multiple ski options including solo and tandem. Also offers pontoon rentals if you want to add a boat day.",'pros':['Fort Walton Beach','Tandem Option','Pontoon Add-On','Emerald Water'],'price_label':'$95+','best_for':'Best for Fort Walton'},
  {'id':'ws30','desc':"Full-service watersports hub in Destin offering jet skis, waverunners, kayaks, and paddleboards. Good for groups who want a mix of activities. 4.7 stars. Higher price reflects the breadth of equipment and guided options.",'pros':['Full Service','Multiple Activities','Guided Options','Destin Central'],'price_label':'$225+','best_for':'Groups & families'},
  {'id':'b477','desc':"Well-established Destin operator on the Destin Harbor Boardwalk. Convenient location, easy parking, family-friendly environment. Good pick if you're staying on the boardwalk and want to walk to your rental.",'pros':['Boardwalk Location','Family Friendly','Walk-Up Booking','Convenient'],'price_label':'$150/hr','best_for':'Boardwalk convenience'},
  {'id':'b464','desc':"Budget-friendly watersports option in Fort Walton Beach for beginners and thrill-seekers. Covers jet skis and other watersports activities. 4.5 stars with good reviews for staff friendliness and equipment quality.",'pros':['Budget Friendly','Beginner OK','Multiple Sports','Staff Friendly'],'price_label':'$99+','best_for':'Budget & beginners'},
],
'faqs': [
  ('What is the best jet ski rental in Destin?','Discount Watersports is the top-rated waverunner operator in Destin with 4.9 stars and nearly 2,000 reviews — and the best price at $95/hr. Power Up Watersports in Fort Walton Beach is a great alternative at the same price with 976 reviews.'),
  ('How much does a jet ski rental cost in Destin?','Expect $95–$150/hr for jet ski or waverunner rentals in Destin. Discount Watersports and Power Up Watersports both offer the best value at $95/hr. Full-service shops with guided options run $150–$225+.'),
  ("Do I need experience to rent a jet ski in Destin?","No prior experience is required. All Destin operators provide a safety briefing before you head out. Destin Harbor and Choctawhatchee Bay are calmer than open Gulf water, making them ideal for first-timers."),
  ('When is the best time to rent a jet ski in Destin?','Spring (March–May) and early Fall (September–October) offer calm water, comfortable temperatures, and manageable crowds. Summer is peak season with the warmest water and longest daylight but more boat traffic.'),
],
'related': [
  ('🚤 Best Boat Tours Destin FL', '/best-boat-tours-destin-florida.html'),
  ('🌊 All Florida Water Sports', '/miami-activities'),
  ('🏝️ Best Tiki Boat Tours Florida', '/best-tiki-boat-tours-florida.html'),
  ('🪂 Best Parasailing Key West', '/best-parasailing-key-west.html'),
],
},

# 2
{
'filename': 'best-boat-tours-destin-florida.html',
'title': 'Best Boat Tours in Destin FL 2026 (Ranked by Reviews)',
'meta': "The 5 best boat tours and charters in Destin, FL for 2026. Dolphin cruises, tiki boats, pontoon rentals, and private yachts. Ranked by rating and reviews.",
'og_url': 'https://miamijetski.com/best-boat-tours-destin-florida.html',
'tag': '⭐ Top Picks · Destin',
'h1': 'Best <span class="teal">Boat Tours</span> in Destin 2026',
'location': 'Destin, FL',
'intro': "From pirate cruises and tiki boats to luxury yacht charters and dolphin watching, Destin has one of the best boat tour scenes on the Gulf Coast. We ranked the top operators by total reviews, rating, and value so you know exactly who to book.",
'quickpick': "Destin Pontoon Charters is the #1 boat operator in Destin by reviews — 5.0 stars across 4,200+ bookings. For dolphin watching, Wave Cutter Charters is the best value at just $30/person with a perfect 5.0 rating.",
'cta_text': 'See All Destin Boat Tours',
'cta_url': '/miami-activities',
'cards': [
  {'id':'bt106','desc':"The most-reviewed pontoon charter operator in Destin with 4,200+ reviews at a perfect 5.0 rating. Private and group pontoon boat rentals with captain for Crab Island, Choctawhatchee Bay, and Gulf adventures. Fits up to 12 passengers. Gear and cooler included.",'pros':['5.0 Stars','4,200+ Reviews','Crab Island','Captain Included'],'price_label':'From $299','best_for':'Most popular operator'},
  {'id':'bt123','desc':"Destin's most-loved family boat experience — the Buccaneer Pirate Cruise with 4,133+ reviews at 4.9 stars. Kids absolutely love it. Swashbuckling entertainment, cannon battles, treasure hunts, and dancing on the water. One of Destin's signature experiences.",'pros':['4,100+ Reviews','Family Favorite','Pirate Show','Best for Kids'],'price_label':'From $10','best_for':'Families & kids'},
  {'id':'b519','desc':"Premium private yacht charter experience in Destin with a perfect 5.0 rating across 1,786 reviews. Luxury vessel with captain — sandbar stops, snorkeling, sunset cruises through Destin Harbor and Norriego Point. Fully customizable private experience.",'pros':['Luxury Yacht','5.0 Stars','Private Charter','Sandbar Stops'],'price_label':'From $699','best_for':'Luxury private charter'},
  {'id':'b553','desc':"Best value dolphin cruise in the Destin area — just $30/person on Wave Cutter Charters departing from Pensacola Beach with a perfect 5.0 rating and 3,437 reviews. Guaranteed wildlife sightings or you ride again free. Worth the short drive from Destin.",'pros':['Best Value','5.0 Stars','3,400+ Reviews','Dolphin Guarantee'],'price_label':'From $30','best_for':'Best value dolphin tour'},
  {'id':'b520','desc':"Float on a tiki bar through Destin's emerald waters on a sandbar swim-stop cruise. 4.9 stars with 1,834 reviews. BYOB-friendly, sunset options available, great for groups and bachelorette parties. Unique Destin experience you won't find everywhere.",'pros':['Tiki Bar Float','Sandbar Stop','BYOB Friendly','Sunset Option'],'price_label':'From $75','best_for':'Tiki boat & sandbar'},
],
'faqs': [
  ('What is the best boat tour in Destin?','Destin Pontoon Charters is the most-reviewed operator with 5.0 stars and 4,200+ reviews — great for all ages. For a unique experience, the Buccaneer Pirate Cruise (4.9 stars, 4,100+ reviews) is a Destin institution that families love.'),
  ('Are there dolphin tours in Destin?','Yes — Wave Cutter Charters departing from nearby Pensacola Beach is the best-rated dolphin cruise at 5.0 stars and 3,400+ reviews for just $30/person. Most Destin Bay tours also include dolphin sightings as the area has a healthy resident dolphin population.'),
  ('How much does a boat charter cost in Destin?','Prices range from $30/person for shared dolphin cruises up to $699+ for private yacht charters. Pontoon rentals with captain typically run $299–$495 and are the most popular option for groups of 6–12 people.'),
  ('When should I book a boat tour in Destin?','Book at least 1–2 weeks ahead in summer (June–August). Spring and Fall have more availability. Sunset tours sell out fastest year-round — book those 2+ weeks in advance.'),
],
'related': [
  ('🛵 Best Jet Ski Rentals Destin', '/best-jet-ski-rentals-destin-florida.html'),
  ('🏝️ Best Tiki Boat Tours Florida', '/best-tiki-boat-tours-florida.html'),
  ('🚤 Best Boat Rentals Miami', '/best-boat-rentals-miami.html'),
  ('🎣 Best Fishing Charters Florida Keys', '/best-fishing-charters-florida-keys.html'),
],
},

# 3
{
'filename': 'best-boat-rentals-naples-florida.html',
'title': 'Best Boat Tours & Rentals in Naples FL 2026 (Top 6 Ranked)',
'meta': "The 6 best boat tours and charter rentals in Naples, Florida for 2026. Private charters, shelling tours, tiki boats, and sailing. Rated 4.7–5.0 stars.",
'og_url': 'https://miamijetski.com/best-boat-rentals-naples-florida.html',
'tag': '⭐ Top Picks · Naples',
'h1': 'Best <span class="teal">Boat Tours</span> in Naples, FL 2026',
'location': 'Naples, FL',
'intro': "Naples is one of Florida's most scenic coastal destinations — with access to the Ten Thousand Islands, Keewaydin Island, and the Gulf. We ranked the top boat tours and charters by rating, reviews, and what makes each one worth booking.",
'quickpick': "Banyan Charters and Rising Tide both hold perfect 5.0 stars. Rising Tide is the best value at $109/person with nearly 700 reviews. Banyan Charters is the best for island shelling and dolphin tours with 360 reviews.",
'cta_text': 'See All Naples Water Activities',
'cta_url': '/miami-activities',
'cards': [
  {'id':'b534','desc':"5.0-star private charter operation specializing in island shelling, dolphin watching, and Gulf Coast exploration. Perfect for couples, families, and small groups. 360 reviews of pure praise for the captain's knowledge and the quality of the shelling destinations reached.",'pros':['5.0 Stars','Island Shelling','Dolphin Watching','Private Charter'],'price_label':'From $395','best_for':'Shelling & dolphins'},
  {'id':'b540','desc':"Naples' best-value guided boat tour at just $109/person — Rising Tide offers scenic cruises through Naples Bay and surrounding waterways. 5.0 stars with 697 reviews. Perfect intro to Naples waterways for first-time visitors. Dolphins, birds, and waterfront mansions.",'pros':['Best Value','5.0 Stars','697 Reviews','Naples Bay'],'price_label':'From $109','best_for':'Best value guided tour'},
  {'id':'b548','desc':"Premium private yacht charter through Naples waterways, Gordon Pass, and the Gulf. 5.0 stars with 328 reviews. Luxury vessel with an experienced captain — customize your route for snorkeling, fishing, or pure sightseeing. Perfect for special occasions.",'pros':['Luxury Charter','5.0 Stars','Customizable','Gulf Access'],'price_label':'From $750','best_for':'Luxury private charter'},
  {'id':'b544','desc':"Epic adventure to the Ten Thousand Islands — one of Florida's most pristine wilderness areas accessible by boat. 4.9 stars with 901 reviews. Full-day experience to remote islands, wildlife encounters, and pristine sandbars inaccessible by car.",'pros':['Ten Thousand Islands','901 Reviews','Remote Sandbars','Wildlife'],'price_label':'From $650','best_for':'Ten Thousand Islands'},
  {'id':'b521','desc':"The fun choice — tiki boat cruises through Naples Bay with BYOB, dolphin spotting, and a floating bar. 4.9 stars with 204 reviews. 90-minute shared cruises departing daily. Great for bachelorette parties, couples, and groups who want to keep things casual and fun.",'pros':['Tiki Bar','BYOB Friendly','Dolphin Spotting','Daily Departures'],'price_label':'From $59','best_for':'Tiki boat fun'},
  {'id':'b434','desc':"Sailing in Naples — Island Sailing Naples offers catamaran and sailing yacht tours through Naples Bay and the Gulf. 4.7 stars with 101 reviews. Unique alternative to motorboat charters, especially popular for sunset sails. BYO food and drinks welcome.",'pros':['Sailing Option','Sunset Sails','Catamaran','Gulf Access'],'price_label':'From $299','best_for':'Sailing & sunsets'},
],
'faqs': [
  ('What is the best boat tour in Naples FL?','Banyan Charters and Rising Tide both have 5.0-star ratings. Rising Tide at $109/person is the best value for first-timers. Banyan Charters specializes in island shelling and is perfect for a private half-day adventure.'),
  ('How much does a boat charter cost in Naples?','Naples boat tours range from $59/person for a tiki boat cruise up to $750+ for a private yacht charter. The most popular option is a private captain charter for groups at $395–$650 for a half-day.'),
  ('What are the best things to do on a boat in Naples?','Top boat activities in Naples include shelling on remote islands (Keewaydin, Tiger Tail), dolphin watching in Naples Bay, exploring the Ten Thousand Islands wilderness, and sunset cruises through Gordon Pass to the Gulf.'),
  ('Is there good snorkeling near Naples?','Snorkeling near Naples is limited compared to the Florida Keys — the Gulf water can have lower visibility due to sediment. However, private charters can reach calmer areas near the Ten Thousand Islands with better underwater life.'),
],
'related': [
  ('🐚 Best Boat Tours Marco Island', '/best-boat-tours-marco-island-florida.html'),
  ('🌺 Best Tiki Boat Tours Florida', '/best-tiki-boat-tours-florida.html'),
  ('🐬 Best Manatee Tours Crystal River', '/best-manatee-tours-crystal-river-florida.html'),
  ('⛵ Best Boat Rentals Miami', '/best-boat-rentals-miami.html'),
],
},

# 4
{
'filename': 'best-manatee-tours-crystal-river-florida.html',
'title': 'Best Manatee Tours in Crystal River FL 2026 (Ranked)',
'meta': "The 6 best manatee tours and swim-with-manatee experiences in Crystal River, FL. Ranked by rating and reviews. Book a guided snorkel tour with the manatees from $30.",
'og_url': 'https://miamijetski.com/best-manatee-tours-crystal-river-florida.html',
'tag': '⭐ Top Picks · Crystal River',
'h1': 'Best <span class="teal">Manatee Tours</span> in Crystal River 2026',
'location': 'Crystal River, FL',
'intro': "Crystal River is the only place in the US where you can legally swim with wild manatees year-round. The spring-fed Kings Bay stays a constant 72°F, making it a manatee refuge in winter and a world-class snorkel destination all year. We ranked the top tour operators.",
'quickpick': "Gulf Coast Expeditions and Kacey's Custom Adventures both have perfect 5.0-star ratings. Explorida Manatee Cruise is the best value at $35 with 1,091 reviews. Book early — morning slots sell out weeks ahead in winter (November–March).",
'cta_text': 'See All Crystal River Tours',
'cta_url': '/miami-activities',
'cards': [
  {'id':'b565','desc':"Perfect 5.0-star guided manatee encounter through Crystal River's spring-fed waterways. Small-group tours led by certified naturalists with snorkel equipment provided. 388 reviews of consistent excellence. Best for families, photographers, and anyone wanting deep wildlife knowledge.",'pros':['5.0 Stars','Naturalist Guide','Snorkel Gear','Small Groups'],'price_label':'From $69','best_for':'Best guided experience'},
  {'id':'b516','desc':"Kacey's Custom Adventures — 5.0 stars across 628 reviews for personalized manatee snorkel and kayak adventures. Custom tour lengths and routes available. Especially popular for private tours where the guide tailors the experience to your group's interests and pace.",'pros':['5.0 Stars','628 Reviews','Custom Routes','Private Tours'],'price_label':'From $75','best_for':'Custom private tours'},
  {'id':'b526','desc':"Best-value manatee cruise in Crystal River — Explorida has 1,091 reviews at 4.9 stars for just $35. Guided boat tours through Kings Bay spring runs with in-water manatee snorkel time. One of the most-reviewed eco-tour operators on the Gulf Coast.",'pros':['Best Value','1,091 Reviews','4.9 Stars','Kings Bay'],'price_label':'From $35','best_for':'Best value'},
  {'id':'b543','desc':"Family Adventure Charters specializes in making Crystal River's manatee experience accessible for all ages — 4.8 stars with 734 reviews. Private charters available with the same captain every time. Perfect for families with young children who want a personal guide.",'pros':['Family Focused','734 Reviews','Private Option','All Ages OK'],'price_label':'From $40','best_for':'Family-friendly'},
  {'id':'b566','desc':"Eco-friendly kayak rental and guided kayak tour operation in nearby Homosassa — perfect for seeing manatees from the water's surface without a motor. 4.8 stars with 257 reviews. Calm spring-run paddling through Crystal River's most beautiful waterways.",'pros':['Kayak Tours','Eco-Friendly','Quiet Experience','Homosassa Springs'],'price_label':'From $30','best_for':'Kayak & paddle'},
  {'id':'b574','desc':"Add an airboat dimension to your Crystal River visit — Blown Away Airboat Tours offers thrilling 1-hour rides through the Crystal River wetlands with manatee and wildlife spotting. 4.9 stars with 138 reviews. A great complement to your manatee snorkel tour.",'pros':['Airboat Adventure','4.9 Stars','Wildlife Spotting','Thrill Factor'],'price_label':'From $51','best_for':'Airboat adventure'},
],
'faqs': [
  ('Is it legal to swim with manatees in Crystal River?','Yes — Crystal River is the only place in the US where passive interaction with wild manatees is federally permitted under the Marine Mammal Protection Act. Touching manatees is prohibited; tours teach guests how to interact passively and respectfully.'),
  ('When is the best time for manatee tours in Crystal River?','November through March is peak season when hundreds of manatees gather in Kings Bay to warm in the 72°F spring water. You can see manatees year-round, but winter offers the highest concentration and most reliable sightings.'),
  ('How much does a manatee tour cost in Crystal River?','Shared group manatee snorkel tours run $35–$75/person. Private charter tours run $250–$500+ for the boat. Book morning departure slots early — they sell out weeks ahead in peak winter season.'),
  ('Do I need to know how to swim to do a manatee tour?','Most tours accommodate non-swimmers with life jackets and shallow-water encounters. Ask your operator about water depth — Kings Bay spring runs are typically 5–12 feet deep. Beginners are very welcome.'),
],
'related': [
  ('🌿 Best Airboat Tours Florida', '/best-airboat-tours-florida.html'),
  ('🚣 Best Kayak Tours Sarasota', '/best-kayak-tours-sarasota-florida.html'),
  ('🐬 Best Dolphin Tours Florida', '/best-dolphin-boat-tours-florida.html'),
  ('⛵ Best Boat Tours Naples', '/best-boat-rentals-naples-florida.html'),
],
},

# 5
{
'filename': 'best-tiki-boat-tours-florida.html',
'title': 'Best Tiki Boat Tours in Florida 2026 (Top 6 Statewide)',
'meta': "The best tiki boat tours in Florida for 2026 — ranked from Key West to Fort Lauderdale to Destin. BYOB floating bar experiences from $59. Rated 4.9–5.0 stars.",
'og_url': 'https://miamijetski.com/best-tiki-boat-tours-florida.html',
'tag': '⭐ Top Picks · Florida Tiki Boats',
'h1': 'Best <span class="teal">Tiki Boat Tours</span> in Florida 2026',
'location': 'Statewide, FL',
'intro': "Tiki boats are one of Florida's most unique water experiences — a floating tiki bar you cruise on through calm coastal waterways. BYOB, dolphins, sunset views, and good vibes. We ranked the best tiki boat operators statewide by rating and reviews.",
'quickpick': "Cruisin' Tikis West Palm Beach leads with 5.0 stars and 848 reviews at just $80/person — the best value tiki experience in Florida. Key West Tiki Boat #1 and Freaky Tiki Fort Lauderdale both have 5.0 stars for a more premium private-charter vibe.",
'cta_text': 'See All Florida Tiki Boat Tours',
'cta_url': '/miami-activities',
'cards': [
  {'id':'b539','desc':"Florida's best-value tiki boat at $80/person — 5.0 stars with 848 reviews. Cruisin' Tikis West Palm Beach runs 2-hour BYOB cruises through the Intracoastal Waterway past waterfront mansions, superyachts, and the famous Mar-a-Lago waterfront. Consistently the best experience per dollar.",'pros':['Best Value','5.0 Stars','848 Reviews','Intracoastal Views'],'price_label':'From $80/person','best_for':'Best value tiki'},
  {'id':'b572','desc':"Key West's top-rated tiki boat rental — fully private charter for your group of up to 6 aboard the floating tiki bar. 5.0 stars with 576 reviews. 2-hour private cruise through Key West Harbor, Christmas Tree Island, and the famous Duval Street Waterfront. BYOB, Bluetooth speaker, cooler included.",'pros':['Private Charter','5.0 Stars','Key West Harbor','BYOB + Cooler'],'price_label':'From $550','best_for':'Key West private tiki'},
  {'id':'b522','desc':"Freaky Tiki Boat Charters on Fort Lauderdale's Intracoastal Waterway — perfect 5.0 stars with 300 reviews. Private 2-hour charters past Fort Lauderdale's famous Millionaire's Row mega-yacht docks. Fully private group experience with BYOB included.",'pros':['5.0 Stars','Millionaires Row','Private Boat','Ft Lauderdale'],'price_label':'From $650','best_for':'Fort Lauderdale luxury'},
  {'id':'b520','desc':"Destin's signature tiki boat experience — a sandbar swim-stop cruise on Choctawhatchee Bay's emerald-green water. 4.9 stars with 1,834 reviews. BYOB-friendly with an anchor stop at a scenic sandbar for swimming. Destin's most unique group outing and one of the Panhandle's most-reviewed tours.",'pros':['Sandbar Stop','1,834 Reviews','Emerald Water','BYOB Friendly'],'price_label':'From $75/person','best_for':'Destin sandbar cruise'},
  {'id':'bt83','desc':"Southwest Florida's beloved tiki cruise — Punta Gorda Tiki runs 90-minute BYOB sunset cruises through Charlotte Harbor with dolphin sightings, mangrove tunnels, and dramatic Gulf sunsets. 4.9 stars with 334 reviews. Great price and a more laid-back, local crowd than busy tourist areas.",'pros':['Charlotte Harbor','4.9 Stars','Dolphin Sightings','Local Vibe'],'price_label':'From $75/person','best_for':'Southwest FL tiki'},
  {'id':'b521','desc':"Naples Bay tiki cruises with dolphin spotting and classic BYOB fun. 4.9 stars with 204 reviews. 90-minute shared departures daily through Naples Bay's calm waters. Great option in Southwest Florida with easy access from downtown Naples and Marco Island.",'pros':['Naples Bay','Daily Departures','Dolphin Spotting','BYOB Fun'],'price_label':'From $59/person','best_for':'Naples area tiki'},
],
'faqs': [
  ('What is a tiki boat tour?','A tiki boat is a floating tiki bar — a pontoon boat decorated as a tiki bar with a thatched roof, bar-top seating, and a Bluetooth sound system. Most are BYOB (bring your own food and drinks). You cruise calm coastal waterways while relaxing on the floating bar.'),
  ('Are tiki boat tours BYOB?','Yes — most Florida tiki boats are BYOB (Bring Your Own Beverage). Bring your own cooler, drinks, and snacks. Some operators provide ice or a built-in cooler. Check each operator\'s policy before booking.'),
  ('How many people fit on a tiki boat?','Most Florida tiki boats fit 6–10 passengers plus the captain. Some larger pontoon tiki boats hold up to 16 passengers. Private charters are the most common format — you get the whole boat for your group.'),
  ('Are tiki boats good for bachelorette parties?','Absolutely — tiki boats are one of the most popular bachelorette party activities in Florida. The BYOB floating bar format, coastal views, and group-exclusive private boat make it a perfect party experience.'),
],
'related': [
  ('🌊 Best Sandbar Tours Florida Keys', '/best-sandbar-tours-keys.html'),
  ('⛵ Best Boat Rentals Miami', '/best-boat-rentals-miami.html'),
  ('🎣 Best Fishing Charters Key West', '/best-fishing-charters-key-west.html'),
  ('🏄 Best Boat Rentals Fort Lauderdale', '/best-boat-rentals-fort-lauderdale.html'),
],
},

# 6
{
'filename': 'best-airboat-tours-florida.html',
'title': 'Best Airboat Tours in Florida 2026 (Top 5 Ranked)',
'meta': "The 5 best airboat tours in Florida for 2026 — gators, wildlife, and swamp adventures from Crystal River to Central Florida and the Everglades. Ranked by reviews.",
'og_url': 'https://miamijetski.com/best-airboat-tours-florida.html',
'tag': '⭐ Top Picks · Florida Airboats',
'h1': 'Best <span class="teal">Airboat Tours</span> in Florida 2026',
'location': 'Florida, Statewide',
'intro': "Florida airboat tours are a bucket-list experience — skimming across freshwater marshes at 30+ mph, spotting alligators, herons, and other wildlife up close. We ranked the best airboat operators statewide from Crystal River to the Everglades edge, by rating and reviews.",
'quickpick': "Tom and Jerry's Airboat Rides at Lake Panasoffkee is the most-reviewed airboat operator in Florida at 4.8 stars with 3,145 reviews and just $35/person. Blown Away Airboat Tours in Crystal River is the best-rated at 4.9 stars.",
'cta_text': 'See All Florida Activities',
'cta_url': '/miami-activities',
'cards': [
  {'id':'b528','desc':"Florida's most-reviewed airboat tour company — 3,145 reviews at 4.8 stars for just $35. Wild gators, sandhill cranes, and native wildlife through the pristine Lake Panasoffkee wetland preserve. 1-hour tours departing multiple times daily. Located in Central Florida between Tampa and Orlando.",'pros':['Most Reviews','Best Price','Lake Panasoffkee','1-Hour Tours'],'price_label':'From $35','best_for':'Most popular, best value'},
  {'id':'b574','desc':"The best-rated airboat tour in Florida — Blown Away Airboat Tours in Crystal River holds 4.9 stars with 138 reviews. Spectacular wetland and river airboat rides through Crystal River's wild waterways with manatee habitat, gators, and otters. Great pair with a manatee snorkel tour.",'pros':['Best Rating','Crystal River','Manatee Habitat','Wildlife Rich'],'price_label':'From $51','best_for':'Crystal River adventure'},
  {'id':'to38','desc':"Raised by Water Airboat Adventures in Sanford (near Orlando) — 4.7 stars with 157 reviews. Custom airboat excursions through St. Johns River and Central Florida waterways. Private charter option available for up to 6 passengers — popular with Orlando tourists looking for a Florida nature experience.",'pros':['Near Orlando','Private Charter','St. Johns River','Custom Duration'],'price_label':'From $750 private','best_for':'Orlando area private tour'},
  {'id':'to108','desc':"Gator Night Airboat Tour at Sawgrass Recreation Park near Fort Lauderdale — 4.4 stars with 3,222 reviews. One of Florida's most-visited airboat attractions at the edge of the Everglades. Night tours available for unique gator-eye glowing action. Family-friendly with educational ranger-led commentary.",'pros':['3,222 Reviews','Night Tours','Everglades Edge','Family Friendly'],'price_label':'See operator','best_for':'Fort Lauderdale / Everglades'},
  {'id':'br12','desc':"SoFlo Water Adventures in North Miami combines an e-bike tour with an airboat ride through the Miami Everglades — a unique combo you won't find anywhere else. 4.5 stars with 136 reviews. Perfect for Miami visitors who want the full Florida adventure experience in one outing.",'pros':['E-Bike + Airboat','Miami Access','Unique Combo','Everglades'],'price_label':'From $99','best_for':'Miami visitors'},
],
'faqs': [
  ('What is an airboat tour?','An airboat is a flat-bottomed boat propelled by an aircraft-type propeller and engine mounted at the stern. They can travel over shallow water, marsh, and even low vegetation, making them ideal for exploring Florida\'s wetlands and seeing wildlife up close.'),
  ('Are airboats safe?','Yes — airboat tours are safe when operated by licensed companies. Passengers wear hearing protection (the engines are loud) and life jackets are available. The boats are extremely stable. All operators listed above are licensed commercial operators with safety records.'),
  ('Will I see alligators on an airboat tour?','Almost always — Florida\'s lakes and marshes have one of the highest alligator densities in the world. Tom and Jerry\'s (Lake Panasoffkee) and Gator Night Airboat Tours (Everglades edge) have especially high gator encounter rates.'),
  ('Do you need to book airboat tours in advance?','Booking 3–7 days ahead is recommended, especially for weekend slots and the most popular morning departures. Tom and Jerry\'s often has same-day availability on weekdays.'),
],
'related': [
  ('🐊 Best Manatee Tours Crystal River', '/best-manatee-tours-crystal-river-florida.html'),
  ('🌊 Best Water Sports Florida', '/miami-activities'),
  ('🚤 Best Boat Tours Destin', '/best-boat-tours-destin-florida.html'),
  ('🏝️ Best Kayak Tours Sarasota', '/best-kayak-tours-sarasota-florida.html'),
],
},

# 7
{
'filename': 'best-boat-rentals-siesta-key-florida.html',
'title': 'Best Boat Rentals on Siesta Key FL 2026 (Top 5 Ranked)',
'meta': "The 5 best boat rentals and water sports on Siesta Key and Sarasota, FL. Pontoon rentals, jet skis, and kayaks on some of Florida's most beautiful Gulf water. From $109.",
'og_url': 'https://miamijetski.com/best-boat-rentals-siesta-key-florida.html',
'tag': '⭐ Top Picks · Siesta Key',
'h1': 'Best <span class="teal">Boat Rentals</span> on Siesta Key 2026',
'location': 'Siesta Key / Sarasota, FL',
'intro': "Siesta Key's crystal-clear Gulf water and powdery white quartz sand beaches make it one of Florida's most spectacular places to be on the water. We ranked the top boat rentals and water sports operators by rating and reviews.",
'quickpick': "Siesta Key Watersports is the #1 operator with 8,588 reviews at 4.9 stars — Siesta Key's most-reviewed water sports company. CBS Outfitters leads for pontoon rentals with 4.8 stars across 1,000+ reviews for both their 20ft and 27ft boats.",
'cta_text': 'See All Sarasota Water Activities',
'cta_url': '/miami-activities',
'cards': [
  {'id':'b542','desc':"Siesta Key's most-reviewed watersports company — 8,588 reviews at 4.9 stars. Waverunner and jet ski rentals, guided jet ski tours, and combo packages directly on Siesta Key. Multiple session lengths available. The go-to for any powered water activity on Siesta Key.",'pros':['8,588 Reviews','4.9 Stars','Jet Ski & Waverunner','On Siesta Key'],'price_label':'From $109/hr','best_for':'Siesta Key jet ski'},
  {'id':'b578','desc':"CBS Outfitters' 20-foot pontoon rental — fits up to 8 passengers for a self-guided Gulf Coast adventure. 4.8 stars with 1,021 reviews. Full day and half day options. Explore Siesta Key's sandbar spots, accessible only by boat. Gas, safety equipment, and dock fees included.",'pros':['Self-Guided','1,021 Reviews','Sandbar Access','8 Passengers'],'price_label':'From $349','best_for':'Pontoon for groups'},
  {'id':'b579','desc':"Upgrade to CBS Outfitters' 27-foot pontoon for larger groups — up to 12 passengers. 4.8 stars with 1,049 reviews. More space, better shade coverage, and access to the same pristine Gulf sandbar spots. Perfect for families or groups of 10–12 who want maximum comfort.",'pros':['12 Passengers','1,049 Reviews','More Space','Best for Big Groups'],'price_label':'From $449','best_for':'Large groups'},
  {'id':'b533','desc':"CB's Saltwater Outfitters on Siesta Key — 4.8 stars with 1,074 reviews. One of the most established boat rental operations on the Gulf Coast, offering flats boats, center consoles, and pontoons. Great for fishing and Gulf exploration with an experienced operator.",'pros':['1,074 Reviews','Fishing Boats','Gulf Fishing','Experienced Staff'],'price_label':'From $349','best_for':'Fishing & boating'},
  {'id':'b573','desc':"Sandy Toes Boat Charters in Gulfport — private charter service with a perfect 5.0 rating and 270 reviews. Captain-led experience to Egmont Key, Shell Key Preserve, and Tampa Bay. Perfect for couples and small groups who want a private day on the water with an experienced captain.",'pros':['5.0 Stars','Private Charter','Captain Included','Egmont Key'],'price_label':'From $250','best_for':'Private captain charter'},
],
'faqs': [
  ('What are the best boat rentals on Siesta Key?','CBS Outfitters has the best pontoon rentals with 4.8 stars across 1,000+ reviews — choose between 20ft (8 people) and 27ft (12 people) boats. For jet ski and waverunner rentals, Siesta Key Watersports is the clear leader with 8,500+ reviews at 4.9 stars.'),
  ('Can I rent a pontoon boat on Siesta Key without a license?','Yes — Florida allows unlicensed boat rentals for vessels up to a certain size. CBS Outfitters provides a safety orientation before departure. No prior boating experience is required.'),
  ('Where should I take a pontoon boat on Siesta Key?','Top destinations include the sandbars accessible from Midnight Pass, Turtle Beach, and the Gulf inlets around Siesta Key. Ask CBS Outfitters for a map of the best sandbar spots when you pick up your boat.'),
  ('Is Siesta Key good for jet skiing?','Yes — Siesta Key is excellent for jet skiing with calm intracoastal water for beginners and Gulf access for experienced riders. The water clarity is exceptional. Book with Siesta Key Watersports for the highest-rated experience.'),
],
'related': [
  ('🚣 Best Kayak Tours Sarasota', '/best-kayak-tours-sarasota-florida.html'),
  ('🌊 Best Boat Tours Destin', '/best-boat-tours-destin-florida.html'),
  ('⛵ Best Boat Rentals Miami', '/best-boat-rentals-miami.html'),
  ('🏝️ Best Tiki Boat Tours Florida', '/best-tiki-boat-tours-florida.html'),
],
},

# 8
{
'filename': 'best-kayak-tours-sarasota-florida.html',
'title': 'Best Kayak Tours in Sarasota FL 2026 (Top 5 Ranked)',
'meta': "The 5 best kayak tours and paddleboard rentals in Sarasota and Siesta Key, FL. 5.0-star rated operators with thousands of reviews. From $30/person.",
'og_url': 'https://miamijetski.com/best-kayak-tours-sarasota-florida.html',
'tag': '⭐ Top Picks · Sarasota',
'h1': 'Best <span class="teal">Kayak Tours</span> in Sarasota 2026',
'location': 'Sarasota / Siesta Key, FL',
'intro': "Sarasota's coastal waterways, mangrove tunnels, and pristine Gulf waters make it one of the best kayaking destinations in Florida. Multiple operators have built thousands of 5-star reviews. We ranked the best by rating, reviews, and what makes each experience unique.",
'quickpick': "Siesta Key Kayak & Paradise Adventures is the most-reviewed kayak operator in Sarasota with 4,540 reviews at 5.0 stars — and just $30/person. Sea Life Kayak Adventures has 3,641 reviews, also at 5.0 stars, with a more wildlife-focused guided experience.",
'cta_text': 'See All Sarasota Activities',
'cta_url': '/miami-activities',
'cards': [
  {'id':'b510','desc':"Sarasota's most-reviewed kayak operator — 4,540 reviews at a perfect 5.0. Guided kayak tours and SUP adventures around Siesta Key's mangrove tunnels, sandbars, and clear Gulf waters. Multiple departure times daily. Best price at just $30/person with equipment included.",'pros':['Most Reviews','5.0 Stars','Best Price','Daily Departures'],'price_label':'From $30/person','best_for':'Best value guided kayak'},
  {'id':'b509','desc':"Sea Life Kayak Adventures — 3,641 reviews at 5.0 stars for guided wildlife kayak tours through Sarasota's coastal ecosystem. Dolphin, manatee, and bird encounters are regular. Expert naturalist guides make this the best educational kayak experience in the Sarasota area.",'pros':['5.0 Stars','Wildlife Focus','Naturalist Guide','3,641 Reviews'],'price_label':'From $59/person','best_for':'Wildlife & nature'},
  {'id':'b500','desc':"Kayaking SRQ by Sarasota Kayak Tours — 4,000 reviews at 5.0 stars. Multiple guided tour options through Sarasota Bay, the Intracoastal, and Siesta Key coastal areas. Excellent for first-timers — the guides are patient, knowledgeable, and excellent with families.",'pros':['5.0 Stars','4,000 Reviews','Multiple Routes','Great for Beginners'],'price_label':'From $45/person','best_for':'Beginners & families'},
  {'id':'b532','desc':"Parasail Low Tide Tours in Sarasota also offers kayak tours — 5.0 stars with 305 reviews. Guided morning kayak tours with wildlife spotting before the parasailing crowds arrive. Unique combo operator if you want to kayak in the morning and parasail in the afternoon.",'pros':['5.0 Stars','Morning Tours','Wildlife Spotting','Add Parasailing'],'price_label':'From $45/person','best_for':'Morning kayak + parasail'},
  {'id':'b525','desc':"Low Tide Tours along the Venice and Sarasota coastline — scenic coastal boat cruises and kayak tours with frequent dolphin sightings. 4.9 stars with 649 reviews at just $30. Great alternative if Sarasota spots are booked — Venice is 25 minutes south with excellent water access.",'pros':['Venice Access','649 Reviews','Dolphin Sightings','Best Budget Option'],'price_label':'From $30/person','best_for':'Venice & coastal tours'},
],
'faqs': [
  ('What is the best kayak tour in Sarasota?','Siesta Key Kayak & Paradise Adventures has 4,540 reviews at 5.0 stars — the most-reviewed and best value at $30/person. For a wildlife-focused experience with an expert naturalist guide, Sea Life Kayak Adventures (3,641 reviews, 5.0 stars) is the top pick.'),
  ('Do I need kayaking experience in Sarasota?','No — all Sarasota kayak tour operators welcome beginners. The tours run in calm protected waters (mangrove tunnels, bays, and intracoastal waterway) where no paddling experience is needed. Guides provide full instruction before departure.'),
  ('What wildlife will I see kayaking in Sarasota?','Common wildlife includes bottlenose dolphins, West Indian manatees (especially in winter), roseate spoonbills, ospreys, bald eagles, and countless fish and sea birds. Morning tours have the highest wildlife activity.'),
  ('When is the best time to kayak in Sarasota?','Year-round, but early morning departures (7–9 AM) offer calm water and the best wildlife activity. Winter (November–March) brings manatees to warm inland waters. Summer is warmest but afternoon thunderstorms are common — book morning tours.'),
],
'related': [
  ('🚤 Best Boat Rentals Siesta Key', '/best-boat-rentals-siesta-key-florida.html'),
  ('🐬 Best Dolphin Tours Florida', '/best-dolphin-boat-tours-florida.html'),
  ('🐊 Best Airboat Tours Florida', '/best-airboat-tours-florida.html'),
  ('🌊 Best Water Sports Clearwater', '/best-water-sports-clearwater-florida.html'),
],
},

# 9
{
'filename': 'best-water-sports-clearwater-florida.html',
'title': 'Best Water Sports in Clearwater Beach FL 2026 (Ranked)',
'meta': "The 6 best water sports and boat tours in Clearwater Beach, FL — jet ski, kayak, parasail, and dolphin tours. 4.8–5.0 star operators. Book now on FareHarbor.",
'og_url': 'https://miamijetski.com/best-water-sports-clearwater-florida.html',
'tag': '⭐ Top Picks · Clearwater Beach',
'h1': 'Best <span class="teal">Water Sports</span> in Clearwater Beach 2026',
'location': 'Clearwater Beach, FL',
'intro': "Clearwater Beach has been ranked America's best beach multiple times — and the water sports scene matches the scenery. From jet skiing and kayaking to dolphin cruises and shelling tours, we ranked the top operators by reviews and rating.",
'quickpick': "Get Up and Go Kayaking at Shell Key Preserve is the most-reviewed operator in the area with an estimated 6,000+ reviews at 5.0 stars. Dolphin Island Jet Ski Adventure is top-rated for jet skiing with 1,248 reviews at 5.0 stars.",
'cta_text': 'See All Clearwater Activities',
'cta_url': '/miami-activities',
'cards': [
  {'id':'b498','desc':"One of Florida's most beloved outdoor experiences — a guided kayak and beach yoga session at the pristine Shell Key Preserve in Tierra Verde. Estimated 6,000+ reviews at 5.0 stars. Paddle through Boca Ciega Bay's sea grass beds and marine wildlife to a protected shell island. Unique and memorable.",'pros':['5.0 Stars','Most Reviews','Shell Key Preserve','Kayak + Yoga'],'price_label':'From $74/person','best_for':'Most popular experience'},
  {'id':'js80','desc':"Dolphin Island Jet Ski Adventure at Clearwater Beach — 5.0 stars with 1,248 reviews. Guided jet ski tour along Clearwater's famous Gulf Coast with dolphin spotting and scenic views. Best-rated powered water sports experience in the Clearwater area.",'pros':['5.0 Stars','1,248 Reviews','Guided Tour','Dolphin Spotting'],'price_label':'From $149/person','best_for':'Best jet ski tour'},
  {'id':'b508','desc':"Coastal Kayak Charters from Tierra Verde — 5.0 stars with 1,116 reviews. Guided kayak tours through Boca Ciega Bay and Egmont Key State Park — a remote uninhabited island with manatees, gopher tortoises, and historic Fort Dade. One of the most unique paddling destinations in Tampa Bay.",'pros':['5.0 Stars','Egmont Key','1,116 Reviews','Manatees & Wildlife'],'price_label':'From $49/person','best_for':'Egmont Key kayak tour'},
  {'id':'b555','desc':"Charter Finders' popular Dolphin & Shelling Cruise at Madeira Beach — 4.9 stars with 427 reviews. Shared boat tour to dolphin-watching hotspots and shell-rich sandbars on the Gulf Coast. Best-reviewed public shelling cruise departing from John's Pass. Great value for families.",'pros':['4.9 Stars','427 Reviews','Shelling & Dolphins','Family Friendly'],'price_label':'From $60/person','best_for':'Dolphin & shelling cruise'},
  {'id':'b535','desc':"John's Pass Waverunner in Madeira Beach — 4.8 stars with 229 reviews. Waverunner rentals directly from John's Pass Village & Boardwalk, one of the Gulf Coast's most popular tourist destinations. Access to both the Gulf and Boca Ciega Bay intracoastal waters.",'pros':['Johns Pass Location','Intracoastal Access','Gulf Access','Walk-Up Friendly'],'price_label':'From $69/hr','best_for':'Waverunner rental'},
  {'id':'b511','desc':"Island Kayak Tours at Shell Key Preserve — 5.0 stars with 328 reviews. Guided kayak tours to the barrier island wilderness near St. Pete Beach. Excellent for wildlife — roseate spoonbills, sea turtles, and dolphins are commonly spotted. Morning tours sell out fastest.",'pros':['5.0 Stars','Shell Key Island','Sea Turtles','328 Reviews'],'price_label':'From $49/person','best_for':'Shell Key island kayak'},
],
'faqs': [
  ('What are the best water sports in Clearwater Beach?','The most popular are guided kayak tours to Shell Key Preserve (5.0 stars, 6,000+ reviews), jet ski tours with Dolphin Island Jet Ski Adventure (5.0 stars, 1,248 reviews), and shelling/dolphin cruises from John\'s Pass (4.9 stars). Parasailing from Clearwater Beach Pier is also very popular.'),
  ('Is Clearwater Beach good for snorkeling?','Clearwater Beach\'s Gulf water can be murky close to shore, but offshore areas near Three Rooker Bar and Egmont Key have better visibility. Guided kayak and boat tours to Shell Key and Egmont Key offer the best marine life encounters in the area.'),
  ('What is John\'s Pass in Madeira Beach?','John\'s Pass Village & Boardwalk is a historic fishing village between Madeira Beach and Treasure Island with restaurants, shops, and multiple water sports operators. It\'s one of the best places to rent waverunners and hop on dolphin tours on the Gulf Coast.'),
  ('When is the best time to visit Clearwater Beach for water sports?','April–June and September–October offer the best conditions — warm water, lower crowds, and good visibility. Summer is peak season with the warmest water. Winter is quieter with cooler temps but manatees are often spotted in the area.'),
],
'related': [
  ('🚣 Best Kayak Tours Sarasota', '/best-kayak-tours-sarasota-florida.html'),
  ('🤿 Best Boat Rentals Siesta Key', '/best-boat-rentals-siesta-key-florida.html'),
  ('🐬 Best Dolphin Tours Florida', '/best-dolphin-boat-tours-florida.html'),
  ('🚤 Best Boat Rentals Fort Lauderdale', '/best-boat-rentals-fort-lauderdale.html'),
],
},

# 10
{
'filename': 'best-dolphin-boat-tours-florida.html',
'title': 'Best Dolphin Boat Tours in Florida 2026 (Top 6 Ranked)',
'meta': "The 6 best dolphin watching boat tours in Florida for 2026 — ranked by rating and reviews. From Pensacola Beach to Marco Island. Shared and private tours from $30.",
'og_url': 'https://miamijetski.com/best-dolphin-boat-tours-florida.html',
'tag': '⭐ Top Picks · Florida Dolphin Tours',
'h1': 'Best <span class="teal">Dolphin Boat Tours</span> in Florida 2026',
'location': 'Florida, Statewide',
'intro': "Florida has one of the largest resident bottlenose dolphin populations in the world, making dolphin watching one of the most reliable and affordable wildlife experiences on any coast. We ranked the best dolphin boat tours statewide by rating, reviews, and value.",
'quickpick': "Wave Cutter Charters near Pensacola Beach leads with a perfect 5.0 stars and 3,437 reviews at just $30/person — Florida's best dolphin tour value. For Southwest Florida, Banyan Charters on Marco Island delivers a premium dolphin and shelling experience with 5.0 stars.",
'cta_text': 'See All Florida Dolphin Tours',
'cta_url': '/miami-activities',
'cards': [
  {'id':'b553','desc':"Florida's best-value dolphin cruise — 5.0 stars with 3,437 reviews for just $30/person. Wave Cutter Charters departs from Pensacola Beach on a fast and thrilling dolphin-watching adventure through the Pensacola Bay and Sound. Near 100% dolphin sighting rate — guaranteed or you ride again.",'pros':['Best Value','5.0 Stars','3,437 Reviews','Near 100% Sighting Rate'],'price_label':'From $30/person','best_for':'Best value dolphin tour'},
  {'id':'b555','desc':"Charter Finders' Dolphin & Shelling Cruise at Madeira Beach — 4.9 stars with 427 reviews at $60/person. Shared boat tour combining dolphin watching with a stop at a shell-rich Gulf sandbar. One of the most popular nature tours departing from John's Pass Village.",'pros':['Dolphin + Shelling','4.9 Stars','427 Reviews','Johns Pass'],'price_label':'From $60/person','best_for':'Dolphin & shelling combo'},
  {'id':'b584','desc':"Premium dolphin and shelling experience on Marco Island — 5.0 stars with 360 reviews. Banyan Charters takes small private groups to remote Ten Thousand Islands shelling spots while searching for dolphins, manatees, and sea birds in some of Florida's most pristine coastal wilderness.",'pros':['5.0 Stars','Private Groups','Marco Island','Ten Thousand Islands'],'price_label':'From $550 private','best_for':'Marco Island premium'},
  {'id':'b525','desc':"Low Tide Tours along the Venice and Sarasota coast — 4.9 stars with 649 reviews at just $30. Scenic coastal boat tour with frequent dolphin sightings along the Gulf Coast. One of the most affordable and consistently reviewed dolphin tour operators in Southwest Florida.",'pros':['Best Price','649 Reviews','Venice Gulf Coast','Daily Departures'],'price_label':'From $30/person','best_for':'Venice & Sarasota coast'},
  {'id':'b585','desc':"Charter Finders' private dolphin & shelling tour from Madeira Beach — 4.9 stars with 426 reviews. Full private boat for your group to the same dolphin hotspots and shell beaches at a more personal pace. Perfect for proposals, anniversaries, and families who want an exclusive experience.",'pros':['Private Boat','4.9 Stars','Exclusive Experience','Perfect for Special Occasions'],'price_label':'From $354 private','best_for':'Private group charter'},
  {'id':'b586','desc':"Code Blue Fishing and Dolphin Cruise from Fort Walton Beach — perfect 5.0 stars with 146 reviews. Half-day dolphin watching tour through Choctawhatchee Bay and Destin Harbor with optional fishing. Experienced captain with extensive local knowledge of dolphin activity patterns.",'pros':['5.0 Stars','Fort Walton Beach','Fishing Option','Destin Area'],'price_label':'From $350','best_for':'Destin area dolphin tour'},
],
'faqs': [
  ('Where is the best place to see dolphins in Florida?','Dolphins can be spotted all along Florida\'s coastlines, but the Gulf Coast has especially high densities. Top spots include Destin / Fort Walton Beach, Sarasota Bay, Pensacola Bay, and the Ten Thousand Islands near Marco Island. Nearly every coastal bay tour includes dolphin sightings.'),
  ('Are dolphin tours worth it in Florida?','Yes — Florida has one of the largest resident bottlenose dolphin populations in the US and sighting rates on guided tours are very high (typically 90%+). The best operators like Wave Cutter Charters offer re-ride guarantees if you don\'t spot dolphins.'),
  ('What is the best time of year for dolphin watching in Florida?','Year-round, but spring and fall (March–May and September–November) offer the best combination of calm water and active dolphins. Dolphins follow fish migrations and are present in Florida\'s waters every month of the year.'),
  ('Do dolphins come to Florida beaches?','Dolphin pods regularly enter shallow bays, inlets, and even approach beaches while fishing. Guided tours take you to known dolphin feeding and travel areas for the highest probability sightings. Wild dolphins should never be fed or touched.'),
],
'related': [
  ('🐊 Best Airboat Tours Florida', '/best-airboat-tours-florida.html'),
  ('🌺 Best Tiki Boat Tours Florida', '/best-tiki-boat-tours-florida.html'),
  ('🐬 Best Manatee Tours Crystal River', '/best-manatee-tours-crystal-river-florida.html'),
  ('⛵ Best Boat Tours Destin', '/best-boat-tours-destin-florida.html'),
],
},

]

generated = []
for p in PAGES:
    html = build_page(p)
    out = f"{BASE}/{p['filename']}"
    with open(out, 'w') as f:
        f.write(html)
    generated.append(p['filename'])
    print(f"Generated: {p['filename']}")

print(f"\nTotal: {len(generated)} pages")
