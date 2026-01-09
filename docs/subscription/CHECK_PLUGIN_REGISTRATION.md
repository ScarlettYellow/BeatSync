# 检查插件注册状态

## 在 Safari Web Inspector 控制台中执行以下代码

**注意**：如果出现 `SyntaxError`，请先刷新页面或清除控制台，然后重新执行。

### 步骤 1：检查 Capacitor 和插件

```javascript
// 清除之前的变量（如果存在）
if (typeof plugin !== 'undefined') {
    delete window.plugin;
}

// 检查 Capacitor
console.log('1. Capacitor 是否存在:', typeof window.Capacitor !== 'undefined');
console.log('2. Capacitor 对象:', window.Capacitor);

// 检查 Plugins
console.log('3. Plugins 是否存在:', !!window.Capacitor?.Plugins);
console.log('4. Plugins 对象:', window.Capacitor?.Plugins);

// 列出所有插件
const allPlugins = window.Capacitor?.Plugins ? Object.keys(window.Capacitor.Plugins) : [];
console.log('5. 所有插件:', allPlugins);

// 检查 SubscriptionPlugin
const subscriptionPlugin = window.Capacitor?.Plugins?.SubscriptionPlugin;
console.log('6. SubscriptionPlugin:', subscriptionPlugin);
console.log('7. SubscriptionPlugin 类型:', typeof subscriptionPlugin);
```

### 步骤 2：如果插件存在，检查方法

```javascript
if (subscriptionPlugin) {
    console.log('8. 插件方法:', Object.keys(subscriptionPlugin));
    console.log('9. getAvailableProducts 类型:', typeof subscriptionPlugin.getAvailableProducts);
} else {
    console.error('❌ SubscriptionPlugin 未找到！');
    console.log('可用的插件:', allPlugins);
}
```

### 步骤 3：如果插件存在，测试调用

```javascript
if (subscriptionPlugin && typeof subscriptionPlugin.getAvailableProducts === 'function') {
    console.log('10. 开始测试调用...');
    try {
        const result = await subscriptionPlugin.getAvailableProducts();
        console.log('11. ✅ 调用成功:', result);
    } catch (error) {
        console.error('12. ❌ 调用失败:', error);
        console.error('错误详情:', {
            message: error.message,
            stack: error.stack,
            name: error.name
        });
    }
} else {
    console.error('❌ 插件或方法不存在，无法测试');
}
```

---

## 预期结果

### 如果插件已正确注册：

```
1. Capacitor 是否存在: true
2. Capacitor 对象: {...}
3. Plugins 是否存在: true
4. Plugins 对象: {...}
5. 所有插件: ["SubscriptionPlugin", "SaveToGallery", "Camera", "Filesystem", "Share"]
6. SubscriptionPlugin: {...}
7. SubscriptionPlugin 类型: object
8. 插件方法: ["getAvailableProducts", "purchase", "getSubscriptionStatus", "restorePurchases", "checkSubscriptionAvailability"]
9. getAvailableProducts 类型: function
10. 开始测试调用...
11. ✅ 调用成功: {products: [...], count: 4}
```

### 如果插件未注册：

```
5. 所有插件: ["SaveToGallery", "Camera", "Filesystem", "Share"]  // 没有 SubscriptionPlugin
6. SubscriptionPlugin: undefined
7. SubscriptionPlugin 类型: undefined
❌ SubscriptionPlugin 未找到！
```

---

## 如果插件未注册

### 可能的原因：

1. **插件文件没有被编译到 App 中**
   - 检查 Xcode 项目设置
   - 确认 `SubscriptionPlugin.m` 和 `SubscriptionPlugin.swift` 在 "App" target 中

2. **插件注册宏有问题**
   - 检查 `SubscriptionPlugin.m` 中的 `CAP_PLUGIN` 宏
   - 确认插件ID是 "SubscriptionPlugin"

3. **需要重新构建项目**
   - 在 Xcode 中清理构建：`Product` → `Clean Build Folder`（`⌘ + Shift + K`）
   - 重新构建：`Product` → `Build`（`⌘ + B`）

---

**请执行上述代码并告诉我结果！** 🔍







# 检查插件注册状态

## 在 Safari Web Inspector 控制台中执行以下代码

**注意**：如果出现 `SyntaxError`，请先刷新页面或清除控制台，然后重新执行。

### 步骤 1：检查 Capacitor 和插件

```javascript
// 清除之前的变量（如果存在）
if (typeof plugin !== 'undefined') {
    delete window.plugin;
}

// 检查 Capacitor
console.log('1. Capacitor 是否存在:', typeof window.Capacitor !== 'undefined');
console.log('2. Capacitor 对象:', window.Capacitor);

// 检查 Plugins
console.log('3. Plugins 是否存在:', !!window.Capacitor?.Plugins);
console.log('4. Plugins 对象:', window.Capacitor?.Plugins);

// 列出所有插件
const allPlugins = window.Capacitor?.Plugins ? Object.keys(window.Capacitor.Plugins) : [];
console.log('5. 所有插件:', allPlugins);

// 检查 SubscriptionPlugin
const subscriptionPlugin = window.Capacitor?.Plugins?.SubscriptionPlugin;
console.log('6. SubscriptionPlugin:', subscriptionPlugin);
console.log('7. SubscriptionPlugin 类型:', typeof subscriptionPlugin);
```

### 步骤 2：如果插件存在，检查方法

```javascript
if (subscriptionPlugin) {
    console.log('8. 插件方法:', Object.keys(subscriptionPlugin));
    console.log('9. getAvailableProducts 类型:', typeof subscriptionPlugin.getAvailableProducts);
} else {
    console.error('❌ SubscriptionPlugin 未找到！');
    console.log('可用的插件:', allPlugins);
}
```

### 步骤 3：如果插件存在，测试调用

```javascript
if (subscriptionPlugin && typeof subscriptionPlugin.getAvailableProducts === 'function') {
    console.log('10. 开始测试调用...');
    try {
        const result = await subscriptionPlugin.getAvailableProducts();
        console.log('11. ✅ 调用成功:', result);
    } catch (error) {
        console.error('12. ❌ 调用失败:', error);
        console.error('错误详情:', {
            message: error.message,
            stack: error.stack,
            name: error.name
        });
    }
} else {
    console.error('❌ 插件或方法不存在，无法测试');
}
```

---

## 预期结果

### 如果插件已正确注册：

```
1. Capacitor 是否存在: true
2. Capacitor 对象: {...}
3. Plugins 是否存在: true
4. Plugins 对象: {...}
5. 所有插件: ["SubscriptionPlugin", "SaveToGallery", "Camera", "Filesystem", "Share"]
6. SubscriptionPlugin: {...}
7. SubscriptionPlugin 类型: object
8. 插件方法: ["getAvailableProducts", "purchase", "getSubscriptionStatus", "restorePurchases", "checkSubscriptionAvailability"]
9. getAvailableProducts 类型: function
10. 开始测试调用...
11. ✅ 调用成功: {products: [...], count: 4}
```

### 如果插件未注册：

```
5. 所有插件: ["SaveToGallery", "Camera", "Filesystem", "Share"]  // 没有 SubscriptionPlugin
6. SubscriptionPlugin: undefined
7. SubscriptionPlugin 类型: undefined
❌ SubscriptionPlugin 未找到！
```

---

## 如果插件未注册

### 可能的原因：

1. **插件文件没有被编译到 App 中**
   - 检查 Xcode 项目设置
   - 确认 `SubscriptionPlugin.m` 和 `SubscriptionPlugin.swift` 在 "App" target 中

2. **插件注册宏有问题**
   - 检查 `SubscriptionPlugin.m` 中的 `CAP_PLUGIN` 宏
   - 确认插件ID是 "SubscriptionPlugin"

3. **需要重新构建项目**
   - 在 Xcode 中清理构建：`Product` → `Clean Build Folder`（`⌘ + Shift + K`）
   - 重新构建：`Product` → `Build`（`⌘ + B`）

---

**请执行上述代码并告诉我结果！** 🔍







# 检查插件注册状态

## 在 Safari Web Inspector 控制台中执行以下代码

**注意**：如果出现 `SyntaxError`，请先刷新页面或清除控制台，然后重新执行。

### 步骤 1：检查 Capacitor 和插件

```javascript
// 清除之前的变量（如果存在）
if (typeof plugin !== 'undefined') {
    delete window.plugin;
}

// 检查 Capacitor
console.log('1. Capacitor 是否存在:', typeof window.Capacitor !== 'undefined');
console.log('2. Capacitor 对象:', window.Capacitor);

// 检查 Plugins
console.log('3. Plugins 是否存在:', !!window.Capacitor?.Plugins);
console.log('4. Plugins 对象:', window.Capacitor?.Plugins);

// 列出所有插件
const allPlugins = window.Capacitor?.Plugins ? Object.keys(window.Capacitor.Plugins) : [];
console.log('5. 所有插件:', allPlugins);

// 检查 SubscriptionPlugin
const subscriptionPlugin = window.Capacitor?.Plugins?.SubscriptionPlugin;
console.log('6. SubscriptionPlugin:', subscriptionPlugin);
console.log('7. SubscriptionPlugin 类型:', typeof subscriptionPlugin);
```

### 步骤 2：如果插件存在，检查方法

```javascript
if (subscriptionPlugin) {
    console.log('8. 插件方法:', Object.keys(subscriptionPlugin));
    console.log('9. getAvailableProducts 类型:', typeof subscriptionPlugin.getAvailableProducts);
} else {
    console.error('❌ SubscriptionPlugin 未找到！');
    console.log('可用的插件:', allPlugins);
}
```

### 步骤 3：如果插件存在，测试调用

```javascript
if (subscriptionPlugin && typeof subscriptionPlugin.getAvailableProducts === 'function') {
    console.log('10. 开始测试调用...');
    try {
        const result = await subscriptionPlugin.getAvailableProducts();
        console.log('11. ✅ 调用成功:', result);
    } catch (error) {
        console.error('12. ❌ 调用失败:', error);
        console.error('错误详情:', {
            message: error.message,
            stack: error.stack,
            name: error.name
        });
    }
} else {
    console.error('❌ 插件或方法不存在，无法测试');
}
```

---

## 预期结果

### 如果插件已正确注册：

```
1. Capacitor 是否存在: true
2. Capacitor 对象: {...}
3. Plugins 是否存在: true
4. Plugins 对象: {...}
5. 所有插件: ["SubscriptionPlugin", "SaveToGallery", "Camera", "Filesystem", "Share"]
6. SubscriptionPlugin: {...}
7. SubscriptionPlugin 类型: object
8. 插件方法: ["getAvailableProducts", "purchase", "getSubscriptionStatus", "restorePurchases", "checkSubscriptionAvailability"]
9. getAvailableProducts 类型: function
10. 开始测试调用...
11. ✅ 调用成功: {products: [...], count: 4}
```

### 如果插件未注册：

```
5. 所有插件: ["SaveToGallery", "Camera", "Filesystem", "Share"]  // 没有 SubscriptionPlugin
6. SubscriptionPlugin: undefined
7. SubscriptionPlugin 类型: undefined
❌ SubscriptionPlugin 未找到！
```

---

## 如果插件未注册

### 可能的原因：

1. **插件文件没有被编译到 App 中**
   - 检查 Xcode 项目设置
   - 确认 `SubscriptionPlugin.m` 和 `SubscriptionPlugin.swift` 在 "App" target 中

2. **插件注册宏有问题**
   - 检查 `SubscriptionPlugin.m` 中的 `CAP_PLUGIN` 宏
   - 确认插件ID是 "SubscriptionPlugin"

3. **需要重新构建项目**
   - 在 Xcode 中清理构建：`Product` → `Clean Build Folder`（`⌘ + Shift + K`）
   - 重新构建：`Product` → `Build`（`⌘ + B`）

---

**请执行上述代码并告诉我结果！** 🔍


















