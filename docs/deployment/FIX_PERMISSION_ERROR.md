# 修复权限错误（Permission denied）

> **错误**：`PermissionError: [Errno 13] Permission denied: '/opt/beatsync/outputs/logs/performance_20251202.log'`

---

## 问题分析

**错误原因**：
- `performance_logger.py` 尝试写入日志文件到 `/opt/beatsync/outputs/logs/`
- 目录可能不存在或权限不足
- 当前用户（ubuntu）没有写入权限

**错误位置**：
- `web_service/backend/performance_logger.py` 第17-26行
- 尝试创建日志目录和文件时失败

---

## 快速修复方案

### 方案1：修复目录权限（推荐）

**在服务器上执行**：

```bash
# 创建日志目录
sudo mkdir -p /opt/beatsync/outputs/logs

# 设置目录权限（允许所有用户写入）
sudo chmod 777 /opt/beatsync/outputs/logs

# 或者设置为ubuntu用户所有
sudo chown -R ubuntu:ubuntu /opt/beatsync/outputs

# 验证权限
ls -ld /opt/beatsync/outputs/logs
```

**然后重启服务**：
```bash
sudo systemctl restart beatsync
```

---

### 方案2：修复整个项目目录权限

**如果方案1不行，修复整个项目目录**：

```bash
# 设置项目目录所有者为ubuntu
sudo chown -R ubuntu:ubuntu /opt/beatsync

# 设置目录权限
sudo chmod -R 755 /opt/beatsync

# 确保日志目录可写
sudo chmod 777 /opt/beatsync/outputs/logs
```

**然后重启服务**：
```bash
sudo systemctl restart beatsync
```

---

### 方案3：修改systemd服务配置（使用ubuntu用户）

**如果服务以root用户运行，但目录属于ubuntu，可以改为使用ubuntu用户运行**：

```bash
# 停止服务
sudo systemctl stop beatsync

# 修改服务配置，使用ubuntu用户
sudo tee /etc/systemd/system/beatsync.service > /dev/null << 'EOF'
[Unit]
Description=BeatSync Web Service Backend
After=network.target

[Service]
Type=simple
User=ubuntu
Group=ubuntu
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

# 重新加载并启动
sudo systemctl daemon-reload
sudo systemctl restart beatsync

# 检查状态
sudo systemctl status beatsync
```

**注意**：如果使用ubuntu用户，需要确保：
- ubuntu用户可以访问所有必要的文件和目录
- 端口8000可以被非root用户绑定（通常可以）

---

## 一键修复命令

**执行以下命令修复权限问题**：

```bash
# 创建日志目录
sudo mkdir -p /opt/beatsync/outputs/logs

# 设置目录权限
sudo chmod 777 /opt/beatsync/outputs/logs

# 或者设置为ubuntu用户所有
sudo chown -R ubuntu:ubuntu /opt/beatsync/outputs

# 验证权限
ls -ld /opt/beatsync/outputs/logs

# 重启服务
sudo systemctl restart beatsync

# 等待3秒
sleep 3

# 检查服务状态
sudo systemctl status beatsync

# 测试访问
curl http://localhost:8000/api/health
```

---

## 验证修复

### 步骤1：检查目录权限

```bash
ls -ld /opt/beatsync/outputs/logs
```

**预期输出**：应该显示目录存在且可写

---

### 步骤2：测试手动启动

```bash
# 停止systemd服务
sudo systemctl stop beatsync

# 手动启动
cd /opt/beatsync/web_service/backend
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000
```

**应该不再出现权限错误**

---

### 步骤3：检查服务状态

```bash
sudo systemctl status beatsync
```

**预期输出**：`active (running)`

---

### 步骤4：测试访问

```bash
# 健康检查
curl http://localhost:8000/api/health

# API文档
curl -I http://localhost:8000/docs
```

---

## 如果问题仍然存在

### 检查所有相关目录权限

```bash
# 检查项目目录
ls -la /opt/beatsync/

# 检查outputs目录
ls -la /opt/beatsync/outputs/

# 检查logs目录
ls -la /opt/beatsync/outputs/logs/
```

### 检查当前用户

```bash
# 查看当前用户
whoami

# 查看服务运行用户
sudo systemctl show beatsync | grep User
```

### 临时禁用性能日志（如果不需要）

**如果不需要性能日志，可以临时禁用**：

修改 `web_service/backend/main.py`，注释掉性能日志导入：

```python
# 导入性能日志记录器
# try:
#     from performance_logger import create_logger
#     PERFORMANCE_LOGGING_ENABLED = True
# except ImportError:
#     PERFORMANCE_LOGGING_ENABLED = False
#     print("WARNING: 性能日志记录器未找到，性能日志功能已禁用")

PERFORMANCE_LOGGING_ENABLED = False
```

**但这不是推荐方案，应该修复权限问题**

---

## 代码修复（已更新）

**已更新 `performance_logger.py`，使其在权限错误时优雅降级**：
- 如果无法写入日志文件，只使用控制台输出
- 不会因为权限错误导致服务无法启动

**需要更新代码**：
```bash
cd /opt/beatsync
git pull origin main
```

**或者手动应用修复**（见上方代码修改）

---

**最后更新**：2025-12-02

