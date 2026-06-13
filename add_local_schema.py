#!/usr/bin/env python3
"""
add_local_schema.py — agrega LocalBusiness + TouristDestination schema
a las 16 zone-activities pages para boost local SEO.
"""
import re, json, glob

# Zone → (display_name, coords, country, region, GeoCircle radius km)
ZONE_META = {
    'miami':       ('Miami, FL', (25.7617, -80.1918), 'US', 'FL', 30),
    'broward':     ('Fort Lauderdale, FL', (26.1224, -80.1373), 'US', 'FL', 25),
    'keys':        ('Florida Keys', (24.5551, -81.7800), 'US', 'FL', 80),
    'palmbeach':   ('Palm Beach, FL', (26.7056, -80.0364), 'US', 'FL', 25),
    'nefl':        ('Northeast Florida', (29.6516, -81.3754), 'US', 'FL', 100),
    'jacksonville': ('Jacksonville, FL', (30.3322, -81.6557), 'US', 'FL', 50),
    'daytona':     ('Daytona Beach, FL', (29.2108, -81.0228), 'US', 'FL', 30),
    'space':       ('Space Coast / Cocoa Beach, FL', (28.3922, -80.6077), 'US', 'FL', 40),
    'orlando':     ('Orlando, FL', (28.5383, -81.3792), 'US', 'FL', 35),
    'centralfl':   ('Central Florida', (28.8000, -81.7000), 'US', 'FL', 80),
    'gulf':        ('Gulf Coast Florida', (28.0395, -82.7898), 'US', 'FL', 100),
    'westfl':      ('West Florida / Naples / Marco Island', (26.6406, -81.8723), 'US', 'FL', 100),
    'everglades':  ('Everglades, FL', (25.7906, -80.5836), 'US', 'FL', 60),
    'hawaii':      ('Hawaii Islands', (20.7984, -156.3319), 'US', 'HI', 200),
    'cancun':      ('Cancún & Riviera Maya', (21.1619, -86.8515), 'MX', 'QR', 60),
    'puntacana':   ('Punta Cana, Dominican Republic', (18.5601, -68.3725), 'DO', 'LA', 50),
}

ZONE_FILE_MAP = {
    'miami-activities.html': 'miami',
    'broward-activities.html': 'broward',
    'keys-activities.html': 'keys',
    'palm-beach-activities.html': 'palmbeach',
    'northeast-florida-activities.html': 'nefl',
    'jacksonville-activities.html': 'jacksonville',
    'daytona-activities.html': 'daytona',
    'space-coast-activities.html': 'space',
    'orlando-activities.html': 'orlando',
    'central-florida-activities.html': 'centralfl',
    'gulf-activities.html': 'gulf',
    'hawaii-activities.html': 'hawaii',
    'cancun-activities.html': 'cancun',
    'punta-cana-activities.html': 'puntacana',
}


def build_schema(zone_key, n_ops):
    name, (lat, lng), country, region, radius_km = ZONE_META[zone_key]
    url = f'https://miamijetskiboatrentals.com/{zone_key.replace("nefl","northeast-florida").replace("centralfl","central-florida").replace("westfl","gulf").replace("daytona","daytona").replace("space","space-coast").replace("palmbeach","palm-beach").replace("puntacana","punta-cana")}-activities'

    schema = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "TouristDestination",
                "name": f"{name} Watersports & Activities",
                "description": f"Marketplace of {n_ops}+ watersports operators in {name}: jet ski, boat charters, fishing, snorkel, sunset cruises and more. Real-time availability via FareHarbor.",
                "url": url,
                "geo": {
                    "@type": "GeoCoordinates",
                    "latitude": lat,
                    "longitude": lng
                },
                "address": {
                    "@type": "PostalAddress",
                    "addressLocality": name.split(',')[0],
                    "addressRegion": region,
                    "addressCountry": country
                },
                "touristType": ["Watersports enthusiasts", "Families", "Adventure travelers"]
            },
            {
                "@type": "LocalBusiness",
                "@id": url + "#business",
                "name": f"Florida Watersports Marketplace — {name}",
                "description": f"Compare and book {n_ops}+ verified watersports operators in {name}.",
                "url": url,
                "areaServed": {
                    "@type": "GeoCircle",
                    "geoMidpoint": {"@type": "GeoCoordinates", "latitude": lat, "longitude": lng},
                    "geoRadius": radius_km * 1000
                },
                "priceRange": "$$",
                "openingHours": "Mo-Su 00:00-23:59"
            }
        ]
    }
    return schema


def main():
    ops = json.load(open('operators-slim.json'))
    by_zone = {}
    for o in ops:
        by_zone.setdefault(o.get('zone', ''), []).append(o)

    updated = 0
    for fp, zone in ZONE_FILE_MAP.items():
        if zone not in ZONE_META: continue
        n_ops = len(by_zone.get(zone, []))
        if n_ops == 0: continue

        html = open(fp).read()
        schema = build_schema(zone, n_ops)
        schema_str = json.dumps(schema, ensure_ascii=False, separators=(',', ':'))

        # ¿ya tiene LocalBusiness schema?
        if 'LocalBusiness' in html and 'TouristDestination' in html:
            continue

        # Insertar antes de </head>
        tag = f'<script type="application/ld+json">{schema_str}</script>\n'
        if '</head>' not in html: continue
        html = html.replace('</head>', tag + '</head>', 1)
        open(fp, 'w').write(html)
        updated += 1
        print(f'  ✓ {fp} ({n_ops} ops, zone={zone})')

    print(f'\nTotal: {updated} archivos')


if __name__ == '__main__':
    main()
