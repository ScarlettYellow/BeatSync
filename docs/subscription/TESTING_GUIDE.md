# 订阅功能测试指南

## 概述

本指南将帮助您测试使用后端 API 实现的订阅功能。现在订阅功能不再依赖原生插件，可以在 iOS App 和 Web 端都正常工作。

---

## 测试前准备

### 1. 确保后端服务运行

```bash
# 检查后端服务是否运行
curl https://beatsync.site/api/health

# 应该返回：
# {"status":"healthy","timestamp":"..."}
```

### 2. 确保订阅系统已启用

后端需要设置环境变量：
```bash
export SUBSCRIPTION_ENABLED=true
export SUBSCRIPTION_DB_PATH=./subscription.db
```

### 3. 同步 Capacitor 项目

```bash
cd /Users/scarlett/Projects/BeatSync
npx cap sync ios
```

---

## iOS App 测试

### 步骤 1：重新构建并运行 App

1. 在 Xcode 中打开项目：
   ```bash
   npx cap open ios
   ```

2. 清理构建：
   - `Product` → `Clean Build Folder` (Shift + Command + K)

3. 重新构建并运行：
   - 选择目标设备（您的 iPhone）
   - 点击运行按钮 (Command + R)

### 步骤 2：打开 Safari Web Inspector

1. 在 Mac 上打开 Safari
2. `开发` → `[您的 iPhone]` → `BeatSync` → `localhost`
3. 打开 Console 标签

### 步骤 3：测试获取产品列表

在 Safari Web Inspector 控制台中执行：

```javascript
// 测试获取产品列表
subscriptionService.getAvailableProducts().then(products => {
    console.log('✅ 产品列表:', products);
}).catch(error => {
    console.error('❌ 获取产品列表失败:', error);
});
```

**预期结果**：
- ✅ 应该返回包含 4 个产品的数组：
  - `basic_monthly` - 基础版（月付）
  - `premium_monthly` - 高级版（月付）
  - `pack_10` - 10次下载包
  - `pack_20` - 20次下载包

### 步骤 4：测试查询订阅状态

```javascript
// 测试查询订阅状态（需要先登录）
subscriptionService.getSubscriptionStatus().then(status => {
    console.log('✅ 订阅状态:', status);
}).catch(error => {
    console.error('❌ 查询订阅状态失败:', error);
});
```

**预期结果**：
- ✅ 如果未登录，返回 `{ hasActiveSubscription: false, message: '未登录' }`
- ✅ 如果已登录，返回订阅详情

### 步骤 5：测试恢复购买

```javascript
// 测试恢复购买
subscriptionService.restorePurchases().then(result => {
    console.log('✅ 恢复购买结果:', result);
}).catch(error => {
    console.error('❌ 恢复购买失败:', error);
});
```

**预期结果**：
- ✅ 如果原生插件可用，会尝试使用原生 StoreKit 恢复
- ✅ 如果原生插件不可用，会从后端获取订阅历史
- ✅ 返回订阅历史列表

### 步骤 6：测试购买功能（可选）

**注意**：购买功能需要真实的支付流程，建议在测试环境中谨慎测试。

```javascript
// 测试购买（需要先登录）
subscriptionService.purchase('basic_monthly').then(result => {
    console.log('✅ 购买结果:', result);
}).catch(error => {
    console.error('❌ 购买失败:', error);
});
```

**预期结果**：
- ✅ iOS App：如果原生插件可用，会调用原生 StoreKit 购买界面
- ✅ iOS App：如果原生插件不可用，会跳转到后端支付页面
- ✅ Web：会跳转到后端支付页面

---

## Web 端测试

### 步骤 1：打开前端页面

访问：`https://scarlettyellow.github.io/BeatSync/` 或本地开发服务器

### 步骤 2：打开浏览器控制台

按 `F12` 或 `Cmd + Option + I` 打开开发者工具

### 步骤 3：测试获取产品列表

```javascript
subscriptionService.getAvailableProducts().then(products => {
    console.log('✅ 产品列表:', products);
}).catch(error => {
    console.error('❌ 获取产品列表失败:', error);
});
```

### 步骤 4：测试订阅功能

在页面上：
1. 查看订阅管理区域是否显示
2. 点击"查看订阅套餐"按钮
3. 应该能看到产品列表

---

## 常见问题排查

### 问题 1：产品列表为空

**可能原因**：
- 后端 API 未正确返回产品列表
- 网络连接问题

**解决方法**：
```javascript
// 检查 API 是否可访问
fetch('https://beatsync.site/api/subscription/products')
    .then(r => r.json())
    .then(data => console.log('API 响应:', data))
    .catch(err => console.error('API 错误:', err));
```

### 问题 2：订阅状态查询失败

**可能原因**：
- 用户未登录
- Token 无效或过期

**解决方法**：
```javascript
// 检查 Token
subscriptionService.getUserToken().then(token => {
    console.log('Token:', token ? '存在' : '不存在');
});
```

### 问题 3：购买功能不工作

**可能原因**：
- 原生插件不可用（iOS App）
- 后端支付 API 未配置

**解决方法**：
- iOS App：检查控制台日志，看是否降级到后端 API
- Web：检查后端支付配置

---

## 测试检查清单

### iOS App 测试

- [ ] App 可以正常构建和运行
- [ ] 订阅管理区域显示正常
- [ ] 可以获取产品列表（4 个产品）
- [ ] 可以查询订阅状态
- [ ] 可以恢复购买（从后端获取历史）
- [ ] 购买功能可以正常工作（或降级到后端 API）

### Web 端测试

- [ ] 订阅管理区域显示正常
- [ ] 可以获取产品列表
- [ ] 可以查询订阅状态
- [ ] 可以创建支付订单（跳转到支付页面）

### 后端 API 测试

- [ ] `/api/subscription/products` 返回产品列表
- [ ] `/api/subscription/status` 返回订阅状态
- [ ] `/api/subscription/history` 返回订阅历史
- [ ] `/api/subscription/purchase` 创建支付订单
- [ ] `/api/subscription/verify-receipt` 验证收据

---

## 预期行为

### iOS App

1. **获取产品列表**：
   - ✅ 调用后端 API `/api/subscription/products`
   - ✅ 返回 4 个产品

2. **购买**：
   - ✅ 优先尝试使用原生 StoreKit 插件
   - ✅ 如果插件不可用，自动降级到后端支付 API
   - ✅ 购买成功后验证收据

3. **恢复购买**：
   - ✅ 优先尝试使用原生 StoreKit 插件
   - ✅ 如果插件不可用，从后端获取订阅历史

4. **查询状态**：
   - ✅ 统一使用后端 API `/api/subscription/status`

### Web 端

1. **所有功能都通过后端 API 实现**
2. **不依赖任何原生插件**

---

## 成功标准

✅ **测试通过的标准**：
1. 可以成功获取产品列表
2. 可以成功查询订阅状态
3. 可以成功恢复购买（从后端获取历史）
4. 购买功能可以正常工作（或正确降级到后端 API）
5. 不再出现"订阅插件未加载"错误

---

**请按照上述步骤进行测试，并告诉我测试结果！** 🚀
