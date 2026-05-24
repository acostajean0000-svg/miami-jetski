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
    'id': 'b577',
    'name': 'Discover ELC - Kayak & Paddleboard Rentals',
    'addr': 'Vero Beach, FL 32963',
    'zone': 'eastcoast', 'zl': 'Vero Beach', 'cat': 'to',
    'price': 35, 'lat': 27.757658, 'lng': -80.415881,
    'photo': 'jPj8yiyWSFe6ZTsnGODG',
    'link': 'https://fareharbor.com/embeds/book/discoverelc/items/490334/calendar/2026/05/?asn=fhdn&asn-ref=miamistylerentals&ref=miamistylerentals&marketplace=yes&flow=no&full-items=yes',
    'badge': 'top', 'rating': 4.8, 'reviews': 390,
    'desc': 'Kayak, paddleboard, and canoe rentals on the Indian River Lagoon in Vero Beach. From $35. 4.8 stars with 390 reviews. Explore Florida\'s Treasure Coast waterways at your own pace.'
  },
  {
    'id': 'b578',
    'name': 'CBS Outfitters - 20ft Pontoon Rental Siesta Key',
    'addr': 'Siesta Key, FL 34242',
    'zone': 'gulf', 'zl': 'Siesta Key', 'cat': 'boat',
    'price': 349, 'lat': 27.25263, 'lng': -82.534017,
    'photo': 'hihc4NnUQNSFRXKLtz7t',
    'link': 'https://fareharbor.com/embeds/book/cbsoutfitters/items/529696/calendar/2026/05/?asn=fhdn&asn-ref=miamistylerentals&ref=miamistylerentals&marketplace=yes&flow=no&full-items=yes',
    'badge': 'top', 'rating': 4.8, 'reviews': 1021,
    'desc': 'Rent a 20-foot Berkshire pontoon boat for 4 hours on the waters of Siesta Key. From $349. 4.8 stars with 1,021 reviews. Cruise the Gulf-side waters near one of Florida\'s top beaches.'
  },
  {
    'id': 'b579',
    'name': 'CBS Outfitters - 27ft Pontoon Rental Siesta Key',
    'addr': 'Siesta Key, FL 34242',
    'zone': 'gulf', 'zl': 'Siesta Key', 'cat': 'boat',
    'price': 449, 'lat': 27.25263, 'lng': -82.534017,
    'photo': 'D52SfhvLTvGmXOcl1tnd',
    'link': 'https://fareharbor.com/embeds/book/cbsoutfitters/items/529702/calendar/2026/05/?asn=fhdn&asn-ref=miamistylerentals&ref=miamistylerentals&marketplace=yes&flow=no&full-items=yes',
    'badge': 'top', 'rating': 4.8, 'reviews': 1049,
    'desc': 'Rent a large 27-foot Berkshire pontoon boat for 4 hours near Siesta Key. From $449. 4.8 stars with 1,049 reviews. Spacious pontoon for larger groups on Sarasota\'s Gulf waters.'
  },
  {
    'id': 'b580',
    'name': 'Vero Tackle - Round Island Single Kayak',
    'addr': 'Vero Beach, FL 32960',
    'zone': 'eastcoast', 'zl': 'Vero Beach', 'cat': 'to',
    'price': 30, 'lat': 27.563824, 'lng': -80.329952,
    'photo': 'f5QQrRAySK2IlljWl863',
    'link': 'https://fareharbor.com/embeds/book/verotackle/items/640350/calendar/2026/05/?asn=fhdn&asn-ref=miamistylerentals&ref=miamistylerentals&marketplace=yes&flow=no&full-items=yes',
    'badge': 'top', 'rating': 4.9, 'reviews': 1022,
    'desc': 'Single kayak rental at Round Island in Vero Beach on Florida\'s Treasure Coast. From $30. 4.9 stars with 1,022 reviews. Paddle the peaceful Indian River Lagoon ecosystem.'
  },
  {
    'id': 'b581',
    'name': 'Vero Tackle - Round Island Tandem Kayak',
    'addr': 'Vero Beach, FL 32960',
    'zone': 'eastcoast', 'zl': 'Vero Beach', 'cat': 'to',
    'price': 40, 'lat': 27.563824, 'lng': -80.329952,
    'photo': 'CsH1ZW5WQQKMaCCD4liJ',
    'link': 'https://fareharbor.com/embeds/book/verotackle/items/640351/calendar/2026/05/?asn=fhdn&asn-ref=miamistylerentals&ref=miamistylerentals&marketplace=yes&flow=no&full-items=yes',
    'badge': 'top', 'rating': 4.9, 'reviews': 1015,
    'desc': 'Tandem kayak rental for two at Round Island in Vero Beach on Florida\'s Treasure Coast. From $40. 4.9 stars with 1,015 reviews. Explore the Indian River Lagoon together.'
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
        'id': 'b577',
        'filename': 'discover-elc-kayak-paddleboard-rentals-vero-beach-florida.html',
        'title': 'Discover ELC Kayak & Paddleboard Rentals | Vero Beach FL',
        'meta': 'Kayak, paddleboard, and canoe rentals on the Indian River Lagoon in Vero Beach. From $35. Rated 4.8 stars with 390 reviews. Explore the Treasure Coast waterways at your own pace.',
        'og_url': 'https://miamijetski.com/discover-elc-kayak-paddleboard-rentals-vero-beach-florida',
        'name': 'Discover ELC - Kayak & Paddleboard Rentals',
        'addr': 'Vero Beach, FL 32963', 'city': 'Vero Beach',
        'price': '$35', 'rating': '4.8',
        'photo': 'https://cdn.filestackcontent.com/jPj8yiyWSFe6ZTsnGODG/convert?cache=true&compress=true&quality=90&format=webp&rotate=exif&w=1000&fit=max',
        'og_photo': 'https://cdn.filestackcontent.com/rotate=deg:exif/resize=width:1200/quality=value:85/auto_image/compress/cache=expiry:max/jPj8yiyWSFe6ZTsnGODG',
        'link': 'https://fareharbor.com/embeds/book/discoverelc/items/490334/calendar/2026/05/?asn=fhdn&asn-ref=miamistylerentals&ref=miamistylerentals&marketplace=yes&flow=no&full-items=yes',
        'lat': '27.757658', 'lng': '-80.415881',
    },
    {
        'id': 'b578',
        'filename': 'cbs-outfitters-20ft-pontoon-rental-siesta-key-florida.html',
        'title': 'CBS Outfitters 20ft Pontoon Boat Rental | Siesta Key FL',
        'meta': 'Rent a 20-foot Berkshire pontoon boat for 4 hours near Siesta Key, FL. From $349. Rated 4.8 stars with 1,021 reviews. Cruise Gulf-side waters near one of Florida\'s top beaches.',
        'og_url': 'https://miamijetski.com/cbs-outfitters-20ft-pontoon-rental-siesta-key-florida',
        'name': 'CBS Outfitters - 20ft Pontoon Rental',
        'addr': 'Siesta Key, FL 34242', 'city': 'Siesta Key',
        'price': '$349', 'rating': '4.8',
        'photo': 'https://cdn.filestackcontent.com/hihc4NnUQNSFRXKLtz7t/convert?cache=true&compress=true&quality=90&format=webp&rotate=exif&w=1000&fit=max',
        'og_photo': 'https://cdn.filestackcontent.com/rotate=deg:exif/resize=width:1200/quality=value:85/auto_image/compress/cache=expiry:max/hihc4NnUQNSFRXKLtz7t',
        'link': 'https://fareharbor.com/embeds/book/cbsoutfitters/items/529696/calendar/2026/05/?asn=fhdn&asn-ref=miamistylerentals&ref=miamistylerentals&marketplace=yes&flow=no&full-items=yes',
        'lat': '27.25263', 'lng': '-82.534017',
    },
    {
        'id': 'b579',
        'filename': 'cbs-outfitters-27ft-pontoon-rental-siesta-key-florida.html',
        'title': 'CBS Outfitters 27ft Pontoon Boat Rental | Siesta Key Sarasota FL',
        'meta': 'Rent a large 27-foot Berkshire pontoon for 4 hours near Siesta Key. From $449. Rated 4.8 stars with 1,049 reviews. Spacious pontoon rental near Sarasota\'s Gulf Coast beaches.',
        'og_url': 'https://miamijetski.com/cbs-outfitters-27ft-pontoon-rental-siesta-key-florida',
        'name': 'CBS Outfitters - 27ft Pontoon Rental',
        'addr': 'Siesta Key, FL 34242', 'city': 'Siesta Key',
        'price': '$449', 'rating': '4.8',
        'photo': 'https://cdn.filestackcontent.com/D52SfhvLTvGmXOcl1tnd/convert?cache=true&compress=true&quality=90&format=webp&rotate=exif&w=1000&fit=max',
        'og_photo': 'https://cdn.filestackcontent.com/rotate=deg:exif/resize=width:1200/quality=value:85/auto_image/compress/cache=expiry:max/D52SfhvLTvGmXOcl1tnd',
        'link': 'https://fareharbor.com/embeds/book/cbsoutfitters/items/529702/calendar/2026/05/?asn=fhdn&asn-ref=miamistylerentals&ref=miamistylerentals&marketplace=yes&flow=no&full-items=yes',
        'lat': '27.25263', 'lng': '-82.534017',
    },
    {
        'id': 'b580',
        'filename': 'vero-tackle-round-island-single-kayak-vero-beach-florida.html',
        'title': 'Vero Tackle Round Island Kayak Rental | Vero Beach FL',
        'meta': 'Single kayak rental at Round Island on the Indian River Lagoon in Vero Beach. From $30. Rated 4.9 stars with 1,022 reviews. Paddle Florida\'s Treasure Coast at your own pace.',
        'og_url': 'https://miamijetski.com/vero-tackle-round-island-single-kayak-vero-beach-florida',
        'name': 'Vero Tackle - Round Island Single Kayak',
        'addr': 'Vero Beach, FL 32960', 'city': 'Vero Beach',
        'price': '$30', 'rating': '4.9',
        'photo': 'https://cdn.filestackcontent.com/f5QQrRAySK2IlljWl863/convert?cache=true&compress=true&quality=90&format=webp&rotate=exif&w=1000&fit=max',
        'og_photo': 'https://cdn.filestackcontent.com/rotate=deg:exif/resize=width:1200/quality=value:85/auto_image/compress/cache=expiry:max/f5QQrRAySK2IlljWl863',
        'link': 'https://fareharbor.com/embeds/book/verotackle/items/640350/calendar/2026/05/?asn=fhdn&asn-ref=miamistylerentals&ref=miamistylerentals&marketplace=yes&flow=no&full-items=yes',
        'lat': '27.563824', 'lng': '-80.329952',
    },
    {
        'id': 'b581',
        'filename': 'vero-tackle-round-island-tandem-kayak-vero-beach-florida.html',
        'title': 'Vero Tackle Round Island Tandem Kayak | Vero Beach FL',
        'meta': 'Tandem kayak rental for two at Round Island on Vero Beach\'s Indian River Lagoon. From $40. Rated 4.9 stars with 1,015 reviews. Explore the Treasure Coast ecosystem together.',
        'og_url': 'https://miamijetski.com/vero-tackle-round-island-tandem-kayak-vero-beach-florida',
        'name': 'Vero Tackle - Round Island Tandem Kayak',
        'addr': 'Vero Beach, FL 32960', 'city': 'Vero Beach',
        'price': '$40', 'rating': '4.9',
        'photo': 'https://cdn.filestackcontent.com/CsH1ZW5WQQKMaCCD4liJ/convert?cache=true&compress=true&quality=90&format=webp&rotate=exif&w=1000&fit=max',
        'og_photo': 'https://cdn.filestackcontent.com/rotate=deg:exif/resize=width:1200/quality=value:85/auto_image/compress/cache=expiry:max/CsH1ZW5WQQKMaCCD4liJ',
        'link': 'https://fareharbor.com/embeds/book/verotackle/items/640351/calendar/2026/05/?asn=fhdn&asn-ref=miamistylerentals&ref=miamistylerentals&marketplace=yes&flow=no&full-items=yes',
        'lat': '27.563824', 'lng': '-80.329952',
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
    'https://miamijetski.com/discover-elc-kayak-paddleboard-rentals-vero-beach-florida',
    'https://miamijetski.com/cbs-outfitters-20ft-pontoon-rental-siesta-key-florida',
    'https://miamijetski.com/cbs-outfitters-27ft-pontoon-rental-siesta-key-florida',
    'https://miamijetski.com/vero-tackle-round-island-single-kayak-vero-beach-florida',
    'https://miamijetski.com/vero-tackle-round-island-tandem-kayak-vero-beach-florida',
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
