# BeatSync 订阅系统 - 管理员操作手册

## 📖 目录

1. [概述](#概述)
2. [系统配置](#系统配置)
3. [白名单管理](#白名单管理)
4. [用户管理](#用户管理)
5. [订阅管理](#订阅管理)
6. [数据统计](#数据统计)
7. [API 使用](#api-使用)
8. [故障排除](#故障排除)

---

## 概述

本手册面向 BeatSync 订阅系统的管理员，介绍如何配置、管理和维护订阅系统。

### 管理员权限

管理员可以：
- ✅ 启用/禁用订阅系统
- ✅ 管理白名单用户
- ✅ 查看用户订阅情况
- ✅ 查看下载统计
- ✅ 管理订阅数据

---

## 系统配置

### 环境变量配置

订阅系统通过环境变量进行配置：

#### 必需配置

```bash
# 启用订阅系统
SUBSCRIPTION_ENABLED=true

# JWT 密钥（用于用户认证）
JWT_SECRET_KEY=your-secret-key-change-in-production

# 管理员 Token（用于管理员 API）
ADMIN_TOKEN=your-admin-token-change-in-production
```

#### 可选配置

```bash
# 数据库路径（默认: 项目根目录/data/subscription.db）
SUBSCRIPTION_DB_PATH=/path/to/subscription.db

# App Store 共享密钥（用于 iOS 收据验证）
APP_STORE_SHARED_SECRET=your-app-store-shared-secret

# App Store Connect API 配置（用于批量创建 IAP）
APP_STORE_CONNECT_API_KEY_ID=your-key-id
APP_STORE_CONNECT_API_ISSUER_ID=your-issuer-id
APP_STORE_CONNECT_API_KEY_PATH=/path/to/AuthKey_xxx.p8
```

### 数据库初始化

1. **初始化数据库**
   ```bash
   cd web_service/backend
   python subscription_db.py
   ```

2. **验证数据库**
   ```bash
   # 检查数据库文件是否存在
   ls -la data/subscription.db
   ```

### 启用/禁用订阅系统

#### 启用订阅系统

1. **设置环境变量**
   ```bash
   export SUBSCRIPTION_ENABLED=true
   ```

2. **重启后端服务**
   ```bash
   # 停止当前服务
   # 重新启动服务
   python main.py
   ```

3. **验证启用状态**
   ```bash
   curl http://localhost:8000/api/subscription/status
   # 应该返回订阅状态，而不是 503 错误
   ```

#### 禁用订阅系统

1. **设置环境变量**
   ```bash
   export SUBSCRIPTION_ENABLED=false
   # 或删除该环境变量
   unset SUBSCRIPTION_ENABLED
   ```

2. **重启后端服务**
   ```bash
   # 停止当前服务
   # 重新启动服务
   python main.py
   ```

3. **验证禁用状态**
   ```bash
   curl http://localhost:8000/api/subscription/status
   # 应该返回 503 错误
   ```

---

## 白名单管理

### 添加用户到白名单

#### 使用 API

```bash
curl -X POST http://localhost:8000/api/admin/whitelist/add \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -F "user_id=USER_ID" \
  -F "reason=测试用户"
```

#### 响应示例

```json
{
  "success": true,
  "message": "用户已添加到白名单",
  "user_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
}
```

### 查看白名单列表

#### 使用 API

```bash
curl -X GET "http://localhost:8000/api/admin/whitelist?page=1&limit=20" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

#### 响应示例

```json
{
  "total": 5,
  "page": 1,
  "limit": 20,
  "users": [
    {
      "user_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
      "added_by": "admin",
      "reason": "测试用户",
      "created_at": "2025-01-01T00:00:00"
    }
  ]
}
```

### 检查用户是否在白名单中

#### 使用 API

```bash
curl -X GET http://localhost:8000/api/admin/whitelist/check/USER_ID \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

#### 响应示例

```json
{
  "is_whitelisted": true,
  "user_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
}
```

### 删除白名单用户

#### 使用 API

```bash
curl -X DELETE http://localhost:8000/api/admin/whitelist/USER_ID \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

#### 响应示例

```json
{
  "success": true,
  "message": "用户已从白名单中移除",
  "user_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
}
```

### 白名单用户权限

白名单用户可以：
- ✅ 免费使用所有功能
- ✅ 不受下载次数限制
- ✅ 不受订阅限制
- ✅ 无限次处理和下载

---

## 用户管理

### 查看用户信息

#### 使用数据库查询

```sql
-- 查看所有用户
SELECT * FROM users;

-- 查看特定用户
SELECT * FROM users WHERE user_id = 'USER_ID';

-- 查看用户注册时间
SELECT user_id, device_id, created_at FROM users ORDER BY created_at DESC;
```

### 查看用户订阅状态

#### 使用 API（需要用户 Token）

```bash
curl -X GET http://localhost:8000/api/subscription/status \
  -H "Authorization: Bearer USER_TOKEN"
```

#### 使用数据库查询

```sql
-- 查看用户订阅
SELECT * FROM subscriptions WHERE user_id = 'USER_ID';

-- 查看用户下载次数
SELECT * FROM download_credits WHERE user_id = 'USER_ID';

-- 查看用户下载记录
SELECT * FROM download_logs WHERE user_id = 'USER_ID' ORDER BY created_at DESC;
```

---

## 订阅管理

### 查看订阅统计

#### 使用数据库查询

```sql
-- 查看所有活跃订阅
SELECT * FROM subscriptions WHERE status = 'active';

-- 查看订阅类型统计
SELECT subscription_type, COUNT(*) as count 
FROM subscriptions 
WHERE status = 'active' 
GROUP BY subscription_type;

-- 查看即将过期的订阅
SELECT * FROM subscriptions 
WHERE status = 'active' 
AND end_date < datetime('now', '+7 days');
```

### 手动修改订阅（谨慎使用）

#### 使用数据库直接修改

```sql
-- 延长订阅时间（示例：延长 30 天）
UPDATE subscriptions 
SET end_date = datetime(end_date, '+30 days') 
WHERE user_id = 'USER_ID' AND status = 'active';

-- 取消订阅
UPDATE subscriptions 
SET status = 'cancelled', auto_renew = 0 
WHERE user_id = 'USER_ID' AND status = 'active';
```

⚠️ **警告**: 直接修改数据库可能导致数据不一致，建议通过 API 或管理界面操作。

---

## 数据统计

### 下载统计

#### 使用数据库查询

```sql
-- 总下载次数
SELECT COUNT(*) FROM download_logs;

-- 按次数类型统计
SELECT credit_type, COUNT(*) as count 
FROM download_logs 
GROUP BY credit_type;

-- 按日期统计
SELECT DATE(created_at) as date, COUNT(*) as count 
FROM download_logs 
GROUP BY DATE(created_at) 
ORDER BY date DESC;

-- 用户下载排行
SELECT user_id, COUNT(*) as download_count 
FROM download_logs 
GROUP BY user_id 
ORDER BY download_count DESC 
LIMIT 10;
```

### 订阅统计

#### 使用数据库查询

```sql
-- 订阅用户数
SELECT COUNT(DISTINCT user_id) FROM subscriptions WHERE status = 'active';

-- 订阅收入统计（需要结合支付记录）
SELECT 
  subscription_type,
  COUNT(*) as count,
  SUM(amount) as total_revenue
FROM subscriptions s
JOIN payment_records p ON s.transaction_id = p.transaction_id
WHERE s.status = 'active'
GROUP BY subscription_type;
```

### 用户活跃度统计

#### 使用数据库查询

```sql
-- 活跃用户数（最近 7 天有下载）
SELECT COUNT(DISTINCT user_id) 
FROM download_logs 
WHERE created_at > datetime('now', '-7 days');

-- 新用户注册统计
SELECT DATE(created_at) as date, COUNT(*) as count 
FROM users 
GROUP BY DATE(created_at) 
ORDER BY date DESC;
```

---

## API 使用

### 管理员 API 端点

#### 白名单管理

| 方法 | 端点 | 说明 |
|------|------|------|
| GET | `/api/admin/whitelist` | 获取白名单列表 |
| POST | `/api/admin/whitelist/add` | 添加用户到白名单 |
| DELETE | `/api/admin/whitelist/{user_id}` | 删除白名单用户 |
| GET | `/api/admin/whitelist/check/{user_id}` | 检查用户是否在白名单中 |

#### 认证

所有管理员 API 都需要在请求头中提供管理员 Token：

```bash
Authorization: Bearer YOUR_ADMIN_TOKEN
```

### 用户 API 端点

#### 订阅相关

| 方法 | 端点 | 说明 |
|------|------|------|
| GET | `/api/subscription/status` | 获取订阅状态 |
| GET | `/api/subscription/history` | 获取订阅历史 |
| POST | `/api/subscription/verify-receipt` | 验证收据 |

#### 下载次数相关

| 方法 | 端点 | 说明 |
|------|------|------|
| GET | `/api/credits/check` | 检查下载次数 |
| POST | `/api/credits/consume` | 消费下载次数 |
| GET | `/api/downloads/history` | 获取下载记录 |

---

## 故障排除

### 常见问题

#### 1. 订阅系统未启用

**症状**: API 返回 503 错误，提示"订阅系统未启用"

**解决方案**:
1. 检查 `SUBSCRIPTION_ENABLED` 环境变量
2. 确保数据库已初始化
3. 重启后端服务

#### 2. 数据库连接失败

**症状**: 日志显示数据库连接错误

**解决方案**:
1. 检查数据库文件是否存在
2. 检查数据库文件权限
3. 检查 `SUBSCRIPTION_DB_PATH` 环境变量

#### 3. 白名单管理失败

**症状**: 白名单 API 返回 403 错误

**解决方案**:
1. 检查 `ADMIN_TOKEN` 环境变量
2. 确保请求头中包含正确的 Token
3. 检查 Token 格式（Bearer Token）

#### 4. 收据验证失败

**症状**: 收据验证 API 返回错误

**解决方案**:
1. 检查 `APP_STORE_SHARED_SECRET` 环境变量
2. 检查收据数据格式
3. 检查网络连接（App Store 验证需要网络）

### 日志查看

#### 后端服务日志

```bash
# 查看实时日志
tail -f /tmp/beatsync_backend.log

# 查看错误日志
grep ERROR /tmp/beatsync_backend.log
```

#### 数据库日志

数据库操作日志会输出到标准输出，可以通过后端服务日志查看。

### 数据备份

#### 备份数据库

```bash
# 备份数据库文件
cp data/subscription.db data/subscription.db.backup.$(date +%Y%m%d)

# 或使用 SQLite 备份命令
sqlite3 data/subscription.db ".backup data/subscription.db.backup"
```

#### 恢复数据库

```bash
# 恢复数据库文件
cp data/subscription.db.backup.$(date +%Y%m%d) data/subscription.db
```

---

## 最佳实践

### 1. 定期备份

- 建议每天备份数据库
- 保留至少 7 天的备份

### 2. 监控系统

- 监控订阅系统状态
- 监控 API 响应时间
- 监控数据库大小

### 3. 日志管理

- 定期清理日志文件
- 保留重要日志用于分析

### 4. 安全措施

- 定期更换 `ADMIN_TOKEN`
- 定期更换 `JWT_SECRET_KEY`
- 限制管理员 API 访问

---

## 更新日志

### 2025-01-XX
- 初始版本发布
- 支持白名单管理
- 支持订阅管理
- 支持数据统计

---

**最后更新**: 2025-12-25
