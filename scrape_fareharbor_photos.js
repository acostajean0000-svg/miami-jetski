#!/usr/bin/env node
/**
 * scrape_fareharbor_photos.js — Headless-browser scraper for FareHarbor item photos.
 *
 * For each operator in operators.json with a FareHarbor booking link,
 * opens the booking page in Chromium, waits for the FH widget to fully render,
 * then extracts filestack photo handles from the rendered DOM.
 *
 * USAGE (run on YOUR machine, not in the sandbox):
 *   cd /Users/raptor/miami-jetski-main
 *   npm init -y
 *   npm install playwright
 *   npx playwright install chromium
 *   node scrape_fareharbor_photos.js
 *
 * Outputs fh_scrape_photos.json (resume-safe — re-running picks up where it left off).
 *
 * Flags:
 *   --concurrency 3   # parallel pages (default 3, keep low to avoid bot detection)
 *   --limit 50        # cap how many ops to process (default = all)
 *   --headless false  # show browser window
 *   --resume false    # ignore existing output and restart
 *
 * Expected runtime: ~5–8 seconds per operator. 2,000 ops × 6s / 3 parallel = ~1 hour.
 */

const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');

const args = Object.fromEntries(
  process.argv.slice(2).reduce((acc, v, i, arr) => {
    if (v.startsWith('--')) acc.push([v.slice(2), arr[i + 1] && !arr[i + 1].startsWith('--') ? arr[i + 1] : true]);
    return acc;
  }, [])
);
const CONCURRENCY = parseInt(args.concurrency || 3);
const LIMIT = parseInt(args.limit || 0);
const HEADLESS = args.headless !== 'false';
const RESUME = args.resume !== 'false';
const TARGETS_FILE = args.targets || null;  // si se da, solo scrape esos op IDs
const PER_PAGE_TIMEOUT_MS = 25000;
const MIN_DWELL_MS = 4000; // give widget time to load photos

const HANDLE_RE = /(?:filestackcontent\.com|filepicker\.io\/api\/file)\/(?:[^\/"']+\/)*?([A-Za-z0-9]{15,30})/g;

async function main() {
  const operators = JSON.parse(fs.readFileSync('operators.json', 'utf-8'));
  const outPath = 'fh_scrape_photos.json';
  let out = {};
  if (RESUME && fs.existsSync(outPath)) {
    out = JSON.parse(fs.readFileSync(outPath, 'utf-8'));
    console.log(`Resuming from ${Object.keys(out).length} already-scraped operators`);
  }

  // Si TARGETS_FILE existe, restringir a esos IDs
  let targetIds = null;
  if (TARGETS_FILE && fs.existsSync(TARGETS_FILE)) {
    const targets = JSON.parse(fs.readFileSync(TARGETS_FILE, 'utf-8'));
    targetIds = new Set(targets.map(t => t.id));
    console.log(`Targets file: ${TARGETS_FILE} → scraping solo ${targetIds.size} ops`);
  }
  const todo = operators.filter(o => {
    if (out[o.id]) return false;
    if (targetIds && !targetIds.has(o.id)) return false;
    const link = o.link || '';
    return /fareharbor\.com\/embeds\/book\//.test(link);
  });
  const total = LIMIT ? Math.min(LIMIT, todo.length) : todo.length;
  console.log(`Scraping ${total} operators (concurrency=${CONCURRENCY}, headless=${HEADLESS})`);

  const browser = await chromium.launch({ headless: HEADLESS });
  const context = await browser.newContext({
    viewport: { width: 1280, height: 900 },
    userAgent:
      'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
  });

  let done = 0;
  const t0 = Date.now();

  async function processOne(op) {
    const page = await context.newPage();
    const url = op.link;
    let handles = new Set();
    try {
      await page.goto(url, { waitUntil: 'domcontentloaded', timeout: PER_PAGE_TIMEOUT_MS });
      // Dwell so the FH widget can populate photos
      await page.waitForTimeout(MIN_DWELL_MS);
      // Pull from rendered DOM
      const html = await page.content();
      let m;
      while ((m = HANDLE_RE.exec(html))) handles.add(m[1]);
      // Also: walk all <img> src/srcset attributes explicitly
      const imgUrls = await page.$$eval('img', els =>
        els.flatMap(el => [el.src, el.dataset.src, el.dataset.lazy, el.srcset].filter(Boolean))
      );
      for (const u of imgUrls) {
        const matches = String(u).matchAll(HANDLE_RE);
        for (const mm of matches) handles.add(mm[1]);
      }
    } catch (err) {
      out[op.id] = { error: err.message.slice(0, 200), handles: [] };
      done++;
      await page.close();
      return;
    }
    out[op.id] = { handles: [...handles], duration_ms: Date.now() - t0 };
    done++;
    await page.close();
  }

  // Process in batches of CONCURRENCY
  const work = todo.slice(0, total);
  for (let i = 0; i < work.length; i += CONCURRENCY) {
    const batch = work.slice(i, i + CONCURRENCY);
    await Promise.all(batch.map(processOne));
    // Save progress every batch
    fs.writeFileSync(outPath, JSON.stringify(out, null, 2));
    const elapsed = (Date.now() - t0) / 1000;
    const rate = done / elapsed;
    const eta = (total - done) / rate;
    const withPhotos = Object.values(out).filter(r => r.handles && r.handles.length).length;
    console.log(
      `  ${done}/${total} · ${elapsed.toFixed(0)}s · ${rate.toFixed(2)}/s · ETA ${(eta / 60).toFixed(1)}min · with_photos=${withPhotos}`
    );
  }

  await browser.close();
  console.log(`\n✅ DONE. Output: ${outPath}`);
}

main().catch(e => {
  console.error(e);
  process.exit(1);
});
