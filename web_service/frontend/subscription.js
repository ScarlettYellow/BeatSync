/**
 * 订阅系统前端接口
 * 与 iOS StoreKit 2 插件集成
 */

// 检查是否在 iOS App 中
const isIOSApp = (() => {
    // 多种检测方式，确保在 iOS App 中正确识别
    if (typeof window.Capacitor === 'undefined') {
        console.log('[订阅检测] Capacitor 未定义');
        return false;
    }
    
    // 方式1: 检查平台
    if (window.Capacitor.getPlatform && window.Capacitor.getPlatform() === 'ios') {
        console.log('[订阅检测] ✅ 检测到 iOS 平台（方式1）');
        return true;
    }
    
    // 方式2: 检查 isNativePlatform
    if (window.Capacitor.isNativePlatform && window.Capacitor.getPlatform && window.Capacitor.getPlatform() === 'ios') {
        console.log('[订阅检测] ✅ 检测到 iOS 平台（方式2）');
        return true;
    }
    
    // 方式3: 检查 userAgent（备用方案）
    const isIOSDevice = /iPhone|iPad|iPod/i.test(navigator.userAgent);
    const isNative = window.Capacitor.isNativePlatform;
    if (isIOSDevice && isNative) {
        console.log('[订阅检测] ✅ 检测到 iOS 平台（方式3：userAgent + isNativePlatform）');
        return true;
    }
    
    console.log('[订阅检测] ❌ 未检测到 iOS App 环境', {
        hasCapacitor: typeof window.Capacitor !== 'undefined',
        platform: window.Capacitor?.getPlatform?.(),
        isNativePlatform: window.Capacitor?.isNativePlatform,
        userAgent: navigator.userAgent
    });
    return false;
})();

/**
 * 订阅插件接口
 */
class SubscriptionService {
    constructor() {
        // 延迟获取插件，因为插件可能在 Capacitor 初始化后才注册
        this.getPlugin = () => {
            try {
                // 方法1: 直接访问 Plugins.SubscriptionPlugin
                if (window.Capacitor?.Plugins?.SubscriptionPlugin) {
                    return window.Capacitor.Plugins.SubscriptionPlugin;
                }
                
                // 方法2: 通过 Capacitor 的插件注册表访问
                if (window.Capacitor?.Plugins) {
                    const plugins = window.Capacitor.Plugins;
                    // 尝试不同的访问方式
                    if (plugins['SubscriptionPlugin']) {
                        return plugins['SubscriptionPlugin'];
                    }
                    // 列出所有可用的插件
                    const allPlugins = Object.keys(plugins);
                    console.log('[订阅服务] 所有可用插件:', allPlugins);
                }
                
                console.log('[订阅服务] 插件未找到，当前状态:', {
                    hasCapacitor: typeof window.Capacitor !== 'undefined',
                    hasPlugins: !!window.Capacitor?.Plugins,
                    pluginsKeys: window.Capacitor?.Plugins ? Object.keys(window.Capacitor.Plugins) : [],
                    allCapacitorKeys: window.Capacitor ? Object.keys(window.Capacitor) : [],
                    CapacitorType: typeof window.Capacitor,
                    PluginsType: typeof window.Capacitor?.Plugins
                });
                
                return null;
            } catch (error) {
                console.error('[订阅服务] 获取插件时出错:', error);
                return null;
            }
        };
        
        // 插件加载重试机制
        this.pluginLoadRetries = 0;
        this.maxRetries = 10;
        this.retryDelay = 500; // 500ms
    }
    
    /**
     * 等待插件加载（带重试）
     */
    async waitForPlugin(maxWaitTime = 5000) {
        const startTime = Date.now();
        while (Date.now() - startTime < maxWaitTime) {
            const plugin = this.getPlugin();
            if (plugin) {
                console.log('[订阅服务] ✅ 插件已加载');
                return plugin;
            }
            console.log('[订阅服务] 等待插件加载...', Date.now() - startTime, 'ms');
            await new Promise(resolve => setTimeout(resolve, this.retryDelay));
        }
        console.error('[订阅服务] ❌ 等待插件加载超时');
        return null;
    }

    /**
     * 检查订阅功能是否可用（现在所有平台都可用，通过后端 API）
     */
    async checkAvailability() {
        // 现在所有平台都支持订阅功能（通过后端 API）
        return {
            available: true,
            message: '订阅功能可用（通过后端 API）'
        };
    }

    /**
     * 获取可用订阅产品（通过后端 API）
     */
    async getAvailableProducts() {
        console.log('[订阅服务] getAvailableProducts 被调用（使用后端 API）');
        
        try {
            // 获取 API 基础 URL
            const apiBaseURL = this.getApiBaseURL();
            
            console.log('[订阅服务] 调用后端 API:', `${apiBaseURL}/api/subscription/products`);
            
            const response = await fetch(`${apiBaseURL}/api/subscription/products`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`获取产品列表失败: ${response.status} ${errorText}`);
            }
            
            const result = await response.json();
            console.log('[订阅服务] ✅ 获取产品列表成功:', result);
            
            // 返回产品列表
            if (result.products && Array.isArray(result.products)) {
                return result.products;
            } else {
                console.warn('[订阅服务] ⚠️ API 返回格式异常:', result);
                return [];
            }
        } catch (error) {
            console.error('[订阅服务] ❌ 获取产品列表失败:', error);
            throw error;
        }
    }

    /**
     * 购买订阅（iOS App 使用 StoreKit，Web 使用后端支付）
     * @param {string} productId - 产品ID (如 'basic_monthly', 'premium_yearly')
     */
    async purchase(productId) {
        console.log('[订阅服务] purchase 被调用，productId:', productId);
        
        // iOS App：使用原生 StoreKit 购买，然后验证收据
        if (isIOSApp) {
            return await this.purchaseIOS(productId);
        }
        
        // Web：使用后端支付 API
        return await this.purchaseWeb(productId);
    }
    
    /**
     * iOS App 购买（使用原生 StoreKit）
     */
    async purchaseIOS(productId) {
        console.log('[订阅服务] iOS 购买流程开始');
        
        // 先尝试获取原生插件（如果可用）
        const plugin = this.getPlugin();
        
        if (plugin) {
            try {
                console.log('[订阅服务] 使用原生插件进行购买');
                // 使用原生插件购买
                const purchaseResult = await plugin.purchase({ productId });
                
                // 购买成功后，验证收据
                if (purchaseResult && purchaseResult.transactionReceipt) {
                    console.log('[订阅服务] 购买成功，验证收据...');
                    await this.verifyReceipt(productId, purchaseResult.transactionReceipt);
                }
                
                return purchaseResult;
            } catch (error) {
                console.error('[订阅服务] 原生插件购买失败:', error);
                // 如果原生插件失败，降级到后端 API（Web 支付方式）
                console.log('[订阅服务] 降级到后端支付 API');
                return await this.purchaseWeb(productId);
            }
        } else {
            // 插件不可用，使用后端支付 API
            console.log('[订阅服务] 原生插件不可用，使用后端支付 API');
            return await this.purchaseWeb(productId);
        }
    }
    
    /**
     * Web 购买（使用后端支付 API）
     */
    async purchaseWeb(productId) {
        console.log('[订阅服务] Web 购买流程开始');
        
        try {
            const token = await this.getUserToken();
            if (!token) {
                throw new Error('请先登录');
            }
            
            const apiBaseURL = this.getApiBaseURL();
            
            // 创建支付订单
            const response = await fetch(`${apiBaseURL}/api/subscription/purchase`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'Authorization': `Bearer ${token}`
                },
                body: new URLSearchParams({
                    product_id: productId,
                    payment_method: 'wechat'  // 默认使用微信支付，可以根据需要修改
                })
            });
            
            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`创建支付订单失败: ${response.status} ${errorText}`);
            }
            
            const result = await response.json();
            console.log('[订阅服务] ✅ 支付订单创建成功:', result);
            
            // 如果有支付 URL，根据环境决定是否跳转
            if (result.payment_url) {
                // iOS App 中不跳转到 Web 支付页面（应该使用 StoreKit）
                if (isIOSApp) {
                    console.log('[订阅服务] iOS App 环境，不跳转到 Web 支付页面');
                    // 返回订单信息，但不跳转
                    return {
                        ...result,
                        skip_redirect: true,
                        message: '订单已创建，请在 iOS 内购中完成支付'
                    };
                } else {
                    // Web 环境：跳转到支付页面
                    window.location.href = result.payment_url;
                }
            }
            
            return result;
        } catch (error) {
            console.error('[订阅服务] ❌ Web 购买失败:', error);
            throw error;
        }
    }
    
    /**
     * 验证 iOS 收据
     */
    async verifyReceipt(productId, receiptData) {
        try {
            const token = await this.getUserToken();
            if (!token) {
                throw new Error('请先登录');
            }
            
            const apiBaseURL = this.getApiBaseURL();
            
            // 将收据数据转换为 base64（如果还不是）
            let receiptBase64 = receiptData;
            if (typeof receiptData === 'object') {
                receiptBase64 = btoa(JSON.stringify(receiptData));
            }
            
            const response = await fetch(`${apiBaseURL}/api/subscription/verify-receipt`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'Authorization': `Bearer ${token}`
                },
                body: new URLSearchParams({
                    receipt_data: receiptBase64,
                    product_id: productId
                })
            });
            
            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`验证收据失败: ${response.status} ${errorText}`);
            }
            
            const result = await response.json();
            console.log('[订阅服务] ✅ 收据验证成功:', result);
            
            return result;
        } catch (error) {
            console.error('[订阅服务] ❌ 验证收据失败:', error);
            throw error;
        }
    }

    /**
     * 查询订阅状态
     */
    async getSubscriptionStatus() {
        if (!isIOSApp) {
            // 如果不是 iOS App，从后端 API 获取
            return await this.getBackendSubscriptionStatus();
        }

        const plugin = this.getPlugin();
        if (!plugin) {
            // 插件未加载，降级到后端 API
            console.warn('订阅插件未加载，使用后端 API 获取订阅状态');
            return await this.getBackendSubscriptionStatus();
        }

        try {
            const result = await plugin.getSubscriptionStatus();
            return result;
        } catch (error) {
            console.error('查询订阅状态失败:', error);
            // 降级到后端 API
            return await this.getBackendSubscriptionStatus();
        }
    }

    /**
     * 从后端获取订阅状态
     */
    async getBackendSubscriptionStatus() {
        try {
            const token = await this.getUserToken();
            if (!token) {
                return {
                    hasActiveSubscription: false,
                    message: '未登录'
                };
            }

            // 获取 API 基础 URL（从 script.js 中定义的 API_BASE_URL）
            const apiBaseURL = window.API_BASE_URL || (() => {
                const hostname = window.location.hostname;
                if (window.Capacitor?.isNativePlatform) {
                    return 'https://beatsync.site';
                }
                if (hostname === 'localhost' || hostname === '127.0.0.1') {
                    return 'http://localhost:8000';
                }
                const privateIpPattern = /^(192\.168\.|10\.|172\.(1[6-9]|2[0-9]|3[01])\.)/;
                if (privateIpPattern.test(hostname)) {
                    return `http://${hostname}:8000`;
                }
                return 'https://beatsync.site';
            })();

            const response = await fetch(`${apiBaseURL}/api/subscription/status`, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (response.ok) {
                return await response.json();
            } else {
                throw new Error('获取订阅状态失败');
            }
        } catch (error) {
            console.error('从后端获取订阅状态失败:', error);
            return {
                hasActiveSubscription: false,
                error: error.message
            };
        }
    }

    /**
     * 恢复购买（iOS App 使用 StoreKit，Web 从后端获取订阅历史）
     */
    async restorePurchases() {
        console.log('[订阅服务] restorePurchases 被调用');
        
        // iOS App：使用原生 StoreKit 恢复，然后验证收据
        if (isIOSApp) {
            return await this.restorePurchasesIOS();
        }
        
        // Web：从后端获取订阅历史
        return await this.restorePurchasesWeb();
    }
    
    /**
     * iOS App 恢复购买
     */
    async restorePurchasesIOS() {
        console.log('[订阅服务] iOS 恢复购买流程开始');
        
        // 先尝试获取原生插件（如果可用）
        const plugin = this.getPlugin();
        
        if (plugin) {
            try {
                console.log('[订阅服务] 使用原生插件恢复购买');
                // 使用原生插件恢复
                const restoreResult = await plugin.restorePurchases();
                
                // 恢复成功后，验证所有收据
                if (restoreResult && restoreResult.purchases && Array.isArray(restoreResult.purchases)) {
                    console.log('[订阅服务] 恢复成功，验证收据...');
                    for (const purchase of restoreResult.purchases) {
                        if (purchase.productId && purchase.transactionReceipt) {
                            try {
                                await this.verifyReceipt(purchase.productId, purchase.transactionReceipt);
                            } catch (error) {
                                console.error(`[订阅服务] 验证收据失败 (${purchase.productId}):`, error);
                            }
                        }
                    }
                }
                
                return restoreResult;
            } catch (error) {
                console.error('[订阅服务] 原生插件恢复失败:', error);
                // 如果原生插件失败，降级到后端 API
                console.log('[订阅服务] 降级到后端 API');
                return await this.restorePurchasesWeb();
            }
        } else {
            // 插件不可用，使用后端 API
            console.log('[订阅服务] 原生插件不可用，使用后端 API');
            return await this.restorePurchasesWeb();
        }
    }
    
    /**
     * Web 恢复购买（从后端获取订阅历史）
     */
    async restorePurchasesWeb() {
        console.log('[订阅服务] Web 恢复购买流程开始');
        
        try {
            const token = await this.getUserToken();
            if (!token) {
                throw new Error('请先登录');
            }
            
            const apiBaseURL = this.getApiBaseURL();
            
            // 获取订阅历史
            const response = await fetch(`${apiBaseURL}/api/subscription/history?page=1&limit=100`, {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
            
            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`获取订阅历史失败: ${response.status} ${errorText}`);
            }
            
            const result = await response.json();
            console.log('[订阅服务] ✅ 获取订阅历史成功:', result);
            
            return {
                success: true,
                purchases: result.subscriptions || []
            };
        } catch (error) {
            console.error('[订阅服务] ❌ Web 恢复购买失败:', error);
            throw error;
        }
    }

    /**
     * 获取 API 基础 URL
     */
    getApiBaseURL() {
        // 从 script.js 中定义的 API_BASE_URL 获取，或使用默认值
        if (window.API_BASE_URL) {
            return window.API_BASE_URL;
        }
        
        const hostname = window.location.hostname;
        if (window.Capacitor?.isNativePlatform) {
            return 'https://beatsync.site';
        }
        if (hostname === 'localhost' || hostname === '127.0.0.1') {
            return 'http://localhost:8000';
        }
        const privateIpPattern = /^(192\.168\.|10\.|172\.(1[6-9]|2[0-9]|3[01])\.)/;
        if (privateIpPattern.test(hostname)) {
            return `http://${hostname}:8000`;
        }
        return 'https://beatsync.site';
    }
    
    /**
     * 获取用户 Token
     */
    async getUserToken(autoRegister = true) {
        // 优先从本地缓存获取
        const readLocalToken = async () => {
            if (window.Capacitor?.Preferences) {
                try {
                    const result = await window.Capacitor.Preferences.get({ key: 'user_token' });
                    return result?.value || null;
                } catch (error) {
                    console.error('获取用户 Token 失败:', error);
                    return null;
                }
            }
            return localStorage.getItem('user_token');
        };

        let token = await readLocalToken();
        if (token || !autoRegister) {
            return token;
        }

        // 如果本地没有 token，自动注册/登录（设备ID方式）
        try {
            const deviceId = await this.getDeviceId();
            const apiBaseURL = this.getApiBaseURL();

            const response = await fetch(`${apiBaseURL}/api/auth/register`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded'
                },
                body: new URLSearchParams({
                    device_id: deviceId
                })
            });

            if (!response.ok) {
                console.error('自动注册失败，状态码:', response.status);
                return null;
            }

            const result = await response.json();
            if (result.token) {
                await this.saveUserToken(result.token);
                return result.token;
            }
            console.warn('自动注册返回无 token，响应:', result);
            return null;
        } catch (error) {
            console.error('自动注册获取 token 失败:', error);
            return null;
        }
    }

    /**
     * 保存用户 Token
     */
    async saveUserToken(token) {
        if (window.Capacitor?.Preferences) {
            await window.Capacitor.Preferences.set({ key: 'user_token', value: token });
        } else {
            localStorage.setItem('user_token', token);
        }
    }

    /**
     * 获取或生成设备ID（用于无登录快速绑定账户）
     */
    async getDeviceId() {
        const storageKey = 'device_id';

        const readLocalId = async () => {
            if (window.Capacitor?.Preferences) {
                try {
                    const result = await window.Capacitor.Preferences.get({ key: storageKey });
                    return result?.value || null;
                } catch (error) {
                    console.error('读取设备ID失败:', error);
                    return null;
                }
            }
            return localStorage.getItem(storageKey);
        };

        let deviceId = await readLocalId();
        if (!deviceId) {
            // 生成新的设备ID
            const uuid = (window.crypto?.randomUUID)
                ? window.crypto.randomUUID()
                : `device-${Date.now()}-${Math.random().toString(16).slice(2)}`;
            deviceId = uuid;

            // 写入本地
            if (window.Capacitor?.Preferences) {
                try {
                    await window.Capacitor.Preferences.set({ key: storageKey, value: deviceId });
                } catch (error) {
                    console.error('保存设备ID失败:', error);
                }
            } else {
                localStorage.setItem(storageKey, deviceId);
            }
        }

        return deviceId;
    }
}

// 创建全局实例
const subscriptionService = new SubscriptionService();

// 导出供其他模块使用（Node.js 环境）
if (typeof module !== 'undefined' && module.exports) {
    module.exports = subscriptionService;
}

// 导出供浏览器环境使用（重要：必须挂载到 window 对象）
if (typeof window !== 'undefined') {
    window.subscriptionService = subscriptionService;
}
