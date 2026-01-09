# 修复腾讯云"执行命令"失败问题

> **问题**：执行命令失败，ExitCode 127，找不到部署脚本

---

## 问题分析

**错误原因**：
- Git克隆可能没有完全完成
- 脚本路径可能不正确
- 需要先验证文件是否存在

---

## 解决方案1：分步执行（推荐）

### 步骤1：克隆项目并检查

在腾讯云控制台"执行命令"中执行：

```bash
sudo apt update && sudo apt install -y git && sudo mkdir -p /opt/beatsync && cd /opt && sudo rm -rf beatsync && sudo git clone https://github.com/scarlettyellow/BeatSync.git beatsync && sudo chown -R ubuntu:ubuntu /opt/beatsync && ls -la /opt/beatsync/scripts/deployment/
```

**这个命令会**：
- 更新系统并安装Git
- 删除旧的目录（如果存在）
- 重新克隆项目
- 设置权限
- 列出部署脚本目录，验证文件是否存在

**预期输出**：应该看到 `deploy_to_tencent_cloud.sh` 文件

### 步骤2：执行部署脚本

如果步骤1成功，执行：

```bash
cd /opt/beatsync && sudo bash scripts/deployment/deploy_to_tencent_cloud.sh
```

---

## 解决方案2：直接执行部署命令（如果脚本不存在）

如果脚本文件确实不存在，可以直接执行部署命令：

```bash
cd /opt/beatsync && \
sudo apt update && sudo apt upgrade -y && \
sudo apt install -y git curl wget vim build-essential python3-dev libsndfile1 libsndfile1-dev && \
sudo apt install -y ffmpeg && \
cd /opt/beatsync/web_service/backend && \
pip3 install -r requirements.txt && \
cd /opt/beatsync && \
sudo mkdir -p web_uploads web_outputs logs outputs/web_uploads outputs/web_outputs && \
sudo chmod 755 web_uploads web_outputs logs outputs/web_uploads outputs/web_outputs && \
sudo bash -c 'cat > /etc/systemd/system/beatsync.service << EOF
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
EOF
' && \
sudo systemctl daemon-reload && \
sudo systemctl enable beatsync && \
sudo systemctl start beatsync && \
sudo systemctl status beatsync | head -10
```

---

## 解决方案3：检查并修复（推荐流程）

### 步骤1：检查项目是否克隆成功

```bash
ls -la /opt/beatsync/
```

**应该看到**：项目文件和目录

### 步骤2：检查脚本是否存在

```bash
ls -la /opt/beatsync/scripts/deployment/
```

**应该看到**：`deploy_to_tencent_cloud.sh`

### 步骤3：如果脚本不存在，手动创建

```bash
cd /opt/beatsync && \
sudo mkdir -p scripts/deployment && \
sudo wget -O scripts/deployment/deploy_to_tencent_cloud.sh https://raw.githubusercontent.com/scarlettyellow/BeatSync/main/scripts/deployment/deploy_to_tencent_cloud.sh && \
sudo chmod +x scripts/deployment/deploy_to_tencent_cloud.sh && \
sudo bash scripts/deployment/deploy_to_tencent_cloud.sh
```

### 步骤4：如果步骤3失败，直接执行部署

使用解决方案2中的完整命令。

---

## 解决方案4：使用完整的一键部署命令

**直接复制以下完整命令**（包含所有部署步骤）：

```bash
sudo apt update && sudo apt upgrade -y && \
sudo apt install -y git curl wget vim build-essential python3-dev libsndfile1 libsndfile1-dev ffmpeg python3-pip && \
sudo mkdir -p /opt/beatsync && \
cd /opt && \
sudo rm -rf beatsync && \
sudo git clone https://github.com/scarlettyellow/BeatSync.git beatsync && \
sudo chown -R ubuntu:ubuntu /opt/beatsync && \
cd /opt/beatsync && \
pip3 install --upgrade pip && \
cd web_service/backend && \
pip3 install -r requirements.txt && \
cd /opt/beatsync && \
sudo mkdir -p web_uploads web_outputs logs outputs/web_uploads outputs/web_outputs && \
sudo chmod 755 web_uploads web_outputs logs outputs/web_uploads outputs/web_outputs && \
sudo bash -c 'cat > /etc/systemd/system/beatsync.service << "EOFSERVICE"
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
EOFSERVICE
' && \
sudo systemctl daemon-reload && \
sudo systemctl enable beatsync && \
sudo systemctl start beatsync && \
sleep 3 && \
sudo systemctl status beatsync | head -15 && \
echo "✅ 部署完成！服务地址: http://1.12.239.225:8000"
```

---

## 验证部署

### 检查服务状态

```bash
sudo systemctl status beatsync
```

**应该显示**：`active (running)`

### 测试健康检查

在浏览器中访问：
- http://1.12.239.225:8000/api/health

**应该返回**：`{"status":"healthy","timestamp":"..."}`

---

## 常见问题

### 问题1：Git克隆失败

**解决**：
```bash
# 检查网络连接
ping github.com

# 如果无法访问GitHub，使用镜像或代理
```

### 问题2：pip安装失败

**解决**：
```bash
# 使用国内镜像
pip3 install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 问题3：FFmpeg未安装

**解决**：
```bash
# 手动安装
sudo apt install -y ffmpeg
ffmpeg -version
```

---

## 推荐执行顺序

1. **先执行解决方案1的步骤1**：验证克隆是否成功
2. **如果成功，执行步骤2**：运行部署脚本
3. **如果失败，执行解决方案4**：使用完整的一键部署命令

---

**最后更新**：2025-12-01












