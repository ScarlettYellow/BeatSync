# GitHub Pages无法打开的快速修复

## 问题现象

访问 `scarlettyellow.github.io/BeatSync/` 时，页面无法打开（显示空白或Google新标签页）。

## 快速修复步骤

### 步骤1：检查GitHub Actions部署状态

1. **访问Actions页面**
   - https://github.com/ScarlettYellow/BeatSync/actions

2. **查看部署状态**
   - 找到 "Deploy to GitHub Pages" 工作流
   - 如果显示 ❌ 失败，点击查看错误日志
   - 如果显示 ⏳ 进行中，等待完成
   - 如果显示 ✅ 成功，继续步骤2

### 步骤2：手动触发部署（如果未自动触发）

如果GitHub Actions没有自动运行，手动触发：

1. **访问Actions页面**
   - https://github.com/ScarlettYellow/BeatSync/actions

2. **点击"Deploy to GitHub Pages"工作流**

3. **点击"Run workflow"按钮**

4. **选择分支**：`main`

5. **点击"Run workflow"**

6. **等待部署完成**（约1-2分钟）

### 步骤3：检查Pages设置

1. **访问Pages设置**
   - https://github.com/ScarlettYellow/BeatSync/settings/pages

2. **确认设置**
   - **Source**: 应该是 "GitHub Actions"
   - **Your site is live at**: 应该显示 `https://ScarlettYellow.github.io/BeatSync/`

3. **如果Source不是"GitHub Actions"**
   - 选择 "GitHub Actions"
   - 点击 "Save"

### 步骤4：验证部署

1. **等待2-3分钟**（让部署完成）

2. **访问网站**
   - https://ScarlettYellow.github.io/BeatSync/

3. **如果仍然无法打开**
   - 打开浏览器开发者工具（F12）
   - 查看Console标签的错误信息
   - 查看Network标签，看哪些文件加载失败

## 常见问题

### 问题1：Actions显示"Workflow run not found"

**原因**：GitHub Actions可能还没有运行过

**解决**：手动触发部署（见步骤2）

### 问题2：部署失败，显示权限错误

**原因**：GitHub Actions权限不足

**解决**：
1. 访问：https://github.com/ScarlettYellow/BeatSync/settings/actions
2. 在"Workflow permissions"部分
3. 选择 "Read and write permissions"
4. 点击 "Save"

### 问题3：页面显示404

**原因**：部署还未完成或失败

**解决**：
1. 检查GitHub Actions部署状态
2. 等待部署完成
3. 清除浏览器缓存并硬刷新（Cmd+Shift+R）

## 验证清单

- [ ] GitHub Actions部署成功（绿色勾号）
- [ ] Pages设置中Source是"GitHub Actions"
- [ ] "Your site is live at"显示正确的URL
- [ ] 等待2-3分钟让部署完成
- [ ] 清除浏览器缓存并硬刷新
- [ ] 使用隐私模式测试

## 如果仍然无法打开

请提供以下信息：

1. **GitHub Actions状态**：成功/失败/进行中
2. **浏览器控制台错误**：F12 → Console标签的错误信息
3. **Network标签**：哪些文件返回404或其他错误
4. **直接访问文件**：https://ScarlettYellow.github.io/BeatSync/index.html 是否能打开

