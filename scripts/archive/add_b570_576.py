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
    'id': 'b570',
    'name': 'Discount Watersports - Waverunner Rental',
    'addr': 'Destin, FL 32541',
    'zone': 'destin', 'zl': 'Destin', 'cat': 'js',
    'price': 95, 'lat': 30.393112, 'lng': -86.503616,
    'photo': '1eDKo3txTgCeg3P41lbJ',
    'link': 'https://fareharbor.com/embeds/book/discountwatersportsdestin/items/315320/calendar/2026/05/?asn=fhdn&asn-ref=miamistylerentals&ref=miamistylerentals&marketplace=yes&flow=no&full-items=yes',
    'badge': 'top', 'rating': 4.9, 'reviews': 1928,
    'desc': 'Waverunner jet ski rentals on the emerald green Gulf of Mexico in Destin. From $95. 4.9 stars with 1,928 reviews. One of Destin\'s most popular watersports rental companies.'
  },
  {
    'id': 'b571',
    'name': 'Islamorada Private Charters - Custom Charter',
    'addr': 'Islamorada, FL 33036',
    'zone': 'keywest', 'zl': 'Islamorada', 'cat': 'to',
    'price': 395, 'lat': 24.914807, 'lng': -80.639718,
    'photo': 'N5upCqQnRpyyJn2VQunW',
    'link': 'https://fareharbor.com/embeds/book/islamoradaprivatecharters/items/339947/calendar/2026/05/?asn=fhdn&asn-ref=miamistylerentals&ref=miamistylerentals&marketplace=yes&flow=no&full-items=yes',
    'badge': 'top', 'rating': 5.0, 'reviews': 250,
    'desc': 'Custom private boat charter through the backcountry of Islamorada in the Florida Keys. From $395. 5.0 stars with 250 reviews. Tailored fishing, snorkeling, and exploration charters.'
  },
  {
    'id': 'b572',
    'name': 'Key West Tiki Boat #1 Rental',
    'addr': '3841 N Roosevelt Blvd, Key West, FL 33040',
    'zone': 'keywest', 'zl': 'Key West', 'cat': 'to',
    'price': 550, 'lat': 24.571092, 'lng': -81.752055,
    'photo': '43QUj9pQSClELC2vWpoQ',
    'link': 'https://fareharbor.com/embeds/book/keywesttikiboat/items/347459/calendar/2026/05/?asn=fhdn&asn-ref=miamistylerentals&ref=miamistylerentals&marketplace=yes&flow=no&full-items=yes',
    'badge': 'top', 'rating': 5.0, 'reviews': 576,
    'desc': 'Rent Tiki Boat #1 in Key West for up to 6 people and cruise warm waters. From $550. 5.0 stars with 576 reviews. Self-captained floating tiki bar rental in paradise.'
  },
  {
    'id': 'b573',
    'name': 'Sandy Toes Boat Charters - Private Charter',
    'addr': 'Gulfport, FL 33707',
    'zone': 'tampa', 'zl': 'Gulfport', 'cat': 'to',
    'price': 250, 'lat': 27.741493, 'lng': -82.69695,
    'photo': 'UrpRrVoHSie8F9bNk1Xm',
    'link': 'https://fareharbor.com/embeds/book/sandytoesboatcharters/items/363507/calendar/2026/05/?asn=fhdn&asn-ref=miamistylerentals&ref=miamistylerentals&marketplace=yes&flow=no&full-items=yes',
    'badge': 'top', 'rating': 5.0, 'reviews': 270,
    'desc': 'Personalized private boat charter out of Gulfport through Tampa Bay and the Gulf. From $250. 5.0 stars with 270 reviews. Customizable cruises for any occasion.'
  },
  {
    'id': 'b574',
    'name': 'Blown Away Airboat Tours - Crystal River',
    'addr': 'Crystal River, FL 34428',
    'zone': 'crystalriver', 'zl': 'Crystal River', 'cat': 'to',
    'price': 51, 'lat': 28.90126, 'lng': -82.645253,
    'photo': 'nqQphlgZQuG0EHFxBfT3',
    'link': 'https://fareharbor.com/embeds/book/blownawayairboattours/items/396593/calendar/2026/05/?asn=fhdn&asn-ref=miamistylerentals&ref=miamistylerentals&marketplace=yes&flow=no&full-items=yes',
    'badge': 'top', 'rating': 4.9, 'reviews': 138,
    'desc': 'Backcountry airboat adventure tours through the wild marshes of Crystal River. From $51. 4.9 stars with 138 reviews. Spot alligators and wildlife on a thrilling airboat ride.'
  },
  {
    'id': 'b575',
    'name': 'Salty Sandbars - Half Day Charter Key West',
    'addr': 'Key West, FL 33040',
    'zone': 'keywest', 'zl': 'Key West', 'cat': 'boat',
    'price': 599, 'lat': 24.560796, 'lng': -81.787414,
    'photo': '9EYWNhVpTOaawqcRfxoS',
    'link': 'https://fareharbor.com/embeds/book/saltysandbars/items/417200/calendar/2026/05/?asn=fhdn&asn-ref=miamistylerentals&ref=miamistylerentals&marketplace=yes&flow=no&full-items=yes',
    'badge': 'top', 'rating': 4.9, 'reviews': 174,
    'desc': 'Half-day 4-hour Boston Whaler charter in Key West for snorkeling and sandbar adventures. From $599. 4.9 stars with 174 reviews. Explore Key West sandbars and reefs at your own pace.'
  },
  {
    'id': 'b576',
    'name': 'Islamorada Private Charters - Snorkeling',
    'addr': 'Islamorada, FL 33036',
    'zone': 'keywest', 'zl': 'Islamorada', 'cat': 'to',
    'price': 395, 'lat': 24.914807, 'lng': -80.639718,
    'photo': 'IiNkagaLSeyKOafTMKV2',
    'link': 'https://fareharbor.com/embeds/book/islamoradaprivatecharters/items/456391/calendar/2026/05/?asn=fhdn&asn-ref=miamistylerentals&ref=miamistylerentals&marketplace=yes&flow=no&full-items=yes',
    'badge': 'top', 'rating': 5.0, 'reviews': 244,
    'desc': 'Private snorkeling charter through the coral reefs and sandbars of Islamorada. From $395. 5.0 stars with 244 reviews. Expert guides through some of the Florida Keys\' best snorkeling spots.'
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

pages = [
    {
        'id': 'b570',
        'filename': 'discount-watersports-waverunner-rental-destin-florida.html',
        'title': 'Discount Watersports Waverunner Rental | Destin FL Jet Ski',
        'meta': 'Waverunner jet ski rentals on the emerald green waters of Destin. From $95. Rated 4.9 stars with 1,928 reviews. One of Destin\'s most popular watersports companies. Book today.',
        'og_url': 'https://miamijetski.com/discount-watersports-waverunner-rental-destin-florida',
        'name': 'Discount Watersports - Waverunner Rental',
        'addr': 'Destin, FL 32541', 'city': 'Destin',
        'price': '$95', 'rating': '4.9',
        'photo': 'https://cdn.filestackcontent.com/1eDKo3txTgCeg3P41lbJ/convert?cache=true&compress=true&quality=90&format=webp&rotate=exif&w=1000&fit=max',
        'og_photo': 'https://cdn.filestackcontent.com/rotate=deg:exif/resize=width:1200/quality=value:85/auto_image/compress/cache=expiry:max/1eDKo3txTgCeg3P41lbJ',
        'link': 'https://fareharbor.com/embeds/book/discountwatersportsdestin/items/315320/calendar/2026/05/?asn=fhdn&asn-ref=miamistylerentals&ref=miamistylerentals&marketplace=yes&flow=no&full-items=yes',
        'lat': '30.393112', 'lng': '-86.503616',
    },
    {
        'id': 'b571',
        'filename': 'islamorada-private-charters-custom-charter-islamorada-florida.html',
        'title': 'Islamorada Private Charters | Custom Boat Charter Islamorada FL',
        'meta': 'Custom private boat charter through the backcountry of Islamorada. From $395. Rated 5.0 stars with 250 reviews. Fishing, snorkeling, and exploration charters in the Florida Keys.',
        'og_url': 'https://miamijetski.com/islamorada-private-charters-custom-charter-islamorada-florida',
        'name': 'Islamorada Private Charters - Custom Charter',
        'addr': 'Islamorada, FL 33036', 'city': 'Islamorada',
        'price': '$395', 'rating': '5.0',
        'photo': 'https://cdn.filestackcontent.com/N5upCqQnRpyyJn2VQunW/convert?cache=true&compress=true&quality=90&format=webp&rotate=exif&w=1000&fit=max',
        'og_photo': 'https://cdn.filestackcontent.com/rotate=deg:exif/resize=width:1200/quality=value:85/auto_image/compress/cache=expiry:max/N5upCqQnRpyyJn2VQunW',
        'link': 'https://fareharbor.com/embeds/book/islamoradaprivatecharters/items/339947/calendar/2026/05/?asn=fhdn&asn-ref=miamistylerentals&ref=miamistylerentals&marketplace=yes&flow=no&full-items=yes',
        'lat': '24.914807', 'lng': '-80.639718',
    },
    {
        'id': 'b572',
        'filename': 'key-west-tiki-boat-1-rental-key-west-florida.html',
        'title': 'Key West Tiki Boat #1 Rental | Self-Captained Tiki Boat Key West FL',
        'meta': 'Rent Tiki Boat #1 in Key West for up to 6 people. Cruise warm island waters on a floating tiki bar. From $550. Rated 5.0 stars with 576 reviews. Book your Key West tiki boat today.',
        'og_url': 'https://miamijetski.com/key-west-tiki-boat-1-rental-key-west-florida',
        'name': 'Key West Tiki Boat #1 Rental',
        'addr': '3841 N Roosevelt Blvd, Key West, FL 33040', 'city': 'Key West',
        'price': '$550', 'rating': '5.0',
        'photo': 'https://cdn.filestackcontent.com/43QUj9pQSClELC2vWpoQ/convert?cache=true&compress=true&quality=90&format=webp&rotate=exif&w=1000&fit=max',
        'og_photo': 'https://cdn.filestackcontent.com/rotate=deg:exif/resize=width:1200/quality=value:85/auto_image/compress/cache=expiry:max/43QUj9pQSClELC2vWpoQ',
        'link': 'https://fareharbor.com/embeds/book/keywesttikiboat/items/347459/calendar/2026/05/?asn=fhdn&asn-ref=miamistylerentals&ref=miamistylerentals&marketplace=yes&flow=no&full-items=yes',
        'lat': '24.571092', 'lng': '-81.752055',
    },
    {
        'id': 'b573',
        'filename': 'sandy-toes-boat-charters-private-charter-gulfport-florida.html',
        'title': 'Sandy Toes Boat Charters | Private Charter Gulfport Tampa Bay FL',
        'meta': 'Personalized private boat charter from Gulfport through Tampa Bay and the Gulf. From $250. Rated 5.0 stars with 270 reviews. Customizable cruises for any occasion in Tampa Bay.',
        'og_url': 'https://miamijetski.com/sandy-toes-boat-charters-private-charter-gulfport-florida',
        'name': 'Sandy Toes Boat Charters - Private Charter',
        'addr': 'Gulfport, FL 33707', 'city': 'Gulfport',
        'price': '$250', 'rating': '5.0',
        'photo': 'https://cdn.filestackcontent.com/UrpRrVoHSie8F9bNk1Xm/convert?cache=true&compress=true&quality=90&format=webp&rotate=exif&w=1000&fit=max',
        'og_photo': 'https://cdn.filestackcontent.com/rotate=deg:exif/resize=width:1200/quality=value:85/auto_image/compress/cache=expiry:max/UrpRrVoHSie8F9bNk1Xm',
        'link': 'https://fareharbor.com/embeds/book/sandytoesboatcharters/items/363507/calendar/2026/05/?asn=fhdn&asn-ref=miamistylerentals&ref=miamistylerentals&marketplace=yes&flow=no&full-items=yes',
        'lat': '27.741493', 'lng': '-82.69695',
    },
    {
        'id': 'b574',
        'filename': 'blown-away-airboat-tours-crystal-river-florida.html',
        'title': 'Blown Away Airboat Tours | Backcountry Airboat Adventure Crystal River FL',
        'meta': 'Backcountry airboat adventure tours through wild Crystal River marshes. From $51. Rated 4.9 stars with 138 reviews. Spot alligators and wildlife on a thrilling Florida airboat ride.',
        'og_url': 'https://miamijetski.com/blown-away-airboat-tours-crystal-river-florida',
        'name': 'Blown Away Airboat Tours - Crystal River',
        'addr': 'Crystal River, FL 34428', 'city': 'Crystal River',
        'price': '$51', 'rating': '4.9',
        'photo': 'https://cdn.filestackcontent.com/nqQphlgZQuG0EHFxBfT3/convert?cache=true&compress=true&quality=90&format=webp&rotate=exif&w=1000&fit=max',
        'og_photo': 'https://cdn.filestackcontent.com/rotate=deg:exif/resize=width:1200/quality=value:85/auto_image/compress/cache=expiry:max/nqQphlgZQuG0EHFxBfT3',
        'link': 'https://fareharbor.com/embeds/book/blownawayairboattours/items/396593/calendar/2026/05/?asn=fhdn&asn-ref=miamistylerentals&ref=miamistylerentals&marketplace=yes&flow=no&full-items=yes',
        'lat': '28.90126', 'lng': '-82.645253',
    },
    {
        'id': 'b575',
        'filename': 'salty-sandbars-half-day-charter-key-west-florida.html',
        'title': 'Salty Sandbars Half Day Charter | Boston Whaler Key West FL',
        'meta': 'Half-day 4-hour Boston Whaler charter in Key West for snorkeling and sandbar fun. From $599. Rated 4.9 stars with 174 reviews. Explore Key West sandbars and reefs at your own pace.',
        'og_url': 'https://miamijetski.com/salty-sandbars-half-day-charter-key-west-florida',
        'name': 'Salty Sandbars - Half Day Charter Key West',
        'addr': 'Key West, FL 33040', 'city': 'Key West',
        'price': '$599', 'rating': '4.9',
        'photo': 'https://cdn.filestackcontent.com/9EYWNhVpTOaawqcRfxoS/convert?cache=true&compress=true&quality=90&format=webp&rotate=exif&w=1000&fit=max',
        'og_photo': 'https://cdn.filestackcontent.com/rotate=deg:exif/resize=width:1200/quality=value:85/auto_image/compress/cache=expiry:max/9EYWNhVpTOaawqcRfxoS',
        'link': 'https://fareharbor.com/embeds/book/saltysandbars/items/417200/calendar/2026/05/?asn=fhdn&asn-ref=miamistylerentals&ref=miamistylerentals&marketplace=yes&flow=no&full-items=yes',
        'lat': '24.560796', 'lng': '-81.787414',
    },
    {
        'id': 'b576',
        'filename': 'islamorada-private-charters-snorkeling-islamorada-florida.html',
        'title': 'Islamorada Private Charters Snorkeling | Private Snorkel Charter FL',
        'meta': 'Private snorkeling charter through the coral reefs of Islamorada, Florida Keys. From $395. Rated 5.0 stars with 244 reviews. Expert guides through the Keys\' best snorkeling spots.',
        'og_url': 'https://miamijetski.com/islamorada-private-charters-snorkeling-islamorada-florida',
        'name': 'Islamorada Private Charters - Snorkeling',
        'addr': 'Islamorada, FL 33036', 'city': 'Islamorada',
        'price': '$395', 'rating': '5.0',
        'photo': 'https://cdn.filestackcontent.com/IiNkagaLSeyKOafTMKV2/convert?cache=true&compress=true&quality=90&format=webp&rotate=exif&w=1000&fit=max',
        'og_photo': 'https://cdn.filestackcontent.com/rotate=deg:exif/resize=width:1200/quality=value:85/auto_image/compress/cache=expiry:max/IiNkagaLSeyKOafTMKV2',
        'link': 'https://fareharbor.com/embeds/book/islamoradaprivatecharters/items/456391/calendar/2026/05/?asn=fhdn&asn-ref=miamistylerentals&ref=miamistylerentals&marketplace=yes&flow=no&full-items=yes',
        'lat': '24.914807', 'lng': '-80.639718',
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
    'https://miamijetski.com/discount-watersports-waverunner-rental-destin-florida',
    'https://miamijetski.com/islamorada-private-charters-custom-charter-islamorada-florida',
    'https://miamijetski.com/key-west-tiki-boat-1-rental-key-west-florida',
    'https://miamijetski.com/sandy-toes-boat-charters-private-charter-gulfport-florida',
    'https://miamijetski.com/blown-away-airboat-tours-crystal-river-florida',
    'https://miamijetski.com/salty-sandbars-half-day-charter-key-west-florida',
    'https://miamijetski.com/islamorada-private-charters-snorkeling-islamorada-florida',
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
