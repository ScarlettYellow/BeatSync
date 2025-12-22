// BeatSync Service Worker
// 版本：v1.3.17（添加文件选择和上传流程调试日志）
const CACHE_NAME = 'beatsync-v1.3.17';
const STATIC_CACHE_URLS = [
  '/',
  '/index.html',
  '/style.css?v=20251246',
  '/script.js?v=20251246',
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
  console.log('[Service Worker] 激活中，清除所有旧缓存...');
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          // 删除所有旧版本的缓存（包括CSS/JS缓存）
          if (cacheName !== CACHE_NAME) {
            console.log('[Service Worker] 删除旧缓存:', cacheName);
            return caches.delete(cacheName);
          }
        })
      ).then(() => {
        // 清除所有CSS/JS相关的缓存项
        return caches.open(CACHE_NAME).then((cache) => {
          return cache.keys().then((keys) => {
            keys.forEach((request) => {
              const url = new URL(request.url);
              // 删除所有CSS和JS文件的缓存
              if (url.pathname.endsWith('.css') || url.pathname.endsWith('.js')) {
                console.log('[Service Worker] 清除CSS/JS缓存:', url.pathname);
                cache.delete(request);
              }
            });
          });
        });
      });
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
  
  // CSS和JS文件：网络优先（确保总是加载最新版本，解决缓存问题）
  if (url.pathname.endsWith('.css') || url.pathname.endsWith('.js')) {
    event.respondWith(
      fetch(request)
        .then((response) => {
          // 网络请求成功，直接返回（不缓存CSS/JS，避免缓存问题）
          console.log('[Service Worker] 网络优先加载:', url.pathname);
          return response;
        })
        .catch((error) => {
          // 网络请求失败，尝试从缓存获取（作为回退）
          console.warn('[Service Worker] 网络请求失败，尝试缓存:', url.pathname, error);
          return caches.match(request).then((cachedResponse) => {
            if (cachedResponse) {
              return cachedResponse;
            }
            throw error;
          });
        })
    );
    return;
  }
  
  // 其他静态资源：缓存优先，网络回退
  event.respondWith(
    caches.match(request)
      .then((cachedResponse) => {
        if (cachedResponse) {
          // 从缓存返回
          return cachedResponse;
        }
        
        // 缓存中没有，从网络获取
        return fetch(request).then((response) => {
          // 只缓存成功的GET请求，且只缓存http/https协议的请求（排除扩展程序请求）
          const requestUrl = new URL(request.url);
          const isHttpOrHttps = requestUrl.protocol === 'http:' || requestUrl.protocol === 'https:';
          
          if (response.status === 200 && request.method === 'GET' && isHttpOrHttps) {
            const responseToCache = response.clone();
            caches.open(CACHE_NAME).then((cache) => {
              cache.put(request, responseToCache).catch((error) => {
                // 忽略缓存错误（如扩展程序请求、不支持缓存的请求等）
                console.warn('[Service Worker] 缓存失败（已忽略）:', error.message);
              });
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

