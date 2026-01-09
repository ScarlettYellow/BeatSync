# 简单的调试脚本

## 在 Safari Web Inspector 控制台中执行

**注意**：如果出现语法错误，请先刷新页面（在 App 中下拉刷新或重新启动 App），然后重新执行。

### 一次性执行（复制粘贴整个代码块）

```javascript
(function() {
    console.log('=== 开始检查插件注册 ===');
    
    // 1. 检查 Capacitor
    if (typeof window.Capacitor === 'undefined') {
        console.error('❌ Capacitor 未定义');
        return;
    }
    console.log('✅ Capacitor 已加载');
    
    // 2. 检查 Plugins
    if (!window.Capacitor.Plugins) {
        console.error('❌ Plugins 未定义');
        return;
    }
    console.log('✅ Plugins 已加载');
    
    // 3. 列出所有插件
    const allPlugins = Object.keys(window.Capacitor.Plugins);
    console.log('📋 所有插件:', allPlugins);
    
    // 4. 检查 SubscriptionPlugin
    const plugin = window.Capacitor.Plugins.SubscriptionPlugin;
    if (!plugin) {
        console.error('❌ SubscriptionPlugin 未找到');
        console.log('可用的插件:', allPlugins);
        return;
    }
    console.log('✅ SubscriptionPlugin 已找到');
    console.log('插件对象:', plugin);
    
    // 5. 检查方法
    const methods = Object.keys(plugin);
    console.log('📋 插件方法:', methods);
    
    // 6. 检查 getAvailableProducts 方法
    if (typeof plugin.getAvailableProducts !== 'function') {
        console.error('❌ getAvailableProducts 方法不存在或不是函数');
        return;
    }
    console.log('✅ getAvailableProducts 方法存在');
    
    // 7. 测试调用
    console.log('🔄 开始测试调用...');
    plugin.getAvailableProducts()
        .then(result => {
            console.log('✅ 调用成功:', result);
        })
        .catch(error => {
            console.error('❌ 调用失败:', error);
            console.error('错误详情:', {
                message: error.message,
                stack: error.stack,
                name: error.name
            });
        });
    
    console.log('=== 检查完成 ===');
})();
```

---

## 预期输出

### 如果插件已正确注册：

```
=== 开始检查插件注册 ===
✅ Capacitor 已加载
✅ Plugins 已加载
📋 所有插件: ["SubscriptionPlugin", "SaveToGallery", "Camera", "Filesystem", "Share"]
✅ SubscriptionPlugin 已找到
插件对象: {...}
📋 插件方法: ["getAvailableProducts", "purchase", "getSubscriptionStatus", "restorePurchases", "checkSubscriptionAvailability"]
✅ getAvailableProducts 方法存在
🔄 开始测试调用...
✅ 调用成功: {products: [...], count: 4}
=== 检查完成 ===
```

### 如果插件未注册：

```
=== 开始检查插件注册 ===
✅ Capacitor 已加载
✅ Plugins 已加载
📋 所有插件: ["SaveToGallery", "Camera", "Filesystem", "Share"]
❌ SubscriptionPlugin 未找到
可用的插件: ["SaveToGallery", "Camera", "Filesystem", "Share"]
=== 检查完成 ===
```

---

## 如果插件未注册

请按照以下步骤操作：

1. **在 Xcode 中清理构建**：
   - `Product` → `Clean Build Folder`（`⌘ + Shift + K`）

2. **重新构建项目**：
   - `Product` → `Build`（`⌘ + B`）

3. **重新运行 App**：
   - `Product` → `Run`（`⌘ + R`）

4. **再次执行调试脚本**

---

**请执行上述脚本并告诉我输出结果！** 🔍







# 简单的调试脚本

## 在 Safari Web Inspector 控制台中执行

**注意**：如果出现语法错误，请先刷新页面（在 App 中下拉刷新或重新启动 App），然后重新执行。

### 一次性执行（复制粘贴整个代码块）

```javascript
(function() {
    console.log('=== 开始检查插件注册 ===');
    
    // 1. 检查 Capacitor
    if (typeof window.Capacitor === 'undefined') {
        console.error('❌ Capacitor 未定义');
        return;
    }
    console.log('✅ Capacitor 已加载');
    
    // 2. 检查 Plugins
    if (!window.Capacitor.Plugins) {
        console.error('❌ Plugins 未定义');
        return;
    }
    console.log('✅ Plugins 已加载');
    
    // 3. 列出所有插件
    const allPlugins = Object.keys(window.Capacitor.Plugins);
    console.log('📋 所有插件:', allPlugins);
    
    // 4. 检查 SubscriptionPlugin
    const plugin = window.Capacitor.Plugins.SubscriptionPlugin;
    if (!plugin) {
        console.error('❌ SubscriptionPlugin 未找到');
        console.log('可用的插件:', allPlugins);
        return;
    }
    console.log('✅ SubscriptionPlugin 已找到');
    console.log('插件对象:', plugin);
    
    // 5. 检查方法
    const methods = Object.keys(plugin);
    console.log('📋 插件方法:', methods);
    
    // 6. 检查 getAvailableProducts 方法
    if (typeof plugin.getAvailableProducts !== 'function') {
        console.error('❌ getAvailableProducts 方法不存在或不是函数');
        return;
    }
    console.log('✅ getAvailableProducts 方法存在');
    
    // 7. 测试调用
    console.log('🔄 开始测试调用...');
    plugin.getAvailableProducts()
        .then(result => {
            console.log('✅ 调用成功:', result);
        })
        .catch(error => {
            console.error('❌ 调用失败:', error);
            console.error('错误详情:', {
                message: error.message,
                stack: error.stack,
                name: error.name
            });
        });
    
    console.log('=== 检查完成 ===');
})();
```

---

## 预期输出

### 如果插件已正确注册：

```
=== 开始检查插件注册 ===
✅ Capacitor 已加载
✅ Plugins 已加载
📋 所有插件: ["SubscriptionPlugin", "SaveToGallery", "Camera", "Filesystem", "Share"]
✅ SubscriptionPlugin 已找到
插件对象: {...}
📋 插件方法: ["getAvailableProducts", "purchase", "getSubscriptionStatus", "restorePurchases", "checkSubscriptionAvailability"]
✅ getAvailableProducts 方法存在
🔄 开始测试调用...
✅ 调用成功: {products: [...], count: 4}
=== 检查完成 ===
```

### 如果插件未注册：

```
=== 开始检查插件注册 ===
✅ Capacitor 已加载
✅ Plugins 已加载
📋 所有插件: ["SaveToGallery", "Camera", "Filesystem", "Share"]
❌ SubscriptionPlugin 未找到
可用的插件: ["SaveToGallery", "Camera", "Filesystem", "Share"]
=== 检查完成 ===
```

---

## 如果插件未注册

请按照以下步骤操作：

1. **在 Xcode 中清理构建**：
   - `Product` → `Clean Build Folder`（`⌘ + Shift + K`）

2. **重新构建项目**：
   - `Product` → `Build`（`⌘ + B`）

3. **重新运行 App**：
   - `Product` → `Run`（`⌘ + R`）

4. **再次执行调试脚本**

---

**请执行上述脚本并告诉我输出结果！** 🔍







# 简单的调试脚本

## 在 Safari Web Inspector 控制台中执行

**注意**：如果出现语法错误，请先刷新页面（在 App 中下拉刷新或重新启动 App），然后重新执行。

### 一次性执行（复制粘贴整个代码块）

```javascript
(function() {
    console.log('=== 开始检查插件注册 ===');
    
    // 1. 检查 Capacitor
    if (typeof window.Capacitor === 'undefined') {
        console.error('❌ Capacitor 未定义');
        return;
    }
    console.log('✅ Capacitor 已加载');
    
    // 2. 检查 Plugins
    if (!window.Capacitor.Plugins) {
        console.error('❌ Plugins 未定义');
        return;
    }
    console.log('✅ Plugins 已加载');
    
    // 3. 列出所有插件
    const allPlugins = Object.keys(window.Capacitor.Plugins);
    console.log('📋 所有插件:', allPlugins);
    
    // 4. 检查 SubscriptionPlugin
    const plugin = window.Capacitor.Plugins.SubscriptionPlugin;
    if (!plugin) {
        console.error('❌ SubscriptionPlugin 未找到');
        console.log('可用的插件:', allPlugins);
        return;
    }
    console.log('✅ SubscriptionPlugin 已找到');
    console.log('插件对象:', plugin);
    
    // 5. 检查方法
    const methods = Object.keys(plugin);
    console.log('📋 插件方法:', methods);
    
    // 6. 检查 getAvailableProducts 方法
    if (typeof plugin.getAvailableProducts !== 'function') {
        console.error('❌ getAvailableProducts 方法不存在或不是函数');
        return;
    }
    console.log('✅ getAvailableProducts 方法存在');
    
    // 7. 测试调用
    console.log('🔄 开始测试调用...');
    plugin.getAvailableProducts()
        .then(result => {
            console.log('✅ 调用成功:', result);
        })
        .catch(error => {
            console.error('❌ 调用失败:', error);
            console.error('错误详情:', {
                message: error.message,
                stack: error.stack,
                name: error.name
            });
        });
    
    console.log('=== 检查完成 ===');
})();
```

---

## 预期输出

### 如果插件已正确注册：

```
=== 开始检查插件注册 ===
✅ Capacitor 已加载
✅ Plugins 已加载
📋 所有插件: ["SubscriptionPlugin", "SaveToGallery", "Camera", "Filesystem", "Share"]
✅ SubscriptionPlugin 已找到
插件对象: {...}
📋 插件方法: ["getAvailableProducts", "purchase", "getSubscriptionStatus", "restorePurchases", "checkSubscriptionAvailability"]
✅ getAvailableProducts 方法存在
🔄 开始测试调用...
✅ 调用成功: {products: [...], count: 4}
=== 检查完成 ===
```

### 如果插件未注册：

```
=== 开始检查插件注册 ===
✅ Capacitor 已加载
✅ Plugins 已加载
📋 所有插件: ["SaveToGallery", "Camera", "Filesystem", "Share"]
❌ SubscriptionPlugin 未找到
可用的插件: ["SaveToGallery", "Camera", "Filesystem", "Share"]
=== 检查完成 ===
```

---

## 如果插件未注册

请按照以下步骤操作：

1. **在 Xcode 中清理构建**：
   - `Product` → `Clean Build Folder`（`⌘ + Shift + K`）

2. **重新构建项目**：
   - `Product` → `Build`（`⌘ + B`）

3. **重新运行 App**：
   - `Product` → `Run`（`⌘ + R`）

4. **再次执行调试脚本**

---

**请执行上述脚本并告诉我输出结果！** 🔍


















