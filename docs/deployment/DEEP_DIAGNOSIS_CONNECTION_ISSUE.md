# 深度诊断连接问题

> **问题**：防火墙已开放，但HTTPS仍然无法访问  
> **可能原因**：Nginx配置错误、SSL证书问题、域名解析问题  
> **解决**：逐步检查Nginx配置、证书、域名解析

---

## 问题分析

### 当前状态

- ✅ **防火墙已开放**：443和80端口都已配置
- ✅ **服务运行正常**：Nginx和FastAPI都在运行
- ✅ **本地连接成功**：`curl -k https://localhost/api/health` 成功
- ❌ **外部无法访问**：`https://beatsync.site/api/health` 无法打开

---

## 排查步骤

### 步骤1：检查Nginx配置

**在服务器上执行**：
```bash
# 查看Nginx配置
sudo cat /etc/nginx/sites-available/beatsync

# 检查配置语法
sudo nginx -t

# 查看Nginx错误日志
sudo tail -n 100 /var/log/nginx/error.log
```

**检查要点**：
- server_name是否正确（应该是 `beatsync.site`）
- SSL证书路径是否正确
- proxy_pass是否正确指向 `http://127.0.0.1:8000`

---

### 步骤2：检查SSL证书

**在服务器上执行**：
```bash
# 检查证书文件
sudo ls -la /etc/letsencrypt/live/beatsync.site/

# 检查证书有效期
sudo certbot certificates

# 测试证书
sudo openssl x509 -in /etc/letsencrypt/live/beatsync.site/fullchain.pem -text -noout | grep -A 2 "Subject:"
```

**预期结果**：
- 证书文件存在：`fullchain.pem` 和 `privkey.pem`
- 证书有效：未过期
- 证书域名：包含 `beatsync.site`

---

### 步骤3：检查域名解析

**在本地终端执行**：
```bash
# 检查域名解析
nslookup beatsync.site 8.8.8.8

# 检查是否解析到正确的IP
dig @8.8.8.8 beatsync.site +short
```

**预期结果**：
- 域名解析到：`124.221.58.149`

---

### 步骤4：测试外部连接

**在服务器上执行**：
```bash
# 从服务器测试外部访问
curl -I https://beatsync.site/api/health

# 检查Nginx访问日志
sudo tail -n 50 /var/log/nginx/access.log
```

**预期结果**：
- 如果外部访问成功，应该看到访问日志
- 如果失败，检查错误日志

---

### 步骤5：检查Nginx是否监听所有接口

**在服务器上执行**：
```bash
# 检查Nginx监听配置
sudo netstat -tlnp | grep nginx

# 检查Nginx配置中的listen指令
sudo grep -r "listen" /etc/nginx/sites-available/beatsync
```

**预期结果**：
- 应该监听 `0.0.0.0:443`（所有接口）
- 不应该只监听 `127.0.0.1:443`（仅本地）

---

## 常见问题和解决方案

### 问题1：Nginx配置中server_name错误

**检查**：
```bash
sudo grep "server_name" /etc/nginx/sites-available/beatsync
```

**应该显示**：
```
server_name beatsync.site;
```

**如果错误，修复**：
```bash
sudo vim /etc/nginx/sites-available/beatsync
# 修改server_name为beatsync.site
sudo nginx -t
sudo systemctl reload nginx
```

---

### 问题2：SSL证书路径错误

**检查**：
```bash
sudo grep "ssl_certificate" /etc/nginx/sites-available/beatsync
```

**应该显示**：
```
ssl_certificate /etc/letsencrypt/live/beatsync.site/fullchain.pem;
ssl_certificate_key /etc/letsencrypt/live/beatsync.site/privkey.pem;
```

**如果路径错误，修复**：
```bash
sudo vim /etc/nginx/sites-available/beatsync
# 修改证书路径
sudo nginx -t
sudo systemctl reload nginx
```

---

### 问题3：Nginx只监听本地接口

**检查**：
```bash
sudo grep "listen" /etc/nginx/sites-available/beatsync
```

**应该显示**：
```
listen 443 ssl http2;
listen [::]:443 ssl http2;
```

**不应该显示**：
```
listen 127.0.0.1:443;  # 错误：只监听本地
```

**如果错误，修复**：
```bash
sudo vim /etc/nginx/sites-available/beatsync
# 修改为 listen 443 ssl http2;
sudo nginx -t
sudo systemctl reload nginx
```

---

### 问题4：域名解析到错误的IP

**检查**：
```bash
dig @8.8.8.8 beatsync.site +short
```

**应该返回**：
```
124.221.58.149
```

**如果返回其他IP，修复**：
- 在腾讯云DNS中检查A记录
- 确保记录值是正确的服务器IP

---

## 一键诊断命令

**在服务器上执行以下完整诊断**：

```bash
echo "=== 1. 检查Nginx配置 ==="
sudo cat /etc/nginx/sites-available/beatsync

echo ""
echo "=== 2. 检查Nginx配置语法 ==="
sudo nginx -t

echo ""
echo "=== 3. 检查SSL证书 ==="
sudo ls -la /etc/letsencrypt/live/beatsync.site/ 2>/dev/null || echo "证书目录不存在"
sudo certbot certificates 2>/dev/null | grep -A 5 "beatsync.site" || echo "证书检查失败"

echo ""
echo "=== 4. 检查Nginx监听 ==="
sudo netstat -tlnp | grep nginx

echo ""
echo "=== 5. 检查Nginx错误日志 ==="
sudo tail -n 20 /var/log/nginx/error.log

echo ""
echo "=== 6. 检查Nginx访问日志 ==="
sudo tail -n 10 /var/log/nginx/access.log

echo ""
echo "=== 7. 测试本地HTTPS ==="
curl -sk https://localhost/api/health || echo "本地HTTPS连接失败"

echo ""
echo "=== 8. 检查域名解析 ==="
dig @8.8.8.8 beatsync.site +short
```

---

## 快速修复方案

### 如果Nginx配置有问题

**重新创建正确的Nginx配置**：

```bash
sudo tee /etc/nginx/sites-available/beatsync > /dev/null << 'EOFNGINX'
server {
    listen 80;
    listen [::]:80;
    server_name beatsync.site;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
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

---

## 验证清单

- [ ] Nginx配置正确（server_name、证书路径、proxy_pass）
- [ ] SSL证书存在且有效
- [ ] Nginx监听所有接口（0.0.0.0:443）
- [ ] 域名解析到正确的IP（124.221.58.149）
- [ ] 防火墙已开放443端口
- [ ] Nginx配置语法正确（nginx -t通过）
- [ ] 本地HTTPS连接成功
- [ ] 外部HTTPS连接成功

---

## 相关文档

- `docs/deployment/FIX_TENCENT_CLOUD_SECURITY_GROUP.md` - 安全组配置
- `docs/deployment/TROUBLESHOOT_BACKEND_CONNECTION.md` - 连接问题排查

---

**最后更新**：2025-12-04

