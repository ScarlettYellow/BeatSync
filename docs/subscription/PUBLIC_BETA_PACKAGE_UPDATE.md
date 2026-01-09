# 公测期套餐更新指南

## 📋 新的套餐设计

### 1. 免费体验套餐
- **权益**：前5次处理免费

### 2. 公测期基础版套餐
- **产品ID**：`com.beatsync.public_beta.subscription.basic.monthly`
- **价格**：4.9元/月
- **权益**：
  - 可高清下载20次满意作品
  - 每日处理次数上限为10次

### 3. 公测期高级版套餐
- **产品ID**：`com.beatsync.public_beta.subscription.premium.monthly`
- **价格**：19.9元/月
- **权益**：
  - 可高清下载100次
  - 每日处理次数上限为20次

### 4. 公测期下载次数加油包（10次）
- **产品ID**：`com.beatsync.public_beta.subscription.pack.10`
- **价格**：5元/10次
- **权益**：
  - 可高清下载10次
  - 每日处理次数上限为10次
  - 有效期3个月

### 5. 公测期下载次数加油包（20次）
- **产品ID**：`com.beatsync.public_beta.subscription.pack.20`
- **价格**：9元/20次
- **权益**：
  - 可高清下载20次
  - 每日处理次数上限为10次
  - 有效期3个月

---

## 🔄 需要更新的文件

### 1. iOS App 代码
- `ios/App/SubscriptionPlugin.swift` - 更新产品ID映射

### 2. 后端代码
- `web_service/backend/subscription_receipt_verification.py` - 更新产品类型识别和下载次数配置
- `web_service/backend/payment_service.py` - 更新产品价格和下载次数配置
- `web_service/backend/subscription_service.py` - 更新免费试用逻辑（前5次处理免费）

### 3. 前端代码（如需要）
- `web_service/frontend/subscription.js` - 可能需要更新产品ID显示

---

## ⚠️ 重要变更

### 产品ID变更
- 旧：`com.beatsync.subscription.basic.monthly`
- 新：`com.beatsync.public_beta.subscription.basic.monthly`

- 旧：`com.beatsync.pack.10`
- 新：`com.beatsync.public_beta.subscription.pack.10`

### 下载次数变更
- 基础版月付：100次 → 20次
- 高级版月付：300次 → 100次
- 10次包：10次（不变）
- 新增：20次包（20次）

### 新增功能
- 每日处理次数上限（基础版：10次/天，高级版：20次/天）
- 加油包有效期（3个月）
- 免费体验：前5次处理免费（替代原来的1周免费试用）

---

## 📝 更新检查清单

- [ ] 更新 iOS App 产品ID映射
- [ ] 更新后端产品类型识别
- [ ] 更新下载次数配置
- [ ] 更新价格配置
- [ ] 更新免费试用逻辑（前5次处理免费）
- [ ] 实现每日处理次数上限检查
- [ ] 实现加油包有效期检查
- [ ] 更新前端产品显示（如需要）
- [ ] 测试所有产品购买流程
- [ ] 测试下载次数消费
- [ ] 测试每日处理次数限制

---

**开始更新代码！** 🚀
