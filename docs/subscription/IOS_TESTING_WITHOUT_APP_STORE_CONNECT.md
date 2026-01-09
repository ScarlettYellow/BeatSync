# iOS App 集成测试 - 无需 App Store Connect

## 问题

**iOS App 集成测试是否依赖开通 App Store Connect？**

## 答案

### ✅ 不依赖！可以本地测试

**完整测试需要 App Store Connect，但基础测试可以在本地进行，无需 App Store Connect。**

**已创建 StoreKit Configuration File**：`ios/App/Products.storekit`

---

## 测试方案对比

### 方案 1：本地测试（无需 App Store Connect）✅

#### 使用 StoreKit Configuration File

**优点**：
- ✅ **无需 App Store Connect**
- ✅ **无需创建产品**
- ✅ **无需沙盒测试账号**
- ✅ **可以立即开始测试**
- ✅ **完全本地化**

**限制**：
- ⚠️ 只能测试购买流程
- ⚠️ 不能测试真实的收据验证
- ⚠️ 不能测试订阅续费
- ⚠️ 不能测试退款

**适用场景**：
- 开发阶段测试
- UI 流程测试
- 基本功能验证

### 方案 2：沙盒测试（需要 App Store Connect）✅

#### 使用 App Store Connect 沙盒环境

**优点**：
- ✅ **接近真实环境**
- ✅ **可以测试收据验证**
- ✅ **可以测试订阅续费**
- ✅ **可以测试退款**

**限制**：
- ⚠️ 需要 App Store Connect 账号
- ⚠️ 需要创建产品
- ⚠️ 需要沙盒测试账号
- ⚠️ 需要等待 Apple Developer Program 审核通过

**适用场景**：
- 完整功能测试
- 收据验证测试
- 上线前测试

---

## 本地测试方案（推荐先做）

### 使用 StoreKit Configuration File

#### 1. 创建 StoreKit Configuration File

在 Xcode 中：

1. **File** → **New** → **File**
2. 选择 **StoreKit Configuration File**
3. 命名为 `Products.storekit`
4. 保存到项目根目录

#### 2. 配置测试产品

在 StoreKit Configuration File 中添加产品：

```json
{
  "identifier": "Products",
  "nonRenewingSubscriptions": [],
  "products": [
    {
      "displayPrice": "15.00",
      "familyShareable": false,
      "identifier": "basic_monthly",
      "localizations": [
        {
          "description": "基础版月付 - 每月100次下载",
          "displayName": "基础版月付",
          "locale": "zh_CN"
        }
      ],
      "productID": "basic_monthly",
      "referenceName": "基础版月付",
      "type": "SUBSCRIPTION"
    },
    {
      "displayPrice": "99.00",
      "familyShareable": false,
      "identifier": "basic_yearly",
      "localizations": [
        {
          "description": "基础版年付 - 每年1200次下载",
          "displayName": "基础版年付",
          "locale": "zh_CN"
        }
      ],
      "productID": "basic_yearly",
      "referenceName": "基础版年付",
      "type": "SUBSCRIPTION"
    },
    {
      "displayPrice": "69.00",
      "familyShareable": false,
      "identifier": "premium_monthly",
      "localizations": [
        {
          "description": "高级版月付 - 每月300次下载",
          "displayName": "高级版月付",
          "locale": "zh_CN"
        }
      ],
      "productID": "premium_monthly",
      "referenceName": "高级版月付",
      "type": "SUBSCRIPTION"
    },
    {
      "displayPrice": "499.00",
      "familyShareable": false,
      "identifier": "premium_yearly",
      "localizations": [
        {
          "description": "高级版年付 - 每年3600次下载",
          "displayName": "高级版年付",
          "locale": "zh_CN"
        }
      ],
      "productID": "premium_yearly",
      "referenceName": "高级版年付",
      "type": "SUBSCRIPTION"
    },
    {
      "displayPrice": "5.00",
      "familyShareable": false,
      "identifier": "pack_10",
      "localizations": [
        {
          "description": "10次下载包",
          "displayName": "10次下载包",
          "locale": "zh_CN"
        }
      ],
      "productID": "pack_10",
      "referenceName": "10次下载包",
      "type": "NON_CONSUMABLE"
    },
    {
      "displayPrice": "20.00",
      "familyShareable": false,
      "identifier": "pack_50",
      "localizations": [
        {
          "description": "50次下载包",
          "displayName": "50次下载包",
          "locale": "zh_CN"
        }
      ],
      "productID": "pack_50",
      "referenceName": "50次下载包",
      "type": "NON_CONSUMABLE"
    },
    {
      "displayPrice": "35.00",
      "familyShareable": false,
      "identifier": "pack_100",
      "localizations": [
        {
          "description": "100次下载包",
          "displayName": "100次下载包",
          "locale": "zh_CN"
        }
      ],
      "productID": "pack_100",
      "referenceName": "100次下载包",
      "type": "NON_CONSUMABLE"
    }
  ],
  "subscriptionGroups": [
    {
      "id": "21482000",
      "localizations": [],
      "name": "BeatSync Subscriptions",
      "subscriptions": [
        "basic_monthly",
        "basic_yearly",
        "premium_monthly",
        "premium_yearly"
      ]
    }
  ],
  "version": {
    "major": 3,
    "minor": 0
  }
}
```

#### 3. 在 Xcode 中启用 StoreKit Testing

1. **Product** → **Scheme** → **Edit Scheme**
2. 选择 **Run** → **Options**
3. 在 **StoreKit Configuration** 中选择 `Products.storekit`

#### 4. 运行测试

1. 在 Xcode 中运行 App
2. StoreKit 会使用本地配置文件
3. 可以测试购买流程（无需真实支付）
4. 可以测试订阅状态查询

---

## 测试范围对比

### 本地测试（StoreKit Configuration File）

✅ **可以测试**：
- 产品列表获取
- 购买流程 UI
- 订阅状态查询
- 恢复购买流程
- 基本功能验证

❌ **不能测试**：
- 真实的收据验证
- 订阅续费
- 退款处理
- 后端收据验证 API

### 沙盒测试（App Store Connect）

✅ **可以测试**：
- 产品列表获取
- 购买流程 UI
- 订阅状态查询
- 恢复购买流程
- **真实的收据验证**
- **订阅续费**
- **退款处理**
- **后端收据验证 API**

---

## 推荐测试流程

### 阶段 1：本地测试（现在就可以做）✅

**无需 App Store Connect**

1. 创建 StoreKit Configuration File
2. 配置测试产品
3. 在 Xcode 中启用 StoreKit Testing
4. 测试基本功能：
   - 产品列表获取
   - 购买流程
   - 订阅状态查询
   - UI 交互

**时间**：立即可以开始

### 阶段 2：沙盒测试（等待审核通过后）⏳

**需要 App Store Connect**

1. 等待 Apple Developer Program 审核通过
2. 在 App Store Connect 中创建产品
3. 创建沙盒测试账号
4. 测试完整功能：
   - 真实收据验证
   - 后端 API 集成
   - 订阅续费
   - 退款处理

**时间**：等待审核通过后

---

## 总结

### ✅ 可以立即开始的工作

1. **本地测试**（无需 App Store Connect）
   - 创建 StoreKit Configuration File
   - 测试基本购买流程
   - 测试 UI 交互
   - 验证代码逻辑

2. **代码完善**
   - 完善订阅插件代码
   - 优化错误处理
   - 完善 UI 体验

### ⏳ 需要等待的工作

1. **沙盒测试**（需要 App Store Connect）
   - 等待 Apple Developer Program 审核通过
   - 创建产品和沙盒账号
   - 测试真实收据验证

2. **上线准备**
   - 创建正式产品
   - 配置生产环境
   - 上线 App

---

## 建议

**立即开始本地测试**：
- ✅ 无需等待审核
- ✅ 可以验证代码逻辑
- ✅ 可以测试 UI 流程
- ✅ 可以发现问题并修复

**等审核通过后**：
- 进行沙盒测试
- 测试真实收据验证
- 测试完整流程

---

**最后更新**: 2025-12-25
