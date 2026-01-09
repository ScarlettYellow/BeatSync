/*
 * SubscriptionPlugin.swift - StoreKit 2 订阅管理插件
 * 
 * 功能：
 * - 查询可用订阅产品
 * - 购买订阅
 * - 验证收据（与后端API集成）
 * - 查询订阅状态
 * - 恢复购买
 */

import Foundation
import Capacitor
import StoreKit

/**
 * SubscriptionPlugin - StoreKit 2 订阅管理插件
 * 
 * 功能：
 * - 查询可用订阅产品
 * - 购买订阅
 * - 验证收据（与后端API集成）
 * - 查询订阅状态
 * - 恢复购买
 */
@objc(SubscriptionPlugin)
public class SubscriptionPlugin: CAPPlugin {
    
    // 确保插件ID正确
    public override func getId() -> String {
        return "SubscriptionPlugin"
    }
    
    // 添加初始化日志，用于调试
    public override init() {
        super.init()
        print("📱 [SubscriptionPlugin] 插件已初始化")
    }
    
    // StoreKit 2 产品ID配置
    // 这些ID需要在 App Store Connect 中配置
    // 公测期套餐配置
    private let productIds: [String: String] = [
        "basic_monthly": "com.beatsync.public_beta.subscription.basic.monthly",
        "premium_monthly": "com.beatsync.public_beta.subscription.premium.monthly",
        "pack_10": "com.beatsync.public_beta.subscription.pack.10",
        "pack_20": "com.beatsync.public_beta.subscription.pack.20"
    ]
    
    // 后端API地址（从配置读取或使用默认值）
    private var apiBaseURL: String {
        // 默认值：生产环境
        // 注意：实际应该从 capacitor.config.json 读取，这里简化处理
        return "https://beatsync.site"
    }
    
    // MARK: - 查询可用产品
    
    @objc func getAvailableProducts(_ call: CAPPluginCall) {
        Task {
            do {
                let products = try await Product.products(for: Array(productIds.values))
                
                var productList: [[String: Any]] = []
                for product in products {
                    var productInfo: [String: Any] = [:]
                    productInfo["id"] = product.id
                    productInfo["displayName"] = product.displayName
                    productInfo["description"] = product.description
                    productInfo["price"] = product.price.description
                    productInfo["displayPrice"] = product.displayPrice  // StoreKit 2 使用 displayPrice 获取格式化价格
                    productInfo["subscriptionGroupID"] = product.subscription?.subscriptionGroupID
                    
                    // 查找对应的产品类型
                    for (type, id) in productIds {
                        if id == product.id {
                            productInfo["type"] = type
                            break
                        }
                    }
                    
                    productList.append(productInfo)
                }
                
                call.resolve([
                    "products": productList,
                    "count": productList.count
                ])
            } catch {
                call.reject("获取产品列表失败: \(error.localizedDescription)", "PRODUCT_FETCH_ERROR", error)
            }
        }
    }
    
    // MARK: - 购买订阅
    
    @objc func purchase(_ call: CAPPluginCall) {
        guard let productId = call.getString("productId") else {
            call.reject("缺少 productId 参数", "MISSING_PRODUCT_ID")
            return
        }
        
        // 查找完整的产品ID
        guard let fullProductId = productIds[productId] ?? productIds.values.first(where: { $0 == productId }) else {
            call.reject("无效的产品ID: \(productId)", "INVALID_PRODUCT_ID")
            return
        }
        
        Task {
            do {
                // 获取产品
                let products = try await Product.products(for: [fullProductId])
                guard let product = products.first else {
                    call.reject("产品不存在: \(fullProductId)", "PRODUCT_NOT_FOUND")
                    return
                }
                
                // 购买产品
                let result = try await product.purchase()
                
                switch result {
                case .success(let verification):
                    // 验证收据
                    switch verification {
                    case .verified(let transaction):
                        // 收据验证成功，发送到后端
                        await handleSuccessfulPurchase(transaction: transaction, productId: productId, call: call)
                        await transaction.finish()
                    case .unverified(_, let error):
                        call.reject("收据验证失败: \(error.localizedDescription)", "RECEIPT_VERIFICATION_FAILED", error)
                    }
                case .userCancelled:
                    call.reject("用户取消购买", "USER_CANCELLED")
                case .pending:
                    call.reject("购买待处理", "PURCHASE_PENDING")
                @unknown default:
                    call.reject("未知的购买结果", "UNKNOWN_PURCHASE_RESULT")
                }
            } catch {
                call.reject("购买失败: \(error.localizedDescription)", "PURCHASE_ERROR", error)
            }
        }
    }
    
    // MARK: - 处理成功购买
    
    private func handleSuccessfulPurchase(transaction: Transaction, productId: String, call: CAPPluginCall) async {
        do {
            // 获取收据数据
            let receiptData = try await getReceiptData(transaction: transaction)
            
            // 发送到后端验证
            let verificationResult = try await verifyReceiptWithBackend(
                transactionId: String(transaction.id),
                productId: productId,
                receiptData: receiptData
            )
            
            if verificationResult.success {
                call.resolve([
                    "success": true,
                    "transactionId": String(transaction.id),
                    "productId": productId,
                    "message": "购买成功并已验证"
                ])
            } else {
                call.reject("后端验证失败: \(verificationResult.message ?? "未知错误")", "BACKEND_VERIFICATION_FAILED")
            }
        } catch {
            call.reject("处理购买失败: \(error.localizedDescription)", "PURCHASE_PROCESSING_ERROR", error)
        }
    }
    
    // MARK: - 获取收据数据
    
    private func getReceiptData(transaction: Transaction) async throws -> String {
        // StoreKit 2 中，收据数据包含在 Transaction 中
        // 我们需要将 Transaction 编码为 JSON
        let encoder = JSONEncoder()
        encoder.dateEncodingStrategy = .iso8601
        
        let transactionData: [String: Any] = [
            "id": String(transaction.id),
            "productID": transaction.productID,
            "purchaseDate": transaction.purchaseDate,
            "expirationDate": transaction.expirationDate?.timeIntervalSince1970 ?? 0,
            "isUpgraded": transaction.isUpgraded,
            "revocationDate": transaction.revocationDate?.timeIntervalSince1970 ?? 0,
            "revocationReason": transaction.revocationReason?.rawValue ?? 0
        ]
        
        let jsonData = try JSONSerialization.data(withJSONObject: transactionData)
        return jsonData.base64EncodedString()
    }
    
    // MARK: - 验证收据（与后端API集成）
    
    private func verifyReceiptWithBackend(transactionId: String, productId: String, receiptData: String) async throws -> (success: Bool, message: String?) {
        // 获取用户Token（如果已登录）
        let userToken = await getCurrentUserToken()
        
        var request = URLRequest(url: URL(string: "\(apiBaseURL)/api/subscription/verify-receipt")!)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        if let token = userToken {
            request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        }
        
        let requestBody: [String: Any] = [
            "transaction_id": transactionId,
            "product_id": productId,
            "receipt_data": receiptData,
            "platform": "ios"
        ]
        
        request.httpBody = try JSONSerialization.data(withJSONObject: requestBody)
        
        let (data, response) = try await URLSession.shared.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse else {
            return (false, "无效的响应")
        }
        
        if httpResponse.statusCode == 200 {
            if let json = try? JSONSerialization.jsonObject(with: data) as? [String: Any],
               let success = json["success"] as? Bool {
                return (success, json["message"] as? String)
            }
            return (true, nil)
        } else {
            let errorMessage = String(data: data, encoding: .utf8) ?? "HTTP \(httpResponse.statusCode)"
            return (false, errorMessage)
        }
    }
    
    // MARK: - 获取当前用户Token
    
    private func getCurrentUserToken() async -> String? {
        // 从 Capacitor 存储或 Keychain 获取用户Token
        // 这里需要根据实际实现调整
        if let token = UserDefaults.standard.string(forKey: "user_token") {
            return token
        }
        return nil
    }
    
    // MARK: - 查询订阅状态
    
    @objc func getSubscriptionStatus(_ call: CAPPluginCall) {
        Task {
            do {
                // 获取当前用户的所有订阅
                var statuses: [String: Any] = [:]
                
                for await result in Transaction.currentEntitlements {
                    switch result {
                    case .verified(let transaction):
                        statuses[transaction.productID] = [
                            "productID": transaction.productID,
                            "purchaseDate": ISO8601DateFormatter().string(from: transaction.purchaseDate),
                            "expirationDate": transaction.expirationDate.map { ISO8601DateFormatter().string(from: $0) } ?? NSNull(),
                            "isActive": transaction.expirationDate == nil || transaction.expirationDate! > Date(),
                            "isUpgraded": transaction.isUpgraded
                        ]
                    case .unverified:
                        break
                    }
                }
                
                // 同时从后端获取订阅状态（包含下载次数等信息）
                do {
                    if let backendStatus = try await getBackendSubscriptionStatus() {
                        call.resolve([
                            "localStatus": statuses,
                            "backendStatus": backendStatus,
                            "hasActiveSubscription": !statuses.isEmpty
                        ])
                    } else {
                        call.resolve([
                            "localStatus": statuses,
                            "hasActiveSubscription": !statuses.isEmpty
                        ])
                    }
                } catch {
                    // 后端状态获取失败，只返回本地状态
                    call.resolve([
                        "localStatus": statuses,
                        "hasActiveSubscription": !statuses.isEmpty
                    ])
                }
            } catch {
                call.reject("查询订阅状态失败: \(error.localizedDescription)", "STATUS_QUERY_ERROR", error)
            }
        }
    }
    
    // MARK: - 从后端获取订阅状态
    
    private func getBackendSubscriptionStatus() async throws -> [String: Any]? {
        guard let token = await getCurrentUserToken() else {
            return nil
        }
        
        var request = URLRequest(url: URL(string: "\(apiBaseURL)/api/subscription/status")!)
        request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        
        let (data, response) = try await URLSession.shared.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse,
              httpResponse.statusCode == 200 else {
            return nil
        }
        
        return try JSONSerialization.jsonObject(with: data) as? [String: Any]
    }
    
    // MARK: - 恢复购买
    
    @objc func restorePurchases(_ call: CAPPluginCall) {
        Task {
            do {
                var restoredProducts: [String] = []
                
                // 获取所有历史交易
                for await result in Transaction.all {
                    switch result {
                    case .verified(let transaction):
                        // 验证并同步到后端
                        let receiptData = try await getReceiptData(transaction: transaction)
                        
                        // 查找产品类型
                        var productType: String?
                        for (type, id) in productIds {
                            if id == transaction.productID {
                                productType = type
                                break
                            }
                        }
                        
                        if let type = productType {
                            _ = try await verifyReceiptWithBackend(
                                transactionId: String(transaction.id),
                                productId: type,
                                receiptData: receiptData
                            )
                            restoredProducts.append(transaction.productID)
                        }
                        
                        await transaction.finish()
                    case .unverified:
                        break
                    }
                }
                
                call.resolve([
                    "success": true,
                    "restoredProducts": restoredProducts,
                    "count": restoredProducts.count
                ])
            } catch {
                call.reject("恢复购买失败: \(error.localizedDescription)", "RESTORE_ERROR", error)
            }
        }
    }
    
    // MARK: - 检查订阅可用性
    
    @objc func checkSubscriptionAvailability(_ call: CAPPluginCall) {
        // 检查设备是否支持订阅
        let isAvailable = SKPaymentQueue.canMakePayments()
        
        call.resolve([
            "available": isAvailable,
            "message": isAvailable ? "设备支持应用内购买" : "设备不支持应用内购买或已禁用"
        ])
    }
}
