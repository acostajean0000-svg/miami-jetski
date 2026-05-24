#!/usr/bin/env python3
import re

import os as _os
BASE = _os.path.dirname(_os.path.abspath(__file__))

with open(f'{BASE}/cudjoe-key-boat-rentals-florida-keys-cudjoe-key.html') as f:
    tmpl = f.read()

pages = [
    {
        'id': 'b555',
        'filename': 'charter-finders-dolphin-shelling-cruise-madeira-beach-florida.html',
        'title': 'Charter Finders | Dolphin Shelling Snorkeling Cruise Madeira Beach FL',
        'meta': 'Dolphin shelling snorkeling cruise from Madeira Beach on the Gulf Coast. From $60. Rated 4.9 stars with 427 reviews. Book your Madeira Beach dolphin and shelling boat tour today.',
        'og_url': 'https://miamijetski.com/charter-finders-dolphin-shelling-cruise-madeira-beach-florida',
        'name': 'Charter Finders - Dolphin Shelling Cruise',
        'addr': 'Madeira Beach, FL 33708',
        'city': 'Madeira Beach',
        'price': '$60',
        'rating': '4.9',
        'photo': 'https://cdn.filestackcontent.com/VE0Wc8qmSASOaVOM68nl/convert?cache=true&compress=true&quality=90&format=webp&rotate=exif&w=1000&fit=max',
        'og_photo': 'https://cdn.filestackcontent.com/rotate=deg:exif/resize=width:1200/quality=value:85/auto_image/compress/cache=expiry:max/VE0Wc8qmSASOaVOM68nl',
        'link': 'https://fareharbor.com/embeds/book/charterfinders/items/160477/calendar/2026/05/?asn=fhdn&asn-ref=miamistylerentals&ref=miamistylerentals&marketplace=yes&flow=no&full-items=yes',
        'lat': '27.7883', 'lng': '-82.7856',
    },
    {
        'id': 'b556',
        'filename': 'sol-vibes-dolphin-tour-englewood-florida.html',
        'title': 'Sol Vibes Dolphin Tour | Englewood Florida Boat Tours',
        'meta': 'Dolphin tour along the Englewood Gulf Coast with perfect 5.0-star reviews. From $50. Rated 5.0 stars with 454 reviews. Book your Englewood dolphin boat tour today.',
        'og_url': 'https://miamijetski.com/sol-vibes-dolphin-tour-englewood-florida',
        'name': 'Sol Vibes - Dolphin Tour',
        'addr': 'Englewood, FL 34224',
        'city': 'Englewood',
        'price': '$50',
        'rating': '5.0',
        'photo': 'https://cdn.filestackcontent.com/Wh0JYFP3Tzqtr7mA2pvA/convert?cache=true&compress=true&quality=90&format=webp&rotate=exif&w=1000&fit=max',
        'og_photo': 'https://cdn.filestackcontent.com/rotate=deg:exif/resize=width:1200/quality=value:85/auto_image/compress/cache=expiry:max/Wh0JYFP3Tzqtr7mA2pvA',
        'link': 'https://fareharbor.com/embeds/book/solvibeexcursions/items/449432/calendar/2026/05/?asn=fhdn&asn-ref=miamistylerentals&ref=miamistylerentals&marketplace=yes&flow=no&full-items=yes',
        'lat': '26.9397', 'lng': '-82.3496',
    },
    {
        'id': 'b557',
        'filename': 'sol-vibes-private-boat-tour-englewood-florida.html',
        'title': 'Sol Vibes Private Boat Tour | Englewood Florida Charter',
        'meta': 'Private boat tour along the Englewood Gulf Coast with a perfect 5-star rating. From $900. Rated 5.0 stars with 433 reviews. Book your exclusive private Englewood boat tour today.',
        'og_url': 'https://miamijetski.com/sol-vibes-private-boat-tour-englewood-florida',
        'name': 'Sol Vibes - Private Boat Tour',
        'addr': 'Englewood, FL 34224',
        'city': 'Englewood',
        'price': '$900',
        'rating': '5.0',
        'photo': 'https://cdn.filestackcontent.com/Hizn2dtVTle0JlgRfdDj/convert?cache=true&compress=true&quality=90&format=webp&rotate=exif&w=1000&fit=max',
        'og_photo': 'https://cdn.filestackcontent.com/rotate=deg:exif/resize=width:1200/quality=value:85/auto_image/compress/cache=expiry:max/Hizn2dtVTle0JlgRfdDj',
        'link': 'https://fareharbor.com/embeds/book/solvibeexcursions/items/449460/calendar/2026/05/?asn=fhdn&asn-ref=miamistylerentals&ref=miamistylerentals&marketplace=yes&flow=no&full-items=yes',
        'lat': '26.9397', 'lng': '-82.3496',
    },
    {
        'id': 'b558',
        'filename': 'vero-tackle-waterfront-escape-vero-beach-florida.html',
        'title': 'Vero Tackle Sweet Desire Waterfront Escape | Vero Beach FL Boat Tours',
        'meta': 'Waterfront escape cruise on the Indian River Lagoon in Vero Beach. From $29. Rated 4.9 stars with 1,035 reviews. Book your Treasure Coast boat tour today.',
        'og_url': 'https://miamijetski.com/vero-tackle-waterfront-escape-vero-beach-florida',
        'name': 'Vero Tackle - Sweet Desire Waterfront Escape',
        'addr': 'Vero Beach, FL 32960',
        'city': 'Vero Beach',
        'price': '$29',
        'rating': '4.9',
        'photo': 'https://cdn.filestackcontent.com/uFR0XW6dSpy4YeHZsrR7/convert?cache=true&compress=true&quality=90&format=webp&rotate=exif&w=1000&fit=max',
        'og_photo': 'https://cdn.filestackcontent.com/rotate=deg:exif/resize=width:1200/quality=value:85/auto_image/compress/cache=expiry:max/uFR0XW6dSpy4YeHZsrR7',
        'link': 'https://fareharbor.com/embeds/book/verotackle/items/633360/calendar/2026/05/?asn=fhdn&asn-ref=miamistylerentals&ref=miamistylerentals&marketplace=yes&flow=no&full-items=yes',
        'lat': '27.6528', 'lng': '-80.3704',
    },
    {
        'id': 'b559',
        'filename': 'power-up-watersports-jet-ski-rental-fort-walton-beach-florida.html',
        'title': 'Power Up Watersports Jet Ski Rental | Fort Walton Beach FL',
        'meta': 'Jet ski rentals on the emerald green waters of Fort Walton Beach. From $95. Rated 4.8 stars with 976 reviews. Ride the Gulf of Mexico on a high-powered waverunner today.',
        'og_url': 'https://miamijetski.com/power-up-watersports-jet-ski-rental-fort-walton-beach-florida',
        'name': 'Power Up Watersports - Jet Ski Rental',
        'addr': 'Fort Walton Beach, FL 32548',
        'city': 'Fort Walton Beach',
        'price': '$95',
        'rating': '4.8',
        'photo': 'https://cdn.filestackcontent.com/Z75gCCkRZWrRFcmyLRqD/convert?cache=true&compress=true&quality=90&format=webp&rotate=exif&w=1000&fit=max',
        'og_photo': 'https://cdn.filestackcontent.com/rotate=deg:exif/resize=width:1200/quality=value:85/auto_image/compress/cache=expiry:max/Z75gCCkRZWrRFcmyLRqD',
        'link': 'https://fareharbor.com/embeds/book/powerupwatersports/items/46710/calendar/2026/05/?asn=fhdn&asn-ref=miamistylerentals&ref=miamistylerentals&marketplace=yes&flow=no&full-items=yes',
        'lat': '30.3994', 'lng': '-86.6001',
    },
    {
        'id': 'b560',
        'filename': 'power-up-watersports-pontoon-rental-fort-walton-beach-florida.html',
        'title': 'Power Up Watersports Pontoon Rental | Fort Walton Beach FL',
        'meta': 'Rent a 20-foot pontoon boat in Fort Walton Beach for the whole crew. From $225. Rated 4.8 stars with 986 reviews. Cruise the bay at your own pace. Book your pontoon rental today.',
        'og_url': 'https://miamijetski.com/power-up-watersports-pontoon-rental-fort-walton-beach-florida',
        'name': 'Power Up Watersports - Pontoon Rental',
        'addr': 'Fort Walton Beach, FL 32548',
        'city': 'Fort Walton Beach',
        'price': '$225',
        'rating': '4.8',
        'photo': 'https://cdn.filestackcontent.com/JLIKYZekTOm0AnN9FaHy/convert?cache=true&compress=true&quality=90&format=webp&rotate=exif&w=1000&fit=max',
        'og_photo': 'https://cdn.filestackcontent.com/rotate=deg:exif/resize=width:1200/quality=value:85/auto_image/compress/cache=expiry:max/JLIKYZekTOm0AnN9FaHy',
        'link': 'https://fareharbor.com/embeds/book/powerupwatersports/items/46740/calendar/2026/05/?asn=fhdn&asn-ref=miamistylerentals&ref=miamistylerentals&marketplace=yes&flow=no&full-items=yes',
        'lat': '30.3994', 'lng': '-86.6001',
    },
    {
        'id': 'b561',
        'filename': 'finz-dive-charters-spearfishing-key-west-florida.html',
        'title': 'Finz Dive Charters Spearfishing | Key West FL Spearfishing Trips',
        'meta': 'Spearfishing charter in the crystal-clear waters of Key West with expert guides. From $1,050. Rated 4.9 stars with 279 reviews. Full-day reef spearfishing trips in the Florida Keys.',
        'og_url': 'https://miamijetski.com/finz-dive-charters-spearfishing-key-west-florida',
        'name': 'Finz Dive Charters - Spearfishing',
        'addr': 'Key West, FL 33040',
        'city': 'Key West',
        'price': '$1,050',
        'rating': '4.9',
        'photo': 'https://cdn.filestackcontent.com/1DBwXKjeRvaXojtP1bJY/convert?cache=true&compress=true&quality=90&format=webp&rotate=exif&w=1000&fit=max',
        'og_photo': 'https://cdn.filestackcontent.com/rotate=deg:exif/resize=width:1200/quality=value:85/auto_image/compress/cache=expiry:max/1DBwXKjeRvaXojtP1bJY',
        'link': 'https://fareharbor.com/embeds/book/finzdivecenter/items/76157/calendar/2026/05/?asn=fhdn&asn-ref=miamistylerentals&ref=miamistylerentals&marketplace=yes&flow=no&full-items=yes',
        'lat': '24.5649', 'lng': '-81.7282',
    },
    {
        'id': 'b562',
        'filename': 'cruisin-tikis-st-augustine-matanzas-bay-tours-florida.html',
        'title': 'Cruisin Tikis St. Augustine | Matanzas Bay Tiki Boat Tours FL',
        'meta': 'Tiki boat tours through historic Matanzas Bay in St. Augustine. From $75. Rated 4.9 stars with 260 reviews. Cruise the oldest city in America on a floating tiki bar.',
        'og_url': 'https://miamijetski.com/cruisin-tikis-st-augustine-matanzas-bay-tours-florida',
        'name': 'Cruisin Tikis St. Augustine - Matanzas Bay Tours',
        'addr': 'St. Augustine, FL 32084',
        'city': 'St. Augustine',
        'price': '$75',
        'rating': '4.9',
        'photo': 'https://cdn.filestackcontent.com/ppvH8RgRfhhQzx4G7C9A/convert?cache=true&compress=true&quality=90&format=webp&rotate=exif&w=1000&fit=max',
        'og_photo': 'https://cdn.filestackcontent.com/rotate=deg:exif/resize=width:1200/quality=value:85/auto_image/compress/cache=expiry:max/ppvH8RgRfhhQzx4G7C9A',
        'link': 'https://fareharbor.com/embeds/book/cruisintikissaugustine/items/225361/calendar/2026/05/?asn=fhdn&asn-ref=miamistylerentals&ref=miamistylerentals&marketplace=yes&flow=no&full-items=yes',
        'lat': '29.9184', 'lng': '-81.3072',
    },
    {
        'id': 'b563',
        'filename': 'reel-floridian-inshore-fishing-jupiter-florida.html',
        'title': 'Reel Floridian Inshore Fishing Charter | Jupiter FL Fishing Trips',
        'meta': 'Inshore fishing charters in Jupiter, FL targeting snook, redfish, and tarpon. From $695. Rated 4.8 stars with 184 reviews. Expert local guides on Jupiter\'s best fishing grounds.',
        'og_url': 'https://miamijetski.com/reel-floridian-inshore-fishing-jupiter-florida',
        'name': 'Reel Floridian - Inshore Fishing Jupiter',
        'addr': 'Jupiter, FL 33458',
        'city': 'Jupiter',
        'price': '$695',
        'rating': '4.8',
        'photo': 'https://cdn.filestackcontent.com/ROPccPhRH6cJr2KY89Sh/convert?cache=true&compress=true&quality=90&format=webp&rotate=exif&w=1000&fit=max',
        'og_photo': 'https://cdn.filestackcontent.com/rotate=deg:exif/resize=width:1200/quality=value:85/auto_image/compress/cache=expiry:max/ROPccPhRH6cJr2KY89Sh',
        'link': 'https://fareharbor.com/embeds/book/reelfloridianfishing/items/645016/calendar/2026/05/?asn=fhdn&asn-ref=miamistylerentals&ref=miamistylerentals&marketplace=yes&flow=no&full-items=yes',
        'lat': '26.9348', 'lng': '-80.0942',
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
    with open(f"{BASE}/{p['filename']}", 'w') as f:
        f.write(html)
    print(f"Generated: {p['filename']}")

print("Done.")
