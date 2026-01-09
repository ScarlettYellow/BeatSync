# 使用后端 API 实现订阅功能

## 概述

由于 Capacitor 8 的插件注册问题，我们改为使用后端 API 来实现订阅功能。这样可以在 iOS App 和 Web 端都正常工作，不依赖原生插件。

---

## 架构设计

### 整体流程

```
┌─────────────────┐         ┌─────────────────┐
│   iOS App       │         │   Web Frontend  │
│  (Capacitor)    │         │  (GitHub Pages) │
└────────┬────────┘         └────────┬────────┘
         │                            │
         │  HTTPS API                 │  HTTPS API
         │                            │
         └────────────┬───────────────┘
                      │
         ┌────────────▼────────────┐
         │   FastAPI Backend       │
         │  (beatsync.site)        │
         │                         │
         │  - 产品列表              │
         │  - 订阅状态              │
         │  - 支付订单              │
         │  - 收据验证              │
         │  - 订阅历史              │
         └─────────────────────────┘
```

### iOS App 购买流程

1. **获取产品列表**：调用后端 API `/api/subscription/products`
2. **购买**：
   - 优先使用原生 StoreKit 插件（如果可用）
   - 购买成功后，调用后端 API `/api/subscription/verify-receipt` 验证收据
   - 如果原生插件不可用，降级到后端支付 API
3. **恢复购买**：
   - 优先使用原生 StoreKit 插件（如果可用）
   - 恢复成功后，验证所有收据
   - 如果原生插件不可用，从后端获取订阅历史

### Web 购买流程

1. **获取产品列表**：调用后端 API `/api/subscription/products`
2. **购买**：调用后端 API `/api/subscription/purchase` 创建支付订单，跳转到支付页面
3. **恢复购买**：调用后端 API `/api/subscription/history` 获取订阅历史

---

## 后端 API 端点

### 1. 获取产品列表

**端点**：`GET /api/subscription/products`

**响应**：
```json
{
    "products": [
        {
            "id": "basic_monthly",
            "type": "subscription",
            "displayName": "基础版（月付）",
            "description": "公测期特价：4.8元/月，每月20次下载",
            "price": 4.80,
            "displayPrice": "¥4.80/月",
            "credits": 20,
            "period": "monthly"
        },
        {
            "id": "premium_monthly",
            "type": "subscription",
            "displayName": "高级版（月付）",
            "description": "公测期特价：19.9元/月，每月100次下载",
            "price": 19.90,
            "displayPrice": "¥19.90/月",
            "credits": 100,
            "period": "monthly"
        },
        {
            "id": "pack_10",
            "type": "purchase",
            "displayName": "10次下载包",
            "description": "一次性购买10次下载，永久有效",
            "price": 5.00,
            "displayPrice": "¥5.00",
            "credits": 10,
            "period": null
        },
        {
            "id": "pack_20",
            "type": "purchase",
            "displayName": "20次下载包",
            "description": "一次性购买20次下载，永久有效",
            "price": 9.00,
            "displayPrice": "¥9.00",
            "credits": 20,
            "period": null
        }
    ],
    "count": 4
}
```

### 2. 获取订阅状态

**端点**：`GET /api/subscription/status`

**请求头**：`Authorization: Bearer <token>`

**响应**：
```json
{
    "hasActiveSubscription": true,
    "subscription": {
        "type": "basic_monthly",
        "status": "active",
        "start_date": "2025-01-01T00:00:00Z",
        "end_date": "2025-02-01T00:00:00Z",
        "auto_renew": true
    },
    "download_credits": {
        "subscription": {
            "used": 12,
            "total": 20,
            "remaining": 8
        },
        "purchase": {
            "used": 0,
            "total": 0,
            "remaining": 0
        }
    }
}
```

### 3. 创建支付订单（Web）

**端点**：`POST /api/subscription/purchase`

**请求头**：`Authorization: Bearer <token>`

**请求体**：
```
product_id=basic_monthly&payment_method=wechat
```

**响应**：
```json
{
    "order_id": "order_123456",
    "payment_url": "https://pay.wechat.com/...",
    "product_id": "basic_monthly"
}
```

### 4. 验证 iOS 收据

**端点**：`POST /api/subscription/verify-receipt`

**请求头**：`Authorization: Bearer <token>`

**请求体**：
```
receipt_data=<base64_receipt>&product_id=basic_monthly
```

**响应**：
```json
{
    "verified": true,
    "subscription": {
        "type": "basic_monthly",
        "status": "active",
        "end_date": "2025-02-01T00:00:00Z"
    }
}
```

### 5. 获取订阅历史

**端点**：`GET /api/subscription/history?page=1&limit=100`

**请求头**：`Authorization: Bearer <token>`

**响应**：
```json
{
    "subscriptions": [
        {
            "id": 1,
            "subscription_type": "basic_monthly",
            "status": "active",
            "start_date": "2025-01-01T00:00:00Z",
            "end_date": "2025-02-01T00:00:00Z",
            "auto_renew": true,
            "platform": "ios",
            "transaction_id": "1000000123456789"
        }
    ],
    "total": 1,
    "page": 1,
    "limit": 100
}
```

---

## 前端实现

### 主要修改

1. **`getAvailableProducts()`**：
   - 改为调用后端 API `/api/subscription/products`
   - 不再依赖原生插件

2. **`purchase(productId)`**：
   - iOS App：优先使用原生 StoreKit 插件，购买成功后验证收据
   - 如果原生插件不可用，降级到后端支付 API
   - Web：直接使用后端支付 API

3. **`restorePurchases()`**：
   - iOS App：优先使用原生 StoreKit 插件，恢复成功后验证收据
   - 如果原生插件不可用，从后端获取订阅历史
   - Web：从后端获取订阅历史

4. **`checkAvailability()`**：
   - 现在所有平台都返回可用（通过后端 API）

5. **`getSubscriptionStatus()`**：
   - 统一使用后端 API `/api/subscription/status`

### 代码位置

- **前端订阅服务**：`web_service/frontend/subscription.js`
- **后端 API**：`web_service/backend/main.py`

---

## 优势

1. **不依赖原生插件**：解决了 Capacitor 8 插件注册问题
2. **跨平台统一**：iOS App 和 Web 使用相同的后端 API
3. **降级策略**：iOS App 优先使用原生插件，失败时自动降级到后端 API
4. **易于维护**：所有订阅逻辑集中在后端，前端只需调用 API

---

## 测试步骤

### 1. 获取产品列表

在浏览器控制台或 Safari Web Inspector 中执行：
```javascript
const products = await subscriptionService.getAvailableProducts();
console.log('产品列表:', products);
```

### 2. 查询订阅状态

```javascript
const status = await subscriptionService.getSubscriptionStatus();
console.log('订阅状态:', status);
```

### 3. 购买（Web）

```javascript
// 需要先登录
const result = await subscriptionService.purchase('basic_monthly');
console.log('购买结果:', result);
```

### 4. 恢复购买

```javascript
const result = await subscriptionService.restorePurchases();
console.log('恢复购买结果:', result);
```

---

## 注意事项

1. **iOS App 原生插件**：
   - 如果原生插件可用，会优先使用原生 StoreKit
   - 如果原生插件不可用，会自动降级到后端 API
   - 这样可以在插件问题解决后无缝切换

2. **用户认证**：
   - 所有需要认证的 API 都需要 `Authorization: Bearer <token>` 请求头
   - Token 存储在 `localStorage`（Web）或 `Capacitor Preferences`（iOS App）

3. **API 基础 URL**：
   - iOS App：`https://beatsync.site`
   - Web：根据当前域名自动判断
   - 本地开发：`http://localhost:8000`

---

## 后续优化

1. **iOS App 原生插件修复后**：
   - 可以完全使用原生 StoreKit，提供更好的用户体验
   - 后端 API 作为降级方案保留

2. **支付方式扩展**：
   - 可以添加更多支付方式（支付宝、Stripe 等）
   - 后端 API 已经支持多种支付方式

3. **错误处理**：
   - 可以添加更详细的错误处理和用户提示
   - 可以添加重试机制

---

**更新时间**：2025-12-13  
**状态**：✅ 已完成






# 使用后端 API 实现订阅功能

## 概述

由于 Capacitor 8 的插件注册问题，我们改为使用后端 API 来实现订阅功能。这样可以在 iOS App 和 Web 端都正常工作，不依赖原生插件。

---

## 架构设计

### 整体流程

```
┌─────────────────┐         ┌─────────────────┐
│   iOS App       │         │   Web Frontend  │
│  (Capacitor)    │         │  (GitHub Pages) │
└────────┬────────┘         └────────┬────────┘
         │                            │
         │  HTTPS API                 │  HTTPS API
         │                            │
         └────────────┬───────────────┘
                      │
         ┌────────────▼────────────┐
         │   FastAPI Backend       │
         │  (beatsync.site)        │
         │                         │
         │  - 产品列表              │
         │  - 订阅状态              │
         │  - 支付订单              │
         │  - 收据验证              │
         │  - 订阅历史              │
         └─────────────────────────┘
```

### iOS App 购买流程

1. **获取产品列表**：调用后端 API `/api/subscription/products`
2. **购买**：
   - 优先使用原生 StoreKit 插件（如果可用）
   - 购买成功后，调用后端 API `/api/subscription/verify-receipt` 验证收据
   - 如果原生插件不可用，降级到后端支付 API
3. **恢复购买**：
   - 优先使用原生 StoreKit 插件（如果可用）
   - 恢复成功后，验证所有收据
   - 如果原生插件不可用，从后端获取订阅历史

### Web 购买流程

1. **获取产品列表**：调用后端 API `/api/subscription/products`
2. **购买**：调用后端 API `/api/subscription/purchase` 创建支付订单，跳转到支付页面
3. **恢复购买**：调用后端 API `/api/subscription/history` 获取订阅历史

---

## 后端 API 端点

### 1. 获取产品列表

**端点**：`GET /api/subscription/products`

**响应**：
```json
{
    "products": [
        {
            "id": "basic_monthly",
            "type": "subscription",
            "displayName": "基础版（月付）",
            "description": "公测期特价：4.8元/月，每月20次下载",
            "price": 4.80,
            "displayPrice": "¥4.80/月",
            "credits": 20,
            "period": "monthly"
        },
        {
            "id": "premium_monthly",
            "type": "subscription",
            "displayName": "高级版（月付）",
            "description": "公测期特价：19.9元/月，每月100次下载",
            "price": 19.90,
            "displayPrice": "¥19.90/月",
            "credits": 100,
            "period": "monthly"
        },
        {
            "id": "pack_10",
            "type": "purchase",
            "displayName": "10次下载包",
            "description": "一次性购买10次下载，永久有效",
            "price": 5.00,
            "displayPrice": "¥5.00",
            "credits": 10,
            "period": null
        },
        {
            "id": "pack_20",
            "type": "purchase",
            "displayName": "20次下载包",
            "description": "一次性购买20次下载，永久有效",
            "price": 9.00,
            "displayPrice": "¥9.00",
            "credits": 20,
            "period": null
        }
    ],
    "count": 4
}
```

### 2. 获取订阅状态

**端点**：`GET /api/subscription/status`

**请求头**：`Authorization: Bearer <token>`

**响应**：
```json
{
    "hasActiveSubscription": true,
    "subscription": {
        "type": "basic_monthly",
        "status": "active",
        "start_date": "2025-01-01T00:00:00Z",
        "end_date": "2025-02-01T00:00:00Z",
        "auto_renew": true
    },
    "download_credits": {
        "subscription": {
            "used": 12,
            "total": 20,
            "remaining": 8
        },
        "purchase": {
            "used": 0,
            "total": 0,
            "remaining": 0
        }
    }
}
```

### 3. 创建支付订单（Web）

**端点**：`POST /api/subscription/purchase`

**请求头**：`Authorization: Bearer <token>`

**请求体**：
```
product_id=basic_monthly&payment_method=wechat
```

**响应**：
```json
{
    "order_id": "order_123456",
    "payment_url": "https://pay.wechat.com/...",
    "product_id": "basic_monthly"
}
```

### 4. 验证 iOS 收据

**端点**：`POST /api/subscription/verify-receipt`

**请求头**：`Authorization: Bearer <token>`

**请求体**：
```
receipt_data=<base64_receipt>&product_id=basic_monthly
```

**响应**：
```json
{
    "verified": true,
    "subscription": {
        "type": "basic_monthly",
        "status": "active",
        "end_date": "2025-02-01T00:00:00Z"
    }
}
```

### 5. 获取订阅历史

**端点**：`GET /api/subscription/history?page=1&limit=100`

**请求头**：`Authorization: Bearer <token>`

**响应**：
```json
{
    "subscriptions": [
        {
            "id": 1,
            "subscription_type": "basic_monthly",
            "status": "active",
            "start_date": "2025-01-01T00:00:00Z",
            "end_date": "2025-02-01T00:00:00Z",
            "auto_renew": true,
            "platform": "ios",
            "transaction_id": "1000000123456789"
        }
    ],
    "total": 1,
    "page": 1,
    "limit": 100
}
```

---

## 前端实现

### 主要修改

1. **`getAvailableProducts()`**：
   - 改为调用后端 API `/api/subscription/products`
   - 不再依赖原生插件

2. **`purchase(productId)`**：
   - iOS App：优先使用原生 StoreKit 插件，购买成功后验证收据
   - 如果原生插件不可用，降级到后端支付 API
   - Web：直接使用后端支付 API

3. **`restorePurchases()`**：
   - iOS App：优先使用原生 StoreKit 插件，恢复成功后验证收据
   - 如果原生插件不可用，从后端获取订阅历史
   - Web：从后端获取订阅历史

4. **`checkAvailability()`**：
   - 现在所有平台都返回可用（通过后端 API）

5. **`getSubscriptionStatus()`**：
   - 统一使用后端 API `/api/subscription/status`

### 代码位置

- **前端订阅服务**：`web_service/frontend/subscription.js`
- **后端 API**：`web_service/backend/main.py`

---

## 优势

1. **不依赖原生插件**：解决了 Capacitor 8 插件注册问题
2. **跨平台统一**：iOS App 和 Web 使用相同的后端 API
3. **降级策略**：iOS App 优先使用原生插件，失败时自动降级到后端 API
4. **易于维护**：所有订阅逻辑集中在后端，前端只需调用 API

---

## 测试步骤

### 1. 获取产品列表

在浏览器控制台或 Safari Web Inspector 中执行：
```javascript
const products = await subscriptionService.getAvailableProducts();
console.log('产品列表:', products);
```

### 2. 查询订阅状态

```javascript
const status = await subscriptionService.getSubscriptionStatus();
console.log('订阅状态:', status);
```

### 3. 购买（Web）

```javascript
// 需要先登录
const result = await subscriptionService.purchase('basic_monthly');
console.log('购买结果:', result);
```

### 4. 恢复购买

```javascript
const result = await subscriptionService.restorePurchases();
console.log('恢复购买结果:', result);
```

---

## 注意事项

1. **iOS App 原生插件**：
   - 如果原生插件可用，会优先使用原生 StoreKit
   - 如果原生插件不可用，会自动降级到后端 API
   - 这样可以在插件问题解决后无缝切换

2. **用户认证**：
   - 所有需要认证的 API 都需要 `Authorization: Bearer <token>` 请求头
   - Token 存储在 `localStorage`（Web）或 `Capacitor Preferences`（iOS App）

3. **API 基础 URL**：
   - iOS App：`https://beatsync.site`
   - Web：根据当前域名自动判断
   - 本地开发：`http://localhost:8000`

---

## 后续优化

1. **iOS App 原生插件修复后**：
   - 可以完全使用原生 StoreKit，提供更好的用户体验
   - 后端 API 作为降级方案保留

2. **支付方式扩展**：
   - 可以添加更多支付方式（支付宝、Stripe 等）
   - 后端 API 已经支持多种支付方式

3. **错误处理**：
   - 可以添加更详细的错误处理和用户提示
   - 可以添加重试机制

---

**更新时间**：2025-12-13  
**状态**：✅ 已完成






# 使用后端 API 实现订阅功能

## 概述

由于 Capacitor 8 的插件注册问题，我们改为使用后端 API 来实现订阅功能。这样可以在 iOS App 和 Web 端都正常工作，不依赖原生插件。

---

## 架构设计

### 整体流程

```
┌─────────────────┐         ┌─────────────────┐
│   iOS App       │         │   Web Frontend  │
│  (Capacitor)    │         │  (GitHub Pages) │
└────────┬────────┘         └────────┬────────┘
         │                            │
         │  HTTPS API                 │  HTTPS API
         │                            │
         └────────────┬───────────────┘
                      │
         ┌────────────▼────────────┐
         │   FastAPI Backend       │
         │  (beatsync.site)        │
         │                         │
         │  - 产品列表              │
         │  - 订阅状态              │
         │  - 支付订单              │
         │  - 收据验证              │
         │  - 订阅历史              │
         └─────────────────────────┘
```

### iOS App 购买流程

1. **获取产品列表**：调用后端 API `/api/subscription/products`
2. **购买**：
   - 优先使用原生 StoreKit 插件（如果可用）
   - 购买成功后，调用后端 API `/api/subscription/verify-receipt` 验证收据
   - 如果原生插件不可用，降级到后端支付 API
3. **恢复购买**：
   - 优先使用原生 StoreKit 插件（如果可用）
   - 恢复成功后，验证所有收据
   - 如果原生插件不可用，从后端获取订阅历史

### Web 购买流程

1. **获取产品列表**：调用后端 API `/api/subscription/products`
2. **购买**：调用后端 API `/api/subscription/purchase` 创建支付订单，跳转到支付页面
3. **恢复购买**：调用后端 API `/api/subscription/history` 获取订阅历史

---

## 后端 API 端点

### 1. 获取产品列表

**端点**：`GET /api/subscription/products`

**响应**：
```json
{
    "products": [
        {
            "id": "basic_monthly",
            "type": "subscription",
            "displayName": "基础版（月付）",
            "description": "公测期特价：4.8元/月，每月20次下载",
            "price": 4.80,
            "displayPrice": "¥4.80/月",
            "credits": 20,
            "period": "monthly"
        },
        {
            "id": "premium_monthly",
            "type": "subscription",
            "displayName": "高级版（月付）",
            "description": "公测期特价：19.9元/月，每月100次下载",
            "price": 19.90,
            "displayPrice": "¥19.90/月",
            "credits": 100,
            "period": "monthly"
        },
        {
            "id": "pack_10",
            "type": "purchase",
            "displayName": "10次下载包",
            "description": "一次性购买10次下载，永久有效",
            "price": 5.00,
            "displayPrice": "¥5.00",
            "credits": 10,
            "period": null
        },
        {
            "id": "pack_20",
            "type": "purchase",
            "displayName": "20次下载包",
            "description": "一次性购买20次下载，永久有效",
            "price": 9.00,
            "displayPrice": "¥9.00",
            "credits": 20,
            "period": null
        }
    ],
    "count": 4
}
```

### 2. 获取订阅状态

**端点**：`GET /api/subscription/status`

**请求头**：`Authorization: Bearer <token>`

**响应**：
```json
{
    "hasActiveSubscription": true,
    "subscription": {
        "type": "basic_monthly",
        "status": "active",
        "start_date": "2025-01-01T00:00:00Z",
        "end_date": "2025-02-01T00:00:00Z",
        "auto_renew": true
    },
    "download_credits": {
        "subscription": {
            "used": 12,
            "total": 20,
            "remaining": 8
        },
        "purchase": {
            "used": 0,
            "total": 0,
            "remaining": 0
        }
    }
}
```

### 3. 创建支付订单（Web）

**端点**：`POST /api/subscription/purchase`

**请求头**：`Authorization: Bearer <token>`

**请求体**：
```
product_id=basic_monthly&payment_method=wechat
```

**响应**：
```json
{
    "order_id": "order_123456",
    "payment_url": "https://pay.wechat.com/...",
    "product_id": "basic_monthly"
}
```

### 4. 验证 iOS 收据

**端点**：`POST /api/subscription/verify-receipt`

**请求头**：`Authorization: Bearer <token>`

**请求体**：
```
receipt_data=<base64_receipt>&product_id=basic_monthly
```

**响应**：
```json
{
    "verified": true,
    "subscription": {
        "type": "basic_monthly",
        "status": "active",
        "end_date": "2025-02-01T00:00:00Z"
    }
}
```

### 5. 获取订阅历史

**端点**：`GET /api/subscription/history?page=1&limit=100`

**请求头**：`Authorization: Bearer <token>`

**响应**：
```json
{
    "subscriptions": [
        {
            "id": 1,
            "subscription_type": "basic_monthly",
            "status": "active",
            "start_date": "2025-01-01T00:00:00Z",
            "end_date": "2025-02-01T00:00:00Z",
            "auto_renew": true,
            "platform": "ios",
            "transaction_id": "1000000123456789"
        }
    ],
    "total": 1,
    "page": 1,
    "limit": 100
}
```

---

## 前端实现

### 主要修改

1. **`getAvailableProducts()`**：
   - 改为调用后端 API `/api/subscription/products`
   - 不再依赖原生插件

2. **`purchase(productId)`**：
   - iOS App：优先使用原生 StoreKit 插件，购买成功后验证收据
   - 如果原生插件不可用，降级到后端支付 API
   - Web：直接使用后端支付 API

3. **`restorePurchases()`**：
   - iOS App：优先使用原生 StoreKit 插件，恢复成功后验证收据
   - 如果原生插件不可用，从后端获取订阅历史
   - Web：从后端获取订阅历史

4. **`checkAvailability()`**：
   - 现在所有平台都返回可用（通过后端 API）

5. **`getSubscriptionStatus()`**：
   - 统一使用后端 API `/api/subscription/status`

### 代码位置

- **前端订阅服务**：`web_service/frontend/subscription.js`
- **后端 API**：`web_service/backend/main.py`

---

## 优势

1. **不依赖原生插件**：解决了 Capacitor 8 插件注册问题
2. **跨平台统一**：iOS App 和 Web 使用相同的后端 API
3. **降级策略**：iOS App 优先使用原生插件，失败时自动降级到后端 API
4. **易于维护**：所有订阅逻辑集中在后端，前端只需调用 API

---

## 测试步骤

### 1. 获取产品列表

在浏览器控制台或 Safari Web Inspector 中执行：
```javascript
const products = await subscriptionService.getAvailableProducts();
console.log('产品列表:', products);
```

### 2. 查询订阅状态

```javascript
const status = await subscriptionService.getSubscriptionStatus();
console.log('订阅状态:', status);
```

### 3. 购买（Web）

```javascript
// 需要先登录
const result = await subscriptionService.purchase('basic_monthly');
console.log('购买结果:', result);
```

### 4. 恢复购买

```javascript
const result = await subscriptionService.restorePurchases();
console.log('恢复购买结果:', result);
```

---

## 注意事项

1. **iOS App 原生插件**：
   - 如果原生插件可用，会优先使用原生 StoreKit
   - 如果原生插件不可用，会自动降级到后端 API
   - 这样可以在插件问题解决后无缝切换

2. **用户认证**：
   - 所有需要认证的 API 都需要 `Authorization: Bearer <token>` 请求头
   - Token 存储在 `localStorage`（Web）或 `Capacitor Preferences`（iOS App）

3. **API 基础 URL**：
   - iOS App：`https://beatsync.site`
   - Web：根据当前域名自动判断
   - 本地开发：`http://localhost:8000`

---

## 后续优化

1. **iOS App 原生插件修复后**：
   - 可以完全使用原生 StoreKit，提供更好的用户体验
   - 后端 API 作为降级方案保留

2. **支付方式扩展**：
   - 可以添加更多支付方式（支付宝、Stripe 等）
   - 后端 API 已经支持多种支付方式

3. **错误处理**：
   - 可以添加更详细的错误处理和用户提示
   - 可以添加重试机制

---

**更新时间**：2025-12-13  
**状态**：✅ 已完成

















