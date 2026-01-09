# Web 支付集成暂停说明

## 当前状态

### ⏸️ 暂停启用

**Web 支付集成（微信/支付宝）的框架代码已完成，但暂时不启用。**

## 原因

申请支付商户号需要营业执照，当前没有营业执照，暂时不配置支付商户号。

## 已完成的工作

### ✅ 框架代码

1. **后端实现**
   - `payment_service.py` - 支付服务模块
   - API 端点：创建订单、支付回调、查询状态
   - 数据库集成：支付记录保存

2. **前端实现**
   - `payment.js` - Web 支付服务
   - `script.js` - 支付流程集成
   - 自动环境检测（iOS App vs Web）

### 📁 相关文件

- `web_service/backend/payment_service.py` - 支付服务模块
- `web_service/backend/main.py` - 支付 API 端点
- `web_service/frontend/payment.js` - 前端支付服务
- `web_service/frontend/script.js` - 支付流程集成
- `web_service/backend/requirements.txt` - 支付依赖（已添加）

## 后续计划

### 等获得营业执照后

1. **申请支付商户号**
   - 微信支付商户号
   - 支付宝商户号

2. **配置环境变量**
   ```bash
   WECHAT_PAY_APPID=your_wechat_appid
   WECHAT_PAY_MCHID=your_wechat_mchid
   WECHAT_PAY_API_KEY=your_wechat_api_key
   ALIPAY_APPID=your_alipay_appid
   ALIPAY_PRIVATE_KEY=your_alipay_private_key
   ALIPAY_PUBLIC_KEY=your_alipay_public_key
   ```

3. **集成支付 SDK**
   - 修改 `payment_service.py` 集成真实 SDK
   - 实现真实的支付 URL 生成
   - 实现支付回调签名验证

4. **测试和上线**
   - 使用沙盒环境测试
   - 测试支付流程
   - 上线支付功能

## 当前影响

### ✅ 不影响现有功能

- iOS App 支付（StoreKit）正常工作
- 订阅系统其他功能正常工作
- Web 用户暂时只能通过 iOS App 购买

### 📝 用户体验

- Web 用户点击购买时会提示需要配置支付商户号
- 建议 Web 用户使用 iOS App 进行购买

## 代码保留

所有已实现的代码都会保留，等以后需要时可以：
1. 配置支付商户号
2. 集成真实支付 SDK
3. 启用支付功能

**无需重新开发，只需配置和集成 SDK。**

---

**最后更新**: 2025-12-25
**状态**: ⏸️ 暂停，等待营业执照和支付商户号
