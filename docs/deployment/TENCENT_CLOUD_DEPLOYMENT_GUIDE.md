# 腾讯云轻量应用服务器部署指南

> **目的**：将BeatSync后端服务部署到腾讯云轻量应用服务器  
> **服务器信息**：
> - 地域：广州（广州六区）
> - 配置：2核2GB，40GB SSD，3Mbps带宽
> - 镜像：Ubuntu 22.04 LTS
> - IP地址：1.12.239.225
> - 实例ID：lhins-9bmty95b

---

## 一、部署前准备

### 1.1 服务器信息确认

- ✅ **服务器已创建**：Ubuntu 22.04 LTS
- ✅ **状态**：运行中
- ✅ **IP地址**：1.12.239.225
- ✅ **地域**：广州

### 1.2 本地准备

**需要准备的文件**：
1. 整个BeatSync项目（包含所有代码）
2. 部署脚本（可选，但推荐）

**部署方式**：
- 方式1：使用Git（推荐，如果项目在GitHub）
- 方式2：使用SCP直接上传
- 方式3：使用rsync同步

---

## 二、连接服务器

### 2.1 获取登录密码

1. 在腾讯云控制台，点击"重置密码"
2. 设置新密码（记住这个密码）
3. 或者使用SSH密钥（如果已配置）

### 2.2 SSH连接

**使用密码登录**：
```bash
ssh root@1.12.239.225
# 或
ssh ubuntu@1.12.239.225
```

**使用密钥登录**（如果已配置）：
```bash
ssh -i ~/.ssh/your_key.pem root@1.12.239.225
```

**注意**：腾讯云轻量应用服务器默认用户可能是 `root` 或 `ubuntu`，根据实际情况选择。

---

## 三、服务器环境配置

### 3.1 更新系统

```bash
# 更新系统包
sudo apt update && sudo apt upgrade -y

# 安装基础工具
sudo apt install -y git curl wget vim
```

### 3.2 安装Python和pip

```bash
# 检查Python版本（Ubuntu 22.04默认Python 3.10）
python3 --version

# 安装pip（如果未安装）
sudo apt install -y python3-pip

# 升级pip
pip3 install --upgrade pip
```

### 3.3 安装FFmpeg（关键！）

```bash
# 安装FFmpeg
sudo apt install -y ffmpeg

# 验证安装
ffmpeg -version
```

**预期输出**：应该显示FFmpeg版本信息

### 3.4 安装系统依赖

```bash
# 安装编译工具（用于编译某些Python包）
sudo apt install -y build-essential python3-dev

# 安装音频处理库的系统依赖
sudo apt install -y libsndfile1 libsndfile1-dev
```

---

## 四、部署项目代码

### 方式1：使用Git（推荐）

**如果项目在GitHub上**：

```bash
# 创建项目目录
cd /opt
sudo mkdir -p beatsync
sudo chown $USER:$USER beatsync
cd beatsync

# 克隆项目（替换为你的GitHub仓库地址）
git clone https://github.com/scarlettyellow/BeatSync.git .

# 或如果仓库是私有的，使用SSH
# git clone git@github.com:scarlettyellow/BeatSync.git .
```

### 方式2：使用SCP上传

**从本地机器上传**：

```bash
# 在本地机器上执行（在BeatSync项目根目录）
scp -r . root@1.12.239.225:/opt/beatsync

# 或使用rsync（更高效）
rsync -avz --exclude '.git' --exclude '__pycache__' \
  --exclude '*.pyc' --exclude '.beatsync_cache' \
  . root@1.12.239.225:/opt/beatsync
```

### 方式3：使用压缩包

```bash
# 在本地机器上
cd /Users/scarlett/Projects/BeatSync
tar -czf beatsync.tar.gz --exclude='.git' --exclude='__pycache__' \
  --exclude='*.pyc' --exclude='.beatsync_cache' .

# 上传到服务器
scp beatsync.tar.gz root@1.12.239.225:/opt/

# 在服务器上解压
ssh root@1.12.239.225
cd /opt
tar -xzf beatsync.tar.gz -C beatsync
rm beatsync.tar.gz
```

---

## 五、安装Python依赖

### 5.1 进入项目目录

```bash
cd /opt/beatsync/web_service/backend
```

### 5.2 安装依赖

```bash
# 安装Python依赖
pip3 install -r requirements.txt

# 如果遇到权限问题，使用--user
# pip3 install --user -r requirements.txt
```

**注意**：安装可能需要几分钟，特别是numpy、opencv-python等大型包。

### 5.3 验证安装

```bash
# 检查关键包是否安装成功
python3 -c "import fastapi; import uvicorn; import numpy; import librosa; print('所有依赖安装成功！')"
```

---

## 六、配置服务

### 6.1 创建必要的目录

```bash
# 在项目根目录
cd /opt/beatsync

# 创建上传目录
mkdir -p web_uploads
chmod 755 web_uploads

# 创建输出目录
mkdir -p web_outputs
chmod 755 web_outputs

# 创建日志目录
mkdir -p logs
chmod 755 logs
```

### 6.2 配置环境变量（可选）

```bash
# 创建环境变量文件
cd /opt/beatsync/web_service/backend
cat > .env << EOF
# 允许的前端域名（生产环境建议限制）
ALLOWED_ORIGINS=https://scarlettyellow.github.io,http://localhost:8080

# 上传目录
UPLOAD_DIR=/opt/beatsync/web_uploads

# 输出目录
OUTPUT_DIR=/opt/beatsync/web_outputs
EOF
```

---

## 七、创建systemd服务（推荐）

### 7.1 创建服务文件

```bash
sudo vim /etc/systemd/system/beatsync.service
```

**服务文件内容**：

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

### 7.3 查看日志

```bash
# 查看服务日志
sudo journalctl -u beatsync -f

# 或查看最近100行
sudo journalctl -u beatsync -n 100
```

---

## 八、配置防火墙

### 8.1 腾讯云控制台配置

1. 在腾讯云控制台，进入"防火墙"标签
2. 添加规则：
   - **端口**：8000
   - **协议**：TCP
   - **来源**：0.0.0.0/0（允许所有IP，或限制为特定IP）
   - **动作**：允许

### 8.2 服务器本地防火墙（如果启用）

```bash
# 如果使用ufw
sudo ufw allow 8000/tcp
sudo ufw status

# 如果使用firewalld
sudo firewall-cmd --permanent --add-port=8000/tcp
sudo firewall-cmd --reload
```

---

## 九、测试服务

### 9.1 本地测试

```bash
# 在服务器上测试
curl http://localhost:8000/api/health

# 预期输出：{"status":"healthy","timestamp":"..."}
```

### 9.2 外部测试

```bash
# 从本地机器测试
curl http://1.12.239.225:8000/api/health

# 预期输出：{"status":"healthy","timestamp":"..."}
```

### 9.3 浏览器测试

在浏览器中访问：
- **健康检查**：http://1.12.239.225:8000/api/health
- **API文档**：http://1.12.239.225:8000/docs

---

## 十、更新前端配置

### 10.1 更新前端API地址

**需要修改的文件**：`web_service/frontend/script.js`

**修改内容**：

```javascript
// 找到API_BASE_URL的定义，添加腾讯云服务器地址
const API_BASE_URL = (() => {
  const hostname = window.location.hostname;
  
  if (hostname === 'localhost' || hostname === '127.0.0.1') {
    return 'http://localhost:8000';
  } else if (hostname === 'scarlettyellow.github.io') {
    // 生产环境：使用腾讯云服务器
    return 'http://1.12.239.225:8000';
  } else {
    // 默认使用腾讯云服务器
    return 'http://1.12.239.225:8000';
  }
})();
```

### 10.2 部署前端更新

```bash
# 在本地项目目录
cd /Users/scarlett/Projects/BeatSync

# 提交更改
git add web_service/frontend/script.js
git commit -m "feat: 更新前端API地址为腾讯云服务器"
git push origin main
```

**注意**：GitHub Pages会自动部署更新，通常几分钟内生效。

---

## 十一、性能优化（针对2核2GB配置）

### 11.1 启用并行处理

确保在处理时使用并行模式：

```python
# 在beatsync_parallel_processor.py中
parallel = True  # 启用并行模式
```

### 11.2 配置swap（如果内存不足）

```bash
# 创建2GB swap文件
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# 永久启用
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

### 11.3 优化FFmpeg参数

在代码中使用2线程（2核CPU）：

```python
# 在FFmpeg命令中使用
--threads 2
```

---

## 十二、监控和维护

### 12.1 查看服务状态

```bash
# 查看服务状态
sudo systemctl status beatsync

# 查看服务日志
sudo journalctl -u beatsync -f
```

### 12.2 重启服务

```bash
# 重启服务
sudo systemctl restart beatsync

# 停止服务
sudo systemctl stop beatsync

# 启动服务
sudo systemctl start beatsync
```

### 12.3 查看资源使用

```bash
# 安装htop（如果未安装）
sudo apt install -y htop

# 查看CPU和内存使用
htop

# 或使用top
top

# 查看内存使用
free -h

# 查看磁盘使用
df -h
```

---

## 十三、常见问题排查

### 13.1 服务无法启动

**检查**：
```bash
# 查看服务状态
sudo systemctl status beatsync

# 查看详细日志
sudo journalctl -u beatsync -n 50
```

**常见原因**：
- Python依赖未安装
- 端口被占用
- 文件权限问题

### 13.2 无法访问服务

**检查**：
```bash
# 检查服务是否运行
sudo systemctl status beatsync

# 检查端口是否监听
sudo netstat -tlnp | grep 8000

# 检查防火墙
sudo ufw status
```

**常见原因**：
- 防火墙未开放端口
- 服务未启动
- 腾讯云防火墙规则未配置

### 13.3 处理失败

**检查**：
```bash
# 查看服务日志
sudo journalctl -u beatsync -f

# 检查FFmpeg是否安装
ffmpeg -version

# 检查磁盘空间
df -h
```

**常见原因**：
- FFmpeg未安装
- 磁盘空间不足
- 内存不足（触发swap）

---

## 十四、快速部署脚本

### 14.1 创建部署脚本

在服务器上创建 `/opt/beatsync/deploy.sh`：

```bash
#!/bin/bash
# BeatSync快速部署脚本

set -e

echo "开始部署BeatSync服务..."

# 1. 更新系统
echo "更新系统..."
sudo apt update && sudo apt upgrade -y

# 2. 安装基础工具
echo "安装基础工具..."
sudo apt install -y git curl wget vim build-essential python3-dev

# 3. 安装FFmpeg
echo "安装FFmpeg..."
sudo apt install -y ffmpeg

# 4. 安装Python依赖
echo "安装Python依赖..."
cd /opt/beatsync/web_service/backend
pip3 install -r requirements.txt

# 5. 创建目录
echo "创建必要目录..."
cd /opt/beatsync
mkdir -p web_uploads web_outputs logs
chmod 755 web_uploads web_outputs logs

# 6. 重启服务
echo "重启服务..."
sudo systemctl restart beatsync

echo "部署完成！"
echo "服务地址：http://1.12.239.225:8000"
```

**使用**：
```bash
chmod +x /opt/beatsync/deploy.sh
sudo /opt/beatsync/deploy.sh
```

---

## 十五、部署检查清单

### ✅ 部署前
- [ ] 服务器已创建并运行
- [ ] 已获取服务器IP和登录信息
- [ ] 本地项目代码已准备好

### ✅ 服务器配置
- [ ] 系统已更新
- [ ] Python 3.10已安装
- [ ] FFmpeg已安装并验证
- [ ] 系统依赖已安装

### ✅ 项目部署
- [ ] 项目代码已上传到服务器
- [ ] Python依赖已安装
- [ ] 必要目录已创建
- [ ] 文件权限已配置

### ✅ 服务配置
- [ ] systemd服务已创建
- [ ] 服务已启动并运行
- [ ] 服务已设置为开机自启

### ✅ 网络配置
- [ ] 腾讯云防火墙已开放8000端口
- [ ] 服务器本地防火墙已配置（如需要）

### ✅ 测试验证
- [ ] 本地健康检查通过
- [ ] 外部健康检查通过
- [ ] API文档可访问
- [ ] 前端已更新API地址

---

## 十六、总结

### 16.1 部署完成标志

✅ **服务正常运行**：
- `sudo systemctl status beatsync` 显示 `active (running)`
- `curl http://1.12.239.225:8000/api/health` 返回健康状态

✅ **前端可访问**：
- 前端页面可以正常上传和处理视频
- 处理时间相比Render大幅降低（预期2-4分钟）

### 16.2 下一步

1. **性能测试**：使用测试视频验证处理时间
2. **监控资源**：观察CPU和内存使用情况
3. **优化配置**：根据测试结果调整配置
4. **考虑升级**：如果2GB内存不够，考虑升级到4GB

---

**最后更新**：2025-11-27  
**适用场景**：腾讯云轻量应用服务器部署












