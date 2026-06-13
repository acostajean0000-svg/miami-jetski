#!/usr/bin/env node
/**
 * discover_fareharbor_pw.js — Playwright-powered discovery de operadores FareHarbor.
 *
 * Renderiza páginas FareHarbor con JS habilitado para extraer items reales.
 *
 * Workflow:
 *   1. Lee shortnames de candidate-shortnames.txt (en repo root o pasado con --input)
 *   2. Filtra los que YA están en operators.json
 *   3. Para cada NUEVO, abre Playwright → fareharbor.com/embeds/book/{shortname}/
 *   4. Espera que se rendericen los items
 *   5. Extrae items + precios + fotos
 *   6. Output: proposed_new_ops.json
 *
 * Uso:
 *   NODE_OPTIONS='--max-old-space-size=4096' node discover_fareharbor_pw.js
 *   node discover_fareharbor_pw.js --input mi-archivo.txt --concurrency 3
 */

const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const argv = process.argv.slice(2);
const INPUT = argv.includes('--input') ? argv[argv.indexOf('--input')+1] : 'candidate-shortnames.txt';
const CONCURRENCY = parseInt(argv.includes('--concurrency') ? argv[argv.indexOf('--concurrency')+1] : '3', 10);
const TIMEOUT = 25000;

const FH_SHORTNAME_RE = /fareharbor\.com\/(?:embeds\/book\/)?([a-z0-9][a-z0-9-]+)/i;

function loadExistingShortnames() {
  const ops = JSON.parse(fs.readFileSync('operators.json', 'utf8'));
  const set = new Set();
  for (const o of ops) {
    const m = (o.link || '').match(FH_SHORTNAME_RE);
    if (m) set.add(m[1].toLowerCase());
  }
  return set;
}

function loadCandidates() {
  if (!fs.existsSync(INPUT)) {
    console.error(`❌ No existe ${INPUT}`);
    process.exit(1);
  }
  const lines = fs.readFileSync(INPUT, 'utf8').split('\n');
  const set = new Set();
  for (const raw of lines) {
    const line = raw.trim();
    if (!line || line.startsWith('#')) continue;
    const m = line.match(FH_SHORTNAME_RE);
    if (m) set.add(m[1].toLowerCase());
    else if (/^[a-z0-9-]+$/.test(line)) set.add(line.toLowerCase());
  }
  return [...set];
}

function guessCat(text) {
  const t = text.toLowerCase();
  const rules = [
    ['jetski',     /jet ski|pwc|waverunner/],
    ['yacht',      /yacht|mega yacht|luxury charter/],
    ['boat',       /boat (?:rental|charter|tour)|pontoon|center console|sail/],
    ['fishing',    /fishing (?:charter|trip)|deep sea|inshore|offshore/],
    ['snorkel',    /snorkel|dive|scuba/],
    ['sunset',     /sunset (?:cruise|sail)/],
    ['atv',        /\batv\b|utv|side.by.side|buggy/],
    ['aerial',     /parasail|helicopter|skydiv|sea ?plane/],
    ['bikerental', /bike rental|e.bike|bicycle|pedal/],
    ['watersports', /water sports|kayak|paddle ?board|sup\b/],
    ['airboat',    /airboat|everglades/],
    ['wildlife',   /whale|dolphin (?:watch|tour|encounter)|manatee|safari/],
    ['ghost',      /ghost (?:tour|hunt|walk)|haunted|paranormal|pub crawl/],
    ['culinary',   /food (?:tour|tasting)|wine (?:tour|tasting)|cooking class|tequila/],
    ['golf',       /\bgolf\b/],
    ['mayan_cenote', /cenote|mayan|chichen.?itza|tulum.*ruins/],
    ['themepark',  /disney|universal studios|seaworld|legoland/],
    ['walking_tour', /walking tour|historic walk|art deco/],
    ['lei',        /lei greeting/],
    ['segway',     /segway/],
    ['zipline',    /zip ?line|canopy tour/],
    ['nightlife',  /nightclub|coco bongo|night club/],
    ['tour',       /tour|sightseeing/],
  ];
  for (const [cat, re] of rules) if (re.test(t)) return cat;
  return 'tour';
}

function guessZone(text) {
  const t = text.toLowerCase();
  const rules = [
    ['miami',       /miami beach|miami(?! beach)|south beach|brickell/],
    ['broward',     /fort lauderdale|broward|hollywood (?:fl|beach)/],
    ['keys',        /key west|marathon fl|key largo|islamorada/],
    ['palmbeach',   /palm beach|jupiter/],
    ['nefl',        /jacksonville|st\.? augustine|amelia island/],
    ['orlando',     /orlando|kissimmee|disney/],
    ['space',       /cocoa beach|cape canaveral|space coast|merritt island/],
    ['westfl',      /naples|marco island|fort myers|tampa|destin|panama city|sarasota/],
    ['hawaii',      /maui|oahu|kauai|kona|hawaii|honolulu|hilo|lihue|kahului/],
    ['cancun',      /cancun|playa del carmen|tulum|riviera maya/],
    ['puntacana',   /punta cana|bavaro|bayahibe|la romana/],
  ];
  for (const [zone, re] of rules) if (re.test(t)) return zone;
  return 'unknown';
}

async function verifyShortname(browser, shortname) {
  const ctx = await browser.newContext({
    userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    viewport: {width:1280, height:800},
  });
  const page = await ctx.newPage();

  // CLAVE: interceptar todos los XHR/fetch responses para capturar la API de items
  const apiResponses = [];
  page.on('response', async (response) => {
    try {
      const url = response.url();
      const ct = (response.headers()['content-type'] || '').toLowerCase();
      // FareHarbor API endpoints (varios formatos posibles)
      if (ct.includes('application/json') && /fareharbor\.com/.test(url)) {
        // Capturar solo respuestas relevantes (items/companies/etc)
        if (/\/(items|companies|company|landings|pages|public)\b/.test(url)) {
          const body = await response.text();
          apiResponses.push({url, body: body.slice(0, 200000)});
        }
      }
    } catch (e) {}
  });

  try {
    const url = `https://fareharbor.com/embeds/book/${shortname}/`;
    const resp = await page.goto(url, {waitUntil: 'domcontentloaded', timeout: TIMEOUT});
    const status = resp ? resp.status() : 0;

    if (status === 404 || status === 410) {
      return {shortname, status: 'not_found', http_code: status, reason: 'Shortname no existe'};
    }
    if (status === 403) {
      return {shortname, status: 'forbidden', http_code: 403, reason: 'Bloqueado'};
    }
    if (status !== 200) {
      return {shortname, status: `http_${status}`, http_code: status};
    }

    // Esperar dwell larguito para que carguen XHR + Angular renderice items
    await page.waitForTimeout(7000);

    // Estrategia 1: parsear las API responses interceptadas
    const items = [];
    const seen = new Set();
    let companyName = '';

    for (const r of apiResponses) {
      try {
        const j = JSON.parse(r.body);
        // FareHarbor API responses tienen distintas estructuras según endpoint
        // Buscar items en cualquier nivel del JSON
        const stack = [j];
        while (stack.length) {
          const node = stack.pop();
          if (!node || typeof node !== 'object') continue;
          // Detectar nombre de empresa
          if (node.shortname === shortname && node.name && !companyName) {
            companyName = node.name;
          }
          // Detectar items
          if (node.pk && (node.name || node.headline) && (node.is_bookable !== false)) {
            const id = String(node.pk);
            const name = node.name || node.headline;
            if (id && name && !seen.has(id) && /^\d+$/.test(id)) {
              seen.add(id);
              items.push({id, name: String(name).slice(0, 120)});
            }
          }
          if (Array.isArray(node)) {
            for (const v of node) stack.push(v);
          } else {
            for (const k in node) {
              if (typeof node[k] === 'object') stack.push(node[k]);
            }
          }
        }
      } catch (e) {}
    }

    // Fallback estrategia 2: DOM + regex en HTML completo (por si la API no estaba en allowlist)
    if (!items.length) {
      const html = await page.content();
      // Buscar item IDs en cualquier URL/atributo de la página
      const itemIdRe = /\/items\/(\d+)\b/g;
      const idsFromHtml = new Set();
      let m;
      while ((m = itemIdRe.exec(html))) idsFromHtml.add(m[1]);

      const data = await page.evaluate(() => {
        const itemMap = {};
        document.querySelectorAll('a').forEach(a => {
          const href = a.href || '';
          const m = href.match(/\/items\/(\d+)/);
          if (m) {
            const name = (a.textContent || '').trim().slice(0, 150).replace(/\s+/g, ' ');
            if (name && name.length > 2 && !itemMap[m[1]]) itemMap[m[1]] = name;
          }
        });
        const title = (document.title || '').replace(/^Book Online[\s\-—:]*/i, '').trim();
        const h1 = document.querySelector('h1')?.textContent?.trim() || '';
        return {itemMap, title, h1};
      });

      for (const id of idsFromHtml) {
        items.push({id, name: (data.itemMap[id] || `Item #${id}`).slice(0, 120)});
      }
      if (!companyName) companyName = data.h1 || data.title || shortname;
    }

    if (!items.length) {
      return {
        shortname,
        status: 'exists_no_items',
        http_code: 200,
        company_name: companyName || shortname,
        main_url: url,
        reason: `Pagina existe pero 0 items detectados (revisé ${apiResponses.length} API calls). Posible: company sin items activos, FH cambió estructura o anti-bot.`,
        items: [],
        item_count: 0,
        guessed_cat: 'tour',
        guessed_zone: 'unknown',
      };
    }

    const allText = (companyName + ' ' + items.map(i=>i.name).join(' ')).toLowerCase();
    return {
      shortname,
      status: 'ok',
      http_code: 200,
      company_name: companyName || shortname,
      items: items.slice(0, 30),
      item_count: items.length,
      guessed_cat: guessCat(allText),
      guessed_zone: guessZone(allText),
      main_url: url,
      verified_at: new Date().toISOString().slice(0, 10),
    };
  } catch (e) {
    return {shortname, status: 'error', reason: String(e).slice(0, 120)};
  } finally {
    await ctx.close();
  }
}

async function main() {
  console.log('═══ FareHarbor Discovery (Playwright) ═══\n');

  const existing = loadExistingShortnames();
  const candidates = loadCandidates();
  console.log(`Operadores existentes: ${existing.size} shortnames únicos`);
  console.log(`Candidatos en archivo: ${candidates.length}`);

  const newOnes = candidates.filter(s => !existing.has(s));
  console.log(`Ya existentes (skip):  ${candidates.length - newOnes.length}`);
  console.log(`NUEVOS a verificar:    ${newOnes.length}\n`);

  if (!newOnes.length) {
    console.log('✓ No hay shortnames nuevos.');
    return;
  }

  const browser = await chromium.launch({headless: true});
  const results = [];
  let done = 0;

  // Procesar en batches concurrentes
  const queue = [...newOnes];
  async function worker() {
    while (queue.length) {
      const sn = queue.shift();
      const r = await verifyShortname(browser, sn);
      done++;
      results.push(r);
      const st = r.status;
      const emoji = st === 'ok' ? '✓' : st === 'exists_no_items' ? '⚠' :
                    st === 'not_found' ? '✗' : st === 'forbidden' ? '⛔' : '❌';
      const info = st === 'ok' ?
        `${r.company_name?.slice(0,35)?.padEnd(35)} (${r.item_count} items, ${r.guessed_cat}/${r.guessed_zone})` :
        (r.reason || st);
      console.log(`  ${emoji} [${done}/${newOnes.length}] ${sn.padEnd(30)} — ${info}`);
    }
  }

  await Promise.all(Array(CONCURRENCY).fill(0).map(worker));
  await browser.close();

  const byStatus = {ok:[], exists_no_items:[], not_found:[], forbidden:[], other:[]};
  for (const r of results) {
    if (byStatus[r.status]) byStatus[r.status].push(r);
    else byStatus.other.push(r);
  }

  console.log(`\n${'═'.repeat(70)}`);
  console.log('  RESUMEN:');
  console.log(`  ✓ Verificados completos:    ${byStatus.ok.length}`);
  console.log(`  ⚠ Existen, revisar manual:  ${byStatus.exists_no_items.length}`);
  console.log(`  ✗ No encontrados (404):     ${byStatus.not_found.length}`);
  console.log(`  ⛔ Bloqueados (403):         ${byStatus.forbidden.length}`);
  console.log(`  ❌ Otros errores:           ${byStatus.other.length}`);

  // Guardar
  const newOps = [...byStatus.ok, ...byStatus.exists_no_items];
  const output = {
    generated_at: new Date().toISOString(),
    method: 'playwright',
    existing_count: existing.size,
    candidates_checked: candidates.length,
    new_ops_found: newOps.length,
    fully_verified: byStatus.ok.map(o => o.shortname),
    needs_manual_review: byStatus.exists_no_items.map(o => o.shortname),
    not_found_404: byStatus.not_found.map(o => o.shortname),
    forbidden_403: byStatus.forbidden.map(o => o.shortname),
    other_errors: byStatus.other.map(o => ({shortname: o.shortname, reason: o.reason})),
    new_ops: newOps.sort((a,b) => (a.guessed_zone||'').localeCompare(b.guessed_zone||'') ||
                                   (a.guessed_cat||'').localeCompare(b.guessed_cat||'')),
  };
  fs.writeFileSync('proposed_new_ops.json', JSON.stringify(output, null, 2));
  console.log(`\n✓ Reporte: proposed_new_ops.json`);

  if (byStatus.ok.length) {
    console.log(`\nLISTOS PARA MERGEAR:`);
    console.log(`  python3 merge_proposed_ops.py --list`);
    const sample = byStatus.ok.slice(0,3).map(o=>o.shortname).join(',');
    console.log(`  python3 merge_proposed_ops.py --approve ${sample}${byStatus.ok.length>3?'...':''}`);
  }
}

main().catch(e => { console.error(e); process.exit(1); });
