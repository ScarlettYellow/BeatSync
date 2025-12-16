# 验证SSH密码登录配置

> **目的**：验证密码登录是否已成功启用

---

## 快速验证步骤

### 步骤1：检查配置是否已修改

在VNC终端中执行：

```bash
sudo grep PasswordAuthentication /etc/ssh/sshd_config
```

**预期输出**：
- 应该显示：`PasswordAuthentication yes`
- 如果显示 `PasswordAuthentication no` 或没有输出，说明配置未生效

### 步骤2：检查SSH服务状态

```bash
sudo systemctl status sshd | head -5
```

**预期输出**：
- 应该显示：`Active: active (running)`

### 步骤3：如果配置未生效，手动执行

如果步骤1显示的不是 `PasswordAuthentication yes`，执行：

```bash
# 直接添加配置
echo "PasswordAuthentication yes" | sudo tee -a /etc/ssh/sshd_config

# 重启SSH服务
sudo systemctl restart sshd

# 再次验证
sudo grep PasswordAuthentication /etc/ssh/sshd_config
```

---

## 测试SSH连接

### 在本地机器上测试

打开新的终端窗口（本地机器），执行：

```bash
ssh ubuntu@1.12.239.225
```

**应该**：
- 提示输入密码
- 输入你的实例登录密码后能够成功登录

---

## 如果仍然无法连接

### 检查SSH服务日志

在服务器上执行：

```bash
sudo journalctl -u sshd -n 20
```

查看是否有错误信息。

### 检查防火墙

```bash
# 检查UFW状态
sudo ufw status

# 如果SSH端口未开放，开放它
sudo ufw allow 22/tcp
```

---

**最后更新**：2025-11-27



