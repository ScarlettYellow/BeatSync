# iOS App 本地测试指南

## 📋 准备工作

### 1. 确认文件已更新

✅ **已更新**：
- `ios/App/Products.storekit` - 已更新为公测期产品ID和价格
- `ios/App/SubscriptionPlugin.swift` - 已配置公测期产品ID

### 2. 确认插件已注册

✅ **已确认**：
- `SubscriptionPlugin.swift` 和 `SubscriptionPlugin.m` 已添加到 Xcode 项目
- 插件已正确注册（通过 `@objc(SubscriptionPlugin)` 和 `CAPPlugin`）

---

## 🚀 步骤 1：在 Xcode 中配置 StoreKit Testing

### 1.1 打开项目

```bash
cd ios/App
npx cap open ios
```

或者直接在 Xcode 中打开：
```bash
open ios/App/App.xcworkspace
```

### 1.2 配置 Scheme

**推荐方法：使用快捷键（最简单）**

1. **打开 Edit Scheme 窗口**
   - 在 Xcode 中，直接按快捷键：**`⌘ + <`**（Command + 小于号）
   - 这会直接打开 Scheme 编辑窗口

**或者通过菜单栏：**

1. **选择 Scheme**
   - 在 Xcode 顶部菜单栏，点击 **"Product"** 菜单
   - 选择 **"Scheme"** 子菜单
   - 选择 **"Edit Scheme..."**

**或者通过工具栏：**

1. **找到 Scheme 下拉菜单**
   - 在 Xcode 顶部工具栏，找到运行按钮（▶️，绿色）
   - 运行按钮右侧就是 Scheme 下拉菜单（显示 "App"）
   - 点击 Scheme 下拉菜单右侧的 **"Edit Scheme..."** 按钮

3. **配置 StoreKit Configuration**
   - 在左侧选择 **"Run"**
   - 切换到 **"Options"** 标签
   - 找到 **"StoreKit Configuration"** 下拉菜单
   - 选择 **"Products.storekit"**
   - 点击 **"Close"** 保存

### 1.3 验证配置

- ✅ 确保 `Products.storekit` 文件在项目中可见
- ✅ 文件位置：`ios/App/Products.storekit`
- ✅ 确保文件已添加到 Xcode 项目（在 Project Navigator 中可见）

---

## 🧪 步骤 2：运行 App 并测试

### 2.1 选择目标设备

在 Xcode 中：
- 选择 **模拟器**（推荐：iPhone 15 Pro 或最新版本）
- 或选择 **真机**（需要开发者账号）

### 2.2 运行 App

1. 点击 **运行按钮**（▶️）或按 `⌘ + R`
2. 等待 App 编译和启动

### 2.3 测试产品列表获取

在 App 中：
1. 打开订阅管理页面
2. 点击 **"查看订阅套餐"** 按钮
3. 应该能看到以下产品：
   - ✅ 基础版月付：¥4.80/月
   - ✅ 高级版月付：¥19.90/月
   - ✅ 10次下载包：¥5.00
   - ✅ 20次下载包：¥9.00

**预期结果**：
- ✅ 产品列表正确显示
- ✅ 价格正确显示
- ✅ 产品描述正确显示

**如果失败**：
- 检查浏览器控制台（如果使用 WebView）
- 检查 Xcode 控制台日志
- 确认 `Products.storekit` 文件已正确配置

---

### 2.4 测试购买流程 UI

1. 在 App 中选择一个产品（例如：基础版月付）
2. 点击 **"购买"** 按钮
3. 应该弹出 StoreKit 购买确认对话框

**预期结果**：
- ✅ 购买对话框正确显示
- ✅ 产品信息正确显示
- ✅ 价格正确显示

**注意**：
- 这是本地测试，不会进行真实支付
- StoreKit Configuration File 会模拟购买流程
- 购买会立即成功（无需等待）

---

### 2.5 测试订阅状态查询

1. 在 App 中点击 **"恢复购买"** 按钮
2. 或查看订阅状态

**预期结果**：
- ✅ 订阅状态正确显示
- ✅ 已购买的产品正确显示

---

### 2.6 测试恢复购买

1. 在 App 中点击 **"恢复购买"** 按钮
2. 应该能看到之前"购买"的产品

**预期结果**：
- ✅ 恢复购买功能正常工作
- ✅ 已购买的产品正确恢复

---

## 🔍 步骤 3：调试和验证

### 3.1 查看 Xcode 控制台日志

在 Xcode 底部控制台查看日志：
- 查找 `SubscriptionPlugin` 相关的日志
- 查找 StoreKit 相关的日志
- 查找错误信息（如果有）

### 3.2 查看浏览器控制台（如果使用 WebView）

如果 App 使用 WebView：
1. 在 Safari 中打开 **"开发"** 菜单
2. 选择你的设备 → **"BeatSync"**
3. 查看控制台日志

### 3.3 验证插件调用

在浏览器控制台或 Xcode 控制台中，应该能看到：
```
[SubscriptionPlugin] getAvailableProducts called
[SubscriptionPlugin] Products loaded: 4
```

---

## ⚠️ 常见问题

### 问题 1：产品列表为空

**原因**：
- `Products.storekit` 文件未正确配置
- 产品ID不匹配

**解决方法**：
1. 检查 `Products.storekit` 文件中的 `productID` 是否与 `SubscriptionPlugin.swift` 中的 `productIds` 匹配
2. 确认 Scheme 中已选择 `Products.storekit`
3. 重新运行 App

### 问题 2：购买失败

**原因**：
- StoreKit Configuration File 未正确配置
- 产品ID不匹配

**解决方法**：
1. 确认 Scheme 中已选择 `Products.storekit`
2. 检查产品ID是否匹配
3. 重新运行 App

### 问题 3：插件未找到

**原因**：
- 插件未正确注册
- 插件文件未添加到 Xcode 项目

**解决方法**：
1. 检查 `SubscriptionPlugin.swift` 和 `SubscriptionPlugin.m` 是否在 Xcode 项目中
2. 检查插件是否正确注册（`@objc(SubscriptionPlugin)`）
3. 清理构建缓存：`Product` → `Clean Build Folder`（`⌘ + Shift + K`）
4. 重新构建项目

---

## 📝 测试检查清单

### 基本功能
- [ ] 产品列表获取成功
- [ ] 产品价格正确显示
- [ ] 产品描述正确显示
- [ ] 购买流程 UI 正常
- [ ] 订阅状态查询正常
- [ ] 恢复购买功能正常

### 产品验证
- [ ] 基础版月付：¥4.80/月
- [ ] 高级版月付：¥19.90/月
- [ ] 10次下载包：¥5.00
- [ ] 20次下载包：¥9.00

### 错误处理
- [ ] 网络错误处理（本地测试不适用）
- [ ] 购买取消处理
- [ ] 插件调用错误处理

---

## 🎯 下一步

完成本地测试后：
1. ✅ 验证基本功能正常
2. ⏳ 等待 App Store Connect 审核通过
3. ⏳ 进行沙盒测试（完整测试）

---

## 📚 相关文档

- `docs/subscription/IOS_TESTING_GUIDE.md` - 完整测试指南
- `docs/subscription/APP_STORE_CONNECT_SETUP.md` - App Store Connect 配置指南
- `docs/subscription/NEXT_TASKS.md` - 接下来的工作清单

---

**开始测试吧！** 🚀








# iOS App 本地测试指南

## 📋 准备工作

### 1. 确认文件已更新

✅ **已更新**：
- `ios/App/Products.storekit` - 已更新为公测期产品ID和价格
- `ios/App/SubscriptionPlugin.swift` - 已配置公测期产品ID

### 2. 确认插件已注册

✅ **已确认**：
- `SubscriptionPlugin.swift` 和 `SubscriptionPlugin.m` 已添加到 Xcode 项目
- 插件已正确注册（通过 `@objc(SubscriptionPlugin)` 和 `CAPPlugin`）

---

## 🚀 步骤 1：在 Xcode 中配置 StoreKit Testing

### 1.1 打开项目

```bash
cd ios/App
npx cap open ios
```

或者直接在 Xcode 中打开：
```bash
open ios/App/App.xcworkspace
```

### 1.2 配置 Scheme

**推荐方法：使用快捷键（最简单）**

1. **打开 Edit Scheme 窗口**
   - 在 Xcode 中，直接按快捷键：**`⌘ + <`**（Command + 小于号）
   - 这会直接打开 Scheme 编辑窗口

**或者通过菜单栏：**

1. **选择 Scheme**
   - 在 Xcode 顶部菜单栏，点击 **"Product"** 菜单
   - 选择 **"Scheme"** 子菜单
   - 选择 **"Edit Scheme..."**

**或者通过工具栏：**

1. **找到 Scheme 下拉菜单**
   - 在 Xcode 顶部工具栏，找到运行按钮（▶️，绿色）
   - 运行按钮右侧就是 Scheme 下拉菜单（显示 "App"）
   - 点击 Scheme 下拉菜单右侧的 **"Edit Scheme..."** 按钮

3. **配置 StoreKit Configuration**
   - 在左侧选择 **"Run"**
   - 切换到 **"Options"** 标签
   - 找到 **"StoreKit Configuration"** 下拉菜单
   - 选择 **"Products.storekit"**
   - 点击 **"Close"** 保存

### 1.3 验证配置

- ✅ 确保 `Products.storekit` 文件在项目中可见
- ✅ 文件位置：`ios/App/Products.storekit`
- ✅ 确保文件已添加到 Xcode 项目（在 Project Navigator 中可见）

---

## 🧪 步骤 2：运行 App 并测试

### 2.1 选择目标设备

在 Xcode 中：
- 选择 **模拟器**（推荐：iPhone 15 Pro 或最新版本）
- 或选择 **真机**（需要开发者账号）

### 2.2 运行 App

1. 点击 **运行按钮**（▶️）或按 `⌘ + R`
2. 等待 App 编译和启动

### 2.3 测试产品列表获取

在 App 中：
1. 打开订阅管理页面
2. 点击 **"查看订阅套餐"** 按钮
3. 应该能看到以下产品：
   - ✅ 基础版月付：¥4.80/月
   - ✅ 高级版月付：¥19.90/月
   - ✅ 10次下载包：¥5.00
   - ✅ 20次下载包：¥9.00

**预期结果**：
- ✅ 产品列表正确显示
- ✅ 价格正确显示
- ✅ 产品描述正确显示

**如果失败**：
- 检查浏览器控制台（如果使用 WebView）
- 检查 Xcode 控制台日志
- 确认 `Products.storekit` 文件已正确配置

---

### 2.4 测试购买流程 UI

1. 在 App 中选择一个产品（例如：基础版月付）
2. 点击 **"购买"** 按钮
3. 应该弹出 StoreKit 购买确认对话框

**预期结果**：
- ✅ 购买对话框正确显示
- ✅ 产品信息正确显示
- ✅ 价格正确显示

**注意**：
- 这是本地测试，不会进行真实支付
- StoreKit Configuration File 会模拟购买流程
- 购买会立即成功（无需等待）

---

### 2.5 测试订阅状态查询

1. 在 App 中点击 **"恢复购买"** 按钮
2. 或查看订阅状态

**预期结果**：
- ✅ 订阅状态正确显示
- ✅ 已购买的产品正确显示

---

### 2.6 测试恢复购买

1. 在 App 中点击 **"恢复购买"** 按钮
2. 应该能看到之前"购买"的产品

**预期结果**：
- ✅ 恢复购买功能正常工作
- ✅ 已购买的产品正确恢复

---

## 🔍 步骤 3：调试和验证

### 3.1 查看 Xcode 控制台日志

在 Xcode 底部控制台查看日志：
- 查找 `SubscriptionPlugin` 相关的日志
- 查找 StoreKit 相关的日志
- 查找错误信息（如果有）

### 3.2 查看浏览器控制台（如果使用 WebView）

如果 App 使用 WebView：
1. 在 Safari 中打开 **"开发"** 菜单
2. 选择你的设备 → **"BeatSync"**
3. 查看控制台日志

### 3.3 验证插件调用

在浏览器控制台或 Xcode 控制台中，应该能看到：
```
[SubscriptionPlugin] getAvailableProducts called
[SubscriptionPlugin] Products loaded: 4
```

---

## ⚠️ 常见问题

### 问题 1：产品列表为空

**原因**：
- `Products.storekit` 文件未正确配置
- 产品ID不匹配

**解决方法**：
1. 检查 `Products.storekit` 文件中的 `productID` 是否与 `SubscriptionPlugin.swift` 中的 `productIds` 匹配
2. 确认 Scheme 中已选择 `Products.storekit`
3. 重新运行 App

### 问题 2：购买失败

**原因**：
- StoreKit Configuration File 未正确配置
- 产品ID不匹配

**解决方法**：
1. 确认 Scheme 中已选择 `Products.storekit`
2. 检查产品ID是否匹配
3. 重新运行 App

### 问题 3：插件未找到

**原因**：
- 插件未正确注册
- 插件文件未添加到 Xcode 项目

**解决方法**：
1. 检查 `SubscriptionPlugin.swift` 和 `SubscriptionPlugin.m` 是否在 Xcode 项目中
2. 检查插件是否正确注册（`@objc(SubscriptionPlugin)`）
3. 清理构建缓存：`Product` → `Clean Build Folder`（`⌘ + Shift + K`）
4. 重新构建项目

---

## 📝 测试检查清单

### 基本功能
- [ ] 产品列表获取成功
- [ ] 产品价格正确显示
- [ ] 产品描述正确显示
- [ ] 购买流程 UI 正常
- [ ] 订阅状态查询正常
- [ ] 恢复购买功能正常

### 产品验证
- [ ] 基础版月付：¥4.80/月
- [ ] 高级版月付：¥19.90/月
- [ ] 10次下载包：¥5.00
- [ ] 20次下载包：¥9.00

### 错误处理
- [ ] 网络错误处理（本地测试不适用）
- [ ] 购买取消处理
- [ ] 插件调用错误处理

---

## 🎯 下一步

完成本地测试后：
1. ✅ 验证基本功能正常
2. ⏳ 等待 App Store Connect 审核通过
3. ⏳ 进行沙盒测试（完整测试）

---

## 📚 相关文档

- `docs/subscription/IOS_TESTING_GUIDE.md` - 完整测试指南
- `docs/subscription/APP_STORE_CONNECT_SETUP.md` - App Store Connect 配置指南
- `docs/subscription/NEXT_TASKS.md` - 接下来的工作清单

---

**开始测试吧！** 🚀








# iOS App 本地测试指南

## 📋 准备工作

### 1. 确认文件已更新

✅ **已更新**：
- `ios/App/Products.storekit` - 已更新为公测期产品ID和价格
- `ios/App/SubscriptionPlugin.swift` - 已配置公测期产品ID

### 2. 确认插件已注册

✅ **已确认**：
- `SubscriptionPlugin.swift` 和 `SubscriptionPlugin.m` 已添加到 Xcode 项目
- 插件已正确注册（通过 `@objc(SubscriptionPlugin)` 和 `CAPPlugin`）

---

## 🚀 步骤 1：在 Xcode 中配置 StoreKit Testing

### 1.1 打开项目

```bash
cd ios/App
npx cap open ios
```

或者直接在 Xcode 中打开：
```bash
open ios/App/App.xcworkspace
```

### 1.2 配置 Scheme

**推荐方法：使用快捷键（最简单）**

1. **打开 Edit Scheme 窗口**
   - 在 Xcode 中，直接按快捷键：**`⌘ + <`**（Command + 小于号）
   - 这会直接打开 Scheme 编辑窗口

**或者通过菜单栏：**

1. **选择 Scheme**
   - 在 Xcode 顶部菜单栏，点击 **"Product"** 菜单
   - 选择 **"Scheme"** 子菜单
   - 选择 **"Edit Scheme..."**

**或者通过工具栏：**

1. **找到 Scheme 下拉菜单**
   - 在 Xcode 顶部工具栏，找到运行按钮（▶️，绿色）
   - 运行按钮右侧就是 Scheme 下拉菜单（显示 "App"）
   - 点击 Scheme 下拉菜单右侧的 **"Edit Scheme..."** 按钮

3. **配置 StoreKit Configuration**
   - 在左侧选择 **"Run"**
   - 切换到 **"Options"** 标签
   - 找到 **"StoreKit Configuration"** 下拉菜单
   - 选择 **"Products.storekit"**
   - 点击 **"Close"** 保存

### 1.3 验证配置

- ✅ 确保 `Products.storekit` 文件在项目中可见
- ✅ 文件位置：`ios/App/Products.storekit`
- ✅ 确保文件已添加到 Xcode 项目（在 Project Navigator 中可见）

---

## 🧪 步骤 2：运行 App 并测试

### 2.1 选择目标设备

在 Xcode 中：
- 选择 **模拟器**（推荐：iPhone 15 Pro 或最新版本）
- 或选择 **真机**（需要开发者账号）

### 2.2 运行 App

1. 点击 **运行按钮**（▶️）或按 `⌘ + R`
2. 等待 App 编译和启动

### 2.3 测试产品列表获取

在 App 中：
1. 打开订阅管理页面
2. 点击 **"查看订阅套餐"** 按钮
3. 应该能看到以下产品：
   - ✅ 基础版月付：¥4.80/月
   - ✅ 高级版月付：¥19.90/月
   - ✅ 10次下载包：¥5.00
   - ✅ 20次下载包：¥9.00

**预期结果**：
- ✅ 产品列表正确显示
- ✅ 价格正确显示
- ✅ 产品描述正确显示

**如果失败**：
- 检查浏览器控制台（如果使用 WebView）
- 检查 Xcode 控制台日志
- 确认 `Products.storekit` 文件已正确配置

---

### 2.4 测试购买流程 UI

1. 在 App 中选择一个产品（例如：基础版月付）
2. 点击 **"购买"** 按钮
3. 应该弹出 StoreKit 购买确认对话框

**预期结果**：
- ✅ 购买对话框正确显示
- ✅ 产品信息正确显示
- ✅ 价格正确显示

**注意**：
- 这是本地测试，不会进行真实支付
- StoreKit Configuration File 会模拟购买流程
- 购买会立即成功（无需等待）

---

### 2.5 测试订阅状态查询

1. 在 App 中点击 **"恢复购买"** 按钮
2. 或查看订阅状态

**预期结果**：
- ✅ 订阅状态正确显示
- ✅ 已购买的产品正确显示

---

### 2.6 测试恢复购买

1. 在 App 中点击 **"恢复购买"** 按钮
2. 应该能看到之前"购买"的产品

**预期结果**：
- ✅ 恢复购买功能正常工作
- ✅ 已购买的产品正确恢复

---

## 🔍 步骤 3：调试和验证

### 3.1 查看 Xcode 控制台日志

在 Xcode 底部控制台查看日志：
- 查找 `SubscriptionPlugin` 相关的日志
- 查找 StoreKit 相关的日志
- 查找错误信息（如果有）

### 3.2 查看浏览器控制台（如果使用 WebView）

如果 App 使用 WebView：
1. 在 Safari 中打开 **"开发"** 菜单
2. 选择你的设备 → **"BeatSync"**
3. 查看控制台日志

### 3.3 验证插件调用

在浏览器控制台或 Xcode 控制台中，应该能看到：
```
[SubscriptionPlugin] getAvailableProducts called
[SubscriptionPlugin] Products loaded: 4
```

---

## ⚠️ 常见问题

### 问题 1：产品列表为空

**原因**：
- `Products.storekit` 文件未正确配置
- 产品ID不匹配

**解决方法**：
1. 检查 `Products.storekit` 文件中的 `productID` 是否与 `SubscriptionPlugin.swift` 中的 `productIds` 匹配
2. 确认 Scheme 中已选择 `Products.storekit`
3. 重新运行 App

### 问题 2：购买失败

**原因**：
- StoreKit Configuration File 未正确配置
- 产品ID不匹配

**解决方法**：
1. 确认 Scheme 中已选择 `Products.storekit`
2. 检查产品ID是否匹配
3. 重新运行 App

### 问题 3：插件未找到

**原因**：
- 插件未正确注册
- 插件文件未添加到 Xcode 项目

**解决方法**：
1. 检查 `SubscriptionPlugin.swift` 和 `SubscriptionPlugin.m` 是否在 Xcode 项目中
2. 检查插件是否正确注册（`@objc(SubscriptionPlugin)`）
3. 清理构建缓存：`Product` → `Clean Build Folder`（`⌘ + Shift + K`）
4. 重新构建项目

---

## 📝 测试检查清单

### 基本功能
- [ ] 产品列表获取成功
- [ ] 产品价格正确显示
- [ ] 产品描述正确显示
- [ ] 购买流程 UI 正常
- [ ] 订阅状态查询正常
- [ ] 恢复购买功能正常

### 产品验证
- [ ] 基础版月付：¥4.80/月
- [ ] 高级版月付：¥19.90/月
- [ ] 10次下载包：¥5.00
- [ ] 20次下载包：¥9.00

### 错误处理
- [ ] 网络错误处理（本地测试不适用）
- [ ] 购买取消处理
- [ ] 插件调用错误处理

---

## 🎯 下一步

完成本地测试后：
1. ✅ 验证基本功能正常
2. ⏳ 等待 App Store Connect 审核通过
3. ⏳ 进行沙盒测试（完整测试）

---

## 📚 相关文档

- `docs/subscription/IOS_TESTING_GUIDE.md` - 完整测试指南
- `docs/subscription/APP_STORE_CONNECT_SETUP.md` - App Store Connect 配置指南
- `docs/subscription/NEXT_TASKS.md` - 接下来的工作清单

---

**开始测试吧！** 🚀



















