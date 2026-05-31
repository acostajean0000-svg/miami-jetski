#!/usr/bin/env python3
import json, re

import os as _os
BASE = _os.path.dirname(_os.path.abspath(__file__))

with open(f'{BASE}/operators.json') as f:
    ops = json.load(f)
with open(f'{BASE}/cudjoe-key-boat-rentals-florida-keys-cudjoe-key.html') as f:
    tmpl = f.read()

new_ops = [
  {
    'id': 'b586',
    'name': 'Code Blue Fishing - Dolphin Cruise',
    'addr': 'Fort Walton Beach, FL 32548',
    'zone': 'destin', 'zl': 'Fort Walton Beach', 'cat': 'to',
    'price': 350, 'lat': 30.428408, 'lng': -86.607397,
    'photo': 'YfOcxbaS2CeEKSxeEp0w',
    'link': 'https://fareharbor.com/embeds/book/codebluefishingcharters/items/399810/calendar/2026/05/?asn=fhdn&asn-ref=miamistylerentals&ref=miamistylerentals&marketplace=yes&flow=no&full-items=yes',
    'badge': 'top', 'rating': 5.0, 'reviews': 146,
    'desc': 'Dolphin cruise along the Fort Walton Beach Okaloosa Island coastline with expert guides. From $350. 5.0 stars with 146 reviews. Spot wild dolphins in the Choctawhatchee Bay.'
  },
  {
    'id': 'b587',
    'name': 'Next Level Jet Ski - Sarasota',
    'addr': 'Sarasota, FL 34231',
    'zone': 'gulf', 'zl': 'Sarasota', 'cat': 'js',
    'price': 120, 'lat': 27.345649, 'lng': -82.547617,
    'photo': 'fBBveVWMS3i4t2QORBco',
    'link': 'https://fareharbor.com/embeds/book/nextleveljetstkirental/items/442018/calendar/2026/05/?asn=fhdn&asn-ref=miamistylerentals&ref=miamistylerentals&marketplace=yes&flow=no&full-items=yes',
    'badge': 'top', 'rating': 4.9, 'reviews': 950,
    'desc': 'Jet ski rentals on Sarasota Bay with nearly 1,000 five-star reviews. From $120. 4.9 stars with 950 reviews. Ride the crystal-clear waters near Siesta Key on a high-powered waverunner.'
  },
  {
    'id': 'b588',
    'name': 'Parasail Low Tide - Private Parasailing Sarasota',
    'addr': 'Sarasota, FL 34231',
    'zone': 'gulf', 'zl': 'Sarasota', 'cat': 'to',
    'price': 599, 'lat': 27.332245, 'lng': -82.58035,
    'photo': 'baP41cZTR9anA2EvIVAg',
    'link': 'https://fareharbor.com/embeds/book/parasaillowtide/items/530320/calendar/2026/05/?asn=fhdn&asn-ref=miamistylerentals&ref=miamistylerentals&marketplace=yes&flow=no&full-items=yes',
    'badge': 'top', 'rating': 5.0, 'reviews': 290,
    'desc': 'Private parasailing experience over the turquoise waters of Sarasota Bay. From $599. 5.0 stars with 290 reviews. Exclusive private parasail flight for your group near Siesta Key.'
  },
]

existing_links = [o.get('link','') for o in ops]
added = []
for o in new_ops:
    slug = o['link'].split('/embeds/book/')[1].split('/')[0]
    item_id = o['link'].split('/items/')[1].split('/')[0]
    check = f"{slug}/items/{item_id}"
    if any(check in x for x in existing_links):
        print(f"SKIP {o['id']} {o['name']}")
    else:
        ops.append(o)
        added.append(o)
        print(f"ADD {o['id']} {o['name']}")

print(f"\nTotal: {len(ops)}, Added: {len(added)}")
with open(f'{BASE}/operators.json', 'w') as f:
    json.dump(ops, f, indent=2)
slim = [{k:v for k,v in o.items() if k != 'desc'} for o in ops]
with open(f'{BASE}/operators-slim.json', 'w') as f:
    json.dump(slim, f, indent=2)
print("Saved.")

pages = [
    {
        'id': 'b586',
        'filename': 'code-blue-fishing-dolphin-cruise-fort-walton-beach-florida.html',
        'title': 'Code Blue Fishing Dolphin Cruise | Fort Walton Beach FL',
        'meta': 'Dolphin cruise along the Fort Walton Beach coastline with expert guides. From $350. Rated 5.0 stars with 146 reviews. Spot wild dolphins in Choctawhatchee Bay, Florida Panhandle.',
        'og_url': 'https://miamijetski.com/code-blue-fishing-dolphin-cruise-fort-walton-beach-florida',
        'name': 'Code Blue Fishing - Dolphin Cruise',
        'addr': 'Fort Walton Beach, FL 32548', 'city': 'Fort Walton Beach',
        'price': '$350', 'rating': '5.0',
        'photo': 'https://cdn.filestackcontent.com/YfOcxbaS2CeEKSxeEp0w/convert?cache=true&compress=true&quality=90&format=webp&rotate=exif&w=1000&fit=max',
        'og_photo': 'https://cdn.filestackcontent.com/rotate=deg:exif/resize=width:1200/quality=value:85/auto_image/compress/cache=expiry:max/YfOcxbaS2CeEKSxeEp0w',
        'link': 'https://fareharbor.com/embeds/book/codebluefishingcharters/items/399810/calendar/2026/05/?asn=fhdn&asn-ref=miamistylerentals&ref=miamistylerentals&marketplace=yes&flow=no&full-items=yes',
        'lat': '30.428408', 'lng': '-86.607397',
    },
    {
        'id': 'b587',
        'filename': 'next-level-jet-ski-rentals-sarasota-florida.html',
        'title': 'Next Level Jet Ski Rentals | Sarasota FL Waverunner Rental',
        'meta': 'Jet ski rentals on Sarasota Bay near Siesta Key with nearly 1,000 five-star reviews. From $120. Rated 4.9 stars with 950 reviews. Ride the crystal-clear Gulf Coast waters today.',
        'og_url': 'https://miamijetski.com/next-level-jet-ski-rentals-sarasota-florida',
        'name': 'Next Level Jet Ski - Sarasota',
        'addr': 'Sarasota, FL 34231', 'city': 'Sarasota',
        'price': '$120', 'rating': '4.9',
        'photo': 'https://cdn.filestackcontent.com/fBBveVWMS3i4t2QORBco/convert?cache=true&compress=true&quality=90&format=webp&rotate=exif&w=1000&fit=max',
        'og_photo': 'https://cdn.filestackcontent.com/rotate=deg:exif/resize=width:1200/quality=value:85/auto_image/compress/cache=expiry:max/fBBveVWMS3i4t2QORBco',
        'link': 'https://fareharbor.com/embeds/book/nextleveljetstkirental/items/442018/calendar/2026/05/?asn=fhdn&asn-ref=miamistylerentals&ref=miamistylerentals&marketplace=yes&flow=no&full-items=yes',
        'lat': '27.345649', 'lng': '-82.547617',
    },
    {
        'id': 'b588',
        'filename': 'parasail-low-tide-private-parasailing-sarasota-florida.html',
        'title': 'Parasail Low Tide Private Parasailing | Sarasota FL',
        'meta': 'Private parasailing experience over the turquoise waters of Sarasota Bay. From $599. Rated 5.0 stars with 290 reviews. Exclusive private parasail flight near Siesta Key, Florida.',
        'og_url': 'https://miamijetski.com/parasail-low-tide-private-parasailing-sarasota-florida',
        'name': 'Parasail Low Tide - Private Parasailing Sarasota',
        'addr': 'Sarasota, FL 34231', 'city': 'Sarasota',
        'price': '$599', 'rating': '5.0',
        'photo': 'https://cdn.filestackcontent.com/baP41cZTR9anA2EvIVAg/convert?cache=true&compress=true&quality=90&format=webp&rotate=exif&w=1000&fit=max',
        'og_photo': 'https://cdn.filestackcontent.com/rotate=deg:exif/resize=width:1200/quality=value:85/auto_image/compress/cache=expiry:max/baP41cZTR9anA2EvIVAg',
        'link': 'https://fareharbor.com/embeds/book/parasaillowtide/items/530320/calendar/2026/05/?asn=fhdn&asn-ref=miamistylerentals&ref=miamistylerentals&marketplace=yes&flow=no&full-items=yes',
        'lat': '27.332245', 'lng': '-82.58035',
    },
]

print()
for p in pages:
    html = tmpl
    html = re.sub(r'<title>[^<]+</title>', '<title>' + p['title'] + '</title>', html)
    html = re.sub(r'<meta name="description"[^>]+>', '<meta name="description" content="' + p['meta'] + '">', html)
    html = re.sub(r'<meta property="og:title"[^>]+>', '<meta property="og:title" content="' + p['title'] + '">', html)
    html = re.sub(r'<meta property="og:description"[^>]+>', '<meta property="og:description" content="' + p['meta'] + '">', html)
    html = re.sub(r'<meta property="og:url"[^>]+>', '<meta property="og:url" content="' + p['og_url'] + '">', html)
    html = re.sub(r'<meta property="og:image"[^>]+>', '<meta property="og:image" content="' + p['og_photo'] + '">', html)
    html = html.replace('Cudjoe Key Boat Rentals', p['name'])
    html = html.replace('119 Blimp Rd, Cudjoe Key, FL 33042', p['addr'])
    html = html.replace('Cudjoe Key', p['city'])
    html = re.sub(r'\$300', p['price'], html)
    html = html.replace('>4.9<', '>' + p['rating'] + '<')
    html = re.sub(r'https://cdn\.filestackcontent\.com/[A-Za-z0-9]{15,}/convert[^"\'<\s]*', p['photo'], html)
    html = re.sub(r'https://cdn\.filestackcontent\.com/rotate=deg:exif/resize=width:1200[^"\'<\s]*', p['og_photo'], html)
    html = re.sub(r'https://fareharbor\.com/embeds/book/[^"\'<\s]*', p['link'], html)
    html = html.replace('24.6694', p['lat'])
    html = html.replace('-81.4937', p['lng'])
    with open(f"{BASE}/{p['filename']}", 'w') as f:
        f.write(html)
    print(f"Generated: {p['filename']}")

new_urls = [
    'https://miamijetski.com/code-blue-fishing-dolphin-cruise-fort-walton-beach-florida',
    'https://miamijetski.com/next-level-jet-ski-rentals-sarasota-florida',
    'https://miamijetski.com/parasail-low-tide-private-parasailing-sarasota-florida',
]
with open(f'{BASE}/sitemap.xml') as f:
    sitemap = f.read()
before = sitemap.count('<loc>')
for url in new_urls:
    if url not in sitemap:
        entry = f'  <url>\n    <loc>{url}</loc>\n    <changefreq>monthly</changefreq>\n    <priority>0.7</priority>\n  </url>\n'
        sitemap = sitemap.replace('</urlset>', entry + '</urlset>')
with open(f'{BASE}/sitemap.xml', 'w') as f:
    f.write(sitemap)
print(f"\nSitemap: {before} → {sitemap.count('<loc>')} URLs")
