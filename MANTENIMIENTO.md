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
| `data/cat/{cat}.json` | **Se olvida siempre.** 7 archivos por categoría global que usan 5 landings ES (snorkel-tours, yacht-charters, sunset-cruises, everglades-airboat-tours, miami-exotic-cars). Están fuera del patrón `data/*.json`, así que los scripts de propagación no los tocan |

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


## ⚠️ Dos reglas aprendidas a golpes (26 jul)

1. **Todo cambio de datos se propaga a AMBOS idiomas.** Al reclasificar 5 jet skis se actualizaron
   las landings EN pero no las ES (y en el arreglo posterior, al revés). La paridad EN↔ES
   (conteos, floor, offerCount, mapCount, data file) debe verificarse en cada cambio:
   comparar `N verified operators` vs `N operadores verificados` de cada par.

2. **$50 es el precio placeholder de las importaciones masivas** (80% de los registros `to*`).
   Al reclasificar un operador importado, revisar su precio contra la mediana de su zona+categoría
   — un jet ski a $50 en Tahoe (nativos a $130) es placeholder, no ganga. Nunca dejar que un
   placeholder se convierta en el "desde $X" de una landing.

## ⚠️ Reglas añadidas (28 jul)

3. **El "desde $X" de una landing se calcula EXCLUYENDO los `to*` a $50.** El mínimo crudo
   incluye placeholders de importación y hunde el precio anunciado. Fórmula correcta:
   `min([p for p in precios if not (p==50 and id.startswith('to'))])`.
   Yo mismo rebajé 3 landings a $50 usando el mínimo crudo antes de detectarlo.
   Si TODOS los precios del data file son `to*`-$50, no hay dato: el "$50" es desconocido,
   no barato (afecta a 48 landings de categoría `tour` — se arregla refrescando FareHarbor).

4. **Las tarjetas `rel-card` se reparten por anillo, no por top.** El generador antiguo ponía
   siempre los mismos 3 mejores de la zona: 49.192 enlaces concentrados en 2.740 destinos y
   8.045 operadores sin ningún enlace interno rastreable. Ahora cada operador enlaza a sus
   3 vecinos en el orden por rating dentro de zona+categoría (con caída a zona si el grupo
   es pequeño): cobertura 10.981/11.076, ~3 entrantes cada uno, 0 autoenlaces.
   Script: recrea el anillo tras CUALQUIER reclasificación de categoría.

5. **Reclasificar un operador toca 8 sitios**: operators.json, operators-slim, operators-top,
   `data/{zona}.json`, `data/{zona}-{cat_vieja}.json` (quitar), `data/{zona}-{cat_nueva}.json`
   (añadir, ojo al formato de `link` de cada archivo: unos usan shortcode y otros URL completa),
   los conteos horneados de AMBAS landings EN+ES, y el "View all X in Y" de su propia página.

6. **`/blog` lo sirve `blog.html`, NO `blog/index.html`.** Con `cleanUrls`, `/blog` resuelve
   a `blog.html`; `blog/index.html` solo se serviría en `/blog/`, que con `trailingSlash:false`
   redirige a `/blog`. Existían las dos y divergieron: la servida listaba 75 de 87 guías.
   Al publicar un post nuevo hay que enlazarlo en **`blog.html`** (y en `sitemaps/blog.xml`).
   Cuidado con `grep -c` en estos archivos: están minificados en una línea y cuenta 1.

7. **`<meta charset>` va inmediatamente después de `<head>`.** La plantilla metía antes un
   `<script>` con los TPL y en `index.html` el charset caía en el byte 1257 — pasado el
   límite de 1024 que garantiza la decodificación (riesgo de mojibake en acentos).

8. **El campo `photo` tiene DOS formatos y hay que soportar los dos.** 9.641 operadores lo
   guardan como URL completa y 1.435 como **clave suelta** (`SAGFuZPvQRQUqwevup8Y`).
   Regla: `url = photo if photo.startswith('http') else PHOTO_TPL % photo`.
   Esta suposición ha roto cosas dos veces: el generador de `og:image` dejó 1.339 páginas con
   una foto genérica de Unsplash teniendo foto propia, y mi generador de `rel-card` produjo
   4.005 `src` relativos (imágenes rotas). Hay además URLs del dominio antiguo
   `www.filepicker.io` (88): son válidas, no las trates como error.

9. **Los conteos viven en 6 sitios por landing, no en 2.** Además de `N verified operators` y
   `offerCount` están: `og:description` y `twitter:description` (con la variante
   `N verified <categoría> operators`), el chip `id="mapCount"`, y el precio del FAQ
   (`start around $X`). Verificar los seis o el desajuste sobrevive en el snippet de Google.

10. **Nunca sustituir conteos con regex de texto plano sobre toda la página.** Una landing de
    categoría contiene DOS conteos legítimos: el de su categoría (meta, mapCount) y el de su
    zona (dentro del nodo JSON-LD `TouristDestination`). Un `re.sub` global machaca uno con el
    otro — me pasó. Los nodos de zona se editan parseando el JSON, no por texto.

11. **Fuga de la plantilla de Naples en JSON-LD de zona** (43 páginas): `"264 verified activity
    operators"` (conteo de Naples), `"url": ".../gulf-activities"` (URL legacy 301) y
    `"Florida Watersports Marketplace"` en destinos de Texas, Nevada, Bahamas y Carolina del Sur.
    Al clonar una zona, revisar SIEMPRE los nodos `TouristDestination`/`WebSite`.

12. **La página partner `xtreme-car-rental-punta-cana-en` se tradujo a medias.** Los detectores
    de idioma por "3+ palabras funcionales en un nodo de texto" no ven: `alt` de imagen, mensajes
    pre-rellenados de `wa.me`, cadenas dentro del JS y frases cortas ("Sí, 0% prepago").
    Al auditar idioma hay que mirar esos cuatro sitios además del texto visible.

13. **Una traducción automática rompió el JavaScript de `es/index.html`** (28 jul): `classList`
    → `classLista` (83 veces) y `addEventListener` → `addEventListaener` (15), sin ningún
    `addEventListener` correcto en el archivo. La home española no enganchaba ni un evento:
    filtros, buscador, mapa, comparador y favoritos estaban muertos. **El `node --check` NO lo
    detecta**: es sintaxis válida, falla en tiempo de ejecución. Al traducir, la lista negra de
    identificadores intocables es: `classList, addEventListener, removeEventListener,
    querySelector(All), getElementById, textContent, innerHTML, dataset, Map, Date, List, Name`.
    Comprobación rápida tras cualquier traducción:
    `grep -c '\.addEventListener(' archivo` debe ser > 0.

14. **`vercel.json`: la regla `no-cache` de HTML no cubría las URLs reales.** Era
    `source: "/(.*\\.html)"`, pero con `cleanUrls` se sirve `/miami-jet-ski-rentals` sin
    extensión. Añadida `"/:path((?!.*\\.[a-zA-Z0-9]+$).*)"` al final de `headers` — coge solo
    rutas sin extensión, así que no toca `/data/`, `/og/`, `/vendor/` ni el CSS.

15. **Al auditar en vivo, usar siempre un parámetro anticaché** (`?nocache=fecha`). Una lectura
    normal me devolvió una copia antigua de la landing de Miami y me hizo pensar que faltaba el
    selector de idioma, que sí estaba publicado.

16. **`data/cat/*.json` llevaba 2 meses sin regenerarse** (fechados 30 mayo): 570 de 648
    registros con coordenadas obsoletas — uno situaba un operador en Cancún estando en Cozumel,
    80 km de error — más 10 precios y 1 categoría. Causa: el glob de propagación es `data/*.json`
    y estos viven en `data/cat/`. **Al propagar datos, usar `data/**/*.json`.**
    Siguen sin contener las zonas importadas después de mayo (snorkel 282 de 461, sunset 167 de
    219, yacht 129 de 153): decidir si esas 5 landings ES deben ampliar su alcance o no.

17. **Comprobación de la regla de oro, para repetir tras cada cambio de datos:** cada registro de
    `data/**/*.json`, `operators-slim.json` y `operators-top.json` debe coincidir con
    `operators.json` en lat, lng, price, cat, rating, reviews, name, zl y zone; y `slug-map.js`
    debe ser una biyección con el maestro, con página HTML para cada slug.
    Estado al 28 jul: 177 data files, ambos derivados y las 11.076 entradas del slug-map, en sincronía.

18. **Nunca recortes el NOMBRE del operador para que quepa la meta description.** Mi primer
    `fix_desc.py` acortaba el nombre y dejó 1.146 descripciones tipo *"South Beach Private… in
    Miami Beach"* — perdiendo justo "Kayak Tour", la palabra por la que se busca. Orden correcto:
    nombre y categoría primero, relleno al final, y se recorta el relleno. Google trunca la cola,
    así que lo importante debe ir delante. Ojo al medir longitud: hazlo sobre el texto **ya
    escapado**, porque `&quot;` y `&#x27;` cuentan como 6 caracteres.

19. **`numberOfItems` de un ItemList debe igualar el número de elementos que enumera**, no el
    total de la zona. 32 páginas declaraban el total (y 30 de ellas heredaban el 448 de Miami)
    mientras listaban 30 ítems. Además 38 tenían el `url` del ItemList apuntando a
    `/miami-activities`. Fuente: la plantilla ES de zona se clonó de Miami.

20. **Checklist al publicar un post de blog** (los 12 últimos se quedaron a medias en todo esto):
    enlazarlo en **`blog.html`** y en `sitemaps/blog.xml`; bloque `related-posts` con los posts
    hermanos de su destino; CTA a la **landing** concreta, no a `/?cat=X&zone=Y` (la home filtrada);
    y `BreadcrumbList` en JSON-LD. Faltaban breadcrumbs en 75 de 87 posts.

21. **El bloque `related-posts` se enlazaba a sí mismo en los 75 posts** que lo tenían. Al generar
    listas de "relacionados", excluir siempre la propia página.

22. **La zona `keywest` tiene DOS prefijos de slug**: `keys-activities` para la página de zona y
    `key-west-*` para las landings de categoría. Cualquier mapeo automático zona→slug falla aquí.

## Medición (revisado 28 jul)

- **Propiedad GA4 única: `G-CMH3XLRFH6`.** Había una segunda, `G-4KJ2DD0HB1`, en 2.889 páginas de
  operador: los datos estaban partidos entre dos propiedades. Unificadas todas a la primera.
- **Google Ads: `AW-16509204378`**, etiqueta de conversión `AW-16509204378/Od7PCNePlKAcEJrvmcA9`.
- El bloque de etiqueta canónico está en `miami-activities.html`: carga diferida de `gtag.js` al
  primer scroll/click, `config` de GA4 y de Ads, y un listener global que registra `conversion`
  en **cualquier** enlace a `fareharbor.com/embeds/book/`, leyendo el importe de `data-fh-price`.
- **Por eso todo `<a>` a FareHarbor debe llevar `data-fh-price="<precio>"`**; sin él la conversión
  llega a Ads con valor 0. Las 22 flagships de jet ski no lo tenían.
- Las flagships además disparan `lp_book` y `lp_book_pin` con `value` y `currency`. Ojo: en el
  código van dentro de una cadena JS con comillas escapadas (`\'lp_book\'`), así que un grep de
  `'lp_book'` NO los encuentra — a mí me hizo creer que faltaban.
- Estado: home, 101 zonas, 88 posts y las 22 flagships con etiqueta. **Siguen sin medir 215
  landings de categoría y 931 páginas de operador** — pendiente de decisión.

## Historial de la gran sesión (jul 2026) — para contexto

Corregido: 991 coords invertidas (Charleston/Hilton Head), 8.565 geo de páginas de operador,
4.511 meta descriptions genéricas→únicas, 228 títulos duplicados (diferenciados con ⭐rating),
142 etiquetas tras reclasificar tour→bike/jetski, JSON-LD de zonas (ItemList/FAQ/@id/geo),
hreflang roto en 64 landings, traducción completa de /es/, JS roto en 4 páginas ({{ }}),
550 rel-cards fantasma, slug-map corrupto (at119). Construido: 131 pares de landings bilingües,
176 OG, carga en 2 fases del home (86% menos primer render), 77 CTAs de blog.
