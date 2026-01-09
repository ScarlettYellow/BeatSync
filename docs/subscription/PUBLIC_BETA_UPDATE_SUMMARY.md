# 公测期套餐更新总结

## ✅ 已完成的更新

### 1. iOS App 产品ID更新
- ✅ 更新了 `ios/App/SubscriptionPlugin.swift` 中的产品ID映射
- ✅ 移除了年付订阅和旧的产品ID
- ✅ 更新为公测期产品ID：
  - `com.beatsync.public_beta.subscription.basic.monthly`
  - `com.beatsync.public_beta.subscription.premium.monthly`
  - `com.beatsync.public_beta.subscription.pack.10`
  - `com.beatsync.public_beta.subscription.pack.20`

### 2. 后端产品识别更新
- ✅ 更新了 `web_service/backend/subscription_receipt_verification.py`
- ✅ 支持识别公测期产品ID
- ✅ 更新了下载次数配置：
  - 基础版月付：100次 → 20次
  - 高级版月付：1000次 → 100次
  - 10次包：10次（不变）
  - 新增：20次包（20次）

### 3. 后端价格和下载次数配置更新
- ✅ 更新了 `web_service/backend/payment_service.py`
- ✅ 更新了产品价格：
  - 基础版月付：15元 → 4.9元
  - 高级版月付：69元 → 19.9元
  - 10次包：5元（不变）
  - 新增：20次包（9元）
- ✅ 更新了下载次数配置

### 4. 免费体验逻辑更新
- ✅ 更新了 `web_service/backend/subscription_service.py`
- ✅ 从"1周免费试用50次"改为"前5次处理免费"
- ✅ 不再基于注册时间，而是基于已使用的免费次数

### 5. 加油包有效期更新
- ✅ 更新了 `web_service/backend/subscription_receipt_verification.py`
- ✅ 公测期下载次数加油包有效期设置为3个月（90天）

---

## ⏳ 待实现的功能

### 1. 每日处理次数上限检查
- ⏳ 基础版：每日处理次数上限为10次
- ⏳ 高级版：每日处理次数上限为20次
- ⏳ 加油包：每日处理次数上限为10次
- ⏳ 需要在 `/api/process` 接口中添加检查逻辑

### 2. 处理次数统计
- ⏳ 需要记录用户每日的处理次数
- ⏳ 需要按天重置处理次数计数
- ⏳ 需要区分"处理次数"和"下载次数"

---

## 📋 新的套餐配置

### 产品列表

| 产品ID | 类型 | 价格 | 下载次数 | 每日处理上限 | 有效期 |
|--------|------|------|----------|--------------|--------|
| `com.beatsync.public_beta.subscription.basic.monthly` | 订阅 | ¥4.9/月 | 20次/月 | 10次/天 | 1个月 |
| `com.beatsync.public_beta.subscription.premium.monthly` | 订阅 | ¥19.9/月 | 100次/月 | 20次/天 | 1个月 |
| `com.beatsync.public_beta.subscription.pack.10` | 消耗型 | ¥5 | 10次 | 10次/天 | 3个月 |
| `com.beatsync.public_beta.subscription.pack.20` | 消耗型 | ¥9 | 20次 | 10次/天 | 3个月 |

### 免费体验
- **权益**：前5次处理免费
- **说明**：不基于时间，基于已使用的免费次数

---

## 🔍 代码变更位置

### iOS App
- `ios/App/SubscriptionPlugin.swift` - 产品ID映射

### 后端
- `web_service/backend/subscription_receipt_verification.py` - 产品识别和下载次数配置
- `web_service/backend/payment_service.py` - 产品价格和下载次数配置
- `web_service/backend/subscription_service.py` - 免费体验逻辑

---

## ⚠️ 注意事项

1. **向后兼容**：代码中保留了旧产品ID的兼容逻辑，但建议使用新的公测期产品ID

2. **每日处理次数上限**：目前还未实现，需要在 `/api/process` 接口中添加检查

3. **处理次数 vs 下载次数**：
   - **处理次数**：用户上传视频并开始处理的次数（需要限制）
   - **下载次数**：用户下载处理结果的次数（已有限制）

4. **测试**：更新后需要测试：
   - 产品购买流程
   - 下载次数消费
   - 免费体验逻辑（前5次免费）
   - 加油包有效期（3个月）

---

**更新完成！下一步：实现每日处理次数上限检查。** 🚀
