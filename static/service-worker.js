const CACHE_NAME = 'unamigoteeespera-cache-v15'; // 🔹 Nueva versión
const urlsToCache = [
    '/',                       
    '/offline',  
    '/dashboard-graficas',
    '/apoyos',
    '/partials/apoyos',
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

// ===== INSTALL =====
self.addEventListener('install', event => {
    console.log('[SW] Instalando...');
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => cache.addAll(urlsToCache))
            .then(async () => {
                console.log('[SW] Archivos iniciales cacheados:');
                urlsToCache.forEach(url => console.log('  ✅', url));

                const cachedKeys = await caches.open(CACHE_NAME).then(c => c.keys());
                console.log('[SW] Recursos en cache tras instalación:');
                cachedKeys.forEach(req => console.log('  📦', req.url));
            })
            .catch(err => console.error('[SW] Error cacheando archivos iniciales:', err))
    );
    self.skipWaiting();
});

// ===== ACTIVATE =====
self.addEventListener('activate', event => {
    console.log('[SW] Activando...');
    event.waitUntil(
        caches.keys().then(keys => 
            Promise.all(keys.filter(key => key !== CACHE_NAME).map(k => {
                console.log('[SW] Eliminando caché antigua:', k);
                return caches.delete(k);
            }))
        ).then(async () => {
            console.log('[SW] Activación completada');

            const cache = await caches.open(CACHE_NAME);
            const cachedKeys = await cache.keys();
            console.log('[SW] Recursos cacheados actuales post-activación:');
            cachedKeys.forEach(req => console.log('  📦', req.url));
        })
    );
    self.clients.claim();
});

// ===== FETCH =====
self.addEventListener('fetch', event => {
    const requestUrl = new URL(event.request.url);

    if (requestUrl.origin !== self.location.origin) return;

    if (event.request.method === 'GET') {
        event.respondWith(networkFirstUpdateCache(event.request));
    } else {
        event.respondWith(fetch(event.request).catch(() => handleOfflineFallback(event.request, 'No GET')));
    }
});

// ===== FUNCIONES AUXILIARES =====
async function networkFirstUpdateCache(request) {
    const cache = await caches.open(CACHE_NAME);
    const cachedResponse = await cache.match(request, { ignoreSearch: true });

    try {
        const isDynamic = ['/apoyos', '/grafica_refugios', '/grafica_tiempo'].some(path => request.url.includes(path));
        let fetchRequest = request;

        if (isDynamic) {
            fetchRequest = new Request(request.url + (request.url.includes('?') ? '&' : '?') + '_ts=' + Date.now(), {
                method: request.method,
                headers: request.headers,
                mode: request.mode,
                credentials: request.credentials,
                redirect: request.redirect
            });
        }

        const networkResponse = await fetch(fetchRequest);

        if (networkResponse && networkResponse.status === 200) {
            await cache.put(request, networkResponse.clone());
            console.log('[SW] Caché actualizado desde red:', request.url);

            const cachedKeys = await cache.keys();
            console.log('[SW] Recursos actualmente en cache:');
            cachedKeys.forEach(req => console.log('  📦', req.url));

            const clients = await self.clients.matchAll();
            clients.forEach(client => client.postMessage({
                type: 'RESOURCE_UPDATED',
                url: request.url
            }));
        }

        return networkResponse;

    } catch (err) {
        console.log('[SW] Offline o error de red, usando cache:', request.url, err);

        // Si es gráfica, devolver el logo
        if (['/grafica_refugios', '/grafica_tiempo'].some(path => request.url.includes(path))) {
            const logo = await cache.match('/static/img/logo.png');
            return logo || new Response(null, { status: 404 });
        }

        if (cachedResponse) return cachedResponse;
        return handleOfflineFallback(request, err);
    }
}

// ===== FALLBACK OFFLINE =====
async function handleOfflineFallback(request, error) {
    console.error('[SW] Error al obtener recurso:', request.url, error);
    const cache = await caches.open(CACHE_NAME);

    if (request.destination === 'image') {
        const logo = await cache.match('/static/img/logo.png');
        return logo || new Response(null, { status: 404 });
    }

    if (request.mode === 'navigate' || (request.headers.get('accept') || '').includes('text/html')) {
        const offlinePage = await cache.match('/offline');
        return offlinePage || new Response('<h1>Offline</h1>', { status: 503, headers: { 'Content-Type': 'text/html' } });
    }

    // Para otros recursos, fallback genérico JSON
    return new Response(JSON.stringify({
        error: 'offline',
        message: 'Recurso no disponible mientras estás sin conexión'
    }), {
        status: 503,
        headers: { 'Content-Type': 'application/json' }
    });
}
