# 修复503错误（API文档无法打开）

> **错误**：健康检查显示healthy，但访问 `/docs` 返回 HTTP ERROR 503

---

## 问题分析

**错误现象**：
- ✅ 健康检查 `http://124.221.58.149:8000/api/health` 返回 `{"status":"healthy"}`
- ❌ 访问 `http://124.221.58.149:8000/docs` 返回 HTTP ERROR 503

**可能原因**：
1. 服务虽然运行，但可能有问题（部分端点无法访问）
2. FastAPI应用可能没有正确启动
3. 服务可能正在重启或崩溃
4. 端口8000可能被其他进程占用
5. 防火墙或网络问题

---

## 诊断步骤

### 步骤1：检查服务状态

```bash
sudo systemctl status beatsync
```

**预期输出**：显示 `active (running)`

**如果服务未运行，启动服务**：
```bash
sudo systemctl start beatsync
sudo systemctl enable beatsync
```

---

### 步骤2：检查服务日志

```bash
sudo journalctl -u beatsync -n 50 --no-pager
```

**查看是否有错误信息**，特别是：
- 启动错误
- 导入错误
- 端口占用错误

---

### 步骤3：检查端口是否被占用

```bash
sudo netstat -tlnp | grep 8000
```

**预期输出**：应该显示Python进程监听8000端口

**如果端口被其他进程占用**：
```bash
# 查看占用端口的进程
sudo lsof -i :8000

# 如果需要，停止占用端口的进程
sudo kill <PID>
```

---

### 步骤4：测试本地访问

**在服务器上直接测试**：

```bash
# 测试健康检查
curl http://localhost:8000/api/health

# 测试API文档
curl http://localhost:8000/docs
```

**如果本地也无法访问，说明服务有问题**

---

### 步骤5：检查FastAPI应用是否正确启动

```bash
# 查看服务进程
ps aux | grep uvicorn

# 应该看到类似：
# root     12345  0.1  2.3  /usr/bin/python3 -m uvicorn main:app --host 0.0.0.0 --port 8000
```

**如果进程不存在，服务可能崩溃了**

---

### 步骤6：检查Python依赖是否完整

```bash
cd /opt/beatsync/web_service/backend
python3 -c "import fastapi; import uvicorn; print('✅ 依赖正常')"
```

**如果导入失败，需要重新安装依赖**：
```bash
pip3 install -r requirements.txt
```

---

## 修复方案

### 方案1：重启服务

```bash
sudo systemctl restart beatsync
sleep 3
sudo systemctl status beatsync
```

**然后再次测试**：
```bash
curl http://localhost:8000/api/health
curl http://localhost:8000/docs
```

---

### 方案2：检查并修复服务配置

**检查服务文件**：
```bash
cat /etc/systemd/system/beatsync.service
```

**确保配置正确**：
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

**如果配置不正确，重新创建**：
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

### 方案3：手动启动服务测试

**停止systemd服务**：
```bash
sudo systemctl stop beatsync
```

**手动启动服务**：
```bash
cd /opt/beatsync/web_service/backend
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000
```

**在另一个终端测试**：
```bash
curl http://localhost:8000/api/health
curl http://localhost:8000/docs
```

**如果手动启动可以访问，说明systemd配置有问题**

**按 `Ctrl+C` 停止手动启动的服务，然后修复systemd配置**

---

### 方案4：检查防火墙

**检查8000端口是否开放**：
```bash
sudo ufw status | grep 8000
```

**如果未开放，开放端口**：
```bash
sudo ufw allow 8000/tcp
```

**或者在腾讯云控制台检查防火墙规则**

---

### 方案5：重新安装Python依赖

```bash
cd /opt/beatsync/web_service/backend
pip3 install --upgrade -r requirements.txt
sudo systemctl restart beatsync
```

---

## 快速修复命令（一键执行）

### 如果服务状态异常，执行：

```bash
# 停止服务
sudo systemctl stop beatsync

# 检查并修复服务配置
sudo tee /etc/systemd/system/beatsync.service > /dev/null << 'EOF'
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

# 重新加载并启动
sudo systemctl daemon-reload
sudo systemctl restart beatsync

# 等待3秒
sleep 3

# 检查状态
sudo systemctl status beatsync

# 测试本地访问
curl http://localhost:8000/api/health
curl -I http://localhost:8000/docs
```

---

## 验证修复

### 步骤1：检查服务状态

```bash
sudo systemctl status beatsync
```

**预期输出**：`active (running)`

---

### 步骤2：测试本地访问

```bash
# 健康检查
curl http://localhost:8000/api/health

# API文档（应该返回HTML）
curl -I http://localhost:8000/docs
```

**预期输出**：
- 健康检查：`{"status":"healthy"}`
- API文档：`HTTP/1.1 200 OK`

---

### 步骤3：测试外部访问

**在浏览器中访问**：
- `http://124.221.58.149:8000/api/health`
- `http://124.221.58.149:8000/docs`

**或者使用curl**：
```bash
curl http://124.221.58.149:8000/api/health
curl -I http://124.221.58.149:8000/docs
```

---

## 常见问题

### Q1: 为什么健康检查可以访问，但 `/docs` 不行？

**A**: 
- 可能是FastAPI应用部分功能有问题
- 可能是服务正在重启
- 可能是路由配置问题

### Q2: 如何查看详细的错误信息？

**A**: 
```bash
# 查看服务日志
sudo journalctl -u beatsync -f

# 查看系统日志
sudo dmesg | tail -20
```

### Q3: 服务一直重启怎么办？

**A**: 
1. 查看日志找出崩溃原因
2. 检查Python依赖是否完整
3. 检查代码是否有语法错误
4. 检查端口是否被占用

---

## 如果问题仍然存在

### 完整诊断流程

```bash
# 1. 检查服务状态
sudo systemctl status beatsync

# 2. 查看服务日志
sudo journalctl -u beatsync -n 100 --no-pager

# 3. 检查端口
sudo netstat -tlnp | grep 8000

# 4. 检查进程
ps aux | grep uvicorn

# 5. 测试本地访问
curl -v http://localhost:8000/api/health
curl -v http://localhost:8000/docs

# 6. 检查防火墙
sudo ufw status
```

**将以上命令的输出结果保存，用于进一步诊断**

---

**最后更新**：2025-12-02

