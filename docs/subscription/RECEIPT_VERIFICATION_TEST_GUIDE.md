# 收据验证测试指南

## 概述

收据验证测试脚本 (`test_receipt_verification.py`) 模拟 iOS StoreKit 2 收据验证流程，测试订阅系统的收据验证功能。

## 测试覆盖范围

### 1. 用户注册
- 新用户注册
- 获取 Token 和 User ID

### 2. 验证订阅收据
- 模拟 Basic Monthly 订阅收据
- 调用收据验证 API
- 验证订阅保存到数据库

### 3. 验证一次性购买收据
- 模拟 10次下载包收据
- 调用收据验证 API
- 验证购买记录保存到数据库

### 4. 验证订阅状态
- 查询订阅状态（验证后）
- 验证订阅信息正确显示
- 验证下载次数正确添加

### 5. 查询订阅历史
- 查询所有订阅记录
- 验证订阅记录完整

### 6. 验证多个产品
- 测试不同订阅类型（Premium Yearly）
- 验证不同产品正确处理

## 使用方法

### 前置条件

1. **启动后端服务**
   ```bash
   cd web_service/backend
   python main.py
   # 或
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```

2. **设置环境变量（可选）**
   ```bash
   export SUBSCRIPTION_ENABLED=true
   export ADMIN_TOKEN=test_admin_token_12345
   export JWT_SECRET_KEY=test_jwt_secret_key_12345
   # 注意: APP_STORE_SHARED_SECRET 不需要设置（测试使用模拟收据）
   ```

3. **初始化数据库**
   ```bash
   python subscription_db.py
   ```

### 运行测试

```bash
cd web_service/backend
python test_receipt_verification.py
```

## 测试说明

### 模拟收据数据

测试脚本使用**模拟收据数据**，不进行实际的 App Store 验证。模拟收据数据格式：

```json
{
  "purchaseDate": 1703500800000,
  "productId": "basic_monthly",
  "expirationDate": 1706092800000  // 仅订阅有
}
```

收据数据会被 Base64 编码后发送到 API。

### 实际环境 vs 测试环境

**测试环境（当前脚本）**:
- ✅ 使用模拟收据数据
- ✅ 不调用 App Store 验证 API
- ✅ 直接保存订阅到数据库
- ✅ 适合功能测试

**实际环境**:
- 需要配置 `APP_STORE_SHARED_SECRET`
- 调用 App Store 验证 API
- 验证收据真实性
- 处理验证失败情况

## API 端点

### `POST /api/subscription/verify-receipt`

**参数**:
- `transaction_id`: 交易ID（字符串）
- `product_id`: 产品ID（如 `basic_monthly`, `pack_10`）
- `receipt_data`: Base64 编码的收据数据（JSON格式）
- `platform`: 平台（默认 `"ios"`）

**认证**: 需要用户 Token（通过 `Authorization: Bearer <token>` 头部）

**响应**:
```json
{
  "success": true,
  "message": "收据验证成功",
  "subscription_id": 1
}
```

## 测试流程

1. **用户注册** → 获取 Token 和 User ID
2. **创建模拟收据** → 生成 Base64 编码的收据数据
3. **调用验证 API** → 发送收据到 `/api/subscription/verify-receipt`
4. **验证数据库** → 检查订阅/购买记录是否保存
5. **验证状态** → 查询订阅状态，确认信息正确
6. **查询历史** → 验证订阅历史记录

## 预期输出

```
======================================================================
  收据验证测试 - iOS StoreKit 2 集成
======================================================================

[1] 用户注册
----------------------------------------------------------------------
   ✅ 注册成功
   User ID: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
   Token: xxxxxxxx...

[2] 验证订阅收据（Basic Monthly）
----------------------------------------------------------------------
   收据信息:
   产品ID: basic_monthly
   交易ID: test_transaction_xxxxx
   收据数据长度: xxx 字符

   API 响应:
   状态码: 200
   ✅ 收据验证成功

...

======================================================================
  测试结果汇总
======================================================================
用户注册: ✅ 通过
验证订阅收据: ✅ 通过
验证订阅状态: ✅ 通过
查询订阅历史: ✅ 通过
验证一次性购买收据: ✅ 通过
验证订阅状态（包含购买）: ✅ 通过
验证多个产品: ✅ 通过

总计: 7/7 通过

🎉 所有测试通过！
```

## 注意事项

1. **模拟收据数据**
   - 测试脚本使用模拟收据，不进行实际 App Store 验证
   - 实际环境中需要真实的收据数据和 `APP_STORE_SHARED_SECRET`

2. **数据库操作**
   - 测试数据会保存到数据库
   - 不会自动清理测试数据

3. **时间同步**
   - 测试脚本在 API 调用后等待 1 秒，确保数据库更新
   - 如果测试失败，可能需要增加等待时间

4. **产品类型**
   - 支持的产品类型：
     - 订阅: `basic_monthly`, `basic_yearly`, `premium_monthly`, `premium_yearly`
     - 购买: `pack_10`, `pack_50`, `pack_100`

## 故障排除

### 测试失败：收据验证失败
- 检查后端服务是否运行
- 检查 `SUBSCRIPTION_ENABLED` 环境变量
- 检查数据库是否已初始化
- 检查收据数据格式是否正确

### 测试失败：订阅未保存
- 检查数据库连接
- 检查数据库表结构
- 查看后端日志

### 测试失败：订阅状态不正确
- 等待数据库更新（增加等待时间）
- 检查订阅查询逻辑
- 检查时间格式

## 下一步

完成收据验证测试后，可以：

1. **iOS App 集成**
   - 在 iOS App 中实现 StoreKit 2 购买流程
   - 调用收据验证 API
   - 处理验证结果

2. **实际收据验证**
   - 配置 `APP_STORE_SHARED_SECRET`
   - 测试真实的 App Store 收据验证
   - 处理验证失败情况

3. **错误处理**
   - 测试各种错误情况
   - 实现错误重试机制
   - 实现降级处理
