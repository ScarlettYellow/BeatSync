# 健壮的部署方案（忽略非关键错误）

> **问题**：kdump-tools等非关键包安装失败导致整个部署中断

---

## 问题分析

**错误信息**：
```
Errors were encountered while processing: kdump-tools
```

**原因**：
- kdump-tools是系统调试工具，不是必需的
- 安装失败不影响BeatSync服务运行
- 但命令链使用了`&&`，导致后续步骤未执行

---

## 解决方案：分步执行（推荐）

### 步骤1：修复dpkg并更新系统

```bash
sudo dpkg --configure -a || true && sudo apt update && sudo apt upgrade -y || true
```

**`|| true`** 确保即使有错误也继续执行

### 步骤2：安装必要依赖（忽略非关键错误）

```bash
sudo apt install -y git curl wget vim build-essential python3-dev libsndfile1 libsndfile1-dev ffmpeg python3-pip || true
```

### 步骤3：克隆项目

```bash
sudo mkdir -p /opt/beatsync && cd /opt && sudo rm -rf beatsync && sudo git clone https://github.com/scarlettyellow/BeatSync.git beatsync && sudo chown -R ubuntu:ubuntu /opt/beatsync
```

### 步骤4：安装Python依赖

```bash
cd /opt/beatsync && pip3 install --upgrade pip && cd web_service/backend && pip3 install -r requirements.txt
```

### 步骤5：创建目录和配置服务

```bash
cd /opt/beatsync && sudo mkdir -p web_uploads web_outputs logs outputs/web_uploads outputs/web_outputs && sudo chmod 755 web_uploads web_outputs logs outputs/web_uploads outputs/web_outputs && sudo bash -c 'cat > /etc/systemd/system/beatsync.service << "EOFSERVICE"
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
'
```

### 步骤6：启动服务

```bash
sudo systemctl daemon-reload && sudo systemctl enable beatsync && sudo systemctl start beatsync && sleep 3 && sudo systemctl status beatsync | head -15
```

---

## 一键部署（使用|| true忽略错误）

**直接复制以下命令**（会忽略非关键错误）：

```bash
sudo dpkg --configure -a || true && sudo apt update && sudo apt upgrade -y || true && sudo apt install -y git curl wget vim build-essential python3-dev libsndfile1 libsndfile1-dev ffmpeg python3-pip || true && sudo mkdir -p /opt/beatsync && cd /opt && sudo rm -rf beatsync && sudo git clone https://github.com/scarlettyellow/BeatSync.git beatsync && sudo chown -R ubuntu:ubuntu /opt/beatsync && cd /opt/beatsync && pip3 install --upgrade pip && cd web_service/backend && pip3 install -r requirements.txt && cd /opt/beatsync && sudo mkdir -p web_uploads web_outputs logs outputs/web_uploads outputs/web_outputs && sudo chmod 755 web_uploads web_outputs logs outputs/web_uploads outputs/web_outputs && sudo bash -c 'cat > /etc/systemd/system/beatsync.service << "EOFSERVICE"
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
' && sudo systemctl daemon-reload && sudo systemctl enable beatsync && sudo systemctl start beatsync && sleep 3 && sudo systemctl status beatsync | head -15 && echo "✅ 部署完成！服务地址: http://1.12.239.225:8000"
```

---

## 更简单的方案：跳过apt upgrade

如果`apt upgrade`导致问题，可以跳过它：

```bash
sudo dpkg --configure -a || true && sudo apt update && sudo apt install -y git curl wget vim build-essential python3-dev libsndfile1 libsndfile1-dev ffmpeg python3-pip || true && sudo mkdir -p /opt/beatsync && cd /opt && sudo rm -rf beatsync && sudo git clone https://github.com/scarlettyellow/BeatSync.git beatsync && sudo chown -R ubuntu:ubuntu /opt/beatsync && cd /opt/beatsync && pip3 install --upgrade pip && cd web_service/backend && pip3 install -r requirements.txt && cd /opt/beatsync && sudo mkdir -p web_uploads web_outputs logs outputs/web_uploads outputs/web_outputs && sudo chmod 755 web_uploads web_outputs logs outputs/web_uploads outputs/web_outputs && sudo bash -c 'cat > /etc/systemd/system/beatsync.service << "EOFSERVICE"
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
' && sudo systemctl daemon-reload && sudo systemctl enable beatsync && sudo systemctl start beatsync && sleep 3 && sudo systemctl status beatsync | head -15 && echo "✅ 部署完成！服务地址: http://1.12.239.225:8000"
```

---

## 验证部署

### 检查服务状态

```bash
sudo systemctl status beatsync
```

### 测试健康检查

在浏览器中访问：
- http://1.12.239.225:8000/api/health

---

**最后更新**：2025-12-01



