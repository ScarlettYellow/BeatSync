# PWA支持实现计划

> **目标**：添加PWA支持，使BeatSync可以添加到主屏幕  
> **功能**：Web App Manifest + Service Worker（基础版）

---

## 当前版本信息

### Git版本
- **最新标签**：`v1.3.0`
- **当前Commit**：`90ec1d6`
- **版本描述**：`v1.3.0-202-g90ec1d6-dirty`
- **状态**：开发中（有未提交修改）

### 技术栈
- **前端**：HTML5 + CSS3 + 原生JavaScript（无框架）
- **部署**：GitHub Pages
- **后端**：FastAPI on 腾讯云

---

## PWA实现方案

### 核心功能

1. **Web App Manifest**（必需）
   - 定义应用名称、图标、主题色等
   - 支持添加到主屏幕
   - 全屏/独立窗口模式

2. **Service Worker**（可选，基础版）
   - 缓存静态资源
   - 提升加载速度
   - 基础离线支持（可选）

---

## 实现步骤

### 步骤1：创建Web App Manifest

**文件**：`web_service/frontend/manifest.json`

**内容**：
- 应用名称和描述
- 图标配置（使用现有favicon）
- 主题色和背景色
- 显示模式（standalone）
- 启动URL

---

### 步骤2：创建Service Worker

**文件**：`web_service/frontend/sw.js`

**功能**：
- 缓存静态资源（HTML、CSS、JS）
- 网络优先策略（确保API请求实时）
- 版本控制（更新时清除旧缓存）

---

### 步骤3：更新index.html

**添加**：
- Manifest链接
- Service Worker注册代码
- 安装提示（可选）

---

### 步骤4：创建图标文件（如果需要）

**检查**：
- 已有favicon.ico和favicon.svg
- 可能需要不同尺寸的图标（192x192, 512x512）

---

## 实现细节

### Web App Manifest配置

```json
{
  "name": "BeatSync 视频音轨自动对齐和替换",
  "short_name": "BeatSync",
  "description": "智能视频音轨自动对齐和替换工具",
  "start_url": "/BeatSync/",
  "display": "standalone",
  "background_color": "#ffffff",
  "theme_color": "#007AFF",
  "orientation": "portrait-primary",
  "icons": [
    {
      "src": "favicon.svg",
      "sizes": "any",
      "type": "image/svg+xml"
    },
    {
      "src": "favicon.ico",
      "sizes": "48x48",
      "type": "image/x-icon"
    }
  ]
}
```

---

### Service Worker策略

**缓存策略**：
- **静态资源**（HTML、CSS、JS）：缓存优先
- **API请求**：网络优先（确保实时性）
- **版本控制**：使用版本号控制缓存更新

---

## 浏览器支持

### PWA支持情况

- ✅ **Chrome/Edge**：完全支持
- ✅ **Safari（iOS 11.3+）**：支持添加到主屏幕
- ✅ **Firefox**：支持
- ⚠️ **微信内置浏览器**：部分支持（可能不支持Service Worker）

---

## 测试清单

- [ ] Manifest文件正确配置
- [ ] Service Worker正确注册
- [ ] 可以添加到主屏幕（iOS/Android）
- [ ] 图标显示正确
- [ ] 独立窗口模式正常
- [ ] 缓存策略正常工作
- [ ] 更新机制正常工作

---

## 相关文档

- `docs/web-service/WEB_TO_APP_CONVERSION.md` - Web转App方案分析
- `docs/PROJECT_VERSION_INFO.md` - 项目版本信息

---

**最后更新**：2025-12-03

