# Xcode 添加文件操作指南

## 概述

本指南详细说明如何在 Xcode 项目中添加 SubscriptionPlugin 相关文件。

## 文件清单

需要添加的文件：
1. `ios/App/Plugins/SubscriptionPlugin.swift`
2. `ios/App/SubscriptionPlugin.m`

## 详细步骤

### 方法 1：通过 Xcode 界面添加（推荐）

#### 步骤 1：打开 Xcode 项目

1. 打开 **Finder**
2. 导航到项目目录：`/Users/scarlett/Projects/BeatSync/ios/App/`
3. 双击 `App.xcodeproj` 文件
4. 等待 Xcode 打开项目

**或者**：
- 在终端中运行：
  ```bash
  cd /Users/scarlett/Projects/BeatSync/ios/App
  open App.xcodeproj
  ```

#### 步骤 2：创建 Plugins 文件夹（如果不存在）

1. 在 Xcode 左侧的 **项目导航器**（Project Navigator）中
2. 找到 `App` 文件夹（蓝色图标）
3. 右键点击 `App` 文件夹
4. 选择 **"New Group"**（新建组）
5. 命名为 `Plugins`
6. 按 Enter 确认

#### 步骤 3：添加 SubscriptionPlugin.swift

1. 在项目导航器中，右键点击 `Plugins` 文件夹（或 `App` 文件夹）
2. 选择 **"Add Files to 'App'..."**（将文件添加到 'App'...）
3. 在文件选择对话框中：
   - 导航到：`/Users/scarlett/Projects/BeatSync/ios/App/Plugins/`
   - 选择 `SubscriptionPlugin.swift`
   - **重要**：确保勾选以下选项：
     - ✅ **"Copy items if needed"**（如果需要则复制项目）- 如果文件不在项目目录内
     - ✅ **"Create groups"**（创建组）
     - ✅ **"Add to targets: App"**（添加到目标：App）- 这是最关键的！
4. 点击 **"Add"**（添加）

#### 步骤 4：添加 SubscriptionPlugin.m

1. 在项目导航器中，右键点击 `App` 文件夹
2. 选择 **"Add Files to 'App'..."**
3. 在文件选择对话框中：
   - 导航到：`/Users/scarlett/Projects/BeatSync/ios/App/`
   - 选择 `SubscriptionPlugin.m`
   - **重要**：确保勾选：
     - ✅ **"Copy items if needed"**
     - ✅ **"Create groups"**
     - ✅ **"Add to targets: App"**
4. 点击 **"Add"**

#### 步骤 5：验证文件已添加

1. 在项目导航器中，检查文件是否出现：
   - `App/Plugins/SubscriptionPlugin.swift`
   - `App/SubscriptionPlugin.m`

2. 选择 `SubscriptionPlugin.swift` 文件
3. 在右侧的 **文件检查器**（File Inspector）中
4. 查看 **"Target Membership"** 部分
5. 确保 **"App"** 旁边的复选框已勾选 ✅

6. 同样检查 `SubscriptionPlugin.m` 文件

### 方法 2：直接拖拽添加

#### 步骤 1：打开 Finder 和 Xcode

1. 打开 **Finder**
2. 导航到：`/Users/scarlett/Projects/BeatSync/ios/App/Plugins/`
3. 同时打开 **Xcode**（已打开项目）

#### 步骤 2：拖拽文件

1. 在 Finder 中找到 `SubscriptionPlugin.swift`
2. **拖拽**文件到 Xcode 的项目导航器中
3. 拖到 `App` 文件夹或 `Plugins` 文件夹上
4. 释放鼠标

5. 在弹出的对话框中：
   - ✅ 勾选 **"Copy items if needed"**
   - ✅ 选择 **"Create groups"**
   - ✅ 勾选 **"Add to targets: App"**
6. 点击 **"Finish"**

7. 重复上述步骤添加 `SubscriptionPlugin.m`（从 `ios/App/` 目录）

### 方法 3：使用终端命令（高级）

如果你熟悉命令行，可以使用以下命令：

```bash
cd /Users/scarlett/Projects/BeatSync/ios/App

# 使用 xcodebuild 添加文件（需要手动编辑 project.pbxproj）
# 或者直接打开 Xcode 手动添加更安全
```

**注意**：不推荐手动编辑 `project.pbxproj`，容易出错。

## 验证文件是否正确添加

### 检查 1：文件出现在项目导航器中

- ✅ `SubscriptionPlugin.swift` 在 `App/Plugins/` 下
- ✅ `SubscriptionPlugin.m` 在 `App/` 下

### 检查 2：Target Membership

1. 选择 `SubscriptionPlugin.swift`
2. 在右侧面板的 **"Target Membership"** 中
3. 确保 **"App"** 已勾选 ✅

### 检查 3：编译检查

1. 在 Xcode 顶部菜单，选择 **Product** → **Clean Build Folder**（清理构建文件夹）
   - 或按快捷键：`Shift + Command + K`

2. 尝试编译项目：
   - 按 `Command + B` 或
   - 选择 **Product** → **Build**

3. 检查是否有编译错误：
   - 如果有错误，查看错误信息
   - 常见错误见下方"常见问题"部分

## 常见问题

### 问题 1：文件添加后找不到

**原因**：文件可能被添加到了错误的文件夹

**解决**：
1. 在项目导航器中搜索文件名
2. 找到文件后，拖拽到正确的位置
3. 确保文件在 `App` 文件夹下

### 问题 2：编译错误 "No such module 'StoreKit'"

**原因**：StoreKit 是系统框架，需要 iOS 15.0+

**解决**：
1. 选择项目（蓝色图标）→ **TARGETS** → **App**
2. 选择 **"General"** 标签
3. 在 **"Deployment Info"** 中
4. 确保 **"iOS Deployment Target"** 设置为 **15.0** 或更高

### 问题 3：编译错误 "Use of unresolved identifier 'CAPPlugin'"

**原因**：Capacitor 依赖未正确链接

**解决**：
1. 确保文件已添加到 Target
2. 检查 **"Target Membership"** 中 **"App"** 已勾选
3. 清理并重新构建：`Shift + Command + K`，然后 `Command + B`

### 问题 4：文件显示为红色

**原因**：文件路径丢失或文件被移动

**解决**：
1. 选择红色文件
2. 在右侧面板的 **"File Inspector"** 中
3. 点击 **"Location"** 旁边的文件夹图标
4. 重新选择文件位置

### 问题 5：插件方法未注册

**原因**：`SubscriptionPlugin.m` 未正确添加到项目

**解决**：
1. 确保 `SubscriptionPlugin.m` 在项目中
2. 确保已添加到 Target
3. 检查文件内容是否正确
4. 清理并重新构建项目

## 完整检查清单

完成以下所有步骤后，你的项目应该：

- [ ] `SubscriptionPlugin.swift` 在 `App/Plugins/` 文件夹中
- [ ] `SubscriptionPlugin.m` 在 `App/` 文件夹中
- [ ] 两个文件的 Target Membership 都包含 "App"
- [ ] 项目可以成功编译（无错误）
- [ ] iOS Deployment Target >= 15.0

## 下一步

文件添加完成后：

1. **验证编译**：确保项目可以成功编译
2. **测试插件**：在代码中测试插件是否可用
3. **配置产品ID**：在 App Store Connect 中配置产品
4. **测试购买流程**：使用沙盒账号测试

## 截图说明

### 添加文件对话框

```
┌─────────────────────────────────────────┐
│ Add Files to "App"                      │
├─────────────────────────────────────────┤
│                                         │
│  📁 ios/App/Plugins/                    │
│     📄 SubscriptionPlugin.swift          │
│                                         │
│  ☑ Copy items if needed                 │
│  ○ Create folder references             │
│  ☑ Create groups                        │
│                                         │
│  Add to targets:                        │
│  ☑ App                                  │
│                                         │
│  [Cancel]  [Add]                        │
└─────────────────────────────────────────┘
```

### Target Membership 检查

```
┌─────────────────────────────────────────┐
│ File Inspector                          │
├─────────────────────────────────────────┤
│                                         │
│ Target Membership:                     │
│  ☑ App                                  │
│                                         │
└─────────────────────────────────────────┘
```

## 需要帮助？

如果遇到问题：

1. 检查文件路径是否正确
2. 确保文件已添加到 Target
3. 清理并重新构建项目
4. 查看 Xcode 的编译错误信息
5. 参考 [IOS_STOREKIT_INTEGRATION.md](./IOS_STOREKIT_INTEGRATION.md)

