# 修复外部TLS连接重置问题

> **问题**：服务器本地TLS连接成功，但外部连接失败（`write:errno=54`）  
> **原因**：腾讯云安全策略（DDoS防护、WAF）或网络中间设备阻止  
> **解决**：检查腾讯云安全设置、优化SSL配置、检查网络环境

---

## 问题分析

### 诊断结果对比

**服务器本地TLS连接**：
- ✅ **连接成功**：`CONNECTED(00000003)`
- ✅ **证书链完整**：Let's Encrypt证书正常
- ✅ **SSL握手成功**：TLSv1.3协议正常

**外部TLS连接**：
- ❌ **连接失败**：`write:errno=54`（连接被重置）
- ❌ **TLS握手失败**：在握手过程中连接被重置

### 关键发现

- **Nginx配置正确**：本地连接成功说明配置没问题
- **SSL证书正常**：证书链完整，证书有效
- **问题在外部访问**：很可能是腾讯云安全策略或网络中间设备阻止

---

## 解决方案

### 方案1：检查腾讯云DDoS防护（最重要）

**在腾讯云控制台检查**：

1. **进入轻量应用服务器控制台**
   - 找到服务器实例（IP：124.221.58.149）

2. **检查DDoS防护设置**
   - 查看是否有DDoS防护功能
   - 检查防护规则是否过于严格
   - 确认没有阻止正常HTTPS连接

3. **检查安全组/防火墙**
   - 确认443端口已开放
   - 检查是否有其他限制规则
   - 确认规则来源是 `0.0.0.0/0`

---

### 方案2：检查腾讯云WAF（Web应用防火墙）

**如果启用了WAF**：
1. 检查WAF规则
2. 确认没有阻止HTTPS连接
3. 检查是否有IP白名单设置

---

### 方案3：优化SSL配置（提高兼容性）

**在服务器上执行**：

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

    # 优化SSL配置以提高兼容性
    ssl_buffer_size 8k;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

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

### 方案4：检查网络环境

**可能的问题**：
1. **ISP（网络服务提供商）阻止**：某些ISP可能阻止某些HTTPS连接
2. **公司/学校网络防火墙**：可能阻止HTTPS连接
3. **VPN连接**：可能影响网络路由

**解决方法**：
- 尝试使用移动网络（手机热点）
- 尝试关闭VPN
- 尝试不同的网络环境

---

### 方案5：使用IP地址直接访问（测试）

**在本地终端执行**：
```bash
# 直接使用IP地址访问（绕过域名）
curl -k https://124.221.58.149/api/health -H "Host: beatsync.site"
```

**如果IP地址可以访问**：
- 说明问题在域名解析或DNS
- 需要检查DNS配置

**如果IP地址也无法访问**：
- 说明问题在服务器或网络
- 需要检查服务器配置和网络环境

---

## 诊断命令

### 在服务器上执行详细诊断

```bash
echo "=== 1. 检查Nginx访问日志（最近的外部访问） ==="
sudo tail -n 50 /var/log/nginx/access.log | grep -v "127.0.0.1" | tail -20

echo ""
echo "=== 2. 检查Nginx错误日志（最近的外部错误） ==="
sudo tail -n 50 /var/log/nginx/error.log | grep -v "127.0.0.1" | tail -20

echo ""
echo "=== 3. 检查端口监听（确认监听所有接口） ==="
sudo netstat -tlnp | grep :443

echo ""
echo "=== 4. 检查防火墙规则 ==="
sudo ufw status verbose

echo ""
echo "=== 5. 测试本地TLS连接（详细） ==="
echo | openssl s_client -connect localhost:443 -servername beatsync.site 2>&1 | grep -E "(CONNECTED|Protocol|Cipher|Verify)"
```

---

## 腾讯云安全策略检查清单

### 需要检查的项目

- [ ] **DDoS防护**：检查是否启用，规则是否过于严格
- [ ] **WAF（Web应用防火墙）**：检查是否启用，规则是否阻止连接
- [ ] **安全组规则**：确认443端口已开放，来源是 `0.0.0.0/0`
- [ ] **轻量服务器防火墙**：确认443端口已开放
- [ ] **IP白名单**：检查是否有IP白名单限制

---

## 如果所有方法都失败

### 可能的根本原因

1. **腾讯云安全策略**：
   - DDoS防护可能在阻止某些连接模式
   - 需要联系腾讯云技术支持

2. **网络中间设备**：
   - ISP可能在阻止某些HTTPS连接
   - 需要尝试不同的网络环境

3. **地域限制**：
   - 某些地区可能无法访问
   - 需要测试不同地区的访问

---

## 临时解决方案

### 如果HTTPS无法访问，可以临时使用HTTP

**注意**：这不是推荐方案，但可以作为临时测试：

```bash
# 修改Nginx配置，允许HTTP访问（仅用于测试）
# 不推荐在生产环境使用
```

**更好的方案**：
- 继续排查HTTPS问题
- 联系腾讯云技术支持
- 检查是否有其他安全策略

---

## 验证清单

- [x] 服务器本地TLS连接成功
- [x] SSL证书正常
- [x] Nginx配置正确
- [ ] 检查腾讯云DDoS防护设置
- [ ] 检查腾讯云WAF设置
- [ ] 检查安全组规则
- [ ] 尝试使用IP地址直接访问
- [ ] 尝试不同的网络环境
- [ ] 外部HTTPS连接成功

---

## 相关文档

- `docs/deployment/FIX_TLS_HANDSHAKE_RESET.md` - TLS握手重置问题
- `docs/deployment/FIX_TENCENT_CLOUD_SECURITY_GROUP.md` - 安全组配置

---

**最后更新**：2025-12-04

