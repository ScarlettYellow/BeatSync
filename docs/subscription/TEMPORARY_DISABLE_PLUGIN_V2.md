# 临时禁用 SubscriptionPlugin（测试崩溃原因）

## 目的

确定 `SIGKILL` 崩溃是否由 `SubscriptionPlugin` 导致。

## 步骤

### 步骤 1：临时注释掉插件注册

编辑 `ios/App/SubscriptionPlugin.m`，注释掉 `CAP_PLUGIN` 宏：

```objc
#import <Capacitor/Capacitor.h>

// 临时禁用插件注册，测试是否是插件导致崩溃
/*
CAP_PLUGIN(SubscriptionPlugin, "SubscriptionPlugin",
           CAP_PLUGIN_METHOD(checkSubscriptionAvailability, CAPPluginReturnPromise);
           CAP_PLUGIN_METHOD(getAvailableProducts, CAPPluginReturnPromise);
           CAP_PLUGIN_METHOD(purchase, CAPPluginReturnPromise);
           CAP_PLUGIN_METHOD(getSubscriptionStatus, CAPPluginReturnPromise);
           CAP_PLUGIN_METHOD(restorePurchases, CAPPluginReturnPromise);
)
*/
```

### 步骤 2：重新编译运行

1. 在 Xcode 中：`Product` → `Clean Build Folder` (Shift+Cmd+K)
2. 重新编译运行
3. 观察是否仍然崩溃

### 步骤 3：根据结果判断

- **如果不再崩溃**：说明是 `SubscriptionPlugin` 导致的问题，需要进一步简化插件代码
- **如果仍然崩溃**：说明问题不在插件，可能是其他原因（Capacitor 配置、代码签名等）

---

**请先执行步骤 1，然后告诉我结果！** 🔍

# 临时禁用 SubscriptionPlugin（测试崩溃原因）

## 目的

确定 `SIGKILL` 崩溃是否由 `SubscriptionPlugin` 导致。

## 步骤

### 步骤 1：临时注释掉插件注册

编辑 `ios/App/SubscriptionPlugin.m`，注释掉 `CAP_PLUGIN` 宏：

```objc
#import <Capacitor/Capacitor.h>

// 临时禁用插件注册，测试是否是插件导致崩溃
/*
CAP_PLUGIN(SubscriptionPlugin, "SubscriptionPlugin",
           CAP_PLUGIN_METHOD(checkSubscriptionAvailability, CAPPluginReturnPromise);
           CAP_PLUGIN_METHOD(getAvailableProducts, CAPPluginReturnPromise);
           CAP_PLUGIN_METHOD(purchase, CAPPluginReturnPromise);
           CAP_PLUGIN_METHOD(getSubscriptionStatus, CAPPluginReturnPromise);
           CAP_PLUGIN_METHOD(restorePurchases, CAPPluginReturnPromise);
)
*/
```

### 步骤 2：重新编译运行

1. 在 Xcode 中：`Product` → `Clean Build Folder` (Shift+Cmd+K)
2. 重新编译运行
3. 观察是否仍然崩溃

### 步骤 3：根据结果判断

- **如果不再崩溃**：说明是 `SubscriptionPlugin` 导致的问题，需要进一步简化插件代码
- **如果仍然崩溃**：说明问题不在插件，可能是其他原因（Capacitor 配置、代码签名等）

---

**请先执行步骤 1，然后告诉我结果！** 🔍

# 临时禁用 SubscriptionPlugin（测试崩溃原因）

## 目的

确定 `SIGKILL` 崩溃是否由 `SubscriptionPlugin` 导致。

## 步骤

### 步骤 1：临时注释掉插件注册

编辑 `ios/App/SubscriptionPlugin.m`，注释掉 `CAP_PLUGIN` 宏：

```objc
#import <Capacitor/Capacitor.h>

// 临时禁用插件注册，测试是否是插件导致崩溃
/*
CAP_PLUGIN(SubscriptionPlugin, "SubscriptionPlugin",
           CAP_PLUGIN_METHOD(checkSubscriptionAvailability, CAPPluginReturnPromise);
           CAP_PLUGIN_METHOD(getAvailableProducts, CAPPluginReturnPromise);
           CAP_PLUGIN_METHOD(purchase, CAPPluginReturnPromise);
           CAP_PLUGIN_METHOD(getSubscriptionStatus, CAPPluginReturnPromise);
           CAP_PLUGIN_METHOD(restorePurchases, CAPPluginReturnPromise);
)
*/
```

### 步骤 2：重新编译运行

1. 在 Xcode 中：`Product` → `Clean Build Folder` (Shift+Cmd+K)
2. 重新编译运行
3. 观察是否仍然崩溃

### 步骤 3：根据结果判断

- **如果不再崩溃**：说明是 `SubscriptionPlugin` 导致的问题，需要进一步简化插件代码
- **如果仍然崩溃**：说明问题不在插件，可能是其他原因（Capacitor 配置、代码签名等）

---

**请先执行步骤 1，然后告诉我结果！** 🔍












