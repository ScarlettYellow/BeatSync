# Xcode 添加文件 - 简单操作指南

## 📋 需要添加的文件

文件已经创建在以下位置：
- ✅ `ios/App/Plugins/SubscriptionPlugin.swift` - 已存在
- ✅ `ios/App/SubscriptionPlugin.m` - 已存在

现在只需要在 Xcode 中将它们添加到项目中。

## 🚀 快速操作步骤

### 第一步：打开 Xcode 项目

**方法 1：通过终端（推荐）**
```bash
cd /Users/scarlett/Projects/BeatSync/ios/App
open App.xcodeproj
```

**方法 2：通过 Finder**
1. 打开 Finder
2. 导航到：`/Users/scarlett/Projects/BeatSync/ios/App/`
3. 双击 `App.xcodeproj` 文件

### 第二步：添加 SubscriptionPlugin.swift

1. **在 Xcode 左侧的项目导航器中**（如果没有显示，按 `Command + 1`）
   - 找到 `App` 文件夹（蓝色图标）

2. **右键点击 `App` 文件夹**
   - 选择 **"Add Files to 'App'..."**

3. **在文件选择对话框中**：
   - 导航到：`/Users/scarlett/Projects/BeatSync/ios/App/Plugins/`
   - 选择 `SubscriptionPlugin.swift`
   - **重要设置**：
     ```
     ☑ Copy items if needed
     ☑ Create groups
     ☑ Add to targets: App  ← 必须勾选！
     ```
   - 点击 **"Add"** 按钮

### 第三步：添加 SubscriptionPlugin.m

重复第二步的操作，但这次：

1. 导航到：`/Users/scarlett/Projects/BeatSync/ios/App/`
2. 选择 `SubscriptionPlugin.m` 文件
3. 确保勾选 **"Add to targets: App"**
4. 点击 **"Add"**

### 第四步：验证添加成功

#### ✅ 检查 1：文件出现在项目导航器中

你应该看到：
```
App
  ├── AppDelegate.swift
  ├── Plugins
  │   └── SubscriptionPlugin.swift  ← 应该在这里
  ├── SubscriptionPlugin.m         ← 应该在这里
  └── ...
```

#### ✅ 检查 2：验证 Target Membership

1. **点击 `SubscriptionPlugin.swift` 文件**
2. **在右侧面板**，点击 **"File Inspector"** 标签（📄 图标，第一个标签）
3. **向下滚动**，找到 **"Target Membership"** 部分
4. **确保 "App" 已勾选** ✅

5. **同样检查 `SubscriptionPlugin.m` 文件**

#### ✅ 检查 3：测试编译

1. **清理构建**：按 `Shift + Command + K`
2. **构建项目**：按 `Command + B`
3. **查看结果**：
   - ✅ 如果显示 "Build Succeeded"，说明成功！
   - ❌ 如果有错误，查看下方"常见问题"

### 第五步：检查 iOS 版本要求

StoreKit 2 需要 iOS 15.0+：

1. **点击项目导航器最顶部的蓝色项目图标**（App）
2. **在中间面板**，选择：
   - **"TARGETS"** → **"App"**
   - **"General"** 标签
3. **找到 "Deployment Info"** 部分
4. **确保 "iOS" 版本 >= 15.0**

## ⚠️ 常见问题

### 问题 1：找不到 "Add Files to 'App'..." 选项

**解决**：
- 确保右键点击的是 **文件夹**（蓝色图标），不是文件
- 或者使用菜单：**File** → **Add Files to "App"...**

### 问题 2：文件显示为红色

**原因**：文件路径丢失

**解决**：
1. 选择红色文件，按 `Delete` 键（只删除引用，不删除文件）
2. 重新按照步骤添加

### 问题 3：编译错误 "No such module 'StoreKit'"

**解决**：
- 检查 iOS Deployment Target 是否为 15.0+
- 参考第五步

### 问题 4：编译错误 "Use of unresolved identifier 'CAPPlugin'"

**解决**：
1. 检查 Target Membership（参考检查 2）
2. 清理构建：`Shift + Command + K`
3. 重新构建：`Command + B`

## 📝 操作要点总结

1. ✅ **右键点击 `App` 文件夹** → "Add Files to 'App'..."
2. ✅ **选择文件** → 导航到正确路径
3. ✅ **勾选 "Add to targets: App"** ← 最关键！
4. ✅ **验证 Target Membership** → 确保已勾选
5. ✅ **测试编译** → `Command + B`

## 🎯 完成标志

完成后，你应该能够：

- ✅ 在项目导航器中看到两个文件
- ✅ Target Membership 中 "App" 已勾选
- ✅ 项目可以成功编译（无错误）
- ✅ iOS Deployment Target >= 15.0

## 📚 相关文档

- [IOS_STOREKIT_INTEGRATION.md](./IOS_STOREKIT_INTEGRATION.md) - 完整集成指南
- [XCODE_ADD_FILES_GUIDE.md](./XCODE_ADD_FILES_GUIDE.md) - 详细操作指南

