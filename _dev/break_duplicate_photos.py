#!/usr/bin/env python3
"""Break duplicate photos in operators.json so every operator card is unique.

Strategy: for each cluster of operators sharing a photo, keep the canonical
operator (first by id) with the original photo. Reassign the rest to a
deterministic Lorem Picsum URL keyed by operator id — guaranteed unique,
guaranteed available.

Picsum returns generic high-quality photos (landscapes, scenes, objects).
The cards become visually distinct immediately. You can refine to real
FareHarbor item photos later by running fetch_unique_item_images.js in
your browser and then apply_unique_images.py — that pass will overwrite
these Picsum URLs with real operator photos.

Idempotent: rerunning is a no-op once duplicates are gone. Records that
already have a picsum URL are skipped.
"""
import json
import os
import re
from collections import defaultdict

BASE = os.path.dirname(os.path.abspath(__file__))


# Category-specific seed prefix so Picsum's random selection is at least
# nudged toward different photos across categories. Picsum doesn't filter
# by theme, but different seeds produce visually different images.
CAT_PREFIX = {
    "jetski":      "jetski",
    "boat":        "boat",
    "fishing":     "fishing",
    "watersports": "ws",
    "slingshot":   "sling",
    "tour":        "tour",
    "jetcar":      "jetcar",
    "atv":         "atv",
    "golfcart":    "gc",
    "aerial":      "aerial",
    "bikerental":  "bike",
}


def picsum_url(cat: str, op_id: str) -> str:
    prefix = CAT_PREFIX.get(cat, "fl")
    seed = f"{prefix}-{op_id}"
    # 800×533 matches what cardHTML expects (width=400 in card * 2x retina).
    return f"https://picsum.photos/seed/{seed}/800/533"


def main() -> int:
    path = os.path.join(BASE, "operators.json")
    ops = json.load(open(path))

    # Group by current photo URL.
    clusters = defaultdict(list)
    for o in ops:
        clusters[o.get("photo", "")].append(o)

    # Decide reassignments. Keep the first operator (by id sort) in each
    # duplicate cluster; rewrite the rest.
    used = set()
    for url, group in clusters.items():
        used.add(url)

    reassigned = 0
    for url, group in clusters.items():
        if len(group) < 2:
            continue
        # Stable canonical pick: lowest op-id within the cluster.
        group.sort(key=lambda o: o["id"])
        canonical = group[0]
        for o in group[1:]:
            new = picsum_url(o.get("cat", ""), o["id"])
            # In the (extremely unlikely) event two Picsum seeds collide,
            # append a salt until unique.
            salt = 0
            while new in used:
                salt += 1
                new = picsum_url(o.get("cat", ""), f"{o['id']}-{salt}")
            o["photo"] = new
            used.add(new)
            reassigned += 1

    # Write back operators.json + operators-slim.json
    with open(path, "w") as f:
        json.dump(ops, f, ensure_ascii=False, indent=2)
        f.write("\n")
    slim = [{k: v for k, v in o.items() if k != "desc"} for o in ops]
    with open(os.path.join(BASE, "operators-slim.json"), "w") as f:
        json.dump(slim, f, ensure_ascii=False, indent=2)
        f.write("\n")

    # Verify
    post = defaultdict(list)
    for o in ops:
        post[o["photo"]].append(o["id"])
    dupes = {p: ids for p, ids in post.items() if len(ids) > 1}

    print(f"Reassigned {reassigned} photos.")
    print(f"Operators: {len(ops)}")
    print(f"Unique photo URLs after: {len(post)}")
    print(f"Remaining duplicates: {len(dupes)}")
    if dupes:
        print("  Remaining duplicate clusters:")
        for p, ids in dupes.items():
            print(f"    {len(ids)}x  {p[:80]}")
            print(f"        ids: {ids}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
