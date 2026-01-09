#import <Capacitor/Capacitor.h>

// SubscriptionPlugin - StoreKit 2 订阅管理插件
// 已重新启用以支持 iOS 内购功能

CAP_PLUGIN(SubscriptionPlugin, "SubscriptionPlugin",
           CAP_PLUGIN_METHOD(checkSubscriptionAvailability, CAPPluginReturnPromise);
           CAP_PLUGIN_METHOD(getAvailableProducts, CAPPluginReturnPromise);
           CAP_PLUGIN_METHOD(purchase, CAPPluginReturnPromise);
           CAP_PLUGIN_METHOD(getSubscriptionStatus, CAPPluginReturnPromise);
           CAP_PLUGIN_METHOD(restorePurchases, CAPPluginReturnPromise);
)
