# iOS App 启动崩溃修复 - 已应用

## 修复时间
2025-01-06

## 已执行的修复步骤

### 1. 禁用 SaveToGalleryPlugin
- ✅ 注释了 `ios/App/SaveToGalleryPlugin.m` 中的插件注册
- ✅ 重命名了 `ios/App/SaveToGalleryPlugin.swift` → `SaveToGalleryPlugin.swift.disabled`

### 2. 禁用 SubscriptionPlugin
- ✅ `ios/App/SubscriptionPlugin.m` 已注释（之前已完成）
- ✅ 重命名了 `ios/App/SubscriptionPlugin.swift` → `SubscriptionPlugin.swift.disabled`
- ✅ 重命名了 `ios/App/Plugins/SubscriptionPlugin.swift` → `SubscriptionPlugin.swift.disabled`

## 当前状态

所有自定义插件已临时禁用：
- ❌ SaveToGalleryPlugin（已禁用）
- ❌ SubscriptionPlugin（已禁用）

## 下一步测试步骤

### 1. 清理构建缓存
```bash
# 清理 Xcode DerivedData
rm -rf ~/Library/Developer/Xcode/DerivedData

# 在 Xcode 中：
# Product → Clean Build Folder (Shift+Cmd+K)
```

### 2. 重新同步 Capacitor
```bash
cd /Users/scarlett/Projects/BeatSync
npx cap sync ios
```

### 3. 在 Xcode 中重新编译
1. 打开 Xcode：`npx cap open ios`
2. 选择模拟器或真机
3. 点击运行（⌘R）

### 4. 如果应用能启动
说明问题出在自定义插件上，可以：
- 逐个启用插件，找出问题插件
- 修复插件问题后重新启用

### 5. 如果应用仍然崩溃
需要查看详细日志：
1. 在 Xcode 中：Window → Devices and Simulators
2. 选择设备 → Open Console
3. 过滤 "BeatSync" 或 "App"
4. 查看启动时的详细错误信息

## 可能的问题原因

1. **插件注册问题**：Capacitor 8 的插件注册机制变化
2. **依赖问题**：插件依赖的框架未正确链接
3. **权限问题**：Info.plist 中缺少必要的权限描述
4. **签名问题**：开发证书或 Provisioning Profile 配置错误

## 恢复插件的方法

如果应用能正常启动，需要恢复插件时：

```bash
cd /Users/scarlett/Projects/BeatSync/ios/App

# 恢复 SaveToGalleryPlugin
mv SaveToGalleryPlugin.swift.disabled SaveToGalleryPlugin.swift
# 然后取消注释 SaveToGalleryPlugin.m 中的注册代码

# 恢复 SubscriptionPlugin（如果需要）
mv SubscriptionPlugin.swift.disabled SubscriptionPlugin.swift
mv Plugins/SubscriptionPlugin.swift.disabled Plugins/SubscriptionPlugin.swift
# 然后取消注释 SubscriptionPlugin.m 中的注册代码
```

## 注意事项

- 这些文件只是重命名，没有删除，可以随时恢复
- 如果应用能启动，说明问题确实在插件上
- 建议逐个启用插件，找出具体是哪个插件导致的问题

