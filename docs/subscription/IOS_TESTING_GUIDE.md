# iOS App 订阅系统集成测试指南

## 概述

本指南说明如何在 iOS App 中测试订阅系统，包括本地测试（无需 App Store Connect）和沙盒测试（需要 App Store Connect）。

---

## 测试方案

### 方案 1：本地测试（推荐先做）✅

**无需 App Store Connect，可以立即开始**

使用 StoreKit Configuration File 进行本地测试。

### 方案 2：沙盒测试（完整测试）⏳

**需要 App Store Connect，等待审核通过后**

使用 App Store Connect 沙盒环境进行完整测试。

---

## 阶段 1：本地测试（立即开始）

### 步骤 1：在 Xcode 中启用 StoreKit Testing

1. **打开项目**
   ```bash
   cd ios/App
   npx cap open ios
   ```

2. **配置 Scheme**
   - 在 Xcode 顶部，点击 Scheme（项目名称旁边）
   - 选择 **Edit Scheme...**
   - 在左侧选择 **Run**
   - 切换到 **Options** 标签
   - 在 **StoreKit Configuration** 下拉菜单中选择 `Products.storekit`
   - 点击 **Close** 保存

3. **验证配置**
   - 确保 `Products.storekit` 文件在项目中可见
   - 文件位置：`ios/App/Products.storekit`

### 步骤 2：运行 App 并测试

1. **运行 App**
   - 在 Xcode 中选择目标设备（模拟器或真机）
   - 点击 **Run** 按钮（或按 `Cmd + R`）
   - 等待 App 启动

2. **打开订阅管理**
   - 在 App 中找到"订阅管理"区域
   - 点击"查看订阅套餐"按钮

3. **测试产品列表获取**
   - 应该能看到 7 个产品：
     - 4 个订阅：基础版月付/年付、高级版月付/年付
     - 3 个购买包：10次、50次、100次
   - 检查产品信息是否正确显示

4. **测试购买流程**
   - 点击任意产品的"购买"按钮
   - 应该弹出 StoreKit 购买界面（本地模拟）
   - 点击"购买"完成购买（无需真实支付）
   - 检查订阅状态是否更新

5. **测试订阅状态查询**
   - 查看订阅状态卡片
   - 应该显示：
     - 订阅状态（已订阅/未订阅）
     - 下载次数信息
     - 免费试用信息

6. **测试恢复购买**
   - 点击"恢复购买"按钮
   - 应该显示恢复结果

### 步骤 3：检查控制台日志

在 Xcode 控制台中查看日志：

1. **打开控制台**
   - 在 Xcode 底部打开控制台窗口
   - 或按 `Cmd + Shift + Y`

2. **查看日志**
   - 查找订阅相关的日志
   - 检查是否有错误信息
   - 验证 API 调用是否成功

### 步骤 4：测试后端集成（可选）

如果需要测试后端集成：

1. **确保后端服务运行**
   ```bash
   cd web_service/backend
   export SUBSCRIPTION_ENABLED=true
   python main.py
   ```

2. **测试收据验证**
   - 在 App 中完成购买
   - 检查后端日志，看是否收到收据验证请求
   - 检查数据库，看订阅是否保存

---

## 阶段 2：沙盒测试（等待审核通过后）

### 前置条件

- ✅ Apple Developer Program 审核通过
- ✅ 可以登录 App Store Connect

### 步骤 1：配置 App Store Connect

1. **创建 App 内购买产品**
   - 登录 [App Store Connect](https://appstoreconnect.apple.com)
   - 选择你的 App
   - 进入 **"功能"** → **"App 内购买项目"**
   - 创建 7 个产品（与 `Products.storekit` 中的产品 ID 一致）

2. **获取 App Store 共享密钥**
   - 在 App Store Connect 中
   - 进入 **"用户和访问"** → **"密钥"**
   - 创建或查看 **App Store 共享密钥**

3. **创建沙盒测试账号**
   - 在 App Store Connect 中
   - 进入 **"用户和访问"** → **"沙盒测试员"**
   - 创建测试账号

### 步骤 2：配置后端

1. **设置环境变量**
   ```bash
   export SUBSCRIPTION_ENABLED=true
   export APP_STORE_SHARED_SECRET=your_shared_secret_here
   export ADMIN_TOKEN=your_admin_token
   export JWT_SECRET_KEY=your_jwt_secret
   ```

2. **重启后端服务**
   ```bash
   cd web_service/backend
   python main.py
   ```

### 步骤 3：在设备上登录沙盒账号

1. **在 iOS 设备上**
   - 进入 **设置** → **App Store**
   - 滚动到底部
   - 点击 **"沙盒账号"**
   - 登录你创建的沙盒测试账号

2. **退出当前 App Store 账号**（如果已登录）
   - 在 **设置** → **App Store** 中
   - 退出当前账号（沙盒测试需要单独的账号）

### 步骤 4：测试完整流程

1. **测试产品列表获取**
   - 运行 App
   - 打开订阅管理
   - 验证产品列表是否正确加载

2. **测试购买流程**
   - 选择产品并购买
   - 使用沙盒账号完成购买
   - 验证购买是否成功

3. **测试收据验证**
   - 检查后端日志
   - 验证收据是否发送到后端
   - 验证收据验证是否成功

4. **测试订阅状态更新**
   - 查询订阅状态
   - 验证订阅信息是否正确
   - 验证下载次数是否正确增加

5. **测试下载次数消费**
   - 处理并下载视频
   - 验证下载次数是否正确扣除
   - 验证下载记录是否正确保存

---

## 测试检查清单

### 本地测试检查清单

- [ ] StoreKit Configuration File 已添加到项目
- [ ] 在 Xcode Scheme 中启用了 StoreKit Testing
- [ ] App 可以正常启动
- [ ] 订阅管理界面可以显示
- [ ] 产品列表可以正确加载（7 个产品）
- [ ] 购买流程可以正常进行
- [ ] 订阅状态可以正确查询
- [ ] 恢复购买功能可以正常工作
- [ ] 控制台没有错误日志

### 沙盒测试检查清单

- [ ] Apple Developer Program 审核通过
- [ ] 在 App Store Connect 中创建了产品
- [ ] 获取了 App Store 共享密钥
- [ ] 创建了沙盒测试账号
- [ ] 在设备上登录了沙盒账号
- [ ] 后端环境变量已配置
- [ ] 后端服务已重启
- [ ] 产品列表可以正确加载
- [ ] 购买流程可以正常进行
- [ ] 收据验证可以正常工作
- [ ] 订阅状态可以正确更新
- [ ] 下载次数可以正确消费

---

## 常见问题

### Q1: 产品列表为空

**可能原因**：
- StoreKit Configuration File 未正确配置
- 产品 ID 不匹配

**解决方法**：
1. 检查 `Products.storekit` 文件是否在项目中
2. 检查 Scheme 中是否选择了正确的 StoreKit Configuration
3. 检查产品 ID 是否与代码中的一致

### Q2: 购买失败

**可能原因**：
- StoreKit 未正确初始化
- 产品 ID 不存在

**解决方法**：
1. 检查控制台日志
2. 验证产品 ID 是否正确
3. 检查 SubscriptionPlugin 是否正确注册

### Q3: 订阅状态不更新

**可能原因**：
- 后端服务未运行
- 收据验证失败
- 数据库连接失败

**解决方法**：
1. 检查后端服务是否运行
2. 检查后端日志
3. 检查数据库连接

### Q4: 收据验证失败

**可能原因**：
- App Store 共享密钥未配置
- 收据格式错误
- 网络连接问题

**解决方法**：
1. 检查 `APP_STORE_SHARED_SECRET` 环境变量
2. 检查收据数据格式
3. 检查网络连接

---

## 测试脚本

### 快速测试脚本

可以在 App 的 JavaScript 控制台中运行：

```javascript
// 测试订阅可用性
subscriptionService.checkAvailability().then(console.log);

// 测试获取产品列表
subscriptionService.getAvailableProducts().then(console.log);

// 测试订阅状态
subscriptionService.getSubscriptionStatus().then(console.log);

// 测试购买（需要用户交互）
// subscriptionService.purchase('basic_monthly').then(console.log);
```

---

## 下一步

### 本地测试完成后

1. ✅ 验证基本功能正常
2. ✅ 修复发现的问题
3. ⏳ 等待 Apple Developer Program 审核通过
4. ⏳ 进行沙盒测试
5. ⏳ 进行完整功能测试

---

**最后更新**: 2025-12-25
