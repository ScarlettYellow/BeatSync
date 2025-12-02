# 新服务器分步部署指南

> **新服务器信息**：
> - IPv4地址：124.221.58.149
> - 配置：4核4GB，40GB SSD，3Mbps带宽
> - 镜像：Ubuntu 22.04 LTS

---

## 一、部署前准备

### 1.1 确认服务器信息

- ✅ **服务器已创建**：Ubuntu 22.04 LTS
- ✅ **状态**：运行中
- ✅ **IP地址**：124.221.58.149
- ✅ **配置**：4核4GB（已升级）

### 1.2 选择执行方式

**方式1：SSH登录执行（推荐）**
- 在腾讯云控制台，点击"登录"按钮
- 选择"VNC登录"（在浏览器中直接登录）
- 或选择"密码/密钥登录"（使用SSH客户端）
- 默认用户名：`ubuntu`

**方式2：安装自动化助手客户端（可选）**
- 如果"执行命令"页面显示"未安装客户端"
- 可以点击"安装指引"安装客户端
- 或者直接使用SSH登录（更简单）

**推荐**：使用SSH登录执行命令，更直接、更灵活。

---

## 二、分步部署命令

### 步骤1：修复系统状态（如果需要）

**目的**：修复可能的dpkg状态问题

**如果遇到dpkg锁定错误，先处理锁定问题：**

```bash
# 检查是否有dpkg进程在运行
ps aux | grep -E 'dpkg|apt'

# 如果有进程在运行，等待完成或终止（见下方说明）
# 如果进程卡住，可以终止：
# sudo kill <PID>
# sleep 5
```

**然后执行修复：**

```bash
sudo dpkg --configure -a
```

**如果遇到锁定错误**，参考：`docs/deployment/FIX_DPKG_LOCK.md`

**预期输出**：无错误信息

---

### 步骤2：更新系统

**目的**：更新系统包列表和已安装的包

**步骤2.1：更新包列表**

```bash
sudo apt update
```

**等待完成后，继续：**

**步骤2.2：修复dpkg状态（如果遇到错误）**

如果执行 `apt upgrade` 时出现错误：
```
E: dpkg was interrupted, you must manually run 'sudo dpkg --configure -a' to correct the
```

先执行修复命令：

```bash
sudo dpkg --configure -a
```

**等待完成后，继续：**

**步骤2.3：升级系统包**

```bash
sudo apt upgrade -y
```

**如果仍然失败，尝试：**

```bash
# 修复dpkg状态
sudo dpkg --configure -a

# 修复损坏的包
sudo apt --fix-broken install

# 再次升级
sudo apt upgrade -y
```

**预期输出**：显示更新的包列表，然后自动升级

---

### 步骤3：安装Git

**目的**：安装Git用于克隆项目代码

```bash
sudo apt install -y git
```

**验证安装：**

```bash
git --version
```

**预期输出**：显示Git版本号（如：git version 2.34.1）

---

### 步骤4：创建项目目录

**目的**：创建项目存放目录

```bash
sudo mkdir -p /opt/beatsync
```

**验证：**

```bash
ls -la /opt/ | grep beatsync
```

**预期输出**：显示beatsync目录

---

### 步骤5：进入目录并清理（如果存在旧代码）

**目的**：确保目录干净

```bash
cd /opt
```

**如果之前有代码，先删除：**

```bash
sudo rm -rf beatsync
```

---

### 步骤6：克隆项目代码

**目的**：从GitHub克隆最新代码

```bash
sudo git clone https://github.com/scarlettyellow/BeatSync.git beatsync
```

**预期输出**：
```
Cloning into 'beatsync'...
remote: Enumerating objects: ...
Receiving objects: 100% ...
```

**验证：**

```bash
ls -la /opt/beatsync
```

**预期输出**：显示项目文件列表

---

### 步骤7：设置目录权限

**目的**：将项目目录的所有者设置为ubuntu用户

```bash
sudo chown -R ubuntu:ubuntu /opt/beatsync
```

**验证：**

```bash
ls -ld /opt/beatsync
```

**预期输出**：所有者应该是ubuntu

---

### 步骤8：进入项目目录

**目的**：准备运行部署脚本

```bash
cd /opt/beatsync
```

**验证当前位置：**

```bash
pwd
```

**预期输出**：/opt/beatsync

---

### 步骤9：运行部署脚本

**目的**：执行自动部署脚本，安装所有依赖和配置服务

```bash
sudo bash scripts/deployment/deploy_to_tencent_cloud.sh
```

**预期输出**：
```
==========================================
BeatSync 腾讯云服务器部署脚本
==========================================

步骤1: 更新系统...
步骤2: 安装基础工具...
步骤3: 检查Python版本...
步骤4: 安装FFmpeg...
...
部署完成！
```

**这个脚本会自动完成：**
- 安装Python依赖
- 安装FFmpeg
- 配置Nginx
- 生成SSL证书
- 创建systemd服务
- 启动服务

---

## 三、验证部署

### 步骤10：检查服务状态

**检查后端服务：**

```bash
sudo systemctl status beatsync
```

**预期输出**：显示"active (running)"

**检查Nginx服务：**

```bash
sudo systemctl status nginx
```

**预期输出**：显示"active (running)"

---

### 步骤11：测试API健康检查

**测试健康检查接口：**

```bash
curl -k https://124.221.58.149/api/health
```

**预期输出**：
```json
{"status":"healthy"}
```

**如果返回错误，检查：**
1. 防火墙是否开放443端口
2. Nginx是否运行
3. 后端服务是否运行

---

### 步骤12：访问API文档

**在浏览器中访问：**

- **API文档**：https://124.221.58.149/docs
- **健康检查**：https://124.221.58.149/api/health

**注意**：由于是自签名证书，浏览器会显示"不安全"警告，点击"高级" → "继续访问"即可。

---

## 四、配置防火墙

### 步骤13：在腾讯云控制台配置防火墙

1. 进入服务器详情页
2. 点击"防火墙"标签
3. 点击"添加规则"
4. 配置：
   - **端口**：443
   - **协议**：TCP
   - **来源**：0.0.0.0/0
   - **动作**：允许
5. 点击"确定"

---

## 五、验证前端连接

### 步骤14：等待GitHub Pages部署

代码已更新并推送，等待2-3分钟让GitHub Pages自动部署完成。

### 步骤15：测试前端功能

1. 访问：https://scarlettyellow.github.io/BeatSync/
2. 上传视频文件
3. 测试处理功能
4. 验证API地址是否正确（应该连接到124.221.58.149）

---

## 六、性能测试

### 步骤16：测试处理性能

使用waitonme高清版本样本测试：

**预期效果**：
- 处理时间：**0.8-1.2分钟**
- 相比旧服务器（2核2GB）：减少约2-2.5分钟
- **应该达到1分钟目标** ✅

---

## 七、终止正在运行的命令

### 如果命令一直显示"Command Running"

**方法1：通过控制台终止**
1. 点击"查看执行详情"
2. 查找"终止"或"Stop"按钮
3. 点击终止

**方法2：通过SSH终止（如果控制台无法终止）**

```bash
# SSH登录服务器后，查找进程
ps aux | grep -E 'bash|apt|dpkg|deploy'

# 终止进程（替换<PID>为实际的进程ID）
sudo kill <PID>

# 如果进程不响应，强制终止
sudo kill -9 <PID>
```

**详细说明**：参考 `docs/deployment/STOP_RUNNING_COMMAND.md`

---

## 八、故障排除

### 问题1：步骤1失败（dpkg错误）

**错误信息**：`dpkg: error: ...`

**解决**：
```bash
sudo dpkg --configure -a
sudo apt --fix-broken install
```

然后继续步骤2。

---

### 问题2：步骤3失败（Git安装失败）

**错误信息**：`E: Unable to locate package git`

**解决**：
```bash
sudo apt update
sudo apt install -y git
```

---

### 问题3：步骤6失败（Git克隆失败）

**错误信息**：`fatal: unable to access 'https://github.com/...'`

**可能原因**：
- 网络问题
- GitHub访问受限

**解决**：
1. 检查网络连接
2. 如果GitHub访问受限，可以手动上传代码

---

### 问题4：步骤9失败（部署脚本失败）

**查看详细错误：**

```bash
sudo bash scripts/deployment/deploy_to_tencent_cloud.sh 2>&1 | tee deploy.log
```

**常见问题**：

**Python依赖安装失败：**
```bash
cd /opt/beatsync
pip3 install --user numpy soundfile librosa opencv-python fastapi uvicorn python-multipart
```

**FFmpeg未安装：**
```bash
sudo apt install -y ffmpeg
```

**Nginx配置错误：**
```bash
sudo nginx -t
sudo tail -f /var/log/nginx/error.log
```

---

### 问题5：步骤10失败（服务未启动）

**查看服务日志：**

```bash
# 后端服务日志
sudo journalctl -u beatsync -f

# Nginx日志
sudo tail -f /var/log/nginx/error.log
```

**手动启动服务：**

```bash
# 启动后端服务
sudo systemctl start beatsync
sudo systemctl enable beatsync

# 启动Nginx
sudo systemctl start nginx
sudo systemctl enable nginx
```

---

### 问题6：步骤11失败（API无法访问）

**检查清单**：
1. ✅ 防火墙是否开放443端口
2. ✅ Nginx是否运行：`sudo systemctl status nginx`
3. ✅ 后端服务是否运行：`sudo systemctl status beatsync`
4. ✅ 端口是否监听：`sudo netstat -tlnp | grep -E '8000|443'`

**测试本地连接：**

```bash
# 测试本地8000端口
curl http://127.0.0.1:8000/api/health

# 测试本地443端口（通过Nginx）
curl -k https://127.0.0.1/api/health
```

---

## 八、快速检查清单

- [ ] 步骤1：修复系统状态
- [ ] 步骤2：更新系统
- [ ] 步骤3：安装Git
- [ ] 步骤4：创建项目目录
- [ ] 步骤5：进入目录
- [ ] 步骤6：克隆项目代码
- [ ] 步骤7：设置目录权限
- [ ] 步骤8：进入项目目录
- [ ] 步骤9：运行部署脚本
- [ ] 步骤10：检查服务状态
- [ ] 步骤11：测试API健康检查
- [ ] 步骤12：访问API文档
- [ ] 步骤13：配置防火墙
- [ ] 步骤14：等待GitHub Pages部署
- [ ] 步骤15：测试前端功能
- [ ] 步骤16：测试处理性能

---

## 九、命令汇总（方便复制）

### 完整命令序列

```bash
# 步骤1：修复系统状态
sudo dpkg --configure -a

# 步骤2：更新系统
sudo apt update
sudo apt upgrade -y

# 步骤3：安装Git
sudo apt install -y git

# 步骤4-5：创建目录并进入
sudo mkdir -p /opt/beatsync
cd /opt
sudo rm -rf beatsync

# 步骤6：克隆代码
sudo git clone https://github.com/scarlettyellow/BeatSync.git beatsync

# 步骤7：设置权限
sudo chown -R ubuntu:ubuntu /opt/beatsync

# 步骤8-9：进入目录并运行部署脚本
cd /opt/beatsync
sudo bash scripts/deployment/deploy_to_tencent_cloud.sh

# 步骤10：检查服务状态
sudo systemctl status beatsync
sudo systemctl status nginx

# 步骤11：测试API
curl -k https://124.221.58.149/api/health
```

---

**最后更新**：2025-12-01  
**新服务器IP**：124.221.58.149

