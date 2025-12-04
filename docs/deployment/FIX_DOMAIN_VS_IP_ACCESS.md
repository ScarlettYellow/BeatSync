# 修复域名访问问题

> **问题**：使用IP地址可以访问，但使用域名无法访问  
> **原因**：DNS解析、浏览器缓存、或网络环境问题  
> **解决**：检查DNS解析、清除缓存、优化配置

---

## 问题分析

### 关键发现

从诊断结果看到：
- ✅ **使用IP地址访问成功**：`curl -k https://124.221.58.149/api/health` 返回 `{"status":"healthy"}`
- ✅ **访问日志显示成功请求**：多个外部IP成功访问（200响应）
- ✅ **UptimeRobot监控成功**：多个监控请求返回200
- ✅ **防火墙已开放**：443端口已开放
- ❌ **浏览器无法访问域名**：可能是浏览器或网络环境问题

### 重要信息

从访问日志看到：
- `180.101.245.252` - 使用域名 `http://beatsync.site/api/health` 访问成功（200）
- `101.204.220.4` - 使用IP地址访问成功（200）
- 多个UptimeRobot监控成功（200）

**这说明服务实际上是正常工作的！**

---

## 解决方案

### 方案1：检查DNS解析（最重要）

**在本地终端执行**：
```bash
# 检查域名解析
nslookup beatsync.site 8.8.8.8

# 检查是否解析到正确的IP
dig @8.8.8.8 beatsync.site +short

# 检查多个DNS服务器
for dns in 8.8.8.8 1.1.1.1 119.29.29.29; do
    echo "DNS服务器: $dns"
    dig @$dns beatsync.site +short
done
```

**预期结果**：应该都返回 `124.221.58.149`

---

### 方案2：清除浏览器和DNS缓存

**清除DNS缓存**：

**macOS**：
```bash
sudo dscacheutil -flushcache
sudo killall -HUP mDNSResponder
```

**Windows**：
```bash
ipconfig /flushdns
```

**清除浏览器缓存**：
1. 按 `Ctrl+Shift+Delete`（Windows）或 `Cmd+Shift+Delete`（Mac）
2. 选择"缓存的图片和文件"和"Cookie和其他网站数据"
3. 点击"清除数据"

---

### 方案3：使用curl测试域名访问

**在本地终端执行**：
```bash
# 测试HTTPS域名访问
curl -v https://beatsync.site/api/health

# 如果失败，尝试忽略证书验证
curl -k https://beatsync.site/api/health

# 测试HTTP域名访问（应该重定向到HTTPS）
curl -I http://beatsync.site/api/health
```

**如果curl可以访问但浏览器不能**：
- 说明是浏览器问题
- 需要清除浏览器缓存或使用隐私模式

---

### 方案4：检查DDoS防护设置

**在腾讯云控制台检查**：

1. **进入轻量应用服务器控制台**
   - 找到服务器实例（IP：124.221.58.149）

2. **检查DDoS防护设置**
   - 点击"DDoS防护"或"安全"标签
   - 查看防护规则和阈值
   - 确认没有阻止正常HTTPS连接

3. **检查防护日志**
   - 查看是否有拦截记录
   - 确认没有误拦截正常请求

---

### 方案5：尝试不同的网络环境

**可能的问题**：
1. **公司/学校网络防火墙**：可能阻止某些HTTPS连接
2. **ISP（网络服务提供商）**：可能阻止某些域名访问
3. **VPN连接**：可能影响网络路由

**解决方法**：
- 尝试使用移动网络（手机热点）
- 尝试关闭VPN
- 尝试不同的网络环境

---

## 诊断命令

### 在本地终端执行完整诊断

```bash
echo "=== 1. 测试IP地址访问 ==="
curl -k https://124.221.58.149/api/health -H "Host: beatsync.site"

echo ""
echo "=== 2. 测试域名访问（HTTPS） ==="
curl -v https://beatsync.site/api/health 2>&1 | head -30

echo ""
echo "=== 3. 测试域名访问（忽略证书） ==="
curl -k https://beatsync.site/api/health

echo ""
echo "=== 4. 检查域名解析（多个DNS服务器） ==="
for dns in 8.8.8.8 1.1.1.1 119.29.29.29; do
    echo "DNS服务器: $dns"
    dig @$dns beatsync.site +short
done

echo ""
echo "=== 5. 测试HTTP访问（应该重定向） ==="
curl -I http://beatsync.site/api/health 2>&1 | head -10
```

---

## 重要发现

### 从访问日志看，服务实际上是正常工作的

访问日志显示：
- ✅ 多个外部IP成功访问（200响应）
- ✅ UptimeRobot监控成功
- ✅ 使用IP地址访问成功
- ✅ 使用域名访问也成功（`180.101.245.252` 使用 `http://beatsync.site/api/health` 访问成功）

**这说明服务是正常工作的！**

---

## 如果浏览器仍然无法访问

### 可能的原因

1. **浏览器缓存问题**：
   - 浏览器可能缓存了旧的错误状态
   - 需要清除缓存

2. **浏览器扩展问题**：
   - 某些浏览器扩展可能阻止HTTPS连接
   - 需要禁用扩展后重试

3. **网络环境问题**：
   - 公司/学校网络可能阻止某些HTTPS连接
   - 需要尝试不同的网络环境

4. **DNS缓存问题**：
   - 本地DNS可能缓存了旧的解析结果
   - 需要清除DNS缓存

---

## 验证清单

- [x] 使用IP地址访问成功
- [x] 访问日志显示成功请求
- [x] 防火墙已开放443端口
- [ ] 域名解析正确（请测试）
- [ ] curl可以访问域名（请测试）
- [ ] 浏览器可以访问域名（请测试）
- [ ] 清除浏览器缓存后测试
- [ ] 尝试不同的网络环境

---

## 相关文档

- `docs/deployment/FIX_EXTERNAL_TLS_CONNECTION_RESET.md` - 外部TLS连接重置问题
- `docs/deployment/TROUBLESHOOT_BROWSER_ACCESS.md` - 浏览器访问问题排查

---

**最后更新**：2025-12-04

