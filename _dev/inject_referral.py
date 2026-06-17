#!/usr/bin/env python3
"""
Inject Refstay referral script into all HTML files in this directory.

Idempotent — runs many times without duplicating. Safe to re-run after
generating new pages.

Usage:
    python3 inject_referral.py        # inject into all *.html
    python3 inject_referral.py --dry  # show what would change, don't write
"""

import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SCRIPT_TAG = '<script src="/referral.js" defer></script>'
MARKER = 'src="/referral.js"'  # used to detect "already injected"
DRY_RUN = '--dry' in sys.argv

def inject(html: str) -> tuple[str, bool]:
    """Return (new_html, changed)."""
    if MARKER in html:
        return html, False  # already there

    # Prefer to insert just before </body> (after existing inline scripts)
    body_close = re.search(r'</body\s*>', html, re.IGNORECASE)
    if body_close:
        idx = body_close.start()
        new = html[:idx] + SCRIPT_TAG + '\n' + html[idx:]
        return new, True

    # Fallback: insert before </html>
    html_close = re.search(r'</html\s*>', html, re.IGNORECASE)
    if html_close:
        idx = html_close.start()
        new = html[:idx] + SCRIPT_TAG + '\n' + html[idx:]
        return new, True

    # Last resort: append to end
    return html + '\n' + SCRIPT_TAG + '\n', True


def main():
    html_files = sorted(ROOT.glob('*.html'))
    n_total = len(html_files)
    n_changed = 0
    n_skipped_already = 0
    n_skipped_error = 0

    for fp in html_files:
        try:
            html = fp.read_text(encoding='utf-8', errors='replace')
        except Exception as e:
            print(f'  ! cannot read {fp.name}: {e}')
            n_skipped_error += 1
            continue

        new, changed = inject(html)
        if not changed:
            n_skipped_already += 1
            continue

        if DRY_RUN:
            print(f'  would inject: {fp.name}')
        else:
            fp.write_text(new, encoding='utf-8')
        n_changed += 1

    print(f'\n{"DRY RUN — " if DRY_RUN else ""}Done.')
    print(f'  Total HTML files:   {n_total}')
    print(f'  Newly injected:     {n_changed}')
    print(f'  Already had script: {n_skipped_already}')
    if n_skipped_error:
        print(f'  Read errors:        {n_skipped_error}')

if __name__ == '__main__':
    main()
