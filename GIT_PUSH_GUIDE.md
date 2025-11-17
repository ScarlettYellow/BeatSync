# Git 推送到GitHub指南

## 当前状态

✅ 远程仓库已连接：`https://github.com/ScarlettYellow/BeatSync.git`  
❌ 推送需要GitHub认证

## 推送方式选择

### 方式1：使用GitHub CLI（推荐，最简单）

如果已安装GitHub CLI：

```bash
# 1. 登录GitHub（如果未登录）
gh auth login

# 2. 推送代码
git push -u origin main

# 3. 推送标签
git push origin --tags
```

### 方式2：使用SSH（推荐，长期使用）

如果已配置SSH密钥：

```bash
# 1. 更改远程仓库地址为SSH
git remote set-url origin git@github.com:ScarlettYellow/BeatSync.git

# 2. 推送代码
git push -u origin main

# 3. 推送标签
git push origin --tags
```

### 方式3：使用Personal Access Token（HTTPS）

如果使用HTTPS方式：

```bash
# 1. 在GitHub创建Personal Access Token
#    Settings → Developer settings → Personal access tokens → Tokens (classic)
#    权限：至少选择 repo

# 2. 推送时使用token作为密码
git push -u origin main
# Username: 你的GitHub用户名
# Password: 输入Personal Access Token（不是GitHub密码）

# 3. 推送标签
git push origin --tags
```

### 方式4：手动在终端输入（临时）

```bash
# 直接推送，会提示输入用户名和密码
git push -u origin main

# 注意：如果使用HTTPS，密码需要使用Personal Access Token
# 不是GitHub账户密码
```

## 推荐方案

### 方案A：使用SSH（最方便，长期推荐）

**优点**：
- 一次配置，永久使用
- 不需要每次输入密码
- 更安全

**步骤**：

1. **检查是否已有SSH密钥**：
```bash
ls -la ~/.ssh/id_*.pub
```

2. **如果没有，生成SSH密钥**：
```bash
ssh-keygen -t ed25519 -C "your_email@example.com"
# 按回车使用默认路径
# 可以设置密码（可选）
```

3. **添加SSH密钥到GitHub**：
```bash
# 复制公钥
cat ~/.ssh/id_ed25519.pub
# 或
pbcopy < ~/.ssh/id_ed25519.pub  # macOS
```

然后：
- 登录GitHub
- Settings → SSH and GPG keys → New SSH key
- 粘贴公钥内容
- 保存

4. **测试连接**：
```bash
ssh -T git@github.com
# 应该显示：Hi ScarlettYellow! You've successfully authenticated...
```

5. **更改远程地址并推送**：
```bash
git remote set-url origin git@github.com:ScarlettYellow/BeatSync.git
git push -u origin main
git push origin --tags
```

### 方案B：使用GitHub CLI（简单快速）

**步骤**：

1. **安装GitHub CLI**（如果未安装）：
```bash
# macOS
brew install gh

# 或从 https://cli.github.com/ 下载
```

2. **登录**：
```bash
gh auth login
# 选择GitHub.com
# 选择HTTPS
# 选择浏览器登录或token
```

3. **推送**：
```bash
git push -u origin main
git push origin --tags
```

## 快速推送命令（选择一种方式后使用）

### 如果使用SSH：
```bash
git remote set-url origin git@github.com:ScarlettYellow/BeatSync.git
git push -u origin main && git push origin --tags
```

### 如果使用HTTPS + Token：
```bash
git push -u origin main
# 输入用户名和Personal Access Token
git push origin --tags
```

### 如果使用GitHub CLI：
```bash
gh auth login  # 如果未登录
git push -u origin main && git push origin --tags
```

## 验证推送成功

推送成功后，访问：
https://github.com/ScarlettYellow/BeatSync

应该能看到：
- ✅ 所有代码文件
- ✅ 提交历史
- ✅ 版本标签（v1.3.0）
- ✅ README.md显示

## 后续使用

推送成功后，以后的重要改动可以这样推送：

```bash
# 1. 本地提交
./git_commit_important.sh "类型: 描述"

# 2. 推送到GitHub
git push

# 3. 如果创建了新标签
git push origin --tags
```

## 常见问题

### Q: 提示"Permission denied"
A: 检查SSH密钥是否正确添加到GitHub，或使用Personal Access Token

### Q: 提示"Authentication failed"
A: 如果使用HTTPS，确保使用Personal Access Token而不是GitHub密码

### Q: 如何查看当前远程仓库地址？
```bash
git remote -v
```

### Q: 如何切换远程仓库方式？
```bash
# 切换到SSH
git remote set-url origin git@github.com:ScarlettYellow/BeatSync.git

# 切换到HTTPS
git remote set-url origin https://github.com/ScarlettYellow/BeatSync.git
```

