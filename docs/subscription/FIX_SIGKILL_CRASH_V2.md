# 修复 SIGKILL 崩溃（版本2）

## 问题

App 启动时出现黑屏，Xcode 显示 `Thread 1: signal SIGKILL`，崩溃发生在 `dyld` 的 `lldb_image_notifier` 中。

## 可能原因

1. **插件加载失败**：某个 Capacitor 插件初始化失败
2. **代码签名问题**：真机调试时签名配置错误
3. **构建缓存问题**：Xcode 构建缓存损坏
4. **内存问题**：启动时内存不足
5. **WebView 加载失败**：前端资源加载失败

## 修复步骤

### 步骤 1：清理构建缓存

在 Xcode 中：
1. 菜单：`Product` → `Clean Build Folder`（或按 `Shift + Cmd + K`）
2. 关闭 Xcode

在终端中：
```bash
# 清理 DerivedData
rm -rf ~/Library/Developer/Xcode/DerivedData/*

# 清理构建缓存
cd ios/App
xcodebuild clean -workspace App.xcworkspace -scheme App
```

### 步骤 2：检查插件注册

确认 `SubscriptionPlugin.m` 中的强制链接代码已注释：

```objc
// 强制链接插件类（确保插件被 Objective-C 运行时发现）
// 暂时注释掉，避免启动时崩溃
/*
__attribute__((constructor))
static void SubscriptionPlugin_force_link() {
    ...
}
*/
```

### 步骤 3：检查 Xcode 控制台完整错误

在 Xcode 控制台（底部面板）查看完整的错误信息，查找：
- `dyld` 相关错误
- 插件加载错误
- 内存相关错误

### 步骤 4：尝试在模拟器运行

如果真机崩溃，尝试在模拟器运行：
1. 在 Xcode 中选择模拟器（如 iPhone 15 Pro）
2. 运行 App
3. 如果模拟器正常，可能是真机签名或权限问题

### 步骤 5：检查 Info.plist 配置

确认 `Info.plist` 中的 ATS 配置正确：

```xml
<key>NSAppTransportSecurity</key>
<dict>
    <key>NSAllowsLocalNetworking</key>
    <true/>
</dict>
```

### 步骤 6：检查前端资源

确认前端文件已正确同步：

```bash
# 检查前端文件是否存在
ls -la ios/App/App/public/

# 如果不存在，重新同步
npx cap sync ios
```

### 步骤 7：简化测试（如果以上都失败）

临时禁用所有插件，只保留基础功能：

1. 在 `SubscriptionPlugin.m` 中，确保强制链接代码已注释
2. 在 `Info.plist` 中，检查是否有其他插件配置
3. 尝试最小化配置运行

---

## 快速修复命令

```bash
# 1. 清理构建缓存
rm -rf ~/Library/Developer/Xcode/DerivedData/*

# 2. 重新同步前端代码
npx cap sync ios

# 3. 打开 Xcode
npx cap open ios

# 4. 在 Xcode 中：
#    - Product → Clean Build Folder (Shift+Cmd+K)
#    - 选择模拟器（而不是真机）
#    - 运行 App
```

---

**请先执行快速修复命令，如果仍然崩溃，请提供 Xcode 控制台的完整错误信息！** 🔍

# 修复 SIGKILL 崩溃（版本2）

## 问题

App 启动时出现黑屏，Xcode 显示 `Thread 1: signal SIGKILL`，崩溃发生在 `dyld` 的 `lldb_image_notifier` 中。

## 可能原因

1. **插件加载失败**：某个 Capacitor 插件初始化失败
2. **代码签名问题**：真机调试时签名配置错误
3. **构建缓存问题**：Xcode 构建缓存损坏
4. **内存问题**：启动时内存不足
5. **WebView 加载失败**：前端资源加载失败

## 修复步骤

### 步骤 1：清理构建缓存

在 Xcode 中：
1. 菜单：`Product` → `Clean Build Folder`（或按 `Shift + Cmd + K`）
2. 关闭 Xcode

在终端中：
```bash
# 清理 DerivedData
rm -rf ~/Library/Developer/Xcode/DerivedData/*

# 清理构建缓存
cd ios/App
xcodebuild clean -workspace App.xcworkspace -scheme App
```

### 步骤 2：检查插件注册

确认 `SubscriptionPlugin.m` 中的强制链接代码已注释：

```objc
// 强制链接插件类（确保插件被 Objective-C 运行时发现）
// 暂时注释掉，避免启动时崩溃
/*
__attribute__((constructor))
static void SubscriptionPlugin_force_link() {
    ...
}
*/
```

### 步骤 3：检查 Xcode 控制台完整错误

在 Xcode 控制台（底部面板）查看完整的错误信息，查找：
- `dyld` 相关错误
- 插件加载错误
- 内存相关错误

### 步骤 4：尝试在模拟器运行

如果真机崩溃，尝试在模拟器运行：
1. 在 Xcode 中选择模拟器（如 iPhone 15 Pro）
2. 运行 App
3. 如果模拟器正常，可能是真机签名或权限问题

### 步骤 5：检查 Info.plist 配置

确认 `Info.plist` 中的 ATS 配置正确：

```xml
<key>NSAppTransportSecurity</key>
<dict>
    <key>NSAllowsLocalNetworking</key>
    <true/>
</dict>
```

### 步骤 6：检查前端资源

确认前端文件已正确同步：

```bash
# 检查前端文件是否存在
ls -la ios/App/App/public/

# 如果不存在，重新同步
npx cap sync ios
```

### 步骤 7：简化测试（如果以上都失败）

临时禁用所有插件，只保留基础功能：

1. 在 `SubscriptionPlugin.m` 中，确保强制链接代码已注释
2. 在 `Info.plist` 中，检查是否有其他插件配置
3. 尝试最小化配置运行

---

## 快速修复命令

```bash
# 1. 清理构建缓存
rm -rf ~/Library/Developer/Xcode/DerivedData/*

# 2. 重新同步前端代码
npx cap sync ios

# 3. 打开 Xcode
npx cap open ios

# 4. 在 Xcode 中：
#    - Product → Clean Build Folder (Shift+Cmd+K)
#    - 选择模拟器（而不是真机）
#    - 运行 App
```

---

**请先执行快速修复命令，如果仍然崩溃，请提供 Xcode 控制台的完整错误信息！** 🔍

# 修复 SIGKILL 崩溃（版本2）

## 问题

App 启动时出现黑屏，Xcode 显示 `Thread 1: signal SIGKILL`，崩溃发生在 `dyld` 的 `lldb_image_notifier` 中。

## 可能原因

1. **插件加载失败**：某个 Capacitor 插件初始化失败
2. **代码签名问题**：真机调试时签名配置错误
3. **构建缓存问题**：Xcode 构建缓存损坏
4. **内存问题**：启动时内存不足
5. **WebView 加载失败**：前端资源加载失败

## 修复步骤

### 步骤 1：清理构建缓存

在 Xcode 中：
1. 菜单：`Product` → `Clean Build Folder`（或按 `Shift + Cmd + K`）
2. 关闭 Xcode

在终端中：
```bash
# 清理 DerivedData
rm -rf ~/Library/Developer/Xcode/DerivedData/*

# 清理构建缓存
cd ios/App
xcodebuild clean -workspace App.xcworkspace -scheme App
```

### 步骤 2：检查插件注册

确认 `SubscriptionPlugin.m` 中的强制链接代码已注释：

```objc
// 强制链接插件类（确保插件被 Objective-C 运行时发现）
// 暂时注释掉，避免启动时崩溃
/*
__attribute__((constructor))
static void SubscriptionPlugin_force_link() {
    ...
}
*/
```

### 步骤 3：检查 Xcode 控制台完整错误

在 Xcode 控制台（底部面板）查看完整的错误信息，查找：
- `dyld` 相关错误
- 插件加载错误
- 内存相关错误

### 步骤 4：尝试在模拟器运行

如果真机崩溃，尝试在模拟器运行：
1. 在 Xcode 中选择模拟器（如 iPhone 15 Pro）
2. 运行 App
3. 如果模拟器正常，可能是真机签名或权限问题

### 步骤 5：检查 Info.plist 配置

确认 `Info.plist` 中的 ATS 配置正确：

```xml
<key>NSAppTransportSecurity</key>
<dict>
    <key>NSAllowsLocalNetworking</key>
    <true/>
</dict>
```

### 步骤 6：检查前端资源

确认前端文件已正确同步：

```bash
# 检查前端文件是否存在
ls -la ios/App/App/public/

# 如果不存在，重新同步
npx cap sync ios
```

### 步骤 7：简化测试（如果以上都失败）

临时禁用所有插件，只保留基础功能：

1. 在 `SubscriptionPlugin.m` 中，确保强制链接代码已注释
2. 在 `Info.plist` 中，检查是否有其他插件配置
3. 尝试最小化配置运行

---

## 快速修复命令

```bash
# 1. 清理构建缓存
rm -rf ~/Library/Developer/Xcode/DerivedData/*

# 2. 重新同步前端代码
npx cap sync ios

# 3. 打开 Xcode
npx cap open ios

# 4. 在 Xcode 中：
#    - Product → Clean Build Folder (Shift+Cmd+K)
#    - 选择模拟器（而不是真机）
#    - 运行 App
```

---

**请先执行快速修复命令，如果仍然崩溃，请提供 Xcode 控制台的完整错误信息！** 🔍












