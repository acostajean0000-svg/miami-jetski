#!/usr/bin/env python3
"""
self_host_leaflet.py — eliminate unpkg.com supply-chain risk.

What it does:
  1. Downloads Leaflet 1.9.4 and Leaflet.markercluster 1.5.3 from unpkg
     into vendor/leaflet/ (5 files, ~190 KB total).
  2. Computes a SHA-384 SRI hash for each file.
  3. Rewrites index.html and boat-rentals-florida.html to:
       - Replace https://unpkg.com/leaflet@1.9.4/...  with /vendor/leaflet/...
       - Replace https://unpkg.com/leaflet.markercluster@1.5.3/...  with /vendor/leaflet/...
       - Add integrity="sha384-..." and crossorigin="anonymous" to each tag.
  4. Updates vercel.json CSP to:
       - Drop https://unpkg.com from script-src and style-src
       - Add a one-year immutable Cache-Control header for /vendor/leaflet/*
  5. Makes timestamped backups of every file before modifying it.

Idempotent: re-running just refreshes the files and re-computes hashes.

Why bother:
  Right now your homepage loads ~200 KB of JS from unpkg without integrity
  hashes. If unpkg is ever compromised (it has been before), the attacker
  would run arbitrary code on every visitor — including your booking form.
  Self-hosting + SRI + tightening CSP closes that hole entirely.

Run on your Mac (your sandbox doesn't matter; this needs internet):
  python3 self_host_leaflet.py            # dry run
  python3 self_host_leaflet.py --apply    # write changes
"""
import urllib.request, hashlib, base64, os, sys, re, json, shutil, datetime as dt

DRY_RUN = '--apply' not in sys.argv
BASE = os.path.dirname(os.path.abspath(__file__))
VENDOR = os.path.join(BASE, 'vendor', 'leaflet')

# Map upstream URL -> local filename
FILES = [
    ('https://unpkg.com/leaflet@1.9.4/dist/leaflet.css',
     'leaflet.css'),
    ('https://unpkg.com/leaflet@1.9.4/dist/leaflet.js',
     'leaflet.js'),
    ('https://unpkg.com/leaflet.markercluster@1.5.3/dist/MarkerCluster.css',
     'MarkerCluster.css'),
    ('https://unpkg.com/leaflet.markercluster@1.5.3/dist/MarkerCluster.Default.css',
     'MarkerCluster.Default.css'),
    ('https://unpkg.com/leaflet.markercluster@1.5.3/dist/leaflet.markercluster.js',
     'leaflet.markercluster.js'),
]

# Map upstream URL prefix -> local path prefix
URL_REWRITES = [
    ('https://unpkg.com/leaflet@1.9.4/dist/',          '/vendor/leaflet/'),
    ('https://unpkg.com/leaflet.markercluster@1.5.3/dist/', '/vendor/leaflet/'),
]

HTML_FILES = ['index.html', 'boat-rentals-florida.html']


def backup(path):
    ts = dt.datetime.utcnow().strftime('%Y%m%d-%H%M%S')
    bak = f'{path}.bak-{ts}'
    shutil.copy2(path, bak)
    return bak


def step1_download_and_hash():
    if not DRY_RUN:
        os.makedirs(VENDOR, exist_ok=True)
    sri_map = {}
    print(f'Vendor dir: {VENDOR}')
    print()
    for url, name in FILES:
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=30) as r:
                data = r.read()
        except Exception as e:
            print(f'  FAIL {url}\n    {e}')
            return None
        path = os.path.join(VENDOR, name)
        if not DRY_RUN:
            with open(path, 'wb') as f:
                f.write(data)
        sha384_b64 = base64.b64encode(hashlib.sha384(data).digest()).decode()
        sri_map[name] = f'sha384-{sha384_b64}'
        print(f'  OK  {name:<35} {len(data):>7} B  {sri_map[name]}')
    print()
    return sri_map


def step2_patch_html(sri_map):
    changes = 0
    for fname in HTML_FILES:
        path = os.path.join(BASE, fname)
        if not os.path.exists(path):
            print(f'  skip {fname} (missing)')
            continue
        html = open(path).read()
        original = html

        # Replace each upstream URL with local + add SRI/crossorigin attrs.
        # Approach: regex over <link ... href="UPSTREAM">  and <script ... src="UPSTREAM">,
        # and bare 'string' occurrences inside JS (s.src = 'UPSTREAM').
        for upstream_prefix, local_prefix in URL_REWRITES:
            # Walk through every occurrence of upstream URL
            for url, name in FILES:
                if not url.startswith(upstream_prefix):
                    continue
                local = local_prefix + name
                sri  = sri_map[name]
                # Pattern A: <link ... href="UPSTREAM" ...>   (CSS preload / stylesheet)
                # Pattern B: <script ... src="UPSTREAM" ...></script>
                # Pattern C: s.src = 'UPSTREAM';     (inside inline JS)
                # We just do plain substring replace for the URL itself.
                if url in html:
                    html = html.replace(url, local)
                # Pattern A/B add integrity attr if tag lacks one
                # Find tags pointing to the LOCAL path now, ensure integrity is set.
                tag_re = re.compile(
                    r'<(link|script)\b([^>]*?)(href|src)="' + re.escape(local) + r'"([^>]*)>',
                    re.I,
                )
                def add_sri(m):
                    tag, pre, attr, post = m.groups()
                    inside = pre + post
                    new = inside
                    if 'integrity=' not in inside:
                        new += f' integrity="{sri}"'
                    if 'crossorigin=' not in inside:
                        new += ' crossorigin="anonymous"'
                    return f'<{tag} {attr}="{local}"{new}>'
                html = tag_re.sub(add_sri, html)

        if html != original:
            if not DRY_RUN:
                bak = backup(path)
                with open(path, 'w') as f:
                    f.write(html)
                print(f'  patched {fname}  (backup: {os.path.basename(bak)})')
            else:
                print(f'  would patch {fname}')
            changes += 1
        else:
            print(f'  no change in {fname}')
    print()
    return changes


def step3_update_vercel_json():
    path = os.path.join(BASE, 'vercel.json')
    cfg = json.load(open(path))
    csp_header = next(
        (h for h in cfg['headers'][0]['headers'] if h['key'] == 'Content-Security-Policy'),
        None,
    )
    changed = False

    # Drop https://unpkg.com from CSP source lists
    if csp_header:
        new_csp = csp_header['value'].replace(' https://unpkg.com', '')
        if new_csp != csp_header['value']:
            csp_header['value'] = new_csp
            changed = True
            print('  CSP: removed https://unpkg.com from script-src + style-src')

    # Insert cache header for /vendor/leaflet/ (idempotent)
    has_vendor = any(h.get('source','').startswith('/vendor/leaflet') for h in cfg['headers'])
    if not has_vendor:
        cfg['headers'].insert(-1, {
            "source": "/vendor/leaflet/(.*)",
            "headers": [
                {"key": "Cache-Control", "value": "public, max-age=31536000, immutable"},
            ],
        })
        changed = True
        print('  added /vendor/leaflet/* one-year immutable cache header')

    if changed and not DRY_RUN:
        bak = backup(path)
        with open(path, 'w') as f:
            json.dump(cfg, f, separators=(',', ':'))
        print(f'  wrote vercel.json (backup: {os.path.basename(bak)})')
    elif changed:
        print(f'  would update vercel.json')
    else:
        print(f'  vercel.json already up to date')


def main():
    print('=' * 60)
    print('SELF-HOST LEAFLET — ' + ('DRY RUN' if DRY_RUN else 'APPLYING'))
    print('=' * 60)
    print()

    print('Step 1 — download + hash')
    print('-' * 40)
    sri_map = step1_download_and_hash()
    if sri_map is None:
        print('Aborting: download failed.')
        return 1

    print('Step 2 — patch HTML files')
    print('-' * 40)
    step2_patch_html(sri_map)

    print('Step 3 — update vercel.json')
    print('-' * 40)
    step3_update_vercel_json()

    print()
    print('=' * 60)
    if DRY_RUN:
        print('DRY RUN complete. Re-run with --apply to write changes.')
    else:
        print('Done. Verify, then run miamijetskiboat.command to deploy.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
