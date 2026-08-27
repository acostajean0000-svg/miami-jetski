/* Service worker — Torre Serrallés 305
   Navegación: red primero (siempre la versión más reciente); recursos: caché primero. */
const CACHE = "serralles305-v1";
const ASSETS = ["./","./index.html","./manifest.json","./icon-192.png","./icon-512.png",
  "./plan-a.jpg","./plan-b.jpg","./plan-c.jpg","./plan-d.jpg","./plan-e.jpg","./plan-f.jpg","./og.jpg"];
self.addEventListener("install", e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(ASSETS)).then(() => self.skipWaiting()));
});
self.addEventListener("activate", e => {
  e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== CACHE).map(k => caches.delete(k)))).then(() => self.clients.claim()));
});
self.addEventListener("fetch", e => {
  const url = new URL(e.request.url);
  if (e.request.mode === "navigate") {           // HTML: red primero para no servir versiones viejas
    e.respondWith(fetch(e.request).then(r => { const cp = r.clone(); caches.open(CACHE).then(c => c.put("./index.html", cp)); return r; })
      .catch(() => caches.match("./index.html")));
    return;
  }
  if (url.origin === location.origin) {          // recursos propios: caché primero
    e.respondWith(caches.match(e.request).then(hit => hit || fetch(e.request).then(r => { const cp = r.clone(); caches.open(CACHE).then(c => c.put(e.request, cp)); return r; })));
  }
});
