# 修复 CORS 环境变量配置

> **问题**：重启后端服务后，CORS 仍显示 `access-control-allow-origin: *`  
> **原因**：环境变量 `ALLOWED_ORIGINS` 未正确加载到 systemd 服务中

---

## 问题分析

后端代码使用 `os.getenv("ALLOWED_ORIGINS", "*")` 读取环境变量，但：
1. 后端代码可能没有自动加载 `.env` 文件
2. systemd 服务可能没有读取 `.env` 文件
3. 需要在 systemd 服务文件中显式设置环境变量

---

## 解决方案

### 方法 1：在 systemd 服务文件中设置环境变量（推荐）

```bash
# 1. 查看当前服务文件
sudo systemctl cat beatsync.service

# 2. 编辑服务文件
sudo systemctl edit beatsync.service
```

**如果 `systemctl edit` 失败**（非 TTY 环境），直接编辑文件：

```bash
# 找到服务文件位置
sudo systemctl cat beatsync.service | head -5

# 通常位置是：
# /etc/systemd/system/beatsync.service
# 或
# /lib/systemd/system/beatsync.service

# 编辑服务文件
sudo nano /etc/systemd/system/beatsync.service
```

**在 `[Service]` 部分添加环境变量**：

```ini
[Service]
# ... 其他配置 ...
Environment="ALLOWED_ORIGINS=https://beatsync.site,http://localhost:8000"
```

**完整示例**：

```ini
[Unit]
Description=BeatSync Web Service Backend
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/opt/beatsync/web_service/backend
ExecStart=/usr/bin/python3 -m uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10
Environment="ALLOWED_ORIGINS=https://beatsync.site,http://localhost:8000"

[Install]
WantedBy=multi-user.target
```

**重新加载并重启**：

```bash
# 重新加载 systemd 配置
sudo systemctl daemon-reload

# 重启服务
sudo systemctl restart beatsync.service

# 检查服务状态
sudo systemctl status beatsync.service
```

### 方法 2：使用 EnvironmentFile（如果服务文件支持）

如果服务文件支持 `EnvironmentFile`，可以指向 `.env` 文件：

```ini
[Service]
# ... 其他配置 ...
EnvironmentFile=/opt/beatsync/.env
```

**注意**：`.env` 文件格式需要是 `KEY=value`（不能有空格），例如：
```
ALLOWED_ORIGINS=https://beatsync.site,http://localhost:8000
```

### 方法 3：修改后端代码自动加载 .env 文件

如果后端代码没有加载 `.env` 文件，可以添加：

```python
# 在 main.py 开头添加
from dotenv import load_dotenv
import os

# 加载 .env 文件
load_dotenv('/opt/beatsync/.env')
# 或
load_dotenv()  # 自动查找 .env 文件

# 然后使用环境变量
allowed_origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")
```

**需要安装 python-dotenv**：

```bash
pip3 install python-dotenv
```

---

## 验证配置

### 1. 检查服务文件配置

```bash
# 查看服务文件内容
sudo systemctl cat beatsync.service

# 应该看到 Environment 或 EnvironmentFile 配置
```

### 2. 检查环境变量是否加载

```bash
# 查看服务运行时的环境变量
sudo systemctl show beatsync.service | grep ALLOWED_ORIGINS
```

### 3. 测试 CORS 配置

```bash
# 测试 CORS 响应头
curl -I -H "Origin: https://beatsync.site" https://beatsync.site/api/health
```

**预期输出**（如果配置正确）：
```
HTTP/2 200
...
access-control-allow-origin: https://beatsync.site
access-control-allow-credentials: true
```

---

## 如果仍然显示 `*`

### 检查 1：环境变量格式

确保 `.env` 文件中没有多余空格：

```bash
# 检查 .env 文件格式
cat /opt/beatsync/.env | grep ALLOWED_ORIGINS

# 应该是：
# ALLOWED_ORIGINS=https://beatsync.site,http://localhost:8000
# 不能有空格：
# ALLOWED_ORIGINS = https://beatsync.site, http://localhost:8000  # 错误
```

### 检查 2：后端代码逻辑

检查后端代码是否正确处理环境变量：

```bash
# 查看后端代码
cat /opt/beatsync/web_service/backend/main.py | grep -A 10 "ALLOWED_ORIGINS"
```

### 检查 3：服务日志

查看服务日志，看是否有错误：

```bash
# 查看服务日志
sudo journalctl -u beatsync.service -n 50

# 或实时查看
sudo journalctl -u beatsync.service -f
```

---

## 快速修复脚本

```bash
#!/bin/bash
# 快速修复 CORS 环境变量配置

SERVICE_FILE="/etc/systemd/system/beatsync.service"
ENV_VALUE="https://beatsync.site,http://localhost:8000"

echo "检查服务文件..."
if [ -f "$SERVICE_FILE" ]; then
    echo "✅ 找到服务文件: $SERVICE_FILE"
    
    # 检查是否已有 Environment 配置
    if grep -q "ALLOWED_ORIGINS" "$SERVICE_FILE"; then
        echo "⚠️  服务文件中已有 ALLOWED_ORIGINS 配置"
        echo "请手动编辑: sudo nano $SERVICE_FILE"
    else
        echo "添加环境变量配置..."
        # 在 [Service] 部分添加环境变量
        sudo sed -i '/\[Service\]/a Environment="ALLOWED_ORIGINS='"$ENV_VALUE"'"' "$SERVICE_FILE"
        echo "✅ 已添加环境变量配置"
        
        echo "重新加载 systemd..."
        sudo systemctl daemon-reload
        
        echo "重启服务..."
        sudo systemctl restart beatsync.service
        
        echo "✅ 配置完成"
    fi
else
    echo "❌ 未找到服务文件: $SERVICE_FILE"
    echo "请先找到服务文件位置: sudo systemctl cat beatsync.service"
fi
```

---

## 临时解决方案（如果无法修改服务文件）

如果无法修改 systemd 服务文件，可以：

1. **使用 `*` 暂时接受**（功能正常，但安全性较低）
2. **在 Nginx 层面限制 CORS**（在 Nginx 配置中添加 CORS 头）

---

**最后更新**：2025-12-16
