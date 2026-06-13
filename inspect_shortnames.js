#!/usr/bin/env node
/**
 * inspect_shortnames.js — para los top N shortnames contaminados,
 * obtiene la lista REAL de items de FareHarbor.
 *
 * Output: shortname_items.json
 *   { fabulousbuses: { companyName, items: [{name, pk}] }, ... }
 *
 * Uso:
 *   node inspect_shortnames.js
 */
const fs = require('fs');
const { chromium } = require('playwright');

// Top 5 contaminados (puedes agregar más)
const TARGETS = [
  'fabulousbuses',
  'partytickets',
  'mydeeplife',
  'alemantravelagency',
  'kokomocharters',
];

async function inspect(browser, shortname) {
  const ctx = await browser.newContext({
    userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
  });
  const page = await ctx.newPage();
  const items = [];
  let companyName = '';

  page.on('response', async (response) => {
    try {
      const url = response.url();
      const ct = (response.headers()['content-type'] || '').toLowerCase();
      if (!ct.includes('application/json')) return;
      if (!/fareharbor\.com/.test(url)) return;
      const body = await response.text();
      const j = JSON.parse(body);
      const stack = [j];
      while (stack.length) {
        const node = stack.pop();
        if (!node || typeof node !== 'object') continue;
        if (node.shortname === shortname && node.name && !companyName) {
          companyName = node.name;
        }
        if (node.pk && node.name && node.is_bookable !== false && typeof node.name === 'string' && node.name.length > 3) {
          if (!items.find(it => it.pk === node.pk)) {
            items.push({pk: node.pk, name: node.name, headline: node.headline || ''});
          }
        }
        if (Array.isArray(node)) for (const v of node) stack.push(v);
        else for (const k in node) if (typeof node[k] === 'object') stack.push(node[k]);
      }
    } catch(e){}
  });

  try {
    await page.goto(`https://fareharbor.com/embeds/book/${shortname}/`, {waitUntil: 'domcontentloaded', timeout: 20000});
    await page.waitForTimeout(6000);
    if (!companyName) {
      const title = await page.title();
      companyName = title.replace(/^Book Online[\s\-—:]*/i, '').replace(/\s*[|—–].*$/, '').trim();
    }
  } catch(e) {
    console.error(`  ERROR ${shortname}: ${e.message}`);
  } finally {
    await ctx.close();
  }
  return {companyName, items};
}

(async () => {
  const browser = await chromium.launch({headless: true});
  const out = {};
  for (const sn of TARGETS) {
    console.log(`▸ ${sn}...`);
    out[sn] = await inspect(browser, sn);
    console.log(`  ${out[sn].companyName} — ${out[sn].items.length} items reales`);
    for (const it of out[sn].items.slice(0, 5)) {
      console.log(`    · ${it.name.slice(0, 70)}`);
    }
    if (out[sn].items.length > 5) console.log(`    · (+${out[sn].items.length - 5} más)`);
    console.log('');
  }
  await browser.close();
  fs.writeFileSync('shortname_items.json', JSON.stringify(out, null, 2));
  console.log('✓ Guardado: shortname_items.json');
})();
