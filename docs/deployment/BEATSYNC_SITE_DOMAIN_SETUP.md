# beatsync.site 域名配置完整指南

> **域名**：beatsync.site  
> **服务器IP**：124.221.58.149  
> **目标**：配置域名解析和Let's Encrypt SSL证书

---

## 步骤1：配置DNS解析

### 在腾讯云控制台配置

1. **登录腾讯云控制台**
   - 访问：https://console.cloud.tencent.com/
   - 登录你的账号

2. **进入DNS解析**
   - 搜索"DNS解析"或"域名解析"
   - 或直接访问：https://console.cloud.tencent.com/cns

3. **添加A记录**
   - 找到 `beatsync.site` 域名
   - 点击"解析"或"添加记录"
   - 配置如下：
     ```
     类型：A
     主机记录：@（主域名）或 beatsync（子域名，如果使用子域名）
     记录值：124.221.58.149
     TTL：600（或默认值）
     ```
   - 点击"保存"

4. **如果使用主域名（@）**
   - 主机记录填写：`@`
   - 访问地址：`https://beatsync.site`

5. **如果使用子域名**
   - 主机记录填写：`beatsync`
   - 访问地址：`https://beatsync.beatsync.site`

**推荐**：使用主域名（`@`），访问地址更简洁

---

## 步骤2：验证DNS解析

### 等待DNS生效

**通常需要**：几分钟到几小时

### 检查DNS解析

**在本地终端执行**：
```bash
# 检查DNS解析
nslookup beatsync.site

# 或使用dig（如果已安装）
dig beatsync.site

# 或使用ping
ping beatsync.site
```

**预期结果**：
- 应该返回：`124.221.58.149`
- 如果返回其他IP或无法解析，说明DNS还未生效，请等待

---

## 步骤3：申请Let's Encrypt证书

### 在服务器上执行

**前提**：确保DNS解析已生效（步骤2验证通过）

```bash
# 1. 安装Certbot
sudo apt update
sudo apt install -y certbot python3-certbot-nginx

# 2. 申请证书（自动配置Nginx）
sudo certbot --nginx -d beatsync.site
```

**交互式配置**：
1. **输入邮箱**：用于接收证书到期提醒（建议填写）
2. **同意服务条款**：输入 `Y`
3. **是否分享邮箱**：可选，输入 `Y` 或 `N`
4. **选择重定向HTTP到HTTPS**：建议选择 `2`（重定向）

**Certbot会自动**：
- 申请证书
- 配置Nginx使用证书
- 配置HTTP到HTTPS的重定向
- 重启Nginx服务

---

## 步骤4：验证证书配置

### 检查Nginx配置

```bash
# 查看Nginx配置
sudo cat /etc/nginx/sites-available/beatsync

# 测试Nginx配置
sudo nginx -t

# 如果测试通过，重启Nginx
sudo systemctl restart nginx
```

**应该看到类似配置**：
```nginx
server {
    listen 80;
    server_name beatsync.site;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name beatsync.site;
    
    ssl_certificate /etc/letsencrypt/live/beatsync.site/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/beatsync.site/privkey.pem;
    
    # ... 其他配置
}
```

---

## 步骤5：测试HTTPS访问

### 在浏览器中测试

1. **访问健康检查地址**：
   - `https://beatsync.site/api/health`
   - 应该显示：`healthy`
   - 浏览器地址栏应该显示🔒（安全）

2. **检查证书信息**：
   - 点击地址栏的🔒图标
   - 查看证书详情
   - 应该显示"Let's Encrypt"作为颁发机构

---

### 使用命令行测试

```bash
# 测试HTTPS连接
curl -I https://beatsync.site/api/health

# 应该返回：HTTP/2 200
```

---

## 步骤6：更新前端配置

### 修改前端API地址

**文件**：`web_service/frontend/script.js`

**找到这一行**（约第29行）：
```javascript
const backendUrl = window.API_BASE_URL || 'https://124.221.58.149';
```

**修改为**：
```javascript
const backendUrl = window.API_BASE_URL || 'https://beatsync.site';
```

---

### 提交并部署

**在本地执行**：
```bash
cd /Users/scarlett/Projects/BeatSync
git add web_service/frontend/script.js
git commit -m "update: 使用域名beatsync.site替代IP地址"
git push origin main
```

---

### 在服务器上更新代码

**在服务器上执行**：
```bash
cd /opt/beatsync
sudo git pull origin main
```

**注意**：前端代码在GitHub Pages上，会自动更新（可能需要几分钟）

---

## 步骤7：配置自动续期

### 检查自动续期配置

```bash
# 检查Certbot定时任务
sudo systemctl status certbot.timer

# 查看定时任务详情
sudo systemctl list-timers | grep certbot
```

**如果未配置，手动启用**：
```bash
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer
```

---

### 测试自动续期

```bash
# 测试续期（不会真正续期）
sudo certbot renew --dry-run

# 如果测试成功，会显示：
# "The dry run was successful."
```

---

## 完整配置脚本

### 一键配置脚本（在服务器上执行）

**前提**：DNS解析已生效

```bash
#!/bin/bash
DOMAIN="beatsync.site"

echo "=========================================="
echo "beatsync.site 域名配置"
echo "=========================================="
echo ""

# 1. 检查DNS解析
echo "步骤1: 检查DNS解析..."
DNS_IP=$(dig +short $DOMAIN)
if [ "$DNS_IP" != "124.221.58.149" ]; then
    echo "⚠️ DNS解析未生效或IP不匹配"
    echo "   当前解析IP: $DNS_IP"
    echo "   期望IP: 124.221.58.149"
    echo "   请等待DNS生效后再继续"
    exit 1
fi
echo "✅ DNS解析正确: $DOMAIN -> $DNS_IP"

# 2. 安装Certbot
echo "步骤2: 安装Certbot..."
sudo apt update
sudo apt install -y certbot python3-certbot-nginx

# 3. 申请证书（需要交互式输入）
echo "步骤3: 申请SSL证书..."
echo "注意：需要交互式输入邮箱和同意条款"
sudo certbot --nginx -d $DOMAIN

# 4. 测试Nginx配置
echo "步骤4: 测试Nginx配置..."
sudo nginx -t

# 5. 重启Nginx
echo "步骤5: 重启Nginx..."
sudo systemctl restart nginx

# 6. 检查证书状态
echo "步骤6: 检查证书状态..."
sudo certbot certificates

# 7. 测试自动续期
echo "步骤7: 测试自动续期..."
sudo certbot renew --dry-run

echo ""
echo "=========================================="
echo "配置完成！"
echo "=========================================="
echo "HTTPS地址: https://$DOMAIN"
echo "健康检查: https://$DOMAIN/api/health"
echo ""
echo "下一步："
echo "1. 更新前端配置使用域名"
echo "2. 在浏览器中测试HTTPS访问"
echo ""
```

---

## 验证清单

配置完成后，请验证以下项目：

- [ ] DNS解析正确（`nslookup beatsync.site`返回`124.221.58.149`）
- [ ] 80端口已开放（Let's Encrypt验证需要）
- [ ] 443端口已开放（HTTPS服务）
- [ ] 证书申请成功（`sudo certbot certificates`显示证书）
- [ ] HTTPS可以访问（浏览器显示🔒）
- [ ] HTTP自动重定向到HTTPS
- [ ] 健康检查正常（`https://beatsync.site/api/health`返回`healthy`）
- [ ] 自动续期已配置（`sudo systemctl status certbot.timer`）
- [ ] 前端已更新为使用域名

---

## 常见问题

### 问题1：DNS解析未生效

**检查方法**：
```bash
nslookup beatsync.site
```

**解决方法**：
- 等待DNS生效（通常几分钟到几小时）
- 检查DNS配置是否正确
- 清除本地DNS缓存

---

### 问题2：证书申请失败

**错误信息**：
```
Failed to verify ownership of domain
```

**解决方法**：
1. 确认DNS解析已生效
2. 确认80端口已开放
3. 确认Nginx正在运行
4. 查看详细错误：`sudo certbot certificates`

---

### 问题3：Nginx配置冲突

**如果之前使用自签名证书**：

Certbot会自动更新Nginx配置，但可能需要手动调整：

```bash
# 查看当前配置
sudo cat /etc/nginx/sites-available/beatsync

# 如果配置有问题，可以手动编辑
sudo nano /etc/nginx/sites-available/beatsync

# 测试配置
sudo nginx -t

# 重启Nginx
sudo systemctl restart nginx
```

---

## 后续维护

### 查看证书状态

```bash
sudo certbot certificates
```

### 手动续期（如果需要）

```bash
sudo certbot renew
sudo systemctl restart nginx
```

### 查看证书到期时间

```bash
sudo certbot certificates | grep "Expiry Date"
```

---

## 相关文档

- `docs/deployment/LETS_ENCRYPT_SSL_SETUP.md` - Let's Encrypt详细配置指南
- `docs/deployment/DOMAIN_AND_SSL_CERTIFICATE.md` - 域名和SSL证书说明

---

**最后更新**：2025-12-03

