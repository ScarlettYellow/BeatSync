# 修复DNSPod域名拦截问题

> **问题**：HTTP访问被重定向到 `dnspod.qcloud.com/static/webblock.html?d=beatsync.site`  
> **原因**：腾讯云DNSPod的安全策略在拦截域名访问  
> **解决**：在DNSPod控制台检查并关闭域名拦截功能

---

## 问题分析

### 关键发现

从诊断结果看到：
- ✅ **DNS解析正常**：`beatsync.site` → `124.221.58.149`
- ✅ **SNI测试成功**：TLSv1.3连接成功
- ❌ **HTTP访问被拦截**：返回302重定向到 `dnspod.qcloud.com/static/webblock.html?d=beatsync.site`
- ❌ **HTTPS访问失败**：`Connection reset by peer`

### 根本原因

**腾讯云DNSPod的安全策略在拦截域名访问**！

从HTTP响应看到：
```
< HTTP/1.1 302 OK
< Location: https://dnspod.qcloud.com/static/webblock.html?d=beatsync.site
```

这说明DNSPod认为域名存在安全风险，自动拦截了访问。

---

## 解决方案

### 步骤1：进入DNSPod控制台

**操作步骤**：

1. **登录腾讯云控制台**
   - 访问：https://console.cloud.tencent.com/

2. **进入DNSPod控制台**
   - 控制台 → DNSPod → 权威解析

3. **选择域名**
   - 找到域名：`beatsync.site`
   - 点击域名进入详情页

---

### 步骤2：检查DNS安全设置

**在DNSPod控制台中查找**：

1. **DNS安全**或**安全设置**标签
2. **域名拦截**或**Web拦截**功能
3. **安全策略**或**防护规则**

**需要检查的设置**：
- **域名拦截**：是否启用
- **Web拦截**：是否启用
- **安全策略**：是否有拦截规则
- **白名单**：是否需要添加IP到白名单

---

### 步骤3：关闭域名拦截功能

**如果找到拦截设置**：

1. **关闭域名拦截**
   - 找到"域名拦截"或"Web拦截"开关
   - 关闭该功能

2. **检查拦截规则**
   - 查看是否有拦截规则
   - 删除或禁用拦截规则

3. **添加白名单**（如果需要）
   - 将服务器IP `124.221.58.149` 添加到白名单
   - 将域名 `beatsync.site` 添加到白名单

---

### 步骤4：检查DNS解析设置

**在DNSPod控制台中检查**：

1. **记录管理**
   - 确认A记录存在：`@` → `124.221.58.149`
   - 确认记录状态为"启用"

2. **解析设置**
   - 检查是否有安全策略
   - 检查是否有拦截规则

---

## 详细操作步骤

### 方法1：通过DNSPod控制台

1. **进入DNSPod控制台**
   - https://console.cloud.tencent.com/dns

2. **选择域名**
   - 点击域名 `beatsync.site`

3. **查找安全设置**
   - 在域名详情页查找"DNS安全"、"安全设置"、"域名拦截"等标签
   - 或在"解析设置"中查找安全相关选项

4. **关闭拦截功能**
   - 找到拦截开关，关闭它
   - 保存设置

---

### 方法2：通过轻量服务器控制台

1. **进入轻量应用服务器控制台**
   - 找到服务器实例

2. **查找域名管理**
   - 在服务器详情页查找"域名"或"DNS"相关设置
   - 检查是否有拦截或安全策略

---

## 验证步骤

### 步骤1：等待设置生效

**通常时间**：
- **最快**：几分钟
- **一般**：几小时
- **最长**：24小时

---

### 步骤2：测试HTTP访问

**在本地终端执行**：
```bash
# 测试HTTP访问（应该重定向到HTTPS，而不是拦截页面）
curl -I http://beatsync.site/api/health
```

**预期结果**：
```
HTTP/1.1 301 Moved Permanently
Location: https://beatsync.site/api/health
```

**不应该看到**：
```
Location: https://dnspod.qcloud.com/static/webblock.html?d=beatsync.site
```

---

### 步骤3：测试HTTPS访问

**在本地终端执行**：
```bash
# 测试HTTPS访问
curl -k https://beatsync.site/api/health
```

**预期结果**：
```json
{"status":"healthy","timestamp":"..."}
```

---

## 如果找不到拦截设置

### 可能的位置

1. **DNSPod控制台**：
   - DNS安全 → 域名拦截
   - 安全设置 → Web拦截
   - 解析设置 → 安全策略

2. **轻量服务器控制台**：
   - 域名管理 → 安全设置
   - 防火墙 → DNS拦截

3. **腾讯云安全中心**：
   - 安全中心 → DNS安全
   - 安全中心 → 域名拦截

---

## 临时解决方案

### 如果无法立即关闭拦截

**可以尝试**：
1. **联系腾讯云技术支持**：请求关闭域名拦截
2. **使用IP地址访问**：临时使用IP地址（但这不是长期方案）
3. **检查域名备案**：某些拦截可能与备案状态有关

---

## 验证清单

- [ ] 进入DNSPod控制台
- [ ] 找到域名拦截或安全设置
- [ ] 关闭域名拦截功能
- [ ] 等待设置生效
- [ ] 测试HTTP访问（不再重定向到拦截页面）
- [ ] 测试HTTPS访问（可以正常访问）
- [ ] 浏览器可以访问域名

---

## 相关文档

- `docs/deployment/DEEP_DIAGNOSIS_DOMAIN_ACCESS.md` - 深度诊断域名访问问题
- `docs/deployment/FIX_DOMAIN_VS_IP_ACCESS.md` - 域名访问问题

---

**最后更新**：2025-12-04

