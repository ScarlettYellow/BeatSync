# iOS App StoreKit 2 集成指南

## 概述

本文档说明如何在 BeatSync iOS App 中集成 StoreKit 2 订阅系统。

## 架构设计

### 组件

1. **SubscriptionPlugin.swift** - Capacitor 插件，封装 StoreKit 2 API
2. **subscription.js** - 前端 JavaScript 接口
3. **subscription_receipt_verification.py** - 后端收据验证服务
4. **后端 API** - `/api/subscription/verify-receipt` - 收据验证端点

### 数据流

```
iOS App (StoreKit 2)
    ↓ 购买订阅
SubscriptionPlugin.swift
    ↓ 获取 Transaction
    ↓ 编码为 JSON
前端 JavaScript (subscription.js)
    ↓ 调用后端 API
后端 API (/api/subscription/verify-receipt)
    ↓ 验证并保存
数据库 (subscriptions, download_credits)
```

## 实施步骤

### 1. 添加插件文件

已创建以下文件：
- `ios/App/Plugins/SubscriptionPlugin.swift` - 插件实现
- `ios/App/SubscriptionPlugin.m` - 插件注册

### 2. 注册插件到 Xcode 项目

需要在 Xcode 中手动添加文件：

1. 打开 `ios/App/App.xcodeproj`
2. 将 `SubscriptionPlugin.swift` 添加到项目
3. 将 `SubscriptionPlugin.m` 添加到项目
4. 确保文件被添加到正确的 Target

### 3. 配置产品ID

在 `SubscriptionPlugin.swift` 中配置产品ID：

```swift
private let productIds: [String: String] = [
    "basic_monthly": "com.beatsync.subscription.basic.monthly",
    "basic_yearly": "com.beatsync.subscription.basic.yearly",
    "premium_monthly": "com.beatsync.subscription.premium.monthly",
    "premium_yearly": "com.beatsync.subscription.premium.yearly",
    "pack_10": "com.beatsync.pack.10",
    "pack_20": "com.beatsync.pack.20",
    "pack_50": "com.beatsync.pack.50"
]
```

**重要**：这些产品ID必须在 App Store Connect 中配置。

### 4. 配置后端 API 地址

在 `SubscriptionPlugin.swift` 中配置后端 API 地址：

```swift
private var apiBaseURL: String {
    // 可以从 capacitor.config.json 读取
    return "http://localhost:8000"  // 开发环境
    // return "https://your-api-domain.com"  // 生产环境
}
```

### 5. 在 App Store Connect 中配置产品

1. 登录 [App Store Connect](https://appstoreconnect.apple.com)
2. 选择你的 App
3. 进入"功能" → "App 内购买项目"
4. 创建以下产品：

#### 订阅产品

- **基础版月付** (`com.beatsync.subscription.basic.monthly`)
  - 类型：自动续订订阅
  - 价格：15 CNY/月
  - 下载次数：50次/月

- **基础版年付** (`com.beatsync.subscription.basic.yearly`)
  - 类型：自动续订订阅
  - 价格：99 CNY/年
  - 下载次数：600次/年

- **高级版月付** (`com.beatsync.subscription.premium.monthly`)
  - 类型：自动续订订阅
  - 价格：69 CNY/月
  - 下载次数：1000次/月

- **高级版年付** (`com.beatsync.subscription.premium.yearly`)
  - 类型：自动续订订阅
  - 价格：499 CNY/年
  - 下载次数：12000次/年

#### 一次性购买

- **10次下载包** (`com.beatsync.pack.10`)
  - 类型：非消耗型产品
  - 价格：5 CNY

- **20次下载包** (`com.beatsync.pack.20`)
  - 类型：非消耗型产品
  - 价格：9 CNY

- **50次下载包** (`com.beatsync.pack.50`)
  - 类型：非消耗型产品
  - 价格：20 CNY

### 6. 配置环境变量

在后端服务器配置：

```bash
# .env 文件
SUBSCRIPTION_ENABLED=true
APP_STORE_SHARED_SECRET=your_shared_secret_here
ADMIN_TOKEN=your_admin_token
JWT_SECRET_KEY=your_jwt_secret
```

### 7. 前端集成

在 `index.html` 中引入订阅服务：

```html
<script src="subscription.js"></script>
```

在 `script.js` 中使用：

```javascript
// 检查订阅可用性
const availability = await subscriptionService.checkAvailability();

// 获取可用产品
const products = await subscriptionService.getAvailableProducts();

// 购买订阅
const result = await subscriptionService.purchase('basic_monthly');

// 查询订阅状态
const status = await subscriptionService.getSubscriptionStatus();

// 恢复购买
const restoreResult = await subscriptionService.restorePurchases();
```

## API 参考

### SubscriptionPlugin 方法

#### checkSubscriptionAvailability()
检查设备是否支持应用内购买。

**返回**：
```json
{
  "available": true,
  "message": "设备支持应用内购买"
}
```

#### getAvailableProducts()
获取所有可用的订阅产品。

**返回**：
```json
{
  "products": [
    {
      "id": "com.beatsync.subscription.basic.monthly",
      "type": "basic_monthly",
      "displayName": "基础版月付",
      "description": "每月50次下载",
      "price": "15.00",
      "priceLocale": "zh_CN"
    }
  ],
  "count": 7
}
```

#### purchase(productId)
购买订阅或产品。

**参数**：
- `productId`: 产品ID（如 'basic_monthly'）

**返回**：
```json
{
  "success": true,
  "transactionId": "1234567890",
  "productId": "basic_monthly",
  "message": "购买成功并已验证"
}
```

#### getSubscriptionStatus()
查询当前订阅状态。

**返回**：
```json
{
  "localStatus": {
    "com.beatsync.subscription.basic.monthly": {
      "productID": "com.beatsync.subscription.basic.monthly",
      "purchaseDate": "2025-01-20T10:00:00Z",
      "expirationDate": "2025-02-20T10:00:00Z",
      "isActive": true
    }
  },
  "backendStatus": {
    "is_whitelisted": false,
    "subscription": {...},
    "download_credits": {
      "total": 50,
      "remaining": 45
    }
  },
  "hasActiveSubscription": true
}
```

#### restorePurchases()
恢复之前的购买。

**返回**：
```json
{
  "success": true,
  "restoredProducts": [
    "com.beatsync.subscription.basic.monthly"
  ],
  "count": 1
}
```

## 测试

### 沙盒测试

1. 在 App Store Connect 中创建沙盒测试账号
2. 在设备上登录沙盒测试账号（设置 → App Store → 沙盒账号）
3. 运行 App 并测试购买流程

### 测试检查清单

- [ ] 产品列表加载正常
- [ ] 购买流程正常
- [ ] 收据验证成功
- [ ] 订阅状态查询正常
- [ ] 恢复购买功能正常
- [ ] 下载次数正确增加
- [ ] 订阅过期后正确处理

## 常见问题

### 1. 产品列表为空

**原因**：
- 产品ID未在 App Store Connect 中配置
- 产品状态不是"准备提交"

**解决**：
- 检查 App Store Connect 中的产品配置
- 确保产品状态正确

### 2. 购买失败

**原因**：
- 未登录沙盒测试账号
- 网络问题
- 产品ID错误

**解决**：
- 确保已登录沙盒测试账号
- 检查网络连接
- 验证产品ID是否正确

### 3. 收据验证失败

**原因**：
- 后端 API 地址配置错误
- 用户未登录
- 收据数据格式错误

**解决**：
- 检查 API 地址配置
- 确保用户已登录并获取 Token
- 检查收据数据格式

## 注意事项

1. **StoreKit 2 要求 iOS 15+**
2. **产品ID必须在 App Store Connect 中配置**
3. **测试时需要使用沙盒测试账号**
4. **生产环境需要配置正确的 API 地址**
5. **收据验证需要 App Store 共享密钥**

## 下一步

1. 在 App Store Connect 中配置产品
2. 测试购买流程
3. 集成到前端 UI
4. 处理订阅状态更新
5. 实现订阅管理界面

## 相关文档

- [StoreKit 2 文档](https://developer.apple.com/documentation/storekit)
- [App Store Connect 指南](https://developer.apple.com/app-store-connect/)
- [Capacitor 插件开发](https://capacitorjs.com/docs/plugins)

