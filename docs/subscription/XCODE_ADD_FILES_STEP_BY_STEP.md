# Xcode 添加文件 - 分步操作指南

## 快速开始

### 步骤 1：打开 Xcode 项目

1. **打开终端**，运行：
   ```bash
   cd /Users/scarlett/Projects/BeatSync/ios/App
   open App.xcodeproj
   ```

   或者：
   - 打开 **Finder**
   - 导航到 `/Users/scarlett/Projects/BeatSync/ios/App/`
   - 双击 `App.xcodeproj`

2. 等待 Xcode 完全加载项目

### 步骤 2：添加 SubscriptionPlugin.swift

#### 方法 A：通过菜单添加（推荐）

1. 在 Xcode 左侧的 **项目导航器**（Project Navigator）中
   - 如果没有显示，按 `Command + 1` 或点击左侧边栏图标

2. 找到并**右键点击** `App` 文件夹（蓝色文件夹图标）

3. 选择 **"Add Files to 'App'..."**

4. 在文件选择对话框中：
   - 导航到：`/Users/scarlett/Projects/BeatSync/ios/App/Plugins/`
   - 选择 `SubscriptionPlugin.swift`
   - **关键设置**：
     ```
     ☑ Copy items if needed
     ○ Create folder references
     ☑ Create groups
     
     Add to targets:
     ☑ App  ← 这个必须勾选！
     ```
   - 点击 **"Add"**

#### 方法 B：直接拖拽

1. 打开 **Finder**，导航到 `/Users/scarlett/Projects/BeatSync/ios/App/Plugins/`

2. 找到 `SubscriptionPlugin.swift` 文件

3. **拖拽**文件到 Xcode 的项目导航器中
   - 拖到 `App` 文件夹上
   - 释放鼠标

4. 在弹出的对话框中：
   - ✅ 勾选 **"Copy items if needed"**
   - ✅ 选择 **"Create groups"**
   - ✅ 勾选 **"Add to targets: App"**
   - 点击 **"Finish"**

### 步骤 3：添加 SubscriptionPlugin.m

重复步骤 2，但这次：

1. 导航到：`/Users/scarlett/Projects/BeatSync/ios/App/`
2. 选择 `SubscriptionPlugin.m` 文件
3. 确保勾选 **"Add to targets: App"**

### 步骤 4：验证文件已添加

#### 检查 1：文件位置

在项目导航器中，你应该看到：
```
App
  ├── AppDelegate.swift
  ├── Plugins
  │   └── SubscriptionPlugin.swift  ← 新添加
  ├── SubscriptionPlugin.m          ← 新添加
  └── ...
```

#### 检查 2：Target Membership

1. 点击 `SubscriptionPlugin.swift` 文件
2. 在右侧面板中，找到 **"File Inspector"** 标签（第一个标签）
3. 向下滚动到 **"Target Membership"** 部分
4. 确保 **"App"** 旁边的复选框已勾选 ✅

5. 同样检查 `SubscriptionPlugin.m` 文件

#### 检查 3：编译测试

1. 按 `Shift + Command + K` 清理构建
2. 按 `Command + B` 构建项目
3. 查看是否有错误

### 步骤 5：检查 iOS 部署目标

StoreKit 2 需要 iOS 15.0+：

1. 在项目导航器中，点击最顶部的**蓝色项目图标**（App）
2. 在中间面板，选择 **"TARGETS"** → **"App"**
3. 选择 **"General"** 标签
4. 在 **"Deployment Info"** 部分
5. 确保 **"iOS"** 版本设置为 **15.0** 或更高

## 常见问题快速解决

### ❌ 问题：文件显示为红色

**解决**：
1. 选择红色文件
2. 按 `Delete` 键删除引用（不删除文件）
3. 重新按照步骤 2 添加文件

### ❌ 问题：编译错误 "No such module 'StoreKit'"

**解决**：
- 检查 iOS 部署目标是否为 15.0+
- 参考步骤 5

### ❌ 问题：编译错误 "Use of unresolved identifier 'CAPPlugin'"

**解决**：
1. 确保文件已添加到 Target（检查 Target Membership）
2. 清理构建：`Shift + Command + K`
3. 重新构建：`Command + B`

### ❌ 问题：找不到 "Add Files to 'App'..." 选项

**解决**：
- 确保右键点击的是 `App` **文件夹**（蓝色图标），不是文件
- 或者使用菜单：**File** → **Add Files to "App"...**

## 完整检查清单

完成后，确认：

- [ ] `SubscriptionPlugin.swift` 在项目导航器中可见
- [ ] `SubscriptionPlugin.m` 在项目导航器中可见
- [ ] 两个文件的 Target Membership 都包含 "App"
- [ ] iOS Deployment Target >= 15.0
- [ ] 项目可以成功编译（无错误）

## 如果遇到问题

1. **截图错误信息**：Xcode 底部的错误信息
2. **检查文件路径**：确保文件在正确的位置
3. **重新添加**：删除引用后重新添加
4. **清理构建**：`Shift + Command + K`，然后 `Command + B`

## 下一步

文件添加成功后：

1. ✅ 验证编译通过
2. 📱 在 App Store Connect 中配置产品
3. 🧪 使用沙盒账号测试购买流程

