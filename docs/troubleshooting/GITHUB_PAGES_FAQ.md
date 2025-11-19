# GitHub Pages 常见问题解答

## 问题1：Custom Domain 是什么？为什么设置失败？

### Custom Domain 的作用

**Custom Domain（自定义域名）**允许你使用自己的域名（如 `beatsync.com`）来访问GitHub Pages网站，而不是使用GitHub提供的默认域名（如 `ScarlettYellow.github.io`）。

### 为什么设置失败？

从你的截图看，你设置了 `beatsync.com`，但显示 "DNS check unsuccessful"（DNS检查失败）。

**失败原因**：
1. **域名所有权**：你需要拥有 `beatsync.com` 这个域名
2. **DNS配置**：需要在域名DNS中添加CNAME或A记录指向GitHub Pages
3. **DNS传播**：DNS记录生效需要时间（通常几分钟到几小时）

### 应该设置什么？

#### ✅ 如果你没有自己的域名（推荐）

**不需要设置Custom Domain**，直接使用GitHub提供的免费域名即可：

- **格式**：`https://ScarlettYellow.github.io/BeatSync/`
- **如何获取**：在GitHub仓库的Settings → Pages中查看
- **优点**：免费、无需配置、自动HTTPS

**操作步骤**：
1. 在GitHub Pages设置中，找到"Custom domain"部分
2. 点击"Remove"按钮，删除custom domain设置
3. 使用默认的GitHub Pages域名即可

#### ✅ 如果你有自己的域名

**需要完成以下步骤**：

1. **在域名DNS中添加记录**
   - 添加CNAME记录：
     - **名称**：`@` 或 `www`
     - **值**：`ScarlettYellow.github.io`
   - 或者添加A记录（指向GitHub IP）：
     - GitHub Pages IP地址：`185.199.108.153`, `185.199.109.153`, `185.199.110.153`, `185.199.111.153`

2. **在GitHub Pages中设置**
   - 在"Custom domain"输入框中输入你的域名（如 `beatsync.com`）
   - 点击"Save"
   - 等待DNS检查通过（可能需要几分钟）

3. **启用HTTPS**
   - DNS检查通过后，GitHub会自动为你的域名配置HTTPS证书
   - 勾选"Enforce HTTPS"选项

### 建议

**对于当前项目，建议不设置Custom Domain**，因为：
- 免费且简单
- 无需额外配置
- 自动HTTPS
- 适合演示和个人项目

---

## 问题2：后端环境变量值是否正确？

### 当前值

```
https://ScarlettYellow.github.io,http://localhost:8000
```

### 问题分析

**这个值不完整**，缺少了仓库路径。

GitHub Pages的URL格式是：
```
https://用户名.github.io/仓库名/
```

### 正确的值应该是

根据你的仓库名 `BeatSync`，正确的值应该是：

```
https://ScarlettYellow.github.io/BeatSync/,http://localhost:8000
```

**重要注意事项**：
1. **末尾的斜杠 `/` 很重要**，必须包含
2. **仓库名大小写要匹配**（`BeatSync`）
3. **多个域名用逗号分隔**，不要有空格

### 如何确认正确的URL

1. **访问你的GitHub Pages网站**
   - 在浏览器中访问：`https://ScarlettYellow.github.io/BeatSync/`
   - 如果能正常访问，说明URL正确

2. **查看GitHub Pages设置**
   - 在GitHub仓库的Settings → Pages中
   - 查看"Your site is live at"显示的URL
   - 使用那个完整的URL

3. **检查浏览器地址栏**
   - 访问网站后，查看浏览器地址栏显示的完整URL
   - 使用那个URL作为CORS允许的来源

### 特殊情况

如果你的GitHub Pages是部署在**用户/组织的主仓库**（仓库名是 `ScarlettYellow.github.io`），那么URL格式是：
```
https://ScarlettYellow.github.io/
```
（没有仓库名路径）

但根据你的仓库名是 `BeatSync`，应该使用：
```
https://ScarlettYellow.github.io/BeatSync/
```

### 更新环境变量

在Render Dashboard中：

1. 进入你的后端服务
2. 点击"Environment"
3. 找到 `ALLOWED_ORIGINS` 环境变量
4. 更新值为：
   ```
   https://ScarlettYellow.github.io/BeatSync/,http://localhost:8000
   ```
5. 点击"Save Changes"
6. Render会自动重新部署

### 验证CORS配置

更新后，测试一下：

1. 访问你的GitHub Pages网站
2. 打开浏览器开发者工具（F12）
3. 尝试上传文件并处理
4. 查看Console标签，确认没有CORS错误
5. 查看Network标签，确认API请求成功

---

## 总结

### Custom Domain
- **建议**：不设置，使用默认的GitHub Pages域名
- **如果必须设置**：需要拥有域名并配置DNS

### 环境变量
- **当前值**：`https://ScarlettYellow.github.io,http://localhost:8000`
- **正确值**：`https://ScarlettYellow.github.io/BeatSync/,http://localhost:8000`
- **关键**：包含完整的仓库路径和末尾斜杠

