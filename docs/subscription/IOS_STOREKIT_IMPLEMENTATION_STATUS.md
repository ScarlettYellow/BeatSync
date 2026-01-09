# iOS StoreKit 2 集成实施状态

## 已完成 ✅

### 1. 插件实现 ✅
- ✅ **SubscriptionPlugin.swift** - StoreKit 2 插件实现
  - 产品查询 (`getAvailableProducts`)
  - 订阅购买 (`purchase`)
  - 订阅状态查询 (`getSubscriptionStatus`)
  - 恢复购买 (`restorePurchases`)
  - 订阅可用性检查 (`checkSubscriptionAvailability`)

### 2. 插件注册 ✅
- ✅ **SubscriptionPlugin.m** - Capacitor 插件注册文件
  - 已注册所有方法到 Capacitor

### 3. 前端接口 ✅
- ✅ **subscription.js** - 前端 JavaScript 接口
  - 封装所有订阅功能
  - 支持 iOS App 和 Web 环境
  - 自动降级到后端 API

### 4. 后端集成 ✅
- ✅ **subscription_receipt_verification.py** - 收据验证服务
  - iOS 收据验证逻辑
  - 订阅信息保存到数据库
  - 下载次数自动分配

- ✅ **后端 API** - `/api/subscription/verify-receipt`
  - 接收 iOS 收据数据
  - 验证并保存订阅
  - 返回验证结果

### 5. 文档 ✅
- ✅ **IOS_STOREKIT_INTEGRATION.md** - 完整集成指南
  - 架构设计
  - 实施步骤
  - API 参考
  - 测试指南

## 待完成 ⏳

### 1. Xcode 项目配置（需要手动完成）

#### 1.1 添加文件到 Xcode 项目
1. 打开 `ios/App/App.xcodeproj`
2. 将以下文件添加到项目：
   - `ios/App/Plugins/SubscriptionPlugin.swift`
   - `ios/App/SubscriptionPlugin.m`
3. 确保文件被添加到正确的 Target

#### 1.2 配置 Build Settings
- 确保 Swift 版本 >= 5.5
- 确保 iOS 部署目标 >= 15.0（StoreKit 2 要求）

### 2. App Store Connect 配置（需要手动完成）

#### 2.1 创建产品
需要在 App Store Connect 中创建以下产品：

**订阅产品**：
- `com.beatsync.subscription.basic.monthly` - 基础版月付（15 CNY/月，50次）
- `com.beatsync.subscription.basic.yearly` - 基础版年付（99 CNY/年，600次）
- `com.beatsync.subscription.premium.monthly` - 高级版月付（69 CNY/月，1000次）
- `com.beatsync.subscription.premium.yearly` - 高级版年付（499 CNY/年，12000次）

**一次性购买**：
- `com.beatsync.pack.10` - 10次下载包（5 CNY）
- `com.beatsync.pack.20` - 20次下载包（9 CNY）
- `com.beatsync.pack.50` - 50次下载包（20 CNY）

#### 2.2 获取共享密钥
1. 登录 App Store Connect
2. 进入"用户和访问" → "密钥"
3. 创建或查看 App Store 共享密钥
4. 配置到后端环境变量：`APP_STORE_SHARED_SECRET`

### 3. 环境变量配置

在后端服务器配置：

```bash
# .env 文件
SUBSCRIPTION_ENABLED=true
APP_STORE_SHARED_SECRET=your_shared_secret_here
ADMIN_TOKEN=your_admin_token
JWT_SECRET_KEY=your_jwt_secret
```

### 4. 前端集成（可选）

在 `index.html` 中引入：

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
```

### 5. 测试

#### 5.1 沙盒测试
1. 在 App Store Connect 中创建沙盒测试账号
2. 在设备上登录沙盒测试账号
3. 运行 App 并测试购买流程

#### 5.2 测试检查清单
- [ ] 产品列表加载正常
- [ ] 购买流程正常
- [ ] 收据验证成功
- [ ] 订阅状态查询正常
- [ ] 恢复购买功能正常
- [ ] 下载次数正确增加

## 文件清单

### iOS 文件
- `ios/App/Plugins/SubscriptionPlugin.swift` - 插件实现
- `ios/App/SubscriptionPlugin.m` - 插件注册

### 前端文件
- `web_service/frontend/subscription.js` - 前端接口

### 后端文件
- `web_service/backend/subscription_receipt_verification.py` - 收据验证
- `web_service/backend/main.py` - 已添加 `/api/subscription/verify-receipt` API

### 文档
- `docs/subscription/IOS_STOREKIT_INTEGRATION.md` - 集成指南
- `docs/subscription/IOS_STOREKIT_IMPLEMENTATION_STATUS.md` - 本文档

## 下一步

1. **Xcode 配置** - 添加文件到项目
2. **App Store Connect** - 创建产品
3. **环境变量** - 配置共享密钥
4. **测试** - 沙盒测试购买流程
5. **UI 集成** - 在前端添加订阅界面

## 注意事项

1. **StoreKit 2 要求 iOS 15+**
2. **产品ID必须在 App Store Connect 中配置**
3. **测试时需要使用沙盒测试账号**
4. **生产环境需要配置正确的 API 地址**
5. **收据验证需要 App Store 共享密钥**

## 技术细节

### StoreKit 2 vs StoreKit 1

本实现使用 **StoreKit 2**，优势：
- 更简单的 API
- 更好的异步支持
- 内置收据验证
- 更好的错误处理

### 收据验证流程

1. iOS App 购买订阅（StoreKit 2）
2. 获取 Transaction 对象
3. 编码为 JSON 并发送到后端
4. 后端验证并保存到数据库
5. 分配下载次数

### 数据库集成

订阅验证成功后，会自动：
- 创建 `subscriptions` 记录
- 创建 `download_credits` 记录
- 创建 `payment_records` 记录

## 支持

如有问题，请参考：
- [IOS_STOREKIT_INTEGRATION.md](./IOS_STOREKIT_INTEGRATION.md) - 详细集成指南
- [StoreKit 2 文档](https://developer.apple.com/documentation/storekit)
- [App Store Connect 指南](https://developer.apple.com/app-store-connect/)

