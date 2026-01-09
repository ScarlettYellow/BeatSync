# GitHub Pages HTTPS设置

> **问题**：GitHub Pages页面显示"Not Secure"（不安全）标志

---

## 问题分析

**可能原因**：
1. **GitHub Pages未强制HTTPS**：虽然GitHub Pages默认使用HTTPS，但可能未启用强制
2. **混合内容**：页面中加载了HTTP资源
3. **自签名证书警告**：后端使用自签名证书，浏览器可能显示警告

---

## 解决方案

### 方案1：在GitHub仓库中启用HTTPS强制（推荐）

**步骤**：
1. 进入GitHub仓库：https://github.com/scarlettyellow/BeatSync
2. 点击 **Settings**（设置）
3. 在左侧菜单中找到 **Pages**（页面）
4. 找到 **"Enforce HTTPS"**（强制HTTPS）选项
5. 确保该选项已启用（勾选）

**如果选项不可用**：
- 可能需要等待几分钟让GitHub Pages完全部署
- 或者先访问一次HTTP版本，然后GitHub会自动启用HTTPS

### 方案2：检查是否有HTTP资源

**检查方法**：
1. 按F12打开开发者工具
2. 切换到 **Console** 标签
3. 查看是否有Mixed Content警告
4. 切换到 **Network** 标签
5. 检查所有请求，确保都是HTTPS

### 方案3：使用相对路径

确保所有资源使用相对路径或HTTPS：
```html
<!-- ✅ 正确：相对路径 -->
<link rel="stylesheet" href="style.css">
<script src="script.js"></script>

<!-- ✅ 正确：HTTPS -->
<link rel="stylesheet" href="https://example.com/style.css">

<!-- ❌ 错误：HTTP -->
<link rel="stylesheet" href="http://example.com/style.css">
```

---

## 验证步骤

### 1. 检查GitHub Pages设置

1. 进入仓库 Settings → Pages
2. 确认 "Enforce HTTPS" 已启用
3. 如果未启用，点击启用

### 2. 检查浏览器控制台

1. 按F12打开开发者工具
2. 查看Console标签
3. 不应该有Mixed Content警告

### 3. 检查地址栏

修复后，地址栏应该显示：
- ✅ 🔒（锁图标）表示安全
- ❌ "Not Secure" 表示不安全

---

## 常见问题

### 问题1：GitHub Pages显示"Not Secure"

**原因**：GitHub Pages未强制HTTPS

**解决**：
1. 进入仓库 Settings → Pages
2. 启用 "Enforce HTTPS"

### 问题2：后端API导致警告

**原因**：后端使用自签名证书

**解决**：
- 这是正常的，浏览器会显示警告
- 用户需要点击"高级" → "继续访问"
- 或者使用Let's Encrypt证书（需要域名）

### 问题3：预览页面显示"Not Secure"

**原因**：预览页面在GitHub Pages上，但加载了HTTP资源

**解决**：
- 确保预览页面中的视频URL使用HTTPS
- 确保所有资源使用HTTPS或相对路径

---

## 快速检查清单

- [ ] GitHub Pages Settings → Pages → "Enforce HTTPS" 已启用
- [ ] 所有API调用使用HTTPS
- [ ] 所有资源使用HTTPS或相对路径
- [ ] 浏览器控制台没有Mixed Content警告
- [ ] 地址栏显示🔒（锁图标）

---

**最后更新**：2025-12-01












