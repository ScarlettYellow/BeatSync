# 部署完成后的下一步

> **状态**：后端服务已成功部署并运行
> **下一步**：配置防火墙、更新前端、测试服务

---

## ✅ 已完成

- ✅ 后端服务已部署
- ✅ 健康检查可访问：http://1.12.239.225:8000/api/health
- ✅ API文档可访问：http://1.12.239.225:8000/docs

---

## 步骤1：配置防火墙（必须）

### 在腾讯云控制台配置

1. **进入服务器详情页**
2. **点击"防火墙"标签**
3. **添加规则**：
   - **端口**：`8000`
   - **协议**：`TCP`
   - **来源**：`0.0.0.0/0`（允许所有IP，或限制为特定IP）
   - **动作**：`允许`
4. **保存规则**

### 验证防火墙配置

配置完成后，从本地机器测试：

```bash
curl http://1.12.239.225:8000/api/health
```

**应该返回**：`{"status":"healthy","timestamp":"..."}`

---

## 步骤2：更新前端配置（如果还没更新）

### 检查前端配置

前端配置应该已经更新为使用腾讯云服务器地址。如果还没更新，需要：

1. **检查前端代码**：`web_service/frontend/script.js`
2. **确认API地址**：应该是 `http://1.12.239.225:8000`

### 如果还没更新，执行：

```bash
cd /Users/scarlett/Projects/BeatSync
git add web_service/frontend/script.js
git commit -m "feat: 更新前端API地址为腾讯云服务器"
git push origin main
```

**GitHub Pages会自动部署更新**（通常几分钟内生效）

---

## 步骤3：测试完整流程

### 3.1 测试前端访问

访问前端页面：
- https://scarlettyellow.github.io/BeatSync/

### 3.2 测试上传和处理

1. **上传测试视频**：
   - 选择一个小的测试视频文件（<50MB）
   - 上传dance视频和BGM视频

2. **提交处理任务**：
   - 点击"开始处理"
   - 观察处理状态

3. **验证处理时间**：
   - 记录处理时间
   - 对比之前Render的处理时间（10-20分钟）
   - **预期**：2-4分钟（2核2GB配置）

### 3.3 验证结果

- ✅ 上传成功
- ✅ 处理成功
- ✅ 可以下载结果
- ✅ 处理时间明显缩短

---

## 步骤4：性能监控

### 监控服务器资源

在服务器上执行：

```bash
# 查看CPU和内存使用
htop
# 或
top

# 查看内存使用
free -h

# 查看磁盘使用
df -h

# 查看服务日志
sudo journalctl -u beatsync -f
```

### 关键指标

- **CPU使用率**：应该充分利用2核（80-100%）
- **内存使用**：应该<1.5GB（留有余量）
- **处理时间**：预期2-4分钟（相比Render的10-20分钟）

---

## 步骤5：优化配置（可选）

### 5.1 如果内存不足

如果处理大文件时内存不足，可以配置swap：

```bash
# 创建2GB swap文件
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# 永久启用
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

### 5.2 如果处理时间仍然较长

考虑：
- 升级到2核4GB配置（如果预算允许）
- 优化代码（启用并行处理）
- 优化FFmpeg参数

---

## 步骤6：配置自动清理（可选）

### 清理旧文件

可以配置定时任务清理旧的上传和输出文件：

```bash
# 编辑crontab
sudo crontab -e

# 添加以下行（每天凌晨2点清理3天前的文件）
0 2 * * * find /opt/beatsync/web_uploads -type f -mtime +3 -delete
0 2 * * * find /opt/beatsync/web_outputs -type d -mtime +3 -exec rm -rf {} +
```

---

## 步骤7：设置监控和告警（可选）

### 监控服务状态

可以配置监控脚本检查服务是否运行：

```bash
# 创建监控脚本
sudo vim /opt/beatsync/check_service.sh
```

**脚本内容**：

```bash
#!/bin/bash
if ! systemctl is-active --quiet beatsync; then
    systemctl restart beatsync
    echo "$(date): 服务已重启" >> /opt/beatsync/logs/service_monitor.log
fi
```

**添加到crontab**：

```bash
# 每5分钟检查一次
*/5 * * * * /opt/beatsync/check_service.sh
```

---

## 验证清单

### ✅ 必须完成

- [ ] 防火墙已配置（开放8000端口）
- [ ] 前端配置已更新（如果还没更新）
- [ ] 前端可以正常访问
- [ ] 可以上传视频
- [ ] 可以处理视频
- [ ] 处理时间明显缩短

### ✅ 可选完成

- [ ] 配置swap（如果内存不足）
- [ ] 配置自动清理
- [ ] 配置监控和告警
- [ ] 性能测试和优化

---

## 常见问题

### 问题1：前端无法连接后端

**检查**：
1. 防火墙是否已配置
2. 前端API地址是否正确
3. 后端服务是否运行

### 问题2：处理时间仍然很长

**可能原因**：
- 内存不足（2GB可能不够）
- 视频文件太大
- 需要启用并行处理

**解决**：
- 考虑升级到2核4GB
- 或优化代码

### 问题3：处理失败

**检查**：
1. 查看服务日志：`sudo journalctl -u beatsync -n 50`
2. 检查FFmpeg：`ffmpeg -version`
3. 检查磁盘空间：`df -h`

---

## 总结

**当前状态**：
- ✅ 后端服务已部署并运行
- ✅ 健康检查和API文档可访问

**下一步**：
1. **配置防火墙**（必须）
2. **更新前端**（如果还没更新）
3. **测试完整流程**
4. **验证性能提升**

**预期结果**：
- 处理时间从10-20分钟降至2-4分钟
- 性能提升3-5倍

---

**最后更新**：2025-12-01












