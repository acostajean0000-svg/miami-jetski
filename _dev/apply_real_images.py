#!/usr/bin/env python3
"""
Apply real Filestack image IDs to operators.json, operators-slim.json,
and all hub pages HTML files.

Usage:
  1. Run fetch_missing_images.js in Chrome → copy the JSON output
  2. Paste it as the REAL_IMGS dict below
  3. Run: python3 apply_real_images.py
"""
import json, os, re

BASE = os.path.dirname(os.path.abspath(__file__))

# ── PASTE CHROME OUTPUT HERE ──
REAL_IMGS = {
    # "slug": "FilestackID",
    # e.g. "powerupwatersports": "ABC123xyz",
}
# ─────────────────────────────

def make_photo_url(img_id):
    return f"https://cdn.filestackcontent.com/{img_id}/convert?cache=true&compress=true&quality=90&format=webp&rotate=exif&w=800&fit=max"

def extract_slug(link):
    m = re.search(r'fareharbor\.com/embeds/book/([^/]+)/', link)
    return m.group(1) if m else None

# ── Fix operators.json ──
with open(f"{BASE}/operators.json") as f:
    ops = json.load(f)

fixed = 0
fixed_names = []
for op in ops:
    slug = extract_slug(op.get('link', ''))
    if slug and slug in REAL_IMGS:
        new_photo = make_photo_url(REAL_IMGS[slug])
        old_photo = op.get('photo', '')
        if old_photo != new_photo:
            op['photo'] = new_photo
            fixed += 1
            fixed_names.append((op['id'], op['name'], slug, REAL_IMGS[slug]))

print(f"Fixed {fixed} operators in operators.json")
with open(f"{BASE}/operators.json", 'w') as f:
    json.dump(ops, f, separators=(',', ':'))

# ── Fix operators-slim.json ──
with open(f"{BASE}/operators-slim.json") as f:
    slim = json.load(f)

fixed_slim = 0
for op in slim:
    slug = extract_slug(op.get('link', ''))
    if slug and slug in REAL_IMGS:
        new_photo = make_photo_url(REAL_IMGS[slug])
        if op.get('photo', '') != new_photo:
            op['photo'] = new_photo
            fixed_slim += 1

print(f"Fixed {fixed_slim} operators in operators-slim.json")
with open(f"{BASE}/operators-slim.json", 'w') as f:
    json.dump(slim, f, separators=(',', ':'))

# ── Fix hub HTML pages ──
HUB_FILES = [
    f"{BASE}/miami-activities.html",
    f"{BASE}/key-west-activities.html",
    f"{BASE}/fort-lauderdale-activities.html",
    f"{BASE}/gulf-coast-activities.html",
    f"{BASE}/west-florida-activities.html",
    f"{BASE}/palm-beach-activities.html",
    f"{BASE}/space-coast-activities.html",
    f"{BASE}/jacksonville-activities.html",
]

# Build old_id → new_id replacement map
OLD_IDS = {}
for op in ops:
    slug = extract_slug(op.get('link', ''))
    if slug and slug in REAL_IMGS:
        # Find old img ID from original photo (before fix)
        # We need to match cards in HTML - use op name to find card then fix src
        pass

# Better approach: for each hub page, find img srcs with old fake IDs and replace
# Build a comprehensive old→new ID map

# Re-read original (before our fix above) - we already updated ops in memory
# Use the fixed_names list instead
old_new_map = {}
for op_id, name, slug, new_id in fixed_names:
    # Find what old ID was - it's one of the shared fake ones
    # We'll replace by matching operator name in comment
    old_new_map[name] = new_id

html_fixed_total = 0
for fp in HUB_FILES:
    try:
        with open(fp) as f:
            html = f.read()
    except FileNotFoundError:
        continue

    original = html
    changes = 0

    for name, new_id in old_new_map.items():
        # Find the comment block for this operator and fix its img src
        # Pattern: <!-- N. Name – ... --> ... <img src="...filestackcontent.com/.../OldID">
        new_url = f"https://cdn.filestackcontent.com/rotate=deg:exif/resize=width:800/quality=value:75/auto_image/compress/cache=expiry:max/{new_id}"

        # Find the card block for this operator
        # Match comment + following img tag (within the same card block)
        pattern = rf'(<!-- \d+\. {re.escape(name)} –[^>]*>.*?<img src=")[^"]+(")'
        new_html = re.sub(pattern, rf'\g<1>{new_url}\g<2>', html, flags=re.DOTALL)
        if new_html != html:
            html = new_html
            changes += 1

    if html != original:
        with open(fp, 'w') as f:
            f.write(html)
        print(f"{fp.split('/')[-1]}: fixed {changes} card images")
        html_fixed_total += changes

print(f"\n✅ Total hub page image fixes: {html_fixed_total}")
print(f"\nFixed operators:")
for op_id, name, slug, new_id in fixed_names:
    print(f"  {op_id} | {name} | {slug} → {new_id}")
