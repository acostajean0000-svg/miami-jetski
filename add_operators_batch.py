#!/usr/bin/env python3
import json, re, os
from datetime import date

import os as _os
BASE = _os.path.dirname(_os.path.abspath(__file__))

with open(f'{BASE}/operators.json') as f:
    ops = json.load(f)

new_ops = [
  {
    'id': 'b520',
    'name': 'Destin Tikis - Sandbar Cruise',
    'addr': 'Destin, FL 32541',
    'zone': 'destin', 'zl': 'Destin', 'cat': 'to',
    'price': 75, 'lat': 30.3927, 'lng': -86.5056,
    'photo': 'LnUVWI4T9O6VS3DujVtC',
    'link': 'https://fareharbor.com/embeds/book/destintikis/items/103456/calendar/2026/05/?asn=fhdn&asn-ref=miamistylerentals&ref=miamistylerentals&marketplace=yes&flow=no&full-items=yes',
    'badge': 'top', 'rating': 4.9, 'reviews': 1834,
    'desc': 'Float on a tiki bar through Destin emerald waters on a sandbar swim-stop cruise. From $75. 4.9 stars with 1,834 reviews. Perfect for groups and sunset fun.'
  },
  {
    'id': 'b521',
    'name': 'Naples Tiki Fun Tours',
    'addr': 'Naples, FL 34102',
    'zone': 'naples', 'zl': 'Naples', 'cat': 'to',
    'price': 59, 'lat': 26.1338, 'lng': -81.7923,
    'photo': '3t5jsdazQui9VVQ64xsM',
    'link': 'https://fareharbor.com/embeds/book/cruisintikisnaples/items/158308/calendar/2026/05/?asn=fhdn&asn-ref=miamistylerentals&ref=miamistylerentals&marketplace=yes&flow=no&full-items=yes',
    'badge': 'popular', 'rating': 4.9, 'reviews': 204,
    'desc': 'Tiki boat cruises through Naples Bay with BYOB fun and dolphin spotting. From $59. 4.9 stars with 204 reviews. 90-minute cruises departing daily.'
  },
  {
    'id': 'b522',
    'name': 'Freaky Tiki Boat Charters',
    'addr': 'Fort Lauderdale, FL 33312',
    'zone': 'ftlauderdale', 'zl': 'Fort Lauderdale', 'cat': 'to',
    'price': 650, 'lat': 26.111, 'lng': -80.1183,
    'photo': 'lV1e7jRT5e51UHh4H9Fe',
    'link': 'https://fareharbor.com/embeds/book/freakytikicharters/items/569170/calendar/2026/05/?asn=fhdn&asn-ref=miamistylerentals&ref=miamistylerentals&marketplace=yes&flow=no&full-items=yes',
    'badge': 'top', 'rating': 5.0, 'reviews': 300,
    'desc': 'Private tiki boat charters through Fort Lauderdale Intracoastal Waterway with a 2-hour adventure cruise. From $650. 5.0 stars with 300 reviews. Perfect for private parties.'
  },
  {
    'id': 'b523',
    'name': 'J2 Boats - Madeira Beach',
    'addr': 'Madeira Beach, FL 33708',
    'zone': 'tampa', 'zl': 'Madeira Beach', 'cat': 'boat',
    'price': 349, 'lat': 27.7883, 'lng': -82.7856,
    'photo': '2xK99DkrQAGI2J8hDSLi',
    'link': 'https://fareharbor.com/embeds/book/j2boats/items/604564/calendar/2026/05/?asn=fhdn&asn-ref=miamistylerentals&ref=miamistylerentals&marketplace=yes&flow=no&full-items=yes',
    'badge': 'top', 'rating': 5.0, 'reviews': 130,
    'desc': 'Rent a pontoon boat in Madeira Beach for up to 12 passengers and cruise the Gulf and Boca Ciega Bay. From $349. 5.0 stars with 130 reviews. Daily rentals available.'
  },
  {
    'id': 'b524',
    'name': 'Salty Sandbars - Key West',
    'addr': 'Key West, FL 33040',
    'zone': 'keywest', 'zl': 'Key West', 'cat': 'boat',
    'price': 489, 'lat': 24.5608, 'lng': -81.7874,
    'photo': '97YpXVC8TsimKfG0wcKF',
    'link': 'https://fareharbor.com/embeds/book/saltysandbars/items/637746/calendar/2026/05/?asn=fhdn&asn-ref=miamistylerentals&ref=miamistylerentals&marketplace=yes&flow=no&full-items=yes',
    'badge': 'top', 'rating': 4.9, 'reviews': 174,
    'desc': 'Private sandbar excursions aboard a Boston Whaler in Key West - snorkel, swim, and explore. From $489. 4.9 stars with 174 reviews. 2-hour sandbar tours in paradise.'
  },
  {
    'id': 'b525',
    'name': 'Low Tide Tours - Venice',
    'addr': 'Venice, FL 34285',
    'zone': 'gulf', 'zl': 'Venice', 'cat': 'to',
    'price': 30, 'lat': 27.1091, 'lng': -82.4626,
    'photo': 'rXbEMOG6QQSpcnRYFVC6',
    'link': 'https://fareharbor.com/embeds/book/lowtidetours/items/334561/calendar/2026/05/?asn=fhdn&asn-ref=miamistylerentals&ref=miamistylerentals&marketplace=yes&flow=no&full-items=yes',
    'badge': 'top', 'rating': 4.9, 'reviews': 649,
    'desc': 'Scenic boat cruises along Venice and Sarasota coastline with dolphins and sunset views. From $30. 4.9 stars with 649 reviews.'
  },
  {
    'id': 'b526',
    'name': 'Explorida - Manatee Cruise',
    'addr': 'Crystal River, FL 34428',
    'zone': 'crystalriver', 'zl': 'Crystal River', 'cat': 'to',
    'price': 35, 'lat': 28.899, 'lng': -82.5928,
    'photo': 'vO9vafpGTZiyOwg2oXbL',
    'link': 'https://fareharbor.com/embeds/book/explorida/items/282638/calendar/2026/05/?asn=fhdn&asn-ref=miamistylerentals&ref=miamistylerentals&marketplace=yes&flow=no&full-items=yes',
    'badge': 'top', 'rating': 4.9, 'reviews': 1091,
    'desc': 'Guided manatee viewing and eco cruises through Crystal River spring-fed waterways. From $35. 4.9 stars with 1,091 reviews. Swim with manatees in their natural habitat.'
  },
  {
    'id': 'b527',
    'name': 'Island Hoppers Boat Tours',
    'addr': 'Holmes Beach, FL 34217',
    'zone': 'gulf', 'zl': 'Anna Maria Island', 'cat': 'to',
    'price': 800, 'lat': 27.4976, 'lng': -82.7025,
    'photo': 'x2zgQ0dJT96fths2UjU2',
    'link': 'https://fareharbor.com/embeds/book/islandhoppersboattours/items/556274/calendar/2026/05/?asn=fhdn&asn-ref=miamistylerentals&ref=miamistylerentals&marketplace=yes&flow=no&full-items=yes',
    'badge': 'top', 'rating': 5.0, 'reviews': 364,
    'desc': 'Private catamaran and pontoon boat tours around Anna Maria Island - beach-hopping and dolphin watching. From $800. 5.0 stars with 364 reviews.'
  },
  {
    'id': 'b528',
    'name': "Tom and Jerry's Airboat Rides",
    'addr': 'Lake Panasoffkee, FL 33538',
    'zone': 'centralfl', 'zl': 'Lake Panasoffkee', 'cat': 'to',
    'price': 35, 'lat': 28.7688, 'lng': -82.0723,
    'photo': 'OIOJquMCS3tQmDP5Q23P',
    'link': 'https://fareharbor.com/embeds/book/airboattoursorlando/items/580515/calendar/2026/05/?asn=fhdn&asn-ref=miamistylerentals&ref=miamistylerentals&marketplace=yes&flow=no&full-items=yes',
    'badge': 'top', 'rating': 4.8, 'reviews': 3145,
    'desc': 'Exhilarating 1-hour airboat tours through wild Florida swamps of Lake Panasoffkee with gators and native wildlife. From $35. 4.8 stars with 3,145 reviews.'
  },
]

# Check for duplicates
existing_links = [o.get('link','') for o in ops]
added = []
for o in new_ops:
    slug = o['link'].split('/embeds/book/')[1].split('/')[0]
    dupes = [x for x in existing_links if slug in x]
    if dupes:
        print(f"SKIP {o['id']} {o['name']}: already exists")
    else:
        ops.append(o)
        added.append(o)
        print(f"ADD {o['id']} {o['name']}")

print(f"\nTotal operators: {len(ops)}")
print(f"Added: {len(added)}")

# Save operators.json
with open(f'{BASE}/operators.json', 'w') as f:
    json.dump(ops, f, indent=2)

# Save operators-slim.json (no desc field)
slim = [{k:v for k,v in o.items() if k != 'desc'} for o in ops]
with open(f'{BASE}/operators-slim.json', 'w') as f:
    json.dump(slim, f, indent=2)

print("Saved operators.json and operators-slim.json")
