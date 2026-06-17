#!/usr/bin/env python3
"""One-shot cleaner for operators.json.

Fixes:
- Leaked ID-prefix categories (to, js, b, bt, fi, ws) -> real category names.
- Off-enum categories (kayak, snorkel, bike, scooter) -> mapped buckets.
- Off-enum zones (16 codes) -> canonical zones with proper zl display labels.
- Empty addr fields -> '{zl}, FL' placeholder.
- price == 0 -> null (template will render 'Contact for pricing').
- Punta Cana records get country='DO' and a clear zl.

Writes back to operators.json and operators-slim.json (slim drops 'desc').
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))

CAT_MAP = {
    # ID-prefix leakage
    "to": "tour",
    "js": "jetski",
    "bt": "boat",
    "fi": "fishing",
    "ws": "watersports",
    "b":  "watersports",   # all 15 'b' records are kayak/snorkel/paddle tours
    # off-enum -> nearest bucket recognized by CAT_LABELS
    "kayak":   "watersports",
    "snorkel": "watersports",
    "bike":    "bikerental",
    "scooter": "bikerental",
}

# Map off-enum zone codes to (canonical_zone, default_zl_display_name).
ZONE_MAP = {
    "keywest":      ("keys",      "Key West"),
    "tampa":        ("westfl",    "Tampa"),
    "destin":       ("westfl",    "Destin"),
    "naples":       ("gulf",      "Naples"),
    "crystalriver": ("westfl",    "Crystal River"),
    "orlando":      ("centralfl", "Orlando"),
    "gainesville": ("nefl",       "Gainesville"),
    "ftmyers":      ("gulf",      "Fort Myers"),
    "ftlauderdale": ("broward",   "Fort Lauderdale"),
    "daytona":      ("nefl",      "Daytona Beach"),
    "jacksonville": ("nefl",      "Jacksonville"),
    "eastcoast":    ("space",     "East Coast"),
    "staugustine":  ("nefl",      "St. Augustine"),
    "florida":      ("centralfl", "Florida"),
    "central":      ("centralfl", "Central Florida"),
    "northeast":    ("nefl",      "Northeast Florida"),
    # Punta Cana is special: keep as separate zone (template will label it).
    "puntacana":    ("puntacana", "Punta Cana, Dominican Republic"),
}

FL_ZONE_DEFAULTS = {
    "miami":      "Miami Beach",
    "broward":    "Fort Lauderdale / Broward",
    "keys":       "Florida Keys",
    "palmbeach":  "Palm Beach",
    "gulf":       "Gulf Coast",
    "centralfl":  "Central Florida",
    "everglades": "Everglades",
    "westfl":     "West Florida",
    "space":      "Space Coast",
    "nefl":       "Northeast Florida",
    "puntacana":  "Punta Cana, Dominican Republic",
}


def main() -> int:
    path = os.path.join(BASE, "operators.json")
    ops = json.load(open(path))

    stats = {
        "cat_fixed": 0,
        "zone_fixed": 0,
        "addr_filled": 0,
        "price_nulled": 0,
        "punta_cana_labeled": 0,
    }

    for op in ops:
        # cat normalization
        cat = op.get("cat", "")
        if cat in CAT_MAP:
            op["cat"] = CAT_MAP[cat]
            stats["cat_fixed"] += 1

        # zone normalization
        zone = op.get("zone", "")
        if zone in ZONE_MAP:
            canonical, default_zl = ZONE_MAP[zone]
            op["zone"] = canonical
            # preserve existing zl if it's already a real label; otherwise set
            if not op.get("zl") or op["zl"].lower() == zone:
                op["zl"] = default_zl
            stats["zone_fixed"] += 1

        # Punta Cana: add country field
        if op.get("zone") == "puntacana":
            op["country"] = "DO"
            if not op.get("zl") or "Dominican" not in op.get("zl", ""):
                op["zl"] = "Punta Cana, Dominican Republic"
            stats["punta_cana_labeled"] += 1

        # Ensure zl is set for canonical Florida zones
        if not op.get("zl"):
            op["zl"] = FL_ZONE_DEFAULTS.get(op.get("zone", ""), op.get("zone", ""))

        # Empty addr -> placeholder
        if not op.get("addr", "").strip():
            op["addr"] = f"{op['zl']}, FL" if op.get("zone") != "puntacana" else op["zl"]
            stats["addr_filled"] += 1

        # Zero price -> null (template should render "Contact for pricing")
        if op.get("price") in (0, None):
            op["price"] = None
            stats["price_nulled"] += 1

    # Write full operators.json (pretty-printed for diffability)
    with open(path, "w") as f:
        json.dump(ops, f, ensure_ascii=False, indent=2)
        f.write("\n")

    # Write slim version (drop 'desc')
    slim_path = os.path.join(BASE, "operators-slim.json")
    slim = [{k: v for k, v in o.items() if k != "desc"} for o in ops]
    with open(slim_path, "w") as f:
        json.dump(slim, f, ensure_ascii=False, indent=2)
        f.write("\n")

    print(f"Cleaned {len(ops)} records:")
    for k, v in stats.items():
        print(f"  {k}: {v}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
