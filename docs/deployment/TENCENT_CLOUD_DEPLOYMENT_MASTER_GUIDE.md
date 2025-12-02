# 腾讯云服务器部署完整指南（标准流程）

> **目的**：提供BeatSync项目在腾讯云服务器上的完整部署流程，作为新服务器部署的标准参考

---

## 文档说明

**适用场景**：
- 新服务器首次部署
- 服务器重装系统后重新部署
- 迁移到新的腾讯云服务器

**前置条件**：
- 已购买腾讯云轻量应用服务器
- 已获取服务器IP地址和登录密码
- 已配置SSH密钥（可选，推荐）

---

## 一、服务器准备

### 1.1 服务器配置要求

**推荐配置**：
- **CPU**：4核或以上
- **内存**：4GB或以上
- **带宽**：3M或以上
- **系统**：Ubuntu 22.04 LTS 64位

**最低配置**：
- **CPU**：2核
- **内存**：2GB
- **带宽**：3M
- **系统**：Ubuntu 22.04 LTS 64位

---

### 1.2 服务器镜像选择

**推荐镜像**：
- **Ubuntu 22.04 LTS 64位**（推荐）
- 原因：稳定、兼容性好、长期支持

**其他可选**：
- Ubuntu 20.04 LTS 64位
- Debian 11 64位

---

### 1.3 地域选择

**推荐地域**：
- **华东地区（上海）**（推荐）
- 原因：网络质量好、延迟低

**备选地域**：
- 华南地区（广州）
- 华北地区（北京）

---

## 二、部署前准备

### 2.1 获取服务器信息

**需要的信息**：
- **服务器IP**：例如 `124.221.58.149`
- **登录用户**：通常是 `ubuntu` 或 `root`
- **登录密码**：服务器登录密码
- **SSH密钥**：如果配置了SSH密钥

---

### 2.2 配置防火墙

**在腾讯云控制台操作**：

1. **登录腾讯云控制台**
   - 访问：https://console.cloud.tencent.com/

2. **进入轻量应用服务器**
   - 左侧菜单 → "轻量应用服务器"
   - 选择您的服务器实例

3. **配置防火墙规则**
   - 点击"防火墙"标签
   - 添加以下规则：

| 端口 | 协议 | 策略 | 来源 | 说明 |
|------|------|------|------|------|
| 22 | TCP | 允许 | 0.0.0.0/0 | SSH登录（必需） |
| 8000 | TCP | 允许 | 0.0.0.0/0 | 后端服务（可选，如果直接访问） |
| 443 | TCP | 允许 | 0.0.0.0/0 | HTTPS（配置Nginx后需要） |
| 80 | TCP | 允许 | 0.0.0.0/0 | HTTP（配置Nginx后需要，可选） |

**注意**：端口8000可以在配置HTTPS后关闭，因为所有请求都通过443端口。

---

## 三、服务器初始化

### 3.1 登录服务器

**方式1：使用SSH（推荐）**

```bash
# 如果使用密码登录
ssh ubuntu@<服务器IP>

# 如果使用SSH密钥
ssh -i ~/.ssh/your_key.pem ubuntu@<服务器IP>
```

**方式2：使用VNC（如果SSH无法使用）**

- 在腾讯云控制台使用VNC登录
- 或使用"执行命令"功能

---

### 3.2 更新系统

```bash
# 更新包列表
sudo apt update

# 升级系统包
sudo apt upgrade -y
```

**如果遇到dpkg错误**：
```bash
# 修复dpkg状态
sudo dpkg --configure -a

# 修复损坏的包
sudo apt --fix-broken install

# 重新升级
sudo apt upgrade -y
```

---

### 3.3 安装基础工具

```bash
# 安装基础工具
sudo apt install -y git curl wget vim build-essential python3-dev

# 安装音频处理库
sudo apt install -y libsndfile1 libsndfile1-dev
```

---

### 3.4 安装Git

```bash
# 安装Git
sudo apt install -y git

# 验证安装
git --version
```

---

### 3.5 安装Python和pip

```bash
# 检查Python版本（应该已安装）
python3 --version

# 安装pip（如果未安装）
sudo apt install -y python3-pip

# 升级pip
pip3 install --upgrade pip
```

---

### 3.6 安装FFmpeg

```bash
# 安装FFmpeg
sudo apt install -y ffmpeg

# 验证安装
ffmpeg -version | head -1
```

---

## 四、部署项目代码

### 4.1 创建项目目录

```bash
# 创建项目目录
sudo mkdir -p /opt/beatsync

# 进入目录
cd /opt
```

---

### 4.2 克隆项目代码

```bash
# 确保在 /opt 目录
cd /opt

# 如果 beatsync 目录已存在，先删除
sudo rm -rf beatsync

# 克隆项目代码
sudo git clone https://github.com/scarlettyellow/BeatSync.git beatsync
```

**验证**：
```bash
ls -la /opt/beatsync
```

---

### 4.3 设置目录权限

```bash
# 设置目录所有者为ubuntu用户
sudo chown -R ubuntu:ubuntu /opt/beatsync

# 验证权限
ls -ld /opt/beatsync
```

---

## 五、安装Python依赖

### 5.1 进入后端目录

```bash
cd /opt/beatsync/web_service/backend
```

---

### 5.2 安装依赖

```bash
# 安装Python依赖
pip3 install -r requirements.txt
```

**如果安装失败**：
```bash
# 使用sudo安装（如果需要）
sudo pip3 install -r requirements.txt
```

---

## 六、创建必要目录

### 6.1 创建目录

```bash
cd /opt/beatsync

# 创建上传和输出目录
sudo mkdir -p web_uploads web_outputs logs outputs/web_uploads outputs/web_outputs outputs/logs

# 设置权限
sudo chmod 755 web_uploads web_outputs logs outputs/web_uploads outputs/web_outputs outputs/logs
```

---

## 七、配置systemd服务

### 7.1 创建服务文件

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
```

**注意**：将 `<服务器IP>` 替换为实际IP地址（如果配置中有）

---

### 7.2 启用并启动服务

```bash
# 重新加载systemd配置
sudo systemctl daemon-reload

# 启用服务（开机自启）
sudo systemctl enable beatsync

# 启动服务
sudo systemctl start beatsync

# 检查服务状态
sudo systemctl status beatsync
```

**预期输出**：应该显示 `active (running)`

---

### 7.3 验证服务

```bash
# 测试本地访问
curl http://localhost:8000/api/health
```

**预期输出**：`{"status":"healthy","timestamp":"..."}`

---

## 八、配置HTTPS（Nginx反向代理）

### 8.1 安装Nginx

```bash
# 更新包列表
sudo apt update

# 安装Nginx
sudo apt install -y nginx

# 验证安装
nginx -v
```

---

### 8.2 生成SSL证书

```bash
# 创建SSL证书目录
sudo mkdir -p /etc/nginx/ssl

# 生成自签名证书（有效期1年）
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout /etc/nginx/ssl/beatsync.key \
  -out /etc/nginx/ssl/beatsync.crt \
  -subj "/C=CN/ST=Shanghai/L=Shanghai/O=BeatSync/CN=<服务器IP>"
```

**注意**：将 `<服务器IP>` 替换为实际IP地址

---

### 8.3 创建Nginx配置

```bash
# 创建Nginx配置目录（如果不存在）
sudo mkdir -p /etc/nginx/sites-available
sudo mkdir -p /etc/nginx/sites-enabled

# 创建配置文件
sudo tee /etc/nginx/sites-available/beatsync > /dev/null << 'EOFNGINX'
server {
    listen 80;
    server_name <服务器IP>;
    
    # HTTP重定向到HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name <服务器IP>;

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

**注意**：将 `<服务器IP>` 替换为实际IP地址（两处）

---

### 8.4 启用Nginx配置

```bash
# 创建符号链接
sudo ln -sf /etc/nginx/sites-available/beatsync /etc/nginx/sites-enabled/

# 删除默认配置（如果存在）
sudo rm -f /etc/nginx/sites-enabled/default

# 测试配置
sudo nginx -t
```

**预期输出**：`nginx: configuration file /etc/nginx/nginx.conf test is successful`

---

### 8.5 启动Nginx

```bash
# 启动Nginx
sudo systemctl start nginx

# 设置开机自启
sudo systemctl enable nginx

# 检查状态
sudo systemctl status nginx
```

**预期输出**：应该显示 `active (running)`

---

### 8.6 配置防火墙（443端口）

**在腾讯云控制台操作**：

1. 进入轻量应用服务器 → 选择实例
2. 点击"防火墙"标签
3. 添加规则：
   - **端口**：443
   - **协议**：TCP
   - **策略**：允许
   - **来源**：0.0.0.0/0

---

### 8.7 验证HTTPS

```bash
# 测试HTTPS访问
curl -k https://<服务器IP>/api/health
```

**预期输出**：`{"status":"healthy","timestamp":"..."}`

**在浏览器中测试**：
- 访问：`https://<服务器IP>/api/health`
- 访问：`https://<服务器IP>/docs`

**注意**：浏览器会显示"不安全"警告（自签名证书），点击"高级" → "继续访问"即可。

---

## 九、更新前端配置

### 9.1 更新前端API地址

**文件**：`web_service/frontend/script.js`

**修改生产环境API地址**：

```javascript
// 生产环境：使用腾讯云服务器（HTTPS）
const backendUrl = window.API_BASE_URL || 'https://<服务器IP>';
```

**注意**：将 `<服务器IP>` 替换为实际IP地址

---

### 9.2 提交并推送

```bash
cd /Users/scarlett/Projects/BeatSync
git add web_service/frontend/script.js
git commit -m "feat: 更新前端API地址到新服务器"
git push origin main
```

---

## 十、验证部署

### 10.1 验证服务状态

```bash
# 检查后端服务
sudo systemctl status beatsync

# 检查Nginx服务
sudo systemctl status nginx
```

**预期输出**：都应该显示 `active (running)`

---

### 10.2 验证API访问

```bash
# 健康检查
curl -k https://<服务器IP>/api/health

# API文档
curl -I https://<服务器IP>/docs
```

**预期输出**：
- 健康检查：`{"status":"healthy","timestamp":"..."}`
- API文档：`HTTP/1.1 200 OK`

---

### 10.3 验证前端功能

**访问前端页面**：
- https://scarlettyellow.github.io/BeatSync/

**测试功能**：
1. 上传dance视频
2. 上传bgm视频
3. 点击"开始处理"
4. 查看处理状态
5. 下载处理结果

---

## 十一、常见问题处理

### 11.1 权限错误

**错误**：`PermissionError: Permission denied`

**解决**：
```bash
# 修复目录权限
sudo chown -R ubuntu:ubuntu /opt/beatsync/outputs
sudo chmod 777 /opt/beatsync/outputs/logs
```

---

### 11.2 服务无法启动

**检查服务状态**：
```bash
sudo systemctl status beatsync
sudo journalctl -u beatsync -n 50
```

**常见原因**：
- Python依赖缺失
- 端口被占用
- 配置文件错误

---

### 11.3 外部无法访问

**检查防火墙**：
- 确认腾讯云防火墙已开放相应端口
- 确认UFW已开放端口（如果启用）

**检查服务监听**：
```bash
sudo netstat -tlnp | grep -E '8000|443'
```

---

### 11.4 证书错误

**浏览器显示证书警告**：
- 这是正常的（自签名证书）
- 用户需要手动接受证书警告
- 详细说明见：`docs/deployment/FIX_CERT_ERROR.md`

---

## 十二、部署检查清单

### 服务器准备
- [ ] 服务器已创建
- [ ] 系统已更新
- [ ] 基础工具已安装
- [ ] Git已安装
- [ ] Python和pip已安装
- [ ] FFmpeg已安装

### 项目部署
- [ ] 项目代码已克隆
- [ ] 目录权限已设置
- [ ] Python依赖已安装
- [ ] 必要目录已创建

### 服务配置
- [ ] systemd服务已创建
- [ ] 服务已启动
- [ ] 服务运行正常

### HTTPS配置
- [ ] Nginx已安装
- [ ] SSL证书已生成
- [ ] Nginx配置已创建
- [ ] Nginx配置已启用
- [ ] Nginx服务运行正常
- [ ] 防火墙已开放443端口

### 前端配置
- [ ] 前端API地址已更新
- [ ] 代码已提交并推送
- [ ] GitHub Pages已部署

### 验证测试
- [ ] 服务状态正常
- [ ] 本地访问正常
- [ ] 外部访问正常
- [ ] 前端功能正常

---

## 十三、一键部署脚本

### 13.1 完整部署脚本

**在服务器上执行**：

```bash
#!/bin/bash
set -e

# 配置变量（需要修改）
SERVER_IP="<服务器IP>"  # 替换为实际IP
PROJECT_DIR="/opt/beatsync"

echo "=========================================="
echo "BeatSync 腾讯云服务器部署脚本"
echo "=========================================="
echo ""

# 步骤1：更新系统
echo "步骤1: 更新系统..."
sudo apt update
sudo apt upgrade -y

# 步骤2：安装基础工具
echo "步骤2: 安装基础工具..."
sudo apt install -y git curl wget vim build-essential python3-dev libsndfile1 libsndfile1-dev

# 步骤3：安装FFmpeg
echo "步骤3: 安装FFmpeg..."
sudo apt install -y ffmpeg

# 步骤4：升级pip
echo "步骤4: 升级pip..."
pip3 install --upgrade pip

# 步骤5：创建项目目录
echo "步骤5: 创建项目目录..."
sudo mkdir -p $PROJECT_DIR
cd /opt

# 步骤6：克隆项目代码
echo "步骤6: 克隆项目代码..."
sudo rm -rf beatsync
sudo git clone https://github.com/scarlettyellow/BeatSync.git beatsync

# 步骤7：设置目录权限
echo "步骤7: 设置目录权限..."
sudo chown -R ubuntu:ubuntu $PROJECT_DIR

# 步骤8：安装Python依赖
echo "步骤8: 安装Python依赖..."
cd $PROJECT_DIR/web_service/backend
pip3 install -r requirements.txt

# 步骤9：创建必要目录
echo "步骤9: 创建必要目录..."
cd $PROJECT_DIR
sudo mkdir -p web_uploads web_outputs logs outputs/web_uploads outputs/web_outputs outputs/logs
sudo chmod 755 web_uploads web_outputs logs outputs/web_uploads outputs/web_outputs outputs/logs

# 步骤10：创建systemd服务
echo "步骤10: 创建systemd服务..."
sudo tee /etc/systemd/system/beatsync.service > /dev/null << EOF
[Unit]
Description=BeatSync Web Service Backend
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=$PROJECT_DIR/web_service/backend
Environment="PATH=/usr/local/bin:/usr/bin:/bin"
Environment="PYTHONPATH=$PROJECT_DIR"
ExecStart=/usr/bin/python3 -m uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# 步骤11：启动服务
echo "步骤11: 启动服务..."
sudo systemctl daemon-reload
sudo systemctl enable beatsync
sudo systemctl start beatsync

# 步骤12：安装Nginx
echo "步骤12: 安装Nginx..."
sudo apt install -y nginx

# 步骤13：生成SSL证书
echo "步骤13: 生成SSL证书..."
sudo mkdir -p /etc/nginx/ssl
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout /etc/nginx/ssl/beatsync.key \
  -out /etc/nginx/ssl/beatsync.crt \
  -subj "/C=CN/ST=Shanghai/L=Shanghai/O=BeatSync/CN=$SERVER_IP"

# 步骤14：创建Nginx配置
echo "步骤14: 创建Nginx配置..."
sudo mkdir -p /etc/nginx/sites-available /etc/nginx/sites-enabled
sudo tee /etc/nginx/sites-available/beatsync > /dev/null << EOFNGINX
server {
    listen 80;
    server_name $SERVER_IP;
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name $SERVER_IP;

    ssl_certificate /etc/nginx/ssl/beatsync.crt;
    ssl_certificate_key /etc/nginx/ssl/beatsync.key;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    client_max_body_size 1G;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        proxy_connect_timeout 600s;
        proxy_send_timeout 600s;
        proxy_read_timeout 600s;
    }
}
EOFNGINX

# 步骤15：启用Nginx配置
echo "步骤15: 启用Nginx配置..."
sudo ln -sf /etc/nginx/sites-available/beatsync /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t

# 步骤16：启动Nginx
echo "步骤16: 启动Nginx..."
sudo systemctl restart nginx
sudo systemctl enable nginx

# 步骤17：验证
echo "步骤17: 验证部署..."
sleep 3
sudo systemctl status beatsync | head -10
sudo systemctl status nginx | head -10

echo ""
echo "=========================================="
echo "部署完成！"
echo "=========================================="
echo ""
echo "服务信息："
echo "  - 服务地址: https://$SERVER_IP"
echo "  - 健康检查: https://$SERVER_IP/api/health"
echo "  - API文档: https://$SERVER_IP/docs"
echo ""
echo "⚠️  重要："
echo "1. 请在腾讯云控制台配置防火墙，开放443端口"
echo "2. 更新前端配置，将API地址改为: https://$SERVER_IP"
echo ""
```

**使用方法**：
1. 将脚本保存为 `deploy.sh`
2. 修改 `SERVER_IP` 变量为实际IP地址
3. 执行：`bash deploy.sh`

---

## 十四、部署后维护

### 14.1 更新代码

```bash
cd /opt/beatsync
git pull origin main
sudo systemctl restart beatsync
```

---

### 14.2 查看日志

```bash
# 服务日志
sudo journalctl -u beatsync -f

# 性能日志
tail -f /opt/beatsync/outputs/logs/performance_$(date +%Y%m%d).log
```

---

### 14.3 重启服务

```bash
# 重启后端服务
sudo systemctl restart beatsync

# 重启Nginx
sudo systemctl restart nginx
```

---

## 十五、故障排查

### 15.1 服务无法启动

**检查步骤**：
1. 查看服务状态：`sudo systemctl status beatsync`
2. 查看日志：`sudo journalctl -u beatsync -n 50`
3. 检查端口：`sudo netstat -tlnp | grep 8000`
4. 检查依赖：`pip3 list | grep fastapi`

---

### 15.2 外部无法访问

**检查步骤**：
1. 检查防火墙：腾讯云控制台 → 防火墙
2. 检查服务监听：`sudo netstat -tlnp | grep 443`
3. 检查Nginx状态：`sudo systemctl status nginx`
4. 查看Nginx日志：`sudo tail -f /var/log/nginx/error.log`

---

### 15.3 证书错误

**说明**：
- 自签名证书会在浏览器中显示警告
- 用户需要手动接受证书警告
- 这是正常的，不影响功能

---

## 十六、部署时间估算

**完整部署时间**：
- 服务器初始化：5-10分钟
- 项目部署：5-10分钟
- HTTPS配置：5-10分钟
- 验证测试：5分钟
- **总计**：20-35分钟

**如果使用一键部署脚本**：
- 脚本执行：10-15分钟
- 验证测试：5分钟
- **总计**：15-20分钟

---

## 十七、部署经验总结

### 17.1 关键步骤

1. **防火墙配置**：必须在部署前配置，否则无法访问
2. **目录权限**：确保日志目录有写入权限
3. **SSL证书**：自签名证书需要用户手动接受
4. **服务监听**：确保服务监听0.0.0.0而不是127.0.0.1

---

### 17.2 常见错误

1. **权限错误**：目录权限不足
2. **端口占用**：端口被其他进程占用
3. **防火墙未开放**：外部无法访问
4. **证书错误**：浏览器显示警告（正常）

---

### 17.3 最佳实践

1. **使用SSH登录**：比VNC更方便
2. **分步执行**：遇到问题更容易定位
3. **验证每步**：确保每步都成功再继续
4. **保留日志**：便于排查问题

---

## 十八、相关文档

### 部署相关
- `docs/deployment/STEP_BY_STEP_DEPLOYMENT.md` - 分步部署指南
- `docs/deployment/DEPLOYMENT_COMPLETE.md` - 部署完成总结
- `docs/deployment/HTTPS_SETUP_STEP_BY_STEP.md` - HTTPS配置指南

### 故障排查
- `docs/deployment/FIX_PERMISSION_ERROR.md` - 权限错误修复
- `docs/deployment/FIX_EXTERNAL_ACCESS.md` - 外部访问修复
- `docs/deployment/FIX_CERT_ERROR.md` - 证书错误修复

### 架构说明
- `docs/ARCHITECTURE_OVERVIEW.md` - 服务架构概览
- `docs/LOGGING_GUIDE.md` - 日志查看指南

---

## 十九、快速参考

### 服务器信息模板

**新服务器部署时，记录以下信息**：

```
服务器信息：
- IP地址：<服务器IP>
- 配置：<CPU核数>核<内存>GB<带宽>M
- 系统：Ubuntu 22.04 LTS
- 登录用户：ubuntu
- 创建时间：<日期>

服务地址：
- 后端API：https://<服务器IP>
- 健康检查：https://<服务器IP>/api/health
- API文档：https://<服务器IP>/docs

防火墙端口：
- 22：SSH（必需）
- 443：HTTPS（必需）
- 8000：后端服务（可选）
```

---

### 常用命令速查

```bash
# 服务管理
sudo systemctl status beatsync
sudo systemctl restart beatsync
sudo journalctl -u beatsync -f

# 日志查看
tail -f /opt/beatsync/outputs/logs/performance_$(date +%Y%m%d).log
sudo tail -f /var/log/nginx/error.log

# 端口检查
sudo netstat -tlnp | grep -E '8000|443'

# 更新代码
cd /opt/beatsync && git pull origin main && sudo systemctl restart beatsync
```

---

## 二十、版本信息

**文档版本**：v1.0
**最后更新**：2025-12-02
**适用项目**：BeatSync
**适用服务器**：腾讯云轻量应用服务器

---

**此文档作为新服务器部署的标准参考，建议每次部署时按照此流程执行。**

