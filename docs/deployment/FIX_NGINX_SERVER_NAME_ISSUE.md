# 修复Nginx server_name匹配问题

> **问题**：使用IP地址可以访问，但使用域名无法访问  
> **原因**：Nginx server_name匹配问题、SNI问题、或配置问题  
> **解决**：检查并修复Nginx配置，确保server_name正确匹配

---

## 问题分析

### 关键发现

- ✅ **使用IP地址访问成功**：`curl -k https://124.221.58.149/api/health -H "Host: beatsync.site"` 成功
- ❌ **使用域名访问失败**：`curl -k https://beatsync.site/api/health` 失败（Connection reset by peer）
- ✅ **访问日志显示成功请求**：说明某些请求是成功的

### 可能的原因

1. **Nginx server_name匹配问题**：Nginx可能没有正确匹配域名
2. **SNI（Server Name Indication）问题**：TLS握手时服务器名称不匹配
3. **默认server块问题**：可能有默认server块在拦截请求

---

## 解决方案

### 方案1：检查并修复Nginx配置（最重要）

**在服务器上执行**：

```bash
# 查看所有启用的Nginx配置
sudo ls -la /etc/nginx/sites-enabled/

# 查看默认配置（如果有）
sudo cat /etc/nginx/sites-enabled/default 2>/dev/null || echo "默认配置不存在"

# 查看当前配置
sudo cat /etc/nginx/sites-available/beatsync
```

**如果存在默认配置，需要禁用它**：

```bash
# 禁用默认配置
sudo rm -f /etc/nginx/sites-enabled/default

# 确保只有beatsync配置启用
sudo ls -la /etc/nginx/sites-enabled/
```

---

### 方案2：重新创建Nginx配置（确保正确）

**在服务器上执行**：

```bash
sudo tee /etc/nginx/sites-available/beatsync > /dev/null << 'EOFNGINX'
server {
    listen 80 default_server;
    listen [::]:80 default_server;
    server_name _;
    return 444;
}

server {
    listen 80;
    listen [::]:80;
    server_name beatsync.site;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl default_server;
    listen [::]:443 ssl default_server;
    server_name _;
    ssl_certificate /etc/letsencrypt/live/beatsync.site/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/beatsync.site/privkey.pem;
    return 444;
}

server {
    listen 443 ssl;
    listen [::]:443 ssl;
    server_name beatsync.site;

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

# 测试配置
sudo nginx -t

# 重新加载Nginx
sudo systemctl reload nginx
```

**说明**：
- 添加了默认server块，用于处理不匹配的请求（返回444关闭连接）
- 确保beatsync.site的server块优先级正确

---

### 方案3：检查Nginx访问日志（详细）

**在服务器上执行**：

```bash
# 实时查看访问日志
sudo tail -f /var/log/nginx/access.log

# 在另一个终端，尝试从外部访问
# 观察日志中是否有请求记录
```

**如果日志中没有请求记录**：
- 说明请求在到达Nginx之前就被阻止了
- 可能是防火墙或DDoS防护的问题

**如果日志中有请求记录**：
- 查看请求的Host头和状态码
- 确认server_name是否正确匹配

---

### 方案4：测试SNI（Server Name Indication）

**在本地终端执行**：

```bash
# 测试SNI
echo | openssl s_client -connect beatsync.site:443 -servername beatsync.site 2>&1 | grep -E "(CONNECTED|Protocol|Cipher|Verify|CN)"

# 测试不使用SNI
echo | openssl s_client -connect beatsync.site:443 2>&1 | grep -E "(CONNECTED|Protocol|Cipher|Verify|CN)"
```

**如果使用SNI成功但不使用SNI失败**：
- 说明是SNI配置问题
- 需要确保Nginx正确配置了SNI

---

## 诊断命令

### 在服务器上执行详细诊断

```bash
echo "=== 1. 检查所有启用的Nginx配置 ==="
sudo ls -la /etc/nginx/sites-enabled/

echo ""
echo "=== 2. 检查默认配置（如果有） ==="
sudo cat /etc/nginx/sites-enabled/default 2>/dev/null || echo "默认配置不存在"

echo ""
echo "=== 3. 检查当前配置 ==="
sudo cat /etc/nginx/sites-available/beatsync

echo ""
echo "=== 4. 测试Nginx配置 ==="
sudo nginx -t

echo ""
echo "=== 5. 检查Nginx访问日志（最近10条） ==="
sudo tail -n 10 /var/log/nginx/access.log

echo ""
echo "=== 6. 检查Nginx错误日志（最近10条） ==="
sudo tail -n 10 /var/log/nginx/error.log

echo ""
echo "=== 7. 测试本地HTTPS（使用域名） ==="
curl -k https://beatsync.site/api/health -H "Host: beatsync.site" --resolve beatsync.site:443:127.0.0.1
```

---

## 快速修复（推荐）

### 如果存在默认配置，先禁用它

```bash
# 禁用默认配置
sudo rm -f /etc/nginx/sites-enabled/default

# 确保只有beatsync配置
sudo ln -sf /etc/nginx/sites-available/beatsync /etc/nginx/sites-enabled/beatsync

# 测试配置
sudo nginx -t

# 重新加载Nginx
sudo systemctl reload nginx
```

---

## 验证清单

- [ ] 检查所有启用的Nginx配置
- [ ] 禁用默认配置（如果存在）
- [ ] 重新创建Nginx配置（确保正确）
- [ ] Nginx配置测试通过
- [ ] Nginx已重新加载
- [ ] 测试本地HTTPS（使用域名）
- [ ] 测试外部HTTPS（使用域名）
- [ ] 浏览器可以访问域名

---

## 相关文档

- `docs/deployment/FIX_DOMAIN_VS_IP_ACCESS.md` - 域名访问问题
- `docs/deployment/FIX_EXTERNAL_TLS_CONNECTION_RESET.md` - 外部TLS连接重置

---

**最后更新**：2025-12-04

