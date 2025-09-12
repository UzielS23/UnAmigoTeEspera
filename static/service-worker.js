const CACHE_NAME = 'unamigoteeespera-cache-v10';
const urlsToCache = [
    '/',
    '/static/img/logo.png',
    '/static/img/descarga%20(17).jpg',
    '/manifest.json',
    '/static/img/chaparro.jpg',
    '/static/img/Emma.jpg',
    '/static/img/max.jpg',
    '/static/img/mimi.jpg'
];


self.addEventListener('install', event => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => {
                console.log('Archivos cacheados');
                return cache.addAll(urlsToCache);
            })
    );
    self.skipWaiting(); 
});


self.addEventListener('activate', event => {
    event.waitUntil(
        caches.keys().then(keys => {
            return Promise.all(
                keys.filter(key => key !== CACHE_NAME)
                    .map(key => caches.delete(key))
            );
        })
    );
    self.clients.claim(); 
});


self.addEventListener('fetch', event => {
    event.respondWith(
        caches.match(event.request).then(cachedResponse => {
            if (cachedResponse) {
                return cachedResponse;
            }

           
            return fetch(event.request).then(networkResponse => {
               
                return caches.open(CACHE_NAME).then(cache => {
                    
                    if (networkResponse && networkResponse.status === 200 && networkResponse.type === 'basic') {
                        cache.put(event.request, networkResponse.clone());
                    }
                    return networkResponse;
                });
            }).catch(() => {
              
                if (event.request.destination === 'image') {
                    return caches.match('/static/img/logo.png');
                }
                return new Response('Estás offline', {status: 503, statusText: 'Offline'});
            });
        })
    );
});