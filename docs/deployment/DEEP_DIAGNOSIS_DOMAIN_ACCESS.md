# 深度诊断域名访问问题

> **问题**：配置正确，但域名访问仍然失败  
> **可能原因**：SNI问题、网络环境、DNS解析、或中间设备阻止  
> **解决**：深入诊断SNI、网络环境、DNS解析

---

## 问题分析

### 当前状态

- ✅ **Nginx配置正确**：配置语法正确，server_name正确
- ✅ **默认配置已禁用**：只有beatsync配置启用
- ✅ **使用IP地址可以访问**：说明服务正常
- ❌ **使用域名无法访问**：`Connection reset by peer`

### 关键矛盾

- **IP地址访问成功**：说明Nginx和FastAPI都正常
- **域名访问失败**：说明问题在域名解析或SNI处理

---

## 深入诊断

### 步骤1：测试SNI（Server Name Indication）

**在本地终端执行**：

```bash
# 测试使用SNI
echo | openssl s_client -connect beatsync.site:443 -servername beatsync.site 2>&1 | head -30

# 测试不使用SNI
echo | openssl s_client -connect beatsync.site:443 2>&1 | head -30

# 对比结果
```

**如果使用SNI成功但不使用SNI失败**：
- 说明是SNI配置问题
- 需要确保Nginx正确支持SNI

---

### 步骤2：检查DNS解析（多个DNS服务器）

**在本地终端执行**：

```bash
# 检查多个DNS服务器的解析结果
for dns in 8.8.8.8 1.1.1.1 119.29.29.29 223.5.5.5; do
    echo "=== DNS服务器: $dns ==="
    dig @$dns beatsync.site +short
    echo ""
done

# 检查DNS解析的详细信息
dig @8.8.8.8 beatsync.site +trace
```

**如果不同DNS服务器返回不同结果**：
- 说明DNS传播未完成
- 需要等待DNS传播

---

### 步骤3：测试HTTP访问（应该重定向）

**在本地终端执行**：

```bash
# 测试HTTP访问
curl -v http://beatsync.site/api/health 2>&1 | head -20

# 测试HTTP访问（跟随重定向）
curl -L http://beatsync.site/api/health
```

**预期结果**：
- HTTP应该返回301重定向到HTTPS
- 如果HTTP也无法访问，说明是DNS或网络问题

---

### 步骤4：检查网络路由

**在本地终端执行**：

```bash
# 追踪路由到服务器
traceroute 124.221.58.149

# 或使用mtr（如果已安装）
mtr -r -c 10 124.221.58.149
```

**如果路由异常**：
- 说明网络路径有问题
- 可能需要联系网络服务提供商

---

### 步骤5：测试不同的网络环境

**尝试**：
1. **使用移动网络**（手机热点）
2. **使用不同的WiFi网络**
3. **关闭VPN**（如果使用）
4. **使用不同的设备**（手机、平板）

**如果某个网络环境可以访问**：
- 说明是特定网络环境的问题
- 可能是公司/学校网络防火墙

---

## 可能的原因和解决方案

### 原因1：网络环境阻止域名访问

**可能的情况**：
- 公司/学校网络防火墙阻止某些域名
- ISP（网络服务提供商）阻止某些域名
- VPN连接影响域名解析

**解决方法**：
- 尝试使用移动网络（手机热点）
- 尝试关闭VPN
- 尝试不同的网络环境

---

### 原因2：DNS解析问题

**可能的情况**：
- 本地DNS缓存了错误的解析结果
- DNS服务器返回了错误的IP
- DNS传播未完成

**解决方法**：
```bash
# 清除DNS缓存
sudo dscacheutil -flushcache
sudo killall -HUP mDNSResponder

# 使用不同的DNS服务器
# 在系统设置中修改DNS服务器为8.8.8.8或1.1.1.1
```

---

### 原因3：SNI（Server Name Indication）问题

**可能的情况**：
- 某些客户端不支持SNI
- Nginx的SNI配置有问题

**解决方法**：
- 确保Nginx配置正确支持SNI
- 测试使用和不使用SNI的连接

---

### 原因4：中间设备阻止

**可能的情况**：
- 网络中间设备（代理、防火墙）在阻止HTTPS连接
- 某些安全软件在阻止连接

**解决方法**：
- 检查网络代理设置
- 检查安全软件设置
- 尝试不同的网络环境

---

## 快速测试方案

### 测试1：使用不同的DNS服务器

**在本地终端执行**：

```bash
# 使用Google DNS测试
dig @8.8.8.8 beatsync.site +short
curl -k https://beatsync.site/api/health --dns-servers 8.8.8.8

# 使用Cloudflare DNS测试
dig @1.1.1.1 beatsync.site +short
curl -k https://beatsync.site/api/health --dns-servers 1.1.1.1
```

---

### 测试2：使用手机热点

**操作**：
1. 打开手机热点
2. 电脑连接到手机热点
3. 尝试访问 `https://beatsync.site/api/health`

**如果手机热点可以访问**：
- 说明是当前网络环境的问题
- 需要检查网络设置或联系网络管理员

---

### 测试3：使用在线工具测试

**推荐工具**：
- **SSL Labs**：https://www.ssllabs.com/ssltest/analyze.html?d=beatsync.site
- **在线HTTPS测试**：https://www.sslshopper.com/ssl-checker.html
- **HTTP测试工具**：https://httpstatus.io/

**如果在线工具可以访问**：
- 说明服务是正常的
- 问题在本地网络环境

---

## 诊断命令（完整）

### 在本地终端执行完整诊断

```bash
echo "=== 1. 测试DNS解析（多个DNS服务器） ==="
for dns in 8.8.8.8 1.1.1.1 119.29.29.29; do
    echo "DNS服务器: $dns"
    dig @$dns beatsync.site +short
done

echo ""
echo "=== 2. 测试SNI（使用servername） ==="
echo | openssl s_client -connect beatsync.site:443 -servername beatsync.site 2>&1 | grep -E "(CONNECTED|Protocol|Cipher|Verify|CN)" | head -10

echo ""
echo "=== 3. 测试SNI（不使用servername） ==="
echo | openssl s_client -connect beatsync.site:443 2>&1 | grep -E "(CONNECTED|Protocol|Cipher|Verify|CN)" | head -10

echo ""
echo "=== 4. 测试HTTP访问 ==="
curl -v http://beatsync.site/api/health 2>&1 | head -15

echo ""
echo "=== 5. 测试HTTPS访问（详细模式） ==="
curl -v https://beatsync.site/api/health 2>&1 | head -30

echo ""
echo "=== 6. 测试IP地址访问 ==="
curl -k https://124.221.58.149/api/health -H "Host: beatsync.site"
```

---

## 如果所有方法都失败

### 可能的根本原因

1. **网络环境限制**：
   - 公司/学校网络可能阻止某些域名
   - 需要联系网络管理员

2. **ISP限制**：
   - 某些ISP可能阻止某些HTTPS连接
   - 需要联系ISP或尝试不同的网络

3. **地域限制**：
   - 某些地区可能无法访问
   - 需要测试不同地区的访问

---

## 验证清单

- [x] Nginx配置正确
- [x] 默认配置已禁用
- [x] 使用IP地址可以访问
- [ ] 测试SNI（使用和不使用servername）
- [ ] 测试多个DNS服务器
- [ ] 测试HTTP访问
- [ ] 测试不同的网络环境（手机热点）
- [ ] 使用在线工具测试
- [ ] 使用域名可以访问

---

## 相关文档

- `docs/deployment/FIX_NGINX_SERVER_NAME_ISSUE.md` - Nginx server_name问题
- `docs/deployment/FIX_DOMAIN_VS_IP_ACCESS.md` - 域名访问问题

---

**最后更新**：2025-12-04

