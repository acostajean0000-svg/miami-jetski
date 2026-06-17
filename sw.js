/**
 * sw.js — Service Worker para miamijetskiboatrentals.com
 *
 * Estrategia:
 *  - Cache-first para estáticos (CSS, JSON, imágenes Filestack)
 *  - Network-first para HTMLs (siempre fresh, pero fallback cache)
 *  - Skip cache para iframes (FareHarbor) y trackers
 *
 * Versionado: incrementar CACHE_NAME al cambiar lógica para invalidar.
 */

const CACHE_NAME = 'mjb-v1.0.6';
const STATIC_ASSETS = [
  '/',
  '/operator.css',
  '/manifest.json',
  '/og-image.png',
  '/apple-touch-icon.png',
  '/slug-map.js'
];

const RUNTIME_CACHE = 'mjb-runtime-v6';

// Install: precache estáticos
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(STATIC_ASSETS).catch(() => {}))
      .then(() => self.skipWaiting())
  );
});

// Activate: BORRA TODAS las caches viejas (incluyendo runtime con responses corruptas)
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(
        keys
          .filter(k => k !== CACHE_NAME && k !== RUNTIME_CACHE)
          .map(k => {
            console.log('[SW] Deleting old cache:', k);
            return caches.delete(k);
          })
      )
    ).then(() => self.clients.claim()).then(() => {
      // Notificar a clients que el nuevo SW está activo
      return self.clients.matchAll().then(clients => {
        clients.forEach(c => c.postMessage({type: 'SW_UPDATED', version: '1.0.5'}));
      });
    })
  );
});

// Fetch handler
self.addEventListener('fetch', event => {
  const { request } = event;
  const url = new URL(request.url);

  // Solo GET
  if (request.method !== 'GET') return;

  // Skip trackers y analítica (siempre network)
  if (/clarity\.ms|googletagmanager|google-analytics|connect\.facebook|fareharbor\.com/.test(url.hostname)) {
    return;
  }

  // Skip mismo origen + paths admin/internal
  if (url.pathname.startsWith('/webhook') || url.pathname.includes('/admin')) return;

  // Filestack / Google fonts: NO intercept (let browser handle directly)
  // BUG: cachear estos rompía la carga de thumbnails al servir responses corruptas
  if (/filestackcontent\.com|googleapis\.com|gstatic\.com/.test(url.hostname)) {
    return; // browser usa su cache normal
  }

  // JSON data: stale-while-revalidate
  if (url.pathname.startsWith('/data/') || url.pathname.endsWith('.json')) {
    event.respondWith(
      caches.match(request).then(cached => {
        const fetchPromise = fetch(request).then(response => {
          if (response.ok) {
            const clone = response.clone();
            caches.open(RUNTIME_CACHE).then(c => c.put(request, clone));
          }
          return response;
        }).catch(() => cached);
        return cached || fetchPromise;
      })
    );
    return;
  }

  // CSS / JS estáticos: cache-first
  if (/\.(css|js|woff2?|svg|png|webp)$/.test(url.pathname)) {
    event.respondWith(
      caches.match(request).then(cached => {
        if (cached) return cached;
        return fetch(request).then(response => {
          if (response.ok) {
            const clone = response.clone();
            caches.open(RUNTIME_CACHE).then(c => c.put(request, clone));
          }
          return response;
        });
      })
    );
    return;
  }

  // HTMLs: SIEMPRE network (no cachear nunca). Solo fallback offline.
  if (request.headers.get('Accept')?.includes('text/html')) {
    event.respondWith(
      fetch(request).catch(() => caches.match('/'))
    );
    return;
  }
});
