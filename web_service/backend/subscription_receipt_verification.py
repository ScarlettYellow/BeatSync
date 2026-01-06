#!/usr/bin/env python3
"""
iOS 订阅收据验证
与 StoreKit 2 集成
"""

import os
import json
import base64
import requests
from typing import Optional, Dict
from datetime import datetime
try:
    from subscription_service import is_subscription_enabled, get_db_connection
except ImportError:
    # 如果订阅服务不可用，提供降级函数
    def is_subscription_enabled():
        return False
    def get_db_connection():
        return None

# App Store 收据验证 URL
# 生产环境
APP_STORE_PRODUCTION_URL = "https://buy.itunes.apple.com/verifyReceipt"
# 沙盒环境
APP_STORE_SANDBOX_URL = "https://sandbox.itunes.apple.com/verifyReceipt"

# 从环境变量获取 App Store 共享密钥
APP_STORE_SHARED_SECRET = os.getenv("APP_STORE_SHARED_SECRET", None)


def verify_ios_receipt(receipt_data: str, is_sandbox: bool = False) -> Dict:
    """
    验证 iOS 收据
    
    参数:
        receipt_data: Base64 编码的收据数据
        is_sandbox: 是否为沙盒环境
    
    返回:
        验证结果字典
    """
    if not APP_STORE_SHARED_SECRET:
        return {
            "success": False,
            "error": "APP_STORE_SHARED_SECRET 未配置"
        }
    
    url = APP_STORE_SANDBOX_URL if is_sandbox else APP_STORE_PRODUCTION_URL
    
    payload = {
        "receipt-data": receipt_data,
        "password": APP_STORE_SHARED_SECRET,
        "exclude-old-transactions": True
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        result = response.json()
        
        # 检查状态码
        status = result.get("status", -1)
        
        if status == 0:
            # 验证成功
            return {
                "success": True,
                "receipt": result.get("receipt", {}),
                "latest_receipt_info": result.get("latest_receipt_info", []),
                "pending_renewal_info": result.get("pending_renewal_info", [])
            }
        elif status == 21007:
            # 收据是沙盒收据，但发送到了生产环境
            return verify_ios_receipt(receipt_data, is_sandbox=True)
        elif status == 21008:
            # 收据是生产收据，但发送到了沙盒环境
            return verify_ios_receipt(receipt_data, is_sandbox=False)
        else:
            # 其他错误
            error_messages = {
                21000: "App Store 无法读取你提供的 JSON 数据",
                21002: "receipt-data 属性中的数据格式错误或丢失",
                21003: "收据无法验证",
                21004: "你提供的共享密钥与账户的共享密钥不匹配",
                21005: "收据服务器暂时不可用",
                21006: "此收据有效，但订阅已过期",
                21010: "此收据无法被验证"
            }
            return {
                "success": False,
                "error": error_messages.get(status, f"未知错误: {status}"),
                "status": status
            }
    except Exception as e:
        return {
            "success": False,
            "error": f"验证收据时发生异常: {str(e)}"
        }


def parse_transaction_from_receipt(receipt_info: Dict) -> Optional[Dict]:
    """
    从收据信息中解析交易信息
    
    参数:
        receipt_info: 收据信息字典
    
    返回:
        交易信息字典
    """
    try:
        return {
            "transaction_id": receipt_info.get("transaction_id"),
            "original_transaction_id": receipt_info.get("original_transaction_id"),
            "product_id": receipt_info.get("product_id"),
            "purchase_date_ms": receipt_info.get("purchase_date_ms"),
            "expires_date_ms": receipt_info.get("expires_date_ms"),
            "is_trial_period": receipt_info.get("is_trial_period", False),
            "is_in_intro_offer_period": receipt_info.get("is_in_intro_offer_period", False),
            "cancellation_date_ms": receipt_info.get("cancellation_date_ms")
        }
    except Exception as e:
        print(f"解析交易信息失败: {e}")
        return None


def save_subscription_to_database(user_id: str, transaction_info: Dict, product_type: str) -> bool:
    """
    保存订阅信息到数据库
    
    参数:
        user_id: 用户ID
        transaction_info: 交易信息
        product_type: 产品类型 (如 'basic_monthly', 'premium_yearly')
    
    返回:
        是否成功
    """
    if not is_subscription_enabled():
        return False
    
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        
        # 解析产品类型（公测期套餐）
        subscription_type = None
        download_credits = 0
        
        # 公测期基础版月付
        if "public_beta" in product_type and "basic" in product_type and "monthly" in product_type:
            subscription_type = "basic_monthly"
            download_credits = 20  # 公测期：20次/月
        # 公测期高级版月付
        elif "public_beta" in product_type and "premium" in product_type and "monthly" in product_type:
            subscription_type = "premium_monthly"
            download_credits = 100  # 公测期：100次/月
        # 公测期下载次数加油包
        elif "public_beta" in product_type and "pack" in product_type:
            # 提取包大小（pack.10 或 pack.20）
            if "pack.10" in product_type or "pack_10" in product_type:
                download_credits = 10
            elif "pack.20" in product_type or "pack_20" in product_type:
                download_credits = 20
            else:
                # 尝试从产品ID中提取数字
                import re
                match = re.search(r'pack[._](\d+)', product_type)
                if match:
                    download_credits = int(match.group(1))
                else:
                    download_credits = 10  # 默认值
            subscription_type = None  # 不是订阅，是一次性购买
        # 兼容旧的产品ID格式（向后兼容）
        elif product_type.startswith("basic_monthly"):
            subscription_type = "basic_monthly"
            download_credits = 100
        elif product_type.startswith("basic_yearly"):
            subscription_type = "basic_yearly"
            download_credits = 600
        elif product_type.startswith("premium_monthly"):
            subscription_type = "premium_monthly"
            download_credits = 1000
        elif product_type.startswith("premium_yearly"):
            subscription_type = "premium_yearly"
            download_credits = 12000
        elif product_type.startswith("pack_"):
            # 一次性购买包
            pack_size = product_type.replace("pack_", "")
            download_credits = int(pack_size)
            subscription_type = None  # 不是订阅，是一次性购买
        
        # 保存订阅记录
        if subscription_type:
            from datetime import datetime, timedelta
            import time
            
            purchase_date = datetime.fromtimestamp(transaction_info.get("purchase_date_ms", 0) / 1000)
            expires_date = None
            if transaction_info.get("expires_date_ms"):
                expires_date = datetime.fromtimestamp(transaction_info.get("expires_date_ms") / 1000)
            
            cursor.execute("""
                INSERT INTO subscriptions (
                    user_id, subscription_type, status, start_date, end_date,
                    platform, transaction_id, receipt_data
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                user_id,
                subscription_type,
                "active" if not expires_date or expires_date > datetime.utcnow() else "expired",
                purchase_date.isoformat(),
                expires_date.isoformat() if expires_date else None,
                "ios",
                transaction_info.get("transaction_id"),
                json.dumps(transaction_info)
            ))
            subscription_id = cursor.lastrowid
        else:
            subscription_id = None
        
        # 保存下载次数
        if download_credits > 0:
            from datetime import datetime, timedelta
            
            period_start = datetime.utcnow()
            period_end = None
            
            if subscription_type:
                # 订阅：根据订阅类型设置周期
                if "monthly" in subscription_type:
                    period_end = period_start + timedelta(days=30)
                elif "yearly" in subscription_type:
                    period_end = period_start + timedelta(days=365)
            else:
                # 公测期下载次数加油包：有效期3个月
                if "public_beta" in product_type and "pack" in product_type:
                    period_end = period_start + timedelta(days=90)  # 3个月有效期
                else:
                    # 其他一次性购买：不设置过期时间
                    period_end = None
            
            credit_type = "subscription" if subscription_type else "purchase"
            
            cursor.execute("""
                INSERT INTO download_credits (
                    user_id, credit_type, total_credits, used_credits, remaining_credits,
                    period_start, period_end, source_subscription_id, source_purchase_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                user_id,
                credit_type,
                download_credits,
                0,
                download_credits,
                period_start.isoformat(),
                period_end.isoformat() if period_end else None,
                subscription_id,
                None if subscription_id else cursor.lastrowid
            ))
        
        # 保存支付记录
        cursor.execute("""
            INSERT INTO payment_records (
                user_id, payment_type, product_id, amount, currency,
                platform, transaction_id, status, receipt_data, verified, verified_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id,
            "subscription" if subscription_type else "purchase",
            product_type,
            0,  # 金额从 App Store 获取，这里先设为0
            "CNY",
            "ios",
            transaction_info.get("transaction_id"),
            "completed",
            json.dumps(transaction_info),
            True,
            datetime.utcnow().isoformat()
        ))
        
        conn.commit()
        return True
        
    except Exception as e:
        print(f"保存订阅信息失败: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

