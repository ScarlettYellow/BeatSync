# BeatSync Web服务部署指南

## 部署方案对比

### 方案1：Render（后端）+ GitHub Pages（前端）⭐ **推荐**

**优点**：
- 完全免费
- Render免费层支持Python应用（FastAPI）
- GitHub Pages免费托管静态前端
- 配置简单，易于管理
- 自动HTTPS

**缺点**：
- 需要两个平台分别管理
- Render免费层在15分钟无活动后会休眠（首次访问需要几秒唤醒）

**适用场景**：个人项目、演示、小规模使用

---

### 方案2：Railway（全栈部署）

**优点**：
- 一个平台管理前后端
- 免费层可用（每月$5额度）
- 自动HTTPS
- 支持环境变量

**缺点**：
- 免费层有使用限制
- 超出额度需要付费

**适用场景**：需要统一管理的项目

---

### 方案3：Fly.io

**优点**：
- 免费层可用
- 全球CDN加速
- 支持Docker部署

**缺点**：
- 需要Docker配置
- 配置相对复杂

**适用场景**：需要全球加速的项目

---

## 推荐方案：Render + GitHub Pages

### 第一步：部署后端到Render

1. **准备部署文件**

创建 `render.yaml` 配置文件（在项目根目录）：

```yaml
services:
  - type: web
    name: beatsync-backend
    env: python
    buildCommand: pip install -r web_service/backend/requirements.txt
    startCommand: cd web_service/backend && uvicorn main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.0
```

2. **在Render上创建服务**

   - 访问 https://render.com
   - 注册/登录账号
   - 点击 "New +" → "Web Service"
   - 连接你的GitHub仓库
   - 选择仓库和分支
   - 配置：
     - **Name**: `beatsync-backend`
     - **Environment**: `Python 3`
     - **Build Command**: `pip install -r web_service/backend/requirements.txt`
     - **Start Command**: `cd web_service/backend && uvicorn main:app --host 0.0.0.0 --port $PORT`
     - **Plan**: `Free`
   - 点击 "Create Web Service"

3. **获取后端URL**

   - 部署完成后，Render会提供一个URL，例如：`https://beatsync-backend.onrender.com`
   - 记下这个URL，用于前端配置

---

### 第二步：部署前端到GitHub Pages

1. **修改前端API地址**

   编辑 `web_service/frontend/script.js`，将API地址改为环境变量或Render后端URL。

2. **创建GitHub Pages配置**

   在项目根目录创建 `.github/workflows/deploy-pages.yml`：

```yaml
name: Deploy to GitHub Pages

on:
  push:
    branches:
      - main
    paths:
      - 'web_service/frontend/**'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      
      - name: Deploy to GitHub Pages
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./web_service/frontend
```

3. **启用GitHub Pages**

   - 在GitHub仓库设置中，进入 "Pages"
   - Source选择 "GitHub Actions"
   - 保存设置

4. **获取前端URL**

   - GitHub Pages URL格式：`https://你的用户名.github.io/BeatSync/`
   - 或者使用自定义域名（如果有）

---

### 第三步：配置CORS

编辑 `web_service/backend/main.py`，更新CORS配置：

```python
# 配置CORS（允许前端跨域访问）
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://你的用户名.github.io",  # GitHub Pages域名
        "http://localhost:8000",  # 本地开发
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

### 第四步：环境变量配置（可选）

如果需要动态配置API地址，可以使用环境变量：

**前端** (`web_service/frontend/script.js`):
```javascript
// 根据环境自动选择API地址
const API_BASE_URL = window.location.hostname === 'localhost' 
    ? 'http://localhost:8000' 
    : 'https://beatsync-backend.onrender.com';
```

---

## 部署检查清单

- [ ] Render后端服务已创建并部署成功
- [ ] 后端URL已获取并测试可用
- [ ] 前端API地址已更新为后端URL
- [ ] CORS配置已更新，允许GitHub Pages域名
- [ ] GitHub Pages已启用并部署成功
- [ ] 前端可以正常访问后端API
- [ ] 文件上传和处理功能正常
- [ ] 下载功能正常

---

## 常见问题

### 1. Render服务休眠

**问题**：Render免费层在15分钟无活动后会休眠，首次访问需要几秒唤醒。

**解决**：
- 使用付费计划（$7/月起）
- 或使用外部监控服务定期ping（如UptimeRobot）

### 2. CORS错误

**问题**：前端访问后端时出现CORS错误。

**解决**：
- 检查后端CORS配置，确保包含前端域名
- 检查前端API地址是否正确

### 3. 文件上传大小限制

**问题**：上传大文件失败。

**解决**：
- Render免费层有文件大小限制
- 考虑添加文件大小检查和提示
- 或使用付费计划

---

## 其他部署选项

### Vercel（前端）+ Render（后端）

Vercel也可以免费托管前端，配置类似GitHub Pages。

### Railway（全栈）

Railway可以同时部署前后端，但免费层有使用限制。

---

## 后续优化建议

1. **添加环境变量管理**：使用Render的环境变量功能
2. **添加监控**：使用UptimeRobot等免费监控服务
3. **优化启动时间**：减少依赖，优化代码
4. **添加CDN**：使用Cloudflare加速前端资源

