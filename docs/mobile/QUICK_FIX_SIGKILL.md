# 快速修复 SIGKILL 启动错误

## 立即尝试的修复步骤

### 步骤 1：清理并重新安装（最常见解决方案）

```bash
# 1. 在 Xcode 中停止应用（Cmd+.）

# 2. 清理 DerivedData
rm -rf ~/Library/Developer/Xcode/DerivedData

# 3. 在 Xcode 中：
#    - Product → Clean Build Folder (Shift+Cmd+K)
#    - 关闭 Xcode

# 4. 在设备上删除应用
#    长按应用图标 → 删除应用

# 5. 重新打开 Xcode，重新编译并运行
```

### 步骤 2：检查签名配置

1. **在 Xcode 中：**
   - 选择项目 → Target "App" → Signing & Capabilities
   - 确认 "Automatically manage signing" 已勾选
   - 确认 Team 已正确选择（76HV63JQ24）
   - 确认 Bundle Identifier 为 `com.beatsync.app.dev`

2. **在设备上：**
   - 设置 → 通用 → VPN与设备管理
   - 找到你的开发者证书，点击"信任"

### 步骤 3：检查设备日志（获取详细错误信息）

在 Xcode 中：
1. Window → Devices and Simulators
2. 选择你的设备
3. 点击 "Open Console"
4. 过滤 "BeatSync" 或 "App"
5. 查看启动时的详细错误信息

### 步骤 4：简化启动流程（临时测试）

如果以上都不行，临时修改 `AppDelegate.swift`，移除所有自定义代码：

```swift
func application(_ application: UIApplication, didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?) -> Bool {
    // 最小化启动代码
    return true
}
```

### 步骤 5：使用模拟器测试

如果真机有问题，先在模拟器上测试：
1. 在 Xcode 中选择 iOS Simulator（任意设备）
2. 运行应用
3. 如果模拟器可以运行，问题可能是设备特定的（签名、证书等）

## 常见原因和解决方案

### 原因 1：启动超时（Watchdog）
- **症状**：应用启动时间过长
- **解决**：检查是否有同步的网络请求或阻塞操作

### 原因 2：签名/证书问题
- **症状**：设备上显示"未受信任的开发者"
- **解决**：在设备设置中信任开发者证书

### 原因 3：动态库加载失败
- **症状**：`dyld: Library not loaded`
- **解决**：运行 `npx cap sync ios` 重新同步

### 原因 4：内存问题
- **症状**：应用启动时内存占用过高
- **解决**：检查启动时的资源加载

## 诊断命令

```bash
# 检查 Xcode 版本
xcodebuild -version

# 检查设备连接
xcrun xctrace list devices

# 重新同步 Capacitor
cd /Users/scarlett/Projects/BeatSync
npx cap clean ios
npx cap sync ios
```

## 如果仍然失败

请提供以下信息：
1. Xcode 控制台的完整错误日志
2. 设备日志（Window → Devices and Simulators → Open Console）
3. Xcode 版本
4. iOS 设备型号和系统版本
