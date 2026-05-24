#!/usr/bin/env python3
import json

import os as _os
BASE = _os.path.dirname(_os.path.abspath(__file__))

with open(f'{BASE}/operators.json') as f:
    ops = json.load(f)

new_ops = [
  {
    'id': 'b555',
    'name': 'Charter Finders - Dolphin Shelling Cruise',
    'addr': 'Madeira Beach, FL 33708',
    'zone': 'tampa', 'zl': 'Madeira Beach', 'cat': 'to',
    'price': 60, 'lat': 27.7883, 'lng': -82.7856,
    'photo': 'VE0Wc8qmSASOaVOM68nl',
    'link': 'https://fareharbor.com/embeds/book/charterfinders/items/160477/calendar/2026/05/?asn=fhdn&asn-ref=miamistylerentals&ref=miamistylerentals&marketplace=yes&flow=no&full-items=yes',
    'badge': 'top', 'rating': 4.9, 'reviews': 427,
    'desc': 'Dolphin shelling snorkeling cruise from Madeira Beach. From $60. 4.9 stars with 427 reviews. Explore the Gulf Coast by boat with dolphins and shelling stops.'
  },
  {
    'id': 'b556',
    'name': 'Sol Vibes - Dolphin Tour',
    'addr': 'Englewood, FL 34224',
    'zone': 'gulf', 'zl': 'Englewood', 'cat': 'to',
    'price': 50, 'lat': 26.9397, 'lng': -82.3496,
    'photo': 'Wh0JYFP3Tzqtr7mA2pvA',
    'link': 'https://fareharbor.com/embeds/book/solvibeexcursions/items/449432/calendar/2026/05/?asn=fhdn&asn-ref=miamistylerentals&ref=miamistylerentals&marketplace=yes&flow=no&full-items=yes',
    'badge': 'top', 'rating': 5.0, 'reviews': 454,
    'desc': 'Dolphin tour along the Englewood coastline with perfect 5.0-star reviews. From $50. 5.0 stars with 454 reviews. Spot dolphins in their natural habitat on the Gulf Coast.'
  },
  {
    'id': 'b557',
    'name': 'Sol Vibes - Private Boat Tour',
    'addr': 'Englewood, FL 34224',
    'zone': 'gulf', 'zl': 'Englewood', 'cat': 'to',
    'price': 900, 'lat': 26.9397, 'lng': -82.3496,
    'photo': 'Hizn2dtVTle0JlgRfdDj',
    'link': 'https://fareharbor.com/embeds/book/solvibeexcursions/items/449460/calendar/2026/05/?asn=fhdn&asn-ref=miamistylerentals&ref=miamistylerentals&marketplace=yes&flow=no&full-items=yes',
    'badge': 'top', 'rating': 5.0, 'reviews': 433,
    'desc': 'Private boat tour along the Englewood Gulf Coast with a perfect 5-star rating. From $900. 5.0 stars with 433 reviews. Exclusive private tour for your group.'
  },
  {
    'id': 'b558',
    'name': 'Vero Tackle - Sweet Desire Waterfront Escape',
    'addr': 'Vero Beach, FL 32960',
    'zone': 'eastcoast', 'zl': 'Vero Beach', 'cat': 'to',
    'price': 29, 'lat': 27.6528, 'lng': -80.3704,
    'photo': 'uFR0XW6dSpy4YeHZsrR7',
    'link': 'https://fareharbor.com/embeds/book/verotackle/items/633360/calendar/2026/05/?asn=fhdn&asn-ref=miamistylerentals&ref=miamistylerentals&marketplace=yes&flow=no&full-items=yes',
    'badge': 'top', 'rating': 4.9, 'reviews': 1035,
    'desc': 'Waterfront escape cruise in Vero Beach with over 1,000 glowing reviews. From $29. 4.9 stars with 1,035 reviews. Scenic Indian River Lagoon boat tours on Florida\'s Treasure Coast.'
  },
  {
    'id': 'b559',
    'name': 'Power Up Watersports - Jet Ski Rental',
    'addr': 'Fort Walton Beach, FL 32548',
    'zone': 'destin', 'zl': 'Fort Walton Beach', 'cat': 'js',
    'price': 95, 'lat': 30.3994, 'lng': -86.6001,
    'photo': 'Z75gCCkRZWrRFcmyLRqD',
    'link': 'https://fareharbor.com/embeds/book/powerupwatersports/items/46710/calendar/2026/05/?asn=fhdn&asn-ref=miamistylerentals&ref=miamistylerentals&marketplace=yes&flow=no&full-items=yes',
    'badge': 'top', 'rating': 4.8, 'reviews': 976,
    'desc': 'Jet ski rentals on the emerald green waters of Fort Walton Beach. From $95. 4.8 stars with 976 reviews. Ride the Gulf of Mexico on a high-powered waverunner.'
  },
  {
    'id': 'b560',
    'name': 'Power Up Watersports - Pontoon Rental',
    'addr': 'Fort Walton Beach, FL 32548',
    'zone': 'destin', 'zl': 'Fort Walton Beach', 'cat': 'boat',
    'price': 225, 'lat': 30.3994, 'lng': -86.6001,
    'photo': 'JLIKYZekTOm0AnN9FaHy',
    'link': 'https://fareharbor.com/embeds/book/powerupwatersports/items/46740/calendar/2026/05/?asn=fhdn&asn-ref=miamistylerentals&ref=miamistylerentals&marketplace=yes&flow=no&full-items=yes',
    'badge': 'top', 'rating': 4.8, 'reviews': 986,
    'desc': 'Rent a 20-foot pontoon boat in Fort Walton Beach for the whole crew. From $225. 4.8 stars with 986 reviews. Cruise the bay or Choctawhatchee Bay at your own pace.'
  },
  {
    'id': 'b561',
    'name': 'Finz Dive Charters - Spearfishing',
    'addr': 'Key West, FL 33040',
    'zone': 'keywest', 'zl': 'Key West', 'cat': 'to',
    'price': 1050, 'lat': 24.5649, 'lng': -81.7282,
    'photo': '1DBwXKjeRvaXojtP1bJY',
    'link': 'https://fareharbor.com/embeds/book/finzdivecenter/items/76157/calendar/2026/05/?asn=fhdn&asn-ref=miamistylerentals&ref=miamistylerentals&marketplace=yes&flow=no&full-items=yes',
    'badge': 'top', 'rating': 4.9, 'reviews': 279,
    'desc': 'Spearfishing charter in the crystal-clear waters of Key West with expert guides. From $1,050. 4.9 stars with 279 reviews. Full-day reef spearfishing trips in the Florida Keys.'
  },
  {
    'id': 'b562',
    'name': 'Cruisin Tikis St. Augustine - Matanzas Bay Tours',
    'addr': 'St. Augustine, FL 32084',
    'zone': 'staugustine', 'zl': 'St. Augustine', 'cat': 'to',
    'price': 75, 'lat': 29.9184, 'lng': -81.3072,
    'photo': 'ppvH8RgRfhhQzx4G7C9A',
    'link': 'https://fareharbor.com/embeds/book/cruisintikissaugustine/items/225361/calendar/2026/05/?asn=fhdn&asn-ref=miamistylerentals&ref=miamistylerentals&marketplace=yes&flow=no&full-items=yes',
    'badge': 'top', 'rating': 4.9, 'reviews': 260,
    'desc': 'Tiki boat tours through historic Matanzas Bay in St. Augustine. From $75. 4.9 stars with 260 reviews. Cruise the oldest city in America on a floating tiki bar.'
  },
  {
    'id': 'b563',
    'name': 'Reel Floridian - Inshore Fishing Jupiter',
    'addr': 'Jupiter, FL 33458',
    'zone': 'ftlauderdale', 'zl': 'Jupiter', 'cat': 'to',
    'price': 695, 'lat': 26.9348, 'lng': -80.0942,
    'photo': 'ROPccPhRH6cJr2KY89Sh',
    'link': 'https://fareharbor.com/embeds/book/reelfloridianfishing/items/645016/calendar/2026/05/?asn=fhdn&asn-ref=miamistylerentals&ref=miamistylerentals&marketplace=yes&flow=no&full-items=yes',
    'badge': 'top', 'rating': 4.8, 'reviews': 184,
    'desc': 'Inshore fishing charters in Jupiter, FL targeting snook, redfish, and tarpon in shallow water. From $695. 4.8 stars with 184 reviews. Expert local guides on Jupiter\'s best fishing grounds.'
  },
]

existing_links = [o.get('link','') for o in ops]
added = []
for o in new_ops:
    slug = o['link'].split('/embeds/book/')[1].split('/')[0]
    item_id = o['link'].split('/items/')[1].split('/')[0]
    check = f"{slug}/items/{item_id}"
    if any(check in x for x in existing_links):
        print(f"SKIP {o['id']} {o['name']}: already exists")
    else:
        ops.append(o)
        added.append(o)
        print(f"ADD {o['id']} {o['name']}")

print(f"\nTotal operators: {len(ops)}")
print(f"Added: {len(added)}")

with open(f'{BASE}/operators.json', 'w') as f:
    json.dump(ops, f, indent=2)

slim = [{k:v for k,v in o.items() if k != 'desc'} for o in ops]
with open(f'{BASE}/operators-slim.json', 'w') as f:
    json.dump(slim, f, indent=2)

print("Saved operators.json and operators-slim.json")
