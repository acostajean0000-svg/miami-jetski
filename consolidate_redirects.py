#!/usr/bin/env python3
"""
consolidate_redirects.py — small but real cleanup of vercel.json redirects.

Honest assessment of #8: vercel.json has 750 redirects.
  - 730 are unique legacy-URL → zone-landing mappings (must stay individual,
    each has a different destination)
  - 13 are /es/<page> → /<same-page> (redundant; one regex can replace them)
  - 5 are /es/<page> → /<different-page> (must stay individual; come BEFORE
    the catchall so they win the ordered match)
  - The remainder are domain-level alias redirects.

Net possible saving: 12 entries (1.6%). Not a huge perf win, but cleaner.
Vercel's 2,048-redirect limit is far away regardless.

What this script does:
  1. Removes the 13 redundant /es/<page> → /<same-page> redirects
  2. Inserts ONE catchall: {/es/:path* → /:path*}
  3. Leaves the 5 special-case /es/<...> rules in place (they're listed before
     the catchall so they match first)
  4. Makes a backup of vercel.json before modifying

Idempotent.

Usage:
  python3 consolidate_redirects.py            # dry run
  python3 consolidate_redirects.py --apply
"""
import json, sys, os, shutil, datetime as dt

DRY_RUN = '--apply' not in sys.argv
PATH = 'vercel.json'

cfg = json.load(open(PATH))
old = cfg['redirects']

# Identify /es/<page> → /<same-page> redirects (redundant)
redundant = []
keep = []
for r in old:
    s = r.get('source', '')
    d = r.get('destination', '')
    if s.startswith('/es/') and d == '/' + s[4:].rstrip('/'):
        redundant.append(r)
    else:
        keep.append(r)

print(f'Total redirects before:  {len(old)}')
print(f'Redundant /es/x → /x:    {len(redundant)}')

# Add the regex catchall (Vercel uses :path* syntax). Place after the existing
# /es/x → /something-else rules but before the rest.
catchall = {
    "source": "/es/:path*",
    "destination": "/:path*",
    "permanent": True,
}

# Insert catchall AFTER the last existing /es/ specific redirect so it wins
# only when no specific /es/ rule matches.
last_es_idx = max(
    (i for i, r in enumerate(keep) if r.get('source', '').startswith('/es/')),
    default=-1,
)
already_has_catchall = any(r.get('source') == catchall['source'] for r in keep)
if already_has_catchall:
    print('Catchall /es/:path* → /:path* already present, skipping insert')
    new = keep
else:
    new = keep[:last_es_idx + 1] + [catchall] + keep[last_es_idx + 1:]

cfg['redirects'] = new

print(f'Total redirects after:   {len(new)}  (saved {len(old) - len(new)})')

# Verify size diff
import io
old_str = json.dumps({'redirects': old}, separators=(',', ':'))
new_str = json.dumps({'redirects': new}, separators=(',', ':'))
print(f'JSON bytes saved:        {len(old_str) - len(new_str)}')

if DRY_RUN:
    print()
    print('DRY RUN — re-run with --apply to write changes.')
    sys.exit(0)

# backup
ts = dt.datetime.utcnow().strftime('%Y%m%d-%H%M%S')
bak = f'{PATH}.bak-{ts}'
shutil.copy2(PATH, bak)
with open(PATH, 'w') as f:
    json.dump(cfg, f, separators=(',', ':'))
print(f'Wrote {PATH}  (backup: {bak})')
