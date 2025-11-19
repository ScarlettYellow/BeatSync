# BeatSync Web服务部署检查清单

## 部署前检查

### ✅ 代码准备
- [x] 后端代码已完成开发
- [x] 前端代码已完成开发
- [x] 本地测试通过
- [x] 所有功能正常工作

### ✅ 配置文件
- [x] `render.yaml` - Render部署配置
- [x] `web_service/backend/requirements.txt` - Python依赖
- [x] `web_service/backend/start.sh` - 启动脚本
- [x] `.github/workflows/deploy-pages.yml` - GitHub Pages部署

### ✅ 功能验证
- [x] 文件上传功能正常
- [x] 视频处理功能正常
- [x] 异步处理功能正常
- [x] 进度更新功能正常
- [x] 下载功能正常
- [x] 错误处理完善

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
   - **Plan**: 选择适合的计划（Free/Starter/Standard）

4. **环境变量**
   - 点击 "Advanced" → "Add Environment Variable"
   - 添加 `ALLOWED_ORIGINS` = `https://你的用户名.github.io,http://localhost:8000`
   - 例如：`ALLOWED_ORIGINS` = `https://scarlettyellow.github.io,http://localhost:8000`

5. **创建服务**
   - 点击 "Create Web Service"
   - 等待部署完成（约5-10分钟）

6. **获取后端URL**
   - 部署成功后，Render会提供一个URL
   - 例如：`https://beatsync-backend-xxx.onrender.com`
   - **记录这个URL，下一步需要用到**

### 第二步：更新前端配置

1. **更新后端URL**
   - 编辑 `web_service/frontend/script.js`
   - 找到生产环境的后端URL配置
   - 更新为Render提供的URL

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
   - 推送代码到 `main` 分支
   - GitHub Actions会自动部署前端
   - 部署完成后，前端地址为：`https://你的用户名.github.io/BeatSync/`

3. **验证部署**
   - 访问前端地址
   - 测试完整流程

## 部署后验证

### 后端验证
- [ ] 访问 `https://你的后端URL/docs` 查看API文档
- [ ] 访问 `https://你的后端URL/api/health` 检查健康状态
- [ ] 检查Render日志，确认服务正常运行

### 前端验证
- [ ] 访问GitHub Pages地址
- [ ] 测试文件上传
- [ ] 测试视频处理
- [ ] 测试下载功能

### 完整流程验证
- [ ] 上传两个视频文件
- [ ] 点击"开始处理"
- [ ] 等待处理完成
- [ ] 下载结果视频

## 常见问题

### 1. CORS错误
- 检查 `ALLOWED_ORIGINS` 环境变量是否正确设置
- 确保前端URL包含在允许列表中

### 2. 处理超时
- Render免费层有资源限制
- 考虑升级到付费计划
- 或使用较小的测试视频

### 3. 依赖安装失败
- 检查 `requirements.txt` 是否正确
- 查看Render构建日志

## 相关文件

- `render.yaml` - Render部署配置
- `web_service/backend/requirements.txt` - Python依赖
- `web_service/backend/start.sh` - 启动脚本
- `.github/workflows/deploy-pages.yml` - GitHub Pages部署
- `web_service/DEPLOYMENT_STEPS.md` - 详细部署步骤

