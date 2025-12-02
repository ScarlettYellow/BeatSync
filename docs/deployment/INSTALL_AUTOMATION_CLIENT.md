# 安装腾讯云自动化助手客户端

> **问题**：在腾讯云"执行命令"页面显示"当前未安装客户端"，无法创建命令

---

## 问题分析

**原因**：
- 腾讯云的"执行命令"功能需要安装"自动化助手"客户端
- 新创建的服务器默认没有安装此客户端
- 需要手动安装后才能使用"执行命令"功能

---

## 解决方案

### 方案1：安装自动化助手客户端（推荐）

#### 步骤1：点击安装指引

在"执行命令"页面：
1. 找到"请按照指引进行安装安装指引"链接
2. 点击链接，查看安装指引

#### 步骤2：通过SSH登录安装

**如果安装指引提供了命令，直接执行。**

**或者使用以下命令安装（Ubuntu系统）：**

```bash
# 下载安装脚本
wget https://tat-gz-1258344699.cos.ap-guangzhou.myqcloud.com/tat_agent_install.sh

# 执行安装
sudo bash tat_agent_install.sh

# 或者使用腾讯云官方安装命令（如果提供）
```

**验证安装：**

```bash
# 检查服务状态
sudo systemctl status tat_agent

# 或
ps aux | grep tat_agent
```

---

### 方案2：直接使用SSH登录（更简单，推荐）

**如果不想安装客户端，可以直接使用SSH登录服务器执行命令。**

#### 步骤1：SSH登录服务器

在腾讯云控制台：
1. 点击"登录"按钮
2. 选择登录方式：
   - **VNC登录**：在浏览器中直接登录
   - **密码/密钥登录**：使用SSH客户端

#### 步骤2：执行部署命令

登录后，直接在终端执行部署命令：

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
```

---

## 推荐方案对比

### 方案1：安装自动化助手客户端

**优点**：
- ✅ 可以在控制台直接执行命令
- ✅ 无需SSH登录
- ✅ 方便管理

**缺点**：
- ❌ 需要额外安装
- ❌ 可能需要一些时间

### 方案2：直接使用SSH登录（推荐）

**优点**：
- ✅ 无需安装额外软件
- ✅ 立即可以使用
- ✅ 更直接，更灵活

**缺点**：
- ⚠️ 需要SSH登录

---

## 推荐操作

### 立即部署：使用SSH登录（推荐）

**步骤1：SSH登录服务器**

在腾讯云控制台：
1. 点击"登录"按钮
2. 选择"VNC登录"（最简单，在浏览器中直接登录）
3. 或选择"密码/密钥登录"（使用SSH客户端）

**步骤2：执行部署命令**

登录后，按照分步部署指南执行命令。

---

### 未来使用：安装自动化助手客户端（可选）

如果以后想使用"执行命令"功能，可以安装客户端：

1. 点击"安装指引"链接
2. 按照指引安装客户端
3. 安装完成后，就可以在控制台执行命令了

---

## SSH登录方式

### 方式1：VNC登录（最简单）

**步骤**：
1. 在腾讯云控制台，点击"登录"按钮
2. 选择"VNC登录"
3. 在浏览器中直接打开终端
4. 默认用户名：`ubuntu`
5. 输入密码（如果设置了）

**优点**：
- ✅ 无需SSH客户端
- ✅ 在浏览器中直接操作
- ✅ 最简单

---

### 方式2：SSH客户端登录

**步骤**：
1. 在本地终端执行：
```bash
ssh ubuntu@124.221.58.149
```
2. 输入密码

**优点**：
- ✅ 更灵活
- ✅ 可以复制粘贴命令
- ✅ 支持本地工具

---

## 完整部署流程（使用SSH）

### 第一步：SSH登录

```bash
# 使用VNC登录（在浏览器中）
# 或使用SSH客户端
ssh ubuntu@124.221.58.149
```

### 第二步：执行部署命令

按照分步部署指南执行：

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
```

---

## 总结

### 推荐方案

**使用SSH登录部署**（更简单、更直接）：
1. 点击"登录"按钮
2. 选择"VNC登录"或"密码/密钥登录"
3. 在终端中执行部署命令

### 可选方案

**安装自动化助手客户端**（如果以后想用控制台执行命令）：
1. 点击"安装指引"链接
2. 按照指引安装
3. 安装完成后可以使用"执行命令"功能

---

**最后更新**：2025-12-01

