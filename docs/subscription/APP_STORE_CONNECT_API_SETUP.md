# App Store Connect API 设置指南

## 概述

App Store Connect API **支持**批量创建内购商品！这是 2025 年新增的功能。

## 前提条件

1. **Apple Developer 账号**
2. **App Store Connect 访问权限**（App Manager 或更高）
3. **Python 环境**（用于运行脚本）

## 设置步骤

### 第一步：创建 API Key

1. 登录 [App Store Connect](https://appstoreconnect.apple.com)
2. 进入 **"用户和访问"** → **"密钥"** → **"App Store Connect API"**
3. 点击 **"+"** 创建新密钥
4. 填写信息：
   - **名称**：BeatSync API Key（或任意名称）
   - **访问级别**：选择 **"App Manager"** 或 **"Admin"**
5. 点击 **"生成"**
6. **重要**：下载 `.p8` 文件（只能下载一次！）
7. 记录以下信息：
   - **Key ID**（显示在页面上）
   - **Issuer ID**（显示在页面上）
   - **.p8 文件路径**（下载的文件）

### 第二步：安装依赖

```bash
pip install PyJWT cryptography requests
```

### 第三步：配置环境变量

```bash
export APP_STORE_CONNECT_API_KEY_ID="your_key_id"
export APP_STORE_CONNECT_API_ISSUER_ID="your_issuer_id"
export APP_STORE_CONNECT_API_KEY_PATH="/path/to/AuthKey_XXX.p8"
```

或者创建 `.env` 文件：
```bash
APP_STORE_CONNECT_API_KEY_ID=your_key_id
APP_STORE_CONNECT_API_ISSUER_ID=your_issuer_id
APP_STORE_CONNECT_API_KEY_PATH=/path/to/AuthKey_XXX.p8
```

### 第四步：运行脚本

```bash
cd /Users/scarlett/Projects/BeatSync
python3 scripts/subscription/create_products_via_api.py
```

## 脚本功能

脚本会自动：

1. ✅ **创建订阅组**
   - 基础版订阅组
   - 高级版订阅组

2. ✅ **创建订阅产品**
   - 4 个订阅产品（基础版/高级版 × 月付/年付）
   - 自动关联到订阅组
   - 创建中英文本地化

3. ✅ **创建一次性购买产品**
   - 3 个下载包（10次/20次/50次）
   - 创建中英文本地化

## 注意事项

### ⚠️ 价格设置

**价格设置需要在 App Store Connect 网站手动完成**：
- API 可以创建产品结构
- 但价格配置需要手动设置
- 原因：价格涉及复杂的地区定价策略

### ⚠️ 产品状态

创建后的产品状态为 **"准备提交"**，需要：
1. 在 App Store Connect 网站设置价格
2. 检查所有信息
3. 提交审核

### ⚠️ API 限制

- 有请求频率限制
- 脚本已添加延迟，避免过快请求
- 如果遇到限制，等待后重试

## 验证创建结果

### 在 App Store Connect 网站验证

1. 登录 App Store Connect
2. 进入 **"功能"** → **"App 内购买项目"**
3. 检查所有产品是否已创建
4. 验证产品信息是否正确

### 检查清单

- [ ] 2 个订阅组已创建
- [ ] 4 个订阅产品已创建
- [ ] 3 个一次性购买产品已创建
- [ ] 所有产品ID正确
- [ ] 本地化信息完整
- [ ] 订阅产品已关联到正确的组

## 手动补充步骤

### 1. 设置价格

对于每个产品：
1. 在 App Store Connect 中打开产品
2. 进入 **"价格和可用性"**
3. 设置 CNY 价格
4. 保存

### 2. 提交审核

1. 检查所有产品信息
2. 确保价格已设置
3. 提交产品审核

## 优势

使用 API 创建的优势：

- ✅ **批量创建**：一次创建所有产品
- ✅ **减少错误**：避免手动输入错误
- ✅ **快速高效**：几分钟完成所有创建
- ✅ **可重复**：脚本可以重复运行（会检查重复）

## 如果 API 创建失败

如果 API 创建遇到问题，可以：

1. **检查 API 凭证**：确保 Key ID、Issuer ID、.p8 文件正确
2. **检查权限**：确保 API Key 有足够权限
3. **查看错误信息**：脚本会显示详细错误
4. **手动创建**：参考 `APP_STORE_CONNECT_PRODUCTS_GUIDE.md`

## 相关文件

- `scripts/subscription/create_products_via_api.py` - API 创建脚本
- `ios/App/Products_Config.json` - 产品配置模板
- `docs/subscription/APP_STORE_CONNECT_PRODUCTS_GUIDE.md` - 手动创建指南

