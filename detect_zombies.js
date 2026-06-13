#!/usr/bin/env node
/**
 * detect_zombies.js — detecta shortnames FareHarbor que devuelven páginas vacías
 *
 * Para cada shortname único en operators.json:
 *   1. Abre fareharbor.com/embeds/book/{shortname}/
 *   2. Espera 4s para que cargue el contenido
 *   3. Cuenta items bookables (productos)
 *   4. Si 0 items → ZOMBIE (operator pausado/cerrado)
 *
 * Output: zombie_shortnames.json
 *
 * Throttling: concurrency 2, 1s delay entre ops por worker = ~0.5/s rate
 * Total: ~600 shortnames × 5s = ~50 min. Resume-safe (puedes interrumpir).
 *
 * Uso:
 *   node detect_zombies.js
 *   node detect_zombies.js --limit 50   # solo top 50 más usados
 *   node detect_zombies.js --no-resume  # empezar desde cero
 */
const fs = require('fs');
const { chromium } = require('playwright');

const argv = process.argv.slice(2);
const LIMIT = parseInt(argv.includes('--limit') ? argv[argv.indexOf('--limit')+1] : '0', 10);
const CONCURRENCY = 2;
const DELAY_MS = 1000;
const RESUME = !argv.includes('--no-resume');
const OUT = 'zombie_shortnames.json';

// 1. Extraer shortnames únicos
const ops = JSON.parse(fs.readFileSync('operators.json','utf8'));
const sn_to_ops = {};
for (const o of ops) {
  const m = (o.link||'').match(/\/book\/([^/?]+)/);
  if (!m) continue;
  (sn_to_ops[m[1]] = sn_to_ops[m[1]] || []).push(o.id);
}

let shortnames = Object.entries(sn_to_ops).sort((a,b) => b[1].length - a[1].length);
if (LIMIT > 0) shortnames = shortnames.slice(0, LIMIT);

console.log(`Total shortnames únicos: ${Object.keys(sn_to_ops).length}`);
console.log(`A verificar en esta corrida: ${shortnames.length}`);

// 2. Resume
let results = {};
if (RESUME && fs.existsSync(OUT)) {
  results = JSON.parse(fs.readFileSync(OUT,'utf8'));
  console.log(`Resuming: ${Object.keys(results).length} ya verificados`);
}

const todo = shortnames.filter(([sn]) => !results[sn]);
console.log(`Pendientes: ${todo.length}\n`);

async function probe(browser, shortname) {
  const ctx = await browser.newContext({
    userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
  });
  const page = await ctx.newPage();
  let itemCount = 0;
  let companyName = '';

  page.on('response', async (response) => {
    try {
      const ct = (response.headers()['content-type'] || '').toLowerCase();
      if (!ct.includes('application/json') || !/fareharbor\.com/.test(response.url())) return;
      const body = await response.text();
      const j = JSON.parse(body);
      const stack = [j];
      while (stack.length) {
        const node = stack.pop();
        if (!node || typeof node !== 'object') continue;
        if (node.shortname === shortname && node.name && !companyName) companyName = node.name;
        if (node.pk && node.name && node.is_bookable !== false && typeof node.name === 'string' && node.name.length > 3 && !/default booking|gift card/i.test(node.name)) itemCount++;
        if (Array.isArray(node)) for (const v of node) stack.push(v);
        else for (const k in node) if (typeof node[k] === 'object') stack.push(node[k]);
      }
    } catch(e){}
  });

  let status = 0;
  try {
    const resp = await page.goto(`https://fareharbor.com/embeds/book/${shortname}/`, {waitUntil: 'domcontentloaded', timeout: 18000});
    status = resp ? resp.status() : 0;
    if (status === 200) await page.waitForTimeout(4500);
  } catch(e){ status = -1; }
  await ctx.close();
  return {status, itemCount, companyName, zombie: status === 200 && itemCount === 0};
}

(async () => {
  const browser = await chromium.launch({headless: true});
  const t0 = Date.now();
  let done = 0;
  const queue = [...todo];

  async function worker(id) {
    while (queue.length) {
      const [sn, opIds] = queue.shift();
      try {
        const r = await probe(browser, sn);
        results[sn] = {...r, ops: opIds.length};
        done++;
        const tag = r.zombie ? '🧟 ZOMBIE' : r.status === 200 ? `✓ ${r.itemCount} items` : `✗ ${r.status}`;
        const elapsed = ((Date.now()-t0)/1000).toFixed(0);
        console.log(`  [${done}/${todo.length}] ${elapsed}s · ${sn.padEnd(28)} → ${tag.padEnd(15)} (${opIds.length} ops)`);
        if (done % 10 === 0) fs.writeFileSync(OUT, JSON.stringify(results, null, 2));
        await new Promise(r => setTimeout(r, DELAY_MS));
      } catch(e){ console.error(`  ERR ${sn}: ${e.message}`); }
    }
  }

  await Promise.all(Array(CONCURRENCY).fill(0).map(worker));
  await browser.close();
  fs.writeFileSync(OUT, JSON.stringify(results, null, 2));

  const zombies = Object.entries(results).filter(([_,r]) => r.zombie);
  const zombieOps = zombies.reduce((sum,[_,r]) => sum + r.ops, 0);
  console.log(`\n═ RESUMEN ═`);
  console.log(`  Shortnames probados:  ${Object.keys(results).length}`);
  console.log(`  Zombies detectados:   ${zombies.length}`);
  console.log(`  Ops afectados:        ${zombieOps}`);
  console.log(`\nOutput: ${OUT}`);
  console.log(`Próximo: python3 remove_zombies.py para limpiar operators.json`);
})();
