# 修复 /api/auth/register 404 错误

## 问题描述

`/api/auth/register` 端点返回 404 错误，导致设备 ID 自动登录失败。

## 根本原因

`/api/auth/register` 端点定义在 `if SUBSCRIPTION_AVAILABLE:` 条件块内，当服务器上订阅系统未启用或代码未更新时，端点不会被注册。

## 修复方案

已将 `/api/auth/register` 端点移到条件块外，确保端点始终被注册。

## 部署步骤

### 1. 在服务器上切换到项目目录

```bash
cd /opt/beatsync
```

### 2. 拉取最新代码

```bash
git pull origin main
```

如果遇到 Git 错误，可能需要先检查 Git 配置：

```bash
# 检查当前目录是否是 Git 仓库
git status

# 如果不是，检查项目目录
ls -la /opt/beatsync/.git

# 如果 .git 目录不存在，需要重新克隆
cd /opt
sudo rm -rf beatsync
sudo git clone https://github.com/scarlettyellow/BeatSync.git beatsync
sudo chown -R root:root /opt/beatsync
cd /opt/beatsync
```

### 3. 验证代码已更新

```bash
# 检查 main.py 中 /api/auth/register 的位置
grep -n "api/auth/register" web_service/backend/main.py
```

应该看到端点定义在 `if SUBSCRIPTION_AVAILABLE:` 条件块**外**（大约在第 1220 行）。

### 4. 重启服务

```bash
sudo systemctl restart beatsync
```

### 5. 验证端点可用

```bash
# 测试端点是否可访问（应该返回 503 而不是 404）
curl -X POST https://beatsync.site/api/auth/register \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "device_id=test_device_123"
```

**预期结果**：
- ✅ 如果订阅系统已启用：返回 `{"user_id": "...", "token": "..."}`
- ✅ 如果订阅系统未启用：返回 `{"error": "订阅系统未启用"}` (503)
- ❌ 如果仍然返回 404：说明代码未正确更新

## 验证修复

在 App 中测试：
1. 打开 App
2. 点击"购买"按钮
3. 观察是否还会出现"购买失败，请先登录"的错误
4. 检查 Safari Web Inspector 控制台，应该看到：
   - ✅ `自动注册成功` 或
   - ✅ `自动注册失败，状态码:503`（而不是 404）

## 注意事项

- 确保服务器上的 `SUBSCRIPTION_ENABLED=true` 环境变量已设置
- 确保订阅系统数据库已初始化
- 如果仍然有问题，检查服务器日志：`sudo journalctl -u beatsync -f`



