#!/usr/bin/env python3
"""SEO audit — auditoria masiva sobre 4,874 HTMLs."""
import re, json, glob, os
from collections import Counter, defaultdict

DOMAIN = 'https://miamijetskiboatrentals.com'

# Patrones
TITLE_RE        = re.compile(r'<title[^>]*>([^<]*)</title>', re.I)
DESC_RE         = re.compile(r'<meta[^>]+name=["\']description["\'][^>]*content=["\']([^"\']*)["\']', re.I)
CANONICAL_RE    = re.compile(r'<link[^>]+rel=["\']canonical["\'][^>]*href=["\']([^"\']*)["\']', re.I)
OG_TITLE_RE     = re.compile(r'<meta[^>]+property=["\']og:title["\'][^>]*content=["\']([^"\']*)["\']', re.I)
OG_DESC_RE      = re.compile(r'<meta[^>]+property=["\']og:description["\'][^>]*content=["\']([^"\']*)["\']', re.I)
OG_IMAGE_RE     = re.compile(r'<meta[^>]+property=["\']og:image["\'][^>]*content=["\']([^"\']*)["\']', re.I)
OG_URL_RE       = re.compile(r'<meta[^>]+property=["\']og:url["\'][^>]*content=["\']([^"\']*)["\']', re.I)
TWITTER_RE      = re.compile(r'<meta[^>]+name=["\']twitter:', re.I)
ROBOTS_RE       = re.compile(r'<meta[^>]+name=["\']robots["\'][^>]*content=["\']([^"\']*)["\']', re.I)
H1_RE           = re.compile(r'<h1[^>]*>(.*?)</h1>', re.I|re.S)
H2_RE           = re.compile(r'<h2[^>]*>(.*?)</h2>', re.I|re.S)
IMG_RE          = re.compile(r'<img[^>]*?(?:src=["\']([^"\']*)["\'][^>]*?(?:alt=["\']([^"\']*)["\'])?|alt=["\']([^"\']*)["\'][^>]*?src=["\']([^"\']*)["\'])', re.I)
SCHEMA_RE       = re.compile(r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', re.I|re.S)
LANG_RE         = re.compile(r'<html[^>]+lang=["\']([^"\']*)["\']', re.I)
VIEWPORT_RE     = re.compile(r'<meta[^>]+name=["\']viewport["\'][^>]*content=["\']([^"\']*)["\']', re.I)
HREFLANG_RE     = re.compile(r'<link[^>]+hreflang=["\']([^"\']*)["\']', re.I)
STRIP_TAGS_RE   = re.compile(r'<[^>]+>')


def strip_tags(s):
    return STRIP_TAGS_RE.sub('', s).strip()


def audit_file(fp):
    """Extrae métricas SEO de un HTML."""
    try:
        with open(fp, 'r', encoding='utf-8', errors='ignore') as f:
            html = f.read()
    except Exception as e:
        return None

    m = TITLE_RE.search(html)
    title = m.group(1).strip() if m else None

    m = DESC_RE.search(html)
    desc = m.group(1).strip() if m else None

    m = CANONICAL_RE.search(html)
    canonical = m.group(1).strip() if m else None

    m = OG_TITLE_RE.search(html);  og_title = m.group(1).strip() if m else None
    m = OG_DESC_RE.search(html);   og_desc  = m.group(1).strip() if m else None
    m = OG_IMAGE_RE.search(html);  og_img   = m.group(1).strip() if m else None
    m = OG_URL_RE.search(html);    og_url   = m.group(1).strip() if m else None

    twitter_tags = len(TWITTER_RE.findall(html))

    m = ROBOTS_RE.search(html)
    robots = m.group(1).strip() if m else None

    h1s = [strip_tags(x) for x in H1_RE.findall(html)]
    h2s = [strip_tags(x) for x in H2_RE.findall(html)]

    # Imgs y alt
    img_count = html.lower().count('<img')
    imgs_without_alt = 0
    for img_match in re.finditer(r'<img[^>]*>', html, re.I):
        tag = img_match.group(0)
        if not re.search(r'\balt\s*=\s*["\']', tag, re.I):
            imgs_without_alt += 1

    schemas = SCHEMA_RE.findall(html)
    schema_types = []
    for s in schemas:
        for t in re.findall(r'"@type"\s*:\s*"([^"]+)"', s):
            schema_types.append(t)

    m = LANG_RE.search(html); lang = m.group(1) if m else None
    m = VIEWPORT_RE.search(html); viewport = m.group(1) if m else None
    hreflangs = HREFLANG_RE.findall(html)

    return {
        'file':         os.path.basename(fp),
        'title':        title,
        'title_len':    len(title) if title else 0,
        'desc':         desc,
        'desc_len':     len(desc) if desc else 0,
        'canonical':    canonical,
        'og_title':     og_title,
        'og_desc':      og_desc,
        'og_image':     og_img,
        'og_url':       og_url,
        'twitter_tags': twitter_tags,
        'robots':       robots,
        'h1_count':     len(h1s),
        'h1s':          h1s,
        'h2_count':     len(h2s),
        'img_count':    img_count,
        'imgs_no_alt':  imgs_without_alt,
        'schema_types': schema_types,
        'lang':         lang,
        'viewport':     viewport,
        'hreflangs':    hreflangs,
        'size_kb':      round(len(html)/1024, 1),
    }


def main():
    htmls = sorted(glob.glob('*.html'))
    print(f'Auditando {len(htmls)} HTMLs...\n')

    results = []
    for fp in htmls:
        r = audit_file(fp)
        if r: results.append(r)

    print(f'═' * 80)
    print(f'  SEO AUDIT REPORT — {len(results)} páginas')
    print(f'═' * 80)

    # ── TITLES ────────────────────────────────────────────
    print('\n► TITLES')
    no_title = [r for r in results if not r['title']]
    short = [r for r in results if r['title'] and r['title_len'] < 30]
    long = [r for r in results if r['title_len'] > 70]
    print(f'  Sin title:       {len(no_title)}')
    print(f'  < 30 chars:      {len(short)}')
    print(f'  > 70 chars:      {len(long)}')
    titles = Counter(r['title'] for r in results if r['title'])
    dupes = {t: n for t, n in titles.items() if n > 1}
    print(f'  Titles duplicados (mismo en >1 págs): {len(dupes)}')
    if dupes:
        for t, n in list(dupes.items())[:3]:
            print(f'    {n}×  "{t[:70]}"')

    # ── DESCRIPTIONS ──────────────────────────────────────
    print('\n► META DESCRIPTIONS')
    no_desc = [r for r in results if not r['desc']]
    short = [r for r in results if r['desc'] and r['desc_len'] < 70]
    long = [r for r in results if r['desc_len'] > 160]
    print(f'  Sin description: {len(no_desc)}')
    print(f'  < 70 chars:      {len(short)}')
    print(f'  > 160 chars:     {len(long)}')
    descs = Counter(r['desc'] for r in results if r['desc'])
    desc_dupes = {d: n for d, n in descs.items() if n > 1}
    print(f'  Descs duplicadas: {len(desc_dupes)}')
    if desc_dupes:
        for d, n in list(desc_dupes.items())[:3]:
            print(f'    {n}×  "{d[:80]}"')

    # ── CANONICAL ─────────────────────────────────────────
    print('\n► CANONICAL URLS')
    no_canon = [r for r in results if not r['canonical']]
    print(f'  Sin canonical:   {len(no_canon)}')
    if no_canon:
        for r in no_canon[:5]:
            print(f'    {r["file"]}')
    # ¿canonical apunta al propio archivo?
    canon_mismatch = 0
    canon_external = 0
    for r in results:
        if not r['canonical']: continue
        if not r['canonical'].startswith(DOMAIN):
            canon_external += 1
    print(f'  Canonical apunta fuera del dominio: {canon_external}')

    # ── OPEN GRAPH ────────────────────────────────────────
    print('\n► OPEN GRAPH')
    no_og_title = sum(1 for r in results if not r['og_title'])
    no_og_desc = sum(1 for r in results if not r['og_desc'])
    no_og_img = sum(1 for r in results if not r['og_image'])
    no_og_url = sum(1 for r in results if not r['og_url'])
    print(f'  Sin og:title:   {no_og_title}')
    print(f'  Sin og:description: {no_og_desc}')
    print(f'  Sin og:image:   {no_og_img}')
    print(f'  Sin og:url:     {no_og_url}')

    # Twitter
    no_twitter = sum(1 for r in results if r['twitter_tags'] == 0)
    print(f'  Sin twitter: tags: {no_twitter}')

    # ── ROBOTS ────────────────────────────────────────────
    print('\n► ROBOTS META')
    robots_blocked = [r for r in results if r['robots'] and 'noindex' in r['robots'].lower()]
    print(f'  Páginas con noindex: {len(robots_blocked)}')
    if robots_blocked:
        for r in robots_blocked[:5]:
            print(f'    {r["file"]} → {r["robots"]}')

    # ── HEADERS ───────────────────────────────────────────
    print('\n► HEADERS')
    no_h1 = [r for r in results if r['h1_count'] == 0]
    multi_h1 = [r for r in results if r['h1_count'] > 1]
    print(f'  Sin H1:          {len(no_h1)}')
    print(f'  > 1 H1:          {len(multi_h1)}')
    no_h2 = [r for r in results if r['h2_count'] == 0]
    print(f'  Sin H2:          {len(no_h2)}')

    # ── IMAGES ────────────────────────────────────────────
    print('\n► IMAGES & ALT TEXT')
    total_imgs = sum(r['img_count'] for r in results)
    total_no_alt = sum(r['imgs_no_alt'] for r in results)
    pages_with_missing = sum(1 for r in results if r['imgs_no_alt'] > 0)
    print(f'  Total imgs:      {total_imgs}')
    print(f'  Imgs sin alt:    {total_no_alt}')
    print(f'  Páginas con imgs sin alt: {pages_with_missing}')

    # ── SCHEMA ────────────────────────────────────────────
    print('\n► SCHEMA.ORG')
    no_schema = [r for r in results if not r['schema_types']]
    print(f'  Sin schema:      {len(no_schema)}')
    type_counts = Counter()
    for r in results:
        for t in r['schema_types']:
            type_counts[t] += 1
    print(f'  Tipos schema usados:')
    for t, n in type_counts.most_common(10):
        print(f'    {t:<25} {n} págs')

    # ── HTML LANG ─────────────────────────────────────────
    print('\n► HTML LANG')
    no_lang = [r for r in results if not r['lang']]
    print(f'  Sin lang:        {len(no_lang)}')
    lang_dist = Counter(r['lang'] for r in results if r['lang'])
    for l, n in lang_dist.most_common(5):
        print(f'    {l}: {n}')

    # ── VIEWPORT ──────────────────────────────────────────
    print('\n► VIEWPORT (mobile)')
    no_viewport = [r for r in results if not r['viewport']]
    print(f'  Sin viewport:    {len(no_viewport)}')

    # ── PAGE SIZE ─────────────────────────────────────────
    print('\n► PAGE SIZE')
    sizes = [r['size_kb'] for r in results]
    avg = sum(sizes)/len(sizes)
    print(f'  Promedio:        {avg:.1f} KB')
    print(f'  Min:             {min(sizes):.1f} KB')
    print(f'  Max:             {max(sizes):.1f} KB')
    largest = sorted(results, key=lambda r: -r['size_kb'])[:5]
    print(f'  Top 5 más grandes:')
    for r in largest:
        print(f'    {r["size_kb"]:>6.1f} KB  {r["file"]}')

    # ── SITEMAP / ROBOTS.TXT ──────────────────────────────
    print('\n► SITEMAP & ROBOTS.TXT')
    try:
        sm = open('sitemap.xml').read()
        urls = re.findall(r'<loc>([^<]+)</loc>', sm)
        print(f'  URLs en sitemap: {len(urls)}')
        # ¿Apuntan al dominio correcto?
        wrong_domain = sum(1 for u in urls if not u.startswith(DOMAIN))
        print(f'  URLs con dominio incorrecto: {wrong_domain}')
        # ¿lastmod presente?
        lastmods = len(re.findall(r'<lastmod>', sm))
        print(f'  URLs con <lastmod>: {lastmods}')
    except Exception as e:
        print(f'  ⚠️ sitemap.xml no leíble: {e}')

    try:
        rb = open('robots.txt').read()
        print(f'  robots.txt:')
        for line in rb.strip().split('\n')[:5]:
            print(f'    {line}')
    except Exception as e:
        print(f'  ⚠️ robots.txt no leíble: {e}')

    # ── SAMPLE ────────────────────────────────────────────
    print('\n► SAMPLE (3 random)')
    import random
    random.seed(42)
    for r in random.sample(results, 3):
        print(f'\n  📄 {r["file"]}')
        print(f'     title  ({r["title_len"]}): {r["title"][:80] if r["title"] else "(none)"}')
        print(f'     desc   ({r["desc_len"]}): {r["desc"][:80] if r["desc"] else "(none)"}')
        print(f'     canon: {r["canonical"]}')
        print(f'     og:   title={"✓" if r["og_title"] else "✗"} desc={"✓" if r["og_desc"] else "✗"} img={"✓" if r["og_image"] else "✗"} url={"✓" if r["og_url"] else "✗"}')
        print(f'     H1: {r["h1_count"]} · H2: {r["h2_count"]} · imgs: {r["img_count"]} (sin alt: {r["imgs_no_alt"]})')
        print(f'     schema: {", ".join(r["schema_types"]) or "(none)"}')

    # Guardar JSON con detalle
    with open('/tmp/seo-audit.json', 'w') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f'\n✓ Resultado completo en /tmp/seo-audit.json')


if __name__ == '__main__':
    main()
