#!/usr/bin/env node
/**
 * verify_shortname_candidates.js — verifica shortname candidates via Playwright.
 *
 * Para cada op en shortname_audit.json:
 *   1. Verifica cada candidate visitando fareharbor.com/embeds/book/{candidate}/
 *   2. Si carga sin errores y tiene items → marca como verified
 *   3. Compara items con el nombre del op para confirmar match
 *
 * Output: shortname_verified.json con la lista de matches confirmados
 *
 * Uso:
 *   NODE_OPTIONS='--max-old-space-size=4096' node verify_shortname_candidates.js
 *   node verify_shortname_candidates.js --limit 100 --concurrency 3
 */

const fs = require('fs');
const { chromium } = require('playwright');

const argv = process.argv.slice(2);
const LIMIT = parseInt(argv.includes('--limit') ? argv[argv.indexOf('--limit')+1] : '0', 10);
const CONCURRENCY = parseInt(argv.includes('--concurrency') ? argv[argv.indexOf('--concurrency')+1] : '3', 10);
const RESUME = !argv.includes('--no-resume');
const OUT_FILE = 'shortname_verified.json';

const audit = JSON.parse(fs.readFileSync('shortname_audit.json', 'utf8'));
console.log(`Total ops a verificar: ${audit.length}`);

let verified = {};
if (RESUME && fs.existsSync(OUT_FILE)) {
  verified = JSON.parse(fs.readFileSync(OUT_FILE, 'utf8'));
  console.log(`Resuming: ${Object.keys(verified).length} ya verificados`);
}

const todo = audit.filter(a => !verified[a.id]);
const work = LIMIT > 0 ? todo.slice(0, LIMIT) : todo;
console.log(`Pendientes en esta corrida: ${work.length}`);

async function verifyShortname(browser, shortname, opName) {
  const ctx = await browser.newContext({
    userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
  });
  const page = await ctx.newPage();
  const apiResponses = [];
  page.on('response', async (response) => {
    try {
      const url = response.url();
      const ct = (response.headers()['content-type'] || '').toLowerCase();
      if (ct.includes('application/json') && /fareharbor\.com/.test(url) && /\/(items|companies|company)/i.test(url)) {
        const body = await response.text();
        apiResponses.push(body.slice(0, 100000));
      }
    } catch(e){}
  });

  try {
    const url = `https://fareharbor.com/embeds/book/${shortname}/`;
    const resp = await page.goto(url, {waitUntil: 'domcontentloaded', timeout: 15000});
    const status = resp ? resp.status() : 0;

    if (status === 404 || status === 410) return {ok: false, reason: 'not_found'};
    if (status !== 200) return {ok: false, reason: `http_${status}`};

    await page.waitForTimeout(4000);

    // Extract company name from API
    let companyName = '';
    let itemCount = 0;
    for (const body of apiResponses) {
      try {
        const j = JSON.parse(body);
        const stack = [j];
        while (stack.length) {
          const node = stack.pop();
          if (!node || typeof node !== 'object') continue;
          if (node.shortname === shortname && node.name) {
            companyName = node.name;
          }
          if (node.pk && (node.name || node.headline) && node.is_bookable !== false) {
            itemCount++;
          }
          if (Array.isArray(node)) for (const v of node) stack.push(v);
          else for (const k in node) if (typeof node[k] === 'object') stack.push(node[k]);
        }
      } catch(e){}
    }

    // Get title as fallback
    if (!companyName) {
      const title = await page.title();
      companyName = title.replace(/^Book Online[\s\-—:]*/i, '').replace(/\s*[|—–].*$/, '').trim();
    }

    return {
      ok: itemCount > 0 || companyName.length > 3,
      companyName,
      itemCount,
      score: matchScore(companyName, opName)
    };
  } catch (e) {
    return {ok: false, reason: 'error', err: String(e).slice(0, 80)};
  } finally {
    await ctx.close();
  }
}

function matchScore(fhName, opName) {
  // Score 0-1 de similitud entre nombre FH y nombre op
  const norm = s => s.toLowerCase().replace(/[^a-z0-9 ]/g, '').replace(/\s+/g, ' ').trim();
  const fh = norm(fhName);
  const op = norm(opName);
  if (!fh || !op) return 0;

  const fhWords = new Set(fh.split(' '));
  const opWords = op.split(' ');
  let matches = 0;
  for (const w of opWords) if (fhWords.has(w)) matches++;
  return matches / Math.max(opWords.length, 1);
}

async function processOp(browser, opData) {
  const result = {
    id: opData.id,
    name: opData.name,
    currentShortname: opData.current,
    tried: [],
    bestMatch: null
  };

  for (const candidate of opData.candidates) {
    const r = await verifyShortname(browser, candidate, opData.name);
    result.tried.push({candidate, ...r});
    if (r.ok && r.score >= 0.4) {
      if (!result.bestMatch || r.score > result.bestMatch.score) {
        result.bestMatch = {shortname: candidate, ...r};
      }
    }
  }

  return result;
}

(async () => {
  const browser = await chromium.launch({headless: true});
  let done = 0;
  const t0 = Date.now();

  const queue = [...work];
  async function worker() {
    while (queue.length) {
      const op = queue.shift();
      try {
        const result = await processOp(browser, op);
        verified[op.id] = result;
        done++;
        const status = result.bestMatch
          ? `✓ ${result.bestMatch.shortname} (score ${result.bestMatch.score.toFixed(2)})`
          : `✗ ningún match`;
        const elapsed = ((Date.now() - t0) / 1000).toFixed(0);
        if (done % 10 === 0) {
          fs.writeFileSync(OUT_FILE, JSON.stringify(verified, null, 2));
        }
        console.log(`  [${done}/${work.length}] ${elapsed}s · ${op.id} ${op.name.slice(0,40)} → ${status}`);
      } catch (e) {
        console.error(`  ERROR ${op.id}: ${e.message}`);
      }
    }
  }

  await Promise.all(Array(CONCURRENCY).fill(0).map(worker));
  await browser.close();

  fs.writeFileSync(OUT_FILE, JSON.stringify(verified, null, 2));
  const matches = Object.values(verified).filter(v => v.bestMatch).length;
  console.log(`\n═ DONE ═`);
  console.log(`  Verificados:    ${Object.keys(verified).length}`);
  console.log(`  Con match:      ${matches}`);
  console.log(`  Sin match:      ${Object.keys(verified).length - matches}`);
  console.log(`\nOutput: ${OUT_FILE}`);
})();
