# 修复 HTTPS 连接被拒绝问题

> **问题**：`curl: (7) Failed to connect to beatsync.site port 443 after 188 ms: Connection refused`  
> **原因**：443 端口未开放或 Nginx 未正确配置 HTTPS

---

## 问题诊断

### 当前状态
- ✅ Let's Encrypt 证书已存在且有效（81天后过期）
- ✅ Nginx 配置语法正确
- ❌ HTTPS 连接被拒绝（443 端口）
- ❌ HTTP 没有跳转到 HTTPS（返回 200 而不是 301）

---

## 解决步骤

### 步骤 1：检查 Nginx 配置文件

```bash
# 查看 Nginx 站点配置
sudo cat /etc/nginx/sites-available/beatsync
# 或
sudo cat /etc/nginx/sites-available/default

# 查看所有启用的站点
ls -la /etc/nginx/sites-enabled/
```

**检查要点**：
1. 是否有 `listen 443 ssl;` 配置
2. SSL 证书路径是否正确
3. `server_name` 是否为 `beatsync.site`

---

### 步骤 2：检查 Nginx 是否监听 443 端口

```bash
# 检查 Nginx 监听的端口
sudo netstat -tlnp | grep nginx
# 或
sudo ss -tlnp | grep nginx

# 应该看到类似：
# 0.0.0.0:80    LISTEN  nginx
# 0.0.0.0:443   LISTEN  nginx
```

**如果没有看到 443 端口**，说明 Nginx 没有正确配置 HTTPS。

---

### 步骤 3：检查防火墙/安全组

#### 3.1 检查服务器防火墙（UFW）

```bash
# 检查防火墙状态
sudo ufw status

# 如果防火墙开启，检查 443 端口是否开放
sudo ufw status | grep 443

# 如果没有开放，添加规则
sudo ufw allow 443/tcp
sudo ufw reload
```

#### 3.2 检查腾讯云安全组

**在腾讯云控制台操作**：

1. 登录腾讯云控制台
2. 进入"云服务器 CVM" → "实例"
3. 找到服务器实例（IP: 124.221.58.149）
4. 点击"安全组" → "修改规则"
5. 检查入站规则：
   - **协议端口**：TCP:443
   - **来源**：0.0.0.0/0
   - **策略**：允许
6. 如果没有，点击"添加规则"添加 443 端口

---

### 步骤 4：修复 Nginx HTTPS 配置

如果 Nginx 配置文件中没有 HTTPS 配置，需要添加：

```bash
# 编辑 Nginx 配置文件
sudo nano /etc/nginx/sites-available/beatsync
# 或
sudo nano /etc/nginx/sites-available/default
```

**正确的配置应该包含**：

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
    
    # SSL 证书配置
    ssl_certificate /etc/letsencrypt/live/beatsync.site/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/beatsync.site/privkey.pem;
    
    # SSL 配置（可选，但推荐）
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers on;
    ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384;
    
    # 文件上传大小限制
    client_max_body_size 500M;
    
    # 反向代理到 FastAPI
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
    }
    
    # 健康检查端点
    location /api/health {
        proxy_pass http://127.0.0.1:8000/api/health;
        proxy_set_header Host $host;
        access_log off;
    }
}
```

---

### 步骤 5：重新加载 Nginx

```bash
# 测试配置
sudo nginx -t

# 如果测试通过，重新加载配置
sudo systemctl reload nginx
# 或
sudo systemctl restart nginx

# 检查 Nginx 状态
sudo systemctl status nginx
```

---

### 步骤 6：验证修复

```bash
# 1. 检查端口监听
sudo netstat -tlnp | grep nginx
# 应该看到 443 端口

# 2. 测试 HTTP 跳转
curl -I http://beatsync.site/api/health
# 应该返回：Location: https://beatsync.site/api/health

# 3. 测试 HTTPS 访问
curl -I https://beatsync.site/api/health
# 应该返回：HTTP/2 200

# 4. 测试 HTTPS 内容
curl https://beatsync.site/api/health
# 应该返回：{"status":"healthy"}
```

---

## 如果 Certbot 没有自动配置

如果 Nginx 配置文件中没有 HTTPS 配置，可能需要手动运行 Certbot：

```bash
# 方法 1：让 Certbot 自动配置（推荐）
sudo certbot --nginx -d beatsync.site

# 方法 2：只申请证书，不修改配置
sudo certbot certonly --nginx -d beatsync.site

# 然后手动编辑 Nginx 配置文件添加 SSL 配置
```

---

## 检查后端服务

### 找到后端服务的实际名称

```bash
# 方法 1：查找所有 systemd 服务
sudo systemctl list-units --type=service | grep -i beat
sudo systemctl list-units --type=service | grep -i python
sudo systemctl list-units --type=service | grep -i api

# 方法 2：查找进程
ps aux | grep python
ps aux | grep uvicorn
ps aux | grep fastapi

# 方法 3：查找 supervisor 配置（如果使用）
sudo supervisorctl status
ls /etc/supervisor/conf.d/

# 方法 4：查找 systemd 服务文件
ls /etc/systemd/system/*.service | grep -i beat
```

### 检查后端服务状态

```bash
# 如果使用 systemd
sudo systemctl status <服务名称>

# 如果使用 supervisor
sudo supervisorctl status

# 如果直接运行
ps aux | grep python | grep -v grep
```

### 检查后端 CORS 配置

```bash
# 方法 1：检查环境变量
env | grep ALLOWED_ORIGINS

# 方法 2：检查 .env 文件
cat /opt/beatsync/.env | grep ALLOWED_ORIGINS
# 或
cat ~/.env | grep ALLOWED_ORIGINS

# 方法 3：检查 systemd 服务配置
sudo systemctl cat <服务名称> | grep ALLOWED_ORIGINS
```

### 更新 CORS 配置

```bash
# 方法 1：编辑 .env 文件
sudo nano /opt/beatsync/.env
# 添加或修改：
# ALLOWED_ORIGINS=https://beatsync.site,http://localhost:8000

# 方法 2：在 systemd 服务文件中添加环境变量
sudo nano /etc/systemd/system/<服务名称>.service
# 在 [Service] 部分添加：
# Environment="ALLOWED_ORIGINS=https://beatsync.site,http://localhost:8000"

# 重新加载并重启服务
sudo systemctl daemon-reload
sudo systemctl restart <服务名称>
```

---

## 完整诊断脚本

```bash
#!/bin/bash
echo "=========================================="
echo "HTTPS 连接诊断"
echo "=========================================="
echo ""

echo "1. 检查 Nginx 状态..."
sudo systemctl status nginx --no-pager | head -5
echo ""

echo "2. 检查端口监听..."
sudo netstat -tlnp | grep nginx
echo ""

echo "3. 检查防火墙..."
sudo ufw status | head -10
echo ""

echo "4. 检查 Nginx 配置..."
sudo nginx -t
echo ""

echo "5. 检查 SSL 证书..."
sudo certbot certificates
echo ""

echo "6. 测试 HTTP 跳转..."
curl -I http://beatsync.site/api/health 2>&1 | head -5
echo ""

echo "7. 测试 HTTPS 连接..."
curl -I https://beatsync.site/api/health 2>&1 | head -5
echo ""

echo "8. 检查后端服务..."
ps aux | grep -E "python|uvicorn|fastapi" | grep -v grep | head -3
echo ""

echo "=========================================="
echo "诊断完成"
echo "=========================================="
```

保存为 `diagnose_https.sh`，然后运行：
```bash
chmod +x diagnose_https.sh
./diagnose_https.sh
```

---

## 常见问题

### 问题 1：Nginx 配置正确但 443 端口仍无法连接

**可能原因**：
1. 防火墙未开放 443 端口
2. 腾讯云安全组未开放 443 端口
3. Nginx 未重启

**解决方法**：
1. 检查并开放防火墙
2. 检查并配置安全组
3. 重启 Nginx：`sudo systemctl restart nginx`

### 问题 2：HTTP 没有跳转到 HTTPS

**可能原因**：
1. Nginx 配置中没有 HTTP→HTTPS 跳转规则
2. 使用了错误的 `server_name`

**解决方法**：
1. 检查 Nginx 配置文件
2. 确保有 `return 301 https://$server_name$request_uri;` 配置

### 问题 3：证书路径错误

**检查方法**：
```bash
# 检查证书文件是否存在
sudo ls -la /etc/letsencrypt/live/beatsync.site/

# 应该看到：
# fullchain.pem
# privkey.pem
```

**如果文件不存在**，重新申请证书：
```bash
sudo certbot --nginx -d beatsync.site
```

---

**最后更新**：2025-12-16

