# BeatSync 订阅系统设计方案

## 一、需求分析

### 1.1 套餐设计

#### 免费体验套餐
- **限制**：每周可免费下载2个满意作品
- **处理次数**：无限次（仅限制下载）

#### 基础版付费套餐
- **连续包月**：15元/月，50次下载/月
- **连续包年**：99元/年，600次下载/年（平均50次/月）

#### 高级版付费套餐
- **连续包月**：69元/月，1000次下载/月
- **连续包年**：499元/年，12000次下载/年（平均1000次/月）

#### 购买下载次数套餐（一次性）
- **5元/10次**
- **9元/20次**
- **20元/50次**

### 1.2 核心设计理念
- ✅ **为下载付费**：用户只为满意的结果付费，提升用户体验
- ✅ **处理免费**：允许用户无限次处理，找到满意的结果
- ✅ **多端同步**：iOS App 和网站共享同一套订阅系统
- ✅ **白名单功能**：管理员可添加用户到白名单，白名单用户免费使用所有功能
- ✅ **零耦合设计**：订阅系统与现有功能完全解耦，不影响现有功能的可用性

---

## 二、技术架构设计

### 2.1 整体架构

```
┌─────────────────┐         ┌─────────────────┐
│   iOS App       │         │   Web Frontend  │
│  (Capacitor)    │         │  (GitHub Pages) │
└────────┬────────┘         └────────┬────────┘
         │                            │
         │  HTTPS API                 │  HTTPS API
         │                            │
         └────────────┬───────────────┘
                      │
         ┌────────────▼────────────┐
         │   FastAPI Backend       │
         │  (beatsync.site)        │
         │                         │
         │  - 订阅管理              │
         │  - 支付集成              │
         │  - 下载次数管理          │
         │  - 用户认证              │
         │  - 白名单管理            │
         └────────────┬────────────┘
                      │
         ┌────────────▼────────────┐
         │   SQLite Database      │
         │  (或 PostgreSQL)        │
         │                         │
         │  - users                │
         │  - subscriptions        │
         │  - download_credits     │
         │  - payment_records      │
         │  - whitelist            │
         └─────────────────────────┘
```

### 2.2 支付集成方案

#### iOS App 支付
- **使用 StoreKit 2**（iOS 15+）或 StoreKit 1（兼容旧版本）
- **订阅类型**：自动续订订阅（Auto-Renewable Subscriptions）
- **一次性购买**：使用 In-App Purchase（非消耗型产品）

#### Web 支付
- **微信支付**：适合中国用户
- **支付宝**：适合中国用户
- **Stripe**：适合国际用户（可选）

#### 支付流程
1. **iOS App**：使用原生 StoreKit，通过 App Store 支付
2. **Web**：跳转到支付页面（微信/支付宝），支付成功后回调
3. **后端验证**：验证支付凭证（App Store Receipt / 支付平台回调）
4. **更新订阅**：更新用户订阅状态和下载次数

---

## 三、数据库设计

### 3.1 用户表 (users)

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT UNIQUE NOT NULL,  -- UUID，用于跨端识别
    device_id TEXT,                -- iOS设备ID（用于iOS App）
    email TEXT,                    -- 邮箱（可选，用于Web）
    phone TEXT,                    -- 手机号（可选，用于Web）
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_user_id ON users(user_id);
CREATE INDEX idx_users_device_id ON users(device_id);
```

### 3.2 订阅表 (subscriptions)

```sql
CREATE TABLE subscriptions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    subscription_type TEXT NOT NULL,  -- 'free', 'basic_monthly', 'basic_yearly', 'premium_monthly', 'premium_yearly'
    status TEXT NOT NULL,             -- 'active', 'expired', 'cancelled'
    start_date TIMESTAMP NOT NULL,
    end_date TIMESTAMP,               -- NULL表示永久有效（免费套餐）
    auto_renew BOOLEAN DEFAULT 1,     -- 是否自动续订
    platform TEXT NOT NULL,           -- 'ios', 'web', 'both'
    transaction_id TEXT,              -- App Store Transaction ID 或 支付平台订单号
    receipt_data TEXT,                -- App Store Receipt（用于验证）
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE INDEX idx_subscriptions_user_id ON subscriptions(user_id);
CREATE INDEX idx_subscriptions_status ON subscriptions(status);
```

### 3.3 下载次数表 (download_credits)

```sql
CREATE TABLE download_credits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    credit_type TEXT NOT NULL,        -- 'free_weekly', 'subscription', 'purchase'
    total_credits INTEGER NOT NULL,   -- 总次数
    used_credits INTEGER DEFAULT 0,   -- 已使用次数
    remaining_credits INTEGER NOT NULL,-- 剩余次数
    period_start TIMESTAMP,           -- 周期开始时间（用于免费套餐和订阅）
    period_end TIMESTAMP,             -- 周期结束时间
    source_subscription_id INTEGER,   -- 关联的订阅ID（如果是订阅来源）
    source_purchase_id INTEGER,      -- 关联的购买记录ID（如果是一次性购买）
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (source_subscription_id) REFERENCES subscriptions(id),
    FOREIGN KEY (source_purchase_id) REFERENCES payment_records(id)
);

CREATE INDEX idx_download_credits_user_id ON download_credits(user_id);
CREATE INDEX idx_download_credits_period ON download_credits(period_start, period_end);
```

### 3.4 支付记录表 (payment_records)

```sql
CREATE TABLE payment_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    payment_type TEXT NOT NULL,      -- 'subscription', 'one_time_purchase'
    product_id TEXT NOT NULL,        -- 产品ID（如 'basic_monthly', 'credits_10'）
    amount DECIMAL(10, 2) NOT NULL,   -- 支付金额
    currency TEXT DEFAULT 'CNY',      -- 货币类型
    platform TEXT NOT NULL,          -- 'ios', 'wechat', 'alipay', 'stripe'
    transaction_id TEXT UNIQUE,      -- 交易ID
    status TEXT NOT NULL,            -- 'pending', 'completed', 'failed', 'refunded'
    receipt_data TEXT,               -- 支付凭证（App Store Receipt 或 支付平台回调数据）
    verified BOOLEAN DEFAULT 0,      -- 是否已验证
    verified_at TIMESTAMP,           -- 验证时间
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE INDEX idx_payment_records_user_id ON payment_records(user_id);
CREATE INDEX idx_payment_records_transaction_id ON payment_records(transaction_id);
CREATE INDEX idx_payment_records_status ON payment_records(status);
```

### 3.5 下载记录表 (download_logs)

```sql
CREATE TABLE download_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    task_id TEXT NOT NULL,           -- 任务ID
    version TEXT NOT NULL,            -- 'modular' 或 'v2'
    credit_id INTEGER,               -- 使用的下载次数记录ID
    ip_address TEXT,                 -- IP地址（用于安全）
    user_agent TEXT,                 -- User Agent
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (credit_id) REFERENCES download_credits(id)
);

CREATE INDEX idx_download_logs_user_id ON download_logs(user_id);
CREATE INDEX idx_download_logs_task_id ON download_logs(task_id);
```

### 3.6 白名单表 (whitelist)

```sql
CREATE TABLE whitelist (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT UNIQUE NOT NULL,  -- 用户ID
    added_by TEXT,                  -- 添加者（管理员标识）
    reason TEXT,                    -- 添加原因（可选）
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE INDEX idx_whitelist_user_id ON whitelist(user_id);
```

**说明**：
- 白名单用户不受任何订阅套餐限制
- 可以无限次免费下载
- 管理员可以添加/删除白名单用户

---

## 四、API 设计

### 4.1 用户认证

#### POST /api/auth/register
注册新用户（iOS App 或 Web）

**请求体**：
```json
{
    "device_id": "ios_device_uuid",  // iOS App 提供
    "email": "user@example.com",     // Web 提供（可选）
    "phone": "13800138000"           // Web 提供（可选）
}
```

**响应**：
```json
{
    "user_id": "uuid",
    "token": "jwt_token"  // 用于后续API认证
}
```

#### POST /api/auth/login
登录（通过 user_id 或 device_id）

**请求体**：
```json
{
    "user_id": "uuid",      // 或
    "device_id": "ios_device_uuid"
}
```

**响应**：
```json
{
    "user_id": "uuid",
    "token": "jwt_token"
}
```

### 4.2 订阅管理

#### GET /api/subscription/status
获取当前订阅状态

**响应**：
```json
{
    "is_whitelisted": false,  // 是否在白名单中
    "subscription": {
```json
{
    "subscription": {
        "type": "basic_monthly",
        "status": "active",
        "start_date": "2025-01-01T00:00:00Z",
        "end_date": "2025-02-01T00:00:00Z",
        "auto_renew": true
    },
    "download_credits": {
        "total": 50,
        "used": 12,
        "remaining": 38,
        "period_start": "2025-01-01T00:00:00Z",
        "period_end": "2025-02-01T00:00:00Z"
    },
    "free_weekly": {
        "used": 1,
        "remaining": 1,
        "week_start": "2025-01-20T00:00:00Z",
        "week_end": "2025-01-27T00:00:00Z"
    }
}
```

**说明**：
- 如果 `is_whitelisted` 为 `true`，用户可无限次免费下载，不受订阅和下载次数限制

#### POST /api/subscription/purchase
购买订阅或下载次数（Web端）

**请求体**：
```json
{
    "product_id": "basic_monthly",  // 或 "credits_10"
    "payment_platform": "wechat"    // 或 "alipay"
}
```

**响应**：
```json
{
    "payment_url": "https://pay.wechat.com/...",  // 跳转到支付页面
    "order_id": "order_123456"
}
```

#### POST /api/subscription/verify-ios
验证 iOS App Store 支付（iOS App 调用）

**请求体**：
```json
{
    "receipt_data": "base64_encoded_receipt",
    "product_id": "basic_monthly"
}
```

**响应**：
```json
{
    "verified": true,
    "subscription": {
        "type": "basic_monthly",
        "status": "active",
        "end_date": "2025-02-01T00:00:00Z"
    }
}
```

#### POST /api/subscription/webhook
支付平台回调（微信/支付宝）

**请求体**：（由支付平台提供）

**响应**：
```json
{
    "success": true
}
```

### 4.3 下载次数管理

#### GET /api/credits/check
检查是否有可用下载次数

**响应**：
```json
{
    "is_whitelisted": false,  // 是否在白名单中
    "can_download": true,
    "available_credits": {
        "subscription": 38,
        "free_weekly": 1,
        "purchased": 0
    },
    "total_remaining": 39
}
```

**说明**：
- 如果 `is_whitelisted` 为 `true`，则 `can_download` 始终为 `true`，且不需要消费下载次数

#### POST /api/credits/consume
消费下载次数（在下载时调用）

**请求体**：
```json
{
    "task_id": "task_123",
    "version": "modular",  // 或 "v2"
    "credit_type": "subscription"  // 或 "free_weekly", "purchase"
}
```

**响应**：
```json
{
    "success": true,
    "remaining_credits": 37
}
```

#### GET /api/credits/history
获取下载次数使用历史

**响应**：
```json
{
    "history": [
        {
            "date": "2025-01-20T10:30:00Z",
            "type": "subscription",
            "used": 1,
            "remaining": 37
        },
        ...
    ]
}
```

### 4.4 下载接口设计（零耦合方案）

#### GET /api/download/{task_id}
**重要**：保持现有接口完全不变，确保向后兼容

**现有行为**（保持不变）：
- 无需认证，任何人都可以下载
- 直接返回文件，无任何限制

**新增可选功能**（通过环境变量控制）：
- 如果 `SUBSCRIPTION_ENABLED=false`（默认），完全使用现有行为
- 如果 `SUBSCRIPTION_ENABLED=true`，支持两种模式：

#### 模式1：匿名下载（向后兼容）
- **无认证信息**：直接下载，不检查订阅（保持现有行为）
- **适用场景**：现有用户、未升级的前端

#### 模式2：认证下载（订阅功能）
- **带认证信息**：检查订阅和下载次数
- **流程**：
  1. 验证用户身份（通过可选的 JWT Token）
  2. **检查是否在白名单中**（如果是，直接允许下载，不消费次数）
  3. 检查是否有可用下载次数
  4. 如果有，消费一次下载次数
  5. 返回文件下载

**请求头**（可选）：
```
Authorization: Bearer <token>  // 如果提供，则启用订阅检查
```

**如果无可用次数且不在白名单**：
```json
{
    "error": "insufficient_credits",
    "message": "下载次数不足，请购买订阅或下载次数",
    "available_credits": 0
}
```

**优雅降级**：
- 如果订阅系统不可用（数据库连接失败等），自动回退到匿名模式
- 确保现有功能始终可用

### 4.5 白名单管理（管理员功能）

#### GET /api/admin/whitelist
获取白名单列表（需要管理员权限）

**查询参数**：
- `page`: 页码（默认1）
- `limit`: 每页数量（默认20）
- `search`: 搜索关键词（user_id 或 email）

**响应**：
```json
{
    "total": 10,
    "page": 1,
    "limit": 20,
    "users": [
        {
            "user_id": "uuid1",
            "email": "user1@example.com",
            "phone": "13800138000",
            "added_by": "admin",
            "reason": "测试用户",
            "created_at": "2025-01-20T10:00:00Z"
        },
        ...
    ]
}
```

#### POST /api/admin/whitelist/add
添加用户到白名单（需要管理员权限）

**请求体**：
```json
{
    "user_id": "uuid",  // 必填：用户ID
    "reason": "测试用户"  // 可选：添加原因
}
```

**响应**：
```json
{
    "success": true,
    "message": "用户已添加到白名单",
    "user_id": "uuid"
}
```

#### DELETE /api/admin/whitelist/{user_id}
从白名单中删除用户（需要管理员权限）

**响应**：
```json
{
    "success": true,
    "message": "用户已从白名单中移除",
    "user_id": "uuid"
}
```

#### GET /api/admin/whitelist/check/{user_id}
检查用户是否在白名单中（需要管理员权限）

**响应**：
```json
{
    "is_whitelisted": true,
    "user_id": "uuid",
    "added_at": "2025-01-20T10:00:00Z",
    "added_by": "admin"
}
```

---

## 五、前端实现

### 5.1 iOS App 实现

#### 使用 StoreKit 2（推荐）

```swift
import StoreKit

// 1. 获取产品信息
let productIDs = [
    "com.beatsync.basic_monthly",
    "com.beatsync.basic_yearly",
    "com.beatsync.premium_monthly",
    "com.beatsync.premium_yearly",
    "com.beatsync.credits_10",
    "com.beatsync.credits_20",
    "com.beatsync.credits_50"
]

// 2. 购买订阅
Task {
    do {
        let result = try await product.purchase()
        switch result {
        case .success(let verification):
            // 3. 验证收据
            let receipt = try verification.payloadValue
            await verifyReceiptWithBackend(receipt)
        case .userCancelled:
            // 用户取消
        case .pending:
            // 等待家长批准
        @unknown default:
            break
        }
    } catch {
        // 处理错误
    }
}

// 4. 监听订阅状态变化
Task {
    for await update in Transaction.updates {
        // 处理订阅更新
    }
}
```

#### 订阅状态显示
- 在设置页面显示当前订阅状态
- 显示剩余下载次数
- 提供购买/续订按钮

### 5.2 Web 前端实现

#### 订阅页面
- 显示所有套餐选项
- 显示当前订阅状态
- 提供购买按钮（跳转到支付）

#### 下载前检查
```javascript
// 在 downloadFile 函数中添加
async function downloadFile(url, filename, version) {
    // 1. 检查下载次数
    const checkResponse = await fetch(`${API_BASE_URL}/api/credits/check`, {
        headers: {
            'Authorization': `Bearer ${userToken}`
        }
    });
    const checkResult = await checkResponse.json();
    
    if (!checkResult.can_download) {
        // 显示购买提示
        showPurchaseModal(checkResult);
        return;
    }
    
    // 2. 开始下载
    // 3. 消费下载次数
    await fetch(`${API_BASE_URL}/api/credits/consume`, {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${userToken}`,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            task_id: currentTaskId,
            version: version
        })
    });
    
    // 4. 执行下载
    // ...
}
```

---

## 六、后端实现

### 6.1 环境变量配置

```python
import os

# 订阅系统开关（默认关闭，确保不影响现有功能）
SUBSCRIPTION_ENABLED = os.getenv("SUBSCRIPTION_ENABLED", "false").lower() == "true"

# 订阅系统数据库路径（可选，如果未配置则订阅功能不可用）
SUBSCRIPTION_DB_PATH = os.getenv("SUBSCRIPTION_DB_PATH", None)

# 管理员Token（用于白名单管理）
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", None)
```

### 6.2 可选用户认证中间件

```python
from fastapi import Depends, HTTPException, status, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional

security = HTTPBearer(auto_error=False)  # auto_error=False 允许无认证请求

async def get_optional_user(
    authorization: Optional[str] = Header(None)
) -> Optional[str]:
    """
    可选的用户认证
    - 如果提供了认证信息，验证并返回 user_id
    - 如果没有提供，返回 None（匿名用户）
    - 如果订阅系统未启用，始终返回 None
    """
    if not SUBSCRIPTION_ENABLED:
        return None  # 订阅系统未启用，不进行认证
    
    if not authorization:
        return None  # 无认证信息，匿名用户
    
    try:
        # 提取 Bearer token
        token = authorization.replace("Bearer ", "")
        user_id = verify_token(token)
        return user_id
    except Exception:
        return None  # 认证失败，视为匿名用户
```

### 6.3 下载接口实现（零耦合）

```python
@app.get("/api/download/{task_id}")
async def download_result(
    task_id: str,
    version: Optional[str] = None,
    user_id: Optional[str] = Depends(get_optional_user)
):
    """
    下载处理结果（保持向后兼容）
    """
    # 1. 首先执行现有的文件查找逻辑（保持不变）
    output_dir = OUTPUT_DIR / task_id
    if not output_dir.exists():
        raise HTTPException(status_code=404, detail="任务不存在")
    
    # ... 现有的文件查找逻辑 ...
    
    # 2. 订阅检查（仅在启用且用户已认证时）
    if SUBSCRIPTION_ENABLED and user_id:
        try:
            # 检查白名单
            is_whitelisted = await check_whitelist(user_id)
            if is_whitelisted:
                # 白名单用户，直接允许下载
                await log_download(user_id, task_id, version, credit_type="whitelist")
            else:
                # 检查下载次数
                credits_check = await check_download_credits(user_id)
                if not credits_check["can_download"]:
                    raise HTTPException(
                        status_code=403,
                        detail={
                            "error": "insufficient_credits",
                            "message": "下载次数不足，请购买订阅或下载次数",
                            "available_credits": credits_check["total_remaining"]
                        }
                    )
                # 消费下载次数
                await consume_download_credit(user_id, task_id, version)
        except Exception as e:
            # 订阅系统异常，优雅降级到匿名模式
            print(f"订阅系统异常，降级到匿名模式: {e}")
            # 继续执行下载，不阻止用户
    
    # 3. 返回文件（现有逻辑，保持不变）
    return FileResponse(
        str(output_file),
        media_type='video/mp4',
        filename=filename,
        headers={
            "Accept-Ranges": "bytes",
            "Content-Disposition": f'attachment; filename="{filename}"'
        }
    )
```

**关键设计**：
- ✅ **向后兼容**：无认证请求直接下载（现有行为）
- ✅ **可选功能**：有认证请求才检查订阅
- ✅ **优雅降级**：订阅系统异常时自动回退到匿名模式
- ✅ **环境控制**：通过环境变量控制是否启用

### 6.4 下载次数检查逻辑

```python
async def check_download_credits(user_id: str) -> dict:
    """
    检查用户可用下载次数
    优先级：白名单 > 订阅 > 购买次数 > 免费周次数
    """
    # 0. 首先检查是否在白名单中
    is_whitelisted = await check_whitelist(user_id)
    if is_whitelisted:
        return {
            "is_whitelisted": True,
            "can_download": True,
            "available_credits": {
                "subscription": 0,
                "purchased": 0,
                "free_weekly": 0
            },
            "total_remaining": float('inf')  # 无限次
        }
    
    # 1. 检查订阅次数
    subscription_credits = await get_subscription_credits(user_id)
    
    # 2. 检查购买次数
    purchased_credits = await get_purchased_credits(user_id)
    
    # 3. 检查免费周次数
    free_weekly_credits = await get_free_weekly_credits(user_id)
    
    total_remaining = (
        subscription_credits['remaining'] +
        purchased_credits['remaining'] +
        free_weekly_credits['remaining']
    )
    
    return {
        "is_whitelisted": False,
        "can_download": total_remaining > 0,
        "available_credits": {
            "subscription": subscription_credits['remaining'],
            "purchased": purchased_credits['remaining'],
            "free_weekly": free_weekly_credits['remaining']
        },
        "total_remaining": total_remaining
    }
```

### 6.6 白名单检查逻辑（带异常处理）

```python
async def check_whitelist(user_id: str) -> bool:
    """检查用户是否在白名单中（带异常处理）"""
    if not SUBSCRIPTION_ENABLED or not SUBSCRIPTION_DB_PATH:
        return False  # 订阅系统未启用
    
    try:
        query = "SELECT id FROM whitelist WHERE user_id = ?"
        result = await db.execute(query, (user_id,))
        return result is not None
    except Exception as e:
        print(f"白名单检查异常: {e}")
        return False  # 异常时返回 False，不影响下载

async def add_to_whitelist(user_id: str, added_by: str, reason: str = None) -> bool:
    """添加用户到白名单（带异常处理）"""
    if not SUBSCRIPTION_ENABLED or not SUBSCRIPTION_DB_PATH:
        raise HTTPException(status_code=503, detail="订阅系统未启用")
    
    try:
        query = """
            INSERT INTO whitelist (user_id, added_by, reason)
            VALUES (?, ?, ?)
        """
        await db.execute(query, (user_id, added_by, reason))
        return True
    except IntegrityError:
        # 用户已在白名单中
        return False
    except Exception as e:
        print(f"添加白名单异常: {e}")
        raise HTTPException(status_code=500, detail=f"添加白名单失败: {str(e)}")

async def remove_from_whitelist(user_id: str) -> bool:
    """从白名单中删除用户（带异常处理）"""
    if not SUBSCRIPTION_ENABLED or not SUBSCRIPTION_DB_PATH:
        raise HTTPException(status_code=503, detail="订阅系统未启用")
    
    try:
        query = "DELETE FROM whitelist WHERE user_id = ?"
        result = await db.execute(query, (user_id,))
        return result.rowcount > 0
    except Exception as e:
        print(f"删除白名单异常: {e}")
        raise HTTPException(status_code=500, detail=f"删除白名单失败: {str(e)}")

async def get_whitelist_users(page: int = 1, limit: int = 20, search: str = None) -> dict:
    """获取白名单用户列表（带异常处理）"""
    if not SUBSCRIPTION_ENABLED or not SUBSCRIPTION_DB_PATH:
        raise HTTPException(status_code=503, detail="订阅系统未启用")
    
    try:
        # ... 现有查询逻辑 ...
    except Exception as e:
        print(f"获取白名单列表异常: {e}")
        raise HTTPException(status_code=500, detail=f"获取白名单列表失败: {str(e)}")
```

### 6.5 消费下载次数逻辑

```python
async def consume_download_credit(user_id: str, task_id: str, version: str) -> dict:
    """
    消费下载次数
    优先级：白名单（不消费）> 免费周次数 > 购买次数 > 订阅次数
    """
    # 0. 首先检查是否在白名单中（白名单用户不消费次数）
    is_whitelisted = await check_whitelist(user_id)
    if is_whitelisted:
        # 记录下载日志，但不消费次数
        await log_download(user_id, task_id, version, credit_type="whitelist")
        return {"credit_type": "whitelist", "remaining": float('inf')}
    
    # 1. 优先使用免费周次数
    free_credit = await get_free_weekly_credit(user_id)
    if free_credit and free_credit['remaining'] > 0:
        await use_credit(free_credit['id'], user_id, task_id, version)
        return {"credit_type": "free_weekly", "remaining": free_credit['remaining'] - 1}
    
    # 2. 使用购买次数
    purchased_credit = await get_purchased_credit(user_id)
    if purchased_credit and purchased_credit['remaining'] > 0:
        await use_credit(purchased_credit['id'], user_id, task_id, version)
        return {"credit_type": "purchase", "remaining": purchased_credit['remaining'] - 1}
    
    # 3. 使用订阅次数
    subscription_credit = await get_subscription_credit(user_id)
    if subscription_credit and subscription_credit['remaining'] > 0:
        await use_credit(subscription_credit['id'], user_id, task_id, version)
        return {"credit_type": "subscription", "remaining": subscription_credit['remaining'] - 1}
    
    raise HTTPException(status_code=403, detail="Insufficient credits")
```

---

## 七、多端同步方案

### 7.1 用户识别

#### iOS App
- 使用 `identifierForVendor` 作为 `device_id`
- 首次使用时，后端生成 `user_id`（UUID）
- 将 `user_id` 存储在 iOS Keychain 中

#### Web
- 使用 Cookie 或 LocalStorage 存储 `user_id`
- 如果用户登录（邮箱/手机），关联到 `user_id`

#### 跨端关联
- 用户可以在 Web 端输入 `user_id` 来关联 iOS App 账户
- 或者通过邮箱/手机号关联

### 7.2 数据同步

- **订阅状态**：存储在服务器，两端实时查询
- **下载次数**：存储在服务器，两端实时查询
- **下载记录**：存储在服务器，两端可查看历史

---

## 八、安全考虑

### 8.1 支付安全
- ✅ **iOS**：使用 App Store 官方验证，后端验证 Receipt
- ✅ **Web**：使用支付平台官方 SDK，验证回调签名
- ✅ **防重放**：使用 Transaction ID 唯一性检查

### 8.2 下载次数安全
- ✅ **服务端验证**：所有下载次数检查在服务端完成
- ✅ **防刷**：记录 IP 地址和 User Agent
- ✅ **限流**：防止频繁请求

### 8.3 用户数据安全
- ✅ **JWT Token**：使用 HTTPS 传输
- ✅ **敏感数据加密**：Receipt 等敏感数据加密存储
- ✅ **定期清理**：清理过期的下载记录和临时数据

---

## 九、管理员界面设计

### 9.1 白名单管理界面

#### 功能需求
1. **查看白名单列表**
   - 显示所有白名单用户
   - 支持搜索（按 user_id、email、phone）
   - 分页显示

2. **添加用户到白名单**
   - 输入 user_id（必填）
   - 输入添加原因（可选）
   - 显示添加结果

3. **删除白名单用户**
   - 从列表中删除用户
   - 确认删除操作

#### 实现方案

**方案1：简单的管理页面（推荐）**
- 创建一个简单的 HTML 管理页面
- 使用管理员密码保护（HTTP Basic Auth 或 Token）
- 部署在后端服务器上（如 `/admin/whitelist.html`）

**方案2：命令行工具**
- 创建 Python 命令行脚本
- 通过 SSH 登录服务器执行管理操作

**方案3：API + 前端管理界面**
- 创建独立的管理后台
- 使用 React/Vue 等框架
- 需要额外的开发时间

**推荐使用方案1**，简单快速，满足基本需求。

### 9.2 管理员认证

```python
# 管理员认证中间件
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "your_secret_admin_token")

async def verify_admin(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    if token != ADMIN_TOKEN:
        raise HTTPException(status_code=403, detail="Admin access required")
    return True
```

---

## 十、零耦合设计确认

### 10.0 设计原则确认

**核心原则：订阅系统与现有功能完全解耦，不影响现有功能的可用性**

#### ✅ 确认点1：现有下载接口保持不变
- **现有行为**：`GET /api/download/{task_id}` 无需认证，直接下载
- **新设计**：保持现有行为，认证信息为**可选**
- **结果**：现有前端代码无需修改，继续正常工作

#### ✅ 确认点2：环境变量控制
- **默认状态**：`SUBSCRIPTION_ENABLED=false`（订阅系统关闭）
- **启用方式**：通过环境变量显式启用
- **结果**：部署订阅系统代码不会影响现有功能

#### ✅ 确认点3：可选认证
- **无认证请求**：直接下载（现有行为）
- **有认证请求**：检查订阅（新功能）
- **结果**：现有用户不受影响，新用户可选择使用订阅功能

#### ✅ 确认点4：优雅降级
- **订阅系统异常**：自动回退到匿名模式
- **数据库连接失败**：不影响下载功能
- **结果**：即使订阅系统出问题，现有功能仍然可用

#### ✅ 确认点5：独立API端点
- **订阅相关API**：使用新的独立端点（如 `/api/subscription/*`）
- **现有API**：完全不变
- **结果**：订阅功能不影响任何现有API

---

## 十一、零耦合实施策略

### 11.1 设计原则

1. **向后兼容**
   - 现有下载接口 `/api/download/{task_id}` 保持完全不变
   - 无认证请求直接下载（现有行为）
   - 现有前端代码无需修改即可继续工作

2. **可选功能**
   - 通过环境变量 `SUBSCRIPTION_ENABLED` 控制是否启用
   - 默认关闭，确保不影响现有功能
   - 认证信息可选，提供则启用订阅检查

3. **优雅降级**
   - 订阅系统异常时自动回退到匿名模式
   - 数据库连接失败不影响下载功能
   - 确保现有功能始终可用

4. **渐进式集成**
   - 后端先实施，前端逐步集成
   - 可以分阶段启用功能
   - 支持 A/B 测试

### 11.2 部署策略

#### 阶段1：后端准备（不影响现有功能）
- 创建订阅系统数据库
- 实现订阅系统 API（独立端点）
- **不修改现有接口**
- 通过环境变量控制，默认关闭

#### 阶段2：前端集成（可选）
- iOS App 集成订阅功能
- Web 前端集成订阅功能
- **现有用户不受影响**（无认证请求继续使用）

#### 阶段3：逐步启用
- 通过环境变量启用订阅系统
- 监控系统稳定性
- 如有问题，立即关闭

### 11.3 环境变量配置

```bash
# .env 文件示例

# 订阅系统开关（默认 false，确保不影响现有功能）
SUBSCRIPTION_ENABLED=false

# 订阅系统数据库路径（可选）
SUBSCRIPTION_DB_PATH=/opt/beatsync/data/subscription.db

# 管理员Token（用于白名单管理）
ADMIN_TOKEN=your_secret_admin_token_here

# JWT密钥（用于用户认证）
JWT_SECRET_KEY=your_jwt_secret_key_here
```

---

## 十二、实施步骤

### Phase 1: 基础架构（1-2周）
1. ✅ 数据库设计和创建（包括白名单表）
2. ✅ 用户认证系统（可选认证）
3. ✅ 基础 API 实现（独立端点，不修改现有接口）
4. ✅ 白名单管理 API
5. ✅ **环境变量配置和开关控制**

### Phase 2: iOS 订阅（2-3周）
1. ✅ StoreKit 集成
2. ✅ 订阅购买流程
3. ✅ 收据验证
4. ✅ 订阅状态管理

### Phase 3: Web 支付（2-3周）
1. ✅ 微信支付集成
2. ✅ 支付宝集成
3. ✅ 支付回调处理

### Phase 4: 下载次数管理（1-2周）
1. ✅ 下载次数检查逻辑（带异常处理）
2. ✅ 消费逻辑（带异常处理）
3. ✅ 免费周次数管理
4. ✅ **优雅降级机制**

### Phase 4.5: 零耦合集成（1周）
1. ✅ **修改下载接口（可选认证，向后兼容）**
2. ✅ **异常处理和降级机制**
3. ✅ **环境变量配置**
4. ✅ **测试现有功能不受影响**

### Phase 5: 前端集成（1-2周）
1. ✅ iOS App UI
2. ✅ Web 订阅页面
3. ✅ 下载前检查提示

### Phase 6: 白名单功能（1周）
1. ✅ 白名单数据库表创建
2. ✅ 白名单检查逻辑
3. ✅ 白名单管理 API
4. ✅ 管理员界面（简单HTML页面）

### Phase 7: 测试和优化（1-2周）
1. ✅ 端到端测试
2. ✅ 性能优化
3. ✅ 安全审计
4. ✅ 白名单功能测试

---

## 十三、优化建议

### 10.1 套餐设计优化

#### 建议1：免费套餐优化
- **当前**：每周2次
- **建议**：首次注册送10次，之后每周2次
- **理由**：提升新用户转化率

#### 建议2：基础版年付优化
- **当前**：99元/年，600次（平均50次/月）
- **建议**：99元/年，700次（平均58次/月，更划算）
- **理由**：提升年付吸引力

#### 建议3：购买次数套餐优化
- **当前**：5元/10次，9元/20次，20元/50次
- **建议**：保持价格，但增加"首次购买送2次"活动
- **理由**：降低首次购买门槛

### 10.2 技术优化

#### 建议1：使用 Redis 缓存
- 缓存用户订阅状态
- 缓存下载次数
- 减少数据库查询

#### 建议2：异步任务队列
- 支付验证异步处理
- 订阅状态更新异步处理
- 提升响应速度

#### 建议3：监控和告警
- 支付成功率监控
- 订阅续订率监控
- 异常告警

---

## 十四、成本估算

### 开发成本
- **后端开发**：3-4周
- **iOS 开发**：2-3周
- **Web 开发**：1-2周
- **测试**：1-2周
- **总计**：7-11周

### 运营成本
- **支付平台手续费**：
  - 微信/支付宝：0.6%
  - App Store：30%（第一年），15%（续订）
- **服务器成本**：现有服务器可支持
- **数据库**：SQLite 或 PostgreSQL（低成本）

---

## 十五、风险评估

### 风险1：支付平台审核
- **iOS**：App Store 审核可能较慢
- **缓解**：提前准备，遵循 Apple 审核指南

### 风险2：支付失败率
- **风险**：用户支付失败影响体验
- **缓解**：提供多种支付方式，优化支付流程

### 风险3：订阅续订率
- **风险**：用户可能忘记续订
- **缓解**：提前提醒，提供自动续订选项

---

## 十六、总结

本方案提供了完整的订阅系统设计，包括：
- ✅ 多端统一的订阅系统
- ✅ 灵活的支付集成方案
- ✅ 完善的下载次数管理
- ✅ 安全可靠的数据存储
- ✅ **白名单管理功能**
- ✅ **零耦合设计**：完全不影响现有功能
- ✅ 清晰的实施步骤

### 零耦合设计特点
- ✅ **向后兼容**：现有下载接口完全不变
- ✅ **可选功能**：通过环境变量控制，默认关闭
- ✅ **优雅降级**：订阅系统异常时自动回退
- ✅ **渐进式集成**：可以分阶段启用功能

### 白名单功能特点
- ✅ **优先级最高**：白名单用户不受任何限制
- ✅ **无限下载**：白名单用户可无限次免费下载
- ✅ **易于管理**：提供简单的管理界面和API
- ✅ **完整记录**：记录添加者、添加原因、添加时间

### 实施保证
- ✅ **现有功能不受影响**：下载接口保持完全向后兼容
- ✅ **可选启用**：通过环境变量控制，默认关闭
- ✅ **异常安全**：订阅系统异常不影响现有功能
- ✅ **渐进式部署**：可以安全地分阶段启用

**建议优先实施 iOS App 订阅系统**，因为：
1. iOS 用户付费意愿更高
2. StoreKit 集成相对简单
3. App Store 支付流程成熟

**Web 支付可以作为补充**，适合：
1. 不想在 App Store 付费的用户
2. 企业用户批量购买
3. 特殊促销活动

请确认此方案是否符合您的需求，如有需要调整的地方，我们可以进一步讨论。


