# iOS StoreKit 集成 - 下一步行动指南

## ✅ 已完成

1. ✅ 创建 SubscriptionPlugin.swift 和 SubscriptionPlugin.m
2. ✅ 修复编译错误（priceLocale → displayPrice）
3. ✅ 文件已添加到 Xcode 项目
4. ✅ 构建成功
5. ✅ 警告隐藏设置完成
6. ✅ 创建 StoreKit Configuration File（本地测试用）

## 📋 下一步行动清单

### 阶段 0：本地测试（无需 App Store Connect）✅ 可以立即开始

#### 0.1 配置 StoreKit Configuration File

1. **在 Xcode 中启用 StoreKit Testing**
   - 打开项目：`npx cap open ios`
   - **Product** → **Scheme** → **Edit Scheme**
   - 选择 **Run** → **Options**
   - 在 **StoreKit Configuration** 中选择 `Products.storekit`
   - 点击 **Close** 保存

2. **运行本地测试**
   - 在 Xcode 中运行 App（模拟器或真机）
   - StoreKit 会使用本地配置文件
   - 可以测试购买流程（无需真实支付）
   - 可以测试订阅状态查询

**测试范围**：
- ✅ 产品列表获取
- ✅ 购买流程 UI
- ✅ 订阅状态查询
- ✅ 恢复购买流程
- ✅ 基本功能验证

**限制**：
- ⚠️ 不能测试真实的收据验证
- ⚠️ 不能测试订阅续费
- ⚠️ 不能测试后端收据验证 API

### 阶段 1：App Store Connect 配置（完整测试需要）

#### 1.1 创建 App 内购买产品

1. 登录 [App Store Connect](https://appstoreconnect.apple.com)
2. 选择你的 App
3. 进入 **"功能"** → **"App 内购买项目"**
4. 创建以下产品：

**订阅产品**（自动续订订阅）：
- `com.beatsync.subscription.basic.monthly`
  - 名称：基础版月付
  - 价格：15 CNY/月
  - 描述：每月50次高清下载
  
- `com.beatsync.subscription.basic.yearly`
  - 名称：基础版年付
  - 价格：99 CNY/年
  - 描述：每年600次高清下载
  
- `com.beatsync.subscription.premium.monthly`
  - 名称：高级版月付
  - 价格：69 CNY/月
  - 描述：每月1000次高清下载
  
- `com.beatsync.subscription.premium.yearly`
  - 名称：高级版年付
  - 价格：499 CNY/年
  - 描述：每年12000次高清下载

**一次性购买**（非消耗型产品）：
- `com.beatsync.pack.10` - 10次下载包（5 CNY）
- `com.beatsync.pack.20` - 20次下载包（9 CNY）
- `com.beatsync.pack.50` - 50次下载包（20 CNY）

#### 1.2 获取 App Store 共享密钥

1. 在 App Store Connect 中
2. 进入 **"用户和访问"** → **"密钥"**
3. 创建或查看 **App Store 共享密钥**
4. 保存密钥（用于后端验证）

#### 1.3 创建沙盒测试账号

1. 在 App Store Connect 中
2. 进入 **"用户和访问"** → **"沙盒测试员"**
3. 创建测试账号（用于测试购买）

### 阶段 2：后端配置

#### 2.1 配置环境变量

在后端服务器配置：

```bash
# .env 文件或环境变量
SUBSCRIPTION_ENABLED=true
APP_STORE_SHARED_SECRET=your_shared_secret_here
ADMIN_TOKEN=your_admin_token
JWT_SECRET_KEY=your_jwt_secret
```

#### 2.2 重启后端服务

```bash
cd web_service/backend
# 停止旧服务
pkill -f "python3 main.py"

# 启动新服务（带环境变量）
SUBSCRIPTION_ENABLED=true \
APP_STORE_SHARED_SECRET=your_shared_secret \
ADMIN_TOKEN=your_admin_token \
JWT_SECRET_KEY=your_jwt_secret \
python3 main.py
```

### 阶段 3：前端集成

#### 3.1 引入订阅服务

在 `web_service/frontend/index.html` 中添加：

```html
<script src="subscription.js"></script>
```

#### 3.2 在 script.js 中使用

示例代码：

```javascript
// 检查订阅可用性
async function checkSubscription() {
    if (isCapacitorNative && window.Capacitor?.Plugins?.SubscriptionPlugin) {
        try {
            const result = await subscriptionService.checkAvailability();
            console.log('订阅可用性:', result);
        } catch (error) {
            console.error('检查订阅失败:', error);
        }
    }
}

// 获取可用产品
async function loadProducts() {
    try {
        const products = await subscriptionService.getAvailableProducts();
        console.log('可用产品:', products);
        return products;
    } catch (error) {
        console.error('获取产品失败:', error);
    }
}

// 购买订阅
async function purchaseSubscription(productId) {
    try {
        const result = await subscriptionService.purchase(productId);
        console.log('购买成功:', result);
        // 刷新订阅状态
        await refreshSubscriptionStatus();
    } catch (error) {
        console.error('购买失败:', error);
    }
}

// 查询订阅状态
async function refreshSubscriptionStatus() {
    try {
        const status = await subscriptionService.getSubscriptionStatus();
        console.log('订阅状态:', status);
        return status;
    } catch (error) {
        console.error('查询状态失败:', error);
    }
}
```

### 阶段 4：测试

#### 4.1 在设备上登录沙盒测试账号

1. 在 iOS 设备上
2. 进入 **设置** → **App Store**
3. 滚动到底部，点击 **"沙盒账号"**
4. 登录你创建的沙盒测试账号

#### 4.2 测试购买流程

1. 运行 App
2. 调用 `getAvailableProducts()` 获取产品列表
3. 调用 `purchase('basic_monthly')` 测试购买
4. 使用沙盒账号完成购买
5. 验证收据是否成功发送到后端
6. 验证下载次数是否正确增加

#### 4.3 测试订阅状态查询

1. 调用 `getSubscriptionStatus()` 查询状态
2. 验证返回的订阅信息
3. 验证下载次数信息

### 阶段 5：UI 集成（可选）

#### 5.1 创建订阅界面

在 `index.html` 中添加订阅管理界面：

```html
<div id="subscription-section" style="display: none;">
    <h3>订阅管理</h3>
    <div id="subscription-status"></div>
    <div id="subscription-products"></div>
    <button id="restore-purchases-btn">恢复购买</button>
</div>
```

#### 5.2 实现订阅 UI 逻辑

在 `script.js` 中实现：
- 显示订阅状态
- 显示可用产品列表
- 购买按钮
- 恢复购买功能

## 🎯 优先级

### 立即可以开始（无需 App Store Connect）✅

1. **本地测试配置**
   - ✅ StoreKit Configuration File 已创建
   - ⏳ 在 Xcode 中启用 StoreKit Testing
   - ⏳ 测试基本购买流程
   - ⏳ 测试 UI 交互

2. **代码完善**
   - 完善订阅插件代码
   - 优化错误处理
   - 完善 UI 体验

### 高优先级（完整测试需要 App Store Connect）

1. **App Store Connect 配置**（等待审核通过后）
   - 创建产品
   - 获取共享密钥
   - 创建沙盒测试账号

2. **后端环境变量配置**
   - 设置 APP_STORE_SHARED_SECRET
   - 重启服务

3. **完整测试**
   - 测试产品列表获取
   - 测试购买流程
   - 测试真实收据验证

### 中优先级（建议完成）

4. **前端集成**
   - 引入 subscription.js
   - 实现订阅功能调用

5. **UI 集成**
   - 创建订阅界面
   - 实现订阅管理

### 低优先级（可选）

6. **优化和增强**
   - 订阅状态自动刷新
   - 订阅过期提醒
   - 订阅管理界面优化

## 📝 检查清单

### App Store Connect
- [ ] 创建 4 个订阅产品
- [ ] 创建 3 个一次性购买产品
- [ ] 获取 App Store 共享密钥
- [ ] 创建沙盒测试账号

### 后端配置
- [ ] 配置 APP_STORE_SHARED_SECRET
- [ ] 配置其他环境变量
- [ ] 重启服务并验证

### 前端集成
- [ ] 引入 subscription.js
- [ ] 实现订阅功能调用
- [ ] 测试基本功能

### 测试
- [ ] 在设备上登录沙盒账号
- [ ] 测试产品列表获取
- [ ] 测试购买流程
- [ ] 测试收据验证
- [ ] 测试订阅状态查询
- [ ] 测试恢复购买

## 🚀 立即开始

### 方案 1：本地测试（推荐先做）✅ 无需 App Store Connect

**可以立即开始**：

1. **在 Xcode 中启用 StoreKit Testing**
   - 打开项目：`npx cap open ios`
   - **Product** → **Scheme** → **Edit Scheme**
   - 选择 **Run** → **Options**
   - 在 **StoreKit Configuration** 中选择 `Products.storekit`
   - 点击 **Close** 保存

2. **运行测试**
   - 在 Xcode 中运行 App
   - 测试产品列表获取
   - 测试购买流程
   - 测试订阅状态查询

**优点**：
- ✅ 无需等待审核
- ✅ 可以立即开始测试
- ✅ 可以验证代码逻辑
- ✅ 可以测试 UI 流程

### 方案 2：沙盒测试（等待审核通过后）⏳ 需要 App Store Connect

**等待 Apple Developer Program 审核通过后**：

1. 登录 App Store Connect
2. 创建第一个产品（可以先创建一个测试产品）
3. 获取共享密钥
4. 创建沙盒测试账号

完成后，可以进行完整的收据验证测试！

## 📚 相关文档

- [IOS_STOREKIT_INTEGRATION.md](./IOS_STOREKIT_INTEGRATION.md) - 完整集成指南
- [IOS_STOREKIT_IMPLEMENTATION_STATUS.md](./IOS_STOREKIT_IMPLEMENTATION_STATUS.md) - 实施状态

