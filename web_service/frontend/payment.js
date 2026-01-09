/**
 * Web 支付服务
 * 支持微信支付和支付宝支付
 */

class WebPaymentService {
    constructor() {
        this.apiBaseURL = window.API_BASE_URL || this.getApiBaseURL();
    }

    getApiBaseURL() {
        // 检测环境并返回相应的 API 地址
        if (window.Capacitor?.getPlatform() === 'ios') {
            // iOS App 环境
            return 'https://beatsync.site';
        } else if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
            // 本地开发环境
            return 'http://localhost:8000';
        } else {
            // 生产环境
            return 'https://beatsync.site';
        }
    }

    async getUserToken() {
        // 获取用户 Token
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
    }

    async createPaymentOrder(productId, paymentMethod = 'wechat') {
        /**
         * 创建支付订单
         * 
         * @param {string} productId - 产品ID
         * @param {string} paymentMethod - 支付方式 ('wechat' 或 'alipay')
         * @returns {Promise<Object>} 支付订单信息
         */
        try {
            const token = await this.getUserToken();
            if (!token) {
                throw new Error('未登录，请先注册');
            }

            const response = await fetch(`${this.apiBaseURL}/api/payment/create`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'Authorization': `Bearer ${token}`
                },
                body: new URLSearchParams({
                    product_id: productId,
                    payment_method: paymentMethod
                })
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error || '创建支付订单失败');
            }

            return await response.json();
        } catch (error) {
            console.error('创建支付订单失败:', error);
            throw error;
        }
    }

    async getPaymentStatus(orderId) {
        /**
         * 查询支付订单状态
         * 
         * @param {string} orderId - 订单ID
         * @returns {Promise<Object>} 订单状态信息
         */
        try {
            const token = await this.getUserToken();
            if (!token) {
                throw new Error('未登录');
            }

            const response = await fetch(`${this.apiBaseURL}/api/payment/status/${orderId}`, {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error || '查询支付状态失败');
            }

            return await response.json();
        } catch (error) {
            console.error('查询支付状态失败:', error);
            throw error;
        }
    }

    async pollPaymentStatus(orderId, maxAttempts = 60, interval = 2000) {
        /**
         * 轮询支付订单状态
         * 
         * @param {string} orderId - 订单ID
         * @param {number} maxAttempts - 最大轮询次数
         * @param {number} interval - 轮询间隔（毫秒）
         * @returns {Promise<Object>} 订单状态信息
         */
        for (let i = 0; i < maxAttempts; i++) {
            try {
                const status = await this.getPaymentStatus(orderId);
                
                if (status.status === 'completed') {
                    return status;
                } else if (status.status === 'failed' || status.status === 'cancelled') {
                    throw new Error(`支付失败: ${status.status}`);
                }
                
                // 等待后继续轮询
                await new Promise(resolve => setTimeout(resolve, interval));
            } catch (error) {
                if (i === maxAttempts - 1) {
                    throw error;
                }
                await new Promise(resolve => setTimeout(resolve, interval));
            }
        }
        
        throw new Error('支付超时，请稍后查询订单状态');
    }

    redirectToPayment(paymentUrl) {
        /**
         * 跳转到支付页面
         * 
         * @param {string} paymentUrl - 支付URL
         */
        if (paymentUrl) {
            window.location.href = paymentUrl;
        } else {
            throw new Error('支付URL无效');
        }
    }

    openPaymentWindow(paymentUrl) {
        /**
         * 在新窗口打开支付页面
         * 
         * @param {string} paymentUrl - 支付URL
         * @returns {Window} 新窗口对象
         */
        if (paymentUrl) {
            return window.open(paymentUrl, 'payment', 'width=600,height=800');
        } else {
            throw new Error('支付URL无效');
        }
    }
}

// 创建全局实例
window.webPaymentService = new WebPaymentService();
