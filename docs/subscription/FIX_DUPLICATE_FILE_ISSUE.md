# 修复重复文件问题

## 问题

发现有两个 `SubscriptionPlugin.swift` 文件：
1. `ios/App/Plugins/SubscriptionPlugin.swift` - ✅ 已修复（使用 displayPrice）
2. `ios/App/SubscriptionPlugin.swift` - ❌ 旧版本（使用 priceLocale）

Xcode 项目引用的是 `ios/App/SubscriptionPlugin.swift`（旧版本），所以仍然报错。

## 解决方案

### 已自动修复

已自动将正确的文件内容复制到 Xcode 引用的位置。

### 验证修复

1. **在 Xcode 中**：
   - 打开 `SubscriptionPlugin.swift`（在 `App` 文件夹下）
   - 跳转到第 50 行（`Command + L`，输入 50）
   - 应该看到：`productInfo["displayPrice"] = product.displayPrice`
   - **不应该**看到：`productInfo["priceLocale"]`

2. **如果还是旧代码**：
   - 在 Xcode 中按 `Command + S` 保存
   - 或者关闭文件后重新打开

3. **清理并重新构建**：
   - `Shift + Command + K`（清理）
   - `Command + B`（构建）

## 关于依赖包错误

图 2 显示的错误主要是：
- "Missing package product 'Capacitor'"
- "Missing package product 'Cordova'"
- "Missing package product 'IONFilesystemLib'"
- "There is no XCFramework found"

这些是 Capacitor 依赖问题，与订阅插件无关。解决方法：

### 方法 1：同步 Capacitor（推荐）

在终端运行：
```bash
cd /Users/scarlett/Projects/BeatSync
npx cap sync ios
```

### 方法 2：清理并重新构建

1. 关闭 Xcode
2. 删除 DerivedData：
   ```bash
   rm -rf ~/Library/Developer/Xcode/DerivedData
   ```
3. 重新打开 Xcode
4. 运行 `npx cap sync ios`
5. 清理构建：`Shift + Command + K`
6. 重新构建：`Command + B`

## 下一步

1. ✅ 文件已更新
2. ⏳ 在 Xcode 中验证文件内容
3. ⏳ 运行 `npx cap sync ios` 解决依赖问题
4. ⏳ 清理并重新构建

