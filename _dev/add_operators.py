#!/usr/bin/env python3
"""Append new operator records to operators.json.

Replaces the seven hand-written add_b*.py scripts. Pass a JSON batch file:

    python3 add_operators.py path/to/batch.json

Where batch.json is a JSON array of operator records. Each record needs at
least an `id` (unique). The script:
  * skips records whose `id` is already present in operators.json,
  * appends new records,
  * rewrites operators-slim.json (drops `desc`),
  * and emits a summary.

Idempotent: rerunning with the same batch is a no-op.
"""
import argparse
import json
import os
import sys

BASE = os.path.dirname(os.path.abspath(__file__))


def load(path: str):
    with open(path) as f:
        return json.load(f)


def save(path: str, data) -> None:
    with open(path, "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("batch", help="JSON file containing an array of new operator records")
    p.add_argument(
        "--dry-run", action="store_true", help="Show what would change, write nothing"
    )
    args = p.parse_args()

    if not os.path.exists(args.batch):
        print(f"error: batch file not found: {args.batch}", file=sys.stderr)
        return 2

    ops = load(os.path.join(BASE, "operators.json"))
    new_ops = load(args.batch)
    if not isinstance(new_ops, list):
        print("error: batch must be a JSON array", file=sys.stderr)
        return 2

    existing_ids = {o["id"] for o in ops}
    added, skipped = [], []
    for o in new_ops:
        if "id" not in o:
            print(f"  skip (no id): {o.get('name', '<unnamed>')}")
            skipped.append(o)
            continue
        if o["id"] in existing_ids:
            print(f"  skip (duplicate id): {o['id']}")
            skipped.append(o)
            continue
        ops.append(o)
        existing_ids.add(o["id"])
        added.append(o)

    print(f"\nSummary: +{len(added)} new, {len(skipped)} skipped, total now {len(ops)}")
    if args.dry_run:
        print("(dry run — not writing)")
        return 0

    save(os.path.join(BASE, "operators.json"), ops)
    slim = [{k: v for k, v in o.items() if k != "desc"} for o in ops]
    save(os.path.join(BASE, "operators-slim.json"), slim)
    print("Wrote operators.json and operators-slim.json")
    print("Next: run regen_slug_maps.py to update slug-map.js and REV_SLUG.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
