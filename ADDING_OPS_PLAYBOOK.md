# Adding Operators from FareHarbor — Playbook

Lessons learned mirroring FH inventory for **Punta Cana, Cancún, Key West, Miami** (~1,500 ops added across 4 zones in one session).

---

## TL;DR — the workflow

1. **Get the CSV.** Navigate to `partner.fareharbor.com/items?locSearch=<Zone>&view=list`, click Download → **"Email top 500 matches"**. FH caps exports at 500 by quality score.
2. **Filter the CSV in code:**
   - Drop rows where `availability_count == 0 AND availability_next_180days == 0` (zero-avail / not bookable).
   - Drop rows whose `location` is outside the target metro (FH searches return surrounding cities — e.g. Miami search returns NYC, Boston, Australia).
3. **Build a 4-phase plan in code:**
   - Phase 1: list of op-IDs to delete + list of new FH items to add (save as JSON for inspection).
   - Phase 2: delete old ops + add 301 redirects + sitemap cleanup + internal-link cleanup.
   - Phase 3a: append new ops to `operators.json` + `operators-slim.json` + `slug-map.js`.
   - Phase 3b: generate static HTML pages by cloning a template.
   - Phase 4: update zone-landing `ops-index <ul>` + audit.

---

## Gotchas, in priority order

### 1. CSV `image_url` is empty for 6–13% of items
Apply a **category-fallback** photo handle pulled from another working op in the same zone+cat:
```python
cat_handles_by_cat = {}
for o in ops:
    if o.get('zone') != target_zone: continue
    cat = o.get('cat')
    m = HANDLE_RE.search(o.get('photo',''))
    if m and m.group(1) != TMPL_HANDLE:
        cat_handles_by_cat.setdefault(cat, m.group(1))

# For each new op with empty handle:
fb = cat_handles_by_cat.get(op['cat']) or cat_handles_by_cat.get('tour')
```

If you skip this step, those pages will inherit the **template's photo handle** and look identical to the template (the at59 Punta Cana ATV image bled into 33 KW + 61 Miami + 25 Cancún pages on first pass).

### 2. Photo-handle extraction bug
`photo_url.split('/')[-1].split('?')[0]` returns `"convert"`, not the handle.

Use the regex instead:
```python
HANDLE_RE = re.compile(r'(?:filestackcontent\.com|filepicker\.io/api/file)/(?:[^/]+/)*?([A-Za-z0-9]{15,30})')
handle = HANDLE_RE.search(photo_url).group(1)
```

Or pull from the CSV `image_url` field directly (CSV gives bare handle, no suffix).

### 3. Operator names starting with digits break `re.sub` replacement strings
Items like "1 Hour Jet Ski Rental" or "30 Min ATV Tour" produce **`re.error: invalid group reference 11`** when inserted into replacement strings containing `\1` backrefs (Python parses `\1` + "1 Hour..." as `\11`).

**Solution: use callable replacements throughout Phase 3b template generation:**
```python
# BAD
txt = re.sub(pattern, rf'\1{r["name"]}\2', txt)

# GOOD
escaped_name = h(r['name'])
txt = re.sub(pattern, lambda mm: mm.group(1) + escaped_name + mm.group(2), txt)
```

### 4. The "doubled `/convert?…` suffix" bug
A buggy URL-normalization regex matched only the prefix of URLs that already had the suffix, producing:
```
.../HANDLE/convert?...&fit=max/convert?...&fit=max
```
which 404s.

**Detection:** any URL containing `&fit=max/convert?`.
**Fix:** `re.sub(r'(&fit=max)/convert\?[^"\'\s<>]+', r'\1', txt)`

### 5. Slug collisions when adding ops
Some FH item names produce slugs that match deleted-op slugs (e.g., `original-key-west-pub-crawl-key-west`). Always check + suffix with op-id on collision:
```python
cand = f'{slugify(name)}-cancun'
if cand in all_slugs: cand = f'{cand}-{new_id}'
all_slugs.add(cand)
```

### 6. Zone landing-page slug naming is inconsistent
Don't assume the zone slug. The site uses:
- `/keys-activities` (not `/key-west-activities`)
- `/miami-activities`, `/cancun-activities`, `/punta-cana-activities` (standard)
- `/jacksonville-activities` (not `/nefl-activities`)
- `/gulf-coast-activities` (not `/gulf-activities`)

When adding 301 redirects, always verify the destination page actually exists. Pointing to a non-existent zone-landing slug creates a click→redirect→404→listing loop that looks like "nothing happens".

### 7. CSV location filter is necessary
FH location search returns far-flung items. For Miami CSV: 38 of 500 were NYC, Washington, Boston, SF, etc. Always whitelist the target metro before adding to a single zone.

```python
MIAMI_AREA = {'Miami','Miami Beach','North Miami Beach','Miami Shores','North Miami',
              'Coconut Grove','Bal Harbour','Key Biscayne','Aventura','Sunny Isles Beach',
              'Surfside','Doral','Hialeah','Coral Gables','South Beach','Quail Heights',
              'Miami-Dade County','Miami Lakes','Pinecrest','Cutler Bay','Homestead'}
```

### 8. CSV availability ≠ live FH page availability
`availability_count > 0` from the CSV doesn't always match what the FH booking page shows. Some items have "calendar but bookings closed" gaps. **Honor user reports** if they say a specific op shows "no online availability" — delete the op + add a redirect.

---

## Template substitution checklist

When cloning `atv-buggy-excursion-punta-cana-canelo-tours.html` (the canonical template), you MUST replace ALL of these per-op-zone-cat strings. Missing any of these creates leftover-template artifacts visible to users:

### URL / SEO
- [ ] Slug (canonical, og:url, internal refs) — single string-replace works
- [ ] FareHarbor booking URL — every occurrence (Book Now btn, sticky-book, lightframe script, JSON-LD `offers.url`)
- [ ] Photo Filestack **handle** — every occurrence (hero img, og:image, twitter:image, JSON-LD `image`)

### Visible hero
- [ ] `<title>`
- [ ] `<h1>` (operator name)
- [ ] `<span class="hero-addr">📍 City, Country</span>` — **easy to miss, this caused the "wrong city" bug**
- [ ] `<span class="hero-rating">` + reviews count
- [ ] `<div class="hero-badge">CATEGORY LABEL</div>`

### Fact bar
- [ ] `From $X`
- [ ] `X.X★ Rating`
- [ ] `N Reviews`
- [ ] `🇨🇨` country flag + zone label (e.g., `🇩🇴 Punta Cana` → `🇺🇸 Miami`)

### Content sections
- [ ] About section `<h2>About <Name></h2><p>...</p>` (category-specific copy)
- [ ] `<div class="tags-row">` chips (emoji + label per category)
- [ ] `<ul class="highlights-list">` (5 bullets, category-specific)
- [ ] `<div class="included-list">` tags (3–6 items, category-specific)
- [ ] `<h2>FAQ – Op Name</h2>`

### Meta tags
- [ ] `<title>`
- [ ] `<meta name="description">`
- [ ] `<meta property="og:title">`
- [ ] `<meta property="og:description">`
- [ ] `<meta property="og:image">`
- [ ] `<meta name="twitter:title">`
- [ ] `<meta name="twitter:description">`
- [ ] `<meta name="twitter:image">`

### JSON-LD structured data
- [ ] `"name"` (operator name)
- [ ] `"description"`
- [ ] `"image"`
- [ ] `"address.addressLocality"` (city)
- [ ] `"address.addressCountry"` (ISO code: `DO`, `MX`, `US`)
- [ ] `"geo.latitude"` + `"geo.longitude"`
- [ ] `"priceRange"`
- [ ] `"offers.url"` (FH booking URL)
- [ ] `"aggregateRating.ratingValue"` + `"reviewCount"`
- [ ] `BreadcrumbList` position-2 name + url (e.g., "Cancún Activities" + `/cancun-activities`)
- [ ] FAQPage entries (operator-specific Q&As — or generic fallback)

### Internal links
- [ ] Visible breadcrumb (`<div class="breadcrumb">`) text + href
- [ ] "Related operators" footer section
- [ ] Any "Sister experiences" links

---

## Mass-delete cleanup checklist

When replacing all of a zone's operators:

- [ ] Remove from `operators.json`
- [ ] Remove from `operators-slim.json`
- [ ] Remove from `slug-map.js`
- [ ] Delete the static HTML files
- [ ] Remove from `sitemap.xml`
- [ ] Add 301 redirects in `vercel.json` (every deleted slug → `/zone-activities`)
- [ ] Strip dead links from "Related operators" sections sitewide
- [ ] Strip dead `<li>` entries from zone-landing `ops-index <ul>` lists
- [ ] Strip dead links from any `/zone-activities` page's existing op list

---

## Card-grid pages need this scaffold

Zone landing pages render cards **client-side** from `operators-slim.json`. Required scaffolding (copy from `cancun-activities.html`):

```html
<head>
  ...
  <script src="/slug-map.js" defer></script>
</head>
<body>
  <header class="hero">...</header>
  
  <section class="filters">
    <button class="cat-chip active" data-cat="all">All</button>
    <button class="cat-chip" data-cat="boat">Boat</button>
    <!-- ... -->
  </section>
  
  <section class="grid" id="grid"><!-- populated by JS --></section>
  
  <script>
    const ZONE_KEY = "cancun";  // or filter on multiple: keywest+keys+marathon
    // ... render(), thumbUrl(), fetch operators-slim.json
  </script>
  
  <!-- FH_BOOKING_MODAL_v2 -->
  ...
  
  <!-- ORPHAN_FIX_OP_INDEX -->
  <section class="ops-index">
    <h2>All N operators</h2>
    <ul><li>...</li></ul>
  </section>
</body>
```

The `ops-index <ul>` is for SEO crawl + JS-disabled fallback. Both the grid AND the ul must be kept in sync with operators.json after every mirror.

---

## Audits to run after every mirror

```bash
python3 verify_card_images.py          # Card thumbnail vs op.photo mismatch
```

Plus these custom audits (Python one-liners):

```python
# 1. JSON ↔ slug-map ↔ HTML sync
assert len(ops_json) == len(ops_slim) == len(slug_map)
assert all(f"{slug}.html" exists for slug in slug_map.values())

# 2. Card↔hero photo handle alignment per op
for op in mirrored_ops:
    card_handle = HANDLE_RE.search(op['photo']).group(1)
    hero_handle = HANDLE_RE.search(read_hero_img(slug)).group(1)
    assert card_handle == hero_handle

# 3. Hero location text matches operator
for op in mirrored_ops:
    expected = f"📍 {op['zl']}, {country_for(op['zone'])}"
    actual = re.search(r'<span class="hero-addr">([^<]+)</span>', html)
    assert actual.group(1) == expected
```

---

## Deployment notes

- **Vercel deploys atomically in principle**, but in practice we observed partial-deploy states (vercel.json with new redirects deployed while operators-slim.json was stale).
- **Browser/CDN cache**: after deploy, hard-reload listings. Card images especially can be cached aggressively.
- **301 redirects** preserve SEO equity from deleted slugs. Always add them; never leave deleted slugs as 404s.
- After deploy: clicks on listing-card thumbnails should navigate to `/new-slug` static page (not a redirect). If you see a redirect chain, the operators-slim.json + HTML weren't pushed.

---

## Categories observed in FH CSVs

Use this mapping when categorizing FH `tags` field → our internal `cat`:

```python
def fh_cat(tags, name):
    t = (tags + ' ' + name).lower()
    if any(k in t for k in ('atv','utv','buggy','off-road')): return 'atv'
    if any(k in t for k in ('jet car','jetcar')): return 'jetcar'
    if any(k in t for k in ('jet ski','jetski','waverunner')): return 'jetski'
    if any(k in t for k in ('flyboard','parasail','snorkel','scuba','dive','kayak',
                            'paddleboard','windsurf','wakeboard','tubing')): return 'watersports'
    if 'fishing' in t: return 'fishing'
    if any(k in t for k in ('helicopter','balloon','aerial','skydiv','flight')): return 'aerial'
    if 'slingshot' in t: return 'slingshot'
    if any(k in t for k in ('catamaran','sailing','speedboat','yacht','charter','cruise',
                            'party boat','boat rental','boat tour','sail')): return 'boat'
    if any(k in t for k in ('golf cart','moke')): return 'golfcart'
    if any(k in t for k in ('bike','bicycle','e-bike','trikke','scooter','moped')): return 'bikerental'
    return 'tour'  # safe default
```

ID prefixes by category: `at`, `bt`, `to`, `fi`, `js`, `ws`, `ae`, `gc`, `br`, `sl`, `jc`.

---

## Zone → country / flag / coords / addr format

```python
ZONE_FLAG    = {'puntacana':'🇩🇴','cancun':'🇲🇽','keywest':'🇺🇸','keys':'🇺🇸',
                'marathon':'🇺🇸','miami':'🇺🇸','broward':'🇺🇸','palmbeach':'🇺🇸'}
ZONE_COUNTRY = {'puntacana':'Dominican Republic','cancun':'Mexico',
                'keywest':'FL, USA','keys':'FL, USA','marathon':'FL, USA',
                'miami':'FL, USA','broward':'FL, USA','palmbeach':'FL, USA'}
ZONE_ISO     = {'puntacana':'DO','cancun':'MX','keywest':'US','keys':'US',
                'marathon':'US','miami':'US','broward':'US','palmbeach':'US'}
```

---

## Final tally (this session)

| Zone | Before | After | Net | Partner Concentration |
|---|---|---|---|---|
| Punta Cana | 117 (runnersadventures 113, 96%) | 90 | −27 | 7 partners (top runnersadventures 48) |
| Cancún | 103 (offroadcancun 103, 100%) | 479 | +376 | 32 partners (top upgradevacations 76) |
| Key West | 253 (sixfinscharter 20, top) | 473 | +220 | 126 partners (top sunsetwatersports 26) |
| Miami | 466 (305toursandrentals 30, top) | 453 | −13 | 95 partners (top 100miami 29) |
| **Total mirrored ops** | | **1,495** | | |
