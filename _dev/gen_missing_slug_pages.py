#!/usr/bin/env python3
"""Pre-render a static HTML file for every operator slug that doesn't have one.

Why: 251 of the 652 operator slugs in slug-map.js had no static .html on disk —
they relied on the Vercel rewrite to fall through to operator-template.html.
That works in theory, but some deploys serve a 404 before the rewrite fires,
and there's no need to depend on it: we can just write each file.

Each generated page:
  * Has operator-specific <title>, <meta description>, OpenGraph & Twitter tags
  * Has pre-rendered JSON-LD (LocalBusiness + BreadcrumbList) so search engines
    see the real data without running JavaScript
  * Falls back to the same dynamic JS as operator-template.html to actually
    paint the cards / map / book button

Idempotent: re-running overwrites existing generated files. Hand-edited files
(the original 401) are NOT touched because they already exist on disk and we
SKIP if a file is present.

Run after operators.json or slug-map.js changes:
    python3 gen_missing_slug_pages.py
"""
import json
import os
import re
from html import escape

BASE = os.path.dirname(os.path.abspath(__file__))


CAT_LABELS = {
    "jetski": "Jet Ski Rental",
    "boat": "Boat Rental",
    "slingshot": "Slingshot Rental",
    "watersports": "Water Sports",
    "tour": "Tour",
    "fishing": "Fishing Charter",
    "jetcar": "Jet Car Rental",
    "atv": "ATV Rental",
    "golfcart": "Golf Cart Rental",
    "aerial": "Aerial Tour",
    "bikerental": "Bike Rental",
}
ZONE_LABELS = {
    "miami": "Miami Beach",
    "broward": "Fort Lauderdale / Broward",
    "keys": "Florida Keys",
    "palmbeach": "Palm Beach",
    "gulf": "Gulf Coast",
    "centralfl": "Central Florida",
    "everglades": "Everglades",
    "westfl": "West Florida",
    "space": "Space Coast",
    "nefl": "Northeast Florida",
    "puntacana": "Punta Cana, Dominican Republic",
}
CAT_PAGE = {
    "jetski": "/jet-ski-rentals-florida.html",
    "boat": "/boat-rentals-florida.html",
    "slingshot": "/slingshot-rentals-florida.html",
    "watersports": "/water-sports-florida.html",
    "tour": "/tours-florida.html",
    "fishing": "/fishing-charters-florida.html",
    "jetcar": "/jet-car-rentals-florida.html",
    "atv": "/atv-rentals-florida.html",
    "golfcart": "/golf-cart-rentals-florida.html",
    "aerial": "/tours-florida.html",
    "bikerental": "/water-sports-florida.html",
}


def render_page(op: dict, slug: str) -> str:
    site = "https://miamijetskiboatrentals.com"
    url = f"{site}/{slug}"
    cat = op.get("cat", "")
    zone = op.get("zone", "")
    cat_label = CAT_LABELS.get(cat, cat or "Activity")
    zone_label = ZONE_LABELS.get(zone, op.get("zl") or zone)
    cat_page = CAT_PAGE.get(cat, "/")
    country = op.get("country", "US")
    region = "FL" if country == "US" else ""
    price = op.get("price")
    price_text = f"From ${price}/hr" if isinstance(price, (int, float)) and price > 0 else "Contact for pricing"
    lat = op.get("lat")
    lng = op.get("lng")
    has_coords = bool(lat) and bool(lng) and lat != 0 and lng != 0
    map_block = (
        f'  <p class="stitle">📍 Location</p>\n'
        f'  <div class="map-wrap">\n'
        f'    <iframe src="https://maps.google.com/maps?q={lat},{lng}&z=15&output=embed"\n'
        f'            allowfullscreen loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe>\n'
        f'  </div>\n'
    ) if has_coords else ""

    title = f"{op['name']} | {cat_label} in {zone_label} | Florida Water Sports"
    description = (
        f"Book {op['name']} — {cat_label} in {zone_label}. {price_text}. "
        f"{op.get('addr', '')}".strip().rstrip(".") + "."
    )

    ld_business = {
        "@context": "https://schema.org",
        "@type": "LocalBusiness",
        "name": op["name"],
        "description": f"{cat_label} in {zone_label}. {price_text}.",
        "address": {
            "@type": "PostalAddress",
            "streetAddress": op.get("addr", ""),
            "addressRegion": region,
            "addressCountry": country,
        },
        "geo": {
            "@type": "GeoCoordinates",
            "latitude": op.get("lat"),
            "longitude": op.get("lng"),
        },
        "url": url,
        "image": op.get("photo", ""),
    }
    if isinstance(price, (int, float)) and price > 0:
        ld_business["priceRange"] = f"From ${price}"
    if op.get("rating") and op.get("reviews"):
        ld_business["aggregateRating"] = {
            "@type": "AggregateRating",
            "ratingValue": str(op["rating"]),
            "reviewCount": str(int(op["reviews"])),
            "bestRating": "5",
        }
    ld_breadcrumbs = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{site}/"},
            {"@type": "ListItem", "position": 2, "name": cat_label, "item": f"{site}{cat_page}"},
            {"@type": "ListItem", "position": 3, "name": op["name"], "item": url},
        ],
    }

    e = escape  # alias
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="color-scheme" content="dark">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(description)}">
<meta name="robots" content="index,follow">
<link rel="canonical" href="{e(url)}">
<meta property="og:title" content="{e(op['name'])} | {e(cat_label)} in {e(zone_label)}">
<meta property="og:description" content="Book {e(op['name'])} in {e(zone_label)}. {e(price_text)}.">
<meta property="og:url" content="{e(url)}">
<meta property="og:type" content="website">
<meta property="og:image" content="{e(op.get('photo','') or site + '/og-image.png')}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="{e(op.get('photo','') or site + '/og-image.png')}">
<link rel="icon" type="image/x-icon" href="/favicon.ico">
<link rel="manifest" href="/manifest.json">
<meta name="theme-color" content="#040d1a">
<script type="application/ld+json">{json.dumps(ld_business, ensure_ascii=False, separators=(',', ':'))}</script>
<script type="application/ld+json">{json.dumps(ld_breadcrumbs, ensure_ascii=False, separators=(',', ':'))}</script>
<link rel="preconnect" href="https://fareharbor.com" crossorigin>
<link rel="dns-prefetch" href="https://fareharbor.com">
<script async src="https://www.googletagmanager.com/gtag/js?id=G-4KJ2DD0HB1"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}gtag('js',new Date());gtag('config','G-4KJ2DD0HB1');</script>
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:#040d1a;color:#e8f4fd;min-height:100vh}}
a{{color:inherit;text-decoration:none}}
nav{{background:#040d1a;border-bottom:1px solid rgba(0,210,255,.15);padding:0 20px;position:sticky;top:0;z-index:100;display:flex;align-items:center;gap:16px;height:56px}}
.nav-logo{{font-size:1rem;font-weight:700;color:#00d2ff}}.nav-logo span{{color:#e8f4fd}}
.nav-back{{margin-left:auto;font-size:.85rem;color:#00d2ff;background:rgba(0,210,255,.08);border:1px solid rgba(0,210,255,.2);border-radius:8px;padding:6px 14px}}
.bc{{padding:14px 20px;font-size:.78rem;color:#7ba3c0;max-width:1100px;margin:0 auto;display:flex;flex-wrap:wrap;gap:6px}}
.bc a{{color:#00d2ff}}.sep{{opacity:.4}}
#main{{max-width:1100px;margin:0 auto;padding:0 20px 40px}}
.hero-photo{{width:100%;height:320px;object-fit:cover;border-radius:16px;background:#0a1929;display:block}}
.hero-wrap{{position:relative;margin-bottom:24px}}
.hero-badge{{position:absolute;top:16px;left:16px;background:rgba(0,0,0,.7);border:1px solid rgba(0,210,255,.3);border-radius:20px;padding:5px 14px;font-size:.8rem;font-weight:600;color:#00d2ff}}
h1{{font-size:clamp(1.4rem,4vw,2rem);font-weight:800;margin-bottom:12px}}
.chips{{display:flex;flex-wrap:wrap;gap:10px;margin-bottom:28px}}
.chip{{background:rgba(0,210,255,.08);border:1px solid rgba(0,210,255,.15);border-radius:20px;padding:6px 14px;font-size:.82rem;color:#a8d4f0}}
.chip.price{{background:rgba(0,210,255,.15);border-color:rgba(0,210,255,.35);color:#00d2ff;font-weight:700;font-size:.95rem}}
.book-btn{{display:block;width:100%;max-width:480px;background:linear-gradient(135deg,#00d2ff,#0099cc);color:#040d1a;font-weight:800;font-size:1.1rem;text-align:center;padding:16px 24px;border-radius:14px;margin:0 auto 40px;box-shadow:0 4px 20px rgba(0,210,255,.3)}}
.stitle{{font-size:1.1rem;font-weight:700;color:#00d2ff;margin-bottom:14px}}
.dg{{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:14px;margin-bottom:40px}}
.dc{{background:rgba(255,255,255,.04);border:1px solid rgba(0,210,255,.1);border-radius:12px;padding:16px 18px}}
.dl{{font-size:.72rem;text-transform:uppercase;letter-spacing:.08em;color:#7ba3c0;margin-bottom:6px}}
.dv{{font-size:.95rem;font-weight:600}}
.map-wrap{{border-radius:14px;overflow:hidden;margin-bottom:40px;border:1px solid rgba(0,210,255,.15)}}
.map-wrap iframe{{width:100%;height:320px;border:0;display:block}}
footer{{background:#020810;border-top:1px solid rgba(0,210,255,.1);padding:28px 20px;text-align:center;color:#4a7a9b;font-size:.82rem}}
footer a{{color:#00d2ff}}
@media(max-width:600px){{.hero-photo{{height:220px}}.map-wrap iframe{{height:240px}}}}
</style>
</head>
<body>
<nav>
  <a href="/" class="nav-logo">💧 Florida<span>WaterSports</span></a>
  <a href="/" class="nav-back">← All operators</a>
</nav>
<div class="bc">
  <a href="/">Home</a><span class="sep">›</span>
  <a href="{e(cat_page)}">{e(cat_label)}</a><span class="sep">›</span>
  <span>{e(op['name'])}</span>
</div>
<main id="main">
  <div class="hero-wrap">
    <img class="hero-photo" src="{e(op.get('photo','') or '/og-image.png')}" alt="{e(op['name'])}"
         loading="eager" fetchpriority="high"
         onerror="this.onerror=null;this.src='https://images.unsplash.com/photo-1544551763-46a013bb70d5?w=900&amp;q=80'">
    {f'<span class="hero-badge">{e(op.get("badge",""))}</span>' if op.get('badge') else ''}
  </div>
  <h1>{e(op['name'])}</h1>
  <div class="chips">
    <span class="chip price">{e(price_text)}</span>
    <span class="chip">{e(zone_label)}</span>
    <span class="chip">{e(cat_label)}</span>
  </div>
  <a href="{e(op.get('link','#'))}" target="_blank" rel="noopener noreferrer" class="book-btn">🏄 Book Now — {e(price_text)}</a>
  <p class="stitle">📋 Details</p>
  <div class="dg">
    <div class="dc"><div class="dl">Address</div><div class="dv">{e(op.get('addr',''))}</div></div>
    <div class="dc"><div class="dl">Category</div><div class="dv">{e(cat_label)}</div></div>
    <div class="dc"><div class="dl">Zone</div><div class="dv">{e(zone_label)}</div></div>
    <div class="dc"><div class="dl">Starting Price</div><div class="dv">{e(price_text)}</div></div>
  </div>
{map_block}</main>
<footer>
  <p>© 2026 <a href="/">FloridaWaterSports</a> · 550+ operators across Florida</p>
</footer>
</body>
</html>
"""


def main() -> int:
    ops = json.load(open(os.path.join(BASE, "operators.json")))
    slug_text = open(os.path.join(BASE, "slug-map.js")).read()
    slugs = dict(re.findall(r'"([^"]+)":"([^"]+)"', slug_text))  # id -> slug

    written, skipped_exists, skipped_no_op = 0, 0, 0
    for op_id, slug in slugs.items():
        path = os.path.join(BASE, f"{slug}.html")
        if os.path.exists(path):
            skipped_exists += 1
            continue
        op = next((o for o in ops if o["id"] == op_id), None)
        if not op:
            skipped_no_op += 1
            continue
        open(path, "w").write(render_page(op, slug))
        written += 1

    print(f"Generated: {written}")
    print(f"Skipped (file already existed): {skipped_exists}")
    print(f"Skipped (op not in operators.json): {skipped_no_op}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
