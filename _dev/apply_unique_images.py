#!/usr/bin/env python3
"""Apply unique per-operator photos from a FareHarbor scrape result.

Workflow:
  1. Run fetch_unique_item_images.js in Chrome DevTools (signed into FH).
  2. Save its JSON output as unique_images.json in this folder.
  3. python3 apply_unique_images.py

Input shape (unique_images.json):
  { "op_id": "FilestackHandle", ... }

Updates operators.json and operators-slim.json. Also reports any operators
still carrying a duplicated photo afterward (so you know which ones the
FareHarbor API couldn't differentiate).
"""
import json
import os
import re
import sys
from collections import Counter, defaultdict

BASE = os.path.dirname(os.path.abspath(__file__))

# Same Filestack URL shape clean_operators_data / apply_real_images already use.
PHOTO_TEMPLATE = (
    "https://cdn.filestackcontent.com/{handle}/convert"
    "?cache=true&compress=true&quality=90&format=webp&rotate=exif&w=800&fit=max"
)


def main() -> int:
    map_path = os.path.join(BASE, "unique_images.json")
    if not os.path.exists(map_path):
        print(f"error: {map_path} not found", file=sys.stderr)
        print("  Run fetch_unique_item_images.js in Chrome first, then save its", file=sys.stderr)
        print("  output as unique_images.json in this folder.", file=sys.stderr)
        return 2

    mapping = json.load(open(map_path))
    if not isinstance(mapping, dict):
        print("error: unique_images.json must be an object of {op_id: handle}", file=sys.stderr)
        return 2

    ops = json.load(open(os.path.join(BASE, "operators.json")))
    op_by_id = {o["id"]: o for o in ops}

    applied, skipped_unknown, skipped_same = 0, 0, 0
    for op_id, handle in mapping.items():
        op = op_by_id.get(op_id)
        if not op:
            skipped_unknown += 1
            continue
        # Don't rewrite if the handle is already the same.
        cur = re.search(r"filestackcontent\.com/([A-Za-z0-9]{10,30})", op.get("photo", "") or "")
        if cur and cur.group(1) == handle:
            skipped_same += 1
            continue
        op["photo"] = PHOTO_TEMPLATE.format(handle=handle)
        applied += 1

    print(f"Applied {applied} new photos. Skipped {skipped_same} unchanged, {skipped_unknown} unknown ids.")

    # Write back full + slim
    with open(os.path.join(BASE, "operators.json"), "w") as f:
        json.dump(ops, f, ensure_ascii=False, indent=2)
        f.write("\n")
    slim = [{k: v for k, v in o.items() if k != "desc"} for o in ops]
    with open(os.path.join(BASE, "operators-slim.json"), "w") as f:
        json.dump(slim, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print("Updated operators.json and operators-slim.json")

    # Post-check: which photos are still duplicated?
    photo_count: dict[str, list[str]] = defaultdict(list)
    for o in ops:
        photo_count[o.get("photo", "")].append(o["id"])
    dupes = {p: ids for p, ids in photo_count.items() if len(ids) > 1 and p}
    still_dup_ops = sum(len(v) for v in dupes.values())
    print(f"\nRemaining duplicates: {len(dupes)} photo URL(s) shared by {still_dup_ops} operators")
    if dupes:
        for p, ids in sorted(dupes.items(), key=lambda kv: -len(kv[1]))[:5]:
            handle = (re.search(r"filestackcontent\.com/([A-Za-z0-9]{10,30})", p) or [None, "?"])[1]
            print(f"  {len(ids)}× handle={handle} ids={ids[:8]}{'…' if len(ids)>8 else ''}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
