# 安装Certbot并申请SSL证书

> **问题**：`sudo: certbot: command not found`  
> **解决**：先安装certbot，再申请证书

---

## 完整步骤

### 步骤1：安装Certbot

**在服务器上执行**：
```bash
sudo apt update
sudo apt install -y certbot python3-certbot-nginx
```

**预期输出**：
- 更新软件包列表
- 安装certbot和相关依赖
- 可能需要确认安装（输入 `Y`）

**安装时间**：约1-2分钟

---

### 步骤2：验证Certbot安装

**检查版本**：
```bash
certbot --version
```

**预期输出**：
```
certbot 2.x.x
```

---

### 步骤3：申请SSL证书

**执行证书申请**：
```bash
sudo certbot --nginx -d beatsync.site
```

**交互式配置**：

1. **输入邮箱**（用于证书到期提醒）：
   ```
   Enter email address (used for urgent renewal and security notices)
   ```

2. **同意服务条款**：
   ```
   (A)gree/(C)ancel: A
   ```

3. **是否分享邮箱**（可选）：
   ```
   (Y)es/(N)o: N
   ```

4. **选择重定向HTTP到HTTPS**（推荐）：
   ```
   Please choose whether or not to redirect HTTP traffic to HTTPS, removing HTTP access.
   -------------------------------------------------------------------------------
   1: No redirect - Make no further changes to the webserver configuration.
   2: Redirect - Make all requests redirect to secure HTTPS access.
   -------------------------------------------------------------------------------
   Select the appropriate number [1-2] then [enter]: 2
   ```

**预期输出**：
```
Successfully received certificate.
Certificate is saved at: /etc/letsencrypt/live/beatsync.site/fullchain.pem
Key is saved at:         /etc/letsencrypt/live/beatsync.site/privkey.pem
This certificate expires on YYYY-MM-DD.
These files will be updated when the certificate auto-renews.
```

---

### 步骤4：验证Nginx配置

**测试Nginx配置**：
```bash
sudo nginx -t
```

**预期输出**：
```
nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
nginx: configuration file /etc/nginx/nginx.conf test is successful
```

---

### 步骤5：重启Nginx

**应用新配置**：
```bash
sudo systemctl reload nginx
# 或
sudo systemctl restart nginx
```

**检查Nginx状态**：
```bash
sudo systemctl status nginx
```

---

### 步骤6：验证HTTPS访问

**在浏览器中访问**：
```
https://beatsync.site
```

**预期结果**：
- ✅ 显示绿色锁图标（安全连接）
- ✅ 证书信息显示 "Let's Encrypt"
- ✅ 网站正常加载

---

## 一键安装和申请（完整命令）

**如果步骤1-3需要一次性执行**：

```bash
# 安装Certbot
sudo apt update && sudo apt install -y certbot python3-certbot-nginx

# 申请证书（需要交互式输入）
sudo certbot --nginx -d beatsync.site
```

---

## 常见问题

### 问题1：apt update失败

**错误**：`E: Could not get lock /var/lib/dpkg/lock-frontend`

**解决**：
```bash
# 等待其他apt进程完成，或
sudo killall apt apt-get
sudo rm /var/lib/apt/lists/lock
sudo rm /var/cache/apt/archives/lock
sudo rm /var/lib/dpkg/lock*
sudo dpkg --configure -a
sudo apt update
```

---

### 问题2：证书申请失败 - DNS验证失败

**错误**：`Failed to verify domain beatsync.site`

**可能原因**：
- DNS解析未生效
- 域名无法从公网访问

**解决**：
1. 验证DNS解析：
   ```bash
   nslookup beatsync.site 8.8.8.8
   ```

2. 验证域名可访问：
   ```bash
   curl -I http://beatsync.site
   ```

3. 等待DNS传播后重试

---

### 问题3：证书申请失败 - Nginx配置问题

**错误**：`The nginx plugin is not working`

**可能原因**：
- Nginx未运行
- Nginx配置错误
- 端口80未开放

**解决**：
```bash
# 检查Nginx状态
sudo systemctl status nginx

# 检查Nginx配置
sudo nginx -t

# 检查端口80
sudo netstat -tlnp | grep :80

# 检查防火墙
sudo ufw status
```

---

### 问题4：证书申请成功但HTTPS无法访问

**可能原因**：
- 端口443未开放
- Nginx配置未正确应用
- 防火墙阻止443端口

**解决**：
```bash
# 检查端口443
sudo netstat -tlnp | grep :443

# 检查防火墙
sudo ufw allow 443/tcp
sudo ufw reload

# 检查Nginx配置
sudo nginx -t
sudo systemctl reload nginx
```

---

## 证书自动续期

### Let's Encrypt证书有效期

- **有效期**：90天
- **自动续期**：certbot会自动设置定时任务

### 验证自动续期

**检查定时任务**：
```bash
sudo systemctl status certbot.timer
```

**手动测试续期**：
```bash
sudo certbot renew --dry-run
```

---

## 验证清单

- [ ] 安装certbot成功
- [ ] 证书申请成功
- [ ] Nginx配置正确
- [ ] HTTPS可以访问
- [ ] 证书信息正确（Let's Encrypt）
- [ ] 自动续期已配置

---

## 相关文档

- `docs/deployment/LETS_ENCRYPT_SSL_SETUP.md` - Let's Encrypt详细指南
- `docs/deployment/DNS_PROPAGATION_TROUBLESHOOTING.md` - DNS解析问题排查

---

**最后更新**：2025-12-04

