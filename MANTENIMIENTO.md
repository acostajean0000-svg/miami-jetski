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
- `data-fh-price` cubierto en 11.063 páginas de operador (29.363 enlaces), las 2 homes, 99 zonas,
  263 landings y los 88 posts. Antes lo tenían solo 53 landings y 88 zonas: **3.879 páginas de
  operador con Ads enviaban la conversión con valor 0**.
- En las 5 páginas de categoría global (snorkel-tours, yacht-charters, sunset-cruises,
  everglades-airboat-tours, miami-exotic-cars) las tarjetas enlazan a la **página interna** del
  operador y FareHarbor es solo fallback: ahí `data-fh-price` no aplica, la conversión se mide
  en la página de operador.

## Secuela del bug de slug-map (at119)

`swamp-cottage-rental-clyde-butchers-big-cypress-gallery-everglades` es la página huérfana
intencional. Cuando el slug de **at119** (Orlando ATV Polk City) apuntaba aquí, `fix_desc.py`
escribió en ella la ficha del ATV. Se arregló el slug-map pero **no la página**, que durante
semanas anunció "ATV adventure in Polk City, near Orlando. From $187" bajo el H1 "Swamp Cottage
Rental", con etiquetas de ATV, tarjetas de ATV de Central FL y `var ITEM = {item_id:'at119',
item_category:'atv', price:0}` en la analítica. Restaurada al producto real (Ochopee, Big Cypress,
$45, `clydebutcher/256631`).
**Lección: arreglar el índice no arregla las páginas que ya se generaron con el índice roto.**

Comprobación para detectar esta clase de daño: comparar el H1 de cada página con el sujeto de su
meta description. Al 28 jul, 0 páginas de operador discrepan (las 120 que salta el detector son
landings donde el H1 es una frase comercial — "Rent a Boat in Austin" — y es correcto).

## Enlazado interno de operadores: 11.076/11.076 (28 jul)

Hay **tres marcados distintos** de bloque "relacionados" en las páginas de operador, y cualquier
script que solo conozca uno deja fuera al resto:
1. `rel-grid` + `rel-card` con imagen (10.900 páginas) — el que gestiona el script de anillo.
2. Chips con estilos en línea, sin CSS propio (50 páginas de plantilla antigua).
3. 67 páginas que no tenían ningún bloque; se les añadió el formato de chips, porque **esa
   plantilla no carga el CSS de `rel-card`** y las tarjetas saldrían sin estilo.

Los 69 huérfanos finales se resolvieron insertando cada uno como tarjeta extra en un vecino de su
zona que sí tuviera `rel-grid`. Al hacerlo en bucle, varios huérfanos de una misma zona caen en el
mismo anfitrión: hay que deduplicar después (a mí me dejó 6 tarjetas repetidas en una página).

**`rosé-fireworks-sail-hiltonhead` (bt99) es el único slug con carácter no ASCII.** Funciona
—canonical, og:url, sitemap y sus 5 enlaces entrantes usan todos la forma con tilde, así que no hay
URL duplicada— pero cualquier regex `[a-z0-9-]+` lo pierde y lo cuenta como huérfano. No renombrar:
es una URL ya indexada y el beneficio sería marginal.

## `partners.html` — página de un socio, NO del sitio (28 jul)

Es la página co-marcada de **Jhon Doyle**: sus 16 enlaces internos llevan `?ref=jhondoyle` y su
enlace a FareHarbor va con `asn-ref=miamistylerentals&ref=jhondoyle`. Los `ref` son intencionados
y **no se tocan**. Lo que estaba mal era su alcance: aparecía en `sitemaps/static.xml`, era
indexable y se enlazaba como "Partners" desde el pie de `about.html` y desde `contact.html`, así
que el tráfico orgánico del sitio acababa acreditando comisión al socio.
Ahora: `noindex,follow`, fuera del sitemap y sin enlaces entrantes.
**Si algún día se crea una página real de reclutamiento de afiliados, que sea otra URL.**

## ⚠️ PARÁMETROS DUPLICADOS = COMISIÓN PERDIDA (29 jul)

Una reserva real (cliente Jesse Morones, Bruschi Boat Rental, $529,56) **no generó comisión**.
Soporte de FareHarbor identificó la causa: el enlace llevaba los parámetros de seguimiento
**repetidos literalmente**:

```
?flow=48216&asn=fhdn&asn-ref=X&asn-ref=X&ref=X&ref=X      ← ROTO, no atribuye
?asn=fhdn&asn-ref=X&ref=X&…                                ← correcto
```

**Llevar `asn-ref` Y `ref` a la vez es CORRECTO.** Lo que rompe la atribución es que cualquiera de
ellos aparezca **dos veces** en la misma URL.

Auditado el sitio a raíz de esto: **58 enlaces en 20 páginas** (todas de la tanda `*-fl.html`)
tenían los parámetros duplicados, porque el bloque de tracking se añadió dos veces al construirlas.
Cada reserva salida de esas páginas perdía la comisión. Corregidos deduplicando y conservando el
orden original; los 46.177 enlaces del sitio están ahora limpios.

### Calendario con fecha fija = cliente en un mes pasado

Otro fallo de la misma auditoría: **104 enlaces llevaban `/calendar/2026/05/`** (y 2 con `2026/04`)
incrustado en la ruta. En agosto de 2026 el cliente pulsaba "reservar" y aterrizaba en el calendario
de FareHarbor abierto en **mayo**, sin disponibilidad. 30 páginas y 34 registros del dato.
Eliminado el segmento: sin fecha, FareHarbor abre en el mes actual y no vuelve a caducar.
**Nunca fijes el mes en la URL.**

**Comprobación obligatoria antes de cada deploy:**
```python
ks=[k for k,_ in urllib.parse.parse_qsl(urlparse(u).query)]
assert len(ks)==len(set(ks)), 'parámetro duplicado: comisión perdida'
```
Excepción legítima: `partners.html` usa `ref=jhondoyle` (página del socio, ver más arriba).

## Parámetros de los enlaces de FareHarbor (42.221 enlaces)

Combinación estándar: `asn=fhdn&asn-ref=miamistylerentals&ref=miamistylerentals&bookable-only=yes&full-items=yes&marketplace=yes&flow=no`
Variantes legítimas encontradas:
- `asn=fhdn-mxn` (2.806), `fhdn-eur` (105), `fhdn-aud` (65) — variantes de divisa por operador.
- `branding=no` (668) y `flow=613885` (88) — flujos concretos, no tocar sin comprobar.
- 172 enlaces con solo `asn/asn-ref/ref` (les faltan `full-items`, `marketplace`, `flow`,
  `bookable-only`): pendiente de decidir si conviene homogeneizarlos.
El único `ref` distinto de `miamistylerentals` en todo el sitio es el del socio, en `partners.html`.

## Conteos: los cinco sitios del BODY (además de los seis del head)

Corregir el `<head>` no basta. En las páginas de zona el total propio aparece también en:
1. el pie `© 2026 … · N+ operators in X` (35 con conteo viejo, y **43 pies en inglés dentro de
   páginas ES**), 2. el encabezado `All operators in X (N)`, 3. el enlace de la guía
   `(N+ operators) →`, 4. el chip `id="mapCount"`, 5. las respuestas del FAQ.
Cuidado con el regex del pie: entre `©` y el conteo hay un `<a>`, así que `[^<]{0,80}` **no
coincide** — y si usas el mismo patrón para verificar, te dará un "limpio" falso. A mí me pasó.
Los conteos de otras zonas y de categorías en la misma página son legítimos: no los toques.

## Paridad de contenido EN↔ES (28 jul)

Ratio de palabras ES/EN: mediana 1,08 (el español ocupa algo más, es lo normal). 26 pares por
debajo de 0,70 merecen revisión; el caso extremo era **`es/daytona-activities` con 196 palabras
frente a 631 y cero preguntas frecuentes**: le faltaban la guía SEO, el FAQ y el bloque FAQPage.
Portados y traducidos (ratio 0,72). El resto de pares bajos son de plantilla distinta, no
traducciones incompletas — comprobar antes de "arreglar".

## Los enlaces internos de /es/ deben quedarse en /es/ (28 jul)

Las 182 páginas ES tenían **1.438 enlaces en el cuerpo apuntando a la versión inglesa** de páginas
que sí existen en español: el visitante hispanohablante salía del idioma al primer clic. Corregidos.
Al generar o tocar una página ES:
- Todo `href="/X"` del **body** debe ser `href="/es/X"` si existe `es/X.html`.
- **Excepción: el selector de idioma**, que se identifica por `hreflang="en"` o el emoji 🇺🇸.
  Son 137 y deben seguir apuntando a la raíz. Si los reescribes, el usuario no puede volver al inglés.
- Los `<link rel="alternate">` viven en el `<head>`: no tocar el head en esta operación.
- Comprobación inversa: 139 enlaces EN→`/es/` y todos son el selector 🇪🇸. Correcto.
- El blog solo existe en inglés y **ninguna página ES lo enlaza**: si algún día se traduce, habrá
  que añadir esos enlaces.

## ⚠️ El campo `price` NO es el precio del producto (hallazgo 28 jul)

**105 de los 130 data files de zona+categoría tienen UN ÚNICO precio para todos sus operadores**
(austin-boat: 235 operadores todos a $95; cabo-tour: 241 todos a $50). En los 11.076 registros del
maestro solo existen **47 precios distintos**, y `50` aparece 4.538 veces. Es decir: `price` es una
**estimación asignada por categoría**, no el precio real de cada producto.

Consecuencias que hay que tener presentes:
- El "desde $X" de cada landing es una estimación de categoría, no el mínimo real.
- Todas las tarjetas de una landing muestran el mismo precio.
- El `data-fh-price` que alimenta el valor de conversión de Google Ads lleva esa estimación.
- `lowPrice`/`offers` del JSON-LD declaran ese mismo número.
- Mi trabajo previo sobre "placeholders de $50" estaba alineando páginas con un número sintético:
  $50 no es el placeholder de unas importaciones, es el valor de la categoría `tour` entera.

**Para tener precios reales hay que traerlos de FareHarbor.** Hasta entonces, no interpretar las
diferencias de precio entre operadores de una misma categoría como información real.

### 64 precios reales recuperados de la home (28 jul)

La lista estática del pie de `index.html` conservaba los precios ORIGINALES: **87 valores distintos
en 156 operadores**, frente a los 11 del maestro para ese mismo grupo. Es anterior al aplanamiento
por categoría. Cruzando por el item de FareHarbor se recuperaron 64 precios que contradecían al
maestro, algunos de forma grave:

| operador | real | decía el maestro |
|---|---|---|
| Pretender Multi-Day Private Luxury Charter | $4.000 | $75 |
| 38' Top Shelf Private Coastal Day Yacht | $2.399 | $150 |
| 65 ALISA | $2.000 | $100 |
| Cowgirl 45' Premium Offshore Fishing | $1.050 | $150 |

Restaurados y propagados a los ocho sitios: 3 maestros, 119 registros en data files, 64 fichas de
operador (191 `data-fh-price`, 158 textos, 192 metas, 63 `Offer.price`), 176 tarjetas rel-card en
166 archivos y 32 landings (20 `lowPrice`, 18 `highPrice`, 86 textos, 20 respuestas de FAQ).

**Quedan ~11.000 operadores con la estimación de categoría.** Si aparece otra fuente con precios
reales (un export de FareHarbor, o HTML antiguo sin regenerar), cruzar por
`shortname/item-id` del enlace, que es la clave estable — no por nombre ni por slug.

## Bloque `lp-insights` de las landings (creado 28 jul)

250 landings (EN+ES) llevan una sección `class="lp-insights"` **generada desde su data file**, para
que cada página tenga contenido propio en vez de plantilla compartida:
- reparto real de operadores por área (`zl`), 2. los 5 mejor valorados con enlace a su ficha,
  rating y nº de reseñas, 3. total de reseñas y valoración media.

Efecto medido: palabras propias mediana 326 → 444; similitud entre hermanas (Jaccard de 5-gramas)
boat-rentals 0,52 → 0,38 (máx 0,70 → 0,50), jet-ski 0,47 → 0,38. Añade además ~1.250 enlaces
internos a fichas de operador.

**Reglas al regenerarlo:**
- **NO usa el campo `price`**, que es una estimación por categoría (ver sección anterior).
  Sí usa `reviews` (392 valores distintos, varía de verdad) y `rating` (8 niveles).
- Los enlaces a operador van **siempre a la raíz**, nunca a `/es/`: las fichas no tienen versión ES.
  Mi primer intento generó `/es/{slug}` y habrían sido 1.250 enlaces roots.
- Ancla de inserción: antes de la sección del FAQ; si no hay, antes de `</main>`; si no, antes de
  `<footer`. Buscar el FAQ **solo después de `</head>`**, porque "Preguntas frecuentes" aparece
  también en la meta description y el `find` te devuelve la posición del head.
- Guardarse de `str.find()` devolviendo −1: insertar en `h[:-1]` rompe el HTML. Verificar siempre
  que el archivo siga cerrando en `</html>`. A mí me pasó en la flagship de Miami.

## Auditar idioma: los CINCO escondites (barrido completo 28 jul)

Un detector que solo mire el texto visible deja pasar la mayoría. Hay que revisar los cinco:
1. **Texto visible** entre etiquetas.
2. **`alt` y `title`** de imágenes.
3. **`aria-label` y `placeholder`** — invisibles en pantalla pero es lo que **lee un lector de
   pantalla**: había 74 páginas ES con `aria-label="Show operators near me"`, `"Close booking"`,
   `"Clear"`, 21 con `"Quick booking bar"`, y un placeholder en spanglish
   (*"Buscar operadores **and** locations"*).
4. **Mensajes pre-rellenados de `wa.me`** (el texto que aparece escrito en WhatsApp del usuario).
5. **Cadenas dentro del JS**, y en particular **el HTML generado con `innerHTML`**: ahí vivían
   `'Book Now'` (82), `>Compare Operators<` (76), `"No favorites yet. Click ❤️ on any operator
   pin…"` (76) y `"Free cancellation · Instant booking"` (31). Un regex que excluya cadenas con
   `<>{}` para "evitar código" se salta justo este escondite — fue mi error en el primer barrido.

Cuidado al filtrar: los **nombres de producto de los operadores sí están en inglés** y no se
traducen ("Chassahowitzka River Clear Kayak Tour"). Estado final: 0 residuos salvo esos nombres.

## Idioma en el sentido inverso, y jerarquía de encabezados (28 jul)

Aplicando el método de los cinco escondites a las páginas **inglesas** buscando español:
- 315 coincidencias en texto visible y `alt` son **nombres de producto en español** de operadores
  de Cabo, Cancún y Tulum ("Tour de Puesta de Sol en Caborey"). Legítimos, no traducir.
- `CAT_KEYWORDS` de la home incluye a propósito términos en español (`moto de agua`, `lancha`)
  para que una búsqueda en español encuentre la categoría. **No tocar.**
- Un único fallo real: la home **inglesa** tenía el botón `Ver más (${remaining} restantes) ▼`.

Jerarquía de encabezados, ahora correcta en las 11.546 páginas:
- 57 páginas tenían un `<h2>` de subtítulo **antes** del `<h1>` (el banner superior va sobre el
  hero). Convertidos a `<p>` conservando sus estilos en línea: mismo aspecto, esquema correcto.
- 21 saltaban de `h1` a `h3` (el `h3` del widget de reserva, "📅 Check Availability & Book").
  Renivelados a `h2` **con los estilos del h3 en línea**, porque `h3{font-size:1.1rem;
  font-weight:800}` sí tiene regla propia y un cambio de etiqueta a secas habría alterado el diseño.

## Validez HTML y accesibilidad de controles (28 jul)

- **`id` duplicados: ninguno** en las 11.546 páginas. Ojo al comprobarlo: el patrón `\bid="` también
  coincide con `data-id="`, y esos SÍ pueden repetirse — me dio 4 falsos positivos. Usar
  `(?<=[\s"\'])id="`.
- **251 botones sin nombre accesible** (los ✕/× de cerrar modales, paneles y lightbox) en 127
  archivos: un lector de pantalla los anunciaba solo como "botón". Etiquetados con `aria-label`
  según el idioma de la página ("Close"/"Cerrar"). Incluye los botones generados dentro de
  plantillas JS, que también los necesitan; verificados los 1.444 scripts afectados sin errores.
- Inputs sin etiqueta: ninguno (todos tienen `placeholder` o `aria-label`).

## Ampliación de `data/cat/*.json` (28 jul) y el sexto escondite del idioma

Estado tras revisar el alcance declarado de cada página:
- `everglades-airboat-tours` (32/32) y `miami-exotic-cars` (27/27): **ya completas**.
- `snorkel-tours` decía "Florida, Hawaii **& Caribbean**" y le faltaban 84 de Puerto Rico, 5 de
  Cozumel y 2 de Nassau — todos caribeños, **dentro** de su alcance. Añadidos: 282 → 373.
  Regeneradas las pestañas de zona (había una de "Gulf Coast" con 0 operadores y varios conteos
  viejos), el precio mínimo ($65 → $55, real del dato), el `priceRange` del JSON-LD y las metas.
- `yacht-charters` y `sunset-cruises` dicen "Florida & Caribbean" y lo que les falta es Austin,
  Myrtle, Havasu y Lake Mead — **fuera** de ese alcance. No ampliadas: primero habría que decidir
  si esas páginas pasan a ser globales y reescribir su título y descripción.

**Sexto escondite del idioma: una frase en inglés con un nombre propio acentuado.**
Mi filtro descartaba como "español" cualquier texto con á/é/í/ó/ú/ñ. Eso ocultó frases como
*"Explore the reefs, wrecks and marine life of Hawaii, **Cancún**, Key West…"* — inglesa, en la
página ES. Al quitar los topónimos antes de aplicar el filtro aparecieron **105 fragmentos más** en
37 páginas ES: párrafos de guía completos y spanglish de plantilla
(*"La temporada alta en Newport Beach es May-Oct, with the most pleasant weather"*,
*"Los precios en the Florida Keys comienzan alrededor de $91 per person for most tours"*,
*"operadores verificados en Fort Lauderdale **and** Broward — luxury yacht charters"*).
Traducidos todos; 997 scripts ES verificados sin errores.

## Séptimo escondite: el CONTENIDO del JSON-LD (28 jul)

Validar que el JSON-LD *parsea* no dice nada de lo que declara. Al revisar el texto de cada campo:
- **226 campos en inglés dentro de páginas ES** (`description`, `@graph/description`,
  `mainEntity/acceptedAnswer/text`, `mainEntity/name`). Es lo que Google lee para los resultados
  enriquecidos, así que un usuario buscando en español veía el fragmento en inglés.
- **20 páginas ES declaraban un FAQPage entero sobre Miami** — Bar Harbor, Seattle, Park City,
  Lake Tahoe… con preguntas como *"What are the best things to do in Miami on the water?"*.
  Tenían DOS bloques: el correcto en español y este heredado de la plantilla de Miami. Eliminado
  el de Miami en las 20.
- **20 FAQPage vacíos** (`mainEntity: []`) en páginas EN: ruido inútil, eliminados.
- **22 páginas con dos FAQPage, ambos con preguntas válidas y distintas.** Google pide uno por
  página. **Fusionados** en lugar de borrar: la home pasa de 5+6 a 11 preguntas,
  northeast-florida de 2+6 a 8. Deduplicadas 6 preguntas repetidas (una la introduje yo al
  añadir el FAQ de Daytona).

Regla: **un solo FAQPage por página, sin `mainEntity` vacío, y en el idioma de la página.**

## Semántica del JSON-LD, no solo que parsee (28 jul)

Que un bloque parsee no dice nada de si Google lo entiende. Revisando tipos, propiedades y valores:

**Tipos y propiedades corrompidos por la traducción — todo en `es/index.html`:**
`"@type":"ListaItem"` ×61, `"BreadcrumbLista"`, `"ItemLista"` y la propiedad
`"itemListaElement"` ×2. Con el tipo Y la propiedad inválidos, **la ItemList de 60 operadores y
los breadcrumbs de la home española eran completamente invisibles para Google.** Es el mismo
daño que `classList`→`classLista`: al traducir, la lista negra debe incluir los tipos y
propiedades de schema.org, no solo los identificadores de JavaScript.

**Valores que no cuadraban con el dato** (lo que Google compara con la página):
- 66 `Offer.price`, 7 `reviewCount` y 2 `ratingValue` en páginas de operador. **Causa: mis propias
  correcciones de precio de esta sesión llegaron al data file y al texto visible, pero no al
  JSON-LD.** El JSON-LD es el séptimo sitio donde vive un precio.
- 154 `offerCount`, 116 `lowPrice` y 140 `highPrice` en `AggregateOffer` de landings; varios
  llevaban el total de la zona en lugar del de su categoría (bar-harbor-bike-rentals declaraba
  124, el total de Bar Harbor, en vez de sus 23 bicicletas).

Comprobación a repetir tras cualquier cambio de datos o precios:
recorrer los nodos y verificar `Offer.price`, `AggregateRating.ratingValue`/`reviewCount` contra
`operators.json`, y `AggregateOffer.lowPrice`/`highPrice`/`offerCount` contra el data file de la
página. Estado: 24.050 bloques, 0 rotos, 0 problemas semánticos.

## La propiedad `image` del JSON-LD es el OCTAVO sitio donde vive una imagen

Al arreglar las fotos genéricas actualicé `og:image` y `twitter:image`, pero **no la propiedad
`image` del JSON-LD**, que es la que Google usa para los resultados enriquecidos. Resultado:
1.352 páginas seguían declarando una foto de stock de Unsplash. Corregidas, más:
- 210 landings cuyo `image` era el logo genérico `/og-image.png` teniendo su OG propia en `/og/`.
- 81 páginas de operador con **dos fotos válidas distintas** en `image` y `og:image`; alineadas
  con la del maestro.

También sincronizados: 121 nodos sin `inLanguage` (ahora `es-ES`/`en-US` según la página),
37 `PostalAddress` sin `addressLocality`, 4 `GeoCoordinates` que no coincidían con `operators.json`.

**Los ocho sitios donde vive el mismo dato** (comprobar los ocho tras cualquier cambio):
data file · maestros (operators/slim/top) · texto visible · meta description · og · twitter ·
JSON-LD (`Offer.price`, `AggregateRating`, `AggregateOffer`, `image`, `geo`) · `data-fh-price`.

## Camino de reserva en la ficha de operador (unificado 29 jul)

Cada ficha tenía hasta **cinco mecanismos de reserva** compitiendo, y de forma desigual entre
páginas. Estado anterior: 4.760 fichas con DOS barras fijas solapadas en móvil, 3.891 sin ninguna,
67 solo con la de JavaScript. Ahora **las 11.076 tienen exactamente una**.

**Mecanismos que se conservan, en este orden de prioridad:**
1. `fh-widget` — iframe de FareHarbor con el calendario. Es la reserva de verdad (10.998 fichas).
2. `fh-fallback` — "Calendar not loading?" con enlace directo. Red de seguridad, ocupa poco.
3. `book-card` en el lateral (escritorio) y `mobile-book-bar` fija abajo (móvil).
4. `fh-modal` — solo donde ya existía; abre FareHarbor en capa sin salir de la página.

**Eliminado:** el `<script>` que creaba una segunda barra `mob-cta` por JavaScript. Duplicaba la
barra estática, la tapaba (z-index 99000 sobre 200), dependía de JS y **generaba el botón sin
`data-fh-price`**, así que esas conversiones llegaban a Google Ads con valor 0.

**La barra que se conserva es la estática** porque funciona sin JavaScript, lleva el precio y el
`data-fh-price` correcto. Si hay que regenerarla, el marcado es:
`<div class="mobile-book-bar">` + precio + `<a data-fh-price data-fh-name href={link FH} class="btn-book">`.
Verificado: 11.076 con una sola barra, precio coincidente con `operators.json`, 0 sin enlace.

### El modal, ahora en las 11.074 fichas con reserva FareHarbor (29 jul)

Antes solo lo tenían 6.254; en las otras 4.822 los botones abrían FareHarbor en pestaña nueva y
**no se disparaba el evento `book_now_click`**, así que ese clic no se medía.

Cómo funciona: un listener en `document` (fase de captura) intercepta **cualquier**
`a[href*="fareharbor.com/embeds/book/"]` de la página, hace `preventDefault` y abre el iframe en
capa. Por eso unifica de golpe el CTA del hero, la tarjeta lateral, la barra móvil y el enlace de
respaldo. Respeta cmd/ctrl/shift para abrir en pestaña nueva, cierra con Escape o clic fuera, y
tiene detección de "catálogo vacío" que muestra un aviso si el operador ya no tiene items.

**Piezas necesarias — las tres o no funciona:**
1. HTML: `<div class="fh-modal" id="fhModal">` con los ids `fhModalIframe`, `fhModalLoading`,
   `fhModalTitle` y `fhUnavailable`.
2. JS: la IIFE con `openFhModal` / `window.closeFhModal`.
3. CSS: las 14 reglas `.fh-modal*` + `@keyframes fhspin`. Están en `operator.css`, **pero 105
   fichas no lo cargan** y llevan su CSS en línea: a esas hay que inyectarles también las reglas.

Excepciones legítimas: `miami-bloom-bar-flowers` y `xtreme-car-rental-punta-cana` reservan por
WhatsApp y no tienen ancla a FareHarbor, así que no llevan modal.

## JavaScript común de las páginas de zona en archivo externo (29 jul)

Las 90 páginas de zona llevaban ~50 KB de JS **idéntico** cada una (bloques "SPRINT 11-15", mapa,
buscador). Extraído a dos archivos cacheados:

| archivo | KB | páginas |
|---|---|---|
| `/js/zone-en.<hash>.js` | 50,7 | 45 |
| `/js/zone-es.<hash>.js` | 47,8 | 42 |

Peso mediano de una página de zona: **138 KB → 80 KB (-42%)**; 5,6 MB menos de HTML en el sitio.
En la segunda visita el archivo ya está en caché y no se descarga.

**Reglas para no romperlo:**
- Los bloques comunes van **seguidos al final** de la secuencia de scripts, después del bloque
  propio de cada zona (`ZONE_KEY`, `ZONE_NAME`). El `<script src>` va **en esa misma posición y
  sin `async`/`defer`**: son IIFE que dependen del orden de ejecución.
- El bundle debe ser **byte a byte** la concatenación de lo que había en línea. Comprobarlo antes
  de desplegar; así el comportamiento es idéntico por construcción.
- **El nombre lleva el hash del contenido** porque la cabecera es `immutable` con un año. Si
  editas el bundle, hay que regenerar el hash y actualizar las 45/42 referencias, o los
  navegadores nunca verán el cambio.
- Regla en `vercel.json`: `/js/(.*)` → `max-age=31536000, immutable`.

**3 páginas siguen en línea** (`es/keys`, `es/jacksonville`, `es/daytona`) porque su secuencia de
scripts difiere: jacksonville y daytona vienen de la plantilla de **operador** (llevan
`openFhModal` y un bloque `BASE MAP jacksonville` — ojo, daytona también lo lleva con ese nombre).

De paso, cadenas en inglés encontradas en el JS español: `🔍 No matches`, `Compare →`, `Clear`,
`No results` en el bundle (42 páginas) y 8 más en `es/keys-activities`. Un barrido que exija dos
palabras inglesas no las ve: son de una sola palabra.

## Auditoría de cierre (29 jul) — qué comprobar y qué NO son errores

**Estado: 11.546 páginas sin un solo problema** de estructura, head, JSON-LD, recursos, datos,
enlaces internos ni ruta de reserva. 6.812 scripts únicos (39.815 instancias) sin errores.

**Cómo verificar la sintaxis JS de todo el sitio en segundos**: deduplicar por hash MD5 y validar
los únicos con `new vm.Script(code)` en UN proceso de node. Lanzar `node --check` por script
(39.815 procesos) no termina nunca.

**Falsos positivos recurrentes — comprobarlos antes de "arreglar":**
- `/_vercel/insights/script.js` "no existe": está dentro de un comentario HTML y además lo sirve
  Vercel en runtime.
- Una landing de categoría contiene DOS conteos correctos: el suyo en las metas y el de su zona
  dentro del nodo `TouristDestination`. Excluir el JSON-LD al comparar contra el data file.
- `twitter:description` distinta de `og:description` suele ser solo una variante más larga.
- Los nombres de producto de operadores están en inglés en páginas ES (y en español en páginas EN)
  y **no se traducen**.

**Fugas encontradas y corregidas en esta auditoría** (todas ya publicadas como limpias antes):
- 89 páginas ES con `Instant online booking with free cancellation.` en el JSON-LD.
- 74 con `✓ Verified FareHarbor operators` y `⚡ Instant booking` en `innerHTML`.
- 76 con las plantillas `N verified activity operators in`, `Compare and book N+ verified
  watersports operators`, `Marketplace of N+ watersports operators`, `Watersports Marketplace —`.
- 4 cadenas en el bundle `zone-es.js` (afectaban a 42 páginas) y 8 en `es/keys-activities`.
- **14 páginas con la fuga de Naples en `twitter:description`**: *"Compara 388+ verified operators
  on Austin y Lake Travis, Texas — Austin, Austin, **Sanibel, Fort Myers**. Pontoon rentals..."*
  en Austin, Havasu, Lake Mead, Ozarks, Myrtle y Nassau. Corregido igualando a `og:description`.
- `yacht-charters` declaraba 130 con 129 en el dato (quedó de eliminar un registro huérfano).

**Lección:** cada barrido de idioma que hice dio "cero residuos" y el siguiente, con el umbral o el
filtro ajustado, encontró más. Un detector que exige 2 palabras inglesas no ve `Loading…`; uno que
descarta textos con tilde no ve una frase inglesa que mencione *Cancún*.

## Historial de la gran sesión (jul 2026) — para contexto

Corregido: 991 coords invertidas (Charleston/Hilton Head), 8.565 geo de páginas de operador,
4.511 meta descriptions genéricas→únicas, 228 títulos duplicados (diferenciados con ⭐rating),
142 etiquetas tras reclasificar tour→bike/jetski, JSON-LD de zonas (ItemList/FAQ/@id/geo),
hreflang roto en 64 landings, traducción completa de /es/, JS roto en 4 páginas ({{ }}),
550 rel-cards fantasma, slug-map corrupto (at119). Construido: 131 pares de landings bilingües,
176 OG, carga en 2 fases del home (86% menos primer render), 77 CTAs de blog.

---

## ⚠️ CONVERSIONES DE GOOGLE ADS — las tres formas de perderlas

Auditoría de ago 2026. El 65% del sitio no reportaba conversiones a Ads. Tres causas
independientes, y hay que comprobar las tres por separado:

**1. El evento sin `send_to`.** `gtag('event','conversion',{value,currency})` sin `send_to`
NO llega a Google Ads. Se queda en GA4 como un evento suelto llamado "conversion".
La llamada correcta lleva siempre la etiqueta:

    gtag('event','conversion',{send_to:'AW-16509204378/Od7PCNePlKAcEJrvmcA9',
                               value:parseFloat(p)||0,currency:'USD'});

**2. El `config` que falta.** Aunque el evento lleve `send_to`, si la página nunca ejecuta
`gtag('config','AW-16509204378')` no hay destino configurado. El bloque bueno lleva DOS
config seguidos (GA4 y Ads) y el loader pide `?id=AW-16509204378`, no el de GA4.

**3. `window.gtag` inexistente.** 1.146 páginas no cargaban gtag.js. Como el código va
protegido con `if(window.gtag)`, no falla: **se salta en silencio**. No hay error en consola,
no hay nada que ver. Solo se detecta contando páginas sin `G-CMH3XLRFH6`.

### Comprobación de despliegue

    páginas con G-CMH3XLRFH6                       == total
    páginas con gtag('config','AW-16509204378')    == total   (y nunca >1 por página)
    eventos 'conversion' sin send_to               == 0

## ⚠️ APÓSTROFOS EN `onclick` — el fallo que ningún linter ve

`onclick="trackBookNow('Focused Mahi Sailfish on 33' Stuart Angler','79','boat')"` es un
**error de sintaxis**: el handler no compila, no se registra la conversión, y el enlace sigue
funcionando — así que parece que todo va bien. 320 páginas lo tenían.

Dos orígenes distintos, y el segundo se me escapó en la primera pasada:

- **Apóstrofo sin escapar** en el JS: marcas de pies (`33'`, `63'`), posesivos
  ("St. Augustine's", "World's"). Rompe la cadena JS.
- **Comilla doble sin escapar** en el atributo HTML: `6'0" Libtech`, `"Sandy" • Captain
  Included`. El JS es válido pero el navegador **cierra el atributo** en la comilla.
  Un test que solo parsee el JS da estas por buenas. Hay que mirar además el HTML crudo.

`node --check` NO sirve aquí (el handler no es un fichero JS). La prueba autoritativa es
extraer cada `onclick`, deshacer las entidades y pasarlo por `new Function(code)`.

**Al reconstruir un `onclick`, reconstruye el atributo entero** desde `operators.json`
(clave estable `shortname/itemid` sacada del `href`). No parchees con regex: un patrón
`trackBookNow\(.*?\)` se corta en el paréntesis de nombres como "(Walk Up)" y deja basura
detrás — así pasé de 320 rotos a 904 y tuve que restaurar de copia.

El escapador debe hacer las dos cosas, en este orden: primero JS (`\` y `'`), luego HTML
(`&`, `<`, `>`, `"`). La función `esc()` de las portadas escapa `& < > "` pero **no el
apóstrofo**, así que no vale para meter texto dentro de una cadena JS.

## Valor y categoría de la conversión

- `value` iba a **0 en el 30,6%** de las llamadas. Un 0 le enseña a Smart Bidding que ese
  clic no vale nada. Se recupera de `operators.json` cruzando por `shortname/itemid`.
- `boat` funcionaba como **categoría por defecto**: 62% de las llamadas. Tras corregir,
  22% y 31 categorías reales. Un "Four Day Bike Rentals" declarado como `boat` contamina
  cualquier segmentación por tipo de actividad.
- Recuerda que `price` sigue siendo una **constante por categoría** salvo en 64 casos. El
  valor enviado es un proxy, no el precio real, hasta que se cargue el export de FareHarbor.

## Falsos positivos recurrentes al auditar (no los persigas)

- `\bid="..."` captura también `data-id="..."` — el guion cuenta como límite de palabra.
- `t.count('<head')` cuenta `<header`. Y en index.html hay un `<head>` dentro de un comentario.
- `expand` invocado como `.map(expand)` no lo ve un patrón `expand\s*\(`.
- Nombres de producto dentro de strings: `trackBookNow('Tour (Private)'...)` parece una
  llamada a una función `Tour(`.
- `/_vercel/insights/script.js` no existe en el repo: lo sirve Vercel en runtime.
- `href="/'+slug+'"` dentro de JS parece un enlace interno roto.
- `bookUrl` en `boat-rentals-florida.html` es una **variable local**, no la función global.

---

## ⚠️ EL LISTENER EN CAPTURA QUE SE TRAGABA TODAS LAS CONVERSIONES

El fallo más caro encontrado, y sólo aparece **ejecutando la página**, nunca leyéndola.

En 11.139 páginas el listener del modal de FareHarbor está registrado así:

    document.addEventListener('click', function(e){ ... e.preventDefault(); e.stopPropagation(); ... }, true);
                                                                                                        ^^^^ captura

Al ser **fase de captura sobre `document`**, corre *antes* de que el evento llegue al `<a>`.
El `stopPropagation()` detiene ahí el evento, así que el `onclick="trackBookNow(...)"` del
propio botón **nunca se ejecuta**. El modal abre, el cliente reserva, la comisión entra —
y Google Ads no se entera de nada.

Lección: `stopPropagation()` en captura **cancela a los handlers del propio destino**, no
sólo a los ancestros. Si un handler global intercepta el clic, la analítica tiene que
dispararse *dentro de ese handler*, no en el elemento.

La corrección dispara la conversión dentro del propio handler, justo antes de abrir el modal,
tomando el precio de `data-fh-price` y la categoría del `onclick` ya corregido.

## Los cuatro caminos de conversión (no dupliques)

Tras la auditoría hay exactamente un mecanismo por página. Antes de tocar nada, mira cuál usa:

| Mecanismo | Páginas | Cómo dispara |
|---|---|---|
| Handler global en captura | 231 | Lee `data-fh-price` de cualquier enlace FH. **Ya lo cubre todo** |
| Handler del modal | 11.139 | Llama a `trackBookNow` antes de `openFhModal` |
| `onclick` en el botón | mayoría de páginas de operador | Sólo si nada intercepta el clic |
| Listener delegado inyectado | 221 | Para páginas sin ninguno de los anteriores |

**Regla: si la página ya tiene el handler global en captura, NO añadas nada más** — se cuenta
dos veces. Me pasó en 22 landings de jet ski y en las 88 del blog, y sólo lo vi simulando el
clic y contando cuántos eventos `conversion` salían. Un clic = exactamente una conversión.

## El evento `lp_book` no es una conversión

231 landings disparaban `gtag('event','lp_book',{op,value,currency})`. Nombre propio, sin
`send_to`: **Google Ads no lo reconoce**. Sirve para GA4, no para pujar. Ahora esas páginas
disparan además la conversión real.

## ⚠️ La portada /es no expandía los enlaces

`es/index.html` renderizaba `href="miamiaquatours/221278"` — URL **relativa**. Cada clic iba
a `/es/miamiaquatours/221278` → 404. Los 20 botones y las 20 imágenes de la portada española
estaban rotos. Causa: la home inglesa define `window._expandOp` (con `_OP_LINK_A/B/C` y
`_OP_PH_A/B`) y lo aplica en `_applyLoadedData`; la española nunca recibió ese bloque.
Recuerda que `operators-top.json` trae 1.111 de 1.114 enlaces en formato corto.

**Comprobación:** tras cargar la home, ningún `a[data-fh-price]` debe tener un `href` que no
empiece por `https://fareharbor.com/`, y ninguna `img` de tarjeta un `src` relativo.

## Banco de pruebas en jsdom (lo único que ve los fallos de ejecución)

`node run.js` carga páginas reales con jsdom, intercepta `fetch` sirviendo los JSON del disco,
simula un clic en el primer enlace de FareHarbor y comprueba:

- que no haya errores de ejecución (con polyfills de `matchMedia`, `IntersectionObserver` y Leaflet)
- que el clic dispare **una** conversión, con `send_to` correcto y valor > 0
- que el botón apunte de verdad a `fareharbor.com`
- que el contenedor de tarjetas no quede vacío tras cargar los datos

Sin esto no se detecta ninguno de los fallos de esta sección: todos se leen perfectamente
bien en el HTML.

---

## ⚠️ MAPAS DE SLUGS DE ZONA — seis páginas clonadas sin cambiar el mapa

`austin-activities`, `myrtle-beach-activities`, `lake-havasu-activities`,
`lake-of-the-ozarks-activities`, `lake-mead-activities` y `nassau-activities` cargaban
**`/slug-map/naples.js`**: se clonaron de la página de Naples y sólo se actualizó el
`fetch(data/...)`, no el `<script src>` del mapa.

Consecuencia: sin entrada en el mapa, el código genera el slug a partir del nombre y la zona,
produciendo rutas como `/afternoon-charter-miss-b-haven-westfl` cuando la ficha real es
`afternoon-charter-miss-b-haven-destin`. **587 tarjetas llevaban a un 404** — en Austin,
las 388 de la página.

Los seis mapas ni siquiera existían. Se generan desde el maestro filtrando por los ids del
fichero de datos de la zona:

    slug-map/<zona>.js  =  { id: MASTER[id] }  para cada id en data/<datos>.json

**Regla al clonar una página de zona: hay que cambiar TRES cosas** — el `fetch(data/X.json)`,
el `<script src="/slug-map/X.js">` y el mapa debe existir y cubrir todos los ids de X.

### Comprobación (estática, sin navegador)

Para cada página que cargue un mapa: todo id de su fichero de datos debe estar en el mapa, y
todo slug del mapa debe existir como `.html`. Hoy: 132 páginas, 14.938 entradas, 0 huecos.

Además había 344 operadores de `westfl` y algunos de `hawaii`, `keywest` y `puntacana`
ausentes de su mapa, y 12 slugs que apuntaban a páginas inexistentes.

## Cargar los `<script src>` locales al auditar con jsdom

jsdom **no descarga** los scripts locales, así que `window._OP_SLUG_MAP` nunca existe y toda
página de zona parece tener miles de enlaces rotos. Sin insertarlos me salían 1.860 destinos
inexistentes; insertándolos, 362 (los reales); tras arreglarlos, 0.

Antes de parsear hay que sustituir cada `<script src="/x.js"></script>` por su contenido.
Y al comparar rutas con el disco, **decodifica antes**: hay una ficha con tilde
(`rosé-fireworks-sail-hiltonhead.html`) que aparece como `%C3%A9` y parece rota sin serlo.

## Lo que sí quedó verificado ejecutando

- El iframe del modal carga la URL correcta de FareHarbor: mismo item, atribución intacta,
  sin parámetros duplicados y sin calendario fijo (119/120 páginas; la restante no tiene
  enlaces FH porque es un directorio que enlaza a fichas).
- 26.550 enlaces internos generados en runtime: 0 rotos.
- Las páginas tipo directorio (`san-diego-activities` y similares) no llevan botón de reserva
  a propósito: la tarjeta va a la ficha del operador y allí se reserva. No es un fallo.

---

## ⚠️ REDIRECTS QUE TAPAN PÁGINAS EXISTENTES

**En Vercel los `redirects` se evalúan ANTES del sistema de ficheros; los `rewrites`, DESPUÉS.**
De ahí se sigue todo lo demás:

- Un **redirect** cuyo `source` coincide con una página existente **gana**: la página queda
  inalcanzable aunque el `.html` esté ahí.
- Un **rewrite** cuyo `source` coincide con una página existente es inofensivo: gana el fichero.

Había **64 redirects tapando fichas de operador reales**. Las 64 tenían widget de reserva y
estaban en el sitemap; 56 eran `permanent: true`. Google las rastreaba, recibía un 301 y las
desindexaba cediendo autoridad a `/naples-activities` — que además era la zona equivocada
(eran de Tampa y Destin). Restos de una limpieza de 404 anterior a que esas fichas existieran.

**Regla: al generar páginas nuevas, comprueba que ningún redirect tenga ese slug como
`source`.** Un redirect a una zona genérica es el patrón típico de limpieza de 404 y hay que
retirarlo en cuanto la ficha exista.

## Rewrites huérfanos: `gulf-activities` nunca existió

40 rewrites apuntaban a `/gulf-activities`, una página que no existe — incluidos comodines
`(.*)-destin`, `(.*)-tampa`, `(.*)-naples`, `(.*)-sarasota`, `(.*)-pensacola`, `(.*)-westfl`.
Efecto: `/destin-activities`, `/tampa-activities` y `/fort-myers-activities` devolvían 404, y
cualquier ruta inexistente terminada en `-tampa` servía una página rota en vez del 404 propio.
Reapuntados a `/west-florida-activities`, que cubre esa costa con 1.630 operadores.

### Comprobación de despliegue del enrutado

    ningún redirect.source coincide con una página existente
    todo redirect.destination y rewrite.destination existe como .html
    0 bucles, 0 sources duplicados, 0 cadenas

## Lo que estaba bien (no lo toques)

- **Canónicas**: 11.546 páginas, 0 ausentes, 0 duplicadas, 0 relativas, 0 apuntando a un 404.
  Las 4 de Cozumel que apuntan a otra URL lo hacen **a propósito**: existen las variantes
  `-cancun` y `-cozumel` del mismo producto y la canónica consolida hacia una. Por eso el
  sitemap las excluye. No es un fallo.
- **hreflang**: 366 páginas, 0 destinos rotos, 0 idiomas duplicados, 0 sin `x-default`,
  reciprocidad completa. Ojo: **no todo lo que está fuera de `/es/` es inglés** —
  `xtreme-car-rental-punta-cana` es español en la raíz y su par inglés es `...-en`.
  Una comprobación que asuma "raíz = inglés" da un falso positivo aquí.
- **Sitemap**: `sitemap.xml` es un **índice** de 48 sitemaps hijos en `/sitemaps/`, no una
  lista de URLs. Suman 11.538 URLs únicas para 11.546 páginas. Excluye correctamente
  `404`, `offline`, `partners`, los índices servidos por otra ruta y las 4 canonicalizadas.
  Quedan 80 URLs repetidas entre sitemaps de zonas solapadas (Cancún/Playa del Carmen/Tulum/
  Isla Mujeres): Google lo tolera, es cosmético.

## filepicker.io es el dominio MUERTO-EN-VIDA de Filestack

898 URLs en 287 páginas usaban `www.filepicker.io/api/file/HANDLE` — el dominio antiguo de
Filestack. Hoy aún resuelve, pero es legacy sin garantía. El handle es el mismo en ambos:

    https://www.filepicker.io/api/file/HANDLE[/convert?...]  →  https://cdn.filestackcontent.com/HANDLE[/convert?...]

Migradas las 898 (sustitución de prefijo, mismos parámetros de convert). Verificado cargando
12 handles aleatorios en el CDN nuevo: 12/12 OK.

Quedan 5 og:image en dominios de operadores ajenos (rippleeffectecotours, wsimg, floridawatertour,
civitatis, luxepartyshop). Hoy cargan las 5 (verificado en navegador), pero dependen de sitios que
no controlamos: si un operador rediseña su web, su og:image muere sin aviso. Candidatas a re-hostear.

## El modal decía "catálogo vacío" al primer clic (y funcionaba al segundo)

`openFhModal` pone el iframe en `about:blank`, luego asigna la URL de FareHarbor. El `onload`
de `about:blank` se dispara cuando `src` ya es la URL real, pasa el filtro y arranca un timer de
3,5 s que lee `iframe.contentDocument.body.innerText`. Si FareHarbor aún no cargó (primer clic,
sin caché), lo que lee es **todavía el documento about:blank**: 0 caracteres → `showUnavailable()`.
Al segundo clic FareHarbor carga en <3,5 s, el documento ya es cross-origin (inaccesible) y no salta.

Esa detección **nunca** puede ver un catálogo vacío real: FareHarbor siempre es cross-origin. Solo
produce falsos positivos. Guarda añadida: si `contentDocument` es accesible y su `location` es
`about:blank`, no evaluar. 11.089 páginas; las 50 restantes usan una variante sin detección.

## ⚠️ MODAL v3 — determinista, sin temporizadores de "vacío"

Tras desplegar la guarda anterior el usuario reportó que iba PEOR (hasta 4 clics). Al reproducirlo
en vivo aparecieron dos cosas que el HTML no mostraba:

1. **La CSP bloqueaba `analytics.google.com`, `stats.g.doubleclick.net` y `ad.doubleclick.net`**
   (`connect-src` solo permitía `*.google-analytics.com`, el dominio antiguo). Todas las
   conversiones reparadas en esta sesión morían en el navegador con "Refused to connect".
   Nunca hubo error visible: la consola no la mira nadie. Añadidos a la CSP.
2. `index.html` ya tenía escrito *"la auto-detección de iframe vacío se removió — daba falsos
   positivos"*. Esa corrección se hizo una vez, en la portada, y nunca se propagó a las otras
   11.138 páginas con modal. **Cuando arregles algo en la portada, búscalo en el resto.**

Nueva `openFhModal` (una sola variante para las 11.139 páginas, antes había 8):
- `iframe.src=url` directo. Sin `about:blank` previo ni `requestAnimationFrame` (que no se
  ejecuta con la pestaña oculta y creaba la carrera de `onload`).
- `onload` solo oculta el spinner si `src` es la URL pedida.
- Sin detección de "catálogo vacío": FareHarbor es cross-origin, es físicamente imposible.
- A los 12 s sin `onload`: panel "está tardando → abrir en pestaña nueva" con **la misma URL**
  (atribución intacta). Antes mandaba a `/` con "Browse similar operators" — el cliente se
  perdía y la comisión también.

Queda el banner gris "Don't see availability? Browse similar operators" (11.205 páginas), que
sigue enlazando a `/`. Es una fuga de conversión manual; candidato a apuntar a la misma URL.
