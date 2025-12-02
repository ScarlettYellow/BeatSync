# 修复部署脚本超时问题

> **错误**：执行部署脚本时超时（超过60秒）

---

## 问题分析

**错误原因**：
- 腾讯云"执行命令"功能默认超时时间为60秒
- 部署脚本需要：
  - 更新系统包（步骤1）
  - 安装基础工具（步骤2）
  - 安装FFmpeg（步骤4）- **最耗时**：需要下载138MB，安装153个包
  - 安装Python依赖（步骤6）- 可能需要下载大量包
- 总执行时间可能超过60秒，导致超时

**当前状态**：
- 脚本已执行到步骤4（安装FFmpeg）
- 正在下载FFmpeg依赖包时被超时中断
- 前面的步骤（1-3）应该已经完成

---

## 解决方案

### 方案1：使用SSH直接执行（推荐）

**优点**：不受超时限制，可以实时查看进度

**步骤**：

1. **使用SSH登录服务器**
   ```bash
   ssh ubuntu@124.221.58.149
   ```

2. **进入项目目录**
   ```bash
   cd /opt/beatsync
   ```

3. **使用nohup在后台执行部署脚本**
   ```bash
   sudo nohup bash scripts/deployment/deploy_to_tencent_cloud.sh > /tmp/deploy.log 2>&1 &
   ```

4. **查看执行进度**
   ```bash
   tail -f /tmp/deploy.log
   ```

5. **检查脚本是否还在运行**
   ```bash
   ps aux | grep deploy_to_tencent_cloud
   ```

---

### 方案2：分步骤执行（适合"执行命令"功能）

**将部署脚本拆分成多个小步骤，每个步骤单独执行**

#### 步骤8.1：检查FFmpeg是否已安装

```bash
ffmpeg -version
```

**如果已安装，跳过步骤8.2，直接执行步骤8.3**

---

#### 步骤8.2：安装FFmpeg（单独执行）

```bash
sudo apt install -y ffmpeg
```

**预期输出**：下载并安装FFmpeg及其依赖包（可能需要2-5分钟）

**验证**：
```bash
ffmpeg -version | head -1
```

---

#### 步骤8.3：进入项目目录

```bash
cd /opt/beatsync
```

**验证**：
```bash
pwd
# 应该显示：/opt/beatsync
```

---

#### 步骤8.4：安装Python依赖

```bash
cd /opt/beatsync/web_service/backend
pip3 install -r requirements.txt
```

**预期输出**：下载并安装Python包（可能需要1-3分钟）

**验证**：
```bash
pip3 list | grep -E "(fastapi|uvicorn|librosa)"
```

---

#### 步骤8.5：创建必要目录

```bash
cd /opt/beatsync
sudo mkdir -p web_uploads web_outputs logs outputs/web_uploads outputs/web_outputs
sudo chmod 755 web_uploads web_outputs logs outputs/web_uploads outputs/web_outputs
```

**验证**：
```bash
ls -la /opt/beatsync | grep -E "(web_uploads|web_outputs|logs)"
```

---

#### 步骤8.6：创建systemd服务

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
```

**验证**：
```bash
cat /etc/systemd/system/beatsync.service
```

---

#### 步骤8.7：启用并启动服务

```bash
sudo systemctl daemon-reload
sudo systemctl enable beatsync
sudo systemctl restart beatsync
```

**验证**：
```bash
sudo systemctl status beatsync
```

**预期输出**：显示服务状态为"active (running)"

---

#### 步骤8.8：检查服务状态

```bash
sleep 2
sudo systemctl is-active beatsync && echo "✅ 服务运行正常" || echo "❌ 服务启动失败"
```

**如果失败，查看日志**：
```bash
sudo journalctl -u beatsync -n 20
```

---

## 快速修复命令（SSH方式）

### 如果使用SSH登录，执行：

```bash
# 进入项目目录
cd /opt/beatsync

# 在后台执行部署脚本
sudo nohup bash scripts/deployment/deploy_to_tencent_cloud.sh > /tmp/deploy.log 2>&1 &

# 查看执行进度
tail -f /tmp/deploy.log
```

**按 `Ctrl+C` 退出日志查看，脚本会继续在后台运行**

---

## 快速修复命令（分步骤方式）

### 如果继续使用"执行命令"功能，按顺序执行：

#### 步骤1：检查FFmpeg
```bash
ffmpeg -version || sudo apt install -y ffmpeg
```

#### 步骤2：安装Python依赖
```bash
cd /opt/beatsync/web_service/backend && pip3 install -r requirements.txt
```

#### 步骤3：创建目录
```bash
cd /opt/beatsync && sudo mkdir -p web_uploads web_outputs logs outputs/web_uploads outputs/web_outputs && sudo chmod 755 web_uploads web_outputs logs outputs/web_uploads outputs/web_outputs
```

#### 步骤4：创建systemd服务
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
```

#### 步骤5：启动服务
```bash
sudo systemctl daemon-reload && sudo systemctl enable beatsync && sudo systemctl restart beatsync && sleep 2 && sudo systemctl status beatsync
```

---

## 验证部署是否成功

### 检查服务状态

```bash
sudo systemctl status beatsync
```

### 检查服务日志

```bash
sudo journalctl -u beatsync -n 20
```

### 测试健康检查

```bash
curl http://localhost:8000/api/health
```

**预期输出**：`{"status":"healthy"}`

### 测试API文档

在浏览器中访问：`http://124.221.58.149:8000/docs`

---

## 常见问题

### Q1: 如何知道脚本执行到哪里了？

**A**: 
- 如果使用SSH：`tail -f /tmp/deploy.log`
- 如果使用"执行命令"：查看执行结果输出

### Q2: FFmpeg安装需要多长时间？

**A**: 
- 通常需要2-5分钟
- 取决于网络速度和服务器性能

### Q3: Python依赖安装需要多长时间？

**A**: 
- 通常需要1-3分钟
- 取决于需要安装的包数量

### Q4: 如何确认部署是否成功？

**A**: 
1. 检查服务状态：`sudo systemctl status beatsync`
2. 测试健康检查：`curl http://localhost:8000/api/health`
3. 查看服务日志：`sudo journalctl -u beatsync -n 20`

---

## 推荐方案

**强烈推荐使用SSH方式执行部署脚本**，因为：
1. 不受超时限制
2. 可以实时查看进度
3. 可以随时中断和恢复
4. 更灵活，便于调试

---

**最后更新**：2025-12-02

