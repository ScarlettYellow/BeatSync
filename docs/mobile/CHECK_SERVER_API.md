# 检查服务器订阅API端点

## 快速检查脚本

已创建检查脚本：`scripts/deployment/check_subscription_api.sh`

### 执行方式

```bash
# 在项目根目录执行
./scripts/deployment/check_subscription_api.sh
```

脚本会要求输入SSH密码：`wine2025@`

### 脚本会检查：

1. ✅ 端点是否存在（在 main.py 中查找）
2. ✅ 服务状态（beatsync 服务是否运行）
3. ✅ 最近日志（查看是否有错误）
4. ✅ 订阅系统是否启用（检查环境变量）
5. ✅ 本地API测试（在服务器上测试端点）

## 手动检查命令

如果脚本无法执行，可以手动SSH登录后执行：

```bash
# 1. SSH登录
ssh ubuntu@124.221.58.149
# 输入密码：wine2025@

# 2. 检查端点是否存在
cd /opt/beatsync/web_service/backend
grep -n "/api/subscription/products" main.py

# 3. 检查服务状态
sudo systemctl status beatsync

# 4. 查看日志
sudo journalctl -u beatsync -n 50

# 5. 测试API（在服务器上）
curl http://localhost:8000/api/subscription/products

# 6. 如果端点存在但返回404，重启服务
sudo systemctl restart beatsync
sudo systemctl status beatsync
```

## 可能的问题和解决方案

### 问题1：端点不存在
**原因**：代码未更新到最新版本
**解决**：
```bash
cd /opt/beatsync
git pull origin main
sudo systemctl restart beatsync
```

### 问题2：端点存在但返回404
**原因**：服务未重启，或Python模块缓存
**解决**：
```bash
# 完全重启服务
sudo systemctl stop beatsync
sleep 2
sudo systemctl start beatsync

# 或者清除Python缓存
cd /opt/beatsync/web_service/backend
find . -name "*.pyc" -delete
find . -name "__pycache__" -type d -exec rm -r {} +
sudo systemctl restart beatsync
```

### 问题3：订阅系统未启用
**原因**：环境变量未设置
**解决**：
```bash
# 检查服务配置
sudo systemctl cat beatsync

# 如果服务配置中没有 SUBSCRIPTION_ENABLED，需要添加
sudo systemctl edit beatsync
# 添加：
# [Service]
# Environment="SUBSCRIPTION_ENABLED=true"

# 然后重启
sudo systemctl daemon-reload
sudo systemctl restart beatsync
```

