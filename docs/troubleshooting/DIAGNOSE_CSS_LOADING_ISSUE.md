# CSS 加载问题诊断和修复

> **问题**：更新域名后，App UI 样式丢失，CSS 文件无法正确加载  
> **原因**：`capacitor://localhost` 协议下，外部 CSS 文件可能无法正确加载  
> **解决**：诊断并修复 CSS 加载问题，而不是重写 CSS

---

## 问题分析

### 当前状况

1. **之前（使用 `server.url`）**：
   - App 从远程服务器（`https://beatsync.site`）加载前端
   - CSS 文件通过 HTTP/HTTPS 正常加载

2. **现在（移除 `server.url`）**：
   - App 从本地 bundle 加载前端（`web_service/frontend`）
   - CSS 文件通过 `capacitor://localhost` 协议加载
   - **CSS 文件存在，但样式没有应用**

### 可能的原因

1. **MIME Type 问题**：`capacitor://localhost` 可能无法正确识别 CSS 文件的 MIME type
2. **CORS/安全策略**：虽然本地文件不受 CORS 限制，但可能有其他安全策略
3. **文件路径问题**：相对路径在 `capacitor://` 协议下解析不正确
4. **缓存问题**：WebView 缓存了旧的空样式
5. **Capacitor 配置问题**：需要额外的配置来支持本地资源加载

---

## 诊断步骤

### 步骤 1：检查 CSS 文件是否真的加载了

在 Safari Web Inspector Console 中执行：

```javascript
// 检查所有样式表
Array.from(document.styleSheets).forEach((sheet, index) => {
  try {
    console.log(`样式表 ${index}:`, sheet.href, sheet.cssRules ? `${sheet.cssRules.length} 条规则` : 'ERROR');
  } catch(e) {
    console.log(`样式表 ${index}:`, sheet.href, 'CORS 错误:', e.message);
  }
});

// 检查 style.css 是否在列表中
const styleSheet = Array.from(document.styleSheets).find(s => s.href && s.href.includes('style.css'));
console.log('style.css 样式表:', styleSheet);
if (styleSheet) {
  try {
    console.log('规则数量:', styleSheet.cssRules.length);
    console.log('第一条规则:', styleSheet.cssRules[0]);
  } catch(e) {
    console.error('无法访问规则:', e);
  }
}
```

**预期结果**：
- 如果 CSS 加载成功：应该看到 `style.css` 和规则数量 > 0
- 如果 CSS 加载失败：会看到错误或规则数量为 0

### 步骤 2：检查 Network 中的 CSS 文件

在 Safari Web Inspector **Network** 标签中：
1. 找到 `style.css?v=20251242` 请求
2. 检查：
   - **Status**：应该是 `200`
   - **Type**：应该是 `text/css`
   - **Size**：应该 > 0
   - **Response Headers**：应该有 `Content-Type: text/css`

### 步骤 3：检查文件是否真的存在

在服务器上（或本地）验证：

```bash
# 检查文件是否存在
ls -lh /Users/scarlett/Projects/BeatSync/web_service/frontend/style.css

# 检查 iOS bundle 中的文件
ls -lh ios/App/App/public/style.css

# 检查文件内容
head -20 ios/App/App/public/style.css
```

### 步骤 4：尝试直接访问 CSS 文件

在 App 中打开 Web Inspector，在 Console 中执行：

```javascript
// 尝试直接加载 CSS
fetch('capacitor://localhost/style.css?v=20251242')
  .then(r => r.text())
  .then(css => console.log('CSS 内容（前100字符）:', css.substring(0, 100)))
  .catch(e => console.error('加载失败:', e));
```

---

## 解决方案

### 方案 1：修复 MIME Type（如果问题在此）

如果 CSS 文件加载但样式没有应用，可能是 MIME type 问题。

**在 iOS 项目中添加 MIME type 支持**：

需要在 `AppDelegate.swift` 或 `ViewController.swift` 中配置：

```swift
// AppDelegate.swift 或 ViewController.swift
import WebKit

// 在 viewDidLoad 或 application:didFinishLaunchingWithOptions 中添加
if let webView = bridge?.webView {
    let config = webView.configuration
    // 确保 CSS 文件正确识别
    // 注意：Capacitor 通常会自动处理，但可能需要检查配置
}
```

或者检查 `WKWebView` 配置是否正确加载了本地资源。

### 方案 2：使用内联 CSS（临时方案，当前使用）

**优点**：立即生效，不依赖外部文件加载  
**缺点**：CSS 和 JS 耦合，维护困难

**当前实现**：已在 `script.js` 的 `app-specific-styles` 中注入完整 CSS。

### 方案 3：使用 Base64 编码内联（推荐）

将 CSS 文件内容转换为 Base64，然后内联到 HTML：

```bash
# 生成 Base64 编码的 CSS
base64 -i web_service/frontend/style.css | tr -d '\n' > style.css.base64
```

然后在 `index.html` 中：

```html
<style>
  /* 通过 JavaScript 动态加载 Base64 编码的 CSS */
</style>
<script>
  // 解码并注入 CSS
  const cssBase64 = '...'; // Base64 编码的 CSS
  const css = atob(cssBase64);
  const style = document.createElement('style');
  style.textContent = css;
  document.head.appendChild(style);
</script>
```

**优点**：
- 不依赖外部文件加载
- 样式集中在一个文件
- 避免协议问题

**缺点**：
- HTML 文件变大
- 需要更新 Base64 编码

### 方案 4：修复 Capacitor 本地资源加载（根本解决）

检查 Capacitor 版本和配置：

```bash
# 检查 Capacitor 版本
npm list @capacitor/core @capacitor/ios

# 检查是否有更新
npm outdated @capacitor/core @capacitor/ios
```

**可能需要的配置**：

在 `Info.plist` 中添加：

```xml
<key>WKAppBoundDomains</key>
<array>
    <string>localhost</string>
</array>
```

或者检查 `AppDelegate.swift` 中是否正确配置了本地资源加载。

---

## 推荐的解决流程

### 短期（立即修复）

1. ✅ **使用内联 CSS**（当前方案）
   - 已经在 `script.js` 中注入完整 CSS
   - 确保样式正确应用

### 中期（1-2 周内）

2. **诊断根本原因**
   - 执行上述诊断步骤
   - 确定是 MIME type、路径、还是配置问题

3. **根据诊断结果修复**
   - 如果是 MIME type：添加配置
   - 如果是路径：修复路径引用
   - 如果是配置：更新 Capacitor 配置

### 长期（永久解决）

4. **恢复使用外部 CSS 文件**
   - 移除内联 CSS 代码
   - 确保外部 CSS 文件正确加载
   - 测试并验证

---

## 验证修复

修复后，验证步骤：

1. **检查样式表加载**：
   ```javascript
   Array.from(document.styleSheets).find(s => s.href && s.href.includes('style.css'))
   ```

2. **检查样式应用**：
   ```javascript
   getComputedStyle(document.querySelector('.upload-btn')).backgroundColor
   // 应该返回: "rgb(0, 122, 255)"
   ```

3. **UI 测试**：
   - 按钮应该是蓝色
   - 上传区域应该有虚线边框
   - 背景应该是灰色
   - 字体大小和间距应该正确

---

## 当前状态

- ✅ **临时方案**：使用内联 CSS，样式已正确应用
- ⏳ **待诊断**：根本原因（需要执行诊断步骤）
- ⏳ **待修复**：根据诊断结果修复 CSS 加载问题
- ⏳ **待恢复**：移除内联 CSS，恢复外部 CSS 文件

---

**最后更新**：2025-12-18  
**当前方案**：内联 CSS（临时）  
**下一步**：执行诊断步骤，确定根本原因








