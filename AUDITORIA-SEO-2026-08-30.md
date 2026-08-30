# Auditoría SEO — miamijetskiboatrentals.com
**Fecha:** 30 de agosto de 2026 · **Alcance:** 11.546 páginas locales + producción + datos GSC de slingshotmia

---

## Resumen ejecutivo

La base on-page es excepcionalmente sólida: cero títulos duplicados, cero descripciones duplicadas,
H1 único en todas las páginas, canónicas perfectas, hreflang recíproco y sitemap completo (11.538 URLs).
Los problemas graves no están en el HTML sino en tres capas: **lo que producción todavía sirve**,
**la canibalización con slingshotmia.com**, y un puñado de señales menores a escala.

---

## 🔴 Crítico

### 1. Producción sirve la versión rota (11.700+ archivos sin desplegar)
Todo lo corregido en esta sesión sigue vivo en el dominio real:
- 64 fichas de operador **tapadas por redirects 301** → Google las está desindexando ahora mismo
- Austin: 388 tarjetas → 404 (mapa de slugs de Naples); ídem Myrtle, Havasu, Ozarks, Lake Mead, Nassau
- Portada /es con los 20 botones y 20 imágenes rotos
- 58 enlaces con parámetros duplicados (el bug de la comisión Bruschi) y 104 con calendario fijo
- Conversiones de Ads perdidas en ~65% del sitio

**Acción: desplegar.** Es la medida SEO con mayor impacto disponible.

### 2. Canibalización con slingshotmia.com (confirmada con GSC)
La posición media de slingshotmia pasó de ~7 a ~28 en la segunda quincena de junio 2026 —
exactamente cuando se expandió este marketplace. Clicks -44% interanual (ago 2025: 227 → ago 2026: 128).
El 86% de las impresiones de slingshotmia son consultas "slingshot", y este sitio compite con:
- 63 páginas con "slingshot" en el slug (incl. `/6-seaters-slingshot-polaris-miami`, casi idéntico
  al `/6-seaters-slingshot-miami` de slingshotmia)
- "Slingshot" en el título de la portada: *"Jet Ski, Slingshot & Boat Rentals Florida"*
- 24 páginas miami+jetski contra las 159 consultas jet-ski de slingshotmia

**Decisión de negocio pendiente:** qué dominio debe ganar "slingshot rental miami".
Recomendación: el marketplace se retira de slingshot-Miami (enlaza a slingshotmia como operador
destacado) y conserva el resto del país.

---

## 🟡 Importante

### 3. Títulos largos: 2.129 páginas >65 caracteres
Google los trunca en resultados. Patrón dominante: nombre de producto largo + zona + "· Book Now".
Arreglable por plantilla (recortar el sufijo cuando el nombre excede).

### 4. og:image en dominios de terceros
- 88 páginas usan `www.filepicker.io` — el dominio **antiguo** de Filestack; riesgo de que deje de resolver
- 5 páginas apuntan a dominios de operadores ajenos (rippleeffectecotours, civitatis, wsimg…)
- Las 11.001 de `cdn.filestackcontent.com` funcionan, aunque self-hosted daría más control

### 5. Meta descriptions largas: 221 páginas >165 caracteres
Se truncan. Mismo tratamiento por plantilla que los títulos.

### 6. CTR hundido con buena posición (lección de GSC aplicable aquí)
En slingshotmia hay ~9.000 impresiones en posiciones 7–15 con CTR≈0 porque el título no responde
a la consulta (`automatic`, `price`, `south beach`). El marketplace tiene el mismo riesgo en sus
215 landings de categoría: revisar Search Console de **este** dominio con el mismo método cuando
haya datos post-deploy.

---

## 🟢 Correcto (verificado, no tocar)

| Factor | Estado |
|---|---|
| Títulos duplicados | 0 de 11.546 |
| Meta descriptions duplicadas o ausentes | 0 |
| H1 ausente o múltiple | 0 |
| Canónicas (ausentes/duplicadas/rotas) | 0 — las 4 de Cozumel consolidan a propósito |
| hreflang | 366 páginas, reciprocidad completa, 0 rotos |
| Sitemap | índice + 48 hijos, 11.538 URLs, exclusiones correctas |
| noindex | solo 404 y offline (correcto) |
| Contenido delgado <150 palabras | 4 (una es offline.html) |
| JSON-LD | 24.050 bloques válidos; solo 2 páginas raíz sin schema |
| Enlaces internos (estáticos + generados por JS) | 0 rotos de 26.220 |
| Redirects/rewrites | 0 bucles, 0 destinos muertos (tras esta sesión) |
| Robots.txt | correcto, sitemap declarado |

---

## Orden recomendado

1. **Deploy** (desbloquea todo lo demás)
2. Decidir la estrategia slingshot Miami ↔ slingshotmia
3. Solicitar reindexación en GSC de las 64 fichas des-tapadas y las 6 páginas de zona reparadas
4. Recortar los 2.129 títulos y 221 descripciones por plantilla
5. Migrar las 88 og:image de filepicker.io a cdn.filestackcontent.com
6. En 3–4 semanas: export de GSC de este dominio y repetir el análisis de CTR por consulta
