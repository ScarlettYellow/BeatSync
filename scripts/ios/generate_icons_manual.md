# iOS 图标和启动画面生成指南

由于自动转换工具需要额外的系统依赖，这里提供手动步骤（只需 2-3 分钟）。

## 步骤 1: 生成应用图标 (1024x1024)

### 方法 A: 使用 macOS Preview（推荐）

1. 打开 `web_service/frontend/favicon.svg`
2. 菜单：**文件** → **导出...**
3. 格式选择：**PNG**
4. 点击 **选项...**，设置：
   - 宽度：`1024` 像素
   - 高度：`1024` 像素
   - 分辨率：`72` DPI（或更高）
5. 保存到：`ios/App/App/Assets.xcassets/AppIcon.appiconset/AppIcon-1024.png`

### 方法 B: 使用在线工具

1. 访问 https://cloudconvert.com/svg-to-png
2. 上传 `web_service/frontend/favicon.svg`
3. 设置尺寸：`1024x1024`
4. 下载并保存到：`ios/App/App/Assets.xcassets/AppIcon.appiconset/AppIcon-1024.png`

## 步骤 2: 生成启动画面（白底+图标居中）

运行以下 Python 脚本（需要 Pillow）：

```bash
python3 scripts/ios/create_splash.py
```

或者手动创建：

1. 使用图像编辑软件（如 Preview、Photoshop、GIMP）
2. 创建白色背景画布：
   - 尺寸 1: `2732x2732` → 保存为 `splash-2732x2732.png`
   - 尺寸 2: `1366x1366` → 保存为 `splash-2732x2732-1.png`
   - 尺寸 3: `683x683` → 保存为 `splash-2732x2732-2.png`
3. 在每个画布中心放置图标（图标大小约为画布的 1/3，即约 900px、450px、225px）
4. 保存到：`ios/App/App/Assets.xcassets/Splash.imageset/`

## 步骤 3: 验证

运行以下命令检查文件是否存在：

```bash
ls -lh ios/App/App/Assets.xcassets/AppIcon.appiconset/AppIcon-1024.png
ls -lh ios/App/App/Assets.xcassets/Splash.imageset/splash-*.png
```

## 完成！

完成后，在 Xcode 中打开项目检查：

```bash
npx cap open ios
```

