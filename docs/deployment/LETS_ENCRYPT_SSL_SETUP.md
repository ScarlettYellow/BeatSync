# Let's Encrypt 免费SSL证书申请和配置指南

> **目标**：为BeatSync服务配置免费的HTTPS证书，解决浏览器兼容性问题  
> **证书提供商**：Let's Encrypt（免费，自动续期）  
> **适用场景**：已配置域名并完成DNS解析

---

## 前置条件

### 1. 域名已配置并解析到服务器

**检查DNS解析**：
```bash
# 在本地执行
nslookup yourdomain.com

# 应该返回服务器IP：124.221.58.149
```

**如果未配置域名**：
- 在域名服务商处添加A记录
- 主机记录：`@` 或 `beatsync`（子域名）
- 记录值：`124.221.58.149`
- TTL：600（或默认值）

---

### 2. 服务器端口已开放

**必须开放的端口**：
- **80端口**：Let's Encrypt验证需要（HTTP）
- **443端口**：HTTPS服务（如果已配置）

**在腾讯云控制台检查**：
- 进入"防火墙"或"安全组"
- 确保80和443端口已开放

---

### 3. Nginx已安装并运行

**检查Nginx状态**：
```bash
# 在服务器上执行
sudo systemctl status nginx

# 如果未安装，执行
sudo apt update
sudo apt install -y nginx
```

---

## 步骤1：安装Certbot

### 在服务器上执行

```bash
# 更新软件包列表
sudo apt update

# 安装Certbot和Nginx插件
sudo apt install -y certbot python3-certbot-nginx

# 验证安装
certbot --version
```

**预期输出**：
```
certbot 2.x.x
```

---

## 步骤2：申请SSL证书

### 方法1：自动配置（推荐，最简单）

**Certbot会自动检测Nginx配置并申请证书**：

```bash
# 替换为你的域名
sudo certbot --nginx -d yourdomain.com

# 如果使用子域名
sudo certbot --nginx -d beatsync.yourdomain.com
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

### 方法2：仅申请证书（手动配置Nginx）

**如果不想让Certbot自动修改Nginx配置**：

```bash
# 仅申请证书，不修改Nginx配置
sudo certbot certonly --nginx -d yourdomain.com
```

**证书文件位置**：
- 证书：`/etc/letsencrypt/live/yourdomain.com/fullchain.pem`
- 私钥：`/etc/letsencrypt/live/yourdomain.com/privkey.pem`

**然后手动配置Nginx**（见步骤3）

---

## 步骤3：验证Nginx配置

### 检查Certbot自动生成的配置

```bash
# 查看Nginx配置
sudo cat /etc/nginx/sites-available/beatsync

# 或查看所有配置
sudo nginx -T
```

**应该看到类似配置**：
```nginx
server {
    listen 80;
    server_name yourdomain.com;
    
    # HTTP自动重定向到HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;
    
    # SSL证书配置（Certbot自动添加）
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    
    # SSL配置（Certbot自动添加）
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;
    
    # 原有的代理配置
    location / {
        proxy_pass http://127.0.0.1:8000;
        # ...
    }
}
```

---

### 测试Nginx配置

```bash
# 测试配置是否正确
sudo nginx -t

# 如果测试通过，重启Nginx
sudo systemctl restart nginx
```

---

## 步骤4：测试证书

### 在浏览器中测试

1. **访问HTTPS地址**：
   - `https://yourdomain.com/api/health`
   - 应该显示"healthy"，且浏览器地址栏显示🔒（安全）

2. **检查证书信息**：
   - 点击地址栏的🔒图标
   - 查看证书详情
   - 应该显示"Let's Encrypt"作为颁发机构

---

### 使用命令行测试

```bash
# 测试HTTPS连接
curl -I https://yourdomain.com/api/health

# 应该返回200 OK
```

---

## 步骤5：配置自动续期

### Let's Encrypt证书有效期

- **有效期**：90天
- **自动续期**：Certbot通常已自动配置

---

### 检查自动续期配置

```bash
# 检查Certbot定时任务
sudo systemctl status certbot.timer

# 查看定时任务详情
sudo systemctl list-timers | grep certbot
```

**如果未配置，手动启用**：
```bash
# 启用Certbot定时任务
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

### 手动续期（如果需要）

```bash
# 手动续期所有证书
sudo certbot renew

# 续期后重启Nginx
sudo systemctl restart nginx
```

---

## 步骤6：更新前端配置

### 修改前端API地址

**文件**：`web_service/frontend/script.js`

**修改**：
```javascript
// 从
const backendUrl = window.API_BASE_URL || 'https://124.221.58.149';

// 改为
const backendUrl = window.API_BASE_URL || 'https://yourdomain.com';
```

**提交并部署**：
```bash
git add web_service/frontend/script.js
git commit -m "update: 使用域名替代IP地址"
git push origin main
```

---

## 常见问题

### 问题1：DNS解析未生效

**错误信息**：
```
Failed to verify ownership of domain
```

**解决方法**：
1. 检查DNS解析是否正确
2. 等待DNS解析生效（可能需要几分钟到几小时）
3. 使用`nslookup yourdomain.com`验证

---

### 问题2：80端口未开放

**错误信息**：
```
Connection refused on port 80
```

**解决方法**：
1. 在腾讯云控制台开放80端口
2. 检查防火墙配置
3. 确保Nginx正在监听80端口

---

### 问题3：证书申请失败

**错误信息**：
```
Failed to obtain certificate
```

**解决方法**：
1. 检查域名是否正确解析到服务器
2. 检查80端口是否开放
3. 检查Nginx是否正常运行
4. 查看详细错误日志：`sudo certbot certificates`

---

### 问题4：证书续期失败

**解决方法**：
```bash
# 查看证书状态
sudo certbot certificates

# 手动续期
sudo certbot renew --force-renewal

# 检查续期日志
sudo journalctl -u certbot.timer
```

---

## 完整配置脚本

### 一键配置脚本（在服务器上执行）

**前提**：已配置域名DNS解析

```bash
#!/bin/bash
# Let's Encrypt SSL证书一键配置脚本

DOMAIN="yourdomain.com"  # 替换为你的域名

echo "=========================================="
echo "Let's Encrypt SSL证书配置"
echo "=========================================="
echo ""

# 1. 安装Certbot
echo "步骤1: 安装Certbot..."
sudo apt update
sudo apt install -y certbot python3-certbot-nginx

# 2. 申请证书（自动配置Nginx）
echo "步骤2: 申请SSL证书..."
echo "注意：需要交互式输入邮箱和同意条款"
sudo certbot --nginx -d $DOMAIN

# 3. 测试Nginx配置
echo "步骤3: 测试Nginx配置..."
sudo nginx -t

# 4. 重启Nginx
echo "步骤4: 重启Nginx..."
sudo systemctl restart nginx

# 5. 检查证书状态
echo "步骤5: 检查证书状态..."
sudo certbot certificates

# 6. 测试自动续期
echo "步骤6: 测试自动续期..."
sudo certbot renew --dry-run

echo ""
echo "=========================================="
echo "配置完成！"
echo "=========================================="
echo "HTTPS地址: https://$DOMAIN"
echo "健康检查: https://$DOMAIN/api/health"
echo ""
```

---

## 验证清单

配置完成后，请验证以下项目：

- [ ] DNS解析正确（`nslookup yourdomain.com`返回服务器IP）
- [ ] 80端口已开放（Let's Encrypt验证需要）
- [ ] 443端口已开放（HTTPS服务）
- [ ] 证书申请成功（`sudo certbot certificates`显示证书）
- [ ] HTTPS可以访问（浏览器显示🔒）
- [ ] HTTP自动重定向到HTTPS
- [ ] 自动续期已配置（`sudo systemctl status certbot.timer`）
- [ ] 前端已更新为使用域名

---

## 证书文件位置

**证书文件**：
- 证书：`/etc/letsencrypt/live/yourdomain.com/fullchain.pem`
- 私钥：`/etc/letsencrypt/live/yourdomain.com/privkey.pem`
- 证书链：`/etc/letsencrypt/live/yourdomain.com/chain.pem`

**不要直接使用这些文件**，Certbot会自动管理。

---

## 维护命令

### 查看所有证书

```bash
sudo certbot certificates
```

### 撤销证书（如果需要）

```bash
sudo certbot revoke --cert-path /etc/letsencrypt/live/yourdomain.com/cert.pem
```

### 删除证书

```bash
sudo certbot delete --cert-name yourdomain.com
```

---

## 相关文档

- `docs/deployment/DOMAIN_AND_SSL_CERTIFICATE.md` - 域名和SSL证书说明
- `docs/deployment/TENCENT_CLOUD_DEPLOYMENT_MASTER_GUIDE.md` - 完整部署指南

---

**最后更新**：2025-12-03

