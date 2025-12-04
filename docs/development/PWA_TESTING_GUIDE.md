# PWA功能测试指南

> **目标**：验证PWA功能是否正常工作，包括添加到主屏幕、Service Worker缓存等

---

## 测试环境

### 浏览器支持

- ✅ **Chrome/Edge（桌面）**：完全支持
- ✅ **Chrome（Android）**：完全支持
- ✅ **Safari（iOS 11.3+）**：支持添加到主屏幕（Service Worker支持有限）
- ✅ **Firefox**：支持
- ⚠️ **微信内置浏览器**：部分支持（可能不支持Service Worker）

---

## 测试步骤

### 1. 验证Manifest文件

**访问**：
```
https://scarlettyellow.github.io/BeatSync/manifest.json
```

**预期结果**：
- 返回JSON格式的manifest内容
- 包含name、short_name、icons等字段

---

### 2. 验证Service Worker注册

**在浏览器控制台检查**：

1. 打开开发者工具（F12）
2. 切换到"Application"标签（Chrome）或"存储"标签（Firefox）
3. 查看"Service Workers"部分

**预期结果**：
- Service Worker状态为"activated"
- Scope为`/BeatSync/`
- 控制台显示：`[PWA] Service Worker注册成功`

---

### 3. 测试添加到主屏幕（桌面Chrome）

**步骤**：
1. 访问：`https://scarlettyellow.github.io/BeatSync/`
2. 点击地址栏右侧的"安装"图标（或菜单中的"安装BeatSync"）
3. 确认安装

**预期结果**：
- 应用以独立窗口打开
- 没有浏览器地址栏
- 图标显示在桌面/开始菜单

---

### 4. 测试添加到主屏幕（Android Chrome）

**步骤**：
1. 访问：`https://scarlettyellow.github.io/BeatSync/`
2. 点击浏览器菜单（三个点）
3. 选择"添加到主屏幕"或"安装应用"
4. 确认安装

**预期结果**：
- 应用图标出现在主屏幕
- 点击图标以独立窗口打开应用
- 没有浏览器地址栏

---

### 5. 测试添加到主屏幕（iOS Safari）

**步骤**：
1. 访问：`https://scarlettyellow.github.io/BeatSync/`
2. 点击分享按钮（方框+箭头）
3. 选择"添加到主屏幕"
4. 确认添加

**预期结果**：
- 应用图标出现在主屏幕
- 点击图标以全屏模式打开应用
- 没有浏览器地址栏和底部工具栏

---

### 6. 测试Service Worker缓存

**步骤**：
1. 打开开发者工具 → Network标签
2. 刷新页面
3. 查看资源加载情况

**预期结果**：
- 静态资源（HTML、CSS、JS）从Service Worker缓存加载
- 显示"ServiceWorker"或"disk cache"
- API请求仍然从网络加载（网络优先策略）

---

### 7. 测试离线功能（可选）

**步骤**：
1. 正常访问页面，确保资源已缓存
2. 断开网络（或使用开发者工具的"Offline"模式）
3. 刷新页面

**预期结果**：
- 页面仍然可以加载（从缓存）
- 静态资源正常显示
- API请求失败（预期行为，因为需要实时数据）

---

### 8. 测试更新机制

**步骤**：
1. 修改Service Worker文件（更改CACHE_NAME版本号）
2. 重新部署
3. 访问页面

**预期结果**：
- 新Service Worker自动安装
- 旧缓存自动清除
- 控制台显示更新日志

---

## 常见问题排查

### 问题1：无法添加到主屏幕

**可能原因**：
- Manifest文件路径错误
- Manifest文件格式错误
- 未使用HTTPS（PWA要求HTTPS）

**解决方法**：
- 检查manifest.json是否可访问
- 验证JSON格式是否正确
- 确认使用HTTPS访问

---

### 问题2：Service Worker未注册

**可能原因**：
- Service Worker文件路径错误
- 未使用HTTPS（本地开发除外）
- 浏览器不支持Service Worker

**解决方法**：
- 检查sw.js是否可访问
- 查看浏览器控制台错误信息
- 确认浏览器版本支持Service Worker

---

### 问题3：图标显示不正确

**可能原因**：
- 图标文件路径错误
- 图标尺寸不符合要求
- 浏览器缓存未更新

**解决方法**：
- 检查favicon.svg和favicon.ico是否存在
- 验证图标文件可访问
- 清除浏览器缓存后重试

---

### 问题4：独立窗口模式不正常

**可能原因**：
- Manifest配置错误
- 浏览器不支持standalone模式

**解决方法**：
- 检查manifest.json中的display设置
- 确认浏览器版本支持standalone模式

---

## 验证清单

- [ ] Manifest文件可访问且格式正确
- [ ] Service Worker成功注册并激活
- [ ] 可以添加到主屏幕（桌面）
- [ ] 可以添加到主屏幕（Android）
- [ ] 可以添加到主屏幕（iOS）
- [ ] 独立窗口模式正常
- [ ] 图标显示正确
- [ ] Service Worker缓存正常工作
- [ ] API请求使用网络优先策略
- [ ] 更新机制正常工作

---

## 测试工具

### Chrome DevTools

1. **Application标签**：
   - Service Workers：查看Service Worker状态
   - Manifest：查看Manifest配置
   - Cache Storage：查看缓存内容

2. **Network标签**：
   - 查看资源加载来源（Service Worker/Network）
   - 测试离线模式

3. **Lighthouse**：
   - 运行PWA审计
   - 检查PWA最佳实践

---

### 在线工具

- **PWA Builder**：https://www.pwabuilder.com/
- **Lighthouse CI**：https://github.com/GoogleChrome/lighthouse-ci

---

**最后更新**：2025-12-03

