# App Store Connect - 创建 App 配置指南

## 📋 配置选项说明

### 1. 平台 (Platform) ⭐ 必须选择

**选择**：✅ **iOS**

**说明**：
- 勾选 `iOS` 复选框
- 如果将来需要支持其他平台，可以后续添加
- 对于 BeatSync，目前只需要 iOS

---

### 2. 名称 (Name)

**已填写**：`BeatSync` ✅

**说明**：
- 这是 App 在 App Store 中显示的名称
- 当前显示 22 个字符，符合要求（最多 30 个字符）
- 无需修改

---

### 3. 主要语言 (Primary Language) ⭐ 必须选择

**选择**：**简体中文**

**说明**：
1. 点击下拉菜单
2. 选择 **"简体中文"** 或 **"Chinese (Simplified)"**
3. 这是 App 的主要语言，用于 App Store 显示

---

### 4. 套装 ID (Bundle ID)

**已预填**：`BeatSync App - com.beatsync.app` ✅

**说明**：
- 这是之前创建的 App ID
- Bundle ID 为 `com.beatsync.app`
- 无需修改

---

### 5. SKU ⭐ 必须填写

**填写内容**：`beatsync-app`

**说明**：
- SKU（Stock Keeping Unit）是 App 的唯一标识符
- 用于内部管理和追踪
- **格式建议**：使用小写字母和连字符，例如：
  - `beatsync-app`
  - `beatsync-ios`
  - `beatsync-2024`
- **重要**：SKU 一旦创建不能修改，但不会在 App Store 中显示给用户

**推荐填写**：
```
beatsync-app
```

---

### 6. 用户访问权限 (User Access)

**已选择**：`完全访问权限` ✅

**说明**：
- 完全访问权限：所有团队成员都可以访问和管理这个 App
- 有限访问权限：只有特定角色可以访问
- 对于个人开发者或小团队，选择"完全访问权限"即可

---

## ✅ 完整配置清单

### 必须配置的选项

- [ ] **平台**：✅ 勾选 `iOS`
- [ ] **主要语言**：选择 `简体中文`
- [ ] **SKU**：填写 `beatsync-app`
- [ ] **名称**：已填写 `BeatSync` ✅
- [ ] **套装 ID**：已预填 `com.beatsync.app` ✅
- [ ] **用户访问权限**：已选择 `完全访问权限` ✅

---

## 🚀 配置步骤

### 步骤 1：选择平台

1. 在 **"平台"** 部分
2. 勾选 **`iOS`** 复选框

### 步骤 2：选择主要语言

1. 点击 **"主要语言"** 下拉菜单
2. 选择 **"简体中文"** 或 **"Chinese (Simplified)"**

### 步骤 3：填写 SKU

1. 在 **"SKU"** 输入框中
2. 输入：`beatsync-app`
3. 红色警告应该消失

### 步骤 4：检查其他选项

- ✅ 名称：`BeatSync`（已填写）
- ✅ 套装 ID：`com.beatsync.app`（已预填）
- ✅ 用户访问权限：`完全访问权限`（已选择）

### 步骤 5：创建 App

1. 检查所有必填项都已填写
2. 点击右下角的 **"创建"** 按钮
3. 等待 App 创建完成

---

## ⚠️ 重要提示

### SKU 注意事项

1. **唯一性**：
   - SKU 在你的开发者账号中必须唯一
   - 如果 `beatsync-app` 已被使用，可以尝试：
     - `beatsync-app-ios`
     - `beatsync-2024`
     - `beatsync-main`

2. **格式要求**：
   - 只能包含字母、数字、连字符（-）和点（.）
   - 不能包含空格
   - 建议使用小写字母

3. **不能修改**：
   - SKU 一旦创建不能修改
   - 但不会在 App Store 中显示给用户
   - 主要用于内部管理

### 平台选择

- **iOS**：必须选择，这是主要平台
- **其他平台**：可以后续添加，不需要现在选择

---

## 📋 配置示例

**完整配置应该如下**：

```
平台：✅ iOS
名称：BeatSync
主要语言：简体中文
套装 ID：BeatSync App - com.beatsync.app
SKU：beatsync-app
用户访问权限：完全访问权限
```

---

## 🎯 下一步

创建 App 完成后：

1. ✅ App 创建成功
2. ⏳ 创建 App 内购买产品（7个产品）
3. ⏳ 获取 App Store 共享密钥
4. ⏳ 创建沙盒测试账号
5. ⏳ 配置后端环境变量

详细步骤请参考：
- `docs/subscription/APP_STORE_CONNECT_SETUP.md` - 完整配置指南
- `docs/subscription/APP_STORE_CONNECT_QUICK_START.md` - 快速开始指南

---

**配置完成后，点击"创建"按钮！** 🚀
