/**
 * Run this in Chrome DevTools Console while logged into FareHarbor (fareharbor.com).
 * Fetches real Filestack image IDs for the 52 operators with placeholder images.
 * Paste entire script → hit Enter → wait ~30 seconds → copy the output JSON.
 */

const SLUGS = [
  '100miami','100proboats','altamartrade','aquaholic-charters','aquariusboatrental',
  'bluwaterrentals','boatpartyfortlauderdale','bonitajetski','bruschiboatrental',
  'clearwaterbeachwaverunnerrentals','coastalcruises','cocoabeachcatamaran',
  'destinbonfirecompany','destinprivateyachts','ezraiderfortlauderdale',
  'floridaadventuresandrentals','gatorsparasail','getupandgokayaking-chaz',
  'getupandgokayaking-silversprings','getupandgokayaking-titusville',
  'hopeandjoysanctuary','jetskifl','jetskimiamirentals','johnspassparasail',
  'jonesairandsea','kokomocharters','luxejetskirentalorl','miamiaquatours',
  'nativeguidedfishing','paddlethefloridakeys','paradiseislandpontoonrentals',
  'paradisekw','paradiserentalskw','powerupwatersports','sail-keywest',
  'searocketftlauderdale','seasideadventures','sfjetskirentals','sidexsidestpete',
  'sixfinscharter','skytoursmiami','slingshotandjetskirentals','sobesurf',
  'solewatersports','southfloridatrikketours','sunsetwatersportskeywest',
  'suppaddleinflorida','treasurecoastexcursions','treasureseekersshelltours',
  'us2u','visitpalmbeach','wynwoodartwalk'
];

async function fetchCompanyImage(slug) {
  try {
    // Try the FH partner API company endpoint
    const url = `https://partner-be.fareharbor.com/api/company/?shortname=${slug}`;
    const r = await fetch(url, { credentials: 'include' });
    if (!r.ok) return null;
    const data = await r.json();
    const results = data.results || data;
    if (Array.isArray(results) && results.length > 0) {
      const c = results[0];
      const img = c.image_cdn_url || c.image_url || c.logo_url || c.photo_url || '';
      const m = img.match(/filestackcontent\.com\/([A-Za-z0-9]{10,})/);
      if (m) return m[1];
    }
  } catch(e) {}

  try {
    // Fallback: search partner marketplace items by company slug
    const url2 = `https://partner-be.fareharbor.com/api/item/?company__shortname=${slug}&page_size=5`;
    const r2 = await fetch(url2, { credentials: 'include' });
    if (!r2.ok) return null;
    const data2 = await r2.json();
    const items = data2.results || data2;
    if (Array.isArray(items) && items.length > 0) {
      for (const item of items) {
        const img = item.main_image_url || (item.images && item.images[0] && item.images[0].url) || '';
        const m = img.match(/filestackcontent\.com\/([A-Za-z0-9]{10,})/);
        if (m) return m[1];
      }
    }
  } catch(e) {}

  return null;
}

(async () => {
  console.log(`Fetching images for ${SLUGS.length} operators...`);
  const result = {};
  let found = 0;

  for (let i = 0; i < SLUGS.length; i++) {
    const slug = SLUGS[i];
    const imgId = await fetchCompanyImage(slug);
    if (imgId) {
      result[slug] = imgId;
      found++;
      console.log(`✅ ${slug}: ${imgId}`);
    } else {
      console.log(`❌ ${slug}: not found`);
    }
    // Small delay to avoid rate limiting
    await new Promise(r => setTimeout(r, 300));
  }

  console.log(`\n\n✅ Found ${found}/${SLUGS.length} images`);
  console.log('\n\n--- COPY THIS JSON ---\n');
  console.log(JSON.stringify(result, null, 2));
  console.log('\n--- END JSON ---');
})();
