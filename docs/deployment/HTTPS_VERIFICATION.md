# HTTPS配置验证和测试

> **目的**：验证HTTPS配置是否成功，测试完整功能

---

## 验证步骤

### 步骤1：验证Nginx服务运行正常

```bash
# 检查Nginx服务状态
sudo systemctl status nginx
```

**预期输出**：应该显示 `active (running)`

---

### 步骤2：验证HTTPS访问（服务器本地）

```bash
# 测试HTTPS健康检查
curl -k https://124.221.58.149/api/health
```

**预期输出**：
```json
{"status":"healthy","timestamp":"2025-12-02T14:13:43.048160"}
```

**如果返回错误，检查**：
- Nginx是否运行：`sudo systemctl status nginx`
- 防火墙是否开放443端口
- 查看Nginx错误日志：`sudo tail -f /var/log/nginx/error.log`

---

### 步骤3：验证HTTPS访问（浏览器）

**在浏览器中访问**：
- `https://124.221.58.149/api/health`
- `https://124.221.58.149/docs`

**注意**：
- 浏览器会显示"不安全"警告（因为是自签名证书）
- 点击"高级" → "继续前往 124.221.58.149（不安全）"
- 这是正常的，因为使用的是自签名证书

**预期结果**：
- 健康检查应该返回JSON响应
- API文档应该显示FastAPI文档页面

---

### 步骤4：验证HTTP重定向到HTTPS

```bash
# 测试HTTP访问（应该重定向到HTTPS）
curl -I http://124.221.58.149/api/health
```

**预期输出**：
```
HTTP/1.1 301 Moved Permanently
Location: https://124.221.58.149/api/health
```

**说明**：HTTP请求被正确重定向到HTTPS

---

### 步骤5：检查防火墙配置

**确认以下端口已开放**：
- **443**：HTTPS（必需）
- **8000**：后端服务（可选，如果直接访问）

**在腾讯云控制台检查**：
1. 登录腾讯云控制台
2. 进入轻量应用服务器 → 选择实例
3. 点击"防火墙"标签
4. 确认443端口规则存在且已启用

---

## 前端配置验证

### 检查前端配置

**前端应该已更新为HTTPS**：
- 文件：`web_service/frontend/script.js`
- 配置：`https://124.221.58.149`

**如果未更新，需要更新**：
```javascript
// 生产环境：使用腾讯云服务器（HTTPS）
const backendUrl = window.API_BASE_URL || 'https://124.221.58.149';
```

**然后提交并推送**：
```bash
cd /Users/scarlett/Projects/BeatSync
git add web_service/frontend/script.js
git commit -m "feat: 更新前端API地址为HTTPS"
git push origin main
```

---

## 完整功能测试

### 测试1：访问前端页面

**访问**：https://scarlettyellow.github.io/BeatSync/

**检查浏览器控制台**：
- 打开开发者工具（F12）
- 查看Console标签
- 应该看到：
  ```
  🟢 生产环境检测（腾讯云服务器 - HTTPS）
     访问地址: https://scarlettyellow.github.io/BeatSync/
     后端URL: https://124.221.58.149
  ```

**不应该看到Mixed Content错误**

---

### 测试2：健康检查

**在前端页面**：
- 应该自动执行健康检查
- 不应该显示"后端服务不可用"错误

**或者手动测试**：
- 在浏览器中访问：`https://124.221.58.149/api/health`
- 应该返回：`{"status":"healthy","timestamp":"..."}`

---

### 测试3：上传视频

**测试完整流程**：
1. 上传dance视频
2. 上传bgm视频
3. 点击"开始处理"
4. 查看处理状态
5. 下载处理结果

**预期结果**：
- 上传应该成功（不再出现Mixed Content错误）
- 处理应该正常进行
- 可以正常下载结果

---

## 故障排查

### 如果HTTPS无法访问

**检查Nginx状态**：
```bash
sudo systemctl status nginx
```

**检查Nginx配置**：
```bash
sudo nginx -t
```

**查看Nginx日志**：
```bash
sudo tail -f /var/log/nginx/error.log
```

**检查端口监听**：
```bash
sudo netstat -tlnp | grep 443
```

**检查防火墙**：
- 确认腾讯云防火墙已开放443端口
- 确认UFW已开放443端口（如果启用）

---

### 如果前端仍然显示Mixed Content错误

**检查前端配置**：
- 确认前端API地址是 `https://124.221.58.149`（不是 `http://`）
- 确认GitHub Pages已部署最新版本

**清除浏览器缓存**：
- 按 `Ctrl+Shift+R`（Windows/Linux）或 `Cmd+Shift+R`（Mac）强制刷新
- 或者使用隐私模式测试

---

### 如果浏览器显示证书警告

**这是正常的**：
- 自签名证书会在浏览器中显示"不安全"警告
- 点击"高级" → "继续访问"即可
- 功能不受影响

**如果要消除警告**：
- 需要使用受信任的SSL证书（如Let's Encrypt）
- 但需要域名，不能使用IP地址

---

## 部署完成检查清单

- [x] Nginx已安装
- [x] SSL证书已生成
- [x] Nginx配置已创建
- [x] Nginx配置已启用
- [x] Nginx配置测试通过
- [x] Nginx服务运行正常
- [x] 防火墙已配置（443端口）
- [x] HTTPS访问正常（服务器本地）
- [ ] HTTPS访问正常（浏览器）
- [ ] HTTP重定向到HTTPS正常
- [ ] 前端配置已更新为HTTPS
- [ ] 前端页面可以正常访问后端
- [ ] 上传功能正常
- [ ] 处理功能正常
- [ ] 下载功能正常

---

## 后续优化建议

### 1. 配置域名（可选）

**如果有域名**：
- 配置DNS解析到服务器IP
- 使用域名访问服务
- 可以使用Let's Encrypt免费证书（消除浏览器警告）

### 2. 配置日志轮转

**避免日志文件过大**：
```bash
# 配置Nginx日志轮转
sudo vim /etc/logrotate.d/nginx
```

### 3. 监控和告警

**建议配置**：
- 服务监控（监控Nginx和BeatSync服务状态）
- 性能监控（监控CPU、内存、带宽使用）

---

**最后更新**：2025-12-02

