const CACHE_NAME = 'unamigoteeespera-cache-v15';
const urlsToCache = [
    '/',
    '/offline',
    '/login',
    '/dashboard-graficas',
    '/apoyos',
    '/partials/apoyos',
    '/notificaciones',
    '/static/img/logo.png',
    '/static/img/descarga%20(17).jpg',
    '/static/img/chaparro.jpg',
    '/static/img/Emma.jpg',
    '/static/img/max.jpg',
    '/static/img/mimi.jpg',
    '/manifest.json',
    '/static/img/icon-192.png',
    '/static/img/icon-512.png'
];

// INSTALL
self.addEventListener('install', event => {
    event.waitUntil(caches.open(CACHE_NAME).then(cache => cache.addAll(urlsToCache)));
    self.skipWaiting();
});

// ACTIVATE
self.addEventListener('activate', event => {
    event.waitUntil(
        caches.keys().then(keys =>
            Promise.all(keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k)))
        )
    );
    self.clients.claim();
});

// FETCH
self.addEventListener('fetch', event => {
    if (event.request.method !== 'GET') return;

    event.respondWith((async () => {
        const cache = await caches.open(CACHE_NAME);
        const cachedResponse = await cache.match(event.request, { ignoreSearch: true });

        if (cachedResponse) return cachedResponse;

        try {
            const isGraph = ['/grafica_refugios', '/grafica_tiempo'].some(path => event.request.url.includes(path));
            const fetchRequest = isGraph
                ? new Request(event.request.url, { cache: 'no-store', method: 'GET' })
                : event.request;

            const networkResponse = await fetch(fetchRequest);

            if (networkResponse && networkResponse.status === 200 && !isGraph) {
                await cache.put(event.request, networkResponse.clone());
            }

            return networkResponse;

        } catch (err) {
            console.log('[SW] Offline o error de red:', event.request.url);

            // 🔹 Para gráficas: devolver JSON vacío (evita error .map())
            if (['/grafica_refugios', '/grafica_tiempo'].some(path => event.request.url.includes(path))) {
                return new Response(JSON.stringify([]), {
                    status: 200,
                    headers: { 'Content-Type': 'application/json' }
                });
            }

            // Fallback general para imágenes
            if (event.request.destination === 'image') {
                return cache.match('/static/img/logo.png');
            }

            // Fallback para navegación
            if (event.request.mode === 'navigate' || (event.request.headers.get('accept') || '').includes('text/html')) {
                return cache.match('/offline');
            }

            // Fallback genérico JSON
            return new Response(JSON.stringify({ error: 'offline' }), {
                status: 503,
                headers: { 'Content-Type': 'application/json' }
            });
        }
    })());
});
