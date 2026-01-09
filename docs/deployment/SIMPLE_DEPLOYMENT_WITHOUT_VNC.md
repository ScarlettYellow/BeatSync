# 简单部署方案（不使用VNC）

> **目的**：使用Git直接在服务器上克隆项目并部署，无需VNC和SSH配置

---

## 方案：使用Git克隆 + 腾讯云控制台

### 优点
- ✅ 不需要VNC终端
- ✅ 不需要配置SSH密码登录
- ✅ 只需要在腾讯云控制台操作
- ✅ 简单直接

---

## 步骤1：在腾讯云控制台使用"文件传输"功能

### 方式1：使用腾讯云控制台的"文件传输"（如果有）

1. 在腾讯云控制台，进入服务器详情页
2. 查找"文件传输"或"文件管理"功能
3. 上传项目文件

### 方式2：使用"执行命令"功能（推荐）

1. 在腾讯云控制台，进入服务器详情页
2. 查找"执行命令"或"命令执行"功能
3. 直接执行以下命令

---

## 步骤2：在服务器上执行命令

### 如果腾讯云控制台有"执行命令"功能

**直接复制粘贴以下命令块**：

```bash
# 1. 更新系统并安装Git
sudo apt update && sudo apt install -y git

# 2. 创建项目目录
sudo mkdir -p /opt/beatsync
cd /opt

# 3. 克隆项目（如果项目是公开的）
sudo git clone https://github.com/scarlettyellow/BeatSync.git beatsync

# 4. 设置权限
sudo chown -R ubuntu:ubuntu /opt/beatsync

# 5. 进入项目目录
cd /opt/beatsync

# 6. 运行部署脚本
sudo bash scripts/deployment/deploy_to_tencent_cloud.sh
```

---

## 步骤3：如果项目是私有的

如果GitHub仓库是私有的，需要先配置SSH密钥，或者：

### 使用HTTPS + Personal Access Token

1. 在GitHub创建Personal Access Token
2. 使用token克隆：

```bash
# 替换YOUR_TOKEN为你的GitHub token
git clone https://YOUR_TOKEN@github.com/scarlettyellow/BeatSync.git /opt/beatsync
```

---

## 方案2：使用压缩包上传（如果Git不可用）

### 步骤1：在本地创建压缩包

在本地机器上执行：

```bash
cd /Users/scarlett/Projects/BeatSync

# 创建压缩包
tar -czf beatsync.tar.gz \
  --exclude='.git' \
  --exclude='__pycache__' \
  --exclude='*.pyc' \
  --exclude='.beatsync_cache' \
  --exclude='outputs/web_uploads/*' \
  --exclude='outputs/web_outputs/*' \
  --exclude='outputs/logs/*' \
  .
```

### 步骤2：上传到服务器

**如果腾讯云控制台有文件上传功能**：
1. 上传 `beatsync.tar.gz` 到服务器
2. 使用"执行命令"功能解压

**执行命令**：

```bash
# 解压到目标目录
cd /opt
sudo mkdir -p beatsync
cd beatsync
sudo tar -xzf /path/to/beatsync.tar.gz
sudo chown -R ubuntu:ubuntu /opt/beatsync
cd /opt/beatsync
sudo bash scripts/deployment/deploy_to_tencent_cloud.sh
```

---

## 方案3：使用腾讯云控制台的"Web终端"（如果有）

如果腾讯云控制台提供Web终端功能：

1. 在控制台找到"Web终端"或"在线终端"
2. 直接在浏览器中操作
3. 执行上述Git克隆命令

---

## 推荐流程

### 最简单的方式（如果项目在GitHub上公开）

1. **在腾讯云控制台找到"执行命令"功能**
2. **执行以下命令**：

```bash
sudo apt update && \
sudo apt install -y git && \
sudo mkdir -p /opt/beatsync && \
cd /opt && \
sudo git clone https://github.com/scarlettyellow/BeatSync.git beatsync && \
sudo chown -R ubuntu:ubuntu /opt/beatsync && \
cd /opt/beatsync && \
sudo bash scripts/deployment/deploy_to_tencent_cloud.sh
```

**这个命令会**：
- ✅ 安装Git
- ✅ 克隆项目
- ✅ 设置权限
- ✅ 自动运行部署脚本

---

## 如果腾讯云控制台没有"执行命令"功能

### 使用SSH密钥（如果已配置）

如果你之前配置过SSH密钥，可以在本地机器上：

```bash
# 使用密钥连接
ssh -i ~/.ssh/your_key ubuntu@1.12.239.225

# 然后执行上述命令
```

### 或者：使用腾讯云控制台的"重置密码"功能

1. 在控制台重置SSH密码
2. 使用新密码通过SSH连接
3. 执行部署命令

---

## 验证部署

部署完成后，在浏览器中访问：

- **健康检查**：http://1.12.239.225:8000/api/health
- **API文档**：http://1.12.239.225:8000/docs

---

## 总结

**推荐方式**：
1. ✅ 使用腾讯云控制台的"执行命令"功能（如果有）
2. ✅ 直接执行Git克隆命令
3. ✅ 自动运行部署脚本

**优点**：
- 不需要VNC
- 不需要配置SSH
- 一条命令完成所有操作

---

**最后更新**：2025-11-27












