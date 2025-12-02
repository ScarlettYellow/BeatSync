# 腾讯云服务器快速部署参考（速查版）

> **目的**：提供快速部署参考，适合有经验的用户快速执行

---

## 前置条件

- ✅ 已购买腾讯云轻量应用服务器
- ✅ 已获取服务器IP和登录密码
- ✅ 已配置防火墙（22、443端口）

---

## 快速部署流程

### 1. 登录服务器

```bash
ssh ubuntu@<服务器IP>
```

---

### 2. 系统初始化

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装基础工具
sudo apt install -y git curl wget vim build-essential python3-dev libsndfile1 libsndfile1-dev

# 安装FFmpeg
sudo apt install -y ffmpeg

# 升级pip
pip3 install --upgrade pip
```

---

### 3. 部署项目

```bash
# 克隆代码
cd /opt
sudo rm -rf beatsync
sudo git clone https://github.com/scarlettyellow/BeatSync.git beatsync

# 设置权限
sudo chown -R ubuntu:ubuntu /opt/beatsync

# 安装依赖
cd /opt/beatsync/web_service/backend
pip3 install -r requirements.txt

# 创建目录
cd /opt/beatsync
sudo mkdir -p web_uploads web_outputs logs outputs/web_uploads outputs/web_outputs outputs/logs
sudo chmod 755 web_uploads web_outputs logs outputs/web_uploads outputs/web_outputs outputs/logs
```

---

### 4. 配置systemd服务

```bash
sudo tee /etc/systemd/system/beatsync.service > /dev/null << 'EOF'
[Unit]
Description=BeatSync Web Service Backend
After=network.target
[Service]
Type=simple
User=root
WorkingDirectory=/opt/beatsync/web_service/backend
Environment="PATH=/usr/local/bin:/usr/bin:/bin"
Environment="PYTHONPATH=/opt/beatsync"
ExecStart=/usr/bin/python3 -m uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable beatsync
sudo systemctl start beatsync
```

---

### 5. 配置HTTPS（Nginx）

```bash
# 安装Nginx
sudo apt install -y nginx

# 生成SSL证书
sudo mkdir -p /etc/nginx/ssl
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout /etc/nginx/ssl/beatsync.key \
  -out /etc/nginx/ssl/beatsync.crt \
  -subj "/C=CN/ST=Shanghai/L=Shanghai/O=BeatSync/CN=<服务器IP>"

# 创建Nginx配置
sudo mkdir -p /etc/nginx/sites-available /etc/nginx/sites-enabled
sudo tee /etc/nginx/sites-available/beatsync > /dev/null << 'EOFNGINX'
server {
    listen 80;
    server_name <服务器IP>;
    return 301 https://$server_name$request_uri;
}
server {
    listen 443 ssl http2;
    server_name <服务器IP>;
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

# 启用配置
sudo ln -sf /etc/nginx/sites-available/beatsync /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t

# 启动Nginx
sudo systemctl restart nginx
sudo systemctl enable nginx
```

**注意**：将 `<服务器IP>` 替换为实际IP地址（3处）

---

### 6. 配置防火墙

**在腾讯云控制台**：
- 开放443端口（TCP，0.0.0.0/0）

---

### 7. 验证部署

```bash
# 检查服务状态
sudo systemctl status beatsync
sudo systemctl status nginx

# 测试访问
curl -k https://<服务器IP>/api/health
```

---

### 8. 更新前端配置

**文件**：`web_service/frontend/script.js`

```javascript
// 生产环境：使用腾讯云服务器（HTTPS）
const backendUrl = window.API_BASE_URL || 'https://<服务器IP>';
```

**提交并推送**：
```bash
git add web_service/frontend/script.js
git commit -m "feat: 更新前端API地址到新服务器"
git push origin main
```

---

## 常见问题快速修复

### 权限错误

```bash
sudo chown -R ubuntu:ubuntu /opt/beatsync/outputs
sudo chmod 777 /opt/beatsync/outputs/logs
```

---

### 服务无法启动

```bash
sudo journalctl -u beatsync -n 50
sudo systemctl restart beatsync
```

---

### 外部无法访问

```bash
# 检查端口
sudo netstat -tlnp | grep -E '8000|443'

# 检查防火墙（腾讯云控制台）
```

---

## 部署检查清单

- [ ] 系统已更新
- [ ] 基础工具已安装
- [ ] 项目代码已克隆
- [ ] Python依赖已安装
- [ ] systemd服务已配置
- [ ] 服务运行正常
- [ ] Nginx已配置
- [ ] HTTPS访问正常
- [ ] 防火墙已配置
- [ ] 前端配置已更新

---

## 完整文档

**详细步骤**：`docs/deployment/TENCENT_CLOUD_DEPLOYMENT_MASTER_GUIDE.md`

---

**最后更新**：2025-12-02

