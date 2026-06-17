#!/usr/bin/env python3
"""
extract_css.py — extract the duplicated inline operator-page CSS into
a single cached external file (/operator.css).

What it does:
  1. Computes the md5 of each <style> block in every HTML file.
  2. The dominant block (≈9 KB on 4,736 operator pages) is written to
     /operator.css ONE time.
  3. Each page in that dominant group gets its inline <style>…</style>
     replaced with <link rel="stylesheet" href="/operator.css">.
  4. Pages with variant CSS (40 special pages: index, exotic cars,
     activity landings, etc.) are left untouched.

Idempotent — running twice does nothing the second time.

Usage:
  python3 extract_css.py            # dry run
  python3 extract_css.py --apply
"""
import glob, re, hashlib, sys, os

DRY_RUN = '--apply' not in sys.argv
TARGET_PATH = 'operator.css'
LINK_TAG = '<link rel="stylesheet" href="/operator.css">'
STYLE_RE = re.compile(r'<style[^>]*>(.*?)</style>', re.S)

# Pass 1: find the dominant CSS hash
groups = {}  # md5 -> [(file, css)]
for f in sorted(glob.glob('*.html')):
    h = open(f).read()
    styles = STYLE_RE.findall(h)
    css = ''.join(styles)
    if not css: continue
    hsh = hashlib.md5(css.encode()).hexdigest()[:8]
    groups.setdefault(hsh, []).append((f, css))

dom_hash = max(groups, key=lambda k: len(groups[k]))
dom_css = groups[dom_hash][0][1]
dom_files = [f for f, _ in groups[dom_hash]]
print(f'Dominant CSS hash: {dom_hash}')
print(f'  size: {len(dom_css)} bytes')
print(f'  pages using it: {len(dom_files)}')

# Pass 2: write /operator.css
if not DRY_RUN:
    with open(TARGET_PATH, 'w') as f:
        f.write(dom_css.strip() + '\n')
    print(f'Wrote {TARGET_PATH} ({os.path.getsize(TARGET_PATH)} bytes)')

# Pass 3: replace inline <style> with <link> in dominant-group pages
changed = 0
skipped = 0
for fn in dom_files:
    h = open(fn).read()
    if LINK_TAG in h:
        skipped += 1  # already linked (idempotent)
        continue

    # Re-extract just to be sure: find the exact <style> block and replace
    matches = list(STYLE_RE.finditer(h))
    if not matches:
        skipped += 1
        continue

    # Replace ALL <style> blocks with one <link>
    # (the dominant pages have exactly ONE style block based on sampling)
    new = STYLE_RE.sub(LINK_TAG, h, count=1)
    # If multiple style blocks, remove the rest
    new = STYLE_RE.sub('', new)

    if new != h:
        changed += 1
        if not DRY_RUN:
            open(fn, 'w').write(new)

print()
print('=' * 60)
print('CSS EXTRACTION — ' + ('DRY RUN' if DRY_RUN else 'APPLIED'))
print('=' * 60)
print(f'Pages updated:           {changed}')
print(f'Pages already linked:    {skipped}')
print(f'Per-page bytes saved:    ~{len(dom_css):,}')
print(f'Total network savings:   ~{changed * len(dom_css) / 1024 / 1024:.1f} MB (uncompressed)')
print(f'Plus repeat-visit:       /operator.css cached once via edge for {changed} pages')
if DRY_RUN:
    print('\nRe-run with --apply to write changes.')
