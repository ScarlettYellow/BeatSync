# 修复Certbot ImportError问题

> **错误**：`ImportError: cannot import name 'appengine' from 'requests.packages.urllib3.contrib'`  
> **原因**：Python包版本冲突（urllib3与requests_toolbelt不兼容）  
> **解决**：修复Python依赖或使用snap安装certbot

---

## 问题分析

### 错误信息
```
ImportError: cannot import name 'appengine' from 'requests.packages.urllib3.contrib'
```

### 原因
- **Python包版本冲突**：系统包（`/usr/lib/python3/dist-packages/`）和手动安装的包（`/usr/local/lib/python3.10/dist-packages/`）版本不兼容
- **urllib3版本问题**：urllib3版本过新或过旧，与requests_toolbelt不兼容

---

## 解决方案

### 方案1：修复Python依赖（推荐）

**步骤1：更新和修复Python包**

```bash
# 更新软件包列表
sudo apt update

# 修复损坏的依赖
sudo apt --fix-broken install

# 重新安装certbot相关包
sudo apt remove --purge certbot python3-certbot-nginx
sudo apt install -y certbot python3-certbot-nginx
```

**步骤2：如果仍有问题，修复urllib3**

```bash
# 检查urllib3版本
pip3 list | grep urllib3

# 如果存在多个版本，卸载手动安装的版本
sudo pip3 uninstall urllib3 -y

# 重新安装系统版本
sudo apt install --reinstall python3-urllib3
```

---

### 方案2：使用snap安装certbot（最可靠）

**snap版本的certbot更稳定，不受系统Python包影响**

**步骤1：安装snapd（如果未安装）**

```bash
sudo apt update
sudo apt install -y snapd
```

**步骤2：使用snap安装certbot**

```bash
# 安装certbot
sudo snap install --classic certbot

# 创建符号链接（如果不存在）
sudo ln -sf /snap/bin/certbot /usr/bin/certbot
```

**步骤3：申请证书**

```bash
sudo certbot --nginx -d beatsync.site
```

---

### 方案3：使用pip安装certbot（备选）

**如果apt和snap都有问题，可以使用pip**

```bash
# 安装pip（如果未安装）
sudo apt install -y python3-pip

# 使用pip安装certbot
sudo pip3 install certbot certbot-nginx

# 申请证书
sudo certbot --nginx -d beatsync.site
```

---

## 推荐执行顺序

### 优先尝试方案1（修复依赖）

```bash
# 一键修复命令
sudo apt update && \
sudo apt --fix-broken install && \
sudo apt remove --purge certbot python3-certbot-nginx && \
sudo apt install -y certbot python3-certbot-nginx && \
certbot --version
```

**如果成功**：继续申请证书
```bash
sudo certbot --nginx -d beatsync.site
```

**如果失败**：尝试方案2（snap）

---

### 如果方案1失败，使用方案2（snap）

```bash
# 安装snapd
sudo apt update && sudo apt install -y snapd

# 安装certbot
sudo snap install --classic certbot

# 创建符号链接
sudo ln -sf /snap/bin/certbot /usr/bin/certbot

# 验证安装
certbot --version

# 申请证书
sudo certbot --nginx -d beatsync.site
```

---

## 验证安装

**检查certbot版本**：
```bash
certbot --version
```

**预期输出**：
```
certbot 2.x.x
```

**测试certbot命令**：
```bash
sudo certbot --help
```

**如果显示帮助信息**：说明安装成功 ✅

---

## 常见问题

### Q1：方案1执行后仍然报错

**A**：尝试方案2（snap），snap版本更稳定。

---

### Q2：snap安装失败

**A**：检查snapd服务状态：
```bash
sudo systemctl status snapd
sudo systemctl enable snapd
sudo systemctl start snapd
```

---

### Q3：pip安装后certbot命令找不到

**A**：检查certbot路径：
```bash
which certbot
# 如果返回空，可能需要添加到PATH或使用完整路径
sudo /usr/local/bin/certbot --nginx -d beatsync.site
```

---

## 申请证书（安装成功后）

**无论使用哪种方案安装，申请证书的命令相同**：

```bash
sudo certbot --nginx -d beatsync.site
```

**交互式配置**：
1. 输入邮箱
2. 同意服务条款（输入 `A`）
3. 是否分享邮箱（可选）
4. 选择重定向HTTP到HTTPS（建议选择 `2`）

---

## 验证清单

- [ ] 修复Python依赖（方案1）或使用snap安装（方案2）
- [ ] certbot命令可以正常执行
- [ ] 证书申请成功
- [ ] HTTPS可以访问
- [ ] 证书信息正确

---

**最后更新**：2025-12-04

