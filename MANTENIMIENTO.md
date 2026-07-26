# Guía de mantenimiento — miamijetskiboatrentals.com

*Última actualización: 26 julio 2026. Documento generado tras la gran sesión de expansión y auditoría.*

## Arquitectura

Sitio estático (~12.000 HTML) en **Vercel**, con `cleanUrls: true` y `trailingSlash: false`.

**Datos maestros (fuente de verdad):**
| Archivo | Contenido |
|---|---|
| `operators.json` | 11.076 operadores, todos los campos (7.7 MB) |
| `operators-slim.json` | Igual sin `desc` — lo cargan las páginas (3.2 MB) |
| `operators-top.json` | Top ~1.100 (3 por zona×categoría) — **fase 1 del home** (326 KB). REGENERAR si cambian operadores |
| `slug-map.js` | `window._OP_SLUG_MAP = {id: slug}` — 11.076 entradas |
| `data/{zona}.json` | Operadores de una zona (para páginas -activities) |
| `data/{zona}-{cat}.json` | Operadores de zona+categoría (para landings) |

**Regla de oro:** los data files y las páginas son DERIVADOS de operators.json.
Si cambias un operador (precio, rating, categoría), hay que propagar a: operators-slim,
operators-top, data/*, y los valores horneados en HTML (conteos, ratings, ItemList).

## Tipos de página

| Tipo | Ejemplo | Cuántas |
|---|---|---|
| Home | `index.html`, `es/index.html` | 2 |
| Zona | `{zona}-activities.html` (+`es/`) | 45 + 45 |
| Landing de categoría | `{ciudad}-{categoria}.html` (+`es/`) | 131 + 131 |
| Operador | `{slug}.html` | 11.076 |
| Blog | `blog/*.html` | 87 + índice |
| Legales/infra | about, contact, privacy, terms, 404, offline | — |

**Links de FareHarbor:** siempre con `asn-ref=miamistylerentals&ref=miamistylerentals`.
Formato shortcode en data files flagship: `"shortname/itemid"` — la página lo expande con LINK_TPL.

## Generadores (en la carpeta outputs de la sesión Cowork)

- `catgen2.py` — landings EN por categoría. Config `ZONES` + umbral 20 ops. Deriva TODO de los datos (conteos, áreas con umbral ≥3 ops y ≥5%, centroide, ItemList).
- `es_catgen.py` — versiones ES de landings de categoría (tabla GEN + frames con variables).
- `es_gen.py` — versiones ES de flagships jet ski (config por ciudad con FAQ de licencia).
- `oggen.py` — imágenes OG 1200×630 por landing (actualizar su lista BASES al añadir zonas).
- `fix_desc.py` — meta descriptions únicas de operadores desde el dato.

## Checklist al añadir una zona/landing nueva

1. Operadores en operators.json con: id único (prefijo de zona), zone, cat, zl, coords VÁLIDAS (¡lat>0, lng<0 en América!), link con ref, price
2. Generar data files + landing (catgen2) + versión ES (es_catgen)
3. Post-fixes obligatorios (los bugs históricos): footer con destinos correctos, cross-links a la MISMA categoría, H1 según categoría, emoji según categoría
4. Imagen OG propia + og:image apuntándola
5. hreflang recíproco EN↔ES + toggles 🇪🇸/🇺🇸 en topbar
6. Registrar en `sitemaps/landing.xml` y `sitemaps/es.xml` con lastmod real
7. Enlazar desde el hub de zona (bloque CAT_LANDING_LINKS) y home (bloque CATEGORY_CITY_LINKS)

## Validación estándar (los 9 puntos)

Por cada página nueva/modificada:
- `node --check` del script principal · JSON-LD parsea · conteo declarado == len(data file)
- sin residuo de plantilla (Miami/Key West fuera de sus páginas) · geo correcta (no 25.7617 fuera de Miami)
- tracking `value:'+(o.price||100)+'` presente · og:image existe · links internos existen · ES sin inglés visible

## Deploy

```
script: ~/Desktop/update repos/miamijetskiboat.command
flujo:  rsync miami-jetski-main → iCloud…/GitHub/miami-jetski → commit → push → Vercel
```
- Credencial del push: token classic (scope repo) de **acostajean0000-svg** en Keychain (helper osxkeychain).
- Si el push falla con "Invalid username or token": el token caducó → github.com/settings/tokens (cuenta acostajean0000-svg, token CLASSIC, scope repo).
- GitHub Desktop usa credencial propia (sign-in por navegador) — sirve de plan B para push manual.
- El repo de trabajo (miami-jetski-main) tiene su propio git local SIN remote; el commit ahí es solo checkpoint.

## Convenciones y trampas conocidas

- **Zonas con clave interna ≠ slug**: broward→fort-lauderdale, nefl→northeast-florida, westfl→west-florida, keywest→key-west, laketahoe→lake-tahoe, etc.
- **cat `walking_tour`** usa guion bajo (el data file es `-walking_tour.json` renombrado a `-walking-tour.json` en algunos casos — verificar).
- **`/gulf-activities` y `/keywest-activities`** son URLs históricas: viven como 301 en vercel.json. No enlazarlas internamente.
- Página especial: `miami-bloom-bar-flowers` reserva por WhatsApp (sin ref FareHarbor — correcto).
- `swamp-cottage-rental-…-everglades` es huérfana intencional (operador retirado, aún convierte).
- Los 4 productos Cozumel cross-listados en Cancún canonicalizan a la versión Cozumel y están FUERA del sitemap.
- Cache: HTML no-cache; data/*.json 1h+SWR; og/, icons/, vendor/ inmutables. Al cambiar lógica del SW, subir versión en `sw.js` (CACHE_NAME/RUNTIME_CACHE).

## Historial de la gran sesión (jul 2026) — para contexto

Corregido: 991 coords invertidas (Charleston/Hilton Head), 8.565 geo de páginas de operador,
4.511 meta descriptions genéricas→únicas, 228 títulos duplicados (diferenciados con ⭐rating),
142 etiquetas tras reclasificar tour→bike/jetski, JSON-LD de zonas (ItemList/FAQ/@id/geo),
hreflang roto en 64 landings, traducción completa de /es/, JS roto en 4 páginas ({{ }}),
550 rel-cards fantasma, slug-map corrupto (at119). Construido: 131 pares de landings bilingües,
176 OG, carga en 2 fases del home (86% menos primer render), 77 CTAs de blog.
