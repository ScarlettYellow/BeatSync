# 域名迁移完成指南

> **域名**：beatsync.site  
> **状态**：ICP 备案已通过  
> **目标**：将服务从 IP 地址迁移到正式域名

---

## ✅ 已完成的代码修改

### 1. 前端 API 地址更新
- ✅ `web_service/frontend/script.js` 
  - Capacitor 原生环境：`http://124.221.58.149` → `https://beatsync.site`
  - 生产环境：`https://124.221.58.149` → `https://beatsync.site`
  - 错误提示信息已更新

### 2. Capacitor 配置更新
- ✅ `capacitor.config.json`
  - 添加 `server.url: "https://beatsync.site"`
  - `allowNavigation` 改为 `beatsync.site`
  - `cleartext: false`（启用 HTTPS）

### 3. iOS App Transport Security 恢复
- ✅ `ios/App/App/Info.plist`
  - 移除了 `124.221.58.149` 的 ATS 例外
  - 移除了 `NSAllowsArbitraryLoads` 等不安全设置
  - 恢复标准 ATS 安全设置

---

## 🔧 需要手动完成的服务器端配置

### 4. Nginx SSL 证书配置

**在服务器上执行**：

```bash
# 1. 确认 DNS 解析已生效
nslookup beatsync.site
# 应该返回：124.221.58.149

# 2. 安装 Certbot（如果未安装）
sudo apt update
sudo apt install -y certbot python3-certbot-nginx

# 3. 申请 Let's Encrypt 证书（自动配置 Nginx）
sudo certbot --nginx -d beatsync.site

# 4. 验证 Nginx 配置
sudo nginx -t

# 5. 重启 Nginx
sudo systemctl restart nginx

# 6. 检查证书状态
sudo certbot certificates
```

**验证 HTTP 到 HTTPS 跳转**：

```bash
# 测试 HTTP 跳转
curl -I http://beatsync.site/api/health
# 应该返回：Location: https://beatsync.site/api/health

# 测试 HTTPS 访问
curl -I https://beatsync.site/api/health
# 应该返回：HTTP/2 200
```

**Nginx 配置应该包含**：

```nginx
# HTTP 跳转到 HTTPS
server {
    listen 80;
    server_name beatsync.site;
    return 301 https://$server_name$request_uri;
}

# HTTPS 服务
server {
    listen 443 ssl http2;
    server_name beatsync.site;
    
    ssl_certificate /etc/letsencrypt/live/beatsync.site/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/beatsync.site/privkey.pem;
    
    # ... 其他配置（反向代理到 FastAPI，文件上传大小限制等）
}
```

---

### 5. 后端 CORS 配置

**检查后端环境变量**：

```bash
# 在服务器上检查环境变量
echo $ALLOWED_ORIGINS

# 如果未设置或需要更新，编辑环境变量配置
# 方法1：如果使用 systemd service
sudo systemctl edit beatsync-backend

# 方法2：如果使用 .env 文件
sudo nano /opt/beatsync/.env
```

**更新 CORS 配置**：

```bash
# 设置环境变量（根据实际情况选择方法）
export ALLOWED_ORIGINS="https://beatsync.site,http://localhost:8000"

# 或者在 .env 文件中添加/修改
ALLOWED_ORIGINS=https://beatsync.site,http://localhost:8000
```

**如果使用 CDN**，还需要添加 CDN 域名：

```bash
ALLOWED_ORIGINS=https://beatsync.site,https://cdn.beatsync.site,http://localhost:8000
```

**重启后端服务**：

```bash
# 如果使用 systemd
sudo systemctl restart beatsync-backend

# 或重启 Python 服务
sudo supervisorctl restart beatsync-api
# 或其他进程管理工具
```

**验证 CORS 配置**：

```bash
# 测试 CORS 响应头
curl -I -H "Origin: https://beatsync.site" https://beatsync.site/api/health

# 应该看到：Access-Control-Allow-Origin: https://beatsync.site
```

---

### 6. CDN 加速配置

**在腾讯云控制台操作**：

#### 步骤 1：开通 CDN 服务
1. 登录腾讯云控制台：https://console.cloud.tencent.com/
2. 进入 CDN 控制台：https://console.cloud.tencent.com/cdn
3. 如果未开通，点击"开通 CDN"

#### 步骤 2：添加加速域名
1. 点击"域名管理" → "添加域名"
2. 填写域名信息：
   - **加速域名**：`beatsync.site`
   - **加速区域**：中国境内
   - **加速类型**：CDN 网页小文件
   - **源站类型**：源站域名（推荐）或源站 IP
   - **源站地址**：
     - 源站域名：`beatsync.site`（推荐）
     - 或源站 IP：`124.221.58.149`
   - **回源协议**：HTTPS（443 端口）
   - **回源 Host**：`beatsync.site`（如果使用源站域名，保持默认）

3. 点击"提交"

#### 步骤 3：配置 HTTPS
1. 进入域名配置 → "HTTPS 配置"
2. 上传 SSL 证书或使用 Let's Encrypt 证书
3. 开启 HTTPS 加速
4. 开启 HTTP/2（如果支持）

#### 步骤 4：配置缓存规则
1. 进入"缓存配置"
2. 配置视频文件缓存：
   - **文件类型**：`.mp4`, `.avi`, `.mov`, `.mkv`
   - **缓存时间**：7 天
   - **忽略参数**：开启

3. 配置 API 接口（不缓存）：
   - **路径**：`/api/*`
   - **缓存时间**：0 秒（不缓存）

#### 步骤 5：等待 CDN 生效
- CDN 配置通常 5-30 分钟生效
- 可以通过 CDN 控制台查看配置状态

#### 步骤 6：更新 DNS 解析（可选）
如果使用 CDN 提供的 CNAME，需要：
1. 在 CDN 控制台获取 CNAME 地址
2. 在 DNS 解析控制台添加 CNAME 记录
3. 等待 DNS 生效

**注意**：如果使用主域名 CNAME，需要先删除原有的 A 记录。

---

## ✅ 验证清单

完成所有配置后，请验证以下项目：

### 代码层面
- [x] 前端 API 地址已更新为 `https://beatsync.site`
- [x] Capacitor 配置已更新
- [x] iOS ATS 已恢复安全设置

### 服务器端
- [ ] DNS 解析正确（`nslookup beatsync.site` 返回 `124.221.58.149` 或 CDN IP）
- [ ] HTTP 自动跳转到 HTTPS
- [ ] HTTPS 证书有效（浏览器显示 🔒）
- [ ] 健康检查正常（`https://beatsync.site/api/health` 返回 `healthy`）
- [ ] CORS 配置正确（浏览器开发者工具 Network 标签检查响应头）
- [ ] 文件上传功能正常
- [ ] 文件下载功能正常

### CDN（如果配置）
- [ ] CDN 域名已添加并生效
- [ ] HTTPS 证书已配置
- [ ] 缓存规则已配置
- [ ] 回源配置正确

---

## 🧪 测试步骤

### 1. Web 端测试
```bash
# 测试健康检查
curl https://beatsync.site/api/health

# 应该返回：{"status":"healthy"}
```

在浏览器中：
1. 访问 `https://beatsync.site`
2. 检查浏览器地址栏是否显示 🔒
3. 检查控制台是否有错误
4. 测试文件上传和处理功能

### 2. iOS App 测试
1. 重新编译并安装 App：
   ```bash
   cd ios/App
   npx cap sync
   # 在 Xcode 中重新编译并安装
   ```
2. 打开 App，测试：
   - 连接后端服务
   - 文件上传
   - 文件处理
   - 文件下载

### 3. 功能测试
- [ ] 上传舞蹈视频
- [ ] 上传 BGM 视频
- [ ] 开始处理任务
- [ ] 查看处理状态
- [ ] 下载处理结果（modular 和 v2 版本）

---

## 📝 常见问题

### 问题 1：SSL 证书错误
**症状**：浏览器显示"您的连接不是私密连接"

**解决方法**：
1. 确认 Let's Encrypt 证书已正确申请
2. 检查 Nginx 配置中的证书路径
3. 验证证书有效期：`sudo certbot certificates`

### 问题 2：CORS 错误
**症状**：浏览器控制台显示 CORS 错误

**解决方法**：
1. 检查后端 `ALLOWED_ORIGINS` 环境变量
2. 确认包含 `https://beatsync.site`
3. 重启后端服务

### 问题 3：iOS App 无法连接
**症状**：App 显示连接失败

**解决方法**：
1. 确认 `capacitor.config.json` 中的 `server.url` 正确
2. 确认 `Info.plist` 中没有阻止 HTTPS 连接
3. 在 Xcode 中重新编译 App

### 问题 4：CDN 回源失败
**症状**：通过 CDN 访问失败

**解决方法**：
1. 检查 CDN 源站配置（IP 或域名）
2. 检查回源协议（应该是 HTTPS）
3. 检查回源 Host 配置

---

## 📚 相关文档

- `docs/deployment/BEATSYNC_SITE_DOMAIN_SETUP.md` - 域名配置详细指南
- `docs/deployment/LETS_ENCRYPT_SSL_SETUP.md` - Let's Encrypt SSL 证书配置
- `docs/deployment/CDN_SETUP_GUIDE.md` - CDN 加速配置指南
- `docs/deployment/NGINX_CORS_AND_FILE_SIZE_FIX.md` - Nginx 配置参考

---

**最后更新**：2025-12-13
