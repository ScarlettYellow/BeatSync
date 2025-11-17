# 解决GitHub Pages重定向到Custom Domain的问题

## 问题描述

访问 `https://ScarlettYellow.github.io/BeatSync/` 时，浏览器自动重定向到 `http://beatsync.com/`，即使已经在GitHub Pages设置中删除了Custom Domain。

## 原因分析

### 1. 浏览器缓存（最可能）⭐
浏览器可能缓存了之前的重定向规则（HTTP 301/302重定向）。

### 2. GitHub Pages的CNAME文件
即使删除了Custom Domain设置，仓库中可能还存在 `CNAME` 文件，这个文件会告诉GitHub Pages使用哪个域名。

**检查结果**：本地仓库中没有发现CNAME文件，但可能存在于GitHub的部署分支中。

### 3. HSTS缓存
浏览器的HSTS（HTTP Strict Transport Security）缓存可能记住了之前的重定向规则。

### 4. DNS传播延迟
DNS记录的更新和传播需要时间（通常几分钟到几小时）。

## 解决方案（按优先级）

### 方案1：清除浏览器缓存和HSTS（最重要）⭐

#### 步骤1：清除浏览器缓存

**Chrome/Edge (Mac)**:
1. 按 `Cmd+Shift+Delete`
2. 选择"缓存的图片和文件"
3. 时间范围选择"全部时间"
4. 点击"清除数据"

**Chrome/Edge (Windows)**:
1. 按 `Ctrl+Shift+Delete`
2. 选择"缓存的图片和文件"
3. 时间范围选择"全部时间"
4. 点击"清除数据"

#### 步骤2：清除HSTS缓存（Chrome）

1. **访问HSTS设置页面**
   - 在地址栏输入：`chrome://net-internals/#hsts`
   - 或：`edge://net-internals/#hsts` (Edge)

2. **删除域名安全策略**
   - 在"Delete domain security policies"部分
   - 输入：`beatsync.com`
   - 点击"Delete"
   - 再输入：`ScarlettYellow.github.io`
   - 点击"Delete"

3. **清除HSTS缓存**
   - 在"Query HSTS/PKP domain"部分
   - 输入：`beatsync.com`
   - 查看是否有缓存记录
   - 如果有，使用上面的删除功能清除

#### 步骤3：使用隐私模式测试

1. 打开浏览器的隐私/无痕模式
   - Chrome: `Cmd+Shift+N` (Mac) 或 `Ctrl+Shift+N` (Windows)
   - Edge: `Cmd+Shift+N` (Mac) 或 `Ctrl+Shift+N` (Windows)

2. 访问：`https://ScarlettYellow.github.io/BeatSync/`

3. 查看是否还会重定向到 `beatsync.com`

4. **如果隐私模式下正常**，说明是浏览器缓存问题，继续清除缓存

5. **如果隐私模式下仍然重定向**，继续下面的方案

---

### 方案2：检查GitHub Pages部署分支

GitHub Actions部署可能会创建 `gh-pages` 分支，CNAME文件可能存在于那个分支中。

#### 检查步骤

1. **访问GitHub仓库分支页面**
   - 访问：https://github.com/ScarlettYellow/BeatSync/branches

2. **查看是否有gh-pages分支**
   - 如果有，点击进入该分支

3. **检查CNAME文件**
   - 在分支的根目录查看是否有 `CNAME` 文件
   - 或者在 `docs/` 目录中查看

4. **如果找到CNAME文件**
   - 点击文件，查看内容
   - 如果内容是 `beatsync.com`，删除该文件
   - 提交更改

#### 删除CNAME文件（如果存在）

**方法1：使用GitHub Web界面**
1. 进入gh-pages分支
2. 找到CNAME文件
3. 点击文件
4. 点击右上角的"Delete"按钮
5. 提交删除

**方法2：使用命令行**
```bash
# 切换到gh-pages分支
git checkout gh-pages

# 删除CNAME文件
git rm CNAME

# 提交更改
git commit -m "fix: 删除CNAME文件以移除custom domain重定向"

# 推送到远程
git push origin gh-pages

# 切换回main分支
git checkout main
```

---

### 方案3：强制重新部署GitHub Pages

1. **访问GitHub Pages设置**
   - 访问：https://github.com/ScarlettYellow/BeatSync/settings/pages

2. **临时禁用Pages**
   - 在"Source"部分，选择"None"
   - 点击"Save"
   - 等待几秒

3. **重新启用Pages**
   - 在"Source"部分，选择"GitHub Actions"
   - 点击"Save"
   - 这会触发重新部署

4. **等待部署完成**
   - 查看Actions标签，确认部署成功
   - 通常需要1-2分钟

5. **测试访问**
   - 使用隐私模式访问：`https://ScarlettYellow.github.io/BeatSync/`
   - 确认不再重定向

---

### 方案4：等待DNS传播

如果以上方法都不行，可能是DNS传播延迟：

1. **等待15-30分钟**
   - DNS和GitHub Pages配置更新需要时间
   - 可以等待一段时间后重试

2. **使用不同网络测试**
   - 使用手机热点
   - 或使用VPN
   - 看是否还会重定向

---

## 验证步骤

完成上述步骤后，验证是否解决：

### 1. 使用隐私模式访问

```
https://ScarlettYellow.github.io/BeatSync/
```

### 2. 检查是否重定向

- 打开浏览器开发者工具（F12）
- 查看Network标签
- 访问网站，查看是否有301/302重定向
- 查看最终URL是什么

### 3. 检查最终URL

- 确认浏览器地址栏显示的是GitHub Pages URL
- 而不是 `beatsync.com`

### 4. 测试功能

- 尝试上传文件
- 确认API请求能正常发送到Render后端
- 确认没有CORS错误

---

## 如果问题仍然存在

### 检查GitHub Pages设置

1. 访问：https://github.com/ScarlettYellow/BeatSync/settings/pages
2. 确认以下设置：
   - **Source**: GitHub Actions（或你选择的部署方式）
   - **Custom domain**: 应该为空或显示"Remove"
   - **Enforce HTTPS**: 可以勾选（如果可用）

### 检查GitHub Actions部署

1. 访问：https://github.com/ScarlettYellow/BeatSync/actions
2. 查看最新的"Deploy to GitHub Pages"工作流
3. 确认部署成功
4. 查看部署日志，确认没有错误

### 联系GitHub支持

如果以上方法都不行，可能是GitHub的配置问题：

1. 访问：https://support.github.com
2. 提交支持请求
3. 说明问题：删除Custom Domain后仍然重定向

---

## 关于beatsync.com域名

从搜索结果看，`beatsync.com` 这个域名确实存在，并且有另一个网站（显示"网站正在建设中"）。

**重要提示**：
- 如果你不拥有 `beatsync.com` 这个域名，不应该在GitHub Pages中设置它
- 这可能导致DNS冲突和重定向问题
- 建议使用GitHub提供的免费域名：`ScarlettYellow.github.io/BeatSync/`

---

## 预防措施

为了避免将来出现类似问题：

1. **不要手动创建CNAME文件**，除非你真的要使用Custom Domain
2. **使用GitHub Pages设置界面**来管理Custom Domain，而不是手动编辑文件
3. **删除Custom Domain时**，确保同时检查并删除所有CNAME文件（包括gh-pages分支中的）
4. **清除浏览器缓存**，避免缓存旧的重定向规则

---

## 快速检查清单

- [ ] 已清除浏览器缓存
- [ ] 已清除HSTS缓存
- [ ] 已在隐私模式下测试
- [ ] 已检查gh-pages分支是否有CNAME文件
- [ ] 已强制重新部署GitHub Pages
- [ ] 已等待DNS传播（15-30分钟）
- [ ] 已在隐私模式下验证不再重定向
