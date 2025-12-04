# 修复TLS握手连接重置问题

> **错误**：`Connection reset by peer` - HTTPS连接在TLS握手阶段被重置  
> **原因**：SSL/TLS配置问题、中间设备阻止、或腾讯云安全策略  
> **解决**：检查SSL配置、检查中间设备、优化TLS设置

---

## 问题分析

### 诊断结果

从curl测试看到：
- ✅ **DNS解析正常**：`beatsync.site` → `124.221.58.149`
- ✅ **HTTP连接成功**：返回 `301 Moved Permanently`
- ✅ **TCP连接成功**：`Connected to beatsync.site (124.221.58.149) port 443`
- ❌ **TLS握手失败**：`Connection reset by peer` - 在TLS握手过程中连接被重置

### 关键信息

```
* Connected to beatsync.site (124.221.58.149) port 443
* ALPN: curl offers h2,http/1.1
* (304) (OUT), TLS handshake, Client hello (1):
* Recv failure: Connection reset by peer
```

这说明：
- TCP连接已建立
- 客户端发送了TLS Client Hello
- 服务器在收到Client Hello后重置了连接

---

## 可能的原因

### 1. Nginx SSL配置问题

**可能的问题**：
- SSL协议版本不兼容
- 加密套件配置问题
- SSL证书链不完整

---

### 2. 腾讯云安全策略

**可能的问题**：
- DDoS防护在阻止连接
- WAF（Web应用防火墙）在阻止连接
- 安全组规则虽然开放了443端口，但可能有其他限制

---

### 3. 中间设备阻止

**可能的问题**：
- 网络中间设备（代理、防火墙）在阻止TLS握手
- ISP（网络服务提供商）在阻止某些HTTPS连接

---

## 解决方案

### 方案1：检查并优化Nginx SSL配置

**在服务器上执行**：

```bash
# 查看Let's Encrypt的默认SSL配置
sudo cat /etc/letsencrypt/options-ssl-nginx.conf

# 查看当前的Nginx配置
sudo cat /etc/nginx/sites-available/beatsync
```

**如果配置有问题，重新创建**：

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

    # 确保HTTP/2正常工作
    http2_max_field_size 16k;
    http2_max_header_size 32k;

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

### 方案2：检查腾讯云安全策略

**在腾讯云控制台检查**：

1. **DDoS防护**：
   - 进入轻量应用服务器控制台
   - 检查是否有DDoS防护设置
   - 确认没有阻止正常连接

2. **WAF（Web应用防火墙）**：
   - 检查是否启用了WAF
   - 如果有，检查WAF规则是否阻止了连接

3. **安全组**：
   - 确认443端口已开放
   - 检查是否有其他限制规则

---

### 方案3：尝试禁用HTTP/2

**如果HTTP/2有问题，可以尝试禁用**：

```bash
sudo tee /etc/nginx/sites-available/beatsync > /dev/null << 'EOFNGINX'
server {
    listen 80;
    listen [::]:80;
    server_name beatsync.site;
    return 301 https://$server_name$request_uri;
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

**注意**：移除了 `http2`，只使用 `ssl`

---

### 方案4：检查Nginx错误日志（详细）

**在服务器上执行**：

```bash
# 实时查看Nginx错误日志
sudo tail -f /var/log/nginx/error.log

# 在另一个终端，尝试从外部访问
# 观察错误日志中的详细信息
```

**可能看到的错误**：
- SSL协议错误
- 证书错误
- 连接重置原因

---

## 诊断命令

### 在服务器上执行详细诊断

```bash
echo "=== 1. 检查Nginx配置 ==="
sudo cat /etc/nginx/sites-available/beatsync

echo ""
echo "=== 2. 检查Let's Encrypt SSL配置 ==="
sudo cat /etc/letsencrypt/options-ssl-nginx.conf

echo ""
echo "=== 3. 检查SSL证书 ==="
sudo openssl x509 -in /etc/letsencrypt/live/beatsync.site/fullchain.pem -text -noout | grep -A 5 "Subject:"

echo ""
echo "=== 4. 检查Nginx进程 ==="
sudo ps aux | grep nginx

echo ""
echo "=== 5. 检查端口监听 ==="
sudo netstat -tlnp | grep :443

echo ""
echo "=== 6. 测试本地HTTPS（详细模式） ==="
curl -v https://localhost/api/health 2>&1 | head -20

echo ""
echo "=== 7. 检查Nginx错误日志（最近20行） ==="
sudo tail -n 20 /var/log/nginx/error.log
```

---

## 快速修复尝试

### 尝试1：重新加载Nginx配置

```bash
# 测试配置
sudo nginx -t

# 如果测试通过，重新加载
sudo systemctl reload nginx

# 如果reload失败，尝试重启
sudo systemctl restart nginx
```

---

### 尝试2：检查SSL证书链

```bash
# 检查证书链是否完整
sudo openssl s_client -connect localhost:443 -servername beatsync.site < /dev/null 2>/dev/null | openssl x509 -noout -text | grep -A 5 "Issuer"
```

---

### 尝试3：使用openssl测试TLS连接

**在服务器上执行**：
```bash
# 测试TLS连接
echo | openssl s_client -connect localhost:443 -servername beatsync.site 2>&1 | head -30
```

**在本地终端执行**：
```bash
# 测试外部TLS连接
echo | openssl s_client -connect beatsync.site:443 -servername beatsync.site 2>&1 | head -30
```

---

## 如果所有方法都失败

### 可能的根本原因

1. **腾讯云安全策略**：
   - DDoS防护可能在阻止连接
   - 需要联系腾讯云技术支持

2. **网络中间设备**：
   - ISP可能在阻止某些HTTPS连接
   - 需要联系网络服务提供商

3. **SSL/TLS兼容性问题**：
   - 某些客户端可能不支持服务器使用的TLS版本
   - 需要调整SSL配置

---

## 验证清单

- [ ] Nginx配置正确（`nginx -t`通过）
- [ ] Nginx已重新加载
- [ ] 本地HTTPS连接成功
- [ ] SSL证书链完整
- [ ] 端口443正在监听
- [ ] 尝试禁用HTTP/2后测试
- [ ] 检查腾讯云安全策略
- [ ] 外部HTTPS连接成功

---

## 相关文档

- `docs/deployment/FIX_SSL_HANDSHAKE_ERRORS.md` - SSL握手错误修复
- `docs/deployment/DEEP_DIAGNOSIS_CONNECTION_ISSUE.md` - 深度诊断连接问题

---

**最后更新**：2025-12-04

