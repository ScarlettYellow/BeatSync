# BeatSync Web服务更新部署指南

## 当前部署状态

- ✅ **后端**：已部署到Render（`https://beatsync-backend-asha.onrender.com`）
- ✅ **前端**：已部署到GitHub Pages（`https://scarlettyellow.github.io/BeatSync/`）

## 更新部署步骤

### 方式1：自动更新（推荐）

只需推送代码到GitHub，系统会自动更新：

```bash
# 1. 添加所有修改
git add .

# 2. 提交更改
git commit -m "feat: 更新Web服务功能（修复V2版本、优化下载体验等）"

# 3. 推送到GitHub
git push origin main
```

**自动更新流程**：
1. **Render后端**：检测到代码更新后，自动重新构建和部署
2. **GitHub Pages前端**：GitHub Actions检测到 `web_service/frontend/` 目录变化后，自动重新部署

### 方式2：手动触发更新

如果需要立即更新：

1. **Render后端**：
   - 访问Render Dashboard
   - 选择 `beatsync-backend` 服务
   - 点击 "Manual Deploy" → "Deploy latest commit"

2. **GitHub Pages前端**：
   - 访问GitHub仓库
   - 进入 "Actions" 标签
   - 找到 "Deploy to GitHub Pages" 工作流
   - 点击 "Run workflow" → "Run workflow"

## 更新内容检查

本次更新包括：

### 后端更新
- ✅ 修复V2版本处理失败问题
- ✅ 修复modular版本模块2失败问题
- ✅ 增强异常处理，即使有异常也能正确识别成功状态
- ✅ 修复状态消息逻辑错误
- ✅ 优化下载响应头，支持断点续传

### 前端更新
- ✅ 优化下载功能，支持Web Share API保存到相册
- ✅ 修复状态文本和按钮状态不一致问题
- ✅ 更新按钮文案（"下载Modular算法结果" / "下载V2算法结果"）
- ✅ 优化移动端下载体验
- ✅ 添加favicon图标

## 部署后验证

### 1. 检查后端
- 访问：`https://beatsync-backend-asha.onrender.com/docs`
- 应该能看到API文档

### 2. 检查前端
- 访问：`https://scarlettyellow.github.io/BeatSync/`
- 应该能看到更新后的界面

### 3. 测试完整流程
- 上传两个视频文件
- 点击"开始处理"
- 等待处理完成
- 测试下载功能

## 注意事项

1. **CORS配置**：确保Render上的 `ALLOWED_ORIGINS` 环境变量包含：
   - `https://scarlettyellow.github.io`
   - `http://localhost:8000`

2. **部署时间**：
   - Render后端：约5-10分钟
   - GitHub Pages前端：约1-2分钟

3. **如果更新失败**：
   - 检查Render日志
   - 检查GitHub Actions日志
   - 查看错误信息并修复

## 相关文件

- `render.yaml` - Render部署配置
- `.github/workflows/deploy-pages.yml` - GitHub Pages部署
- `web_service/backend/requirements.txt` - Python依赖
- `web_service/backend/start.sh` - 启动脚本

