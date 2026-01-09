# Web 支付集成实现文档

## 概述

本文档说明 Web 支付集成（微信支付和支付宝）的实现情况。

## 实现状态

### ✅ 已完成（框架代码）

1. **后端支付服务模块** (`payment_service.py`)
   - ✅ 创建支付订单功能
   - ✅ 微信支付 URL 生成（框架）
   - ✅ 支付宝支付 URL 生成（框架）
   - ✅ 支付回调验证（框架）
   - ✅ 支付状态更新
   - ✅ 支付状态查询

2. **后端 API 端点**
   - ✅ `POST /api/payment/create` - 创建支付订单
   - ✅ `POST /api/payment/callback/wechat` - 微信支付回调
   - ✅ `POST /api/payment/callback/alipay` - 支付宝支付回调
   - ✅ `GET /api/payment/status/{order_id}` - 查询支付状态

3. **前端支付服务** (`payment.js`)
   - ✅ 创建支付订单
   - ✅ 查询支付状态
   - ✅ 轮询支付状态
   - ✅ 跳转到支付页面

4. **前端集成**
   - ✅ 修改 `handlePurchase` 函数支持 Web 支付
   - ✅ 添加 `handleWebPurchase` 函数
   - ✅ 自动检测环境（iOS App vs Web）
   - ✅ 支付方式选择（微信/支付宝）

### ⏸️ 暂停（等待营业执照和支付商户号）

**当前状态**：框架代码已完成，但暂时不启用。

**原因**：
- 申请支付商户号需要营业执照
- 当前没有营业执照
- 暂时不配置支付商户号

**后续计划**：
- 等获得营业执照后申请支付商户号
- 配置支付商户号后集成真实支付 SDK
- 测试和上线支付功能

### ⏳ 待完成（需要配置支付商户号后）

1. **微信支付 SDK 集成**
   - ⏳ 集成 `wechatpay-python` SDK
   - ⏳ 配置微信支付商户号
   - ⏳ 实现真实的支付 URL 生成
   - ⏳ 实现支付回调签名验证

2. **支付宝 SDK 集成**
   - ⏳ 集成 `alipay-sdk-python` SDK
   - ⏳ 配置支付宝商户号
   - ⏳ 实现真实的支付 URL 生成
   - ⏳ 实现支付回调签名验证

3. **前端支付页面**
   - ⏳ 创建支付结果页面
   - ⏳ 实现支付状态轮询页面
   - ⏳ 优化支付流程用户体验

## 当前实现（模拟环境）

### 后端实现

当前实现是**框架代码**，包含：
- 支付订单创建和保存到数据库
- 支付回调处理框架
- 支付状态更新逻辑

但**未集成真实的支付 SDK**，因为需要：
- 微信支付商户号
- 支付宝商户号
- 支付 API 密钥

### 前端实现

当前实现：
- 自动检测环境（iOS App vs Web）
- iOS App 使用 StoreKit 购买
- Web 使用 Web 支付 API
- 支付方式选择（微信/支付宝）
- 模拟支付流程（用于测试）

## 配置说明

### 环境变量

需要在 `.env` 文件中配置：

```bash
# 微信支付配置
WECHAT_PAY_APPID=your_wechat_appid
WECHAT_PAY_MCHID=your_wechat_mchid
WECHAT_PAY_API_KEY=your_wechat_api_key
WECHAT_PAY_CERT_PATH=/path/to/cert.pem  # 可选

# 支付宝配置
ALIPAY_APPID=your_alipay_appid
ALIPAY_PRIVATE_KEY=your_alipay_private_key
ALIPAY_PUBLIC_KEY=your_alipay_public_key
ALIPAY_SIGN_TYPE=RSA2

# 支付回调 URL（自动从 BASE_URL 生成）
BASE_URL=https://beatsync.site
```

### 产品价格配置

在 `payment_service.py` 中配置：

```python
PRODUCT_PRICES = {
    "basic_monthly": 15.00,
    "basic_yearly": 99.00,
    "premium_monthly": 69.00,
    "premium_yearly": 499.00,
    "pack_10": 5.00,
    "pack_50": 20.00,
    "pack_100": 35.00,
}
```

## 支付流程

### 1. 创建支付订单

```
用户点击购买
→ 前端调用 /api/payment/create
→ 后端创建订单并保存到数据库
→ 返回支付 URL
→ 前端跳转到支付页面
```

### 2. 支付回调

```
用户完成支付
→ 支付平台回调 /api/payment/callback/wechat 或 /api/payment/callback/alipay
→ 后端验证支付签名
→ 更新支付订单状态
→ 更新订阅/下载次数
→ 返回成功响应给支付平台
```

### 3. 支付状态查询

```
用户查询支付状态
→ 前端调用 /api/payment/status/{order_id}
→ 后端查询数据库
→ 返回订单状态
```

## 下一步

### 1. 申请支付商户号

- **微信支付**：访问 https://pay.weixin.qq.com/
- **支付宝**：访问 https://open.alipay.com/

### 2. 集成支付 SDK

修改 `payment_service.py`：
- 集成 `wechatpay-python` SDK
- 集成 `alipay-sdk-python` SDK
- 实现真实的支付 URL 生成
- 实现支付回调签名验证

### 3. 测试支付流程

- 使用沙盒环境测试
- 测试支付回调
- 测试支付状态更新
- 测试订阅/下载次数更新

### 4. 上线部署

- 配置生产环境变量
- 部署到生产服务器
- 监控支付流程

## 注意事项

1. **安全性**
   - 支付回调必须验证签名
   - 支付金额必须验证
   - 订单状态必须验证

2. **错误处理**
   - 支付失败处理
   - 网络错误处理
   - 超时处理

3. **用户体验**
   - 支付状态实时更新
   - 支付结果页面
   - 支付失败提示

## 测试

### 模拟环境测试

当前可以使用模拟环境测试：
1. 创建支付订单（会返回模拟 URL）
2. 模拟支付成功（手动触发）
3. 验证订阅状态更新

### 真实环境测试

需要配置支付商户号后：
1. 使用沙盒环境测试
2. 测试真实支付流程
3. 测试支付回调

---

**最后更新**: 2025-12-25
