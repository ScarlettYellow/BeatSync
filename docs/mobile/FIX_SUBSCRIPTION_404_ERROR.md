# 修复订阅套餐404错误

## 问题描述
应用可以正常启动，但点击"查看订阅套餐"时显示：
- 错误：`获取产品列表失败: 404`
- 详情：`{"detail":"Not Found"}`

## 问题分析

### 1. 端点定义
- 后端代码中已定义 `/api/subscription/products` 端点（main.py 第1133行）
- 端点不在条件块内，应该始终可用
- 即使订阅系统未启用，也应该返回空列表，而不是404

### 2. 可能的原因
1. **服务器代码未更新**：服务器上的代码版本可能不是最新的
2. **服务未重启**：代码更新后，systemd 服务未重启
3. **Nginx配置问题**：Nginx 可能没有正确转发到 FastAPI

## 解决方案

### 方案1：检查服务器代码版本（推荐）

1. **SSH登录服务器**：
```bash
ssh root@124.221.58.149
# 或
ssh ubuntu@124.221.58.149
```

2. **检查代码位置**：
```bash
cd /opt/beatsync/web_service/backend
```

3. **检查端点是否存在**：
```bash
grep -n "/api/subscription/products" main.py
```

4. **如果端点不存在，需要更新代码**：
```bash
# 方式1：使用Git拉取最新代码
cd /opt/beatsync
git pull origin main

# 方式2：使用rsync从本地同步
# 在本地机器上执行：
rsync -avz --exclude '.git' --exclude '__pycache__' \
  --exclude '*.pyc' \
  web_service/backend/ root@124.221.58.149:/opt/beatsync/web_service/backend/
```

5. **重启服务**：
```bash
sudo systemctl restart beatsync
sudo systemctl status beatsync
```

### 方案2：检查服务状态

1. **检查服务是否运行**：
```bash
sudo systemctl status beatsync
```

2. **查看服务日志**：
```bash
sudo journalctl -u beatsync -f --lines=50
```

3. **检查服务配置**：
```bash
cat /etc/systemd/system/beatsync.service
```

### 方案3：检查Nginx配置

1. **检查Nginx配置**：
```bash
sudo cat /etc/nginx/sites-available/beatsync
```

2. **确认代理配置**：
```nginx
location /api/ {
    proxy_pass http://127.0.0.1:8000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
}
```

3. **重新加载Nginx**：
```bash
sudo nginx -t
sudo systemctl reload nginx
```

### 方案4：临时测试（本地开发）

如果服务器暂时无法更新，可以在本地测试：

1. **启动本地后端**：
```bash
cd web_service/backend
export SUBSCRIPTION_ENABLED=true
python3 main.py
```

2. **修改前端API地址**（临时）：
在 `script.js` 中，将 `API_BASE_URL` 改为 `http://localhost:8000`

3. **在iOS App中测试**：
- 修改 `capacitor.config.json` 中的服务器地址
- 或使用本地网络IP

## 验证修复

修复后，测试端点：

```bash
# 测试健康检查
curl https://beatsync.site/api/health

# 测试订阅产品列表
curl https://beatsync.site/api/subscription/products
```

预期响应：
```json
{
  "products": [
    {
      "id": "basic_monthly",
      "type": "subscription",
      "displayName": "基础版",
      "description": "公测期特价：4.8元/月，每月20次下载，每日10次处理",
      "price": 4.8,
      "displayPrice": "¥4.8/月",
      "credits": 20,
      "period": "monthly"
    },
    ...
  ],
  "count": 4
}
```

## 注意事项

1. **订阅系统启用**：确保服务器上设置了环境变量 `SUBSCRIPTION_ENABLED=true`
2. **数据库初始化**：确保订阅数据库已初始化
3. **服务重启**：代码更新后必须重启 systemd 服务

## 相关文件

- 后端端点：`web_service/backend/main.py` (第1133行)
- 前端调用：`web_service/frontend/subscription.js` (第122行)
- 部署文档：`docs/deployment/TENCENT_CLOUD_DEPLOYMENT_GUIDE.md`

