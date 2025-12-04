# 前端域名配置方案

> **问题**：为什么前端页面没有使用域名？  
> **当前状态**：前端在GitHub Pages，后端在beatsync.site  
> **解决方案**：将前端也配置到域名（子域名或主域名）

---

## 当前架构

### 前端部署
- **当前地址**：`https://scarlettyellow.github.io/BeatSync/`
- **部署方式**：GitHub Pages（免费）
- **域名**：未配置自定义域名

### 后端部署
- **当前地址**：`https://beatsync.site`
- **部署方式**：腾讯云服务器 + Nginx
- **域名**：已配置 `beatsync.site`

---

## 为什么前端没有使用域名？

### GitHub Pages 限制

1. **免费版不支持自定义域名**（或需要额外配置）
2. **自定义域名需要验证**：需要在GitHub仓库中配置CNAME文件
3. **DNS配置**：需要在域名服务商处配置DNS解析

### 当前架构优势

- ✅ **免费**：GitHub Pages完全免费
- ✅ **自动部署**：代码推送后自动更新
- ✅ **CDN加速**：GitHub Pages自带CDN
- ✅ **简单**：无需服务器维护

---

## 解决方案

### 方案1：GitHub Pages + 自定义域名（推荐）

**优点**：
- ✅ 保持GitHub Pages的自动部署优势
- ✅ 免费使用
- ✅ 前端使用 `www.beatsync.site` 或 `app.beatsync.site`
- ✅ 后端使用 `beatsync.site` 或 `api.beatsync.site`

**步骤**：

#### 1. 在GitHub仓库中配置CNAME

**创建文件**：`web_service/frontend/CNAME`

**内容**（选择一种）：
```
www.beatsync.site
```
或
```
app.beatsync.site
```

#### 2. 在腾讯云DNS中配置解析

**添加CNAME记录**：
- **主机记录**：`www` 或 `app`
- **记录类型**：`CNAME`
- **记录值**：`scarlettyellow.github.io`
- **TTL**：600

**或者添加A记录**（如果GitHub提供IP）：
- **主机记录**：`www` 或 `app`
- **记录类型**：`A`
- **记录值**：GitHub Pages的IP地址（需要查询）

#### 3. 在GitHub Pages设置中启用自定义域名

1. 进入GitHub仓库
2. Settings → Pages
3. 在"Custom domain"中输入：`www.beatsync.site` 或 `app.beatsync.site`
4. 保存

#### 4. 更新前端代码中的API地址（如果需要）

如果使用子域名，可能需要更新前端代码：
- 前端：`www.beatsync.site`
- 后端：`beatsync.site` 或 `api.beatsync.site`

---

### 方案2：在服务器上部署前端（完整控制）

**优点**：
- ✅ 完全控制前端部署
- ✅ 可以使用主域名 `beatsync.site`
- ✅ 后端可以使用 `api.beatsync.site`

**缺点**：
- ❌ 需要服务器资源
- ❌ 需要手动部署（或配置CI/CD）

**步骤**：

#### 1. 在服务器上创建前端目录

```bash
# 创建前端目录
sudo mkdir -p /var/www/beatsync

# 设置权限
sudo chown -R ubuntu:ubuntu /var/www/beatsync
```

#### 2. 部署前端文件

**从GitHub克隆或上传前端文件**：
```bash
cd /var/www/beatsync
git clone https://github.com/scarlettyellow/BeatSync.git .
# 或使用rsync上传
```

#### 3. 配置Nginx提供前端静态文件

**更新Nginx配置**：
```bash
sudo tee /etc/nginx/sites-available/beatsync > /dev/null << 'EOFNGINX'
server {
    listen 80;
    listen [::]:80;
    server_name beatsync.site www.beatsync.site;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name beatsync.site www.beatsync.site;

    ssl_certificate /etc/letsencrypt/live/beatsync.site/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/beatsync.site/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    # 前端静态文件
    root /var/www/beatsync/web_service/frontend;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    # 后端API代理
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # API文档
    location /docs {
        proxy_pass http://127.0.0.1:8000/docs;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOFNGINX

# 重新加载Nginx
sudo nginx -t && sudo systemctl reload nginx
```

#### 4. 更新前端代码中的API地址

**文件**：`web_service/frontend/script.js`

**修改**：
```javascript
// 如果前端和后端在同一域名，使用相对路径
const backendUrl = window.API_BASE_URL || '/api';
```

---

### 方案3：使用子域名分离前后端（推荐架构）

**架构**：
- **前端**：`www.beatsync.site` 或 `app.beatsync.site`（GitHub Pages）
- **后端**：`api.beatsync.site` 或 `beatsync.site`

**优点**：
- ✅ 前后端分离，架构清晰
- ✅ 前端使用GitHub Pages（免费、自动部署）
- ✅ 后端独立部署（灵活、可控）

**步骤**：

#### 1. 配置前端子域名（GitHub Pages）

**创建CNAME文件**：`web_service/frontend/CNAME`
```
www.beatsync.site
```

**在GitHub Pages设置中启用**：`www.beatsync.site`

**在DNS中添加CNAME记录**：
- **主机记录**：`www`
- **记录类型**：`CNAME`
- **记录值**：`scarlettyellow.github.io`

#### 2. 配置后端子域名（可选）

**如果使用 `api.beatsync.site`**：

**在DNS中添加A记录**：
- **主机记录**：`api`
- **记录类型**：`A`
- **记录值**：`124.221.58.149`

**更新Nginx配置**：
```bash
# 在server_name中添加api.beatsync.site
server_name beatsync.site api.beatsync.site;
```

**更新前端代码**：
```javascript
const backendUrl = window.API_BASE_URL || 'https://api.beatsync.site';
```

---

## 推荐方案对比

| 方案 | 前端地址 | 后端地址 | 优点 | 缺点 |
|------|---------|---------|------|------|
| **方案1** | `www.beatsync.site` (GitHub Pages) | `beatsync.site` | 免费、自动部署 | 需要配置CNAME |
| **方案2** | `beatsync.site` | `api.beatsync.site` | 完全控制 | 需要服务器资源 |
| **方案3** | `www.beatsync.site` (GitHub Pages) | `api.beatsync.site` | 架构清晰、分离 | 需要配置两个域名 |

---

## 推荐选择

### 如果希望保持简单

**推荐方案1**：
- 前端：`www.beatsync.site`（GitHub Pages）
- 后端：`beatsync.site`
- 优点：免费、自动部署、简单

### 如果希望架构清晰

**推荐方案3**：
- 前端：`www.beatsync.site`（GitHub Pages）
- 后端：`api.beatsync.site`
- 优点：前后端分离、架构清晰、易于扩展

---

## 实施步骤（方案1示例）

### 步骤1：创建CNAME文件

**在本地创建文件**：`web_service/frontend/CNAME`

**内容**：
```
www.beatsync.site
```

### 步骤2：提交到GitHub

```bash
cd /Users/scarlett/Projects/BeatSync
git add web_service/frontend/CNAME
git commit -m "feat: 添加前端自定义域名配置"
git push origin main
```

### 步骤3：在GitHub Pages中启用

1. 进入GitHub仓库：https://github.com/scarlettyellow/BeatSync
2. Settings → Pages
3. 在"Custom domain"中输入：`www.beatsync.site`
4. 保存

### 步骤4：在腾讯云DNS中配置

**添加CNAME记录**：
- **主机记录**：`www`
- **记录类型**：`CNAME`
- **记录值**：`scarlettyellow.github.io`
- **TTL**：600

### 步骤5：等待DNS生效

**验证DNS解析**：
```bash
nslookup www.beatsync.site 8.8.8.8
```

**预期结果**：
```
www.beatsync.site canonical name = scarlettyellow.github.io
```

---

## 验证清单

- [ ] CNAME文件已创建并提交
- [ ] GitHub Pages已启用自定义域名
- [ ] DNS解析已配置
- [ ] DNS解析已生效
- [ ] 前端可以通过域名访问
- [ ] 前端可以正常连接后端API

---

## 相关文档

- `docs/ARCHITECTURE_OVERVIEW.md` - 服务架构概览
- `docs/deployment/BACKEND_API_VERIFICATION.md` - 后端API验证

---

**最后更新**：2025-12-04

