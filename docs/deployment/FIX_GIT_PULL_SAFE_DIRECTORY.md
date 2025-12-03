# 修复Git Pull时的安全目录错误

> **错误**：`fatal: detected dubious ownership in repository at '/opt/beatsync'`  
> **原因**：Git检测到仓库目录的所有者与当前用户不匹配  
> **解决方案**：添加安全目录配置

---

## 快速修复命令

### 方法1：添加安全目录配置（推荐）

**在服务器上执行**：
```bash
sudo git config --global --add safe.directory /opt/beatsync
cd /opt/beatsync
sudo git pull origin main
sudo systemctl restart beatsync
```

---

### 方法2：修改目录所有者（如果方法1不行）

**在服务器上执行**：
```bash
sudo chown -R ubuntu:ubuntu /opt/beatsync
cd /opt/beatsync
sudo git pull origin main
sudo systemctl restart beatsync
```

---

## 完整部署流程

### 步骤1：修复Git安全目录

```bash
sudo git config --global --add safe.directory /opt/beatsync
```

---

### 步骤2：拉取最新代码

```bash
cd /opt/beatsync
sudo git pull origin main
```

---

### 步骤3：重启服务

```bash
sudo systemctl restart beatsync
```

---

### 步骤4：验证服务状态

```bash
sudo systemctl status beatsync
```

---

## 一键修复命令

**在服务器上执行**：
```bash
sudo git config --global --add safe.directory /opt/beatsync && cd /opt/beatsync && sudo git pull origin main && sudo systemctl restart beatsync && echo "✅ 部署完成"
```

---

## 说明

### 为什么会出现这个错误？

- Git 2.35.2+ 引入了安全特性，防止在不受信任的目录中执行 Git 命令
- `/opt/beatsync` 目录可能由 `root` 用户创建，但当前以 `ubuntu` 用户执行命令
- Git 检测到所有者不匹配，触发安全保护

### 解决方案

- **方法1**：添加安全目录配置，告诉 Git 信任这个目录
- **方法2**：修改目录所有者，确保执行用户拥有该目录

---

**最后更新**：2025-12-03

