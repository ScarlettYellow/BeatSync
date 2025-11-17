# GitHub Pages无法打开的排查指南

## 问题描述

访问 `scarlettyellow.github.io/BeatSync/` 时，页面无法打开（显示空白或404错误）。

## 排查步骤

### 步骤1：检查GitHub Actions部署状态

1. **访问GitHub Actions页面**
   - 访问：https://github.com/ScarlettYellow/BeatSync/actions

2. **查看最新的部署工作流**
   - 找到 "Deploy to GitHub Pages" 工作流
   - 点击进入查看详情

3. **检查部署状态**
   - ✅ **绿色勾号**：部署成功，继续下一步
   - ❌ **红色叉号**：部署失败，查看错误日志
   - ⏳ **黄色圆圈**：正在部署，等待完成

4. **如果部署失败**
   - 点击失败的工作流
   - 查看错误日志
   - 常见错误：
     - 文件路径错误
     - 权限问题
     - 配置错误

### 步骤2：检查GitHub Pages设置

1. **访问Pages设置**
   - 访问：https://github.com/ScarlettYellow/BeatSync/settings/pages

2. **确认设置**
   - **Source**: 应该是 "GitHub Actions"
   - **Custom domain**: 应该为空
   - **Your site is live at**: 应该显示 `https://ScarlettYellow.github.io/BeatSync/`

3. **如果显示404或未部署**
   - 检查是否有部署成功的工作流
   - 如果没有，触发一次部署（见步骤3）

### 步骤3：手动触发部署

如果GitHub Actions没有自动触发，可以手动触发：

1. **方法1：推送一个空提交**
   ```bash
   git commit --allow-empty -m "trigger: 触发GitHub Pages部署"
   git push
   ```

2. **方法2：修改并提交前端文件**
   - 编辑 `web_service/frontend/index.html`（添加一个空格）
   - 提交并推送

3. **方法3：在GitHub Actions中手动运行**
   - 访问：https://github.com/ScarlettYellow/BeatSync/actions
   - 点击 "Deploy to GitHub Pages" 工作流
   - 点击 "Run workflow" 按钮
   - 选择分支（main）
   - 点击 "Run workflow"

### 步骤4：检查部署的文件

1. **访问部署的网站**
   - 访问：https://ScarlettYellow.github.io/BeatSync/
   - 打开浏览器开发者工具（F12）

2. **查看Network标签**
   - 刷新页面
   - 查看哪些文件加载失败
   - 查看HTTP状态码（200=成功，404=未找到）

3. **检查文件路径**
   - 确认 `index.html` 是否存在
   - 确认CSS和JS文件路径是否正确
   - 注意：GitHub Pages的路径是 `/BeatSync/`，不是根路径

### 步骤5：检查前端文件路径

GitHub Pages部署在 `/BeatSync/` 路径下，所以前端文件中的相对路径需要正确。

**检查 `index.html` 中的资源路径**：

```html
<!-- 如果使用相对路径，应该是： -->
<link rel="stylesheet" href="style.css">
<script src="script.js"></script>

<!-- 或者使用绝对路径： -->
<link rel="stylesheet" href="/BeatSync/style.css">
<script src="/BeatSync/script.js"></script>
```

### 步骤6：清除浏览器缓存（再次）

即使已经清除过，如果页面有更新，可能需要再次清除：

1. **硬刷新页面**
   - Mac: `Cmd+Shift+R`
   - Windows: `Ctrl+Shift+R`

2. **清除特定网站缓存**
   - 右键点击地址栏的锁图标
   - 选择"网站设置"
   - 点击"清除数据"

## 常见问题和解决方案

### 问题1：显示404 Not Found

**原因**：
- GitHub Pages还没有部署
- 部署失败
- 路径错误

**解决**：
1. 检查GitHub Actions部署状态
2. 确认Pages设置正确
3. 手动触发部署

### 问题2：显示空白页面

**原因**：
- JavaScript错误
- 资源文件加载失败
- API地址配置错误

**解决**：
1. 打开浏览器开发者工具（F12）
2. 查看Console标签，检查JavaScript错误
3. 查看Network标签，检查资源加载情况
4. 检查前端API地址配置

### 问题3：显示"Site not found"

**原因**：
- GitHub Pages未启用
- 仓库设置为私有（免费账户不支持私有仓库的Pages）

**解决**：
1. 确认仓库是公开的
2. 在Settings → Pages中启用Pages

### 问题4：CSS/JS文件404

**原因**：
- 文件路径不正确
- 文件未部署

**解决**：
1. 检查文件是否存在于 `web_service/frontend/` 目录
2. 检查GitHub Actions部署日志，确认文件已上传
3. 检查HTML中的文件路径

## 验证部署成功

### 方法1：检查GitHub Pages URL

访问：https://ScarlettYellow.github.io/BeatSync/

如果能看到页面内容，说明部署成功。

### 方法2：检查部署分支

1. 访问：https://github.com/ScarlettYellow/BeatSync/branches
2. 查看是否有 `gh-pages` 分支
3. 如果有，进入该分支，查看文件是否正确

### 方法3：使用curl测试

```bash
curl -I https://ScarlettYellow.github.io/BeatSync/
```

应该返回 `200 OK`，而不是 `404 Not Found`。

## 调试技巧

### 1. 查看浏览器控制台

打开浏览器开发者工具（F12），查看：
- **Console标签**：JavaScript错误
- **Network标签**：资源加载情况
- **Elements标签**：HTML结构

### 2. 查看GitHub Actions日志

1. 访问：https://github.com/ScarlettYellow/BeatSync/actions
2. 点击最新的工作流
3. 查看每个步骤的日志
4. 查找错误信息

### 3. 检查文件是否存在

访问以下URL，确认文件存在：
- https://ScarlettYellow.github.io/BeatSync/index.html
- https://ScarlettYellow.github.io/BeatSync/style.css
- https://ScarlettYellow.github.io/BeatSync/script.js

如果这些URL返回404，说明文件未正确部署。

## 快速修复步骤

如果页面无法打开，按以下顺序尝试：

1. ✅ **检查GitHub Actions部署状态**
2. ✅ **手动触发部署**（如果未自动触发）
3. ✅ **检查Pages设置**（Source应该是GitHub Actions）
4. ✅ **清除浏览器缓存并硬刷新**
5. ✅ **检查浏览器控制台错误**
6. ✅ **验证文件URL是否可访问**

## 需要帮助？

如果以上步骤都无法解决问题：

1. **提供以下信息**：
   - GitHub Actions部署日志
   - 浏览器控制台错误信息
   - 浏览器Network标签的截图

2. **检查GitHub Pages状态**：
   - 访问：https://github.com/ScarlettYellow/BeatSync/settings/pages
   - 查看"Your site is live at"显示的URL

3. **联系支持**：
   - GitHub支持：https://support.github.com

