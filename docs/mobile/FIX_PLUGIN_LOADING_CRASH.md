# 修复插件加载导致的 SIGKILL 崩溃

## 问题

应用在启动时因为插件加载问题导致 `signal SIGKILL` 崩溃。

## 已修复的问题

1. ✅ **Bridging Header 已更新** - 添加了 `#import <Capacitor/Capacitor.h>`

## 如果仍然崩溃，尝试以下方案

### 方案 1：临时禁用 SaveToGalleryPlugin（推荐先试这个）

如果 Bridging Header 修复后仍然崩溃，可能是 SaveToGalleryPlugin 导致的问题。

**临时禁用插件：**

1. **重命名插件文件（让 Xcode 找不到它们）：**
   ```bash
   cd /Users/scarlett/Projects/BeatSync/ios/App
   mv SaveToGalleryPlugin.swift SaveToGalleryPlugin.swift.disabled
   mv SaveToGalleryPlugin.m SaveToGalleryPlugin.m.disabled
   ```

2. **在 Xcode 中：**
   - 如果文件还在项目中，右键 → Delete → Remove Reference（不要移到废纸篓）
   - Product → Clean Build Folder (Shift+Cmd+K)
   - 重新编译运行

3. **如果应用可以启动，说明是插件问题**

### 方案 2：检查插件是否正确添加到编译目标

1. **在 Xcode 中：**
   - 选择 `SaveToGalleryPlugin.swift`
   - 查看右侧 File Inspector（⌘⌥1）
   - 确认 "Target Membership" 中 "App" 已勾选

2. **同样检查 `SaveToGalleryPlugin.m`**

### 方案 3：完全移除插件文件

如果方案 1 有效，可以完全移除插件：

```bash
cd /Users/scarlett/Projects/BeatSync/ios/App
rm SaveToGalleryPlugin.swift
rm SaveToGalleryPlugin.m
```

然后重新同步 Capacitor：
```bash
cd /Users/scarlett/Projects/BeatSync
npx cap sync ios
```

### 方案 4：检查是否有重复的插件文件

检查是否有重复的插件定义导致冲突：

```bash
cd /Users/scarlett/Projects/BeatSync/ios
find . -name "*SaveToGallery*" -type f
find . -name "*SubscriptionPlugin*" -type f
```

如果发现重复文件，只保留一个版本。

## 验证修复

1. **清理并重新编译：**
   ```bash
   rm -rf ~/Library/Developer/Xcode/DerivedData
   ```
   在 Xcode 中：Product → Clean Build Folder (Shift+Cmd+K)

2. **在设备上删除应用**

3. **重新编译并运行**

## 如果仍然失败

请提供：
1. Xcode 控制台的完整错误日志
2. 设备日志（Window → Devices and Simulators → Open Console）
3. 执行 `find . -name "*Plugin*" -type f` 的输出


