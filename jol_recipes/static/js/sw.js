var staticCacheName = "JOL-recipe-v1"

var filesToCache = [
    '/',
    '/list',
    '/recipe/bagels',
    '/offline',
    '/static/images/favicon.ico',
    '/static/images/icons/72.png',
    '/static/images/icons/100.png',
    '/static/images/icons/128.png',
    '/static/images/icons/144.png',
    '/static/images/icons/152.png',
    '/static/images/icons/196.png',
    '/static/images/icons/256.png',
    '/static/images/icons/512.png',
    '/static/js/bootstrap.bundle.min.js',
    '/static/js/jquery-3.6.0.min.js',
    '/static/css/bootstrap.min.css',
    '/static/css/custom.min.css'
];

// Cache on install
self.addEventListener("install", event => {
    this.skipWaiting();
    event.waitUntil(
        caches.open(staticCacheName)
        .then(cache => {
            return cache.addAll(filesToCache);
        })
    )
});

// Clear cache on activate
self.addEventListener('activate', (e) => {
    e.waitUntil(
        caches.keys().then((keyList) => {
            return Promise.all(keyList.map((key) => {
                if (key !== staticCacheName) {
                    return caches.delete(key);
                }
            }));
        })
    );
});

// Serve from cache, and return offline page if client is offline 
/* this.addEventListener('fetch', event => {
    if (event.request.mode === 'navigate' || (event.request.method === 'GET' && event.request.headers.get('accept').includes('text/html'))) {
        event.respondWith(
            fetch(event.request.url).catch(error => {
                return caches.match('/offline');
            })
        );
    } else {
        event.respondWith(caches.match(event.request)
            .then(function(response) {
                return response || fetch(event.request);
            })
        );
    }
}); */
self.addEventListener('fetch', (e) => {
    e.respondWith(
        caches.match(e.request).then((r) => {
            console.log('[Service Worker] Fetching resource: ' + e.request.url);
            return r || fetch(e.request).then((response) => {
                return caches.open(staticCacheName).then((cache) => {
                    console.log('[Service Worker] Caching new resource: ' + e.request.url);
                    cache.put(e.request, response.clone());
                    return response;
                });
            });
        })
    );
});