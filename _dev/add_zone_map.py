#!/usr/bin/env python3
"""
add_zone_map.py — agrega mapa Leaflet con clusters + SEO index a zone activity pages.

Para cada *-activities.html con ZONE_KEY:
  - Inyecta CSS Leaflet preload
  - Inyecta <div id="map"> antes del grid
  - Modifica el script de render para inicializar mapa lazy (IntersectionObserver)
  - Cada op renderea como marker con popup → link a operator page
  - Marker cluster groups
"""
from __future__ import annotations
import re, glob, sys, json

# Zona → centro del mapa + zoom inicial
ZONE_CENTER = {
    'miami':       (25.7617, -80.1918, 11),
    'broward':     (26.1224, -80.1373, 11),
    'cancun':      (21.1619, -86.8515, 11),
    'puntacana':   (18.5601, -68.3725, 11),
    'hawaii':      (20.7984, -156.3319, 8),
    'keys':        (24.5551, -81.7800, 10),
    'keywest':     (24.5551, -81.7800, 12),
    'palmbeach':   (26.7056, -80.0364, 11),
    'nefl':        (29.6516, -81.3754, 9),
    'space':       (28.3922, -80.6077, 10),
    'orlando':     (28.5383, -81.3792, 10),
    'centralfl':   (28.8000, -81.7000, 9),
    'gulf':        (28.0395, -82.7898, 8),
    'westfl':      (26.6406, -81.8723, 8),
    'everglades':  (25.7906, -80.5836, 10),
    'daytona':     (29.2108, -81.0228, 11),
    'jacksonville':(30.3322, -81.6557, 11),
}

LEAFLET_PRELOAD = '''<link href="/vendor/leaflet/leaflet.css" rel="preload" as="style" onload="this.onload=null;this.rel='stylesheet'" integrity="sha384-sHL9NAb7lN7rfvG5lfHpm643Xkcjzp4jFvuavGOndn6pjVqS6ny56CAt3nsEVT4H" crossorigin="anonymous">
<noscript><link href="/vendor/leaflet/leaflet.css" rel="stylesheet" integrity="sha384-sHL9NAb7lN7rfvG5lfHpm643Xkcjzp4jFvuavGOndn6pjVqS6ny56CAt3nsEVT4H" crossorigin="anonymous"></noscript>
<link href="/vendor/leaflet/MarkerCluster.css" rel="preload" as="style" onload="this.onload=null;this.rel='stylesheet'" integrity="sha384-pmjIAcz2bAn0xukfxADbZIb3t8oRT9Sv0rvO+BR5Csr6Dhqq+nZs59P0pPKQJkEV" crossorigin="anonymous">
<link href="/vendor/leaflet/MarkerCluster.Default.css" rel="preload" as="style" onload="this.onload=null;this.rel='stylesheet'" integrity="sha384-wgw+aLYNQ7dlhK47ZPK7FRACiq7ROZwgFNg0m04avm4CaXS+Z9Y7nMu8yNjBKYC+" crossorigin="anonymous">
<noscript><link href="/vendor/leaflet/MarkerCluster.css" rel="stylesheet" integrity="sha384-pmjIAcz2bAn0xukfxADbZIb3t8oRT9Sv0rvO+BR5Csr6Dhqq+nZs59P0pPKQJkEV" crossorigin="anonymous"><link href="/vendor/leaflet/MarkerCluster.Default.css" rel="stylesheet" integrity="sha384-wgw+aLYNQ7dlhK47ZPK7FRACiq7ROZwgFNg0m04avm4CaXS+Z9Y7nMu8yNjBKYC+" crossorigin="anonymous"></noscript>
'''

MAP_CSS = '''    .map-wrap{margin:20px 0;border-radius:14px;overflow:hidden;border:1px solid rgba(0,210,255,.15);height:380px;position:relative;background:#0a1428}
    .map-wrap-skeleton{display:flex;align-items:center;justify-content:center;height:100%;color:#7ba3c0;font-size:.9rem;gap:8px}
    .map-wrap-skeleton::before{content:"🗺️";font-size:2rem;animation:pulse 1.5s ease-in-out infinite}
    @keyframes pulse{0%,100%{opacity:.5}50%{opacity:1}}
    #map{height:100%;width:100%}
    .leaflet-popup-content{font-family:inherit;margin:10px 14px;font-size:.85rem}
    .leaflet-popup-content a{color:#00d2ff;font-weight:600;text-decoration:none}
    .leaflet-popup-content .pp-cat{font-size:.72rem;color:#7ba3c0;text-transform:uppercase;letter-spacing:.5px}
    .leaflet-popup-content .pp-price{color:#5e9eff;font-weight:700;margin-top:4px}
    /* SEO index */
    .seo-index{margin:32px 0;padding:24px;background:rgba(0,210,255,.04);border:1px solid rgba(0,210,255,.12);border-radius:14px}
    .seo-index h2{font-size:1.1rem;color:#00d2ff;margin-bottom:14px}
    .seo-index-list{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:6px 16px;list-style:none;margin:0;padding:0;font-size:.85rem}
    .seo-index-list li{padding:3px 0;border-bottom:1px dashed rgba(0,210,255,.08)}
    .seo-index-list li a{color:#a8d4f0;display:flex;justify-content:space-between;gap:8px}
    .seo-index-list li a:hover{color:#00d2ff}
    .seo-index-list .ix-cat{color:#7ba3c0;font-size:.75rem;flex-shrink:0}
    .seo-index-toggle{background:rgba(0,210,255,.1);border:1px solid rgba(0,210,255,.3);color:#00d2ff;padding:6px 14px;border-radius:50px;font-size:.78rem;font-weight:600;cursor:pointer;margin-top:14px;transition:.15s}
    .seo-index-toggle:hover{background:rgba(0,210,255,.18)}'''

# Marker rendering + map init code (inyectado al final del script)
def map_init_code(zone_key: str, lat: float, lng: float, zoom: int) -> str:
    return f'''
// ─── MAP INTEGRATION ────────────────────────────────────────
let mapInstance = null, markerCluster = null;
function loadLeaflet(cb){{
  if (window.L) return cb();
  const s = document.createElement('script');
  s.src = '/vendor/leaflet/leaflet.js';
  s.onload = () => {{
    const c = document.createElement('script');
    c.src = '/vendor/leaflet/leaflet.markercluster.js';
    c.onload = cb;
    document.head.appendChild(c);
  }};
  document.head.appendChild(s);
}}

function initMap(){{
  if (mapInstance) return refreshMarkers();
  loadLeaflet(() => {{
    document.querySelector('.map-wrap-skeleton')?.remove();
    mapInstance = L.map('map',{{zoomControl:true, scrollWheelZoom:false}}).setView([{lat},{lng}],{zoom});
    L.tileLayer('https://{{s}}.basemaps.cartocdn.com/dark_all/{{z}}/{{x}}/{{y}}{{r}}.png',{{
      attribution:'© OpenStreetMap © CARTO', maxZoom:18, subdomains:'abcd'
    }}).addTo(mapInstance);
    markerCluster = L.markerClusterGroup({{showCoverageOnHover:false, maxClusterRadius:50}});
    mapInstance.addLayer(markerCluster);
    refreshMarkers();
  }});
}}

function refreshMarkers(){{
  if (!markerCluster) return;
  markerCluster.clearLayers();
  const slugMap = window._OP_SLUG_MAP || {{}};
  const list = allOps.filter(o => (activeCat==='all' || o.cat===activeCat) && o.lat && o.lng);
  const markers = list.map(op => {{
    const slug = slugMap[op.id] || '';
    const href = slug ? '/'+slug : (op.link || '#');
    const emoji = CAT_EMOJI[op.cat] || '🌊';
    const popup = `<div><div class="pp-cat">${{esc(CAT_LABELS[op.cat]||'')}}</div><a href="${{esc(href)}}"><strong>${{esc(op.name).slice(0,60)}}</strong></a><div class="pp-price">${{op.price?'From $'+op.price:''}}</div></div>`;
    return L.marker([op.lat, op.lng]).bindPopup(popup);
  }});
  markerCluster.addLayers(markers);
  if (markers.length) mapInstance.fitBounds(markerCluster.getBounds().pad(0.15), {{maxZoom:13}});
}}

// Lazy-init mapa cuando el usuario haga scroll cerca de él
new IntersectionObserver((entries) => {{
  if (entries.some(e => e.isIntersecting)) initMap();
}}, {{rootMargin:'200px'}}).observe(document.querySelector('.map-wrap'));

// SEO Index - render lazy
function renderSeoIndex(){{
  const ul = document.getElementById('seoIndexList');
  if (!ul || ul.dataset.rendered) return;
  ul.dataset.rendered = 'true';
  const slugMap = window._OP_SLUG_MAP || {{}};
  const sorted = [...allOps].sort((a,b) => a.name.localeCompare(b.name));
  ul.innerHTML = sorted.map(op => {{
    const slug = slugMap[op.id] || '';
    const href = slug ? '/'+slug : '#';
    const cat = CAT_LABELS[op.cat]||op.cat;
    return '<li><a href="'+esc(href)+'"><span>'+esc(op.name).slice(0,55)+'</span><span class="ix-cat">'+esc(cat)+'</span></a></li>';
  }}).join('');
}}
document.getElementById('seoIndexBtn')?.addEventListener('click', function(){{
  const c = document.getElementById('seoIndexContent');
  if (c.style.display === 'none' || !c.style.display) {{
    c.style.display='block'; this.textContent='Hide index ▲'; renderSeoIndex();
  }} else {{
    c.style.display='none'; this.textContent='Browse all '+allOps.length+' operators alphabetically ▼';
  }}
}});
'''

MAP_HTML = '''  <div class="map-wrap" id="mapWrap"><div class="map-wrap-skeleton">Loading map…</div><div id="map"></div></div>
'''

SEO_INDEX_HTML_TEMPLATE = '''  <section class="seo-index">
    <h2>📋 All Operators in {zone_display_name}</h2>
    <p style="color:#7ba3c0;font-size:.85rem;margin-bottom:14px">Quick alphabetical index for search and browsing.</p>
    <button class="seo-index-toggle" id="seoIndexBtn" type="button">Browse all operators alphabetically ▼</button>
    <div id="seoIndexContent" style="display:none;margin-top:14px">
      <ul class="seo-index-list" id="seoIndexList"></ul>
    </div>
  </section>
'''

ZONE_DISPLAY = {
    'miami': 'Miami', 'broward': 'Fort Lauderdale & Broward',
    'cancun': 'Cancún & Riviera Maya', 'puntacana': 'Punta Cana',
    'hawaii': 'Hawaii', 'keys': 'Florida Keys', 'keywest': 'Key West',
    'palmbeach': 'Palm Beach', 'nefl': 'Northeast Florida',
    'space': 'Space Coast', 'orlando': 'Orlando', 'centralfl': 'Central Florida',
    'gulf': 'Gulf Coast', 'westfl': 'West Florida', 'everglades': 'Everglades',
    'daytona': 'Daytona', 'jacksonville': 'Jacksonville',
}

ZONE_FILE_MAP = {
    'miami-activities.html': 'miami',
    'broward-activities.html': 'broward',
    'cancun-activities.html': 'cancun',
    'punta-cana-activities.html': 'puntacana',
    'hawaii-activities.html': 'hawaii',
    'keys-activities.html': 'keywest',
    'palm-beach-activities.html': 'palmbeach',
    'northeast-florida-activities.html': 'nefl',
    'space-coast-activities.html': 'space',
    'orlando-activities.html': 'orlando',
    'central-florida-activities.html': 'centralfl',
    'gulf-activities.html': 'gulf',
    'daytona-activities.html': 'daytona',
    'jacksonville-activities.html': 'jacksonville',
}


def process(fp: str, zone_key: str) -> bool:
    html = open(fp).read()
    if 'id="mapWrap"' in html: return False  # already done

    if zone_key not in ZONE_CENTER:
        print(f'  ⚠ {fp}: zone {zone_key} sin coords, skip')
        return False

    lat, lng, zoom = ZONE_CENTER[zone_key]

    # 1. Inyectar Leaflet preload antes de </head>
    if '/vendor/leaflet/leaflet.css' not in html:
        html = html.replace('</head>', LEAFLET_PRELOAD + '</head>', 1)

    # 2. Inyectar CSS del mapa al final del <style>
    html = re.sub(r'(</style>)', MAP_CSS + r'\n\1', html, count=1)

    # 3. Inyectar div del mapa antes del grid
    seo_idx = SEO_INDEX_HTML_TEMPLATE.format(zone_display_name=ZONE_DISPLAY.get(zone_key, zone_key))
    html = html.replace(
        '<div class="grid" id="grid">',
        MAP_HTML + '<div class="grid" id="grid">',
        1
    )

    # 4. Inyectar SEO index después de </main>
    html = html.replace('</main>', seo_idx + '</main>', 1)

    # 5. Inyectar mapInit code dentro del último <script> bloque del archivo
    # Encontrar el bloque del IIFE que termina con })();
    map_code = map_init_code(zone_key, lat, lng, zoom)

    # Insertar el código justo antes de )(); o })(); del script principal
    # El script principal es el del setupFilters/render
    if 'window._OP_SLUG_MAP' in html or 'allOps =' in html:
        # Insertar después de la última asignación a allOps (donde se carga la data)
        # Mejor: insertar antes del </script> final del bloque async
        # Buscar la línea "await loadLeaflet... or similar"
        # Hack: insertar map_code antes del último </script>
        last_script = html.rfind('</script>')
        if last_script != -1:
            # Buscar el <script> que lo abrió
            html = html[:last_script] + map_code + '\n' + html[last_script:]

    open(fp, 'w').write(html)
    return True


def main():
    updated = 0
    for fp, zone in ZONE_FILE_MAP.items():
        import os
        if not os.path.exists(fp):
            print(f'  skip (no existe): {fp}')
            continue
        if process(fp, zone):
            print(f'  ✓ {fp} (zone={zone})')
            updated += 1
        else:
            print(f'  - {fp} (ya tenía mapa o sin coords)')
    print(f'\nTotal actualizados: {updated}')


if __name__ == '__main__':
    main()
