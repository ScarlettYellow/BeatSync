# 临时使用IP地址方案

> **原因**：域名备案审核中，域名被拦截  
> **方案**：临时使用IP地址访问，备案通过后改回域名  
> **状态**：已实施，等待备案通过后恢复

---

## 当前状态

### 域名备案

- **域名**：`beatsync.site`
- **备案状态**：审核中
- **备案订单号**：30176484158027072
- **预计时间**：1-20个工作日

### 临时方案

- **前端API地址**：临时使用 `https://124.221.58.149`
- **原因**：域名备案审核期间被拦截
- **状态**：已实施

---

## 已实施的修改

### 前端代码修改

**文件**：`web_service/frontend/script.js`

**修改内容**：
```javascript
// 临时方案：使用IP地址（域名备案审核中，备案通过后改回域名）
const backendUrl = window.API_BASE_URL || 'https://124.221.58.149';
```

**说明**：
- 临时使用IP地址 `124.221.58.149`
- 添加了注释说明这是临时方案
- 备案通过后需要改回域名

---

## 注意事项

### 1. 浏览器证书警告

**问题**：
- 浏览器会显示证书警告（因为SSL证书是域名证书，不是IP证书）
- 用户需要手动接受证书警告

**解决方法**：
- 用户首次访问时需要点击"高级" → "继续访问"
- 这是临时方案，备案通过后改回域名即可解决

---

### 2. 功能限制

**当前限制**：
- 浏览器可能显示"不安全"警告
- 某些浏览器可能阻止访问
- 用户体验可能受影响

**解决方法**：
- 这是临时方案
- 备案通过后改回域名即可解决

---

## 备案通过后的操作

### 步骤1：验证域名可以访问

**在备案通过后**：

1. **测试域名访问**：
```bash
# 测试HTTP访问（应该重定向到HTTPS，不再被拦截）
curl -I http://beatsync.site/api/health

# 测试HTTPS访问
curl -k https://beatsync.site/api/health
```

**预期结果**：
- HTTP返回301重定向到HTTPS（不再重定向到拦截页面）
- HTTPS可以正常访问

---

### 步骤2：恢复域名配置

**修改前端代码**：

**文件**：`web_service/frontend/script.js`

**恢复为域名**：
```javascript
// 生产环境：使用腾讯云服务器（HTTPS）
// 域名：beatsync.site（通过Nginx反向代理，端口443，Let's Encrypt证书）
const backendUrl = window.API_BASE_URL || 'https://beatsync.site';
console.log('🟢 生产环境检测（腾讯云服务器 - HTTPS - beatsync.site）');
console.log('   访问地址:', window.location.href);
console.log('   后端URL:', backendUrl);
return backendUrl;
```

---

### 步骤3：提交并部署

```bash
cd /Users/scarlett/Projects/BeatSync
git add web_service/frontend/script.js
git commit -m "fix: 恢复使用域名beatsync.site（备案已通过）"
git push origin main
```

---

## 验证清单

### 当前状态

- [x] 临时方案已实施（使用IP地址）
- [x] 前端代码已修改
- [ ] 备案审核通过
- [ ] 域名可以正常访问
- [ ] 恢复域名配置
- [ ] 测试域名访问
- [ ] 提交并部署

---

## 备案进度跟踪

### 备案步骤

1. ✅ **提交初审**：已提交
2. ⏳ **腾讯云审核**：审核中（1-2个工作日）
3. ⏳ **待提交管局**：24小时
4. ⏳ **工信部短信核验**：24小时内核验
5. ⏳ **管局审核**：1-20个工作日

### 预计时间

- **最快**：约1周
- **一般**：2-3周
- **最长**：约1个月

---

## 相关文档

- `docs/deployment/FIX_DNSPOD_WEB_BLOCK_ALTERNATIVE.md` - DNSPod拦截问题替代方案
- `docs/deployment/FIX_DOMAIN_VS_IP_ACCESS.md` - 域名访问问题

---

**最后更新**：2025-12-04

