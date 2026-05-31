#!/usr/bin/env python3
import re

import os as _os
BASE = _os.path.dirname(_os.path.abspath(__file__))

with open(f'{BASE}/cudjoe-key-boat-rentals-florida-keys-cudjoe-key.html') as f:
    tmpl = f.read()

pages = [
    {
        'id': 'b552',
        'filename': 'key-west-tiki-boat-rental-key-west-florida.html',
        'title': 'Key West Tiki Boat Rental | Self-Captained Tiki Boat Key West FL',
        'meta': 'Rent a self-captained tiki boat in Key West for up to 6 people. Cruise warm waters in paradise. From $650. Rated 5.0 stars with 558 reviews. Book your Key West tiki boat rental.',
        'og_url': 'https://miamijetski.com/key-west-tiki-boat-rental-key-west-florida',
        'name': 'Key West Tiki Boat Rental',
        'addr': '3841 N Roosevelt Blvd, Key West, FL 33040',
        'city': 'Key West',
        'price': '$650',
        'rating': '5.0',
        'photo': 'https://cdn.filestackcontent.com/R3dsXWVKTZiosM9gFVzy/convert?cache=true&compress=true&quality=90&format=webp&rotate=exif&w=1000&fit=max',
        'og_photo': 'https://cdn.filestackcontent.com/rotate=deg:exif/resize=width:1200/quality=value:85/auto_image/compress/cache=expiry:max/R3dsXWVKTZiosM9gFVzy',
        'link': 'https://fareharbor.com/embeds/book/keywesttikiboat/items/467583/calendar/2026/05/?asn=fhdn&asn-ref=miamistylerentals&ref=miamistylerentals&marketplace=yes&flow=no&full-items=yes',
        'lat': '24.571092',
        'lng': '-81.752055',
    },
    {
        'id': 'b553',
        'filename': 'wave-cutter-charters-dolphin-cruise-pensacola-beach-florida.html',
        'title': 'Wave Cutter Charters | Dolphin Cruise Pensacola Beach FL',
        'meta': 'Dolphin cruise along Pensacola Beach coastline with guaranteed wildlife sightings. From $30. Rated 5.0 stars with 3,437 reviews. Most-reviewed dolphin tour on the Florida Panhandle.',
        'og_url': 'https://miamijetski.com/wave-cutter-charters-dolphin-cruise-pensacola-beach-florida',
        'name': 'Wave Cutter Charters - Dolphin Cruise',
        'addr': 'Pensacola Beach, FL 32561',
        'city': 'Pensacola Beach',
        'price': '$30',
        'rating': '5.0',
        'photo': 'https://cdn.filestackcontent.com/4oize8IgRXaFAc8nuuGh/convert?cache=true&compress=true&quality=90&format=webp&rotate=exif&w=1000&fit=max',
        'og_photo': 'https://cdn.filestackcontent.com/rotate=deg:exif/resize=width:1200/quality=value:85/auto_image/compress/cache=expiry:max/4oize8IgRXaFAc8nuuGh',
        'link': 'https://fareharbor.com/embeds/book/wavecuttercharters/items/359527/calendar/2026/05/?asn=fhdn&asn-ref=miamistylerentals&ref=miamistylerentals&marketplace=yes&flow=no&full-items=yes',
        'lat': '30.3355',
        'lng': '-87.1442',
    },
    {
        'id': 'b554',
        'filename': 'breezy-tiki-private-charter-fort-lauderdale-florida.html',
        'title': 'Breezy Tiki Private Charter | Tiki Boat Fort Lauderdale FL',
        'meta': 'Six-hour private tiki boat charter through Fort Lauderdale waterways. From $1,100. Rated 4.9 stars with 509 reviews. Book your private tiki charter in Fort Lauderdale today.',
        'og_url': 'https://miamijetski.com/breezy-tiki-private-charter-fort-lauderdale-florida',
        'name': 'Breezy Tiki - Private Charter',
        'addr': '1440 N Federal Hwy, Fort Lauderdale, FL 33304',
        'city': 'Fort Lauderdale',
        'price': '$1,100',
        'rating': '4.9',
        'photo': 'https://cdn.filestackcontent.com/oSWdRJ2ESheS6nO0QgIO/convert?cache=true&compress=true&quality=90&format=webp&rotate=exif&w=1000&fit=max',
        'og_photo': 'https://cdn.filestackcontent.com/rotate=deg:exif/resize=width:1200/quality=value:85/auto_image/compress/cache=expiry:max/oSWdRJ2ESheS6nO0QgIO',
        'link': 'https://fareharbor.com/embeds/book/breezytiki/items/98494/calendar/2026/05/?asn=fhdn&asn-ref=miamistylerentals&ref=miamistylerentals&marketplace=yes&flow=no&full-items=yes',
        'lat': '26.124146',
        'lng': '-80.103833',
    },
]

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

    out_path = f"{BASE}/{p['filename']}"
    with open(out_path, 'w') as f:
        f.write(html)
    print(f"Generated: {p['filename']}")

print("Done.")
