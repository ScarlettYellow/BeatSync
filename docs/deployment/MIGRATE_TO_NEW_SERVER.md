# 迁移到新服务器（4核4GB）部署指南

> **新服务器信息**：
> - 实例名称：Ubuntu-COrR
> - IPv4地址：124.221.58.149
> - 地域：上海 | 上海五区
> - 配置：4核4GB，40GB SSD，3Mbps带宽
> - 镜像：Ubuntu 22.04 LTS
> - 到期时间：2026-12-01

---

## 一、部署前准备

### 1.1 确认新服务器信息

- ✅ **服务器已创建**：Ubuntu 22.04 LTS
- ✅ **状态**：运行中
- ✅ **IP地址**：124.221.58.149
- ✅ **地域**：上海
- ✅ **配置**：4核4GB（已升级）

### 1.2 获取登录信息

**登录方式**：
1. 在腾讯云控制台，点击"重置密码"设置新密码
2. 或者使用SSH密钥（如果已配置）
3. 默认用户名：`ubuntu`

---

## 二、部署步骤

### 步骤1：连接新服务器

```bash
# 使用密码登录
ssh ubuntu@124.221.58.149

# 或使用root（如果已配置）
ssh root@124.221.58.149
```

### 步骤2：安装基础依赖

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装基础工具
sudo apt install -y git curl wget vim

# 安装Python和pip
sudo apt install -y python3 python3-pip python3-venv

# 安装FFmpeg
sudo apt install -y ffmpeg

# 验证安装
python3 --version
ffmpeg -version
```

### 步骤3：克隆项目代码

```bash
# 创建项目目录
sudo mkdir -p /opt/beatsync
cd /opt

# 克隆项目（如果使用Git）
sudo git clone https://github.com/scarlettyellow/BeatSync.git beatsync

# 设置权限
sudo chown -R ubuntu:ubuntu /opt/beatsync
cd /opt/beatsync
```

### 步骤4：安装Python依赖

```bash
cd /opt/beatsync

# 安装Python依赖
pip3 install --user numpy soundfile librosa opencv-python fastapi uvicorn python-multipart
```

### 步骤5：配置Nginx（HTTPS反向代理）

```bash
# 安装Nginx
sudo apt install -y nginx

# 创建SSL证书目录
sudo mkdir -p /etc/nginx/ssl

# 生成自签名SSL证书
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout /etc/nginx/ssl/beatsync.key \
  -out /etc/nginx/ssl/beatsync.crt \
  -subj "/C=CN/ST=Shanghai/L=Shanghai/O=BeatSync/CN=124.221.58.149"

# 创建Nginx配置
sudo bash -c 'cat > /etc/nginx/sites-available/beatsync << "EOFNGINX"
server {
    listen 80;
    server_name 124.221.58.149;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name 124.221.58.149;

    ssl_certificate /etc/nginx/ssl/beatsync.crt;
    ssl_certificate_key /etc/nginx/ssl/beatsync.key;

    # 增加文件大小限制（1GB）
    client_max_body_size 1G;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOFNGINX
'

# 启用配置
sudo ln -sf /etc/nginx/sites-available/beatsync /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# 测试配置
sudo nginx -t

# 重启Nginx
sudo systemctl restart nginx
sudo systemctl enable nginx
```

### 步骤6：创建系统服务

```bash
# 创建systemd服务文件
sudo bash -c 'cat > /etc/systemd/system/beatsync.service << "EOFSERVICE"
[Unit]
Description=BeatSync Web Service
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/opt/beatsync
Environment="PATH=/usr/local/bin:/usr/bin:/bin"
ExecStart=/usr/bin/python3 -m uvicorn web_service.backend.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOFSERVICE
'

# 重载systemd
sudo systemctl daemon-reload

# 启动服务
sudo systemctl start beatsync
sudo systemctl enable beatsync

# 检查状态
sudo systemctl status beatsync
```

### 步骤7：配置防火墙

在腾讯云控制台：
1. 进入"防火墙"标签
2. 添加规则：
   - **端口**：443（HTTPS）
   - **协议**：TCP
   - **来源**：0.0.0.0/0
   - **动作**：允许

### 步骤8：更新前端代码

更新前端代码中的API地址：

```bash
# 在本地项目目录
cd /Users/scarlett/Projects/BeatSync
```

需要修改 `web_service/frontend/script.js`：

```javascript
// 将旧IP地址改为新IP地址
const backendUrl = 'https://124.221.58.149';  // 新服务器IP
```

---

## 三、分步部署命令（推荐）

### 步骤1：修复系统状态（如果需要）

```bash
sudo dpkg --configure -a
```

### 步骤2：更新系统

```bash
sudo apt update
sudo apt upgrade -y
```

### 步骤3：安装Git

```bash
sudo apt install -y git
```

### 步骤4：创建项目目录并克隆代码

```bash
sudo mkdir -p /opt/beatsync
cd /opt
sudo rm -rf beatsync
sudo git clone https://github.com/scarlettyellow/BeatSync.git beatsync
```

### 步骤5：设置目录权限

```bash
sudo chown -R ubuntu:ubuntu /opt/beatsync
```

### 步骤6：运行部署脚本

```bash
cd /opt/beatsync
sudo bash scripts/deployment/deploy_to_tencent_cloud.sh
```

---

## 三-1、一键部署脚本（可选）

如果所有步骤都正常，也可以使用一键部署脚本：

```bash
# 在服务器上执行
cd /opt && sudo rm -rf beatsync && \
sudo git clone https://github.com/scarlettyellow/BeatSync.git beatsync && \
sudo chown -R ubuntu:ubuntu /opt/beatsync && \
cd /opt/beatsync && \
sudo bash scripts/deployment/deploy_to_tencent_cloud.sh
```

---

## 四、验证部署

### 4.1 检查服务状态

```bash
# 检查后端服务
sudo systemctl status beatsync

# 检查Nginx
sudo systemctl status nginx

# 检查端口
sudo netstat -tlnp | grep -E '8000|443'
```

### 4.2 测试API

```bash
# 健康检查
curl -k https://124.221.58.149/api/health

# 应该返回：{"status":"healthy"}
```

### 4.3 访问API文档

在浏览器中访问：
- **API文档**：https://124.221.58.149/docs
- **健康检查**：https://124.221.58.149/api/health

**注意**：由于是自签名证书，浏览器会显示"不安全"警告，点击"高级" → "继续访问"即可。

---

## 五、更新前端代码

### 5.1 修改API地址

在本地项目目录：

```bash
cd /Users/scarlett/Projects/BeatSync
```

修改 `web_service/frontend/script.js`：

```javascript
// 找到这一行（大约第29行）
const backendUrl = window.API_BASE_URL || 'https://1.12.239.225';

// 改为
const backendUrl = window.API_BASE_URL || 'https://124.221.58.149';
```

### 5.2 提交并推送

```bash
git add web_service/frontend/script.js
git commit -m "feat: 更新API地址到新服务器 124.221.58.149"
git push origin main
```

### 5.3 等待GitHub Pages部署

等待2-3分钟让GitHub Pages自动部署完成。

---

## 六、性能测试

### 6.1 测试处理时间

使用waitonme高清版本样本测试：

**预期效果**：
- 处理时间：**0.8-1.2分钟**
- 相比旧服务器（2核2GB）：减少约2-2.5分钟
- **应该达到1分钟目标**

### 6.2 监控服务器资源

```bash
# 查看CPU和内存使用
htop

# 或使用
top
```

---

## 七、旧服务器处理（可选）

### 7.1 保留旧服务器

如果旧服务器还在使用：
- 可以保留一段时间作为备份
- 确认新服务器稳定后再停止

### 7.2 停止旧服务器

如果不再需要旧服务器：
1. 在腾讯云控制台停止实例
2. 或者删除实例（注意：删除后无法恢复）

---

## 八、常见问题

### Q1: 连接服务器失败

**解决**：
1. 检查防火墙是否开放22端口（SSH）
2. 检查服务器状态是否为"运行中"
3. 确认IP地址是否正确

### Q2: 服务启动失败

**解决**：
```bash
# 查看日志
sudo journalctl -u beatsync -f

# 检查Python依赖
pip3 list | grep -E 'fastapi|uvicorn'
```

### Q3: Nginx配置错误

**解决**：
```bash
# 测试配置
sudo nginx -t

# 查看错误日志
sudo tail -f /var/log/nginx/error.log
```

### Q4: 前端无法连接

**解决**：
1. 检查防火墙是否开放443端口
2. 检查Nginx是否运行
3. 检查后端服务是否运行
4. 确认API地址是否正确

---

## 九、快速检查清单

- [ ] 服务器已创建并运行
- [ ] SSH连接成功
- [ ] 基础依赖已安装（Python、FFmpeg）
- [ ] 项目代码已克隆
- [ ] Python依赖已安装
- [ ] Nginx已配置并运行
- [ ] SSL证书已生成
- [ ] 后端服务已启动
- [ ] 防火墙已配置（443端口）
- [ ] 前端代码已更新
- [ ] API健康检查通过
- [ ] 性能测试完成

---

## 十、预期效果

### 性能提升

**旧服务器（2核2GB）**：
- 处理时间：3.25分钟（代码优化后）

**新服务器（4核4GB）**：
- 处理时间：**0.8-1.2分钟**
- 提升：**2-2.5分钟**（62-77%）
- **应该达到1分钟目标** ✅

---

**最后更新**：2025-12-01  
**新服务器IP**：124.221.58.149

