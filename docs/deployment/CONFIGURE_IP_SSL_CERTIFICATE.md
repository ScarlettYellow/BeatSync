# 配置IP地址SSL证书（服务器端）

> **目的**：为IP地址配置自签名证书，解决 `ERR_CERT_COMMON_NAME_INVALID` 错误  
> **注意**：这是临时方案，备案通过后改回域名即可

---

## 一键配置命令

**在腾讯云服务器上执行以下命令**：

```bash
# 1. 生成自签名证书
sudo mkdir -p /etc/nginx/ssl
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout /etc/nginx/ssl/ip.key \
  -out /etc/nginx/ssl/ip.crt \
  -subj "/CN=124.221.58.149"

# 2. 设置权限
sudo chmod 600 /etc/nginx/ssl/ip.key
sudo chmod 644 /etc/nginx/ssl/ip.crt

# 3. 备份当前Nginx配置
sudo cp /etc/nginx/sites-available/beatsync /etc/nginx/sites-available/beatsync.backup.$(date +%Y%m%d_%H%M%S)

# 4. 添加IP地址的server块到Nginx配置
sudo tee -a /etc/nginx/sites-available/beatsync > /dev/null << 'EOFNGINX'

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
EOFNGINX

# 5. 测试Nginx配置
sudo nginx -t

# 6. 如果测试通过，重启Nginx
if [ $? -eq 0 ]; then
    sudo systemctl restart nginx
    echo "✅ Nginx配置已更新并重启"
else
    echo "❌ Nginx配置测试失败，请检查配置"
    exit 1
fi

# 7. 检查Nginx状态
sudo systemctl status nginx --no-pager -l
```

---

## 分步执行（如果一键命令失败）

### 步骤1：生成自签名证书

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

### 步骤2：备份当前配置

```bash
# 备份当前配置
sudo cp /etc/nginx/sites-available/beatsync /etc/nginx/sites-available/beatsync.backup.$(date +%Y%m%d_%H%M%S)
```

---

### 步骤3：添加IP地址的server块

**编辑Nginx配置文件**：

```bash
sudo nano /etc/nginx/sites-available/beatsync
```

**在文件末尾添加以下内容**：

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

### 步骤4：测试并重启Nginx

```bash
# 测试配置
sudo nginx -t

# 如果测试通过，重启Nginx
sudo systemctl restart nginx

# 检查Nginx状态
sudo systemctl status nginx
```

---

## 验证配置

### 在服务器上测试

```bash
# 测试IP地址HTTPS访问
curl -k https://124.221.58.149/api/health
```

**预期结果**：
- 返回 `{"status":"healthy"}` 或类似JSON响应
- `-k` 参数忽略证书验证（因为这是自签名证书）

---

### 在浏览器中测试

1. **访问健康检查地址**：
   - 打开浏览器，访问：`https://124.221.58.149/api/health`
   - 浏览器会显示"不安全"警告

2. **接受证书警告**：
   - 点击"高级"或"Advanced"
   - 点击"继续访问"或"Proceed to 124.221.58.149 (unsafe)"
   - 浏览器会记住这个例外

3. **验证访问**：
   - 应该能看到JSON响应：`{"status":"healthy"}` 或类似
   - 之后访问前端页面，应该可以正常连接后端

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

## 移除IP地址配置（备案通过后）

**当域名备案通过后，可以移除IP地址的server块**：

```bash
# 1. 编辑Nginx配置
sudo nano /etc/nginx/sites-available/beatsync

# 2. 删除IP地址的server块（从 "# HTTPS（IP地址 - 自签名证书）" 到 "}" 之间的所有内容）

# 3. 测试配置
sudo nginx -t

# 4. 如果测试通过，重启Nginx
sudo systemctl restart nginx
```

---

## 相关文档

- `docs/deployment/FIX_IP_SSL_CERTIFICATE_ERROR.md` - IP地址SSL证书错误修复
- `docs/deployment/TEMPORARY_IP_ADDRESS_SOLUTION.md` - 临时使用IP地址方案

---

**最后更新**：2025-12-04

