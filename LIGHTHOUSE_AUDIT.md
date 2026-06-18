# Lighthouse Audit Guide

Manual + automated Lighthouse auditing for miamijetskiboatrentals.com

## Quick start

```bash
# Install (one time)
npm install -g lighthouse

# Audit production
lighthouse https://miamijetskiboatrentals.com \
  --output html \
  --output-path ./reports/lighthouse-home.html \
  --chrome-flags="--headless"
```

## URLs to audit

These cover the three main page templates:

| Template | URL | Why |
|---|---|---|
| Homepage | `/` | High traffic, multiple categories |
| Zone page | `/miami-activities` | Filter UI, map, conversion pack |
| Operator page | `/100-miami-luxury-boat-rental-miami` | Booking iframe |

## Targets (LCP/CLS/INP)

- **LCP** (Largest Contentful Paint): under 2.5s on 4G/mobile
- **CLS** (Cumulative Layout Shift): under 0.1
- **INP** (Interaction to Next Paint): under 200ms
- **Performance score**: 85+ mobile, 95+ desktop

## Batch script

Save as `scripts/lhci-batch.sh`:

```bash
#!/usr/bin/env bash
mkdir -p reports
URLS=(
  "https://miamijetskiboatrentals.com"
  "https://miamijetskiboatrentals.com/miami-activities"
  "https://miamijetskiboatrentals.com/keys-activities"
  "https://miamijetskiboatrentals.com/punta-cana-activities"
  "https://miamijetskiboatrentals.com/100-miami-luxury-boat-rental-miami"
)
for url in "${URLS[@]}"; do
  slug=$(echo "$url" | sed 's|https://miamijetskiboatrentals.com||' | sed 's|^/||' | sed 's|/|_|g')
  [ -z "$slug" ] && slug="home"
  echo "→ $url"
  lighthouse "$url" \
    --output json --output html \
    --output-path "./reports/lh-${slug}" \
    --chrome-flags="--headless --no-sandbox" \
    --quiet
done
echo "Reports in ./reports/"
```

Run: `chmod +x scripts/lhci-batch.sh && ./scripts/lhci-batch.sh`

## Known optimizations applied

- ✅ Service Worker v1.0.6 with stale-while-revalidate for /data/*.json
- ✅ `operators-slim.json` compressed (5.4 MB → 2.9 MB, 46% reduction)
- ✅ `link/photo` URL shorthand format with client-side expansion
- ✅ CSS critical/deferred split — styles.css cached aggressively
- ✅ Filestack images: `format=webp`, `quality=75-90`, responsive `width=480`
- ✅ Preconnect to cdn.filestackcontent.com and fareharbor.com
- ✅ First 4 cards `fetchpriority="high"` + `loading="eager"`, rest lazy
- ✅ Skeleton loaders with shimmer reduce CLS while data loads
- ✅ JSON-LD schema injected (LocalBusiness, TouristAttraction, AggregateRating, FAQPage)

## If scores drop

**LCP > 2.5s**
- Check Filestack delivery (CDN region)
- Verify image `srcset` has 480w version
- Run `lighthouse --view --only-categories=performance` and inspect "Opportunities"

**CLS > 0.1**
- Look for images without `width`/`height` attributes
- Ad/widget injections shifting layout (urgency strip, lead modal)
- Web fonts loading — verify `font-display: swap` if custom fonts

**INP > 200ms**
- Heavy filter/sort operations on `allOps` — already debounced 180ms
- Map redraw on category change — check Leaflet pin count

## Continuous monitoring

For automated CI runs, use Lighthouse CI (`@lhci/cli`):

```bash
npm install -g @lhci/cli
lhci autorun --collect.url=https://miamijetskiboatrentals.com/miami-activities
```

Set up budgets in `.lighthouserc.js`:

```js
module.exports = {
  ci: {
    assert: {
      assertions: {
        'categories:performance': ['error', {minScore: 0.85}],
        'categories:seo': ['error', {minScore: 0.95}],
        'categories:accessibility': ['warn', {minScore: 0.90}],
      }
    }
  }
};
```

## Quick wins if score is below target

1. **Compress JSON further** with brotli on Vercel (already enabled by default)
2. **Reduce JS bundle** — slug-map.js is 533 KB; consider chunking by zone
3. **Defer non-critical scripts** — Google Ads, lead modal can wait for `requestIdleCallback`
4. **Preload top-zone JSON** on homepage — `<link rel="preload" as="fetch" href="/data/miami.json">`

---

Updated: 2026-06 (Sprint 7 Tech Debt)
