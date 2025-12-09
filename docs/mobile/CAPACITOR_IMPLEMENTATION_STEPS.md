# Capacitor 实施步骤（已执行）

> 更新日期：2025-12-05

## 已完成
1. 初始化 Capacitor 项目  
   ```bash
   npx cap init BeatSync com.beatsync.app --web-dir web_service/frontend
   ```
2. 安装平台包  
   ```bash
   npm install @capacitor/ios @capacitor/android --save-dev
   ```
3. 添加平台  
   ```bash
   npx cap add ios
   npx cap add android
   ```
4. 配置 `capacitor.config.json`  
   ```json
   {
     "appId": "com.beatsync.app",
     "appName": "BeatSync",
     "webDir": "web_service/frontend",
     "server": {
       "url": "https://124.221.58.149",
       "cleartext": false
     }
   }
   ```
5. 同步资源  
   ```bash
   npx cap sync
   ```

## 图标和启动画面配置（进行中）

### 步骤 1: 生成应用图标 (1024x1024)
- 使用 macOS Preview 或在线工具将 `favicon.svg` 转换为 1024x1024 PNG
- 保存到：`ios/App/App/Assets.xcassets/AppIcon.appiconset/AppIcon-1024.png`
- 详细步骤：参考 `scripts/ios/generate_icons_manual.md`

### 步骤 2: 生成启动画面（白底+图标居中）
```bash
python3 scripts/ios/create_splash.py
```
脚本会自动创建三种尺寸的启动画面。

### 步骤 3: 在 Xcode 中验证
- 打开项目：`npx cap open ios`
- 检查 `App/Assets.xcassets` 中的 `AppIcon` 和 `Splash`

## 待办（备案通过后）
1. 将 `server.url` 改为正式域名（备案通过后替换临时 IP）
2. 在 Xcode 中配置 Bundle Identifier、版本号等
3. 连接 iPhone 进行真机调试
4. 打包并提交 App Store


