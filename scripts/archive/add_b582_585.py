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
    'id': 'b582',
    'name': 'Breezy Tiki - Four Hour Charter',
    'addr': '1440 N Federal Hwy, Fort Lauderdale, FL 33304',
    'zone': 'ftlauderdale', 'zl': 'Fort Lauderdale', 'cat': 'to',
    'price': 880, 'lat': 26.124146, 'lng': -80.103833,
    'photo': 'oSWdRJ2ESheS6nO0QgIO',
    'link': 'https://fareharbor.com/embeds/book/breezytiki/items/98492/calendar/2026/05/?asn=fhdn&asn-ref=miamistylerentals&ref=miamistylerentals&marketplace=yes&flow=no&full-items=yes',
    'badge': 'top', 'rating': 4.9, 'reviews': 459,
    'desc': 'Four-hour private tiki boat charter through Fort Lauderdale waterways and Intracoastal. From $880. 4.9 stars with 459 reviews. Perfect for birthdays, bachelorettes, and group outings.'
  },
  {
    'id': 'b583',
    'name': 'Breezy Tiki - Two Hour Charter',
    'addr': '1440 N Federal Hwy, Fort Lauderdale, FL 33304',
    'zone': 'ftlauderdale', 'zl': 'Fort Lauderdale', 'cat': 'to',
    'price': 550, 'lat': 26.124146, 'lng': -80.103833,
    'photo': '3g7L5ChhTZeIZRWUfEg6',
    'link': 'https://fareharbor.com/embeds/book/breezytiki/items/138798/calendar/2026/05/?asn=fhdn&asn-ref=miamistylerentals&ref=miamistylerentals&marketplace=yes&flow=no&full-items=yes',
    'badge': 'top', 'rating': 4.9, 'reviews': 517,
    'desc': 'Two-hour private tiki boat charter on the Fort Lauderdale Intracoastal Waterway. From $550. 4.9 stars with 517 reviews. Quick and fun floating tiki party for small groups.'
  },
  {
    'id': 'b584',
    'name': 'Banyan Charters - Shelling & Dolphin Tour',
    'addr': 'Marco Island, FL 34145',
    'zone': 'naples', 'zl': 'Marco Island', 'cat': 'to',
    'price': 550, 'lat': 25.912532, 'lng': -81.716967,
    'photo': 'qZexCr5Q5qTooOFR5YyA',
    'link': 'https://fareharbor.com/embeds/book/banyancharters/items/138610/calendar/2026/05/?asn=fhdn&asn-ref=miamistylerentals&ref=miamistylerentals&marketplace=yes&flow=no&full-items=yes',
    'badge': 'top', 'rating': 5.0, 'reviews': 360,
    'desc': 'Shelling and dolphin tour from Marco Island through the Ten Thousand Islands. From $550. 5.0 stars with 360 reviews. Collect rare shells and spot dolphins in Southwest Florida.'
  },
  {
    'id': 'b585',
    'name': 'Charter Finders - Private Dolphin Shelling Cruise',
    'addr': 'Madeira Beach, FL 33708',
    'zone': 'tampa', 'zl': 'Madeira Beach', 'cat': 'to',
    'price': 354, 'lat': 27.7883, 'lng': -82.7856,
    'photo': 'EoEIRg0pRcq8fQAetEJi',
    'link': 'https://fareharbor.com/embeds/book/charterfinders/items/291158/calendar/2026/05/?asn=fhdn&asn-ref=miamistylerentals&ref=miamistylerentals&marketplace=yes&flow=no&full-items=yes',
    'badge': 'top', 'rating': 4.9, 'reviews': 426,
    'desc': 'Private dolphin shelling snorkeling cruise from Madeira Beach on the Gulf Coast. From $354. 4.9 stars with 426 reviews. Exclusive private boat for your group on the Gulf of Mexico.'
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
        'id': 'b582',
        'filename': 'breezy-tiki-four-hour-charter-fort-lauderdale-florida.html',
        'title': 'Breezy Tiki Four Hour Charter | Fort Lauderdale Tiki Boat FL',
        'meta': 'Four-hour private tiki boat charter on Fort Lauderdale Intracoastal Waterway. From $880. Rated 4.9 stars with 459 reviews. Perfect for birthdays, bachelorettes, and group outings.',
        'og_url': 'https://miamijetski.com/breezy-tiki-four-hour-charter-fort-lauderdale-florida',
        'name': 'Breezy Tiki - Four Hour Charter',
        'addr': '1440 N Federal Hwy, Fort Lauderdale, FL 33304', 'city': 'Fort Lauderdale',
        'price': '$880', 'rating': '4.9',
        'photo': 'https://cdn.filestackcontent.com/oSWdRJ2ESheS6nO0QgIO/convert?cache=true&compress=true&quality=90&format=webp&rotate=exif&w=1000&fit=max',
        'og_photo': 'https://cdn.filestackcontent.com/rotate=deg:exif/resize=width:1200/quality=value:85/auto_image/compress/cache=expiry:max/oSWdRJ2ESheS6nO0QgIO',
        'link': 'https://fareharbor.com/embeds/book/breezytiki/items/98492/calendar/2026/05/?asn=fhdn&asn-ref=miamistylerentals&ref=miamistylerentals&marketplace=yes&flow=no&full-items=yes',
        'lat': '26.124146', 'lng': '-80.103833',
    },
    {
        'id': 'b583',
        'filename': 'breezy-tiki-two-hour-charter-fort-lauderdale-florida.html',
        'title': 'Breezy Tiki Two Hour Charter | Fort Lauderdale Tiki Boat FL',
        'meta': 'Two-hour private tiki boat charter on the Fort Lauderdale Intracoastal. From $550. Rated 4.9 stars with 517 reviews. Quick and fun floating tiki party for small groups in Fort Lauderdale.',
        'og_url': 'https://miamijetski.com/breezy-tiki-two-hour-charter-fort-lauderdale-florida',
        'name': 'Breezy Tiki - Two Hour Charter',
        'addr': '1440 N Federal Hwy, Fort Lauderdale, FL 33304', 'city': 'Fort Lauderdale',
        'price': '$550', 'rating': '4.9',
        'photo': 'https://cdn.filestackcontent.com/3g7L5ChhTZeIZRWUfEg6/convert?cache=true&compress=true&quality=90&format=webp&rotate=exif&w=1000&fit=max',
        'og_photo': 'https://cdn.filestackcontent.com/rotate=deg:exif/resize=width:1200/quality=value:85/auto_image/compress/cache=expiry:max/3g7L5ChhTZeIZRWUfEg6',
        'link': 'https://fareharbor.com/embeds/book/breezytiki/items/138798/calendar/2026/05/?asn=fhdn&asn-ref=miamistylerentals&ref=miamistylerentals&marketplace=yes&flow=no&full-items=yes',
        'lat': '26.124146', 'lng': '-80.103833',
    },
    {
        'id': 'b584',
        'filename': 'banyan-charters-shelling-dolphin-tour-marco-island-florida.html',
        'title': 'Banyan Charters Shelling & Dolphin Tour | Marco Island FL',
        'meta': 'Shelling and dolphin tour from Marco Island through the Ten Thousand Islands. From $550. Rated 5.0 stars with 360 reviews. Collect rare shells and spot dolphins in Southwest Florida.',
        'og_url': 'https://miamijetski.com/banyan-charters-shelling-dolphin-tour-marco-island-florida',
        'name': 'Banyan Charters - Shelling & Dolphin Tour',
        'addr': 'Marco Island, FL 34145', 'city': 'Marco Island',
        'price': '$550', 'rating': '5.0',
        'photo': 'https://cdn.filestackcontent.com/qZexCr5Q5qTooOFR5YyA/convert?cache=true&compress=true&quality=90&format=webp&rotate=exif&w=1000&fit=max',
        'og_photo': 'https://cdn.filestackcontent.com/rotate=deg:exif/resize=width:1200/quality=value:85/auto_image/compress/cache=expiry:max/qZexCr5Q5qTooOFR5YyA',
        'link': 'https://fareharbor.com/embeds/book/banyancharters/items/138610/calendar/2026/05/?asn=fhdn&asn-ref=miamistylerentals&ref=miamistylerentals&marketplace=yes&flow=no&full-items=yes',
        'lat': '25.912532', 'lng': '-81.716967',
    },
    {
        'id': 'b585',
        'filename': 'charter-finders-private-dolphin-shelling-cruise-madeira-beach-florida.html',
        'title': 'Charter Finders Private Dolphin Shelling Cruise | Madeira Beach FL',
        'meta': 'Private dolphin shelling snorkeling cruise from Madeira Beach on the Gulf Coast. From $354. Rated 4.9 stars with 426 reviews. Exclusive private boat for your group on the Gulf.',
        'og_url': 'https://miamijetski.com/charter-finders-private-dolphin-shelling-cruise-madeira-beach-florida',
        'name': 'Charter Finders - Private Dolphin Shelling Cruise',
        'addr': 'Madeira Beach, FL 33708', 'city': 'Madeira Beach',
        'price': '$354', 'rating': '4.9',
        'photo': 'https://cdn.filestackcontent.com/EoEIRg0pRcq8fQAetEJi/convert?cache=true&compress=true&quality=90&format=webp&rotate=exif&w=1000&fit=max',
        'og_photo': 'https://cdn.filestackcontent.com/rotate=deg:exif/resize=width:1200/quality=value:85/auto_image/compress/cache=expiry:max/EoEIRg0pRcq8fQAetEJi',
        'link': 'https://fareharbor.com/embeds/book/charterfinders/items/291158/calendar/2026/05/?asn=fhdn&asn-ref=miamistylerentals&ref=miamistylerentals&marketplace=yes&flow=no&full-items=yes',
        'lat': '27.7883', 'lng': '-82.7856',
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
    'https://miamijetski.com/breezy-tiki-four-hour-charter-fort-lauderdale-florida',
    'https://miamijetski.com/breezy-tiki-two-hour-charter-fort-lauderdale-florida',
    'https://miamijetski.com/banyan-charters-shelling-dolphin-tour-marco-island-florida',
    'https://miamijetski.com/charter-finders-private-dolphin-shelling-cruise-madeira-beach-florida',
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
