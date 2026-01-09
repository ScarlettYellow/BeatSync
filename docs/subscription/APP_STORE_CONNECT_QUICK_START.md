# App Store Connect 配置 - 快速开始

## 🎯 现在需要做的 5 件事

### ✅ 1. 创建 App（如果还没有）

1. 登录 [App Store Connect](https://appstoreconnect.apple.com)
2. **"我的 App"** → **"+"** → **"新建 App"**
3. 填写信息：
   - Bundle ID: `com.beatsync.app`
   - 名称: `BeatSync`
   - 主要语言: `简体中文`

---

### ✅ 2. 创建 7 个 App 内购买产品

**位置**：App Store Connect → 你的 App → **"功能"** → **"App 内购买项目"**

#### 订阅产品（4个）

| 产品 ID | 类型 | 价格 | 下载次数 |
|---------|------|------|----------|
| `com.beatsync.subscription.basic.monthly` | 自动续订订阅 | ¥15/月 | 100次/月 |
| `com.beatsync.subscription.basic.yearly` | 自动续订订阅 | ¥99/年 | 1200次/年 |
| `com.beatsync.subscription.premium.monthly` | 自动续订订阅 | ¥69/月 | 300次/月 |
| `com.beatsync.subscription.premium.yearly` | 自动续订订阅 | ¥499/年 | 3600次/年 |

#### 一次性购买（3个）

| 产品 ID | 类型 | 价格 | 下载次数 |
|---------|------|------|----------|
| `com.beatsync.pack.10` | 非消耗型产品 | ¥5 | 10次 |
| `com.beatsync.pack.50` | 非消耗型产品 | ¥20 | 50次 |
| `com.beatsync.pack.100` | 非消耗型产品 | ¥35 | 100次 |

**重要**：
- ⚠️ 产品 ID 必须与代码中的**完全一致**
- ⚠️ 创建后需要等待 Apple 审核（通常几分钟到几小时）

---

### ✅ 3. 获取 App Store 共享密钥

1. App Store Connect → **"用户和访问"** → **"密钥"**
2. 找到 **"App Store 共享密钥"**
3. 点击 **"生成"** 或 **"查看"**
4. **立即复制并保存**（只显示一次！）

---

### ✅ 4. 创建沙盒测试账号

1. App Store Connect → **"用户和访问"** → **"沙盒测试员"**
2. 点击 **"+"** → **"新建沙盒测试员"**
3. 填写信息：
   - 使用**未注册过 Apple ID 的邮箱**
   - 设置密码（至少8位）
   - 国家/地区：`中国`
4. 点击 **"创建"**

**建议**：创建 2-3 个测试账号用于不同场景测试

---

### ✅ 5. 配置后端环境变量

在服务器上设置：

```bash
export SUBSCRIPTION_ENABLED=true
export APP_STORE_SHARED_SECRET=你的共享密钥
export ADMIN_TOKEN=你的管理员令牌
export JWT_SECRET_KEY=你的JWT密钥
```

然后重启后端服务。

---

## 📋 快速检查清单

### App Store Connect
- [ ] App 已创建
- [ ] 7 个产品已创建（4个订阅 + 3个一次性）
- [ ] 产品 ID 与代码完全一致
- [ ] App Store 共享密钥已获取
- [ ] 沙盒测试账号已创建

### 后端配置
- [ ] `APP_STORE_SHARED_SECRET` 已设置
- [ ] 后端服务已重启
- [ ] 订阅系统已启用

---

## 🚀 完成后

配置完成后，可以开始测试：

1. **在设备上登录沙盒账号**
   - 设置 → App Store → 退出当前账号
   - 在 App 内购买时使用沙盒账号登录

2. **测试购买流程**
   - 运行 App
   - 打开订阅管理
   - 测试购买

---

## 📚 详细文档

完整配置步骤请参考：
- `docs/subscription/APP_STORE_CONNECT_SETUP.md` - 详细配置指南

测试步骤请参考：
- `docs/subscription/IOS_TESTING_GUIDE.md` - 完整测试指南
- `docs/subscription/IOS_TESTING_STEPS.md` - 详细测试步骤

---

**开始配置吧！** 🎉
