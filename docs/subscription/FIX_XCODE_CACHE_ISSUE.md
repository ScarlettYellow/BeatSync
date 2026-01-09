# 修复 Xcode 缓存问题

## 问题

即使代码已修复，Xcode 仍然显示旧的编译错误。这通常是缓存问题。

## 解决方案

### 方法 1：清理构建（推荐）

1. **在 Xcode 中**：
   - 按 `Shift + Command + K`（清理构建文件夹）
   - 或者：**Product** → **Clean Build Folder**

2. **关闭 Xcode**

3. **删除 DerivedData**（可选，如果方法1不行）：
   ```bash
   rm -rf ~/Library/Developer/Xcode/DerivedData
   ```

4. **重新打开 Xcode**
   - 打开项目：`App.xcodeproj`

5. **重新构建**：
   - 按 `Command + B`

### 方法 2：完全清理（如果方法1不行）

1. **关闭 Xcode**

2. **删除 DerivedData**：
   ```bash
   rm -rf ~/Library/Developer/Xcode/DerivedData/*
   ```

3. **删除项目构建文件**（可选）：
   ```bash
   cd /Users/scarlett/Projects/BeatSync/ios/App
   rm -rf build/
   ```

4. **重新打开 Xcode**

5. **清理并构建**：
   - `Shift + Command + K`
   - `Command + B`

### 方法 3：验证文件已更新

1. **在 Xcode 中打开 `SubscriptionPlugin.swift`**

2. **检查第 50 行**：
   - 应该看到：`productInfo["displayPrice"] = product.displayPrice`
   - **不应该**看到：`productInfo["priceLocale"]`

3. **如果还是旧代码**：
   - 文件可能没有保存
   - 在 Xcode 中按 `Command + S` 保存
   - 或者重新打开文件

### 方法 4：检查文件是否正确添加到项目

1. **在项目导航器中**，找到 `SubscriptionPlugin.swift`

2. **选择文件**，在右侧面板检查：
   - **Target Membership** → **App** 应该已勾选 ✅

3. **如果未勾选**：
   - 勾选 **App**
   - 重新构建

## 验证修复

完成清理后：

1. **构建项目**：`Command + B`
2. **检查错误**：
   - ✅ 如果显示 "Build Succeeded"，说明成功！
   - ❌ 如果还有错误，查看具体错误信息

## 如果仍然报错

请提供：
1. **具体的错误信息**（截图或文字）
2. **错误所在的行号**
3. **完整的错误消息**

这样我可以进一步帮你修复。

