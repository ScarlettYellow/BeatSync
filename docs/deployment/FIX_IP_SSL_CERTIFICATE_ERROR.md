# 修复IP地址SSL证书错误

> **问题**：使用IP地址访问时，浏览器报 `ERR_CERT_COMMON_NAME_INVALID` 错误  
> **原因**：SSL证书是为域名 `beatsync.site` 签发的，不是为IP地址签发的  
> **解决**：配置Nginx同时支持IP地址访问，使用自签名证书

---

## 问题分析

### 错误信息

从浏览器控制台看到：
```
GET https://124.221.58.149/api/health net::ERR_CERT_COMMON_NAME_INVALID
```

### 根本原因

1. **SSL证书不匹配**：
   - 服务器上的SSL证书是为域名 `beatsync.site` 签发的（Let's Encrypt证书）
   - 当使用IP地址 `124.221.58.149` 访问时，浏览器检查证书的Common Name
   - 发现证书是为 `beatsync.site` 签发的，不是为IP地址签发的
   - 浏览器拒绝连接，报 `ERR_CERT_COMMON_NAME_INVALID` 错误

2. **Let's Encrypt不支持IP证书**：
   - Let's Encrypt只支持域名证书，不支持IP地址证书
   - 无法为IP地址申请Let's Encrypt证书

---

## 解决方案

### 方案1：配置Nginx同时支持IP地址访问（推荐）

**在服务器上为IP地址配置自签名证书**：

1. **生成自签名证书**（如果还没有）：
```bash
# 在服务器上执行
sudo mkdir -p /etc/nginx/ssl
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout /etc/nginx/ssl/ip.key \
  -out /etc/nginx/ssl/ip.crt \
  -subj "/CN=124.221.58.149"
```

2. **修改Nginx配置**，添加IP地址的server块：

```nginx
# HTTP重定向到HTTPS（IP地址）
server {
    listen 80;
    server_name 124.221.58.149;
    return 301 https://$server_name$request_uri;
}

# HTTPS（域名 - Let's Encrypt证书）
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
    }
}

# HTTPS（IP地址 - 自签名证书）
server {
    listen 443 ssl;
    listen [::]:443 ssl;
    server_name 124.221.58.149;
    
    ssl_certificate /etc/nginx/ssl/ip.crt;
    ssl_certificate_key /etc/nginx/ssl/ip.key;
    
    client_max_body_size 500M;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

3. **测试Nginx配置**：
```bash
sudo nginx -t
```

4. **重启Nginx**：
```bash
sudo systemctl restart nginx
```

---

### 方案2：用户手动接受证书警告（临时方案）

**如果不想修改服务器配置，可以让用户手动接受证书警告**：

1. **用户需要先手动访问**：
   - 在浏览器中访问：`https://124.221.58.149/api/health`
   - 点击"高级" → "继续访问"（或"Proceed to 124.221.58.149 (unsafe)"）
   - 浏览器会记住这个例外，之后就可以正常访问了

2. **改进前端错误提示**：
   - 在错误信息中明确告诉用户需要手动访问健康检查地址
   - 提供直接链接，方便用户点击

---

## 实施步骤

### 步骤1：在服务器上生成自签名证书

**在腾讯云服务器上执行**：

```bash
# 创建SSL证书目录
sudo mkdir -p /etc/nginx/ssl

# 生成自签名证书（IP地址）
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout /etc/nginx/ssl/ip.key \
  -out /etc/nginx/ssl/ip.crt \
  -subj "/CN=124.221.58.149"

# 设置权限
sudo chmod 600 /etc/nginx/ssl/ip.key
sudo chmod 644 /etc/nginx/ssl/ip.crt
```

---

### 步骤2：修改Nginx配置

**在腾讯云服务器上执行**：

```bash
# 备份当前配置
sudo cp /etc/nginx/sites-available/beatsync /etc/nginx/sites-available/beatsync.backup

# 编辑配置文件
sudo nano /etc/nginx/sites-available/beatsync
```

**添加IP地址的server块**（在现有配置后面添加）：

```nginx
# HTTPS（IP地址 - 自签名证书）
server {
    listen 443 ssl;
    listen [::]:443 ssl;
    server_name 124.221.58.149;
    
    ssl_certificate /etc/nginx/ssl/ip.crt;
    ssl_certificate_key /etc/nginx/ssl/ip.key;
    
    client_max_body_size 500M;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

**保存并退出**（`Ctrl+X` → `Y` → `Enter`）

---

### 步骤3：测试并重启Nginx

```bash
# 测试配置
sudo nginx -t

# 如果测试通过，重启Nginx
sudo systemctl restart nginx

# 检查Nginx状态
sudo systemctl status nginx
```

---

### 步骤4：验证IP地址访问

**在本地测试**：

```bash
# 测试HTTPS访问（会显示证书警告，但可以访问）
curl -k https://124.221.58.149/api/health
```

**预期结果**：
- 返回 `{"status":"healthy"}` 或类似JSON响应
- 浏览器访问时仍会显示证书警告（因为是自签名证书），但用户可以接受

---

## 改进前端错误提示

**同时改进前端错误提示，让用户知道需要接受证书警告**：

**文件**：`web_service/frontend/script.js`

**修改 `checkBackendHealth` 函数的错误处理**：

```javascript
// 检测证书错误
if (fetchError.message.includes('ERR_CERT_COMMON_NAME_INVALID') ||
    fetchError.message.includes('ERR_CERT_AUTHORITY_INVALID') ||
    fetchError.message.includes('certificate') ||
    fetchError.message.includes('SSL') ||
    fetchError.message.includes('TLS')) {
    console.warn('⚠️ SSL证书错误：证书是为域名签发的，使用IP地址访问时需要接受证书警告');
    console.warn('   解决方法：请先手动访问 https://124.221.58.149/api/health 并接受证书警告');
    // 可以在这里显示用户友好的错误提示
}
```

---

## 验证清单

- [ ] 在服务器上生成自签名证书
- [ ] 修改Nginx配置，添加IP地址的server块
- [ ] 测试Nginx配置
- [ ] 重启Nginx
- [ ] 测试IP地址HTTPS访问
- [ ] 改进前端错误提示
- [ ] 测试前端访问（浏览器会显示证书警告，但可以接受）

---

## 注意事项

1. **自签名证书警告**：
   - 即使配置了自签名证书，浏览器仍会显示"不安全"警告
   - 用户需要手动接受证书警告
   - 这是临时方案，备案通过后改回域名即可解决

2. **备案通过后**：
   - 备案通过后，域名可以正常访问
   - 可以移除IP地址的server块配置
   - 前端改回使用域名

3. **安全性**：
   - 自签名证书不提供身份验证
   - 但可以加密通信，防止中间人攻击
   - 对于临时方案，这是可以接受的

---

## 相关文档

- `docs/deployment/TEMPORARY_IP_ADDRESS_SOLUTION.md` - 临时使用IP地址方案
- `docs/deployment/FIX_DNSPOD_WEB_BLOCK_ALTERNATIVE.md` - DNSPod拦截问题替代方案

---

**最后更新**：2025-12-04

