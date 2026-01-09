# 添加 SaveToGallery 插件到 Xcode 项目

## 说明

已创建自定义插件 `SaveToGalleryPlugin.swift` 用于直接保存视频到相册。需要在 Xcode 中手动添加此文件到项目。

## 步骤

1. **在 Xcode 中打开项目**
   - 确保项目已打开

2. **添加插件文件到项目**
   - 在 Xcode 左侧导航栏，找到 `App` → `App` 文件夹
   - 右键点击 `App` 文件夹
   - 选择 `Add Files to "App"...`
   - 导航到 `ios/App/App/SaveToGalleryPlugin.swift`
   - 确保勾选：
     - ✅ "Copy items if needed"（如果文件不在项目目录中）
     - ✅ "Create groups"（不是 folder references）
     - ✅ Target: "App" 被勾选
   - 点击 `Add`

3. **验证文件已添加**
   - 在左侧导航栏中应该能看到 `SaveToGalleryPlugin.swift` 文件
   - 点击文件，确保右侧显示 Swift 代码内容

4. **重新构建项目**
   - `Product` → `Clean Build Folder`（Shift + Command + K）
   - 然后 `Product` → `Build`（Command + B）

5. **测试**
   - 运行 App 到 iPhone
   - 测试下载功能，应该会：
     - 首次使用时请求相册权限
     - 权限允许后，视频直接保存到相册（不再弹出分享菜单）

## 注意事项

- 如果插件文件已经在项目目录中，`npx cap sync` 可能已经自动添加了
- 如果 Xcode 报错找不到 `SaveToGalleryPlugin`，说明文件未正确添加到项目中
- 确保 `Info.plist` 中已添加相册权限说明（已完成）

## 故障排除

如果插件仍然不可用：

1. 检查文件是否在 Xcode 项目中（左侧导航栏可见）
2. 检查 Target 是否包含此文件（选中文件，右侧 Inspector 中查看 Target Membership）
3. 清理并重新构建项目
4. 检查控制台是否有插件加载错误












