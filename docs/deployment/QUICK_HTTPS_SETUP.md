# 快速配置HTTPS（解决Mixed Content错误）

> **问题**：HTTPS前端页面无法访问HTTP后端（Mixed Content错误）

---

## 问题分析

**错误信息**：
```
Mixed Content: The page at 'https://scarlettyellow.github.io/BeatSync/' 
was loaded over HTTPS, but requested an insecure resource 
'http://124.221.58.149:8000/api/health'. 
This request has been blocked; the content must be served over HTTPS.
```

**原因**：
- ✅ 前端：HTTPS（GitHub Pages）
- ❌ 后端：HTTP（http://124.221.58.149:8000）
- 浏览器安全策略：HTTPS页面不能请求HTTP资源

**解决方案**：配置Nginx反向代理 + 自签名SSL证书（HTTPS）

---

## 快速配置步骤

### 步骤1：安装Nginx

```bash
sudo apt update
sudo apt install -y nginx
```

---

### 步骤2：生成自签名SSL证书

```bash
# 创建SSL证书目录
sudo mkdir -p /etc/nginx/ssl

# 生成自签名证书（有效期1年）
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout /etc/nginx/ssl/beatsync.key \
  -out /etc/nginx/ssl/beatsync.crt \
  -subj "/C=CN/ST=Shanghai/L=Shanghai/O=BeatSync/CN=124.221.58.149"
```

**注意**：自签名证书会在浏览器中显示"不安全"警告，但可以解决Mixed Content问题。

---

### 步骤3：配置Nginx反向代理

```bash
sudo tee /etc/nginx/sites-available/beatsync > /dev/null << 'EOFNGINX'
server {
    listen 80;
    server_name 124.221.58.149;
    
    # HTTP重定向到HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name 124.221.58.149;

    # SSL证书配置
    ssl_certificate /etc/nginx/ssl/beatsync.crt;
    ssl_certificate_key /etc/nginx/ssl/beatsync.key;
    
    # SSL配置（提高安全性）
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # 文件上传大小限制（1GB）
    client_max_body_size 1G;

    # 反向代理到后端服务
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # 超时设置
        proxy_connect_timeout 600s;
        proxy_send_timeout 600s;
        proxy_read_timeout 600s;
    }
}
EOFNGINX
```

---

### 步骤4：启用Nginx配置

```bash
# 创建符号链接
sudo ln -sf /etc/nginx/sites-available/beatsync /etc/nginx/sites-enabled/

# 删除默认配置（如果存在）
sudo rm -f /etc/nginx/sites-enabled/default

# 测试配置
sudo nginx -t
```

**如果测试通过，继续下一步**

---

### 步骤5：重启Nginx

```bash
sudo systemctl restart nginx
sudo systemctl enable nginx
```

---

### 步骤6：配置防火墙（开放443端口）

**在腾讯云控制台操作**：

1. 登录腾讯云控制台
2. 进入轻量应用服务器 → 选择实例
3. 点击"防火墙"标签
4. 添加规则：
   - **端口**：`443`
   - **协议**：`TCP`
   - **策略**：`允许`
   - **来源**：`0.0.0.0/0`
5. 点击"确定"

**或者在服务器上执行**（如果UFW启用）：
```bash
sudo ufw allow 443/tcp
sudo ufw reload
```

---

### 步骤7：验证HTTPS配置

```bash
# 测试HTTPS访问
curl -k https://124.221.58.149/api/health
```

**预期输出**：`{"status":"healthy","timestamp":"..."}`

**在浏览器中访问**：
- `https://124.221.58.149/api/health`
- `https://124.221.58.149/docs`

**注意**：浏览器会显示"不安全"警告（因为是自签名证书），点击"高级" → "继续访问"即可。

---

## 一键配置脚本

**在服务器上执行以下完整脚本**：

```bash
#!/bin/bash
set -e

echo "=== 配置HTTPS（Nginx + 自签名证书）==="
echo ""

# 步骤1：安装Nginx
echo "步骤1: 安装Nginx..."
sudo apt update
sudo apt install -y nginx
echo "✅ Nginx已安装"
echo ""

# 步骤2：生成SSL证书
echo "步骤2: 生成自签名SSL证书..."
sudo mkdir -p /etc/nginx/ssl
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout /etc/nginx/ssl/beatsync.key \
  -out /etc/nginx/ssl/beatsync.crt \
  -subj "/C=CN/ST=Shanghai/L=Shanghai/O=BeatSync/CN=124.221.58.149"
echo "✅ SSL证书已生成"
echo ""

# 步骤3：配置Nginx
echo "步骤3: 配置Nginx反向代理..."
sudo tee /etc/nginx/sites-available/beatsync > /dev/null << 'EOFNGINX'
server {
    listen 80;
    server_name 124.221.58.149;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name 124.221.58.149;

    ssl_certificate /etc/nginx/ssl/beatsync.crt;
    ssl_certificate_key /etc/nginx/ssl/beatsync.key;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    client_max_body_size 1G;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        proxy_connect_timeout 600s;
        proxy_send_timeout 600s;
        proxy_read_timeout 600s;
    }
}
EOFNGINX

# 步骤4：启用配置
echo "步骤4: 启用Nginx配置..."
sudo ln -sf /etc/nginx/sites-available/beatsync /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
echo "✅ Nginx配置已启用"
echo ""

# 步骤5：重启Nginx
echo "步骤5: 重启Nginx..."
sudo systemctl restart nginx
sudo systemctl enable nginx
echo "✅ Nginx已启动"
echo ""

# 步骤6：开放防火墙（UFW）
echo "步骤6: 配置防火墙..."
if sudo ufw status | grep -q "Status: active"; then
    sudo ufw allow 443/tcp
    sudo ufw reload
    echo "✅ UFW已配置（443端口）"
else
    echo "⚠️  UFW未启用，请在腾讯云控制台配置防火墙（443端口）"
fi
echo ""

# 步骤7：验证
echo "步骤7: 验证HTTPS配置..."
sleep 2
if curl -k -s https://124.221.58.149/api/health | grep -q "healthy"; then
    echo "✅ HTTPS配置成功！"
    echo ""
    echo "访问地址："
    echo "  - https://124.221.58.149/api/health"
    echo "  - https://124.221.58.149/docs"
    echo ""
    echo "⚠️  重要：请在腾讯云控制台配置防火墙，开放443端口！"
else
    echo "❌ HTTPS配置失败，请检查日志："
    echo "   sudo journalctl -u nginx -n 50"
fi
```

**保存为脚本并执行**：
```bash
# 保存脚本
cat > /tmp/setup_https.sh << 'EOF'
#!/bin/bash
set -e
echo "=== 配置HTTPS（Nginx + 自签名证书）==="
echo ""
echo "步骤1: 安装Nginx..."
sudo apt update
sudo apt install -y nginx
echo "✅ Nginx已安装"
echo ""
echo "步骤2: 生成自签名SSL证书..."
sudo mkdir -p /etc/nginx/ssl
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout /etc/nginx/ssl/beatsync.key \
  -out /etc/nginx/ssl/beatsync.crt \
  -subj "/C=CN/ST=Shanghai/L=Shanghai/O=BeatSync/CN=124.221.58.149"
echo "✅ SSL证书已生成"
echo ""
echo "步骤3: 配置Nginx反向代理..."
sudo tee /etc/nginx/sites-available/beatsync > /dev/null << 'EOFNGINX'
server {
    listen 80;
    server_name 124.221.58.149;
    return 301 https://$server_name$request_uri;
}
server {
    listen 443 ssl http2;
    server_name 124.221.58.149;
    ssl_certificate /etc/nginx/ssl/beatsync.crt;
    ssl_certificate_key /etc/nginx/ssl/beatsync.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    client_max_body_size 1G;
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 600s;
        proxy_send_timeout 600s;
        proxy_read_timeout 600s;
    }
}
EOFNGINX
echo "步骤4: 启用Nginx配置..."
sudo ln -sf /etc/nginx/sites-available/beatsync /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
echo "✅ Nginx配置已启用"
echo ""
echo "步骤5: 重启Nginx..."
sudo systemctl restart nginx
sudo systemctl enable nginx
echo "✅ Nginx已启动"
echo ""
echo "步骤6: 配置防火墙..."
if sudo ufw status | grep -q "Status: active"; then
    sudo ufw allow 443/tcp
    sudo ufw reload
    echo "✅ UFW已配置（443端口）"
else
    echo "⚠️  UFW未启用，请在腾讯云控制台配置防火墙（443端口）"
fi
echo ""
echo "步骤7: 验证HTTPS配置..."
sleep 2
if curl -k -s https://124.221.58.149/api/health | grep -q "healthy"; then
    echo "✅ HTTPS配置成功！"
    echo ""
    echo "访问地址："
    echo "  - https://124.221.58.149/api/health"
    echo "  - https://124.221.58.149/docs"
    echo ""
    echo "⚠️  重要：请在腾讯云控制台配置防火墙，开放443端口！"
else
    echo "❌ HTTPS配置失败，请检查日志："
    echo "   sudo journalctl -u nginx -n 50"
fi
EOF

# 执行脚本
chmod +x /tmp/setup_https.sh
bash /tmp/setup_https.sh
```

---

## 更新前端配置

**配置HTTPS后，需要更新前端配置**：

**文件**：`web_service/frontend/script.js`

**更新为**：
```javascript
// 生产环境：使用腾讯云服务器（HTTPS）
const backendUrl = window.API_BASE_URL || 'https://124.221.58.149';
```

**然后提交并推送**：
```bash
cd /Users/scarlett/Projects/BeatSync
git add web_service/frontend/script.js
git commit -m "feat: 更新前端API地址为HTTPS"
git push origin main
```

---

## 验证清单

- [ ] Nginx已安装
- [ ] SSL证书已生成
- [ ] Nginx配置已启用
- [ ] Nginx服务运行正常
- [ ] 防火墙已开放443端口（腾讯云控制台）
- [ ] HTTPS访问正常：`curl -k https://124.221.58.149/api/health`
- [ ] 前端配置已更新为HTTPS
- [ ] 前端页面可以正常访问后端

---

## 浏览器警告处理

**自签名证书会在浏览器中显示"不安全"警告**：

1. 访问 `https://124.221.58.149/api/health`
2. 浏览器会显示"您的连接不是私密连接"
3. 点击"高级"
4. 点击"继续前往 124.221.58.149（不安全）"

**这是正常的，因为使用的是自签名证书。**

---

## 故障排查

### 如果HTTPS无法访问

1. **检查Nginx状态**
   ```bash
   sudo systemctl status nginx
   ```

2. **检查Nginx配置**
   ```bash
   sudo nginx -t
   ```

3. **查看Nginx日志**
   ```bash
   sudo tail -f /var/log/nginx/error.log
   ```

4. **检查防火墙**
   - 腾讯云控制台 → 防火墙 → 确认443端口已开放

5. **检查SSL证书**
   ```bash
   ls -la /etc/nginx/ssl/
   ```

---

**最后更新**：2025-12-02

