#!/usr/bin/env python3
"""Refactor index.html to fix the issues identified in the audit.

Idempotent: safe to run multiple times.

Changes:
1. Replace stale operator counts (417, 411, 377, 881) -> current count from operators.json.
2. Regenerate the inline JSON-LD ItemList from operators.json (keeps SEO,
   but data is fresh).
3. Add `esc()` / `escAttr()` helpers at the top of the main inline <script>.
4. Wrap risky template-literal interpolations of operator data with esc().
5. Add rel="noreferrer" to every external target="_blank" link.
6. Remove obsolete <meta name="keywords"> tag.
"""
import json
import os
import re

BASE = os.path.dirname(os.path.abspath(__file__))


def _esc_html_attr_value(s: str) -> str:
    """Conservative HTML attribute escape for static (build-time) strings."""
    return (
        s.replace("&", "&amp;")
        .replace('"', "&quot;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def build_item_list_jsonld(ops: list) -> str:
    """Build a schema.org ItemList JSON-LD payload from operators.json."""
    site = "https://miamijetskiboatrentals.com"
    cat_labels = {
        "jetski": "Jet Ski Rental",
        "boat": "Boat Rental",
        "slingshot": "Slingshot Rental",
        "watersports": "Water Sports",
        "tour": "Tour",
        "fishing": "Fishing Charter",
        "jetcar": "Jet Car Rental",
        "atv": "ATV Rental",
        "golfcart": "Golf Cart Rental",
        "aerial": "Aerial Tour",
        "bikerental": "Bike Rental",
    }
    zone_labels = {
        "miami": "Miami Beach",
        "broward": "Fort Lauderdale / Broward",
        "keys": "Florida Keys",
        "palmbeach": "Palm Beach",
        "gulf": "Gulf Coast",
        "centralfl": "Central Florida",
        "everglades": "Everglades",
        "westfl": "West Florida",
        "space": "Space Coast",
        "nefl": "Northeast Florida",
        "puntacana": "Punta Cana, Dominican Republic",
    }

    # Load id -> slug map from slug-map.js so SEO URLs match what the site serves.
    slug_text = open(os.path.join(BASE, "slug-map.js")).read()
    slugs = dict(re.findall(r'"([^"]+)":"([^"]+)"', slug_text))

    # Pick top operators by popularity (rating * log10(reviews+1)) so SEO value
    # is concentrated where users actually click. The full catalogue is exposed
    # via sitemap.xml + per-operator pages.
    import math

    def score(o: dict) -> float:
        r = float(o.get("rating") or 0)
        rv = float(o.get("reviews") or 0)
        return r * math.log10(rv + 1)

    top = sorted(ops, key=score, reverse=True)[:60]

    items = []
    for i, op in enumerate(top, start=1):
        cat = cat_labels.get(op.get("cat"), op.get("cat", ""))
        zone = zone_labels.get(op.get("zone"), op.get("zl", ""))
        op_slug = slugs.get(op["id"], "")
        url = f"{site}/{op_slug}" if op_slug else site
        # Lean schema: name + url only. Per-operator pages carry the full
        # LocalBusiness markup with address, geo, image, price.
        items.append({
            "@type": "ListItem",
            "position": i,
            "item": {
                "@type": "LocalBusiness",
                "name": op.get("name", ""),
                "description": f"{cat} in {zone}",
                "url": url,
            },
        })

    payload = {
        "@context": "https://schema.org",
        "@type": "ItemList",
        "name": f"Florida Water Sports & Activities — {len(ops)} Operators",
        "description": (
            f"Compare {len(ops)} jet ski, boat, fishing, slingshot, jet car, golf cart, "
            "ATV, aerial and tour operators across Florida. Miami Beach, Fort Lauderdale, "
            "Florida Keys, Gulf Coast & more."
        ),
        "url": f"{site}/",
        "numberOfItems": len(ops),
        "itemListElement": items,
    }
    return json.dumps(payload, ensure_ascii=False, separators=(",", ":"))


# --- inline helper block to add at the top of the main app <script> ----
ESCAPE_HELPERS_JS = """\
// --- Escaping helpers (CWE-79: defense-in-depth for template literals) ---
const _ESC_MAP={'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;','`':'&#96;'};
function esc(s){return String(s==null?'':s).replace(/[&<>"'`]/g,c=>_ESC_MAP[c]);}
function escAttr(s){return esc(s);}
function escUrl(s){if(s==null)return '';var u=String(s);return /^\\s*(javascript|data|vbscript):/i.test(u)?'#':esc(u);}
function escCss(s){return String(s==null?'':s).replace(/['"\\\\\\s]/g,encodeURIComponent);}
"""


def patch_index(html: str, ops: list) -> str:
    n = len(ops)
    changes = []

    # 1. Replace stale operator counts.
    replacements = [
        (r"Compare 417 Operators", f"Compare {n} Operators"),
        (r"Compare 417 operators", f"Compare {n} operators"),
        (r"\"417 Operators", f"\"{n} Operators"),
        (r">417 Operators", f">{n} Operators"),
        (r"Browse 881 operators", f"Browse {n} operators"),
        (r"— 881 Operators", f"— {n} Operators"),
        (r">881</span>", f">{n}</span>"),
        (r"id=\"mobCtaCount\">881<", f"id=\"mobCtaCount\">{n}<"),
        (r"Compare 411 Operators", f"Compare {n} Operators"),
        (r"Compare 377", f"Compare {n}"),
    ]
    for pat, repl in replacements:
        new_html, c = re.subn(pat, repl, html)
        if c:
            changes.append(f"replaced {c}× '{pat[:50]}…'")
            html = new_html

    # Generic remaining "417 operators" / "417 Operators" fallback.
    new_html, c = re.subn(r"\b417\s+(operators?)\b", lambda m: f"{n} {m.group(1)}", html)
    if c:
        changes.append(f"replaced {c}× generic '417 operator(s)'")
        html = new_html
    new_html, c = re.subn(r"\b881\s+(operators?)\b", lambda m: f"{n} {m.group(1)}", html)
    if c:
        changes.append(f"replaced {c}× generic '881 operator(s)'")
        html = new_html

    # 2. Regenerate JSON-LD ItemList.
    new_payload = build_item_list_jsonld(ops)
    # Match the existing block: <script type="application/ld+json">{"@context":...,"@type":"ItemList",...}</script>
    item_list_pat = re.compile(
        r'<script type="application/ld\+json">\s*\{"@context":"https://schema\.org","@type":"ItemList".*?\}\s*</script>',
        re.DOTALL,
    )
    new_block = (
        '<script type="application/ld+json">' + new_payload + "</script>"
    )
    new_html, c = item_list_pat.subn(new_block, html, count=1)
    if c:
        changes.append(f"regenerated ItemList JSON-LD ({len(new_block):,} chars)")
        html = new_html

    # 3. Inject escape helpers at the top of the main <script>.
    marker = "// ---- DATA ----\nlet allOperators = [];"
    if marker in html and "function esc(" not in html:
        html = html.replace(marker, ESCAPE_HELPERS_JS + "\n" + marker, 1)
        changes.append("injected esc/escAttr/escUrl/escCss helpers")

    # 4. Wrap risky template-literal interpolations with esc(). Conservative —
    # only the body-text and attribute uses, not function calls or numbers.
    # We do this once per pattern to avoid double-wrapping (esc(esc(...))).
    def wrap_once(pattern: str, replacement: str, label: str) -> None:
        nonlocal html, changes
        # Skip patterns already wrapped: look for replacement substring.
        # Use re.subn but only replace strings not preceded by 'esc('.
        new_html, c = re.subn(
            r"(?<!esc\()" + pattern, replacement, html
        )
        if c:
            changes.append(f"wrapped {c}× {label}")
            html = new_html

    # Names and addresses (HTML text content)
    wrap_once(r"\$\{op\.name\}", "${esc(op.name)}", "${op.name}")
    wrap_once(r"\$\{op\.zl\}", "${esc(op.zl)}", "${op.zl}")
    wrap_once(r"\$\{op\.addr\}", "${esc(op.addr)}", "${op.addr}")
    wrap_once(r"\$\{op\.badge\}", "${esc(op.badge)}", "${op.badge}")
    wrap_once(r"\$\{o\.name\}", "${esc(o.name)}", "${o.name}")
    # URLs in href: escape javascript: schemes
    wrap_once(r"\$\{op\.link\}", "${escUrl(op.link)}", "${op.link}")

    # 5. Add rel="noreferrer" wherever target="_blank" rel="noopener" exists
    # (only when noreferrer is not already there).
    pat = re.compile(r'(target="_blank"\s+rel="noopener)(?!\s+noreferrer)"', re.IGNORECASE)
    new_html, c = pat.subn(r'\1 noreferrer"', html)
    if c:
        changes.append(f"added 'noreferrer' to {c}× target=_blank")
        html = new_html

    # 6. Remove obsolete <meta name="keywords">.
    new_html, c = re.subn(
        r'\s*<meta\s+name="keywords"[^>]*>\s*\n?', "\n  ", html, count=1
    )
    if c:
        changes.append("removed obsolete <meta keywords>")
        html = new_html

    return html, changes


def main() -> int:
    ops = json.load(open(os.path.join(BASE, "operators.json")))
    html = open(os.path.join(BASE, "index.html")).read()
    new_html, changes = patch_index(html, ops)
    open(os.path.join(BASE, "index.html"), "w").write(new_html)
    print(f"Operators in dataset: {len(ops)}")
    print(f"index.html: {len(html):,} -> {len(new_html):,} chars "
          f"(Δ {len(new_html)-len(html):+,})")
    print("Changes applied:")
    for c in changes:
        print(f"  - {c}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
