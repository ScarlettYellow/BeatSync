# 腾讯云服务器快速部署步骤

> **快速参考**：按照以下步骤快速部署BeatSync到腾讯云服务器

---

## 前置条件

- ✅ 服务器已创建（Ubuntu 22.04 LTS）
- ✅ 服务器IP：1.12.239.225
- ✅ 已获取服务器登录密码或SSH密钥

---

## 方式1：使用部署脚本（推荐）

### 步骤1：上传项目到服务器

**在本地机器上执行**：

```bash
cd /Users/scarlett/Projects/BeatSync
./scripts/deployment/upload_to_tencent_cloud.sh
```

**或手动使用rsync**：

```bash
rsync -avz --exclude '.git' --exclude '__pycache__' \
  --exclude '*.pyc' --exclude '.beatsync_cache' \
  . root@1.12.239.225:/opt/beatsync
```

### 步骤2：SSH连接到服务器

```bash
ssh root@1.12.239.225
```

### 步骤3：运行部署脚本

```bash
cd /opt/beatsync
sudo bash scripts/deployment/deploy_to_tencent_cloud.sh
```

**脚本会自动完成**：
- ✅ 更新系统
- ✅ 安装依赖（Python、FFmpeg等）
- ✅ 安装Python包
- ✅ 创建必要目录
- ✅ 配置systemd服务
- ✅ 启动服务

---

## 方式2：手动部署

### 步骤1：连接服务器

```bash
ssh root@1.12.239.225
```

### 步骤2：上传项目代码

**在本地机器上**：

```bash
# 使用rsync上传
rsync -avz --exclude '.git' --exclude '__pycache__' \
  --exclude '*.pyc' . root@1.12.239.225:/opt/beatsync
```

### 步骤3：安装系统依赖

```bash
# 在服务器上执行
sudo apt update && sudo apt upgrade -y
sudo apt install -y git curl wget vim build-essential python3-dev libsndfile1 libsndfile1-dev
sudo apt install -y ffmpeg
```

### 步骤4：安装Python依赖

```bash
cd /opt/beatsync/web_service/backend
pip3 install -r requirements.txt
```

### 步骤5：创建目录

```bash
cd /opt/beatsync
mkdir -p web_uploads web_outputs logs outputs/web_uploads outputs/web_outputs
chmod 755 web_uploads web_outputs logs outputs/web_uploads outputs/web_outputs
```

### 步骤6：创建systemd服务

```bash
sudo vim /etc/systemd/system/beatsync.service
```

**内容**：

```ini
[Unit]
Description=BeatSync Web Service Backend
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/beatsync/web_service/backend
Environment="PATH=/usr/local/bin:/usr/bin:/bin"
ExecStart=/usr/bin/python3 -m uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

### 步骤7：启动服务

```bash
sudo systemctl daemon-reload
sudo systemctl enable beatsync
sudo systemctl start beatsync
sudo systemctl status beatsync
```

---

## 步骤8：配置防火墙

### 在腾讯云控制台

1. 进入服务器详情页
2. 点击"防火墙"标签
3. 添加规则：
   - **端口**：8000
   - **协议**：TCP
   - **来源**：0.0.0.0/0
   - **动作**：允许

---

## 步骤9：测试服务

```bash
# 在服务器上测试
curl http://localhost:8000/api/health

# 从本地机器测试
curl http://1.12.239.225:8000/api/health
```

**预期输出**：`{"status":"healthy","timestamp":"..."}`

---

## 步骤10：更新前端配置

### 已自动更新

前端配置已更新为使用腾讯云服务器地址：`http://1.12.239.225:8000`

### 部署前端更新

```bash
# 在本地项目目录
cd /Users/scarlett/Projects/BeatSync
git add web_service/frontend/script.js
git commit -m "feat: 更新前端API地址为腾讯云服务器"
git push origin main
```

**GitHub Pages会自动部署更新**（通常几分钟内生效）

---

## 验证部署

### 1. 服务状态

```bash
sudo systemctl status beatsync
```

**应该显示**：`active (running)`

### 2. 健康检查

访问：http://1.12.239.225:8000/api/health

**应该返回**：`{"status":"healthy","timestamp":"..."}`

### 3. API文档

访问：http://1.12.239.225:8000/docs

**应该显示**：FastAPI自动生成的API文档

### 4. 前端测试

访问：https://scarlettyellow.github.io/BeatSync/

**应该能够**：
- ✅ 上传视频文件
- ✅ 提交处理任务
- ✅ 查看处理状态
- ✅ 下载处理结果

---

## 常用命令

```bash
# 查看服务状态
sudo systemctl status beatsync

# 查看服务日志
sudo journalctl -u beatsync -f

# 重启服务
sudo systemctl restart beatsync

# 停止服务
sudo systemctl stop beatsync

# 启动服务
sudo systemctl start beatsync
```

---

## 故障排查

### 服务无法启动

```bash
# 查看详细日志
sudo journalctl -u beatsync -n 50
```

### 无法访问服务

1. 检查服务状态：`sudo systemctl status beatsync`
2. 检查端口监听：`sudo netstat -tlnp | grep 8000`
3. 检查防火墙：腾讯云控制台 → 防火墙 → 确认8000端口已开放

### 处理失败

1. 检查FFmpeg：`ffmpeg -version`
2. 检查磁盘空间：`df -h`
3. 检查内存使用：`free -h`

---

## 完成！

部署完成后，你的服务应该：
- ✅ 运行在 http://1.12.239.225:8000
- ✅ 前端可以正常访问和使用
- ✅ 处理时间相比Render大幅降低（预期2-4分钟）

**下一步**：进行性能测试，验证处理时间是否达到预期！

---

**最后更新**：2025-11-27












