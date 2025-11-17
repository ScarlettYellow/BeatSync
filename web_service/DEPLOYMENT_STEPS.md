# BeatSync Web服务部署步骤

## 快速部署指南

### 方案：Render（后端）+ GitHub Pages（前端）

---

## 第一步：部署后端到Render

### 1. 准备工作

确保以下文件已准备好：
- ✅ `web_service/backend/main.py` - 后端主程序
- ✅ `web_service/backend/requirements.txt` - Python依赖
- ✅ `render.yaml` - Render配置文件（已创建）
- ✅ `web_service/backend/start.sh` - 启动脚本（已创建）

### 2. 在Render上创建服务

1. **访问Render**
   - 打开 https://render.com
   - 使用GitHub账号登录（推荐）

2. **创建Web Service**
   - 点击 "New +" → "Web Service"
   - 选择 "Connect GitHub" 连接你的仓库
   - 选择 `BeatSync` 仓库

3. **配置服务**
   - **Name**: `beatsync-backend`
   - **Region**: 选择离你最近的区域（如 `Singapore`）
   - **Branch**: `main`
   - **Root Directory**: 留空（使用根目录）
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r web_service/backend/requirements.txt`
   - **Start Command**: `cd web_service/backend && uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Plan**: `Free`

4. **环境变量（可选）**
   - 点击 "Advanced" → "Add Environment Variable"
   - 添加 `ALLOWED_ORIGINS` = `https://你的用户名.github.io,http://localhost:8000`
   - 如果不设置，默认允许所有来源（仅用于测试）

5. **创建服务**
   - 点击 "Create Web Service"
   - 等待部署完成（约5-10分钟）

6. **获取后端URL**
   - 部署成功后，Render会提供一个URL
   - 格式：`https://beatsync-backend.onrender.com`
   - **重要**：记下这个URL，下一步需要用到

---

## 第二步：更新前端配置

### 1. 更新API地址

编辑 `web_service/frontend/script.js`，找到：

```javascript
// TODO: 替换为实际的Render后端URL
return window.API_BASE_URL || 'https://beatsync-backend.onrender.com';
```

将 `https://beatsync-backend.onrender.com` 替换为你实际的Render后端URL。

### 2. 提交更改

```bash
git add web_service/frontend/script.js
git commit -m "feat: 更新前端API地址为Render后端URL"
git push
```

---

## 第三步：部署前端到GitHub Pages

### 1. 启用GitHub Pages

1. 在GitHub仓库页面，点击 "Settings"
2. 左侧菜单选择 "Pages"
3. 在 "Source" 部分：
   - 选择 "GitHub Actions"
4. 点击 "Save"

### 2. 触发部署

GitHub Actions会自动检测到 `.github/workflows/deploy-pages.yml` 文件，并在以下情况自动部署：
- 推送到 `main` 分支
- `web_service/frontend/` 目录下的文件有变化

### 3. 查看部署状态

1. 在GitHub仓库页面，点击 "Actions" 标签
2. 查看 "Deploy to GitHub Pages" 工作流
3. 等待部署完成（约1-2分钟）

### 4. 访问前端

部署完成后，访问：
- `https://你的用户名.github.io/BeatSync/`

**注意**：如果仓库名不是 `BeatSync`，URL会是 `https://你的用户名.github.io/仓库名/`

---

## 第四步：配置CORS（重要）

### 1. 在Render上设置环境变量

1. 进入Render Dashboard
2. 选择 `beatsync-backend` 服务
3. 点击 "Environment"
4. 添加环境变量：
   - **Key**: `ALLOWED_ORIGINS`
   - **Value**: `https://你的用户名.github.io,http://localhost:8000`
   - 多个域名用逗号分隔
5. 点击 "Save Changes"
6. Render会自动重新部署

### 2. 验证CORS配置

部署完成后，测试前端是否能正常访问后端API。

---

## 测试部署

### 1. 测试后端

在浏览器访问：
```
https://你的Render后端URL/api/health
```

应该返回：
```json
{"status": "ok"}
```

### 2. 测试前端

1. 访问GitHub Pages URL
2. 打开浏览器开发者工具（F12）
3. 尝试上传文件并处理
4. 检查Network标签，确认API请求是否成功

---

## 常见问题

### Q1: Render服务休眠

**A**: Render免费层在15分钟无活动后会休眠。首次访问需要几秒唤醒，这是正常的。

**解决方案**：
- 使用免费监控服务（如UptimeRobot）定期ping你的后端URL
- 或升级到付费计划（$7/月起）

### Q2: CORS错误

**A**: 检查以下几点：
1. Render环境变量 `ALLOWED_ORIGINS` 是否设置正确
2. 前端API地址是否正确
3. 浏览器控制台是否有具体错误信息

### Q3: 文件上传失败

**A**: 可能的原因：
1. 文件太大（Render免费层有大小限制）
2. 网络超时
3. 后端服务正在休眠（首次访问）

### Q4: GitHub Pages 404错误

**A**: 检查：
1. GitHub Pages是否已启用
2. Actions工作流是否成功
3. 仓库设置中的Pages配置是否正确

---

## 后续优化

1. **添加监控**：使用UptimeRobot等免费服务监控后端可用性
2. **优化启动时间**：减少依赖，优化代码
3. **添加CDN**：使用Cloudflare加速前端资源
4. **自定义域名**：如果有域名，可以配置到Render和GitHub Pages

---

## 部署检查清单

- [ ] Render后端服务已创建
- [ ] 后端URL已获取
- [ ] 前端API地址已更新
- [ ] 代码已提交并推送到GitHub
- [ ] GitHub Pages已启用
- [ ] GitHub Actions部署成功
- [ ] CORS环境变量已配置
- [ ] 后端健康检查通过
- [ ] 前端可以正常访问
- [ ] 文件上传功能正常
- [ ] 处理功能正常
- [ ] 下载功能正常

---

## 需要帮助？

如果遇到问题，请检查：
1. Render Dashboard的日志
2. GitHub Actions的日志
3. 浏览器开发者工具的控制台和网络标签

