#!/usr/bin/env python3
"""
支付服务模块
支持微信支付和支付宝支付
"""

import os
import uuid
import json
from datetime import datetime
from typing import Optional, Dict
from pathlib import Path

# 导入订阅系统模块
try:
    from subscription_db import get_db_path
    from subscription_service import is_subscription_enabled
    import sqlite3
    PAYMENT_AVAILABLE = True
except ImportError:
    PAYMENT_AVAILABLE = False
    print("WARNING: 支付系统模块依赖订阅系统，订阅系统未找到")

# 环境变量配置
WECHAT_PAY_APPID = os.getenv("WECHAT_PAY_APPID", None)
WECHAT_PAY_MCHID = os.getenv("WECHAT_PAY_MCHID", None)
WECHAT_PAY_API_KEY = os.getenv("WECHAT_PAY_API_KEY", None)
WECHAT_PAY_CERT_PATH = os.getenv("WECHAT_PAY_CERT_PATH", None)  # 证书路径（可选）

ALIPAY_APPID = os.getenv("ALIPAY_APPID", None)
ALIPAY_PRIVATE_KEY = os.getenv("ALIPAY_PRIVATE_KEY", None)  # 应用私钥
ALIPAY_PUBLIC_KEY = os.getenv("ALIPAY_PUBLIC_KEY", None)  # 支付宝公钥
ALIPAY_SIGN_TYPE = os.getenv("ALIPAY_SIGN_TYPE", "RSA2")

# 支付回调 URL（从环境变量获取，或使用默认值）
BASE_URL = os.getenv("BASE_URL", "https://beatsync.site")
WECHAT_CALLBACK_URL = f"{BASE_URL}/api/payment/callback/wechat"
ALIPAY_CALLBACK_URL = f"{BASE_URL}/api/payment/callback/alipay"

# 产品价格配置（单位：元）
# 公测期套餐配置
PRODUCT_PRICES = {
    # 公测期订阅
    "basic_monthly": 4.80,  # 公测期基础版：4.8元/月
    "premium_monthly": 19.90,  # 公测期高级版：19.9元/月
    # 公测期下载次数加油包
    "pack_10": 5.00,  # 10次包：5元
    "pack_20": 9.00,  # 20次包：9元
    # 兼容旧配置（向后兼容）
    "basic_yearly": 99.00,
    "premium_yearly": 499.00,
    "pack_50": 20.00,
    "pack_100": 35.00,
}

# 产品下载次数配置
# 公测期套餐配置
PRODUCT_CREDITS = {
    # 公测期订阅
    "basic_monthly": 20,  # 公测期基础版：20次/月
    "premium_monthly": 100,  # 公测期高级版：100次/月
    # 公测期下载次数加油包
    "pack_10": 10,  # 10次包
    "pack_20": 20,  # 20次包
    # 兼容旧配置（向后兼容）
    "basic_yearly": 1200,
    "premium_yearly": 3600,
    "pack_50": 50,
    "pack_100": 100,
}


def get_db_connection():
    """获取数据库连接"""
    if not PAYMENT_AVAILABLE:
        return None
    db_path = get_db_path()
    if not db_path:
        return None
    return sqlite3.connect(str(db_path), check_same_thread=False)


def create_payment_order(user_id: str, product_id: str, payment_method: str = "wechat") -> Optional[Dict]:
    """
    创建支付订单
    
    参数:
        user_id: 用户ID
        product_id: 产品ID
        payment_method: 支付方式 ('wechat' 或 'alipay')
    
    返回:
        支付订单信息字典，包含 order_id 和 payment_url
    """
    if not is_subscription_enabled():
        return None
    
    # 验证产品ID
    if product_id not in PRODUCT_PRICES:
        return None
    
    # 获取产品价格和下载次数
    amount = PRODUCT_PRICES[product_id]
    credits = PRODUCT_CREDITS[product_id]
    
    # 生成订单ID
    order_id = f"ORDER_{int(datetime.utcnow().timestamp() * 1000)}_{uuid.uuid4().hex[:8].upper()}"
    
    # 保存订单到数据库
    conn = get_db_connection()
    if not conn:
        return None
    
    try:
        cursor = conn.cursor()
        
        # 确定支付类型
        payment_type = "subscription" if product_id in ["basic_monthly", "basic_yearly", "premium_monthly", "premium_yearly"] else "one_time"
        
        # 插入支付记录
        cursor.execute("""
            INSERT INTO payment_records (
                user_id, payment_type, product_id, amount, currency,
                platform, transaction_id, status, verified
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id,
            payment_type,
            product_id,
            amount,
            "CNY",
            payment_method,
            order_id,
            "pending",
            0
        ))
        
        conn.commit()
        
        # 生成支付URL
        if payment_method == "wechat":
            payment_url = create_wechat_payment_url(order_id, product_id, amount, user_id)
        elif payment_method == "alipay":
            payment_url = create_alipay_payment_url(order_id, product_id, amount, user_id)
        else:
            payment_url = None
        
        return {
            "order_id": order_id,
            "product_id": product_id,
            "amount": amount,
            "credits": credits,
            "payment_method": payment_method,
            "payment_url": payment_url,
            "status": "pending"
        }
    except Exception as e:
        print(f"创建支付订单失败: {e}")
        conn.rollback()
        return None
    finally:
        conn.close()


def create_wechat_payment_url(order_id: str, product_id: str, amount: float, user_id: str) -> Optional[str]:
    """
    创建微信支付URL
    
    注意: 这是简化版本，实际实现需要使用微信支付 SDK
    """
    if not WECHAT_PAY_APPID or not WECHAT_PAY_MCHID:
        # 如果没有配置，返回模拟URL（用于测试）
        return f"{BASE_URL}/payment/wechat?order_id={order_id}&amount={amount}"
    
    try:
        # 这里应该使用 wechatpay-python SDK
        # 示例代码（需要根据实际SDK调整）:
        # from wechatpay import WeChatPay
        # wechat_pay = WeChatPay(
        #     appid=WECHAT_PAY_APPID,
        #     mchid=WECHAT_PAY_MCHID,
        #     api_key=WECHAT_PAY_API_KEY
        # )
        # payment_url = wechat_pay.create_order(...)
        
        # 临时返回模拟URL
        return f"{BASE_URL}/payment/wechat?order_id={order_id}&amount={amount}"
    except Exception as e:
        print(f"创建微信支付URL失败: {e}")
        return None


def create_alipay_payment_url(order_id: str, product_id: str, amount: float, user_id: str) -> Optional[str]:
    """
    创建支付宝支付URL
    
    注意: 这是简化版本，实际实现需要使用支付宝 SDK
    """
    if not ALIPAY_APPID or not ALIPAY_PRIVATE_KEY:
        # 如果没有配置，返回模拟URL（用于测试）
        return f"{BASE_URL}/payment/alipay?order_id={order_id}&amount={amount}"
    
    try:
        # 这里应该使用 alipay-sdk-python SDK
        # 示例代码（需要根据实际SDK调整）:
        # from alipay import AliPay
        # alipay = AliPay(
        #     appid=ALIPAY_APPID,
        #     app_private_key_string=ALIPAY_PRIVATE_KEY,
        #     alipay_public_key_string=ALIPAY_PUBLIC_KEY,
        #     sign_type=ALIPAY_SIGN_TYPE
        # )
        # payment_url = alipay.api_alipay_trade_page_pay(...)
        
        # 临时返回模拟URL
        return f"{BASE_URL}/payment/alipay?order_id={order_id}&amount={amount}"
    except Exception as e:
        print(f"创建支付宝支付URL失败: {e}")
        return None


def verify_wechat_payment(callback_data: Dict) -> Optional[Dict]:
    """
    验证微信支付回调
    
    参数:
        callback_data: 微信支付回调数据
    
    返回:
        验证结果字典，包含 order_id, status, amount 等
    """
    # 这里应该使用微信支付 SDK 验证签名
    # 示例代码（需要根据实际SDK调整）:
    # from wechatpay import WeChatPay
    # wechat_pay = WeChatPay(...)
    # result = wechat_pay.verify_callback(callback_data)
    
    # 临时实现：从回调数据中提取订单信息
    order_id = callback_data.get("out_trade_no") or callback_data.get("order_id")
    transaction_id = callback_data.get("transaction_id")
    status = callback_data.get("result_code") or callback_data.get("status")
    
    if order_id and status == "SUCCESS":
        return {
            "success": True,
            "order_id": order_id,
            "transaction_id": transaction_id,
            "status": "completed"
        }
    
    return None


def verify_alipay_payment(callback_data: Dict) -> Optional[Dict]:
    """
    验证支付宝支付回调
    
    参数:
        callback_data: 支付宝支付回调数据
    
    返回:
        验证结果字典，包含 order_id, status, amount 等
    """
    # 这里应该使用支付宝 SDK 验证签名
    # 示例代码（需要根据实际SDK调整）:
    # from alipay import AliPay
    # alipay = AliPay(...)
    # result = alipay.verify(callback_data, callback_data.get("sign"))
    
    # 临时实现：从回调数据中提取订单信息
    order_id = callback_data.get("out_trade_no") or callback_data.get("order_id")
    transaction_id = callback_data.get("trade_no")
    status = callback_data.get("trade_status") or callback_data.get("status")
    
    if order_id and status in ["TRADE_SUCCESS", "TRADE_FINISHED", "completed"]:
        return {
            "success": True,
            "order_id": order_id,
            "transaction_id": transaction_id,
            "status": "completed"
        }
    
    return None


def update_payment_status(order_id: str, status: str, transaction_id: Optional[str] = None) -> bool:
    """
    更新支付订单状态
    
    参数:
        order_id: 订单ID
        status: 订单状态 ('completed', 'failed', 'cancelled')
        transaction_id: 交易ID（可选）
    
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
        
        # 更新支付记录
        cursor.execute("""
            UPDATE payment_records
            SET status = ?,
                transaction_id = COALESCE(?, transaction_id),
                verified = ?,
                verified_at = ?,
                updated_at = ?
            WHERE transaction_id = ?
        """, (
            status,
            transaction_id,
            1 if status == "completed" else 0,
            datetime.utcnow().isoformat() if status == "completed" else None,
            datetime.utcnow().isoformat(),
            order_id
        ))
        
        conn.commit()
        
        # 如果支付成功，更新订阅或下载次数
        if status == "completed":
            # 获取订单信息
            cursor.execute("""
                SELECT user_id, product_id, payment_type
                FROM payment_records
                WHERE transaction_id = ?
            """, (order_id,))
            
            order = cursor.fetchone()
            if order:
                user_id, product_id, payment_type = order
                
                # 更新订阅或下载次数
                from subscription_receipt_verification import save_subscription_to_database
                
                # 构造交易信息（模拟）
                transaction_info = {
                    "transaction_id": transaction_id or order_id,
                    "product_id": product_id,
                    "purchase_date_ms": int(datetime.utcnow().timestamp() * 1000),
                    "expires_date_ms": None
                }
                
                # 保存订阅或购买记录
                save_subscription_to_database(user_id, transaction_info, product_id)
        
        return True
    except Exception as e:
        print(f"更新支付状态失败: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()


def get_payment_status(order_id: str) -> Optional[Dict]:
    """
    查询支付订单状态
    
    参数:
        order_id: 订单ID
    
    返回:
        订单状态信息字典
    """
    if not is_subscription_enabled():
        return None
    
    conn = get_db_connection()
    if not conn:
        return None
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                id, user_id, payment_type, product_id, amount, currency,
                platform, transaction_id, status, verified, verified_at,
                created_at, updated_at
            FROM payment_records
            WHERE transaction_id = ?
        """, (order_id,))
        
        order = cursor.fetchone()
        if order:
            return {
                "order_id": order_id,
                "user_id": order[1],
                "payment_type": order[2],
                "product_id": order[3],
                "amount": float(order[4]),
                "currency": order[5],
                "platform": order[6],
                "transaction_id": order[7],
                "status": order[8],
                "verified": bool(order[9]),
                "verified_at": order[10],
                "created_at": order[11],
                "updated_at": order[12]
            }
        return None
    except Exception as e:
        print(f"查询支付状态失败: {e}")
        return None
    finally:
        conn.close()
