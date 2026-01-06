#!/usr/bin/env python3
"""
订阅系统数据库初始化和管理
使用 SQLite 数据库
"""

import sqlite3
import os
from pathlib import Path
from typing import Optional
from datetime import datetime

# 获取数据库路径
def get_db_path() -> Optional[Path]:
    """获取订阅系统数据库路径"""
    db_path = os.getenv("SUBSCRIPTION_DB_PATH")
    if not db_path:
        # 默认路径：项目根目录下的 data 目录
        project_root = Path(__file__).parent.parent.parent
        db_path = project_root / "data" / "subscription.db"
    
    db_path = Path(db_path)
    # 确保目录存在
    db_path.parent.mkdir(parents=True, exist_ok=True)
    return db_path


def init_database():
    """初始化数据库，创建所有表"""
    db_path = get_db_path()
    if not db_path:
        print("WARNING: 订阅系统数据库路径未配置，订阅功能将不可用")
        return False
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    try:
        # 1. 用户表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT UNIQUE NOT NULL,
                device_id TEXT,
                email TEXT,
                phone TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 2. 订阅表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS subscriptions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                subscription_type TEXT NOT NULL,
                status TEXT NOT NULL,
                start_date TIMESTAMP NOT NULL,
                end_date TIMESTAMP,
                auto_renew BOOLEAN DEFAULT 1,
                platform TEXT NOT NULL,
                transaction_id TEXT,
                receipt_data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)
        
        # 3. 下载次数表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS download_credits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                credit_type TEXT NOT NULL,
                total_credits INTEGER NOT NULL,
                used_credits INTEGER DEFAULT 0,
                remaining_credits INTEGER NOT NULL,
                period_start TIMESTAMP,
                period_end TIMESTAMP,
                source_subscription_id INTEGER,
                source_purchase_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id),
                FOREIGN KEY (source_subscription_id) REFERENCES subscriptions(id),
                FOREIGN KEY (source_purchase_id) REFERENCES payment_records(id)
            )
        """)
        
        # 4. 支付记录表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS payment_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                payment_type TEXT NOT NULL,
                product_id TEXT NOT NULL,
                amount DECIMAL(10, 2) NOT NULL,
                currency TEXT DEFAULT 'CNY',
                platform TEXT NOT NULL,
                transaction_id TEXT UNIQUE,
                status TEXT NOT NULL,
                receipt_data TEXT,
                verified BOOLEAN DEFAULT 0,
                verified_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)
        
        # 5. 下载记录表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS download_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                task_id TEXT NOT NULL,
                version TEXT NOT NULL,
                credit_id INTEGER,
                credit_type TEXT,
                ip_address TEXT,
                user_agent TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id),
                FOREIGN KEY (credit_id) REFERENCES download_credits(id)
            )
        """)
        
        # 6. 白名单表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS whitelist (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT UNIQUE NOT NULL,
                added_by TEXT,
                reason TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)
        
        # 7. 处理记录表（用于记录每日处理次数）
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS process_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                task_id TEXT NOT NULL,
                process_date DATE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)
        
        # 创建索引
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_user_id ON users(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_device_id ON users(device_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_subscriptions_user_id ON subscriptions(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_subscriptions_status ON subscriptions(status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_download_credits_user_id ON download_credits(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_download_credits_period ON download_credits(period_start, period_end)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_payment_records_user_id ON payment_records(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_payment_records_transaction_id ON payment_records(transaction_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_payment_records_status ON payment_records(status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_download_logs_user_id ON download_logs(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_download_logs_task_id ON download_logs(task_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_whitelist_user_id ON whitelist(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_process_logs_user_id ON process_logs(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_process_logs_date ON process_logs(process_date)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_process_logs_user_date ON process_logs(user_id, process_date)")
        
        conn.commit()
        print(f"✅ 订阅系统数据库初始化成功: {db_path}")
        return True
        
    except Exception as e:
        conn.rollback()
        print(f"❌ 数据库初始化失败: {e}")
        return False
    finally:
        conn.close()


if __name__ == "__main__":
    # 直接运行此脚本可以初始化数据库
    init_database()


