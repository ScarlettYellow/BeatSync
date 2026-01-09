# 启用SSH密码登录 - 简单方法

> **目的**：在腾讯云服务器上启用SSH密码登录，解决"Permission denied"问题

---

## 方法1：使用sed命令（最简单，推荐）

**在VNC终端中直接执行以下命令**：

```bash
# 1. 备份配置文件
sudo cp /etc/ssh/sshd_config /etc/ssh/sshd_config.backup

# 2. 启用密码登录（如果已存在则修改，不存在则添加）
sudo sed -i 's/#PasswordAuthentication yes/PasswordAuthentication yes/' /etc/ssh/sshd_config
sudo sed -i 's/PasswordAuthentication no/PasswordAuthentication yes/' /etc/ssh/sshd_config

# 如果文件中没有PasswordAuthentication行，添加它
if ! grep -q "^PasswordAuthentication" /etc/ssh/sshd_config; then
    echo "PasswordAuthentication yes" | sudo tee -a /etc/ssh/sshd_config
fi

# 3. 验证配置
sudo grep PasswordAuthentication /etc/ssh/sshd_config

# 4. 重启SSH服务
sudo systemctl restart sshd

# 5. 验证SSH服务状态
sudo systemctl status sshd
```

**预期输出**：
- 第3步应该显示：`PasswordAuthentication yes`
- 第5步应该显示：`active (running)`

---

## 方法2：使用nano编辑器（比vim简单）

**在VNC终端中执行**：

```bash
# 使用nano编辑器（比vim更简单）
sudo nano /etc/ssh/sshd_config
```

**在nano中**：
1. 按 `Ctrl+W` 搜索 `PasswordAuthentication`
2. 找到后，确保设置为 `PasswordAuthentication yes`
3. 如果前面有 `#` 号，删除它
4. 如果不存在，在文件末尾添加 `PasswordAuthentication yes`
5. 按 `Ctrl+O` 保存
6. 按 `Enter` 确认文件名
7. 按 `Ctrl+X` 退出

**然后重启SSH服务**：

```bash
sudo systemctl restart sshd
```

---

## 方法3：一键脚本（最简单）

**在VNC终端中执行以下完整命令**：

```bash
# 一键启用密码登录
sudo bash -c 'cp /etc/ssh/sshd_config /etc/ssh/sshd_config.backup && \
sed -i "s/#PasswordAuthentication yes/PasswordAuthentication yes/" /etc/ssh/sshd_config && \
sed -i "s/PasswordAuthentication no/PasswordAuthentication yes/" /etc/ssh/sshd_config && \
grep -q "^PasswordAuthentication" /etc/ssh/sshd_config || echo "PasswordAuthentication yes" >> /etc/ssh/sshd_config && \
systemctl restart sshd && \
echo "✅ 密码登录已启用！" && \
systemctl status sshd | head -3'
```

---

## 验证配置

**执行以下命令验证**：

```bash
# 检查配置
sudo grep PasswordAuthentication /etc/ssh/sshd_config

# 检查SSH服务状态
sudo systemctl status sshd
```

**应该看到**：
- `PasswordAuthentication yes`
- SSH服务状态为 `active (running)`

---

## 测试SSH连接

**在本地机器上测试**：

```bash
# 测试SSH连接
ssh ubuntu@1.12.239.225
```

**应该能够**：
- 提示输入密码
- 使用实例登录密码成功登录

---

## 如果仍然无法连接

### 检查防火墙

```bash
# 在服务器上检查SSH端口（22）是否开放
sudo ufw status
# 或
sudo iptables -L -n | grep 22
```

### 检查SSH服务

```bash
# 检查SSH服务是否运行
sudo systemctl status sshd

# 查看SSH日志
sudo journalctl -u sshd -n 20
```

---

## 完成后的下一步

启用密码登录后，可以：

1. **在本地机器上测试SSH连接**：
   ```bash
   ssh ubuntu@1.12.239.225
   ```

2. **运行上传脚本**：
   ```bash
   cd /Users/scarlett/Projects/BeatSync
   ./scripts/deployment/upload_to_tencent_cloud.sh
   ```

---

**最后更新**：2025-11-27












