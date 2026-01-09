# 修复插件未注册问题

## 问题诊断

从控制台输出可以看到：
- ❌ `SubscriptionPlugin` 不在插件列表中
- ❌ 可用的插件只有：`["CapacitorHttp", "Console", "WebView", "CapacitorCookies", "SystemBars", "Camera", "Filesystem", "Share"]`
- ❌ 自定义插件（`SubscriptionPlugin` 和 `SaveToGalleryPlugin`）都没有被注册

**根本原因**：Capacitor 无法发现自定义插件，可能是 `CAP_PLUGIN` 宏没有正确工作。

---

## 解决方案

### 步骤 1：确认插件文件在 Xcode 项目中

1. **在 Xcode 中打开项目**
2. **检查文件是否在项目中**：
   - 在左侧导航栏中查找 `SubscriptionPlugin.swift` 和 `SubscriptionPlugin.m`
   - 如果文件是灰色的，说明它们没有被添加到项目中

3. **如果文件不在项目中，手动添加**：
   - 右键点击项目根目录
   - 选择 **"Add Files to App"**
   - 选择 `ios/App/SubscriptionPlugin.swift` 和 `ios/App/SubscriptionPlugin.m`
   - 确保勾选：
     - ✅ "Copy items if needed"
     - ✅ "Create groups"
     - ✅ Target: "App" 被勾选
   - 点击 **"Add"**

### 步骤 2：检查 Target Membership

1. **在 Xcode 中选择 `SubscriptionPlugin.swift` 文件**
2. **在右侧 Inspector 面板中，检查 "Target Membership"**
3. **确保 "App" target 被勾选**

### 步骤 3：检查 Bridging Header

1. **在 Xcode 中选择项目（最顶部的蓝色图标）**
2. **选择 "App" target**
3. **打开 "Build Settings" 标签**
4. **搜索 "Objective-C Bridging Header"**
5. **确认值为**：`App-Bridging-Header.h` 或 `$(SRCROOT)/App-Bridging-Header.h`

### 步骤 4：检查 Build Settings

1. **在 "Build Settings" 中搜索 "Defines Module"**
2. **确保 "Defines Module" 设置为 "Yes"**

### 步骤 5：清理并重新构建

1. **清理构建缓存**：
   - `Product` → `Clean Build Folder`（`⌘ + Shift + K`）

2. **删除 DerivedData**（可选但推荐）：
   ```bash
   rm -rf ~/Library/Developer/Xcode/DerivedData
   ```

3. **重新构建项目**：
   - `Product` → `Build`（`⌘ + B`）

4. **重新运行 App**：
   - `Product` → `Run`（`⌘ + R`）

---

## 验证修复

重新运行 App 后，在 Safari Web Inspector 控制台中执行：

```javascript
console.log('所有插件:', Object.keys(window.Capacitor.Plugins));
```

**预期结果**：
- 应该包含 `SubscriptionPlugin` 在插件列表中

---

## 如果仍然不行

### 检查 1：确认 CAP_PLUGIN 宏

打开 `ios/App/SubscriptionPlugin.m`，确认包含：

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

### 检查 2：确认 Swift 类标记

打开 `ios/App/SubscriptionPlugin.swift`，确认包含：

```swift
@objc(SubscriptionPlugin)
public class SubscriptionPlugin: CAPPlugin {
    public override func getId() -> String {
        return "SubscriptionPlugin"
    }
    // ...
}
```

### 检查 3：检查编译错误

1. **在 Xcode 中打开 "Report Navigator"**（`⌘ + 9`）
2. **查看最新的构建日志**
3. **查找是否有关于 `SubscriptionPlugin` 的错误或警告**

---

## 已知问题

从之前的文档可以看到，`SaveToGalleryPlugin` 也有类似的注册问题。这可能表明：
1. Capacitor 8 的插件注册机制可能有变化
2. 自定义插件需要特殊配置才能被注册

---

**请按照步骤 1-5 操作，特别是步骤 2（检查 Target Membership）和步骤 5（清理并重新构建）！** 🚀


















