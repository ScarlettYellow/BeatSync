# 修复腾讯云服务器故障

> **检测结果**：存在3个异常项
> - 内核故障（Panic）
> - 常用端口未开放（22端口）
> - 实例重启

---

## 一、问题分析

### 1.1 内核故障（Panic）

**问题**：
- 实例在2025-12-02 11:28出现过Panic
- 可能导致系统不稳定

**原因**：
- 可能是系统更新或配置问题
- 可能是资源不足导致
- 可能是硬件问题

### 1.2 常用端口未开放（22端口）

**问题**：
- 外网探测22端口未放通
- 可能导致无法SSH登录

**原因**：
- 防火墙未配置22端口规则

### 1.3 实例重启

**问题**：
- 实例在2025-12-02 11:27出现过重启
- 可能与内核故障相关

---

## 二、解决方案

### 问题1：修复内核故障（Panic）

#### 步骤1：检查系统日志

**通过VNC登录服务器后：**

```bash
# 查看系统日志
sudo dmesg | tail -50

# 查看内核日志
sudo journalctl -k | tail -50

# 查看最近的错误
sudo journalctl -p err -n 50
```

#### 步骤2：检查系统资源

```bash
# 检查内存使用
free -h

# 检查磁盘空间
df -h

# 检查系统负载
uptime
```

#### 步骤3：更新系统（如果资源充足）

```bash
# 更新系统
sudo apt update
sudo apt upgrade -y

# 重启系统（如果必要）
sudo reboot
```

#### 步骤4：如果问题持续

**如果内核故障持续出现：**
1. 考虑重置系统（会丢失数据）
2. 或联系腾讯云技术支持

---

### 问题2：开放22端口（SSH）

#### 步骤1：在腾讯云控制台配置防火墙

1. 进入服务器详情页
2. 点击"防火墙"标签
3. 点击"添加规则"
4. 配置：
   - **端口**：22
   - **协议**：TCP
   - **来源**：0.0.0.0/0（或限制为你的IP）
   - **动作**：允许
5. 点击"确定"

#### 步骤2：验证端口开放

**在本地测试：**

```bash
# 测试SSH连接
ssh ubuntu@124.221.58.149

# 或使用telnet测试
telnet 124.221.58.149 22
```

---

### 问题3：处理实例重启

#### 步骤1：检查重启原因

```bash
# 查看系统启动日志
sudo journalctl -b -1 | tail -50

# 查看上次启动的错误
sudo journalctl -b -1 -p err
```

#### 步骤2：检查服务状态

```bash
# 检查所有服务状态
sudo systemctl status

# 检查关键服务
sudo systemctl status beatsync
sudo systemctl status nginx
```

#### 步骤3：如果服务未启动，重新启动

```bash
# 启动后端服务
sudo systemctl start beatsync
sudo systemctl enable beatsync

# 启动Nginx
sudo systemctl start nginx
sudo systemctl enable nginx

# 检查状态
sudo systemctl status beatsync
sudo systemctl status nginx
```

---

## 三、完整修复流程

### 步骤1：通过VNC登录服务器

1. 在腾讯云控制台，点击"登录"按钮
2. 选择"VNC登录"
3. 在浏览器中打开终端

### 步骤2：检查系统状态

```bash
# 检查系统是否正常运行
uptime

# 检查服务状态
sudo systemctl status beatsync
sudo systemctl status nginx

# 检查磁盘空间
df -h
```

### 步骤3：修复防火墙（开放22端口）

**在腾讯云控制台：**
1. 进入服务器详情页
2. 点击"防火墙"标签
3. 添加规则：端口22，协议TCP，允许

### 步骤4：重启服务（如果需要）

```bash
# 重启后端服务
sudo systemctl restart beatsync

# 重启Nginx
sudo systemctl restart nginx

# 检查状态
sudo systemctl status beatsync
sudo systemctl status nginx
```

### 步骤5：验证修复

```bash
# 测试API健康检查
curl -k https://124.221.58.149/api/health

# 应该返回：{"status":"healthy"}
```

---

## 四、紧急处理方案

### 如果服务器无法访问

#### 方案1：重启服务器

**在腾讯云控制台：**
1. 点击"重启"按钮
2. 等待服务器重启完成（2-3分钟）
3. 重新登录并检查服务

#### 方案2：重置密码（如果无法登录）

**在腾讯云控制台：**
1. 点击"重置密码"
2. 设置新密码
3. 重启服务器
4. 使用新密码登录

#### 方案3：查看控制台日志

**在腾讯云控制台：**
1. 进入"监控"标签
2. 查看系统日志
3. 查看错误信息

---

## 五、预防措施

### 5.1 配置自动重启服务

**确保服务在重启后自动启动：**

```bash
# 检查服务是否已启用自动启动
sudo systemctl is-enabled beatsync
sudo systemctl is-enabled nginx

# 如果未启用，启用它
sudo systemctl enable beatsync
sudo systemctl enable nginx
```

### 5.2 配置监控告警

**在腾讯云控制台：**
1. 进入"监控"标签
2. 配置告警规则
3. 设置CPU、内存、磁盘告警

### 5.3 定期备份

**定期备份重要数据：**
1. 使用快照功能
2. 或备份到COS

---

## 六、快速修复命令

### 完整修复流程（通过VNC登录后执行）

```bash
# 1. 检查系统状态
uptime
df -h
free -h

# 2. 检查服务状态
sudo systemctl status beatsync
sudo systemctl status nginx

# 3. 如果服务未运行，启动服务
sudo systemctl start beatsync
sudo systemctl start nginx
sudo systemctl enable beatsync
sudo systemctl enable nginx

# 4. 检查端口监听
sudo netstat -tlnp | grep -E '8000|443'

# 5. 测试API
curl -k https://124.221.58.149/api/health
```

---

## 七、问题优先级

### 高优先级（立即处理）

1. ✅ **开放22端口**：否则无法SSH登录
2. ✅ **检查服务状态**：确保服务正常运行

### 中优先级（尽快处理）

3. ⚠️ **检查内核故障**：查看日志，了解原因
4. ⚠️ **检查重启原因**：确保系统稳定

### 低优先级（观察）

5. 📊 **监控系统状态**：持续观察是否再次出现

---

## 八、验证修复

### 检查清单

- [ ] 22端口已开放（可以在控制台配置）
- [ ] 可以通过SSH登录
- [ ] 后端服务正常运行
- [ ] Nginx服务正常运行
- [ ] API健康检查通过
- [ ] 系统资源充足（内存、磁盘）

---

## 九、如果问题持续

### 联系腾讯云技术支持

如果问题持续出现：
1. 在腾讯云控制台提交工单
2. 提供错误日志和检测结果
3. 描述问题现象

### 考虑重置服务器

如果问题严重：
1. 备份重要数据
2. 重置系统（会丢失所有数据）
3. 重新部署服务

---

**最后更新**：2025-12-01

