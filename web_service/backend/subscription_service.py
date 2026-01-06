#!/usr/bin/env python3
"""
订阅系统服务层
提供订阅、下载次数、白名单等核心功能
"""

import os
import sqlite3
import uuid
import jwt
from pathlib import Path
from typing import Optional, Dict, List
from datetime import datetime, timedelta
from subscription_db import get_db_path

# 环境变量配置
SUBSCRIPTION_ENABLED = os.getenv("SUBSCRIPTION_ENABLED", "false").lower() == "true"
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24 * 30  # 30天


def is_subscription_enabled() -> bool:
    """检查订阅系统是否启用"""
    return SUBSCRIPTION_ENABLED and get_db_path() is not None


def get_db_connection():
    """获取数据库连接"""
    db_path = get_db_path()
    if not db_path:
        return None
    return sqlite3.connect(str(db_path), check_same_thread=False)


# ==================== 用户认证 ====================

def generate_jwt_token(user_id: str) -> str:
    """生成 JWT Token"""
    payload = {
        "user_id": user_id,
        "exp": datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS),
        "iat": datetime.utcnow()
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def verify_jwt_token(token: str) -> Optional[str]:
    """验证 JWT Token，返回 user_id"""
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload.get("user_id")
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def create_or_get_user(device_id: Optional[str] = None, email: Optional[str] = None, phone: Optional[str] = None) -> Dict:
    """创建或获取用户"""
    if not is_subscription_enabled():
        # 订阅系统未启用，返回临时 user_id
        return {
            "user_id": str(uuid.uuid4()),
            "token": None
        }
    
    conn = get_db_connection()
    if not conn:
        return {"user_id": str(uuid.uuid4()), "token": None}
    
    try:
        cursor = conn.cursor()
        
        # 尝试通过 device_id、email 或 phone 查找用户
        user_id = None
        if device_id:
            cursor.execute("SELECT user_id FROM users WHERE device_id = ?", (device_id,))
            result = cursor.fetchone()
            if result:
                user_id = result[0]
        
        if not user_id and email:
            cursor.execute("SELECT user_id FROM users WHERE email = ?", (email,))
            result = cursor.fetchone()
            if result:
                user_id = result[0]
        
        if not user_id and phone:
            cursor.execute("SELECT user_id FROM users WHERE phone = ?", (phone,))
            result = cursor.fetchone()
            if result:
                user_id = result[0]
        
        # 如果用户不存在，创建新用户
        if not user_id:
            user_id = str(uuid.uuid4())
            cursor.execute("""
                INSERT INTO users (user_id, device_id, email, phone)
                VALUES (?, ?, ?, ?)
            """, (user_id, device_id, email, phone))
            conn.commit()
        
        # 生成 Token
        token = generate_jwt_token(user_id)
        
        return {
            "user_id": user_id,
            "token": token
        }
    except Exception as e:
        print(f"创建用户失败: {e}")
        return {"user_id": str(uuid.uuid4()), "token": None}
    finally:
        conn.close()


# ==================== 白名单管理 ====================

def check_whitelist(user_id: str) -> bool:
    """检查用户是否在白名单中"""
    if not is_subscription_enabled():
        return False
    
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM whitelist WHERE user_id = ?", (user_id,))
        result = cursor.fetchone()
        return result is not None
    except Exception as e:
        print(f"白名单检查异常: {e}")
        return False
    finally:
        conn.close()


def add_to_whitelist(user_id: str, added_by: str, reason: Optional[str] = None) -> bool:
    """添加用户到白名单"""
    if not is_subscription_enabled():
        return False
    
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO whitelist (user_id, added_by, reason)
            VALUES (?, ?, ?)
        """, (user_id, added_by, reason))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        # 用户已在白名单中
        return False
    except Exception as e:
        print(f"添加白名单异常: {e}")
        return False
    finally:
        conn.close()


def remove_from_whitelist(user_id: str) -> bool:
    """从白名单中删除用户"""
    if not is_subscription_enabled():
        return False
    
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM whitelist WHERE user_id = ?", (user_id,))
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        print(f"删除白名单异常: {e}")
        return False
    finally:
        conn.close()


def get_whitelist_users(page: int = 1, limit: int = 20, search: Optional[str] = None) -> Dict:
    """获取白名单用户列表"""
    if not is_subscription_enabled():
        return {"total": 0, "page": page, "limit": limit, "users": []}
    
    conn = get_db_connection()
    if not conn:
        return {"total": 0, "page": page, "limit": limit, "users": []}
    
    try:
        cursor = conn.cursor()
        offset = (page - 1) * limit
        
        if search:
            search_pattern = f"%{search}%"
            query = """
                SELECT w.user_id, w.added_by, w.reason, w.created_at, u.email, u.phone
                FROM whitelist w
                LEFT JOIN users u ON w.user_id = u.user_id
                WHERE w.user_id LIKE ? OR u.email LIKE ? OR u.phone LIKE ?
                ORDER BY w.created_at DESC
                LIMIT ? OFFSET ?
            """
            cursor.execute(query, (search_pattern, search_pattern, search_pattern, limit, offset))
            users = cursor.fetchall()
            
            count_query = """
                SELECT COUNT(*) as total
                FROM whitelist w
                LEFT JOIN users u ON w.user_id = u.user_id
                WHERE w.user_id LIKE ? OR u.email LIKE ? OR u.phone LIKE ?
            """
            cursor.execute(count_query, (search_pattern, search_pattern, search_pattern))
            total = cursor.fetchone()[0]
        else:
            query = """
                SELECT w.user_id, w.added_by, w.reason, w.created_at, u.email, u.phone
                FROM whitelist w
                LEFT JOIN users u ON w.user_id = u.user_id
                ORDER BY w.created_at DESC
                LIMIT ? OFFSET ?
            """
            cursor.execute(query, (limit, offset))
            users = cursor.fetchall()
            
            cursor.execute("SELECT COUNT(*) FROM whitelist")
            total = cursor.fetchone()[0]
        
        users_list = []
        for row in users:
            users_list.append({
                "user_id": row[0],
                "added_by": row[1],
                "reason": row[2],
                "created_at": row[3],
                "email": row[4],
                "phone": row[5]
            })
        
        return {
            "total": total,
            "page": page,
            "limit": limit,
            "users": users_list
        }
    except Exception as e:
        print(f"获取白名单列表异常: {e}")
        return {"total": 0, "page": page, "limit": limit, "users": []}
    finally:
        conn.close()


# ==================== 下载次数管理 ====================

def check_download_credits(user_id: str) -> Dict:
    """检查用户可用下载次数"""
    if not is_subscription_enabled():
        return {
            "is_whitelisted": False,
            "can_download": True,  # 订阅系统未启用，允许下载
            "available_credits": {"subscription": 0, "purchased": 0, "free_trial": 0},
            "total_remaining": 999999  # 使用大数字代替 float('inf')
        }
    
    # 首先检查白名单
    if check_whitelist(user_id):
        return {
            "is_whitelisted": True,
            "can_download": True,
            "available_credits": {"subscription": 0, "purchased": 0, "free_trial": 0},
            "total_remaining": 999999  # 使用大数字代替 float('inf')
        }
    
    conn = get_db_connection()
    if not conn:
        # 数据库连接失败：如果订阅系统启用，不允许下载（安全起见）
        return {
            "is_whitelisted": False,
            "can_download": False,  # 订阅系统启用但数据库连接失败，不允许下载
            "available_credits": {"subscription": 0, "purchased": 0, "free_trial": 0},
            "total_remaining": 0
        }
    
    try:
        cursor = conn.cursor()
        now = datetime.utcnow().isoformat()
        
        # 检查订阅次数（当前有效的订阅）
        cursor.execute("""
            SELECT SUM(dc.remaining_credits)
            FROM download_credits dc
            JOIN subscriptions s ON dc.source_subscription_id = s.id
            WHERE dc.user_id = ? 
            AND dc.credit_type = 'subscription'
            AND dc.remaining_credits > 0
            AND s.status = 'active'
            AND (dc.period_end IS NULL OR dc.period_end > ?)
        """, (user_id, now))
        subscription_credits = cursor.fetchone()[0] or 0
        
        # 检查购买次数（未过期）
        cursor.execute("""
            SELECT SUM(remaining_credits)
            FROM download_credits
            WHERE user_id = ?
            AND credit_type = 'purchase'
            AND remaining_credits > 0
        """, (user_id,))
        purchased_credits = cursor.fetchone()[0] or 0
        
        # 检查免费体验：前5次处理免费（公测期新规则）
        # 获取用户已使用的免费处理次数
        cursor.execute("""
            SELECT COALESCE(SUM(used_credits), 0)
            FROM download_credits
            WHERE user_id = ?
            AND credit_type = 'free_trial'
        """, (user_id,))
        free_trial_used = cursor.fetchone()[0] or 0
        
        free_trial_credits = 0
        # 如果已使用的免费次数少于5次，计算剩余免费次数
        if free_trial_used < 5:
            free_trial_credits = 5 - free_trial_used
            
            # 检查是否有免费试用记录，如果没有则创建
            cursor.execute("""
                SELECT id, remaining_credits
                FROM download_credits
                WHERE user_id = ?
                AND credit_type = 'free_trial'
                LIMIT 1
            """, (user_id,))
            free_credit = cursor.fetchone()
            
            if not free_credit:
                # 创建免费体验记录（前5次处理免费）
                now = datetime.utcnow()
                cursor.execute("""
                    INSERT INTO download_credits (user_id, credit_type, total_credits, used_credits, remaining_credits, period_start, period_end)
                    VALUES (?, 'free_trial', 5, 0, 5, ?, NULL)
                """, (user_id, now.isoformat()))
                conn.commit()
                free_trial_credits = 5
                # 重新查询以确保数据正确
                cursor.execute("""
                    SELECT id, remaining_credits
                    FROM download_credits
                    WHERE user_id = ?
                    AND credit_type = 'free_trial'
                    LIMIT 1
                """, (user_id,))
                free_credit_check = cursor.fetchone()
                if free_credit_check:
                    free_trial_credits = free_credit_check[1] if free_credit_check[1] > 0 else 0
            else:
                # 使用现有记录的剩余次数
                free_trial_credits = free_credit[1] if free_credit[1] > 0 else 0
        
        total_remaining = subscription_credits + purchased_credits + free_trial_credits
        
        # 如果订阅系统启用，必须检查是否有可用次数
        # 如果没有订阅、购买包或免费体验，不允许下载
        can_download = total_remaining > 0
        
        return {
            "is_whitelisted": False,
            "can_download": can_download,
            "available_credits": {
                "subscription": subscription_credits,
                "purchased": purchased_credits,
                "free_trial": free_trial_credits
            },
            "total_remaining": total_remaining if total_remaining > 0 else 0
        }
    except Exception as e:
        print(f"检查下载次数异常: {e}")
        import traceback
        traceback.print_exc()
        # 异常时：如果订阅系统启用，不允许下载（安全起见）
        # 如果订阅系统未启用，允许下载（向后兼容）
        if is_subscription_enabled():
            return {
                "is_whitelisted": False,
                "can_download": False,  # 订阅系统启用但检查失败，不允许下载
                "available_credits": {"subscription": 0, "purchased": 0, "free_trial": 0},
                "total_remaining": 0
            }
        else:
            return {
                "is_whitelisted": False,
                "can_download": True,  # 订阅系统未启用，允许下载（向后兼容）
                "available_credits": {"subscription": 0, "purchased": 0, "free_trial": 0},
                "total_remaining": 999999  # 使用大数字代替 float('inf')
            }
    finally:
        conn.close()


def consume_download_credit(user_id: str, task_id: str, version: str, ip_address: Optional[str] = None, user_agent: Optional[str] = None) -> Dict:
    """消费下载次数"""
    if not is_subscription_enabled():
        # 订阅系统未启用，不消费次数
        return {"credit_type": "none", "remaining": 999999}  # 使用大数字代替 float('inf')
    
    # 检查白名单
    if check_whitelist(user_id):
        # 记录下载日志，但不消费次数
        log_download(user_id, task_id, version, credit_type="whitelist", ip_address=ip_address, user_agent=user_agent)
        return {"credit_type": "whitelist", "remaining": 999999}  # 使用大数字代替 float('inf')
    
    conn = get_db_connection()
    if not conn:
        # 数据库连接失败，不消费次数
        return {"credit_type": "none", "remaining": 999999}  # 使用大数字代替 float('inf')
    
    try:
        cursor = conn.cursor()
        now = datetime.utcnow().isoformat()
        
        # 优先级：免费周次数 > 购买次数 > 订阅次数
        
        # 1. 优先使用免费体验次数（前5次处理免费）
        cursor.execute("""
            SELECT id, remaining_credits
            FROM download_credits
            WHERE user_id = ?
            AND credit_type = 'free_trial'
            AND remaining_credits > 0
            ORDER BY created_at ASC
            LIMIT 1
        """, (user_id,))
        free_credit = cursor.fetchone()
        
        # 如果没有免费体验记录，检查是否已经使用过5次
        if not free_credit:
            cursor.execute("""
                SELECT COALESCE(SUM(used_credits), 0)
                FROM download_credits
                WHERE user_id = ?
                AND credit_type = 'free_trial'
            """, (user_id,))
            free_trial_used = cursor.fetchone()[0] or 0
            
            # 如果已使用少于5次，创建免费体验记录
            if free_trial_used < 5:
                now_dt = datetime.utcnow()
                cursor.execute("""
                    INSERT INTO download_credits (user_id, credit_type, total_credits, used_credits, remaining_credits, period_start, period_end)
                    VALUES (?, 'free_trial', 5, ?, ?, ?, NULL)
                """, (user_id, free_trial_used, 5 - free_trial_used, now_dt.isoformat()))
                conn.commit()
                # 重新查询
                cursor.execute("""
                    SELECT id, remaining_credits
                    FROM download_credits
                    WHERE user_id = ?
                    AND credit_type = 'free_trial'
                    AND remaining_credits > 0
                    ORDER BY created_at ASC
                    LIMIT 1
                """, (user_id,))
                free_credit = cursor.fetchone()
        
        if free_credit:
            credit_id, remaining = free_credit
            cursor.execute("""
                UPDATE download_credits
                SET used_credits = used_credits + 1,
                    remaining_credits = remaining_credits - 1,
                    updated_at = ?
                WHERE id = ?
            """, (now, credit_id))
            conn.commit()
            log_download(user_id, task_id, version, credit_id=credit_id, credit_type="free_trial", ip_address=ip_address, user_agent=user_agent)
            return {"credit_type": "free_trial", "remaining": remaining - 1}
        
        # 2. 使用购买次数
        cursor.execute("""
            SELECT id, remaining_credits
            FROM download_credits
            WHERE user_id = ?
            AND credit_type = 'purchase'
            AND remaining_credits > 0
            ORDER BY created_at ASC
            LIMIT 1
        """, (user_id,))
        purchased_credit = cursor.fetchone()
        
        if purchased_credit:
            credit_id, remaining = purchased_credit
            cursor.execute("""
                UPDATE download_credits
                SET used_credits = used_credits + 1,
                    remaining_credits = remaining_credits - 1,
                    updated_at = ?
                WHERE id = ?
            """, (now, credit_id))
            conn.commit()
            log_download(user_id, task_id, version, credit_id=credit_id, credit_type="purchase", ip_address=ip_address, user_agent=user_agent)
            return {"credit_type": "purchase", "remaining": remaining - 1}
        
        # 3. 使用订阅次数
        cursor.execute("""
            SELECT dc.id, dc.remaining_credits
            FROM download_credits dc
            JOIN subscriptions s ON dc.source_subscription_id = s.id
            WHERE dc.user_id = ?
            AND dc.credit_type = 'subscription'
            AND dc.remaining_credits > 0
            AND s.status = 'active'
            AND (dc.period_end IS NULL OR dc.period_end > ?)
            ORDER BY dc.created_at ASC
            LIMIT 1
        """, (user_id, now))
        subscription_credit = cursor.fetchone()
        
        if subscription_credit:
            credit_id, remaining = subscription_credit
            cursor.execute("""
                UPDATE download_credits
                SET used_credits = used_credits + 1,
                    remaining_credits = remaining_credits - 1,
                    updated_at = ?
                WHERE id = ?
            """, (now, credit_id))
            conn.commit()
            log_download(user_id, task_id, version, credit_id=credit_id, credit_type="subscription", ip_address=ip_address, user_agent=user_agent)
            return {"credit_type": "subscription", "remaining": remaining - 1}
        
        # 没有可用次数
        return {"credit_type": "none", "remaining": 0}
        
    except Exception as e:
        print(f"消费下载次数异常: {e}")
        # 异常时降级，不消费次数
        return {"credit_type": "none", "remaining": 999999}  # 使用大数字代替 float('inf')
    finally:
        conn.close()


def log_download(user_id: str, task_id: str, version: str, credit_id: Optional[int] = None, credit_type: Optional[str] = None, ip_address: Optional[str] = None, user_agent: Optional[str] = None):
    """记录下载日志"""
    if not is_subscription_enabled():
        return
    
    conn = get_db_connection()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO download_logs (user_id, task_id, version, credit_id, credit_type, ip_address, user_agent)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (user_id, task_id, version, credit_id, credit_type, ip_address, user_agent))
        conn.commit()
    except Exception as e:
        print(f"记录下载日志异常: {e}")
    finally:
        conn.close()


# ==================== 订阅信息查询 ====================

def get_user_subscription_info(user_id: str) -> Optional[Dict]:
    """获取用户当前活跃订阅信息"""
    if not is_subscription_enabled():
        return None
    
    conn = get_db_connection()
    if not conn:
        return None
    
    try:
        cursor = conn.cursor()
        now = datetime.utcnow().isoformat()
        
        # 查询用户当前活跃的订阅（状态为 active，且未过期）
        cursor.execute("""
            SELECT 
                id,
                subscription_type,
                status,
                start_date,
                end_date,
                auto_renew,
                platform,
                transaction_id,
                created_at
            FROM subscriptions
            WHERE user_id = ?
            AND status = 'active'
            AND (end_date IS NULL OR end_date > ?)
            ORDER BY created_at DESC
            LIMIT 1
        """, (user_id, now))
        
        subscription = cursor.fetchone()
        
        if subscription:
            sub_id, sub_type, status, start_date, end_date, auto_renew, platform, transaction_id, created_at = subscription
            
            return {
                "id": sub_id,
                "subscription_type": sub_type,
                "status": status,
                "start_date": start_date,
                "end_date": end_date,
                "auto_renew": bool(auto_renew),
                "platform": platform,
                "transaction_id": transaction_id,
                "created_at": created_at
            }
        
        return None
    except Exception as e:
        print(f"获取订阅信息异常: {e}")
        return None
    finally:
        conn.close()


def get_subscription_history(user_id: str, page: int = 1, limit: int = 20) -> Dict:
    """获取用户订阅历史"""
    if not is_subscription_enabled():
        return {
            "total": 0,
            "page": page,
            "limit": limit,
            "subscriptions": []
        }
    
    conn = get_db_connection()
    if not conn:
        return {
            "total": 0,
            "page": page,
            "limit": limit,
            "subscriptions": []
        }
    
    try:
        cursor = conn.cursor()
        offset = (page - 1) * limit
        
        # 查询总数
        cursor.execute("""
            SELECT COUNT(*) FROM subscriptions WHERE user_id = ?
        """, (user_id,))
        total = cursor.fetchone()[0] or 0
        
        # 查询订阅列表
        cursor.execute("""
            SELECT 
                id,
                subscription_type,
                status,
                start_date,
                end_date,
                auto_renew,
                platform,
                transaction_id,
                created_at,
                updated_at
            FROM subscriptions
            WHERE user_id = ?
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
        """, (user_id, limit, offset))
        
        subscriptions = []
        for row in cursor.fetchall():
            sub_id, sub_type, status, start_date, end_date, auto_renew, platform, transaction_id, created_at, updated_at = row
            subscriptions.append({
                "id": sub_id,
                "subscription_type": sub_type,
                "status": status,
                "start_date": start_date,
                "end_date": end_date,
                "auto_renew": bool(auto_renew),
                "platform": platform,
                "transaction_id": transaction_id,
                "created_at": created_at,
                "updated_at": updated_at
            })
        
        return {
            "total": total,
            "page": page,
            "limit": limit,
            "subscriptions": subscriptions
        }
    except Exception as e:
        print(f"获取订阅历史异常: {e}")
        return {
            "total": 0,
            "page": page,
            "limit": limit,
            "subscriptions": []
        }
    finally:
        conn.close()


def get_download_history(user_id: str, page: int = 1, limit: int = 20) -> Dict:
    """获取用户下载记录"""
    if not is_subscription_enabled():
        return {
            "total": 0,
            "page": page,
            "limit": limit,
            "downloads": []
        }
    
    conn = get_db_connection()
    if not conn:
        return {
            "total": 0,
            "page": page,
            "limit": limit,
            "downloads": []
        }
    
    try:
        cursor = conn.cursor()
        offset = (page - 1) * limit
        
        # 查询总数
        cursor.execute("""
            SELECT COUNT(*) FROM download_logs WHERE user_id = ?
        """, (user_id,))
        total = cursor.fetchone()[0] or 0
        
        # 查询下载记录列表
        cursor.execute("""
            SELECT 
                id,
                task_id,
                version,
                credit_type,
                ip_address,
                user_agent,
                created_at
            FROM download_logs
            WHERE user_id = ?
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
        """, (user_id, limit, offset))
        
        downloads = []
        for row in cursor.fetchall():
            dl_id, task_id, version, credit_type, ip_address, user_agent, created_at = row
            downloads.append({
                "id": dl_id,
                "task_id": task_id,
                "version": version,
                "credit_type": credit_type or "unknown",
                "ip_address": ip_address,
                "user_agent": user_agent,
                "created_at": created_at
            })
        
        return {
            "total": total,
            "page": page,
            "limit": limit,
            "downloads": downloads
        }
    except Exception as e:
        print(f"获取下载记录异常: {e}")
        return {
            "total": 0,
            "page": page,
            "limit": limit,
            "downloads": []
        }
    finally:
        conn.close()


def get_used_credits_stats(user_id: str) -> Dict:
    """获取用户已使用次数统计"""
    if not is_subscription_enabled():
        return {
            "free_trial": {"used": 0, "total": 0},
            "subscription": {"used": 0, "total": 0},
            "purchase": {"used": 0, "total": 0}
        }
    
    conn = get_db_connection()
    if not conn:
        return {
            "free_trial": {"used": 0, "total": 0},
            "subscription": {"used": 0, "total": 0},
            "purchase": {"used": 0, "total": 0}
        }
    
    try:
        cursor = conn.cursor()
        
        # 统计免费试用已使用次数
        cursor.execute("""
            SELECT 
                SUM(used_credits) as used,
                SUM(total_credits) as total
            FROM download_credits
            WHERE user_id = ? AND credit_type = 'free_trial'
        """, (user_id,))
        free_trial_stats = cursor.fetchone()
        free_trial_used = free_trial_stats[0] or 0
        free_trial_total = free_trial_stats[1] or 0
        
        # 统计订阅已使用次数
        cursor.execute("""
            SELECT 
                SUM(used_credits) as used,
                SUM(total_credits) as total
            FROM download_credits
            WHERE user_id = ? AND credit_type = 'subscription'
        """, (user_id,))
        subscription_stats = cursor.fetchone()
        subscription_used = subscription_stats[0] or 0
        subscription_total = subscription_stats[1] or 0
        
        # 统计购买次数包已使用次数
        cursor.execute("""
            SELECT 
                SUM(used_credits) as used,
                SUM(total_credits) as total
            FROM download_credits
            WHERE user_id = ? AND credit_type = 'purchase'
        """, (user_id,))
        purchase_stats = cursor.fetchone()
        purchase_used = purchase_stats[0] or 0
        purchase_total = purchase_stats[1] or 0
        
        return {
            "free_trial": {
                "used": free_trial_used,
                "total": free_trial_total
            },
            "subscription": {
                "used": subscription_used,
                "total": subscription_total
            },
            "purchase": {
                "used": purchase_used,
                "total": purchase_total
            }
        }
    except Exception as e:
        print(f"获取已使用次数统计异常: {e}")
        return {
            "free_trial": {"used": 0, "total": 0},
            "subscription": {"used": 0, "total": 0},
            "purchase": {"used": 0, "total": 0}
        }
    finally:
        conn.close()



# ==================== 每日处理次数管理 ====================

def get_user_subscription_type(user_id: str) -> Optional[str]:
    """获取用户当前的订阅类型"""
    if not is_subscription_enabled():
        return None
    
    conn = get_db_connection()
    if not conn:
        return None
    
    try:
        cursor = conn.cursor()
        now = datetime.utcnow().isoformat()
        
        # 查找当前有效的订阅
        cursor.execute("""
            SELECT s.subscription_type
            FROM subscriptions s
            JOIN download_credits dc ON s.id = dc.source_subscription_id
            WHERE s.user_id = ?
            AND s.status = 'active'
            AND dc.credit_type = 'subscription'
            AND dc.remaining_credits > 0
            AND (dc.period_end IS NULL OR dc.period_end > ?)
            ORDER BY s.created_at DESC
            LIMIT 1
        """, (user_id, now))
        
        result = cursor.fetchone()
        if result:
            return result[0]
        
        # 如果没有订阅，检查是否有有效的购买包
        cursor.execute("""
            SELECT dc.credit_type
            FROM download_credits dc
            WHERE dc.user_id = ?
            AND dc.credit_type = 'purchase'
            AND dc.remaining_credits > 0
            AND (dc.period_end IS NULL OR dc.period_end > ?)
            ORDER BY dc.created_at DESC
            LIMIT 1
        """, (user_id, now))
        
        result = cursor.fetchone()
        if result:
            return "purchase"  # 购买包
        
        return None
    except Exception as e:
        print(f"获取用户订阅类型异常: {e}")
        return None
    finally:
        conn.close()


def get_daily_process_limit(user_id: str) -> int:
    """获取用户每日处理次数上限"""
    if not is_subscription_enabled():
        return 999999  # 订阅系统未启用，无限制
    
    # 检查白名单
    if check_whitelist(user_id):
        return 999999  # 白名单用户无限制
    
    subscription_type = get_user_subscription_type(user_id)
    
    # 根据订阅类型返回每日处理次数上限
    if subscription_type == "basic_monthly":
        return 10  # 基础版：10次/天
    elif subscription_type == "premium_monthly":
        return 20  # 高级版：20次/天
    elif subscription_type == "purchase":
        return 10  # 购买包：10次/天
    else:
        # 没有订阅或购买包，检查是否有免费体验次数
        conn = get_db_connection()
        if not conn:
            return 999999
        
        try:
            cursor = conn.cursor()
            # 检查是否还有免费体验次数
            cursor.execute("""
                SELECT COALESCE(SUM(used_credits), 0)
                FROM download_credits
                WHERE user_id = ?
                AND credit_type = 'free_trial'
            """, (user_id,))
            result = cursor.fetchone()
            free_trial_used = result[0] if result and result[0] else 0
            
            if free_trial_used < 5:
                return 999999  # 免费体验期间无限制
            else:
                return 0  # 没有订阅且免费体验已用完，不允许处理
        except Exception as e:
            print(f"检查免费体验次数异常: {e}")
            import traceback
            traceback.print_exc()
            # 异常时：如果订阅系统启用，不允许处理（安全起见）
            return 0
        finally:
            conn.close()


def get_today_process_count(user_id: str) -> int:
    """获取用户今日已处理次数"""
    if not is_subscription_enabled():
        return 0
    
    conn = get_db_connection()
    if not conn:
        return 0
    
    try:
        cursor = conn.cursor()
        today = datetime.utcnow().date().isoformat()
        
        cursor.execute("""
            SELECT COUNT(*)
            FROM process_logs
            WHERE user_id = ?
            AND process_date = ?
        """, (user_id, today))
        
        result = cursor.fetchone()
        return result[0] if result else 0
    except Exception as e:
        print(f"获取今日处理次数异常: {e}")
        return 0
    finally:
        conn.close()


def check_daily_process_limit(user_id: str) -> Dict:
    """检查用户是否超过每日处理次数上限"""
    if not is_subscription_enabled():
        return {
            "allowed": True,
            "limit": 999999,
            "used": 0,
            "remaining": 999999,
            "message": "订阅系统未启用"
        }
    
    # 检查白名单
    if check_whitelist(user_id):
        return {
            "allowed": True,
            "limit": 999999,
            "used": 0,
            "remaining": 999999,
            "message": "白名单用户无限制"
        }
    
    limit = get_daily_process_limit(user_id)
    used = get_today_process_count(user_id)
    remaining = limit - used
    
    if remaining <= 0:
        return {
            "allowed": False,
            "limit": limit,
            "used": used,
            "remaining": 0,
            "message": f"今日处理次数已达上限（{limit}次/天），请明天再试或升级套餐"
        }
    
    return {
        "allowed": True,
        "limit": limit,
        "used": used,
        "remaining": remaining,
        "message": f"今日剩余处理次数：{remaining}/{limit}"
    }


def record_process(user_id: str, task_id: str) -> bool:
    """记录一次处理请求"""
    if not is_subscription_enabled():
        return True
    
    conn = get_db_connection()
    if not conn:
        return True
    
    try:
        cursor = conn.cursor()
        today = datetime.utcnow().date().isoformat()
        
        cursor.execute("""
            INSERT INTO process_logs (user_id, task_id, process_date)
            VALUES (?, ?, ?)
        """, (user_id, task_id, today))
        
        conn.commit()
        return True
    except Exception as e:
        print(f"记录处理次数异常: {e}")
        return False
    finally:
        conn.close()
