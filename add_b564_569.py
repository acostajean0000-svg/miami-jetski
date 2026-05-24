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
    'id': 'b564',
    'name': 'Destin Tikis - Beach & Cruise',
    'addr': 'Destin, FL 32541',
    'zone': 'destin', 'zl': 'Destin', 'cat': 'to',
    'price': 75, 'lat': 30.392711, 'lng': -86.505577,
    'photo': 'qMj7S3cRTgKovO7m6Xm9',
    'link': 'https://fareharbor.com/embeds/book/destintikis/items/677665/calendar/2026/05/?asn=fhdn&asn-ref=miamistylerentals&ref=miamistylerentals&marketplace=yes&flow=no&full-items=yes',
    'badge': 'top', 'rating': 4.9, 'reviews': 1614,
    'desc': 'Beach and cruise tiki boat experience in Destin with stops along the emerald coast. From $75. 4.9 stars with 1,614 reviews. Floating fun on the Gulf of Mexico.'
  },
  {
    'id': 'b565',
    'name': 'Gulf Coast Expeditions - Manatee Encounter',
    'addr': 'Crystal River, FL 34428',
    'zone': 'crystalriver', 'zl': 'Crystal River', 'cat': 'to',
    'price': 69, 'lat': 28.898261, 'lng': -82.589936,
    'photo': 'yDap9aFQHW8p3BlQdKt6',
    'link': 'https://fareharbor.com/embeds/book/gcexpeditions/items/24619/calendar/2026/05/?asn=fhdn&asn-ref=miamistylerentals&ref=miamistylerentals&marketplace=yes&flow=no&full-items=yes',
    'badge': 'top', 'rating': 5.0, 'reviews': 388,
    'desc': 'Guided manatee encounter tour through the spring-fed waters of Crystal River. From $69. 5.0 stars with 388 reviews. Swim alongside gentle manatees in their natural habitat.'
  },
  {
    'id': 'b566',
    'name': 'River Adventure Tours - Kayak Rental',
    'addr': 'Homosassa, FL 34446',
    'zone': 'crystalriver', 'zl': 'Homosassa', 'cat': 'to',
    'price': 30, 'lat': 28.801656, 'lng': -82.604543,
    'photo': 'GNQde4AR1SxBcZHZfbke',
    'link': 'https://fareharbor.com/embeds/book/riveradventuretours/items/67895/calendar/2026/05/?asn=fhdn&asn-ref=miamistylerentals&ref=miamistylerentals&marketplace=yes&flow=no&full-items=yes',
    'badge': 'top', 'rating': 4.8, 'reviews': 257,
    'desc': 'Kayak rentals on the crystal-clear Homosassa River with manatees, birds, and springs. From $30. 4.8 stars with 257 reviews. Paddle through Florida\'s most pristine river ecosystem.'
  },
  {
    'id': 'b567',
    'name': 'Breezy Tiki - Three Hour Charter',
    'addr': '1440 N Federal Hwy, Fort Lauderdale, FL 33304',
    'zone': 'ftlauderdale', 'zl': 'Fort Lauderdale', 'cat': 'to',
    'price': 675, 'lat': 26.124146, 'lng': -80.103833,
    'photo': 'WiSaniaTne8aJRNG2M8A',
    'link': 'https://fareharbor.com/embeds/book/breezytiki/items/149043/calendar/2026/05/?asn=fhdn&asn-ref=miamistylerentals&ref=miamistylerentals&marketplace=yes&flow=no&full-items=yes',
    'badge': 'top', 'rating': 4.9, 'reviews': 517,
    'desc': 'Three-hour private tiki boat charter through Fort Lauderdale waterways. From $675. 4.9 stars with 517 reviews. Perfect for small groups and celebrations on the Intracoastal.'
  },
  {
    'id': 'b568',
    'name': 'Manatee Kayaking Company - Guided Tour',
    'addr': 'Fort Myers, FL 33908',
    'zone': 'naples', 'zl': 'Fort Myers', 'cat': 'to',
    'price': 45, 'lat': 26.693277, 'lng': -81.777406,
    'photo': 'BeWHMDASeuH6wYli0UxK',
    'link': 'https://fareharbor.com/embeds/book/manateekayakingcompany/items/229087/calendar/2026/05/?asn=fhdn&asn-ref=miamistylerentals&ref=miamistylerentals&marketplace=yes&flow=no&full-items=yes',
    'badge': 'top', 'rating': 4.8, 'reviews': 260,
    'desc': 'Guided kayak tour with manatees through the warm waters of Fort Myers. From $45. 4.8 stars with 260 reviews. Get up-close with Florida manatees by kayak.'
  },
  {
    'id': 'b569',
    'name': 'Reef Quest Eco Boat Tours - Two Hour Tour',
    'addr': 'Islamorada, FL 33036',
    'zone': 'keywest', 'zl': 'Islamorada', 'cat': 'to',
    'price': 300, 'lat': 24.91566, 'lng': -80.640483,
    'photo': '2JVORceSAaS3WxgEyipk',
    'link': 'https://fareharbor.com/embeds/book/reefquesttours/items/281731/calendar/2026/05/?asn=fhdn&asn-ref=miamistylerentals&ref=miamistylerentals&marketplace=yes&flow=no&full-items=yes',
    'badge': 'top', 'rating': 5.0, 'reviews': 100,
    'desc': 'Two-hour eco boat tour through the coral reefs and mangroves of Islamorada. From $300. 5.0 stars with 100 reviews. Spot marine life in the Florida Keys backcountry.'
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
print("Saved operators.json and operators-slim.json")

# Generate HTML pages
pages = [
    {
        'id': 'b564',
        'filename': 'destin-tikis-beach-cruise-destin-florida.html',
        'title': 'Destin Tikis Beach & Cruise | Tiki Boat Destin FL',
        'meta': 'Beach and cruise tiki boat experience in Destin with stops along the emerald coast. From $75. Rated 4.9 stars with 1,614 reviews. Book your Destin tiki boat beach cruise today.',
        'og_url': 'https://miamijetski.com/destin-tikis-beach-cruise-destin-florida',
        'name': 'Destin Tikis - Beach & Cruise',
        'addr': 'Destin, FL 32541', 'city': 'Destin',
        'price': '$75', 'rating': '4.9',
        'photo': 'https://cdn.filestackcontent.com/qMj7S3cRTgKovO7m6Xm9/convert?cache=true&compress=true&quality=90&format=webp&rotate=exif&w=1000&fit=max',
        'og_photo': 'https://cdn.filestackcontent.com/rotate=deg:exif/resize=width:1200/quality=value:85/auto_image/compress/cache=expiry:max/qMj7S3cRTgKovO7m6Xm9',
        'link': 'https://fareharbor.com/embeds/book/destintikis/items/677665/calendar/2026/05/?asn=fhdn&asn-ref=miamistylerentals&ref=miamistylerentals&marketplace=yes&flow=no&full-items=yes',
        'lat': '30.392711', 'lng': '-86.505577',
    },
    {
        'id': 'b565',
        'filename': 'gulf-coast-expeditions-manatee-encounter-crystal-river-florida.html',
        'title': 'Gulf Coast Expeditions Manatee Encounter | Crystal River FL',
        'meta': 'Guided manatee encounter tour through Crystal River spring-fed waters. From $69. Rated 5.0 stars with 388 reviews. Swim alongside manatees in their natural habitat.',
        'og_url': 'https://miamijetski.com/gulf-coast-expeditions-manatee-encounter-crystal-river-florida',
        'name': 'Gulf Coast Expeditions - Manatee Encounter',
        'addr': 'Crystal River, FL 34428', 'city': 'Crystal River',
        'price': '$69', 'rating': '5.0',
        'photo': 'https://cdn.filestackcontent.com/yDap9aFQHW8p3BlQdKt6/convert?cache=true&compress=true&quality=90&format=webp&rotate=exif&w=1000&fit=max',
        'og_photo': 'https://cdn.filestackcontent.com/rotate=deg:exif/resize=width:1200/quality=value:85/auto_image/compress/cache=expiry:max/yDap9aFQHW8p3BlQdKt6',
        'link': 'https://fareharbor.com/embeds/book/gcexpeditions/items/24619/calendar/2026/05/?asn=fhdn&asn-ref=miamistylerentals&ref=miamistylerentals&marketplace=yes&flow=no&full-items=yes',
        'lat': '28.898261', 'lng': '-82.589936',
    },
    {
        'id': 'b566',
        'filename': 'river-adventure-tours-kayak-rental-homosassa-florida.html',
        'title': 'River Adventure Tours Kayak Rental | Homosassa FL Kayak Tours',
        'meta': 'Kayak rentals on the crystal-clear Homosassa River with manatees and springs. From $30. Rated 4.8 stars with 257 reviews. Paddle Florida\'s pristine river ecosystem.',
        'og_url': 'https://miamijetski.com/river-adventure-tours-kayak-rental-homosassa-florida',
        'name': 'River Adventure Tours - Kayak Rental',
        'addr': 'Homosassa, FL 34446', 'city': 'Homosassa',
        'price': '$30', 'rating': '4.8',
        'photo': 'https://cdn.filestackcontent.com/GNQde4AR1SxBcZHZfbke/convert?cache=true&compress=true&quality=90&format=webp&rotate=exif&w=1000&fit=max',
        'og_photo': 'https://cdn.filestackcontent.com/rotate=deg:exif/resize=width:1200/quality=value:85/auto_image/compress/cache=expiry:max/GNQde4AR1SxBcZHZfbke',
        'link': 'https://fareharbor.com/embeds/book/riveradventuretours/items/67895/calendar/2026/05/?asn=fhdn&asn-ref=miamistylerentals&ref=miamistylerentals&marketplace=yes&flow=no&full-items=yes',
        'lat': '28.801656', 'lng': '-82.604543',
    },
    {
        'id': 'b567',
        'filename': 'breezy-tiki-three-hour-charter-fort-lauderdale-florida.html',
        'title': 'Breezy Tiki Three Hour Charter | Fort Lauderdale Tiki Boat FL',
        'meta': 'Three-hour private tiki boat charter through Fort Lauderdale waterways. From $675. Rated 4.9 stars with 517 reviews. Perfect for groups on the Intracoastal Waterway.',
        'og_url': 'https://miamijetski.com/breezy-tiki-three-hour-charter-fort-lauderdale-florida',
        'name': 'Breezy Tiki - Three Hour Charter',
        'addr': '1440 N Federal Hwy, Fort Lauderdale, FL 33304', 'city': 'Fort Lauderdale',
        'price': '$675', 'rating': '4.9',
        'photo': 'https://cdn.filestackcontent.com/WiSaniaTne8aJRNG2M8A/convert?cache=true&compress=true&quality=90&format=webp&rotate=exif&w=1000&fit=max',
        'og_photo': 'https://cdn.filestackcontent.com/rotate=deg:exif/resize=width:1200/quality=value:85/auto_image/compress/cache=expiry:max/WiSaniaTne8aJRNG2M8A',
        'link': 'https://fareharbor.com/embeds/book/breezytiki/items/149043/calendar/2026/05/?asn=fhdn&asn-ref=miamistylerentals&ref=miamistylerentals&marketplace=yes&flow=no&full-items=yes',
        'lat': '26.124146', 'lng': '-80.103833',
    },
    {
        'id': 'b568',
        'filename': 'manatee-kayaking-company-guided-tour-fort-myers-florida.html',
        'title': 'Manatee Kayaking Company Guided Tour | Fort Myers FL Kayak Tours',
        'meta': 'Guided kayak tour with manatees through the warm waters of Fort Myers. From $45. Rated 4.8 stars with 260 reviews. Get up-close with Florida manatees by kayak.',
        'og_url': 'https://miamijetski.com/manatee-kayaking-company-guided-tour-fort-myers-florida',
        'name': 'Manatee Kayaking Company - Guided Tour',
        'addr': 'Fort Myers, FL 33908', 'city': 'Fort Myers',
        'price': '$45', 'rating': '4.8',
        'photo': 'https://cdn.filestackcontent.com/BeWHMDASeuH6wYli0UxK/convert?cache=true&compress=true&quality=90&format=webp&rotate=exif&w=1000&fit=max',
        'og_photo': 'https://cdn.filestackcontent.com/rotate=deg:exif/resize=width:1200/quality=value:85/auto_image/compress/cache=expiry:max/BeWHMDASeuH6wYli0UxK',
        'link': 'https://fareharbor.com/embeds/book/manateekayakingcompany/items/229087/calendar/2026/05/?asn=fhdn&asn-ref=miamistylerentals&ref=miamistylerentals&marketplace=yes&flow=no&full-items=yes',
        'lat': '26.693277', 'lng': '-81.777406',
    },
    {
        'id': 'b569',
        'filename': 'reef-quest-eco-boat-tours-islamorada-florida.html',
        'title': 'Reef Quest Eco Boat Tours | Two Hour Tour Islamorada FL',
        'meta': 'Two-hour eco boat tour through coral reefs and mangroves of Islamorada. From $300. Rated 5.0 stars with 100 reviews. Spot marine life in the Florida Keys backcountry.',
        'og_url': 'https://miamijetski.com/reef-quest-eco-boat-tours-islamorada-florida',
        'name': 'Reef Quest Eco Boat Tours - Two Hour Tour',
        'addr': 'Islamorada, FL 33036', 'city': 'Islamorada',
        'price': '$300', 'rating': '5.0',
        'photo': 'https://cdn.filestackcontent.com/2JVORceSAaS3WxgEyipk/convert?cache=true&compress=true&quality=90&format=webp&rotate=exif&w=1000&fit=max',
        'og_photo': 'https://cdn.filestackcontent.com/rotate=deg:exif/resize=width:1200/quality=value:85/auto_image/compress/cache=expiry:max/2JVORceSAaS3WxgEyipk',
        'link': 'https://fareharbor.com/embeds/book/reefquesttours/items/281731/calendar/2026/05/?asn=fhdn&asn-ref=miamistylerentals&ref=miamistylerentals&marketplace=yes&flow=no&full-items=yes',
        'lat': '24.91566', 'lng': '-80.640483',
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

# Update sitemap
new_urls = [
    'https://miamijetski.com/destin-tikis-beach-cruise-destin-florida',
    'https://miamijetski.com/gulf-coast-expeditions-manatee-encounter-crystal-river-florida',
    'https://miamijetski.com/river-adventure-tours-kayak-rental-homosassa-florida',
    'https://miamijetski.com/breezy-tiki-three-hour-charter-fort-lauderdale-florida',
    'https://miamijetski.com/manatee-kayaking-company-guided-tour-fort-myers-florida',
    'https://miamijetski.com/reef-quest-eco-boat-tours-islamorada-florida',
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
