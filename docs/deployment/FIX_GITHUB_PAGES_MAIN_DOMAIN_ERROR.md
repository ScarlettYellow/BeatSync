# 修复GitHub Pages主域名配置错误

> **错误**：`beatsync.site is improperly configured. Domain does not resolve to the GitHub Pages server.`  
> **原因**：GitHub Pages要求主域名也指向GitHub Pages，但主域名已用于后端API  
> **解决**：使用子域名分离前后端，或配置主域名也指向GitHub Pages（需要调整后端）

---

## 问题分析

### 当前状态

- ✅ **DNS解析正常**：`www.beatsync.site` 正确解析到 `scarlettyellow.github.io`
- ❌ **GitHub Pages报错**：`beatsync.site is improperly configured`

### 错误原因

GitHub Pages的要求：
- 如果使用 `www.beatsync.site`，**主域名 `beatsync.site` 也必须指向GitHub Pages**
- 或者只使用 `beatsync.site`（主域名），不使用www

**当前冲突**：
- 后端API已使用 `beatsync.site`
- GitHub Pages要求 `beatsync.site` 也指向GitHub Pages
- 两者冲突！

---

## 解决方案

### 方案1：使用子域名分离前后端（推荐）

**架构**：
- **前端**：`app.beatsync.site`（GitHub Pages）
- **后端**：`api.beatsync.site` 或 `beatsync.site`（腾讯云服务器）

**优点**：
- ✅ 前后端完全分离
- ✅ 避免域名冲突
- ✅ 架构清晰

**步骤**：

#### 1. 修改CNAME文件

**文件**：`web_service/frontend/CNAME`

**内容**：
```
app.beatsync.site
```

#### 2. 在GitHub Pages中更新域名

1. 进入GitHub仓库 → Settings → Pages
2. 在"Custom domain"中输入：`app.beatsync.site`
3. 保存

#### 3. 在腾讯云DNS中添加CNAME记录

**添加记录**：
- **主机记录**：`app`
- **记录类型**：`CNAME`
- **记录值**：`scarlettyellow.github.io`
- **TTL**：`600`

#### 4. 更新前端代码中的API地址

**文件**：`web_service/frontend/script.js`

**修改**：
```javascript
// 生产环境：使用腾讯云服务器（HTTPS）
const backendUrl = window.API_BASE_URL || 'https://beatsync.site';
```

**保持不变**（后端仍然使用 `beatsync.site`）

---

### 方案2：主域名指向GitHub Pages，后端使用子域名

**架构**：
- **前端**：`beatsync.site`（GitHub Pages）
- **后端**：`api.beatsync.site`（腾讯云服务器）

**优点**：
- ✅ 主域名用于前端（用户友好）
- ✅ 后端使用子域名（清晰）

**缺点**：
- ❌ 需要修改后端配置和前端代码

**步骤**：

#### 1. 修改CNAME文件

**文件**：`web_service/frontend/CNAME`

**内容**：
```
beatsync.site
```

#### 2. 在GitHub Pages中更新域名

1. 进入GitHub仓库 → Settings → Pages
2. 在"Custom domain"中输入：`beatsync.site`
3. 保存

#### 3. 在腾讯云DNS中添加主域名CNAME记录

**添加记录**：
- **主机记录**：`@`
- **记录类型**：`CNAME`
- **记录值**：`scarlettyellow.github.io`
- **TTL**：`600`

**注意**：这会覆盖现有的A记录，需要先删除或修改

#### 4. 配置后端使用子域名

**在服务器上配置Nginx**：

```bash
# 更新Nginx配置，使用api.beatsync.site
sudo tee /etc/nginx/sites-available/beatsync > /dev/null << 'EOFNGINX'
server {
    listen 80;
    listen [::]:80;
    server_name api.beatsync.site;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name api.beatsync.site;

    ssl_certificate /etc/letsencrypt/live/beatsync.site/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/beatsync.site/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    client_max_body_size 500M;

    location / {
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
}
EOFNGINX

# 重新加载Nginx
sudo nginx -t && sudo systemctl reload nginx
```

#### 5. 申请api子域名的SSL证书

```bash
sudo certbot --nginx -d api.beatsync.site
```

#### 6. 更新前端代码中的API地址

**文件**：`web_service/frontend/script.js`

**修改**：
```javascript
// 生产环境：使用腾讯云服务器（HTTPS）
const backendUrl = window.API_BASE_URL || 'https://api.beatsync.site';
```

---

### 方案3：保持现状，忽略GitHub Pages警告（不推荐）

**说明**：
- 前端使用 `www.beatsync.site`（GitHub Pages）
- 后端使用 `beatsync.site`（腾讯云服务器）
- 忽略GitHub Pages关于主域名的警告

**缺点**：
- ❌ GitHub Pages会持续显示警告
- ❌ 无法启用"Enforce HTTPS"（如果主域名未配置）
- ❌ 不符合GitHub Pages的最佳实践

---

## 推荐方案

### 推荐：方案1（使用app子域名）

**理由**：
- ✅ 前后端完全分离，架构清晰
- ✅ 避免域名冲突
- ✅ 修改最少（只需修改CNAME文件和DNS）
- ✅ 后端配置无需改动

---

## 实施步骤（方案1）

### 步骤1：修改CNAME文件

**在本地修改**：`web_service/frontend/CNAME`

**内容**：
```
app.beatsync.site
```

### 步骤2：提交到GitHub

```bash
cd /Users/scarlett/Projects/BeatSync
git add web_service/frontend/CNAME
git commit -m "fix: 修改前端域名为app.beatsync.site避免主域名冲突"
git push origin main
```

### 步骤3：在GitHub Pages中更新域名

1. 进入GitHub仓库 → Settings → Pages
2. 在"Custom domain"中输入：`app.beatsync.site`
3. 保存

### 步骤4：在腾讯云DNS中添加CNAME记录

**添加记录**：
- **主机记录**：`app`
- **记录类型**：`CNAME`
- **记录值**：`scarlettyellow.github.io`
- **TTL**：`600`

**删除或保留www记录**（可选）：
- 如果不再使用www，可以删除www记录
- 或者保留，让www也指向GitHub Pages

### 步骤5：等待DNS生效并验证

**验证DNS解析**：
```bash
nslookup app.beatsync.site 8.8.8.8
```

**预期结果**：
```
app.beatsync.site canonical name = scarlettyellow.github.io
```

### 步骤6：在GitHub Pages中检查

1. 点击"Check again"
2. 应该显示成功（因为使用的是子域名，不要求主域名）

---

## 最终架构

### 配置完成后

- **前端**：`https://app.beatsync.site`（GitHub Pages）
- **后端**：`https://beatsync.site`（腾讯云服务器）

### 用户访问

- 用户访问：`https://app.beatsync.site`
- 前端自动连接后端：`https://beatsync.site`

---

## 验证清单

- [ ] CNAME文件已修改为 `app.beatsync.site`
- [ ] 已提交到GitHub
- [ ] GitHub Pages中已更新域名
- [ ] 在腾讯云DNS中添加了 `app` CNAME记录
- [ ] DNS解析已生效
- [ ] GitHub Pages DNS检查成功
- [ ] 前端可以通过新域名访问
- [ ] 前端可以正常连接后端API

---

## 相关文档

- `docs/deployment/FRONTEND_DOMAIN_CONFIGURATION.md` - 前端域名配置方案
- `docs/deployment/FIX_GITHUB_PAGES_DNS_ERROR.md` - GitHub Pages DNS错误修复

---

**最后更新**：2025-12-04

