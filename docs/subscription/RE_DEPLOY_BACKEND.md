# 重新部署后端服务指南

## 概述

后端服务部署在腾讯云服务器上，使用 systemd 服务管理。重新部署需要更新代码并重启服务。

---

## 方法一：通过 Git 更新（推荐）

### 步骤 1：SSH 登录服务器

```bash
ssh ubuntu@beatsync.site
# 或使用您的服务器 IP
# ssh ubuntu@<服务器IP>
```

### 步骤 2：更新代码

```bash
# 进入项目目录
cd /opt/beatsync

# 拉取最新代码
sudo git pull origin main

# 如果遇到 "safe.directory" 错误，先执行：
sudo git config --global --add safe.directory /opt/beatsync
sudo git pull origin main
```

### 步骤 3：安装依赖（如果需要）

```bash
cd /opt/beatsync/web_service/backend
pip3 install -r requirements.txt
```

### 步骤 4：重启服务

```bash
# 重启 systemd 服务
sudo systemctl restart beatsync

# 检查服务状态
sudo systemctl status beatsync
```

### 步骤 5：验证部署

```bash
# 测试 API 端点
curl https://beatsync.site/api/subscription/products

# 应该返回产品列表，而不是 404
```

---

## 方法二：手动上传文件

如果 Git 不可用，可以手动上传更新后的文件：

### 步骤 1：在本地准备文件

确保 `web_service/backend/main.py` 已更新（包含 `/api/subscription/products` 端点）。

### 步骤 2：上传文件到服务器

```bash
# 从本地 Mac 上传文件
scp web_service/backend/main.py ubuntu@beatsync.site:/opt/beatsync/web_service/backend/main.py
```

### 步骤 3：SSH 登录并重启服务

```bash
ssh ubuntu@beatsync.site

# 重启服务
sudo systemctl restart beatsync

# 检查状态
sudo systemctl status beatsync
```

---

## 方法三：使用部署脚本

如果项目中有部署脚本：

```bash
# SSH 登录服务器
ssh ubuntu@beatsync.site

# 运行部署脚本
cd /opt/beatsync
sudo bash scripts/deployment/deploy_to_tencent_cloud.sh
```

---

## 常用 systemd 命令

### 查看服务状态

```bash
sudo systemctl status beatsync
```

### 查看服务日志

```bash
# 查看最近 50 行日志
sudo journalctl -u beatsync -n 50

# 实时查看日志
sudo journalctl -u beatsync -f
```

### 重启服务

```bash
sudo systemctl restart beatsync
```

### 停止服务

```bash
sudo systemctl stop beatsync
```

### 启动服务

```bash
sudo systemctl start beatsync
```

---

## 验证部署成功

### 1. 检查服务状态

```bash
sudo systemctl status beatsync
```

**应该显示**：`Active: active (running)`

### 2. 测试 API 端点

```bash
# 测试产品列表端点
curl https://beatsync.site/api/subscription/products

# 应该返回 JSON 格式的产品列表，而不是 404
```

**预期响应**：
```json
{
  "products": [
    {
      "id": "basic_monthly",
      "type": "subscription",
      "displayName": "基础版（月付）",
      ...
    },
    ...
  ],
  "count": 4
}
```

### 3. 检查服务日志

```bash
sudo journalctl -u beatsync -n 20
```

**应该看到**：服务正常启动，没有错误信息

---

## 常见问题

### 问题 1：Git pull 失败

**错误**：`fatal: unsafe repository`

**解决**：
```bash
sudo git config --global --add safe.directory /opt/beatsync
sudo git pull origin main
```

### 问题 2：服务重启失败

**检查日志**：
```bash
sudo journalctl -u beatsync -n 50
```

**常见原因**：
- Python 依赖缺失
- 代码语法错误
- 端口被占用

### 问题 3：API 仍然返回 404

**可能原因**：
1. 代码未正确更新
2. 服务未重启
3. Nginx 配置问题

**解决**：
```bash
# 确认文件已更新
grep -n "subscription/products" /opt/beatsync/web_service/backend/main.py

# 确认服务已重启
sudo systemctl status beatsync

# 检查 Nginx 配置
sudo nginx -t
sudo systemctl restart nginx
```

---

## 快速部署命令（一键执行）

```bash
# SSH 登录后，执行以下命令：
cd /opt/beatsync && \
sudo git config --global --add safe.directory /opt/beatsync && \
sudo git pull origin main && \
cd web_service/backend && \
pip3 install -r requirements.txt && \
cd /opt/beatsync && \
sudo systemctl restart beatsync && \
sleep 2 && \
sudo systemctl status beatsync | head -15 && \
echo "✅ 部署完成！" && \
curl -s https://beatsync.site/api/subscription/products | head -20
```

---

## 部署后检查清单

- [ ] 代码已更新（`git pull` 或文件上传成功）
- [ ] 服务已重启（`systemctl restart beatsync`）
- [ ] 服务状态正常（`systemctl status beatsync` 显示 `active (running)`）
- [ ] API 端点可访问（`curl https://beatsync.site/api/subscription/products` 返回产品列表）
- [ ] 没有错误日志（`journalctl -u beatsync -n 20` 没有错误）

---

**请按照上述步骤重新部署后端服务，然后再次测试 API 端点！** 🚀




# 重新部署后端服务指南

## 概述

后端服务部署在腾讯云服务器上，使用 systemd 服务管理。重新部署需要更新代码并重启服务。

---

## 方法一：通过 Git 更新（推荐）

### 步骤 1：SSH 登录服务器

```bash
ssh ubuntu@beatsync.site
# 或使用您的服务器 IP
# ssh ubuntu@<服务器IP>
```

### 步骤 2：更新代码

```bash
# 进入项目目录
cd /opt/beatsync

# 拉取最新代码
sudo git pull origin main

# 如果遇到 "safe.directory" 错误，先执行：
sudo git config --global --add safe.directory /opt/beatsync
sudo git pull origin main
```

### 步骤 3：安装依赖（如果需要）

```bash
cd /opt/beatsync/web_service/backend
pip3 install -r requirements.txt
```

### 步骤 4：重启服务

```bash
# 重启 systemd 服务
sudo systemctl restart beatsync

# 检查服务状态
sudo systemctl status beatsync
```

### 步骤 5：验证部署

```bash
# 测试 API 端点
curl https://beatsync.site/api/subscription/products

# 应该返回产品列表，而不是 404
```

---

## 方法二：手动上传文件

如果 Git 不可用，可以手动上传更新后的文件：

### 步骤 1：在本地准备文件

确保 `web_service/backend/main.py` 已更新（包含 `/api/subscription/products` 端点）。

### 步骤 2：上传文件到服务器

```bash
# 从本地 Mac 上传文件
scp web_service/backend/main.py ubuntu@beatsync.site:/opt/beatsync/web_service/backend/main.py
```

### 步骤 3：SSH 登录并重启服务

```bash
ssh ubuntu@beatsync.site

# 重启服务
sudo systemctl restart beatsync

# 检查状态
sudo systemctl status beatsync
```

---

## 方法三：使用部署脚本

如果项目中有部署脚本：

```bash
# SSH 登录服务器
ssh ubuntu@beatsync.site

# 运行部署脚本
cd /opt/beatsync
sudo bash scripts/deployment/deploy_to_tencent_cloud.sh
```

---

## 常用 systemd 命令

### 查看服务状态

```bash
sudo systemctl status beatsync
```

### 查看服务日志

```bash
# 查看最近 50 行日志
sudo journalctl -u beatsync -n 50

# 实时查看日志
sudo journalctl -u beatsync -f
```

### 重启服务

```bash
sudo systemctl restart beatsync
```

### 停止服务

```bash
sudo systemctl stop beatsync
```

### 启动服务

```bash
sudo systemctl start beatsync
```

---

## 验证部署成功

### 1. 检查服务状态

```bash
sudo systemctl status beatsync
```

**应该显示**：`Active: active (running)`

### 2. 测试 API 端点

```bash
# 测试产品列表端点
curl https://beatsync.site/api/subscription/products

# 应该返回 JSON 格式的产品列表，而不是 404
```

**预期响应**：
```json
{
  "products": [
    {
      "id": "basic_monthly",
      "type": "subscription",
      "displayName": "基础版（月付）",
      ...
    },
    ...
  ],
  "count": 4
}
```

### 3. 检查服务日志

```bash
sudo journalctl -u beatsync -n 20
```

**应该看到**：服务正常启动，没有错误信息

---

## 常见问题

### 问题 1：Git pull 失败

**错误**：`fatal: unsafe repository`

**解决**：
```bash
sudo git config --global --add safe.directory /opt/beatsync
sudo git pull origin main
```

### 问题 2：服务重启失败

**检查日志**：
```bash
sudo journalctl -u beatsync -n 50
```

**常见原因**：
- Python 依赖缺失
- 代码语法错误
- 端口被占用

### 问题 3：API 仍然返回 404

**可能原因**：
1. 代码未正确更新
2. 服务未重启
3. Nginx 配置问题

**解决**：
```bash
# 确认文件已更新
grep -n "subscription/products" /opt/beatsync/web_service/backend/main.py

# 确认服务已重启
sudo systemctl status beatsync

# 检查 Nginx 配置
sudo nginx -t
sudo systemctl restart nginx
```

---

## 快速部署命令（一键执行）

```bash
# SSH 登录后，执行以下命令：
cd /opt/beatsync && \
sudo git config --global --add safe.directory /opt/beatsync && \
sudo git pull origin main && \
cd web_service/backend && \
pip3 install -r requirements.txt && \
cd /opt/beatsync && \
sudo systemctl restart beatsync && \
sleep 2 && \
sudo systemctl status beatsync | head -15 && \
echo "✅ 部署完成！" && \
curl -s https://beatsync.site/api/subscription/products | head -20
```

---

## 部署后检查清单

- [ ] 代码已更新（`git pull` 或文件上传成功）
- [ ] 服务已重启（`systemctl restart beatsync`）
- [ ] 服务状态正常（`systemctl status beatsync` 显示 `active (running)`）
- [ ] API 端点可访问（`curl https://beatsync.site/api/subscription/products` 返回产品列表）
- [ ] 没有错误日志（`journalctl -u beatsync -n 20` 没有错误）

---

**请按照上述步骤重新部署后端服务，然后再次测试 API 端点！** 🚀




# 重新部署后端服务指南

## 概述

后端服务部署在腾讯云服务器上，使用 systemd 服务管理。重新部署需要更新代码并重启服务。

---

## 方法一：通过 Git 更新（推荐）

### 步骤 1：SSH 登录服务器

```bash
ssh ubuntu@beatsync.site
# 或使用您的服务器 IP
# ssh ubuntu@<服务器IP>
```

### 步骤 2：更新代码

```bash
# 进入项目目录
cd /opt/beatsync

# 拉取最新代码
sudo git pull origin main

# 如果遇到 "safe.directory" 错误，先执行：
sudo git config --global --add safe.directory /opt/beatsync
sudo git pull origin main
```

### 步骤 3：安装依赖（如果需要）

```bash
cd /opt/beatsync/web_service/backend
pip3 install -r requirements.txt
```

### 步骤 4：重启服务

```bash
# 重启 systemd 服务
sudo systemctl restart beatsync

# 检查服务状态
sudo systemctl status beatsync
```

### 步骤 5：验证部署

```bash
# 测试 API 端点
curl https://beatsync.site/api/subscription/products

# 应该返回产品列表，而不是 404
```

---

## 方法二：手动上传文件

如果 Git 不可用，可以手动上传更新后的文件：

### 步骤 1：在本地准备文件

确保 `web_service/backend/main.py` 已更新（包含 `/api/subscription/products` 端点）。

### 步骤 2：上传文件到服务器

```bash
# 从本地 Mac 上传文件
scp web_service/backend/main.py ubuntu@beatsync.site:/opt/beatsync/web_service/backend/main.py
```

### 步骤 3：SSH 登录并重启服务

```bash
ssh ubuntu@beatsync.site

# 重启服务
sudo systemctl restart beatsync

# 检查状态
sudo systemctl status beatsync
```

---

## 方法三：使用部署脚本

如果项目中有部署脚本：

```bash
# SSH 登录服务器
ssh ubuntu@beatsync.site

# 运行部署脚本
cd /opt/beatsync
sudo bash scripts/deployment/deploy_to_tencent_cloud.sh
```

---

## 常用 systemd 命令

### 查看服务状态

```bash
sudo systemctl status beatsync
```

### 查看服务日志

```bash
# 查看最近 50 行日志
sudo journalctl -u beatsync -n 50

# 实时查看日志
sudo journalctl -u beatsync -f
```

### 重启服务

```bash
sudo systemctl restart beatsync
```

### 停止服务

```bash
sudo systemctl stop beatsync
```

### 启动服务

```bash
sudo systemctl start beatsync
```

---

## 验证部署成功

### 1. 检查服务状态

```bash
sudo systemctl status beatsync
```

**应该显示**：`Active: active (running)`

### 2. 测试 API 端点

```bash
# 测试产品列表端点
curl https://beatsync.site/api/subscription/products

# 应该返回 JSON 格式的产品列表，而不是 404
```

**预期响应**：
```json
{
  "products": [
    {
      "id": "basic_monthly",
      "type": "subscription",
      "displayName": "基础版（月付）",
      ...
    },
    ...
  ],
  "count": 4
}
```

### 3. 检查服务日志

```bash
sudo journalctl -u beatsync -n 20
```

**应该看到**：服务正常启动，没有错误信息

---

## 常见问题

### 问题 1：Git pull 失败

**错误**：`fatal: unsafe repository`

**解决**：
```bash
sudo git config --global --add safe.directory /opt/beatsync
sudo git pull origin main
```

### 问题 2：服务重启失败

**检查日志**：
```bash
sudo journalctl -u beatsync -n 50
```

**常见原因**：
- Python 依赖缺失
- 代码语法错误
- 端口被占用

### 问题 3：API 仍然返回 404

**可能原因**：
1. 代码未正确更新
2. 服务未重启
3. Nginx 配置问题

**解决**：
```bash
# 确认文件已更新
grep -n "subscription/products" /opt/beatsync/web_service/backend/main.py

# 确认服务已重启
sudo systemctl status beatsync

# 检查 Nginx 配置
sudo nginx -t
sudo systemctl restart nginx
```

---

## 快速部署命令（一键执行）

```bash
# SSH 登录后，执行以下命令：
cd /opt/beatsync && \
sudo git config --global --add safe.directory /opt/beatsync && \
sudo git pull origin main && \
cd web_service/backend && \
pip3 install -r requirements.txt && \
cd /opt/beatsync && \
sudo systemctl restart beatsync && \
sleep 2 && \
sudo systemctl status beatsync | head -15 && \
echo "✅ 部署完成！" && \
curl -s https://beatsync.site/api/subscription/products | head -20
```

---

## 部署后检查清单

- [ ] 代码已更新（`git pull` 或文件上传成功）
- [ ] 服务已重启（`systemctl restart beatsync`）
- [ ] 服务状态正常（`systemctl status beatsync` 显示 `active (running)`）
- [ ] API 端点可访问（`curl https://beatsync.site/api/subscription/products` 返回产品列表）
- [ ] 没有错误日志（`journalctl -u beatsync -n 20` 没有错误）

---

**请按照上述步骤重新部署后端服务，然后再次测试 API 端点！** 🚀















