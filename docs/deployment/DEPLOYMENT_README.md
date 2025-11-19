# BeatSync Web服务部署指南

## 快速部署

### 方案：Render（后端）+ GitHub Pages（前端）

---

## 部署步骤

### 第一步：部署后端到Render

1. **访问Render**
   - 打开 https://render.com
   - 使用GitHub账号登录

2. **创建Web Service**
   - 点击 "New +" → "Web Service"
   - 选择 "Connect GitHub" 连接仓库
   - 选择 `BeatSync` 仓库

3. **配置服务**
   - **Name**: `beatsync-backend`
   - **Region**: 选择离你最近的区域
   - **Branch**: `main`
   - **Root Directory**: 留空
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r web_service/backend/requirements.txt`
   - **Start Command**: `cd web_service/backend && uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Plan**: 选择适合的计划

4. **环境变量（重要）**
   - 点击 "Advanced" → "Add Environment Variable"
   - 添加 `ALLOWED_ORIGINS` = `https://你的用户名.github.io,http://localhost:8000`
   - 例如：`ALLOWED_ORIGINS` = `https://scarlettyellow.github.io,http://localhost:8000`

5. **创建服务**
   - 点击 "Create Web Service"
   - 等待部署完成（约5-10分钟）
   - **记录后端URL**（例如：`https://beatsync-backend-xxx.onrender.com`）

### 第二步：更新前端配置

1. **更新后端URL**
   - 编辑 `web_service/frontend/script.js`
   - 找到第15行：`const backendUrl = window.API_BASE_URL || 'https://beatsync-backend-asha.onrender.com';`
   - 将 `https://beatsync-backend-asha.onrender.com` 替换为你的Render后端URL

2. **提交代码**
   ```bash
   git add web_service/frontend/script.js
   git commit -m "更新后端URL为Render地址"
   git push origin main
   ```

### 第三步：部署前端到GitHub Pages

1. **启用GitHub Pages**
   - 打开GitHub仓库设置
   - 进入 "Pages" 设置
   - Source选择 "GitHub Actions"

2. **自动部署**
   - 推送代码到 `main` 分支后，GitHub Actions会自动部署
   - 前端地址：`https://你的用户名.github.io/BeatSync/`

3. **验证部署**
   - 访问前端地址
   - 测试完整流程

## 部署后验证

### 后端验证
- ✅ 访问 `https://你的后端URL/docs` 查看API文档
- ✅ 访问 `https://你的后端URL/api/health` 检查健康状态
- ✅ 检查Render日志，确认服务正常运行

### 前端验证
- ✅ 访问GitHub Pages地址
- ✅ 测试文件上传
- ✅ 测试视频处理
- ✅ 测试下载功能

## 重要提示

1. **CORS配置**：确保 `ALLOWED_ORIGINS` 环境变量包含前端URL
2. **后端URL**：部署后需要更新前端代码中的后端URL
3. **性能考虑**：Render免费层有资源限制，处理大文件可能需要较长时间

## 相关文档

- `docs/DEPLOYMENT_CHECKLIST.md` - 详细检查清单
- `web_service/DEPLOYMENT_STEPS.md` - 详细部署步骤
- `docs/DEPLOYMENT_GUIDE.md` - 部署方案分析

