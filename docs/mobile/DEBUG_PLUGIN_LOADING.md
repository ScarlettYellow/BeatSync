# 调试 SubscriptionPlugin 加载问题

## 问题

App 可以正常启动，但点击购买套餐后仍然显示"购买失败：订单已创建，请在 iOS 内购中完成支付"。

这说明：
- ✅ SubscriptionPlugin 已重新启用（App 不再崩溃）
- ❌ Capacitor 仍然无法发现插件（前端代码降级到 Web 支付）

## 调试步骤

### 步骤1：检查浏览器控制台日志

在 App 中打开 Safari 调试器（或 Xcode 控制台），查找以下日志：

```
[订阅服务] 插件未找到，当前状态: {...}
[订阅服务] 所有可用插件: [...]
[订阅服务] 原生插件不可用，使用后端支付 API
```

如果看到这些日志，说明插件确实没有被 Capacitor 发现。

### 步骤2：检查插件注册

确认 `SubscriptionPlugin.m` 中的注册代码已取消注释：

```objc
CAP_PLUGIN(SubscriptionPlugin, "SubscriptionPlugin",
           CAP_PLUGIN_METHOD(checkSubscriptionAvailability, CAPPluginReturnPromise);
           CAP_PLUGIN_METHOD(getAvailableProducts, CAPPluginReturnPromise);
           CAP_PLUGIN_METHOD(purchase, CAPPluginReturnPromise);
           CAP_PLUGIN_METHOD(getSubscriptionStatus, CAPPluginReturnPromise);
           CAP_PLUGIN_METHOD(restorePurchases, CAPPluginReturnPromise);
)
```

### 步骤3：检查文件是否在编译目标中

在 Xcode 中：
1. 选择 `SubscriptionPlugin.swift`
2. 查看右侧 File Inspector（⌘⌥1）
3. 确认 "Target Membership" 中 "App" 已勾选

同样检查 `SubscriptionPlugin.m`。

### 步骤4：清理并重新编译

```bash
# 清理 Xcode DerivedData
rm -rf ~/Library/Developer/Xcode/DerivedData

# 在 Xcode 中：
# Product → Clean Build Folder (Shift+Cmd+K)
# Product → Build (Cmd+B)
```

### 步骤5：检查插件ID

确认插件ID正确：
- Swift 文件中：`getId()` 返回 `"SubscriptionPlugin"`
- .m 文件中：`CAP_PLUGIN(SubscriptionPlugin, "SubscriptionPlugin", ...)`

### 步骤6：添加调试日志

在 `SubscriptionPlugin.swift` 的 `init` 方法中添加日志：

```swift
public override init() {
    super.init()
    print("📱 SubscriptionPlugin 已初始化")
}
```

如果看到这个日志，说明插件类被加载了，但 Capacitor 可能无法发现它。

### 步骤7：检查 Capacitor 版本

确认 Capacitor 版本兼容性：
- Capacitor 8.0 使用新的插件注册机制
- 可能需要使用 `@objc` 标记所有方法

## 可能的问题和解决方案

### 问题1：插件注册方式不正确

Capacitor 8.0 可能需要不同的注册方式。检查是否有其他插件作为参考。

### 问题2：Swift 和 Objective-C 桥接问题

确保 Bridging Header 正确配置：
- `ios/App/App-Bridging-Header.h` 包含 `#import <Capacitor/Capacitor.h>`

### 问题3：插件方法签名不匹配

确保所有方法都使用 `@objc` 标记，并且参数类型正确。

### 问题4：需要重新同步 Capacitor

```bash
cd /Users/scarlett/Projects/BeatSync
npx cap sync ios
```

然后重新编译。

## 临时解决方案

如果插件仍然无法加载，可以：

1. **使用后端 API 作为临时方案**（当前状态）
2. **手动调用 StoreKit**：在前端直接使用 JavaScript 调用 StoreKit（需要额外的桥接）

## 验证清单

- [ ] 插件注册代码已取消注释
- [ ] 文件在编译目标中
- [ ] 已清理并重新编译
- [ ] 浏览器控制台显示插件已加载
- [ ] 点击购买时弹出 iOS 内购界面

