#!/usr/bin/env python3
import json, re, os

import os as _os
BASE = _os.path.dirname(_os.path.abspath(__file__))

# Load template
with open(f'{BASE}/cudjoe-key-boat-rentals-florida-keys-cudjoe-key.html') as f:
    tmpl = f.read()

pages_to_gen = [
    {
        'id': 'b520',
        'filename': 'destin-tikis-sandbar-cruise-destin-florida.html',
        'title': 'Destin Tikis Sandbar Cruise | Tiki Boat Tours Destin FL',
        'meta': 'Float on a tiki bar through Destin\'s emerald waters. Sandbar swim-stop cruises from $75. Rated 4.9 stars with 1,834 reviews. Book your Destin tiki boat tour today.',
        'og_url': 'https://miamijetski.com/destin-tikis-sandbar-cruise-destin-florida',
        'name': 'Destin Tikis - Sandbar Cruise',
        'addr': 'Destin, FL 32541',
        'city': 'Destin',
        'price': '$75',
        'rating': '4.9',
        'photo': 'https://cdn.filestackcontent.com/LnUVWI4T9O6VS3DujVtC/convert?cache=true&compress=true&quality=90&format=webp&rotate=exif&w=1000&fit=max',
        'og_photo': 'https://cdn.filestackcontent.com/rotate=deg:exif/resize=width:1200/quality=value:85/auto_image/compress/cache=expiry:max/LnUVWI4T9O6VS3DujVtC',
        'link': 'https://fareharbor.com/embeds/book/destintikis/items/103456/calendar/2026/05/?asn=fhdn&asn-ref=miamistylerentals&ref=miamistylerentals&marketplace=yes&flow=no&full-items=yes',
        'lat': '30.3927',
        'lng': '-86.5056',
    },
    {
        'id': 'b521',
        'filename': 'naples-tiki-fun-tours-naples-florida.html',
        'title': 'Naples Tiki Fun Tours | Tiki Boat Cruises Naples FL',
        'meta': 'Tiki boat cruises through Naples Bay with BYOB fun and dolphin spotting. From $59. Rated 4.9 stars. Book your Naples tiki tour today.',
        'og_url': 'https://miamijetski.com/naples-tiki-fun-tours-naples-florida',
        'name': 'Naples Tiki Fun Tours',
        'addr': 'Naples, FL 34102',
        'city': 'Naples',
        'price': '$59',
        'rating': '4.9',
        'photo': 'https://cdn.filestackcontent.com/3t5jsdazQui9VVQ64xsM/convert?cache=true&compress=true&quality=90&format=webp&rotate=exif&w=1000&fit=max',
        'og_photo': 'https://cdn.filestackcontent.com/rotate=deg:exif/resize=width:1200/quality=value:85/auto_image/compress/cache=expiry:max/3t5jsdazQui9VVQ64xsM',
        'link': 'https://fareharbor.com/embeds/book/cruisintikisnaples/items/158308/calendar/2026/05/?asn=fhdn&asn-ref=miamistylerentals&ref=miamistylerentals&marketplace=yes&flow=no&full-items=yes',
        'lat': '26.1338',
        'lng': '-81.7923',
    },
    {
        'id': 'b522',
        'filename': 'freaky-tiki-boat-charters-fort-lauderdale-florida.html',
        'title': 'Freaky Tiki Boat Charters | Tiki Charter Fort Lauderdale FL',
        'meta': 'Private tiki boat charters through Fort Lauderdale\'s Intracoastal Waterway. From $650. Rated 5.0 stars with 300 reviews. Book your private tiki adventure.',
        'og_url': 'https://miamijetski.com/freaky-tiki-boat-charters-fort-lauderdale-florida',
        'name': 'Freaky Tiki Boat Charters',
        'addr': 'Fort Lauderdale, FL 33312',
        'city': 'Fort Lauderdale',
        'price': '$650',
        'rating': '5.0',
        'photo': 'https://cdn.filestackcontent.com/lV1e7jRT5e51UHh4H9Fe/convert?cache=true&compress=true&quality=90&format=webp&rotate=exif&w=1000&fit=max',
        'og_photo': 'https://cdn.filestackcontent.com/rotate=deg:exif/resize=width:1200/quality=value:85/auto_image/compress/cache=expiry:max/lV1e7jRT5e51UHh4H9Fe',
        'link': 'https://fareharbor.com/embeds/book/freakytikicharters/items/569170/calendar/2026/05/?asn=fhdn&asn-ref=miamistylerentals&ref=miamistylerentals&marketplace=yes&flow=no&full-items=yes',
        'lat': '26.111',
        'lng': '-80.1183',
    },
    {
        'id': 'b523',
        'filename': 'j2-boats-pontoon-rental-madeira-beach-florida.html',
        'title': 'J2 Boats Pontoon Rental | Madeira Beach FL Boat Rentals',
        'meta': 'Rent a pontoon boat in Madeira Beach for up to 12 passengers. From $349. Rated 5.0 stars. Daily Gulf Coast boat rentals near St. Pete Beach.',
        'og_url': 'https://miamijetski.com/j2-boats-pontoon-rental-madeira-beach-florida',
        'name': 'J2 Boats - Madeira Beach',
        'addr': 'Madeira Beach, FL 33708',
        'city': 'Madeira Beach',
        'price': '$349',
        'rating': '5.0',
        'photo': 'https://cdn.filestackcontent.com/2xK99DkrQAGI2J8hDSLi/convert?cache=true&compress=true&quality=90&format=webp&rotate=exif&w=1000&fit=max',
        'og_photo': 'https://cdn.filestackcontent.com/rotate=deg:exif/resize=width:1200/quality=value:85/auto_image/compress/cache=expiry:max/2xK99DkrQAGI2J8hDSLi',
        'link': 'https://fareharbor.com/embeds/book/j2boats/items/604564/calendar/2026/05/?asn=fhdn&asn-ref=miamistylerentals&ref=miamistylerentals&marketplace=yes&flow=no&full-items=yes',
        'lat': '27.7883',
        'lng': '-82.7856',
    },
    {
        'id': 'b524',
        'filename': 'salty-sandbars-boston-whaler-key-west-florida.html',
        'title': 'Salty Sandbars Key West | Sandbar Excursions Boston Whaler FL',
        'meta': 'Private sandbar excursions aboard a Boston Whaler in Key West. Snorkel, swim, explore. From $489. Rated 4.9 stars. Book your Key West sandbar adventure.',
        'og_url': 'https://miamijetski.com/salty-sandbars-boston-whaler-key-west-florida',
        'name': 'Salty Sandbars - Key West',
        'addr': 'Key West, FL 33040',
        'city': 'Key West',
        'price': '$489',
        'rating': '4.9',
        'photo': 'https://cdn.filestackcontent.com/97YpXVC8TsimKfG0wcKF/convert?cache=true&compress=true&quality=90&format=webp&rotate=exif&w=1000&fit=max',
        'og_photo': 'https://cdn.filestackcontent.com/rotate=deg:exif/resize=width:1200/quality=value:85/auto_image/compress/cache=expiry:max/97YpXVC8TsimKfG0wcKF',
        'link': 'https://fareharbor.com/embeds/book/saltysandbars/items/637746/calendar/2026/05/?asn=fhdn&asn-ref=miamistylerentals&ref=miamistylerentals&marketplace=yes&flow=no&full-items=yes',
        'lat': '24.5608',
        'lng': '-81.7874',
    },
    {
        'id': 'b525',
        'filename': 'low-tide-tours-boat-cruise-venice-florida.html',
        'title': 'Low Tide Tours | Dolphin Boat Cruise Venice Sarasota FL',
        'meta': 'Scenic boat cruises along the Venice and Sarasota coastline with dolphins and sunset views. From $30. Rated 4.9 stars with 649 reviews. Book your cruise.',
        'og_url': 'https://miamijetski.com/low-tide-tours-boat-cruise-venice-florida',
        'name': 'Low Tide Tours - Venice',
        'addr': 'Venice, FL 34285',
        'city': 'Venice',
        'price': '$30',
        'rating': '4.9',
        'photo': 'https://cdn.filestackcontent.com/rXbEMOG6QQSpcnRYFVC6/convert?cache=true&compress=true&quality=90&format=webp&rotate=exif&w=1000&fit=max',
        'og_photo': 'https://cdn.filestackcontent.com/rotate=deg:exif/resize=width:1200/quality=value:85/auto_image/compress/cache=expiry:max/rXbEMOG6QQSpcnRYFVC6',
        'link': 'https://fareharbor.com/embeds/book/lowtidetours/items/334561/calendar/2026/05/?asn=fhdn&asn-ref=miamistylerentals&ref=miamistylerentals&marketplace=yes&flow=no&full-items=yes',
        'lat': '27.1091',
        'lng': '-82.4626',
    },
    {
        'id': 'b526',
        'filename': 'explorida-manatee-cruise-crystal-river-florida.html',
        'title': 'Explorida Manatee Cruise | Swim With Manatees Crystal River FL',
        'meta': 'Guided manatee viewing and eco cruises through Crystal River spring-fed waterways. From $35. Rated 4.9 stars with 1,091 reviews. Swim with manatees in Florida.',
        'og_url': 'https://miamijetski.com/explorida-manatee-cruise-crystal-river-florida',
        'name': 'Explorida - Manatee Cruise',
        'addr': 'Crystal River, FL 34428',
        'city': 'Crystal River',
        'price': '$35',
        'rating': '4.9',
        'photo': 'https://cdn.filestackcontent.com/vO9vafpGTZiyOwg2oXbL/convert?cache=true&compress=true&quality=90&format=webp&rotate=exif&w=1000&fit=max',
        'og_photo': 'https://cdn.filestackcontent.com/rotate=deg:exif/resize=width:1200/quality=value:85/auto_image/compress/cache=expiry:max/vO9vafpGTZiyOwg2oXbL',
        'link': 'https://fareharbor.com/embeds/book/explorida/items/282638/calendar/2026/05/?asn=fhdn&asn-ref=miamistylerentals&ref=miamistylerentals&marketplace=yes&flow=no&full-items=yes',
        'lat': '28.899',
        'lng': '-82.5928',
    },
    {
        'id': 'b527',
        'filename': 'island-hoppers-boat-tours-anna-maria-island-florida.html',
        'title': 'Island Hoppers Boat Tours | Anna Maria Island Holmes Beach FL',
        'meta': 'Private catamaran and pontoon boat tours around Anna Maria Island. Beach-hopping and dolphin watching. From $800. Rated 5.0 stars with 364 reviews.',
        'og_url': 'https://miamijetski.com/island-hoppers-boat-tours-anna-maria-island-florida',
        'name': 'Island Hoppers Boat Tours',
        'addr': 'Holmes Beach, FL 34217',
        'city': 'Anna Maria Island',
        'price': '$800',
        'rating': '5.0',
        'photo': 'https://cdn.filestackcontent.com/x2zgQ0dJT96fths2UjU2/convert?cache=true&compress=true&quality=90&format=webp&rotate=exif&w=1000&fit=max',
        'og_photo': 'https://cdn.filestackcontent.com/rotate=deg:exif/resize=width:1200/quality=value:85/auto_image/compress/cache=expiry:max/x2zgQ0dJT96fths2UjU2',
        'link': 'https://fareharbor.com/embeds/book/islandhoppersboattours/items/556274/calendar/2026/05/?asn=fhdn&asn-ref=miamistylerentals&ref=miamistylerentals&marketplace=yes&flow=no&full-items=yes',
        'lat': '27.4976',
        'lng': '-82.7025',
    },
    {
        'id': 'b528',
        'filename': 'tom-and-jerrys-airboat-rides-lake-panasoffkee-florida.html',
        'title': "Tom and Jerry's Airboat Rides | Lake Panasoffkee Florida Airboat Tours",
        'meta': "Exhilarating 1-hour airboat tours through Florida swamps with gators and wildlife near Lake Panasoffkee. From $35. Rated 4.8 stars with 3,145 reviews.",
        'og_url': 'https://miamijetski.com/tom-and-jerrys-airboat-rides-lake-panasoffkee-florida',
        'name': "Tom and Jerry's Airboat Rides",
        'addr': 'Lake Panasoffkee, FL 33538',
        'city': 'Lake Panasoffkee',
        'price': '$35',
        'rating': '4.8',
        'photo': 'https://cdn.filestackcontent.com/OIOJquMCS3tQmDP5Q23P/convert?cache=true&compress=true&quality=90&format=webp&rotate=exif&w=1000&fit=max',
        'og_photo': 'https://cdn.filestackcontent.com/rotate=deg:exif/resize=width:1200/quality=value:85/auto_image/compress/cache=expiry:max/OIOJquMCS3tQmDP5Q23P',
        'link': 'https://fareharbor.com/embeds/book/airboattoursorlando/items/580515/calendar/2026/05/?asn=fhdn&asn-ref=miamistylerentals&ref=miamistylerentals&marketplace=yes&flow=no&full-items=yes',
        'lat': '28.7688',
        'lng': '-82.0723',
    },
]

generated = []
for p in pages_to_gen:
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

    out_path = f"{BASE}/{p['filename']}"
    with open(out_path, 'w') as f:
        f.write(html)
    generated.append(p['filename'])
    print(f"Generated: {p['filename']}")

print(f"\nTotal pages generated: {len(generated)}")
