# 深度诊断503错误

> **问题**：快速修复命令已执行，但FastAPI文档页面仍无法访问

---

## 深度诊断步骤

### 步骤1：检查服务实际状态

```bash
# 检查服务状态
sudo systemctl status beatsync

# 检查服务是否真的在运行
sudo systemctl is-active beatsync

# 检查服务是否启用
sudo systemctl is-enabled beatsync
```

---

### 步骤2：查看完整服务日志

```bash
# 查看所有日志（不截断）
sudo journalctl -u beatsync --no-pager | tail -100

# 查看实时日志
sudo journalctl -u beatsync -f
```

**重点关注**：
- 启动错误
- 导入错误（ImportError）
- 端口占用错误
- Python语法错误

---

### 步骤3：检查端口占用情况

```bash
# 检查8000端口是否被占用
sudo lsof -i :8000

# 或者
sudo netstat -tlnp | grep 8000

# 检查是否有其他Python进程
ps aux | grep python | grep 8000
```

**如果端口被占用，需要停止占用进程**：
```bash
# 找到占用端口的进程ID
sudo lsof -i :8000

# 停止进程（替换<PID>为实际进程ID）
sudo kill <PID>
```

---

### 步骤4：测试Python应用能否正常导入

```bash
cd /opt/beatsync/web_service/backend

# 测试导入main模块
python3 -c "from main import app; print('✅ 导入成功')"
```

**如果导入失败，查看具体错误**：
```bash
python3 -c "from main import app"
```

---

### 步骤5：手动启动服务测试

**停止systemd服务**：
```bash
sudo systemctl stop beatsync
```

**确保端口没有被占用**：
```bash
sudo lsof -i :8000
# 如果有输出，说明端口被占用，需要先停止占用进程
```

**手动启动服务**：
```bash
cd /opt/beatsync/web_service/backend
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000
```

**在另一个终端测试**：
```bash
# 测试健康检查
curl -v http://localhost:8000/api/health

# 测试API文档
curl -v http://localhost:8000/docs
```

**观察手动启动时的输出**：
- 是否有错误信息？
- 是否显示 "Application startup complete"？
- 是否有导入错误？

---

### 步骤6：检查Python依赖

```bash
cd /opt/beatsync/web_service/backend

# 检查requirements.txt是否存在
ls -la requirements.txt

# 检查关键依赖是否安装
python3 -c "import fastapi; print('FastAPI版本:', fastapi.__version__)"
python3 -c "import uvicorn; print('Uvicorn版本:', uvicorn.__version__)"
python3 -c "import numpy; print('NumPy已安装')"
python3 -c "import librosa; print('Librosa已安装')"
```

**如果有依赖缺失，重新安装**：
```bash
pip3 install -r requirements.txt
```

---

### 步骤7：检查工作目录和文件权限

```bash
# 检查工作目录
ls -la /opt/beatsync/web_service/backend/

# 检查main.py是否存在
ls -la /opt/beatsync/web_service/backend/main.py

# 检查文件权限
stat /opt/beatsync/web_service/backend/main.py
```

---

### 步骤8：检查防火墙

```bash
# 检查UFW状态
sudo ufw status

# 检查8000端口是否开放
sudo ufw status | grep 8000

# 如果未开放，开放端口
sudo ufw allow 8000/tcp
```

**或者在腾讯云控制台检查防火墙规则**

---

### 步骤9：检查Nginx配置（如果有）

```bash
# 检查Nginx是否运行
sudo systemctl status nginx

# 如果Nginx运行，检查配置
sudo nginx -t

# 查看Nginx错误日志
sudo tail -f /var/log/nginx/error.log
```

**如果Nginx配置了反向代理，可能需要检查配置是否正确**

---

## 常见问题和解决方案

### 问题1：服务启动但立即崩溃

**症状**：`systemctl status` 显示服务不断重启

**解决方案**：
```bash
# 查看详细日志
sudo journalctl -u beatsync -n 100 --no-pager

# 检查是否有导入错误
cd /opt/beatsync/web_service/backend
python3 -c "from main import app"
```

---

### 问题2：端口被占用

**症状**：`lsof -i :8000` 显示端口被其他进程占用

**解决方案**：
```bash
# 找到占用端口的进程
sudo lsof -i :8000

# 停止占用进程
sudo kill <PID>

# 或者使用killall
sudo killall -9 python3

# 重新启动服务
sudo systemctl restart beatsync
```

---

### 问题3：Python依赖缺失

**症状**：日志显示 `ModuleNotFoundError` 或 `ImportError`

**解决方案**：
```bash
cd /opt/beatsync/web_service/backend
pip3 install --upgrade -r requirements.txt
sudo systemctl restart beatsync
```

---

### 问题4：工作目录错误

**症状**：日志显示 `FileNotFoundError` 或路径错误

**解决方案**：
```bash
# 检查systemd服务配置中的WorkingDirectory
cat /etc/systemd/system/beatsync.service | grep WorkingDirectory

# 确保路径正确
ls -la /opt/beatsync/web_service/backend/main.py
```

---

### 问题5：权限问题

**症状**：日志显示权限错误

**解决方案**：
```bash
# 检查文件权限
ls -la /opt/beatsync/web_service/backend/

# 如果需要，修复权限
sudo chown -R root:root /opt/beatsync
sudo chmod -R 755 /opt/beatsync
```

---

## 完整诊断脚本

**一键执行所有诊断步骤**：

```bash
#!/bin/bash
echo "=== 诊断BeatSync服务 ==="
echo ""

echo "1. 检查服务状态..."
sudo systemctl status beatsync | head -20
echo ""

echo "2. 检查端口占用..."
sudo lsof -i :8000 || echo "端口未被占用"
echo ""

echo "3. 检查进程..."
ps aux | grep uvicorn | grep -v grep || echo "未找到uvicorn进程"
echo ""

echo "4. 检查Python依赖..."
cd /opt/beatsync/web_service/backend
python3 -c "import fastapi; print('✅ FastAPI已安装')" 2>&1
python3 -c "import uvicorn; print('✅ Uvicorn已安装')" 2>&1
echo ""

echo "5. 测试导入main模块..."
python3 -c "from main import app; print('✅ main模块导入成功')" 2>&1
echo ""

echo "6. 检查工作目录..."
ls -la /opt/beatsync/web_service/backend/main.py
echo ""

echo "7. 查看最近50条日志..."
sudo journalctl -u beatsync -n 50 --no-pager | tail -30
echo ""

echo "8. 测试本地访问..."
curl -s http://localhost:8000/api/health || echo "❌ 本地访问失败"
echo ""

echo "=== 诊断完成 ==="
```

**保存为脚本并执行**：
```bash
# 保存脚本
cat > /tmp/diagnose_beatsync.sh << 'EOF'
#!/bin/bash
echo "=== 诊断BeatSync服务 ==="
echo ""
echo "1. 检查服务状态..."
sudo systemctl status beatsync | head -20
echo ""
echo "2. 检查端口占用..."
sudo lsof -i :8000 || echo "端口未被占用"
echo ""
echo "3. 检查进程..."
ps aux | grep uvicorn | grep -v grep || echo "未找到uvicorn进程"
echo ""
echo "4. 检查Python依赖..."
cd /opt/beatsync/web_service/backend
python3 -c "import fastapi; print('✅ FastAPI已安装')" 2>&1
python3 -c "import uvicorn; print('✅ Uvicorn已安装')" 2>&1
echo ""
echo "5. 测试导入main模块..."
python3 -c "from main import app; print('✅ main模块导入成功')" 2>&1
echo ""
echo "6. 检查工作目录..."
ls -la /opt/beatsync/web_service/backend/main.py
echo ""
echo "7. 查看最近50条日志..."
sudo journalctl -u beatsync -n 50 --no-pager | tail -30
echo ""
echo "8. 测试本地访问..."
curl -s http://localhost:8000/api/health || echo "❌ 本地访问失败"
echo ""
echo "=== 诊断完成 ==="
EOF

# 执行脚本
chmod +x /tmp/diagnose_beatsync.sh
bash /tmp/diagnose_beatsync.sh
```

---

## 如果手动启动可以访问

**如果手动启动服务可以访问，但systemd服务不行，可能是以下原因**：

### 1. 环境变量问题

**检查systemd服务配置中的Environment**：
```bash
cat /etc/systemd/system/beatsync.service | grep Environment
```

**可能需要添加更多环境变量**：
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
sudo systemctl restart beatsync
```

---

### 2. 工作目录问题

**确保WorkingDirectory正确**：
```bash
# 检查路径是否存在
ls -la /opt/beatsync/web_service/backend/main.py

# 如果不存在，检查实际路径
find /opt/beatsync -name main.py
```

---

### 3. Python路径问题

**检查Python可执行文件路径**：
```bash
which python3
# 应该输出：/usr/bin/python3

# 检查systemd配置中的路径
cat /etc/systemd/system/beatsync.service | grep ExecStart
```

---

## 收集诊断信息

**如果问题仍然存在，请收集以下信息**：

```bash
# 1. 服务状态
sudo systemctl status beatsync > /tmp/beatsync_status.txt

# 2. 完整日志
sudo journalctl -u beatsync --no-pager > /tmp/beatsync_logs.txt

# 3. 端口占用
sudo lsof -i :8000 > /tmp/port_8000.txt

# 4. 进程信息
ps aux | grep uvicorn > /tmp/uvicorn_process.txt

# 5. Python依赖
pip3 list > /tmp/python_packages.txt

# 6. 手动启动测试
cd /opt/beatsync/web_service/backend
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 > /tmp/manual_start.log 2>&1 &
sleep 5
curl -v http://localhost:8000/api/health > /tmp/health_test.txt 2>&1
curl -v http://localhost:8000/docs > /tmp/docs_test.txt 2>&1
sudo killall python3
```

**查看收集的信息**：
```bash
cat /tmp/beatsync_status.txt
cat /tmp/beatsync_logs.txt | tail -50
cat /tmp/port_8000.txt
cat /tmp/uvicorn_process.txt
cat /tmp/manual_start.log
cat /tmp/health_test.txt
cat /tmp/docs_test.txt
```

---

**最后更新**：2025-12-02

