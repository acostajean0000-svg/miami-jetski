# Qué aprovechar técnicamente de GetYourGuide y Viator
**Fecha:** 30 ago 2026 · Inspección real del DOM de GYG (destino + ficha) y Viator (destino). Comparado contra miamijetskiboatrentals.com medido.

---

## Comparativa medida

| Señal | GetYourGuide | Viator | Tu sitio (hoy) |
|---|---|---|---|
| JSON-LD ficha | `["Product","TouristTrip"]` + `sku` + `brand` + `AggregateRating` + **10 `Review` con texto** + `AggregateOffer.lowPrice` | similar | `TouristAttraction` + `Offer` + `AggregateRating`. **0 de 10.916 fichas con `Review`**. Sin `Product` en fichas |
| JSON-LD destino | `Organization` + `BreadcrumbList` + `FAQPage` + `ItemList` | FAQ "People Also Ask" | `ItemList` + `FAQPage` + `BreadcrumbList` + `TouristDestination` + `LocalBusiness` ✅ (más rico que ellos) |
| Título ficha | `Nombre - 2026 (Verified Reviews)` 83 chars | — | `Nombre · Zona · Book Now` — 2.129 >65 chars |
| Título destino | `The BEST Marrakesh Tours … 2026 - FREE Cancellation` | `What are THE BEST 20 Tours & Excursions in Miami?` (pregunta) | `Austin Tours & Activities — 388+ Operators (2026)` ✅ |
| hreflang | 45 locales | ~10 | 2 (en/es) — suficiente para tu mercado |
| Imágenes | 189/pág, 154 `srcset`, AVIF, `fetchpriority=high` en hero, 181 lazy | similar | 1–4 por página, `srcset` en 10.678 fichas ✅, webp, hero con fetchpriority ✅ |
| Peso HTML | **1,5–1,7 MB** | 1,5 MB | **20–88 KB** ✅ (ventaja enorme) |
| Señales de urgencia | "Likely to sell out", "Booked 158 times", "Reserve now & pay later" | "Likely to Sell Out", "Best Seller", "Special Offer", "Free Cancellation" en cada tarjeta | "Free cancellation / Instant confirmation" genéricos. **Nada por operador** |
| Reseñas visibles | 10 reseñas con autor y fecha en la ficha | Bloque "What are people saying" con reseñas recientes por producto | Solo el número (⭐ 4.8 · 187 reseñas) |
| Páginas de POI | Sí (`/marrakesh-l208/` + sights) | Sí: `/Miami-attractions/South-Beach/d662-a1220` con "from $11" | **No existen**: no hay página para "South Beach", "Biscayne Bay", "Lake Travis" |
| Paginación de listados | Scroll | `/Miami/d662-ttd/2` … `/43` (URLs reales) | Todo en una página vía JS (Google solo ve lo baked) |
| Filtros | Por fecha, precio, categoría; estado en URL | Igual | Cliente-side, sin URL |
| CTA | "Check availability" sticky | "Check Availability" | "Book Now" ✅ modal |

---

## 🟢 Aprovechable ya — datos que YA tienes y no usas

### 1. Badges de urgencia reales desde el export de FareHarbor
Tus CSV `marketplace-top-items-2026-06-28*.csv` traen por item: `availability_next_week`,
`availability_next_30days`, `quality_score`, `image_count`, `tags`. Eso permite, sin inventar nada:
- **"Available this week"** si `availability_next_week > 0`
- **"Limited availability"** si `availability_next_week ≤ 3` (el "Likely to sell out" de GYG)
- **"Top rated operator"** si `quality_score ≥ 90`
- Ordenar las tarjetas por `quality_score` en vez de por reseñas
GYG y Viator ponen estas señales en **cada tarjeta**, no solo en la ficha. Es lo que más
diferencia una tarjeta suya de una tuya. Requiere refrescar el export periódicamente
(mensual basta para "top rated"; semanal para disponibilidad).

### 2. `Product` + `sku` en las fichas de operador
Tus fichas usan `TouristAttraction`. GYG usa `["Product","TouristTrip"]` con `sku` = item id.
`Product` es lo que habilita el **rich result de precio + rating** en Google. Ya tienes `price`,
`rating`, `reviews` y el `shortname/itemid` como sku. Cambio de plantilla, 10.916 páginas.

### 3. Páginas de punto de interés (POI)
Viator tiene `/Miami-attractions/South-Beach` con "Explore options from $11". Tú tienes lat/lng
de 11.076 operadores: puedes agrupar por proximidad a POIs conocidos (South Beach, Biscayne
Bay, Key Biscayne, Lake Travis, Clearwater Beach, Molokini…) y generar landings tipo
*"Jet ski & boat rentals near South Beach"*. Son consultas con intención local muy alta que hoy
no tienes página para responder. Mismo generador que las landings de categoría.

### 4. Títulos con año y prueba social, más cortos
GYG: `Nombre - 2026 (Verified Reviews)`. Tú: `Nombre · Zona · Book Now`. Recortar el nombre a
~45 chars y usar `Nombre · Miami (4.8★, 187 reviews)` resuelve los 2.129 títulos largos y añade
la señal que Viator/GYG explotan. Solo plantilla.

### 5. FAQ tipo "People Also Ask" con enlaces a productos
Viator responde "What are the best tours in Miami?" con una lista enlazada de 5 fichas
concretas. Tus FAQ de zona son genéricas (clima, cómo llegar). Convertir 2–3 preguntas por zona
en respuestas que enlacen a los 5 operadores mejor valorados **desde los datos** mejora
enlazado interno y captura PAA. Ya tienes el generador de FAQPage.

---

## 🟡 Aprovechable con trabajo

### 6. Paginación real de listados
Viator sirve `/Miami/d662-ttd/2`…`/43`. Tus zonas grandes (westfl 1.630, miami 1.100+) cargan
todo por JS: Google indexa solo lo que está baked. Generar `/west-florida-activities/2`… con
50 operadores baked por página multiplica las páginas indexables con contenido real.

### 7. Reseñas con texto
GYG imprime 10 `Review` con `reviewBody`, `author`, `datePublished`. **No tienes el texto de las
reseñas** — FareHarbor no lo exporta en el marketplace CSV. Sin dato, no hay nada que copiar;
inventarlo sería fraude ante Google y ante el cliente. Si FareHarbor te da acceso a reseñas por
API, es el primer bloque a añadir.

### 8. Estado de filtros en la URL
GYG/Viator guardan fecha, precio y categoría en la query string → las búsquedas se comparten y
se indexan. Tus filtros son solo cliente. Bajo esfuerzo con `history.replaceState` (ya lo usas
en 36 páginas).

---

## 🔴 No copiar

- **45 locales de hreflang**: tu mercado es EN/ES. Más locales = más páginas que mantener sin tráfico.
- **1,5 MB de HTML por página**: tu ventaja de 20–88 KB es real en móvil y en crawl budget. No la pierdas.
- **"Reserve now & pay later"**: FareHarbor no lo soporta. Prometerlo rompería la reserva.
- **App móvil, wishlists, login**: infraestructura que no aporta a un afiliado.
- **`Organization` con `sameAs` a Wikipedia/Crunchbase**: solo tiene sentido con entidad conocida.

---

## Orden sugerido (impacto / esfuerzo)

1. Badges desde el export FH (`availability_next_week`, `quality_score`) — datos ya en mano
2. `Product` + `sku` en fichas — plantilla, rich results
3. Títulos cortos con rating — plantilla, resuelve 2.129 truncados
4. FAQ de zona con top-5 enlazado — generador existente
5. Landings POI — nuevo generador sobre lat/lng
6. Paginación baked de zonas grandes
7. Filtros en URL
