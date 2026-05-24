#!/usr/bin/env python3
"""Apply recovered FareHarbor booking URLs from a fetch_missing_links.js scrape.

Workflow:
  1. Run fetch_missing_links.js in Chrome DevTools (signed into FH).
  2. Save its JSON output as unique_links.json in this folder.
  3. python3 apply_unique_links.py

Input shape (unique_links.json):
  { "op_id": "https://fareharbor.com/embeds/book/<slug>/items/<id>/...", ... }

Updates operators.json and operators-slim.json. Reports stats and any operators
still without a link afterward.
"""
import json
import os
import sys
from collections import Counter

BASE = os.path.dirname(os.path.abspath(__file__))


def main() -> int:
    map_path = os.path.join(BASE, "unique_links.json")
    if not os.path.exists(map_path):
        print(f"error: {map_path} not found", file=sys.stderr)
        print("  Run fetch_missing_links.js in Chrome first, then save its", file=sys.stderr)
        print("  output as unique_links.json in this folder.", file=sys.stderr)
        return 2

    mapping = json.load(open(map_path))
    if not isinstance(mapping, dict):
        print("error: unique_links.json must be an object of {op_id: url}", file=sys.stderr)
        return 2

    for fn in ("operators.json", "operators-slim.json"):
        ops = json.load(open(os.path.join(BASE, fn)))
        by_id = {o["id"]: o for o in ops}

        applied = 0
        skipped_already = 0
        skipped_unknown = 0
        for op_id, url in mapping.items():
            op = by_id.get(op_id)
            if not op:
                skipped_unknown += 1
                continue
            if op.get("link"):
                skipped_already += 1
                continue
            op["link"] = url
            applied += 1

        with open(os.path.join(BASE, fn), "w") as f:
            json.dump(ops, f, ensure_ascii=False, separators=(",", ":"))

        print(f"{fn}: applied {applied} new links "
              f"(skipped {skipped_already} already had a link, {skipped_unknown} unknown ids)")

    # Post-check on the full file
    ops = json.load(open(os.path.join(BASE, "operators.json")))
    no_link = sum(1 for o in ops if not o.get("link"))
    with_link = len(ops) - no_link
    print(f"\nAfter: {with_link} operators with link, {no_link} still without (will show 'Contact for booking')")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
