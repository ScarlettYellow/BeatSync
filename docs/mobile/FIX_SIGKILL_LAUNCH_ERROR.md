# 修复 iOS App SIGKILL 启动错误

## 问题描述

应用在启动时被系统强制终止，出现 `Thread 1: signal SIGKILL` 错误。这通常发生在 `dyld`（动态链接器）阶段。

## 可能的原因

1. **启动超时** - 应用启动时间过长，被 Watchdog 终止
2. **签名/证书问题** - Provisioning Profile 或证书配置不正确
3. **动态库加载失败** - Capacitor 或依赖库无法正确加载
4. **内存问题** - 启动时内存占用过高
5. **设备上的旧版本冲突** - 设备上已安装的版本有问题

## 解决方案（按顺序尝试）

### 方案 1：清理构建缓存和重新安装

```bash
# 1. 在 Xcode 中停止应用（如果正在运行）

# 2. 清理 DerivedData
rm -rf ~/Library/Developer/Xcode/DerivedData

# 3. 在 Xcode 中：
#    - Product → Clean Build Folder (Shift+Cmd+K)
#    - 关闭 Xcode

# 4. 在设备上删除应用（如果已安装）
#    长按应用图标 → 删除应用

# 5. 重新打开 Xcode，重新编译并运行
```

### 方案 2：检查签名和 Provisioning Profile

1. **在 Xcode 中：**
   - 选择项目 → Target "App" → Signing & Capabilities
   - 确认 "Automatically manage signing" 已勾选
   - 确认 Team 已正确选择
   - 确认 Bundle Identifier 为 `com.beatsync.app.dev`

2. **检查设备：**
   - 设置 → 通用 → VPN与设备管理
   - 确认开发者证书已信任

### 方案 3：检查网络请求阻塞

如果应用在启动时尝试进行网络请求，可能会阻塞启动：

1. **检查 `script.js` 中的启动代码：**
   - 确保没有同步的网络请求
   - 确保所有网络请求都是异步的

2. **临时禁用网络请求测试：**
   - 注释掉启动时的网络请求代码
   - 重新编译测试

### 方案 4：检查 Capacitor 配置

1. **确认 Capacitor 版本兼容性：**
   ```bash
   cd /Users/scarlett/Projects/BeatSync
   npx cap sync ios
   ```

2. **检查 `capacitor.config.ts` 或 `capacitor.config.json`：**
   - 确认服务器 URL 配置正确
   - 确认没有无效的配置项

### 方案 5：查看详细日志

在 Xcode 控制台中，查看完整的错误日志：

1. **查看设备日志：**
   ```bash
   # 在终端中运行
   xcrun simctl spawn booted log stream --predicate 'processImagePath contains "BeatSync"' --level debug
   ```

2. **或者在 Xcode 中：**
   - Window → Devices and Simulators
   - 选择设备 → View Device Logs
   - 查找最近的崩溃日志

### 方案 6：简化启动流程

临时简化 `AppDelegate.swift`，移除所有自定义初始化：

```swift
func application(_ application: UIApplication, didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?) -> Bool {
    // 最小化启动代码
    return true
}
```

### 方案 7：检查 Info.plist 配置

确认以下配置正确：

- `UILaunchStoryboardName` = "LaunchScreen"
- `UIMainStoryboardFile` = "Main"
- 所有必需的权限描述都已添加

### 方案 8：使用模拟器测试

如果真机有问题，先在模拟器上测试：

1. 在 Xcode 中选择 iOS Simulator
2. 运行应用
3. 如果模拟器可以运行，问题可能是设备特定的（签名、证书等）

## 快速诊断命令

```bash
# 1. 检查 Xcode 版本
xcodebuild -version

# 2. 检查设备连接
xcrun xctrace list devices

# 3. 检查项目配置
cd /Users/scarlett/Projects/BeatSync/ios/App
xcodebuild -list

# 4. 清理并重新同步 Capacitor
cd /Users/scarlett/Projects/BeatSync
npx cap clean ios
npx cap sync ios
```

## 常见错误模式

### 错误：`dyld: Library not loaded`
- **原因**：动态库路径错误或库缺失
- **解决**：运行 `npx cap sync ios` 重新同步

### 错误：`Code signing failed`
- **原因**：签名配置错误
- **解决**：检查 Signing & Capabilities 设置

### 错误：应用启动后立即退出
- **原因**：启动时崩溃或异常
- **解决**：查看设备日志，查找崩溃原因

## 如果以上方案都不行

1. **创建新的测试项目：**
   - 使用 Capacitor CLI 创建最小化项目
   - 逐步添加功能，定位问题

2. **检查 Xcode 和 iOS 版本兼容性：**
   - 确认 Xcode 版本支持目标 iOS 版本
   - 确认设备 iOS 版本 >= 15.0（项目最低版本）

3. **联系支持：**
   - 提供完整的 Xcode 控制台日志
   - 提供设备日志
   - 提供项目配置信息



