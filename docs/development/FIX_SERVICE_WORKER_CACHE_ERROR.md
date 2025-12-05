# 修复Service Worker缓存错误

> **错误**：`Failed to execute 'put' on 'Cache': Request scheme 'chrome-extension' is unsupported`  
> **原因**：Service Worker试图缓存浏览器扩展程序的请求，但Cache API不支持  
> **解决**：在缓存前检查请求协议，只缓存http/https请求

---

## 错误分析

### 错误信息

```
Uncaught (in promise) TypeError: Failed to execute 'put' on 'Cache': Request scheme 'chrome-extension' is unsupported
```

### 根本原因

1. **浏览器扩展程序拦截请求**：
   - 某些浏览器扩展程序（如广告拦截器、开发者工具扩展等）会拦截网页请求
   - 这些请求的URL协议是 `chrome-extension://`（Chrome）或 `moz-extension://`（Firefox）

2. **Cache API限制**：
   - Cache API只支持缓存 `http://` 和 `https://` 协议的请求
   - 不支持缓存 `chrome-extension://`、`moz-extension://` 等扩展程序协议的请求

3. **Service Worker行为**：
   - Service Worker会拦截所有网络请求，包括扩展程序的请求
   - 当尝试缓存这些请求时，会抛出错误

---

## 解决方案

### 修复方法

**在缓存前检查请求协议**：

```javascript
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
```

### 修复内容

1. **协议检查**：
   - 使用 `new URL(request.url)` 解析请求URL
   - 检查协议是否为 `http:` 或 `https:`
   - 只缓存符合协议的请求

2. **错误处理**：
   - 在 `cache.put()` 后添加 `.catch()` 处理错误
   - 忽略缓存错误，避免影响正常功能
   - 记录警告日志（可选）

---

## 已修复的文件

**文件**：`web_service/frontend/sw.js`

**修改位置**：第92-100行

**修改前**：
```javascript
return fetch(request).then((response) => {
  // 只缓存成功的GET请求
  if (response.status === 200 && request.method === 'GET') {
    const responseToCache = response.clone();
    caches.open(CACHE_NAME).then((cache) => {
      cache.put(request, responseToCache);
    });
  }
  return response;
```

**修改后**：
```javascript
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
```

---

## 验证步骤

### 步骤1：清除旧Service Worker

1. 打开浏览器开发者工具（F12）
2. 切换到 Application 标签（Chrome）或 Storage 标签（Firefox）
3. 点击 Service Workers
4. 点击 "Unregister" 卸载旧的Service Worker
5. 刷新页面

### 步骤2：检查错误是否消失

1. 打开浏览器控制台（Console标签）
2. 刷新页面
3. 确认不再出现 `Failed to execute 'put' on 'Cache'` 错误
4. 确认Service Worker正常注册和激活

### 步骤3：验证缓存功能

1. 打开开发者工具 → Network标签
2. 刷新页面
3. 查看静态资源（HTML、CSS、JS）是否从Service Worker缓存加载
4. 确认API请求仍从网络加载

---

## 注意事项

1. **扩展程序请求**：
   - 扩展程序的请求不会被缓存（这是正常的）
   - 这些请求不会影响网页的正常功能

2. **错误处理**：
   - 添加了 `.catch()` 处理缓存错误
   - 即使某些请求无法缓存，也不会影响Service Worker的正常运行

3. **兼容性**：
   - 此修复适用于所有支持Service Worker的浏览器
   - 包括Chrome、Firefox、Edge等

---

## 相关文档

- `docs/development/PWA_STATUS.md` - PWA开发状态报告
- `docs/development/PWA_TESTING_GUIDE.md` - PWA测试指南

---

**最后更新**：2025-12-04

