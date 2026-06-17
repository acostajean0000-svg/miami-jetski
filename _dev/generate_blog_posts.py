#!/usr/bin/env python3
"""
generate_blog_posts.py — genera los 6 blog posts iniciales con datos reales.

Cada post incluye:
  - Article schema.org markup
  - Top 5-10 ops del filtro relevante (con precio, link, photo)
  - 600-1000 palabras de contenido
  - Internal links a zone pages
  - Breadcrumb schema
"""
import json
import os

POSTS = [
    {
        "slug": "best-jet-ski-rental-miami-beach-2026",
        "title": "Best Jet Ski Rental in Miami Beach 2026 — Top Operators Compared",
        "cat": "jetski",
        "zone": "miami",
        "min_price": 0,
        "max_price": 500,
        "intro_h2": "Miami Beach Jet Ski Rentals — What to Expect",
        "intro_body": """<p>Miami Beach is one of the world's premier jet ski destinations. Crystal-clear water, year-round sunshine, and a coastline studded with sandbars, island estates, and skylines make it a perfect playground for personal watercraft. Whether you're after a quick 30-minute thrill ride or a half-day exploration of Star Island and Millionaire's Row, dozens of operators offer rentals from $99/hr up.</p>
<p>This guide compares the top-rated jet ski rental operators in Miami Beach for 2026 — based on real-time availability, included safety gear, group size, and proximity to popular launch points like South Beach, Sunny Isles, and Haulover.</p>""",
        "h2_2": "What's Included in a Typical Miami Jet Ski Rental?",
        "body_2": """<p>Most operators include life jackets, basic instruction, fuel, and insurance in the rental price. Premium operators add safety briefings, GPS-equipped jet skis, and waterproof phone pouches. Look for:</p>
<ul>
  <li><strong>Licensing & Insurance:</strong> Florida requires anyone born after January 1, 1988 to have a Boating Safety ID. Most operators handle this on-site.</li>
  <li><strong>Group Capacity:</strong> Most jet skis hold 2-3 passengers. Solo riders should confirm minimum age (usually 18+ to drive).</li>
  <li><strong>Time Slots:</strong> 30-min, 1-hour, and half-day options are common. 1-hour gives you enough time to reach Star Island and back.</li>
  <li><strong>Tour vs Free-Ride:</strong> Guided tours include a route + scenic stops. Free-ride lets you explore independently.</li>
</ul>""",
        "h2_3": "Pricing Breakdown",
        "body_3": """<p>Miami Beach jet ski rentals typically follow this pricing structure for 2026:</p>
<ul>
  <li><strong>30 minutes:</strong> $99–$130</li>
  <li><strong>1 hour:</strong> $150–$250</li>
  <li><strong>2 hours:</strong> $280–$450</li>
  <li><strong>Half-day (4 hrs):</strong> $500–$800</li>
</ul>
<p>Expect higher prices during peak season (December–April, Spring Break) and weekends. Booking online via FareHarbor saves $20–50 vs walk-up rates and locks in your time slot.</p>""",
        "outro": """<p>Ready to ride? Browse <a href="/?cat=jetski&zone=miami">all jet ski rentals in Miami</a> sorted by price, rating, and zone. Each operator offers instant FareHarbor booking with free cancellation up to 24 hours.</p>"""
    },
    {
        "slug": "how-much-does-a-boat-rental-cost-key-west",
        "title": "How Much Does a Boat Rental Cost in Key West? 2026 Pricing Guide",
        "cat": "boat",
        "zone": "keywest",
        "min_price": 0,
        "max_price": 2000,
        "intro_h2": "Key West Boat Rental Pricing — Quick Overview",
        "intro_body": """<p>Key West is the southernmost point of the continental US — a paradise for boating with calm reef waters, snorkel spots, and historic harbors. Boat rental costs vary widely based on boat size, captain inclusion, and trip duration. This guide breaks down what you'll actually pay for popular options in 2026.</p>
<p>From small 18-foot center consoles for fishing trips to 60-foot catamarans for sunset cruises, here's the real cost structure across the most-requested boat types.</p>""",
        "h2_2": "Boat Rental Cost by Size & Type",
        "body_2": """<p>Pricing varies by boat type and includes/excludes options:</p>
<ul>
  <li><strong>18-22ft Center Console (self-drive):</strong> $300-$600 / half-day. Add ~$80 fuel + $30 dock fee.</li>
  <li><strong>24-30ft Bowrider or Pontoon:</strong> $500-$900 / full day. Captain optional (+$200).</li>
  <li><strong>Catamaran Charter (with captain):</strong> $1,200-$2,500 / half-day for groups of 6-12.</li>
  <li><strong>Luxury Yacht Charter:</strong> $2,000-$8,000 / day for 40-65ft yachts.</li>
  <li><strong>Sailing Charter:</strong> $400-$900 / half-day for 36-44ft sailboats.</li>
</ul>""",
        "h2_3": "What's Typically Included vs Extra",
        "body_3": """<p>When comparing quotes, check:</p>
<ul>
  <li><strong>Included:</strong> Coast Guard safety gear, fuel for short trips, ice cooler, snorkel gear (sometimes).</li>
  <li><strong>Often extra:</strong> Fuel for full-day trips, captain gratuity (15-20%), drinks & food, fishing gear, dock fees.</li>
  <li><strong>Watch out for:</strong> Damage deposit ($500-2,000), late-return fees, peak-season surcharges.</li>
</ul>
<p>A self-drive 22ft for $499 may end up costing $700+ with fuel, deposit hold, and fees. A captained charter at $1,500 is often a better value for first-timers.</p>""",
        "outro": """<p>Compare <a href="/?cat=boat&zone=keywest">all boat rentals in Key West</a> sorted by capacity, price, and reviews. Real-time availability and instant booking on every listing.</p>"""
    },
    {
        "slug": "beginners-guide-jet-skiing-cancun",
        "title": "Beginner's Guide to Jet Skiing in Cancun — Safety, Routes & Operators 2026",
        "cat": "jetski",
        "zone": "cancun",
        "min_price": 0,
        "max_price": 500,
        "intro_h2": "First Time Jet Skiing in Cancun? Start Here",
        "intro_body": """<p>Cancun's calm Caribbean waters and shallow turquoise lagoons make it one of the best places in the world to try jet skiing for the first time. The Nichupté Lagoon offers protected waters for absolute beginners, while the open Caribbean is for those wanting more speed and waves.</p>
<p>This guide covers everything a first-time rider needs to know: where to go, what's required, typical costs in pesos and USD, and the best operators for newbies in 2026.</p>""",
        "h2_2": "Requirements for Renting in Mexico",
        "body_2": """<p>Cancun has fewer licensing requirements than Florida. Most operators only require:</p>
<ul>
  <li><strong>Age:</strong> Minimum 16-18 to drive (varies by operator). Passengers can be younger.</li>
  <li><strong>ID:</strong> Passport or driver's license.</li>
  <li><strong>Deposit:</strong> Credit card hold of $300-$500 USD or equivalent.</li>
  <li><strong>Briefing:</strong> 5-10 minute safety orientation — usually in English and Spanish.</li>
</ul>""",
        "h2_3": "Where to Ride: Lagoon vs Open Sea",
        "body_3": """<p>Two main riding areas in Cancun:</p>
<ul>
  <li><strong>Nichupté Lagoon (Hotel Zone):</strong> Calm, protected water. Perfect for beginners. Average wind & no waves.</li>
  <li><strong>Caribbean Sea (Punta Cancún):</strong> Open ocean with small swells. Better for confident riders. More speed possible.</li>
  <li><strong>Isla Mujeres crossing:</strong> 30-minute open-water ride to Isla Mujeres. Advanced only — requires guided tour.</li>
</ul>
<p>For first-timers, always start in the lagoon. Most operators run 30-min sessions for $60-90 USD that include life jacket, safety briefing, and a guide rider.</p>""",
        "outro": """<p>Browse <a href="/?cat=jetski&zone=cancun">all jet ski operators in Cancun</a> filtered by price and zona hotelera. All listings include real-time availability via FareHarbor.</p>"""
    },
    {
        "slug": "snorkeling-spots-punta-cana",
        "title": "Top Snorkeling Spots in Punta Cana 2026 — Reefs, Islands & Best Tours",
        "cat": "snorkel",
        "zone": "puntacana",
        "min_price": 0,
        "max_price": 200,
        "intro_h2": "Why Punta Cana for Snorkeling?",
        "intro_body": """<p>Punta Cana sits on the eastern tip of the Dominican Republic — where the Atlantic and Caribbean meet. Warm year-round water (78-84°F), thriving reefs, and protected island sanctuaries make it a top-3 Caribbean snorkeling destination.</p>
<p>This guide covers the 5 must-visit snorkel spots, what marine life to expect, and the best half-day and full-day tours including round-trip transfers and lunch.</p>""",
        "h2_2": "Top 5 Snorkeling Spots",
        "body_2": """<ol>
  <li><strong>Catalina Island:</strong> 1-hour boat ride south. Crystal water, brain coral, sea turtles. Half-day catamaran trips ~$70-90/pp.</li>
  <li><strong>Saona Island:</strong> Full-day excursion. White sand, starfish in shallow water, lunch on the island. ~$80-110/pp.</li>
  <li><strong>Cabeza de Toro Reef:</strong> 10 min from shore. Beginner-friendly. Many local operators offer 2-hour tours from $40.</li>
  <li><strong>Bávaro Reef:</strong> Near the main hotel strip. Easy access, decent reef life. Good for first-timers.</li>
  <li><strong>Padre Nuestro Cave:</strong> Cenote-style underwater cave (advanced). Crystal-clear freshwater + saltwater mix.</li>
</ol>""",
        "h2_3": "Marine Life You'll See",
        "body_3": """<p>Common encounters on Punta Cana snorkel trips:</p>
<ul>
  <li>Sea turtles (year-round, but peak June–September)</li>
  <li>Parrotfish, sergeant majors, blue tangs (always)</li>
  <li>Stingrays in sandy patches</li>
  <li>Brain coral, sea fans, soft corals</li>
  <li>Nurse sharks (occasional, harmless) at Catalina</li>
</ul>
<p>Avoid touching coral, wear reef-safe sunscreen, and use a guided tour for the best spots. Most tours include snorkel gear, life vest, lunch, and round-trip hotel transfers.</p>""",
        "outro": """<p>Check <a href="/?cat=snorkel&zone=puntacana">all snorkel tours in Punta Cana</a> with real availability, transfer included, and English-speaking guides.</p>"""
    },
    {
        "slug": "road-to-hana-tour-guide-maui",
        "title": "Road to Hana Tour Guide — Maui's 64-Mile Coastal Adventure 2026",
        "cat": "tour",
        "zone": "hawaii",
        "min_price": 0,
        "max_price": 500,
        "intro_h2": "What is the Road to Hana?",
        "intro_body": """<p>The Road to Hana (Hawai'i Route 360) is a winding 64-mile coastal highway connecting Kahului to the small town of Hāna on Maui's eastern shore. It's not just a drive — it's a full-day expedition past 600+ turns, 50+ one-lane bridges, waterfalls, bamboo forests, black sand beaches, and lava tubes.</p>
<p>This guide compares self-drive vs guided tours, lists 10 must-stop attractions, and covers what to pack for the 8-12 hour journey in 2026.</p>""",
        "h2_2": "Self-Drive vs Guided Tour",
        "body_2": """<p>Both options have trade-offs:</p>
<ul>
  <li><strong>Self-drive (rental car):</strong> $80-150/day for car. Total cost $150-300 incl. gas, snacks, fees. You control the schedule but you'll miss commentary and may struggle finding hidden gems. <strong>Best for:</strong> experienced road-trippers, photographers.</li>
  <li><strong>Guided tour (van/SUV):</strong> $150-250/pp for 10-12 hour group tour. Includes pickup, breakfast, lunch, water, full historical commentary, guaranteed parking. <strong>Best for:</strong> first-timers, families, anyone who wants to relax.</li>
  <li><strong>Private VIP tour:</strong> $400-700/pp. Bronco/Jeep, max 4 guests, custom stops, gourmet picnic. <strong>Best for:</strong> couples, anniversaries.</li>
</ul>""",
        "h2_3": "Top 10 Must-Stop Attractions",
        "body_3": """<ol>
  <li>Twin Falls (mile 2) — easy first stop, two waterfalls</li>
  <li>Garden of Eden Arboretum (mile 10)</li>
  <li>Honomanu Bay overlook (mile 14)</li>
  <li>Ke'anae Peninsula — lava-cliff coastline</li>
  <li>Wailua Valley Lookout</li>
  <li>Upper Waikani Falls "Three Bears" (mile 19)</li>
  <li>Pua'a Ka'a State Wayside (waterfalls + pools)</li>
  <li>Hāna Lava Tube</li>
  <li>Wai'ānapanapa State Park (black sand beach)</li>
  <li>'Ohe'o Gulch / Seven Sacred Pools</li>
</ol>""",
        "outro": """<p>Compare <a href="/?cat=tour&zone=hawaii">all Hawaii tour operators</a> including Road to Hana experiences. Self-drive packages, guided van tours, and luxury private tours all in one place.</p>"""
    },
    {
        "slug": "fishing-charter-tips-destin",
        "title": "Fishing Charter Tips for Destin & Gulf Coast 2026 — Inshore vs Offshore",
        "cat": "fishing",
        "zone": "westfl",
        "min_price": 0,
        "max_price": 3000,
        "intro_h2": "Why Destin is the World's Luckiest Fishing Village",
        "intro_body": """<p>Destin, Florida earned its nickname for a reason: the deep Gulf waters are just minutes offshore, putting blue marlin, red snapper, mahi-mahi, and grouper within reach of half-day trips. Combined with shallow inshore bays full of redfish and speckled trout, Destin offers more fishing variety than almost anywhere in the US.</p>
<p>This guide breaks down inshore vs nearshore vs offshore charters, seasonal species, and what to expect for your first trip in 2026.</p>""",
        "h2_2": "Inshore vs Nearshore vs Offshore",
        "body_2": """<p>Three main types of charters in Destin:</p>
<ul>
  <li><strong>Inshore (bays, jetties, flats):</strong> 4-6 hour trips. Calm water — great for kids. Target redfish, speckled trout, flounder, sheepshead. $400-650 for up to 4 people.</li>
  <li><strong>Nearshore (1-10 miles out):</strong> 4-6 hours. Mild swells. Target king mackerel, Spanish mackerel, false albacore, cobia. $600-900 for up to 6.</li>
  <li><strong>Offshore (10-50+ miles):</strong> 8-12 hours. Big-game fishing. Target blue/white marlin, sailfish, yellowfin tuna, mahi, swordfish. $1,500-3,000 for up to 6.</li>
</ul>""",
        "h2_3": "Seasonal Species Calendar",
        "body_3": """<p>Best time for each species in Destin Gulf:</p>
<ul>
  <li><strong>Red Snapper:</strong> June (limited federal season) — book early</li>
  <li><strong>Grouper:</strong> May–October</li>
  <li><strong>Cobia:</strong> March–May (shallow water migration)</li>
  <li><strong>Tuna (yellowfin):</strong> April–September</li>
  <li><strong>Blue Marlin:</strong> July–September</li>
  <li><strong>Mahi-Mahi:</strong> June–August</li>
  <li><strong>Speckled Trout:</strong> Year-round, peak fall</li>
  <li><strong>Redfish:</strong> Year-round, peak winter</li>
</ul>
<p>Tipping captain & mate 15-20% of charter cost is standard. Don't bring your own bait/tackle — captains provide everything.</p>""",
        "outro": """<p>Browse <a href="/?cat=fishing&zone=westfl">all Gulf Coast fishing charters</a> filtered by inshore/offshore, duration, and price. Real captain reviews and instant booking.</p>"""
    }
]


def render_post(post, all_ops):
    # Filtrar ops
    filtered = [o for o in all_ops if o.get('cat') == post['cat'] and o.get('zone') == post['zone']]
    filtered = [o for o in filtered if post['min_price'] <= o.get('price', 0) <= post['max_price']]
    filtered.sort(key=lambda o: -(o.get('rating', 4.5) or 4.5))
    top_ops = filtered[:6]

    ops_html = '<h2>Top Operators</h2>\n<div class="post-ops">\n'
    for op in top_ops:
        photo = op.get('photo', '')
        name = op.get('name', '').replace('&', '&amp;').replace('"', '&quot;')
        zl = op.get('zl', '')
        price = op.get('price', 0)
        link = op.get('link', '')
        ops_html += f'''  <div class="op-mini">
    <div class="op-mini-img"><img src="{photo}" alt="{name}" loading="lazy"></div>
    <div class="op-mini-body">
      <h3>{name}</h3>
      <p>📍 {zl} · From ${price}</p>
      <a href="{link}" target="_blank" rel="noopener" class="op-mini-btn">Check Availability →</a>
    </div>
  </div>
'''
    ops_html += '</div>\n'

    title = post['title']
    title_esc = title.replace('"', '&quot;')
    desc = post['intro_body'].split('<p>')[1].split('</p>')[0][:155] if '<p>' in post['intro_body'] else ''
    hero_img = top_ops[0].get('photo') if top_ops else 'https://miamijetskiboatrentals.com/og-image.png'

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<link rel="preconnect" href="https://cdn.filestackcontent.com" crossorigin>
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="https://miamijetskiboatrentals.com/blog/{post['slug']}">
<meta name="robots" content="index,follow">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:type" content="article">
<meta property="og:url" content="https://miamijetskiboatrentals.com/blog/{post['slug']}">
<meta property="og:image" content="{hero_img}">
<link rel="stylesheet" href="/operator.css">
<style>
.post-wrap{{max-width:780px;margin:120px auto 60px;padding:0 20px;color:#c4ddf0;}}
.post-wrap h1{{color:#fff;font-size:clamp(1.6rem,3.5vw,2.4rem);line-height:1.2;margin-bottom:18px;}}
.post-wrap h2{{color:#fff;font-size:1.4rem;margin:40px 0 14px;}}
.post-wrap p{{font-size:1rem;line-height:1.7;margin-bottom:14px;color:#c4ddf0;}}
.post-wrap a{{color:#00d4c8;}}
.post-wrap ul,.post-wrap ol{{margin:14px 0 14px 22px;line-height:1.7;}}
.post-wrap li{{margin-bottom:6px;}}
.post-meta-bar{{color:#6a8aa0;font-size:.85rem;margin-bottom:30px;padding-bottom:14px;border-bottom:1px solid #1c3a58;}}
.post-ops{{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:20px;margin:24px 0;}}
.op-mini{{background:#0f2038;border:1px solid #1c3a58;border-radius:10px;overflow:hidden;}}
.op-mini-img{{aspect-ratio:16/9;overflow:hidden;}}
.op-mini-img img{{width:100%;height:100%;object-fit:cover;}}
.op-mini-body{{padding:14px;}}
.op-mini-body h3{{color:#fff;font-size:.95rem;margin-bottom:6px;}}
.op-mini-body p{{font-size:.82rem;color:#9bbdd4;margin-bottom:10px;}}
.op-mini-btn{{display:inline-block;background:#00d4c8;color:#081525!important;padding:8px 14px;border-radius:6px;font-weight:600;font-size:.82rem;}}
</style>
</head>
<body>
<nav class="nav"><div class="nav-inner"><a href="/" class="logo"><span class="logo-icon">🌊</span>Florida <span>Watersports</span></a></div></nav>

<article class="post-wrap">
  <div class="post-meta-bar">📅 January 2026 · ☕ {6 + len(top_ops)} min read · <a href="/blog/">← Back to Blog</a></div>
  <h1>{title}</h1>

  <h2>{post['intro_h2']}</h2>
  {post['intro_body']}

  <h2>{post['h2_2']}</h2>
  {post['body_2']}

  {ops_html}

  <h2>{post['h2_3']}</h2>
  {post['body_3']}

  {post['outro']}
</article>

<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "BlogPosting",
  "headline": "{title_esc}",
  "url": "https://miamijetskiboatrentals.com/blog/{post['slug']}",
  "datePublished": "2026-01-15",
  "dateModified": "2026-06-06",
  "author": {{"@type":"Organization","name":"Florida Watersports Marketplace"}},
  "publisher": {{"@type":"Organization","name":"Florida Watersports Marketplace","logo":{{"@type":"ImageObject","url":"https://miamijetskiboatrentals.com/apple-touch-icon.png"}}}},
  "image": "{hero_img}",
  "description": "{desc}",
  "mainEntityOfPage": "https://miamijetskiboatrentals.com/blog/{post['slug']}"
}}
</script>
<script type="application/ld+json">
{{
  "@context":"https://schema.org",
  "@type":"BreadcrumbList",
  "itemListElement":[
    {{"@type":"ListItem","position":1,"name":"Home","item":"https://miamijetskiboatrentals.com/"}},
    {{"@type":"ListItem","position":2,"name":"Blog","item":"https://miamijetskiboatrentals.com/blog/"}},
    {{"@type":"ListItem","position":3,"name":"{title[:50]}","item":"https://miamijetskiboatrentals.com/blog/{post['slug']}"}}
  ]
}}
</script>
</body>
</html>
'''


def main():
    all_ops = json.load(open('operators-slim.json'))
    os.makedirs('blog', exist_ok=True)

    for post in POSTS:
        fp = f"blog/{post['slug']}.html"
        html = render_post(post, all_ops)
        with open(fp, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f'  ✓ {fp}')

    print(f'\n{len(POSTS)} blog posts generados.')


if __name__ == '__main__':
    main()
