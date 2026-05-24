#!/usr/bin/env python3
import json, re

import os as _os
BASE = _os.path.dirname(_os.path.abspath(__file__))

with open(f'{BASE}/operators.json') as f:
    ops = json.load(f)

new_ops = [
  {
    'id': 'b552',
    'name': 'Key West Tiki Boat Rental',
    'addr': '3841 N Roosevelt Blvd, Key West, FL 33040',
    'zone': 'keywest', 'zl': 'Key West', 'cat': 'to',
    'price': 650, 'lat': 24.571092, 'lng': -81.752055,
    'photo': 'R3dsXWVKTZiosM9gFVzy',
    'link': 'https://fareharbor.com/embeds/book/keywesttikiboat/items/467583/calendar/2026/05/?asn=fhdn&asn-ref=miamistylerentals&ref=miamistylerentals&marketplace=yes&flow=no&full-items=yes',
    'badge': 'top', 'rating': 5.0, 'reviews': 558,
    'desc': 'Rent a self-captained tiki boat in Key West for up to 6 people and cruise the warm waters. From $650. 5.0 stars with 558 reviews. No experience needed — tiki boat rental in paradise.'
  },
  {
    'id': 'b553',
    'name': 'Wave Cutter Charters - Dolphin Cruise',
    'addr': 'Pensacola Beach, FL 32561',
    'zone': 'destin', 'zl': 'Pensacola Beach', 'cat': 'to',
    'price': 30, 'lat': 30.3355, 'lng': -87.1442,
    'photo': '4oize8IgRXaFAc8nuuGh',
    'link': 'https://fareharbor.com/embeds/book/wavecuttercharters/items/359527/calendar/2026/05/?asn=fhdn&asn-ref=miamistylerentals&ref=miamistylerentals&marketplace=yes&flow=no&full-items=yes',
    'badge': 'top', 'rating': 5.0, 'reviews': 3437,
    'desc': 'Dolphin cruise along the Pensacola Beach coastline with guaranteed wildlife sightings. From $30. 5.0 stars with 3,437 reviews. Most-reviewed dolphin cruise on the Florida Panhandle.'
  },
  {
    'id': 'b554',
    'name': 'Breezy Tiki - Private Charter',
    'addr': '1440 N Federal Hwy, Fort Lauderdale, FL 33304',
    'zone': 'ftlauderdale', 'zl': 'Fort Lauderdale', 'cat': 'to',
    'price': 1100, 'lat': 26.124146, 'lng': -80.103833,
    'photo': 'oSWdRJ2ESheS6nO0QgIO',
    'link': 'https://fareharbor.com/embeds/book/breezytiki/items/98494/calendar/2026/05/?asn=fhdn&asn-ref=miamistylerentals&ref=miamistylerentals&marketplace=yes&flow=no&full-items=yes',
    'badge': 'top', 'rating': 4.9, 'reviews': 509,
    'desc': 'Six-hour private tiki boat charter through Fort Lauderdale waterways. From $1100. 4.9 stars with 509 reviews. Perfect for private groups and celebrations on the water.'
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
