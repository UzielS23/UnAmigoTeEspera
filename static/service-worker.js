const CACHE_NAME = 'unamigoteeespera-cache-v9';
const urlsToCache = [
    '/',
    '/static/img/logo.png',
    '/static/img/descarga%20(17).jpg',
     '/manifest.json'
    
];

// Instalación del SW
self.addEventListener('install', event => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => {
                console.log('Archivos cacheados');
                return cache.addAll(urlsToCache);
            })
    );
    self.skipWaiting(); // activa el SW inmediatamente
});

// Activación del SW
self.addEventListener('activate', event => {
    event.waitUntil(
        caches.keys().then(keys => {
            return Promise.all(
                keys.filter(key => key !== CACHE_NAME)
                    .map(key => caches.delete(key))
            );
        })
    );
    self.clients.claim(); // toma control de las páginas abiertas
});

// Interceptar peticiones
self.addEventListener('fetch', event => {
    event.respondWith(
        caches.match(event.request).then(cachedResponse => {
            if (cachedResponse) {
                return cachedResponse;
            }

            // Si no está en cache, lo buscamos online
            return fetch(event.request).then(networkResponse => {
                // Guardamos en cache para futuras peticiones
                return caches.open(CACHE_NAME).then(cache => {
                    // Solo cacheamos respuestas válidas
                    if (networkResponse && networkResponse.status === 200 && networkResponse.type === 'basic') {
                        cache.put(event.request, networkResponse.clone());
                    }
                    return networkResponse;
                });
            }).catch(() => {
                // fallback si no hay conexión
                if (event.request.destination === 'image') {
                    return caches.match('/static/img/logo.png');
                }
                return new Response('Estás offline', {status: 503, statusText: 'Offline'});
            });
        })
    );
});
