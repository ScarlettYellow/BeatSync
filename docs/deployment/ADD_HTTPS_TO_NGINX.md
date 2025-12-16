# 为 Nginx 添加 HTTPS 配置

> **当前状态**：Nginx 只配置了 HTTP（80端口），缺少 HTTPS（443端口）配置  
> **目标**：添加 HTTPS 配置，启用 SSL 证书，配置 HTTP→HTTPS 跳转

---

## 当前配置问题

1. ❌ 只监听 80 端口，没有 443 端口
2. ❌ `server_name _;` 是通配符，应该改为 `beatsync.site`
3. ❌ 没有 HTTP→HTTPS 跳转
4. ❌ 没有 SSL 证书配置

---

## 修复步骤

### 步骤 1：备份当前配置

```bash
sudo cp /etc/nginx/sites-available/beatsync /etc/nginx/sites-available/beatsync.backup
```

### 步骤 2：编辑 Nginx 配置文件

```bash
sudo nano /etc/nginx/sites-available/beatsync
```

### 步骤 3：替换为完整配置

**删除现有内容，替换为以下配置**：

```nginx
# HTTP 服务器 - 自动跳转到 HTTPS
server {
    listen 80;
    server_name beatsync.site;
    
    # 自动跳转到 HTTPS
    return 301 https://$server_name$request_uri;
}

# HTTPS 服务器
server {
    listen 443 ssl http2;
    server_name beatsync.site;
    
    # SSL 证书配置（Let's Encrypt）
    ssl_certificate /etc/letsencrypt/live/beatsync.site/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/beatsync.site/privkey.pem;
    
    # SSL 安全配置（推荐）
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers on;
    ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-CHACHA20-POLY1305;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    # 文件上传大小限制
    client_max_body_size 500M;
    
    # 反向代理到 FastAPI 后端
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket 支持（如果需要）
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # 超时设置
        proxy_connect_timeout 600s;
        proxy_send_timeout 600s;
        proxy_read_timeout 600s;
    }
    
    # 健康检查端点（可选，用于监控）
    location /api/health {
        proxy_pass http://127.0.0.1:8000/api/health;
        proxy_set_header Host $host;
        access_log off;
    }
}
```

### 步骤 4：验证配置

```bash
# 测试 Nginx 配置语法
sudo nginx -t
```

**预期输出**：
```
nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
nginx: configuration file /etc/nginx/nginx.conf test is successful
```

### 步骤 5：重新加载 Nginx

```bash
# 重新加载配置（不中断服务）
sudo systemctl reload nginx

# 或重启 Nginx（如果 reload 失败）
sudo systemctl restart nginx

# 检查 Nginx 状态
sudo systemctl status nginx
```

### 步骤 6：验证端口监听

```bash
# 检查端口监听
sudo netstat -tlnp | grep nginx
# 或
sudo ss -tlnp | grep nginx
```

**预期输出**：
```
tcp  0  0  0.0.0.0:80   0.0.0.0:*  LISTEN  nginx
tcp  0  0  0.0.0.0:443  0.0.0.0:*  LISTEN  nginx
```

### 步骤 7：测试 HTTP 跳转

```bash
curl -I http://beatsync.site/api/health
```

**预期输出**：
```
HTTP/1.1 301 Moved Permanently
Server: nginx/1.18.0 (Ubuntu)
Date: ...
Location: https://beatsync.site/api/health
...
```

### 步骤 8：测试 HTTPS 访问

```bash
# 测试 HTTPS 连接
curl -I https://beatsync.site/api/health

# 测试 HTTPS 内容
curl https://beatsync.site/api/health
```

**预期输出**：
```
HTTP/2 200
...
{"status":"healthy"}
```

---

## 如果遇到问题

### 问题 1：证书文件不存在

**检查证书文件**：
```bash
sudo ls -la /etc/letsencrypt/live/beatsync.site/
```

**如果文件不存在**，重新申请证书：
```bash
sudo certbot --nginx -d beatsync.site
```

### 问题 2：Nginx 配置测试失败

**查看详细错误**：
```bash
sudo nginx -t
```

**常见错误**：
- 证书路径错误 → 检查证书文件路径
- 语法错误 → 检查配置文件的括号和分号
- 权限问题 → 确保 Nginx 可以读取证书文件

### 问题 3：443 端口仍无法连接

**检查防火墙**：
```bash
sudo ufw status
sudo ufw allow 443/tcp
sudo ufw reload
```

**检查腾讯云安全组**：
- 确保入站规则中有 TCP:443，来源 0.0.0.0/0

### 问题 4：HTTP 没有跳转到 HTTPS

**检查配置**：
- 确保有两个 `server` 块
- 第一个 `server` 块监听 80 端口，有 `return 301` 配置
- 第二个 `server` 块监听 443 端口，有 SSL 配置

---

## 完整配置示例（带注释）

```nginx
# ============================================
# HTTP 服务器 - 自动跳转到 HTTPS
# ============================================
server {
    listen 80;
    server_name beatsync.site;
    
    # 所有 HTTP 请求自动跳转到 HTTPS
    return 301 https://$server_name$request_uri;
}

# ============================================
# HTTPS 服务器 - 主要服务
# ============================================
server {
    listen 443 ssl http2;
    server_name beatsync.site;
    
    # ============================================
    # SSL 证书配置
    # ============================================
    ssl_certificate /etc/letsencrypt/live/beatsync.site/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/beatsync.site/privkey.pem;
    
    # ============================================
    # SSL 安全配置
    # ============================================
    # 只允许 TLS 1.2 和 1.3（禁用旧版本）
    ssl_protocols TLSv1.2 TLSv1.3;
    
    # 优先使用服务器端密码套件
    ssl_prefer_server_ciphers on;
    
    # 强密码套件
    ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-CHACHA20-POLY1305;
    
    # SSL 会话缓存（提高性能）
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    # ============================================
    # 文件上传大小限制
    # ============================================
    client_max_body_size 500M;
    
    # ============================================
    # 反向代理到 FastAPI 后端
    # ============================================
    location / {
        # 后端服务地址
        proxy_pass http://127.0.0.1:8000;
        
        # 传递原始请求头
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket 支持（如果需要）
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # 超时设置（适应大文件上传和处理）
        proxy_connect_timeout 600s;
        proxy_send_timeout 600s;
        proxy_read_timeout 600s;
    }
    
    # ============================================
    # 健康检查端点（可选）
    # ============================================
    location /api/health {
        proxy_pass http://127.0.0.1:8000/api/health;
        proxy_set_header Host $host;
        # 不记录健康检查日志（减少日志量）
        access_log off;
    }
}
```

---

## 验证清单

完成配置后，验证以下项目：

- [ ] Nginx 配置语法正确（`sudo nginx -t`）
- [ ] Nginx 已重新加载（`sudo systemctl reload nginx`）
- [ ] 80 端口正在监听（`sudo netstat -tlnp | grep :80`）
- [ ] 443 端口正在监听（`sudo netstat -tlnp | grep :443`）
- [ ] HTTP 自动跳转到 HTTPS（`curl -I http://beatsync.site` 返回 301）
- [ ] HTTPS 可以访问（`curl https://beatsync.site/api/health` 返回 200）
- [ ] 浏览器显示 🔒（访问 `https://beatsync.site`）
- [ ] 证书有效（浏览器中点击 🔒 查看证书信息）

---

**最后更新**：2025-12-16

