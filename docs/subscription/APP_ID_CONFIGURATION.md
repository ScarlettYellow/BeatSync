# App ID 配置指南

## 📋 创建 App ID 时的配置选项

### 1. Description（描述）

**填写内容**：
```
BeatSync App
```

或者更详细的描述：
```
BeatSync - 视频节拍同步处理应用
```

**注意事项**：
- ✅ 不能使用特殊字符：`@`, `&`, `*`, `"`
- ✅ 可以使用中文
- ✅ 建议使用简洁明了的名称

---

### 2. Bundle ID（Bundle 标识符）

**已填写**：`com.beatsync.app` ✅

**验证**：
- ✅ 格式正确（反向域名风格）
- ✅ 与代码中的 Bundle ID 一致
- ✅ 不包含星号 `*`

**确认**：这个 Bundle ID 是正确的，无需修改。

---

### 3. Capabilities（功能）配置

#### ✅ 必须启用的功能

**In-App Purchase（应用内购买）** ⭐ **必须启用**

- 位置：在 Capabilities 列表中查找 "In-App Purchase"
- 作用：启用应用内购买和订阅功能
- **这是订阅系统的核心功能，必须启用！**

#### 🔍 如何找到 In-App Purchase

1. 在 Capabilities 列表中向下滚动
2. 或者使用右侧的搜索功能（放大镜图标）
3. 搜索 "In-App Purchase" 或 "Purchase"

#### 📝 其他可选功能

根据你的应用需求，可能还需要：

**Push Notifications（推送通知）**（可选）
- 如果需要订阅到期提醒等功能

**Associated Domains（关联域名）**（可选）
- 如果需要与网站深度集成

**App Groups（应用组）**（可选）
- 如果需要与扩展共享数据

**其他功能**：
- 根据实际需求选择，订阅系统只需要 **In-App Purchase**

---

## ✅ 配置检查清单

### 基本信息
- [ ] Description 已填写（例如：`BeatSync App`）
- [ ] Bundle ID 已填写：`com.beatsync.app`
- [ ] Bundle ID 类型：`Explicit`（精确）

### 功能配置
- [ ] **In-App Purchase（应用内购买）已启用** ⭐ **必须**
- [ ] 其他功能根据需求选择（可选）

---

## 🚀 下一步

配置完成后：

1. **点击 "Continue"（继续）**
2. **检查配置信息**
3. **点击 "Register"（注册）**
4. **等待注册完成**

注册完成后，就可以在 App Store Connect 中使用这个 App ID 创建 App 了！

---

## ⚠️ 重要提示

1. **In-App Purchase 必须启用**
   - 如果没有启用，应用内购买功能将无法使用
   - 订阅系统将无法工作

2. **Bundle ID 不能修改**
   - 一旦注册，Bundle ID 不能更改
   - 确保 `com.beatsync.app` 是正确的

3. **Description 可以修改**
   - 后续可以在 Apple Developer Portal 中修改描述
   - 但建议使用清晰、简洁的描述

---

## 📚 相关文档

- `docs/subscription/APP_STORE_CONNECT_SETUP.md` - App Store Connect 配置指南
- `docs/subscription/APP_STORE_CONNECT_QUICK_START.md` - 快速开始指南

---

**配置完成后，继续创建 App 内购买产品！** 🎉
