# SSL 证书验证错误排查

## 问题描述

执行 `curl -I https://beatsync.site/` 时遇到错误：

```
curl: (60) SSL: no alternative certificate subject name matches target host name 'beatsync.site'
```

## 快速验证（跳过证书验证）

如果要快速验证响应头，可以使用 `-k` 参数跳过 SSL 验证：

```bash
curl -I -k https://beatsync.site/
```

## 可能的原因

### 1. 本地 DNS 缓存问题

CDN 关闭后，本地可能仍缓存了旧的 DNS 记录或证书信息。

**解决方法**：
```bash
# macOS/Linux
sudo dscacheutil -flushcache
sudo killall -HUP mDNSResponder

# 或清除浏览器 DNS 缓存
# Chrome: chrome://net-internals/#dns -> Clear host cache
```

### 2. 证书配置问题

检查服务器上的 SSL 证书配置：

```bash
# 在服务器上执行
sudo certbot certificates

# 查看证书详情
openssl x509 -in /etc/letsencrypt/live/beatsync.site/fullchain.pem -text -noout | grep -A 5 "Subject Alternative Name"
```

### 3. Nginx 配置问题

检查 Nginx 的 SSL 配置：

```bash
# 在服务器上执行
sudo nginx -t
sudo cat /etc/nginx/sites-available/beatsync | grep -A 10 ssl_certificate
```

## 验证步骤

### 步骤 1: 验证 DNS 解析

```bash
# 检查域名解析到哪个 IP
nslookup beatsync.site
# 或
dig beatsync.site

# 应该解析到服务器 IP：124.221.58.149（或您当前的服务器 IP）
```

### 步骤 2: 直接访问 IP（绕过 DNS）

```bash
# 使用服务器 IP 直接访问（需要修改 hosts 文件，或使用 curl 的 --resolve 参数）
curl -I -k --resolve beatsync.site:443:124.221.58.149 https://beatsync.site/
```

### 步骤 3: 在服务器本地验证

如果是在服务器本地执行 curl，可以直接验证：

```bash
# 在服务器上执行
curl -I https://beatsync.site/
# 或
curl -I http://localhost/
```

## 正确的验证方法

### 方法 1: 使用 -k 参数（跳过验证）

```bash
curl -I -k https://beatsync.site/
```

### 方法 2: 检查 CDN 响应头（使用 -k）

```bash
curl -I -k https://beatsync.site/ | grep -i "x-cache\|x-nws"

# 如果没有任何输出，说明 CDN 已关闭
# 如果有 X-Cache-Lookup 或 X-NWS-LOG-UUID，说明 CDN 仍在运行
```

### 方法 3: 在浏览器中检查

1. 访问 https://beatsync.site/
2. 打开浏览器开发者工具（F12）
3. 切换到 Network 标签
4. 刷新页面
5. 点击第一个请求，查看 Response Headers
6. 检查是否有 `X-Cache-Lookup` 或 `X-NWS-LOG-UUID` 响应头

## 验证 CDN 是否已关闭的完整命令

```bash
# 方法 1: 跳过 SSL 验证检查响应头
curl -I -k https://beatsync.site/ | grep -E "X-Cache|X-NWS|Server"

# 方法 2: 查看完整响应头（使用 -k）
curl -I -k https://beatsync.site/

# 预期结果（CDN 已关闭）：
# HTTP/2 200
# Server: nginx/1.18.0 (Ubuntu)
# ...（不应该有 X-Cache-Lookup 或 X-NWS-LOG-UUID）
```

## 如果问题持续存在

1. **检查证书是否过期**：
   ```bash
   sudo certbot certificates
   ```

2. **检查 Nginx 配置**：
   ```bash
   sudo nginx -t
   sudo systemctl status nginx
   ```

3. **重新申请证书（如果需要）**：
   ```bash
   sudo certbot renew --dry-run
   ```

4. **重启 Nginx**：
   ```bash
   sudo systemctl reload nginx
   ```

## 相关文档

- [CDN 暂停验证指南](../deployment/CDN_PAUSED_VERIFICATION.md)
- [SSL 证书自动续期配置](../deployment/SSL_AUTO_RENEWAL_CONFIGURED.md)

---

**最后更新**：2025-12-20






