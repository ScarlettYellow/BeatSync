// BeatSync Service Worker
// 版本：v1.0.0
const CACHE_NAME = 'beatsync-v1.0.0';
const STATIC_CACHE_URLS = [
  '/',
  '/index.html',
  '/style.css',
  '/script.js',
  '/favicon.svg',
  '/favicon.ico'
];

// 安装Service Worker
self.addEventListener('install', (event) => {
  console.log('[Service Worker] 安装中...');
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        console.log('[Service Worker] 缓存静态资源');
        // 只缓存关键资源，不强制所有资源都缓存成功
        return cache.addAll(STATIC_CACHE_URLS).catch((error) => {
          console.warn('[Service Worker] 部分资源缓存失败:', error);
        });
      })
  );
  // 立即激活新的Service Worker
  self.skipWaiting();
});

// 激活Service Worker
self.addEventListener('activate', (event) => {
  console.log('[Service Worker] 激活中...');
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          // 删除旧版本的缓存
          if (cacheName !== CACHE_NAME) {
            console.log('[Service Worker] 删除旧缓存:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
  // 立即控制所有客户端
  return self.clients.claim();
});

// 拦截网络请求
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);
  
  // API请求：网络优先（确保实时性）
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(
      fetch(request)
        .then((response) => {
          // 网络请求成功，直接返回
          return response;
        })
        .catch((error) => {
          // 网络请求失败，尝试从缓存获取（如果有）
          console.warn('[Service Worker] API请求失败，尝试缓存:', error);
          return caches.match(request).then((cachedResponse) => {
            if (cachedResponse) {
              return cachedResponse;
            }
            // 如果缓存也没有，返回错误响应
            return new Response('网络错误，请检查网络连接', {
              status: 503,
              statusText: 'Service Unavailable',
              headers: { 'Content-Type': 'text/plain; charset=utf-8' }
            });
          });
        })
    );
    return;
  }
  
  // 静态资源：缓存优先，网络回退
  event.respondWith(
    caches.match(request)
      .then((cachedResponse) => {
        if (cachedResponse) {
          // 从缓存返回
          return cachedResponse;
        }
        
        // 缓存中没有，从网络获取
        return fetch(request).then((response) => {
          // 只缓存成功的GET请求
          if (response.status === 200 && request.method === 'GET') {
            const responseToCache = response.clone();
            caches.open(CACHE_NAME).then((cache) => {
              cache.put(request, responseToCache);
            });
          }
          return response;
        }).catch((error) => {
          console.warn('[Service Worker] 网络请求失败:', error);
          // 如果是HTML请求，返回离线页面（可选）
          if (request.headers.get('accept').includes('text/html')) {
            return caches.match('/index.html');
          }
          throw error;
        });
      })
  );
});

// 处理消息（用于更新通知等）
self.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
});

