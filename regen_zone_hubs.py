#!/usr/bin/env python3
"""Regenerate every <zone>-activities.html page from operators.json.

The existing pages are 50–700 KB static snapshots with hardcoded operator
cards and stale "417 Operators" data. They drift away from operators.json
the moment new records are added. This script replaces each with a thin
dynamic page (~7 KB) that fetches operators-slim.json + slug-map.js and
renders cards live, so the page is always current.

Out-of-state hubs (cancun-activities.html, hawaii-activities.html) are left
untouched — they have no records in operators.json to link to.

Run after operators.json or slug-map.js changes:
    python3 regen_zone_hubs.py
"""
import json
import os
import re
from collections import Counter

BASE = os.path.dirname(os.path.abspath(__file__))

# (filename, zone-key, display label, hero subhead, lat, lng)
# zone-key matches the same scheme used by index.html's zoneMatches():
# canonical zones in operators.json, or sub-zone keys handled via op.zl.
ZONES = [
    ("miami-activities.html",            "miami",        "Miami",                   25.7617, -80.1918),
    ("fort-lauderdale-activities.html",  "broward",      "Fort Lauderdale & Broward", 26.1224, -80.1373),
    ("florida-keys-activities.html",     "keys",         "Florida Keys",            24.5557, -81.7826),
    ("key-west-activities.html",         "keywest",      "Key West",                24.5551, -81.7800),
    ("gulf-coast-activities.html",       "gulf",         "Gulf Coast",              26.6406, -81.8723),
    ("everglades-activities.html",       "everglades",   "Everglades",              25.7906, -80.5567),
    ("palm-beach-activities.html",       "palmbeach",    "Palm Beach",              26.7056, -80.0364),
    ("west-florida-activities.html",     "westfl",       "West Florida",            27.9506, -82.4572),
    ("space-coast-activities.html",      "space",        "Space Coast",             28.3922, -80.6077),
    ("central-florida-activities.html",  "centralfl",    "Central Florida",         28.5383, -81.3792),
    ("northeast-florida-activities.html","nefl",         "Northeast Florida",       30.3322, -81.6557),
    ("punta-cana-activities.html",       "puntacana",    "Punta Cana",              18.5601, -68.3725),
    # Sub-zones (matched via op.zl)
    ("tampa-activities.html",            "tampa",        "Tampa Bay",               27.9506, -82.4572),
    ("destin-activities.html",           "destin",       "Destin & Pensacola",      30.3935, -86.4958),
    ("orlando-activities.html",          "orlando",      "Orlando",                 28.5383, -81.3792),
    ("naples-activities.html",           "naples",       "Naples",                  26.1420, -81.7948),
    ("fort-myers-activities.html",       "ftmyers",      "Fort Myers",              26.6406, -81.8723),
    ("crystal-river-activities.html",    "crystalriver", "Crystal River",           28.9025, -82.5926),
    ("daytona-activities.html",          "daytona",      "Daytona Beach",           29.2108, -81.0228),
    ("jacksonville-activities.html",     "jacksonville", "Jacksonville",            30.3322, -81.6557),
]

CAT_LABELS = {
    "jetski": "Jet Ski", "boat": "Boat", "fishing": "Fishing", "watersports": "Water Sports",
    "slingshot": "Slingshot", "jetcar": "Jet Car", "golfcart": "Golf Cart", "atv": "ATV",
    "tour": "Tour", "aerial": "Aerial Tour", "bikerental": "Bike & E-Ride",
}
CAT_EMOJI = {
    "jetski": "🛥️", "boat": "⛵", "fishing": "🎣", "watersports": "🏄", "slingshot": "🏎️",
    "jetcar": "🚗", "golfcart": "🛺", "atv": "🏍️", "tour": "🚌", "aerial": "✈️", "bikerental": "🚲",
}
SUBZONE_PATTERNS = {
    "tampa":        r"tampa",
    "destin":       r"destin",
    "orlando":      r"orlando",
    "naples":       r"naples",
    "ftmyers":      r"fort\s*myers|ft\.?\s*myers",
    "crystalriver": r"crystal\s*river",
    "daytona":      r"daytona",
    "jacksonville": r"jacksonville",
    "keywest":      r"key\s*west",
}


def zone_match(zone_key: str, op: dict) -> bool:
    if op.get("zone") == zone_key:
        return True
    pat = SUBZONE_PATTERNS.get(zone_key)
    if pat and re.search(pat, op.get("zl", "") or "", re.I):
        return True
    return False


def jsonld_for(zone_label: str, slug: str, lat: float, lng: float, ops: list) -> str:
    rated = [o for o in ops if o.get("rating") and o.get("reviews")]
    avg_rating = round(sum(o["rating"] for o in rated) / len(rated), 2) if rated else 4.7
    review_count = sum(int(o.get("reviews", 0)) for o in rated)
    prices = [o["price"] for o in ops if isinstance(o.get("price"), (int, float)) and o["price"] > 0]
    p_min = min(prices) if prices else 0
    p_max = max(prices) if prices else 0
    site = "https://miamijetskiboatrentals.com"
    url = f"{site}/{slug}"
    # Top 30 operators by popularity for the ItemList
    def score(o):
        r = float(o.get("rating") or 0); rv = float(o.get("reviews") or 0)
        import math
        return r * math.log10(rv + 1)
    top = sorted(ops, key=score, reverse=True)[:30]
    slug_text = open(os.path.join(BASE, "slug-map.js")).read()
    slugs = dict(re.findall(r'"([^"]+)":"([^"]+)"', slug_text))

    blocks = []
    blocks.append({
        "@context": "https://schema.org",
        "@type": "TouristDestination",
        "name": f"{zone_label} Activities & Water Sports",
        "url": url,
        "description": f"{len(ops)} verified activity operators in {zone_label}. Jet ski, boat charters, watersports, and tours.",
        "geo": {"@type": "GeoCoordinates", "latitude": lat, "longitude": lng},
        "aggregateRating": {
            "@type": "AggregateRating",
            "ratingValue": str(avg_rating),
            "reviewCount": str(review_count),
            "bestRating": "5",
        },
        "priceRange": f"${p_min} – ${p_max}",
    })
    items = []
    for i, o in enumerate(top, start=1):
        op_slug = slugs.get(o["id"], "")
        items.append({
            "@type": "ListItem",
            "position": i,
            "item": {
                "@type": "LocalBusiness",
                "name": o.get("name", ""),
                "description": f"{CAT_LABELS.get(o.get('cat'), o.get('cat',''))} in {zone_label}",
                "url": f"{site}/{op_slug}" if op_slug else url,
            },
        })
    blocks.append({
        "@context": "https://schema.org",
        "@type": "ItemList",
        "name": f"{zone_label} Activities — {len(ops)} Operators",
        "numberOfItems": len(ops),
        "url": url,
        "itemListElement": items,
    })
    return "\n".join(
        f'<script type="application/ld+json">{json.dumps(b, ensure_ascii=False, separators=(",", ":"))}</script>'
        for b in blocks
    )


TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="color-scheme" content="dark">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
  <meta name="description" content="{description}">
  <meta name="robots" content="index,follow">
  <link rel="canonical" href="https://miamijetskiboatrentals.com/{slug}">
  <meta property="og:title" content="{title}">
  <meta property="og:description" content="{description}">
  <meta property="og:type" content="website">
  <meta property="og:url" content="https://miamijetskiboatrentals.com/{slug}">
  <meta property="og:image" content="https://miamijetskiboatrentals.com/og-image.png">
  <meta name="twitter:card" content="summary_large_image">
  <link rel="icon" type="image/x-icon" href="/favicon.ico">
  <link rel="manifest" href="/manifest.json">
  <meta name="theme-color" content="#040d1a">
  {jsonld}
  <link rel="preconnect" href="https://cdn.filestackcontent.com" crossorigin>
  <link rel="preconnect" href="https://fareharbor.com" crossorigin>
  <script src="/slug-map.js" defer></script>
  <style>
    *{{box-sizing:border-box;margin:0;padding:0}}
    body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:#040d1a;color:#e8f4fd;min-height:100vh;line-height:1.5}}
    a{{color:inherit;text-decoration:none}}
    nav{{background:#040d1a;border-bottom:1px solid rgba(0,210,255,.15);padding:0 20px;position:sticky;top:0;z-index:100;display:flex;align-items:center;gap:16px;height:56px}}
    .nav-logo{{font-size:1rem;font-weight:700;color:#00d2ff}}
    .nav-logo span{{color:#e8f4fd}}
    .nav-back{{margin-left:auto;font-size:.85rem;color:#00d2ff;background:rgba(0,210,255,.08);border:1px solid rgba(0,210,255,.2);border-radius:8px;padding:6px 14px}}
    .bc{{padding:14px 20px;font-size:.78rem;color:#7ba3c0;max-width:1200px;margin:0 auto;display:flex;flex-wrap:wrap;gap:6px}}
    .bc a{{color:#00d2ff}}.sep{{opacity:.4}}
    main{{max-width:1200px;margin:0 auto;padding:0 20px 60px}}
    .hero{{padding:40px 0 24px;text-align:center}}
    .hero h1{{font-size:clamp(1.8rem,5vw,2.6rem);font-weight:800;margin-bottom:14px;background:linear-gradient(135deg,#00d2ff,#5e9eff);-webkit-background-clip:text;background-clip:text;color:transparent}}
    .hero p{{color:#a8d4f0;font-size:1rem;max-width:680px;margin:0 auto}}
    .hero .stats{{display:flex;justify-content:center;gap:18px;margin-top:18px;flex-wrap:wrap}}
    .stat{{background:rgba(0,210,255,.08);border:1px solid rgba(0,210,255,.18);border-radius:10px;padding:8px 14px;font-size:.85rem;color:#e8f4fd}}
    .stat strong{{color:#00d2ff;font-weight:800}}
    .filters{{display:flex;flex-wrap:wrap;gap:8px;margin:24px 0 28px;padding:14px 16px;background:rgba(255,255,255,.02);border:1px solid rgba(0,210,255,.08);border-radius:14px}}
    .cat-chip{{cursor:pointer;background:rgba(0,210,255,.06);border:1px solid rgba(0,210,255,.18);border-radius:18px;padding:6px 12px;font-size:.78rem;color:#a8d4f0;transition:.15s;user-select:none}}
    .cat-chip:hover{{border-color:rgba(0,210,255,.45);color:#e8f4fd}}
    .cat-chip.active{{background:rgba(0,210,255,.22);border-color:#00d2ff;color:#00d2ff;font-weight:700}}
    .grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:18px}}
    .card{{background:rgba(255,255,255,.04);border:1px solid rgba(0,210,255,.1);border-radius:14px;overflow:hidden;transition:.2s;display:flex;flex-direction:column}}
    .card:hover{{border-color:rgba(0,210,255,.4);transform:translateY(-3px);box-shadow:0 8px 24px rgba(0,210,255,.12)}}
    .card .img{{height:180px;background-size:cover;background-position:center;background-color:#0a1929;position:relative}}
    .card .badge{{position:absolute;top:10px;left:10px;background:rgba(0,0,0,.7);border:1px solid rgba(0,210,255,.3);border-radius:14px;padding:3px 10px;font-size:.7rem;color:#00d2ff;font-weight:600}}
    .card .body{{padding:14px 16px 16px;display:flex;flex-direction:column;gap:6px;flex:1}}
    .card .name{{font-size:.95rem;font-weight:700;line-height:1.3;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}}
    .card .zl{{font-size:.78rem;color:#7ba3c0}}
    .card .price{{margin-top:auto;font-size:.95rem;font-weight:800;color:#00d2ff}}
    .empty{{text-align:center;padding:60px 20px;color:#7ba3c0}}
    .empty h2{{color:#e8f4fd;margin-bottom:10px}}
    footer{{background:#020810;border-top:1px solid rgba(0,210,255,.1);padding:32px 20px;text-align:center;color:#4a7a9b;font-size:.85rem}}
    footer a{{color:#00d2ff}}
    .sk{{background:linear-gradient(90deg,rgba(0,210,255,.05) 0%,rgba(0,210,255,.12) 50%,rgba(0,210,255,.05) 100%);background-size:200% 100%;animation:sk 1.5s infinite;border-radius:14px;height:280px}}
    @keyframes sk{{0%{{background-position:200% 0}}100%{{background-position:-200% 0}}}}
    @media(max-width:600px){{.hero{{padding:24px 0 12px}}.card .img{{height:150px}}}}
  </style>
</head>
<body>
<nav>
  <a href="/" class="nav-logo">💧 Florida<span>WaterSports</span></a>
  <a href="/" class="nav-back">← All Florida</a>
</nav>
<div class="bc"><a href="/">Home</a><span class="sep">›</span><span>{label} Activities</span></div>
<main>
  <section class="hero">
    <h1>{hero_title}</h1>
    <p>Compare <strong>{count}</strong> verified operators in {label} — jet ski, boat charters, fishing, water sports, tours and more. Instant booking via FareHarbor.</p>
    <div class="stats">
      <span class="stat"><strong>{count}</strong> operators</span>
      <span class="stat">From <strong>${price_min}</strong>/hr</span>
      <span class="stat">⭐ <strong>{avg_rating}</strong> avg rating</span>
    </div>
  </section>
  <div class="filters" id="filters">
    <span class="cat-chip active" data-cat="all">🌎 All ({count})</span>
    {cat_chips}
  </div>
  <div class="grid" id="grid"><div class="sk"></div><div class="sk"></div><div class="sk"></div><div class="sk"></div></div>
</main>
<footer>
  <p>© 2026 <a href="/">FloridaWaterSports</a> · {count} operators in {label}</p>
</footer>
<script>
const ZONE_KEY = {zone_key_json};
const ZL_PATTERN = {zl_pattern_json};
const CAT_LABELS = {cat_labels_json};
const CAT_EMOJI = {cat_emoji_json};
const FALLBACK_IMG = "https://images.unsplash.com/photo-1544551763-46a013bb70d5?w=900&q=80";

function esc(s){{return String(s==null?'':s).replace(/[&<>"'`]/g,c=>({{"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;","`":"&#96;"}})[c]);}}
function inZone(op){{
  if (op.zone === ZONE_KEY) return true;
  if (ZL_PATTERN) return new RegExp(ZL_PATTERN, 'i').test(op.zl||'');
  return false;
}}

let allOps = [];
let activeCat = 'all';

function thumbUrl(u){{
  if(!u) return FALLBACK_IMG;
  if(u.includes('cdn.filestackcontent.com')){{
    return u.replace(/resize=width:\\d+/, 'resize=width:480').replace(/quality=value:\\d+/, 'quality=value:75');
  }}
  return u;
}}

function render(){{
  const slugMap = (window._OP_SLUG_MAP) || {{}};
  const list = allOps.filter(o => activeCat==='all' || o.cat===activeCat);
  const grid = document.getElementById('grid');
  if (!list.length) {{
    grid.innerHTML = '<div class="empty" style="grid-column:1/-1"><h2>No operators in this view</h2><p>Try a different category, or <a href="/" style="color:#00d2ff">browse all of Florida</a>.</p></div>';
    return;
  }}
  grid.innerHTML = list.map((op,i) => {{
    const slug = slugMap[op.id] || '';
    const href = slug ? '/'+encodeURIComponent(slug) : (op.link || '#');
    const priceText = (op.price && op.price > 0) ? ('$'+op.price+'/hr') : 'Contact for pricing';
    const eager = i < 4 ? 'fetchpriority="high" loading="eager"' : 'loading="lazy" decoding="async"';
    return `<a class="card" href="${{esc(href)}}">
      <div class="img" style="background-image:url('${{esc(thumbUrl(op.photo))}}')">
        <span class="badge">${{CAT_EMOJI[op.cat]||'🌊'}} ${{esc(CAT_LABELS[op.cat]||op.cat)}}</span>
      </div>
      <div class="body">
        <div class="name">${{esc(op.name)}}</div>
        <div class="zl">📍 ${{esc(op.zl || '')}}</div>
        <div class="price">${{priceText}}</div>
      </div>
    </a>`;
  }}).join('');
}}

function setupFilters(){{
  document.querySelectorAll('.cat-chip').forEach(c => {{
    c.addEventListener('click', () => {{
      document.querySelectorAll('.cat-chip').forEach(x => x.classList.remove('active'));
      c.classList.add('active');
      activeCat = c.dataset.cat;
      render();
    }});
  }});
}}

(async () => {{
  try {{
    const r = await fetch('/operators-slim.json');
    const ops = await r.json();
    allOps = ops.filter(inZone);
    setupFilters();
    render();
  }} catch(e) {{
    document.getElementById('grid').innerHTML = '<div class="empty" style="grid-column:1/-1"><h2>Could not load operators</h2><p><a href="/" style="color:#00d2ff">Return home</a></p></div>';
  }}
}})();
</script>
</body>
</html>
"""


def main() -> int:
    ops = json.load(open(os.path.join(BASE, "operators.json")))
    written = 0
    for filename, zone_key, label, lat, lng in ZONES:
        # Filter ops for this zone (canonical or sub-zone via zl)
        matching = [o for o in ops if zone_match(zone_key, o)]
        count = len(matching)
        if count == 0:
            print(f"  skip (0 operators): {filename}")
            continue

        cats_in_zone = Counter(o["cat"] for o in matching)
        chips = "".join(
            f'<span class="cat-chip" data-cat="{c}">{CAT_EMOJI.get(c, "🌊")} {CAT_LABELS.get(c, c)} ({n})</span>'
            for c, n in cats_in_zone.most_common()
        )
        prices = [o["price"] for o in matching if isinstance(o.get("price"), (int, float)) and o["price"] > 0]
        price_min = min(prices) if prices else 0
        rated = [o for o in matching if o.get("rating") and o.get("reviews")]
        avg_rating = round(sum(o["rating"] for o in rated) / len(rated), 1) if rated else 4.7

        slug = filename.replace(".html", "")
        title = f"{label} Activities 2026 | {count} Operators — From ${price_min} | ⭐ {avg_rating} Stars"
        description = (
            f"Compare {count} verified {label} activity operators — jet ski, boat charters, "
            f"fishing, water sports, tours. ⭐ {avg_rating} avg rating. Instant booking, free cancellation."
        )
        hero_title = f"{label} Activities & Water Sports"

        html = TEMPLATE.format(
            title=title,
            description=description,
            slug=slug,
            label=label,
            hero_title=hero_title,
            count=count,
            price_min=price_min,
            avg_rating=avg_rating,
            cat_chips=chips,
            zone_key_json=json.dumps(zone_key),
            zl_pattern_json=json.dumps(SUBZONE_PATTERNS.get(zone_key, None)),
            cat_labels_json=json.dumps(CAT_LABELS),
            cat_emoji_json=json.dumps(CAT_EMOJI),
            jsonld=jsonld_for(label, slug, lat, lng, matching),
        )
        path = os.path.join(BASE, filename)
        open(path, "w").write(html)
        print(f"  wrote: {filename:<38} {count:4d} operators, {os.path.getsize(path):,} bytes")
        written += 1
    print(f"\nTotal zone hubs written: {written}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
