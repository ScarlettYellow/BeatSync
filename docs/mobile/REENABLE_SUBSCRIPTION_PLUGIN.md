# 重新启用 SubscriptionPlugin 以支持 iOS 内购

## 背景

`SubscriptionPlugin` 之前被临时禁用是为了解决 iOS App 启动崩溃（SIGKILL）问题。现在 App 已经可以正常启动，需要重新启用插件以支持 iOS 内购功能。

## 当前状态

- ✅ App 可以正常启动（不再崩溃）
- ❌ `SubscriptionPlugin` 被禁用（`.m` 文件中的注册代码被注释）
- ❌ `SubscriptionPlugin.swift` 文件被重命名为 `.disabled`
- ❌ iOS 内购功能不可用，降级到 Web 支付

## 重新启用步骤

### 步骤1：恢复 SubscriptionPlugin.swift 文件

```bash
cd ios/App
mv SubscriptionPlugin.swift.disabled SubscriptionPlugin.swift
```

### 步骤2：取消注释 SubscriptionPlugin.m 中的注册代码

编辑 `ios/App/SubscriptionPlugin.m`，取消注释：

```objc
#import <Capacitor/Capacitor.h>

CAP_PLUGIN(SubscriptionPlugin, "SubscriptionPlugin",
           CAP_PLUGIN_METHOD(checkSubscriptionAvailability, CAPPluginReturnPromise);
           CAP_PLUGIN_METHOD(getAvailableProducts, CAPPluginReturnPromise);
           CAP_PLUGIN_METHOD(purchase, CAPPluginReturnPromise);
           CAP_PLUGIN_METHOD(getSubscriptionStatus, CAPPluginReturnPromise);
           CAP_PLUGIN_METHOD(restorePurchases, CAPPluginReturnPromise);
)
```

### 步骤3：检查并修复编译错误

在 Xcode 中：
1. 打开项目
2. 清理构建（Product → Clean Build Folder，Shift+Cmd+K）
3. 尝试编译（Cmd+B）
4. 检查是否有编译错误

**可能的问题**：
- StoreKit 2 需要 iOS 15.0+，检查 Deployment Target
- 需要导入 `StoreKit` 框架
- 检查 `productIds` 配置是否正确

### 步骤4：同步 Capacitor

```bash
cd /Users/scarlett/Projects/BeatSync
npx cap sync ios
```

### 步骤5：在 Xcode 中测试

1. 打开 Xcode 项目
2. 选择真机或模拟器（iOS 15.0+）
3. 运行 App
4. 检查控制台日志，确认插件已加载

### 步骤6：测试 iOS 内购

1. 在 App 中点击"查看订阅套餐"
2. 点击"购买"按钮
3. 应该弹出 iOS 内购界面（而不是显示错误消息）

## 注意事项

### 1. StoreKit 2 要求

- **最低 iOS 版本**：iOS 15.0+
- **Xcode 版本**：Xcode 13.0+
- **产品配置**：需要在 App Store Connect 中配置产品

### 2. 产品 ID 配置

`SubscriptionPlugin` 中定义的产品 ID：
- `basic_monthly`: `com.beatsync.public_beta.subscription.basic.monthly`
- `premium_monthly`: `com.beatsync.public_beta.subscription.premium.monthly`
- `pack_10`: `com.beatsync.public_beta.subscription.pack.10`
- `pack_20`: `com.beatsync.public_beta.subscription.pack.20`

这些产品 ID 需要在 App Store Connect 中配置。

### 3. 测试环境

- **沙盒测试**：使用沙盒测试账号测试内购
- **StoreKit Configuration**：可以在 Xcode 中使用本地 StoreKit 配置文件测试

### 4. 如果仍然崩溃

如果重新启用后 App 再次崩溃：

1. **检查崩溃日志**：查看 Xcode 控制台的详细错误信息
2. **逐步启用**：先只启用 `SubscriptionPlugin`，不启用 `SaveToGalleryPlugin`
3. **检查依赖**：确保所有 StoreKit 相关的依赖都正确导入

## 验证清单

- [ ] `SubscriptionPlugin.swift` 文件已恢复
- [ ] `SubscriptionPlugin.m` 中的注册代码已取消注释
- [ ] Xcode 项目可以正常编译
- [ ] App 可以正常启动
- [ ] 插件在控制台日志中可见
- [ ] 点击"购买"按钮时弹出 iOS 内购界面
- [ ] 购买流程可以正常完成

## 相关文件

- `ios/App/SubscriptionPlugin.swift` - 插件实现
- `ios/App/SubscriptionPlugin.m` - 插件注册
- `web_service/frontend/subscription.js` - 前端订阅服务
- `ios/App/Products.storekit` - StoreKit 配置文件（如果存在）

