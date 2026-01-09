# 修复Git安全目录错误

> **问题**：`fatal: detected dubious ownership in repository`

---

## 问题分析

**错误信息**：
```
fatal: detected dubious ownership in repository at '/opt/beatsync'
To add an exception for this directory, call:
git config --global --add safe.directory /opt/beatsync
```

**原因**：
- Git检测到仓库的所有者与当前用户不匹配
- 这是Git的安全机制，防止恶意代码执行

---

## 解决方案

### 方案1：添加安全目录（推荐）

在服务器上执行：

```bash
git config --global --add safe.directory /opt/beatsync
cd /opt/beatsync
git pull origin main
sudo systemctl restart beatsync
echo "✅ 代码已更新，服务已重启"
```

### 方案2：修复目录所有权

如果方案1不行，修复目录所有权：

```bash
sudo chown -R ubuntu:ubuntu /opt/beatsync
cd /opt/beatsync
git pull origin main
sudo systemctl restart beatsync
echo "✅ 代码已更新，服务已重启"
```

---

## 一键修复命令

**在服务器上执行**：

```bash
git config --global --add safe.directory /opt/beatsync && cd /opt/beatsync && git pull origin main && sudo systemctl restart beatsync && echo "✅ 代码已更新，服务已重启"
```

---

**最后更新**：2025-12-01












