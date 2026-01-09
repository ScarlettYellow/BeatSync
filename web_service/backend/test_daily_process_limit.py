#!/usr/bin/env python3
"""
测试每日处理次数上限功能

测试场景：
1. 创建测试用户
2. 模拟购买基础版订阅
3. 连续提交处理请求
4. 验证每日处理次数上限检查
"""

import sys
import os
import requests
import time
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# 导入订阅系统模块
from subscription_db import init_database, get_db_path
from subscription_service import (
    create_or_get_user,
    verify_jwt_token,
    check_daily_process_limit,
    record_process,
    get_user_subscription_type,
    get_daily_process_limit,
    get_today_process_count
)

# API 地址
API_BASE_URL = "http://localhost:8000"

def print_section(title):
    """打印分节标题"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)

def test_database_setup():
    """测试数据库设置"""
    print_section("1. 测试数据库设置")
    
    # 初始化数据库
    result = init_database()
    if result:
        print("✅ 数据库初始化成功")
        db_path = get_db_path()
        print(f"   数据库路径: {db_path}")
        
        # 检查 process_logs 表是否存在
        import sqlite3
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='process_logs'
        """)
        table_exists = cursor.fetchone()
        conn.close()
        
        if table_exists:
            print("✅ process_logs 表已存在")
        else:
            print("❌ process_logs 表不存在，需要重新初始化数据库")
            return False
    else:
        print("❌ 数据库初始化失败")
        return False
    
    return True

def test_create_user():
    """测试创建用户"""
    print_section("2. 创建测试用户")
    
    result = create_or_get_user(device_id="test_device_daily_limit")
    user_id = result.get("user_id")
    token = result.get("token")
    
    if user_id and token:
        print(f"✅ 用户创建成功")
        print(f"   User ID: {user_id}")
        print(f"   Token: {token[:20]}...")
        return user_id, token
    else:
        print("❌ 用户创建失败")
        return None, None

def test_simulate_subscription(user_id):
    """模拟购买基础版订阅"""
    print_section("3. 模拟购买基础版订阅")
    
    import sqlite3
    from datetime import datetime, timedelta
    from subscription_db import get_db_path
    
    db_path = get_db_path()
    if not db_path:
        print("❌ 数据库路径未找到")
        return False
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    try:
        # 创建订阅记录
        now = datetime.utcnow()
        end_date = now + timedelta(days=30)
        
        cursor.execute("""
            INSERT INTO subscriptions (
                user_id, subscription_type, status, start_date, end_date,
                platform, transaction_id, receipt_data
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id,
            "basic_monthly",
            "active",
            now.isoformat(),
            end_date.isoformat(),
            "test",
            "test_transaction_123",
            "{}"
        ))
        subscription_id = cursor.lastrowid
        
        # 创建下载次数记录
        cursor.execute("""
            INSERT INTO download_credits (
                user_id, credit_type, total_credits, used_credits, remaining_credits,
                period_start, period_end, source_subscription_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id,
            "subscription",
            20,  # 基础版：20次/月
            0,
            20,
            now.isoformat(),
            end_date.isoformat(),
            subscription_id
        ))
        
        conn.commit()
        print("✅ 基础版订阅创建成功")
        print(f"   订阅ID: {subscription_id}")
        print(f"   下载次数: 20次/月")
        print(f"   每日处理上限: 10次/天")
        return True
    except Exception as e:
        print(f"❌ 创建订阅失败: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def test_daily_limit_check(user_id):
    """测试每日处理次数上限检查"""
    print_section("4. 测试每日处理次数上限检查")
    
    # 检查订阅类型
    subscription_type = get_user_subscription_type(user_id)
    print(f"   订阅类型: {subscription_type}")
    
    # 获取每日处理上限
    limit = get_daily_process_limit(user_id)
    print(f"   每日处理上限: {limit}次/天")
    
    # 获取今日已处理次数
    used = get_today_process_count(user_id)
    print(f"   今日已处理次数: {used}次")
    
    # 检查是否超过上限
    check_result = check_daily_process_limit(user_id)
    print(f"   检查结果: {check_result}")
    
    if check_result.get("allowed"):
        print(f"✅ 允许处理")
        print(f"   剩余次数: {check_result.get('remaining')}次")
    else:
        print(f"❌ 不允许处理")
        print(f"   原因: {check_result.get('message')}")
    
    return check_result

def test_record_process(user_id):
    """测试记录处理请求"""
    print_section("5. 测试记录处理请求")
    
    task_id = f"test_task_{int(time.time())}"
    result = record_process(user_id, task_id)
    
    if result:
        print(f"✅ 处理请求记录成功")
        print(f"   Task ID: {task_id}")
        
        # 验证记录
        used = get_today_process_count(user_id)
        print(f"   今日已处理次数: {used}次")
    else:
        print("❌ 处理请求记录失败")
    
    return result

def test_limit_enforcement(user_id):
    """测试每日处理次数上限强制执行"""
    print_section("6. 测试每日处理次数上限强制执行")
    
    print("   模拟连续提交处理请求...")
    
    # 先记录10次（达到基础版上限）
    for i in range(10):
        task_id = f"test_task_limit_{int(time.time())}_{i}"
        record_process(user_id, task_id)
        time.sleep(0.1)  # 避免时间戳重复
    
    # 检查当前状态
    check_result = check_daily_process_limit(user_id)
    print(f"   当前状态: {check_result}")
    
    # 尝试第11次
    print("\n   尝试第11次处理请求...")
    check_result_11 = check_daily_process_limit(user_id)
    
    if not check_result_11.get("allowed"):
        print(f"✅ 第11次被正确拒绝")
        print(f"   错误信息: {check_result_11.get('message')}")
        return True
    else:
        print(f"❌ 第11次未被拒绝（应该被拒绝）")
        return False

def test_api_integration(token):
    """测试 API 集成"""
    print_section("7. 测试 API 集成")
    
    # 检查服务是否运行
    try:
        response = requests.get(f"{API_BASE_URL}/api/health", timeout=5)
        if response.status_code == 200:
            print("✅ 后端服务正在运行")
        else:
            print(f"⚠️  后端服务响应异常: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到后端服务")
        print(f"   请确保服务正在运行: {API_BASE_URL}")
        return False
    except Exception as e:
        print(f"❌ 检查服务状态失败: {e}")
        return False
    
    # 测试处理请求（需要先上传文件）
    print("\n   注意：完整的 API 测试需要先上传文件")
    print("   这里只测试每日处理次数上限检查逻辑")
    
    return True

def cleanup_test_data(user_id):
    """清理测试数据"""
    print_section("清理测试数据")
    
    import sqlite3
    from subscription_db import get_db_path
    
    db_path = get_db_path()
    if not db_path:
        return
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    try:
        # 删除处理记录
        cursor.execute("DELETE FROM process_logs WHERE user_id = ?", (user_id,))
        
        # 删除下载次数记录
        cursor.execute("DELETE FROM download_credits WHERE user_id = ?", (user_id,))
        
        # 删除订阅记录
        cursor.execute("DELETE FROM subscriptions WHERE user_id = ?", (user_id,))
        
        # 删除用户
        cursor.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
        
        conn.commit()
        print("✅ 测试数据已清理")
    except Exception as e:
        print(f"⚠️  清理测试数据失败: {e}")
        conn.rollback()
    finally:
        conn.close()

def main():
    """主测试函数"""
    print("\n" + "=" * 60)
    print("  每日处理次数上限功能测试")
    print("=" * 60)
    
    # 1. 测试数据库设置
    if not test_database_setup():
        print("\n❌ 数据库设置失败，测试终止")
        return
    
    # 2. 创建测试用户
    user_id, token = test_create_user()
    if not user_id:
        print("\n❌ 用户创建失败，测试终止")
        return
    
    try:
        # 3. 模拟购买订阅
        if not test_simulate_subscription(user_id):
            print("\n❌ 订阅创建失败，测试终止")
            return
        
        # 4. 测试每日处理次数上限检查
        test_daily_limit_check(user_id)
        
        # 5. 测试记录处理请求
        test_record_process(user_id)
        
        # 6. 测试上限强制执行
        test_limit_enforcement(user_id)
        
        # 7. 测试 API 集成
        test_api_integration(token)
        
        print_section("测试总结")
        print("✅ 所有测试完成")
        print("\n提示：")
        print("  - 每日处理次数在每天 00:00 自动重置")
        print("  - 基础版：10次/天")
        print("  - 高级版：20次/天")
        print("  - 购买包：10次/天")
        
    finally:
        # 清理测试数据
        cleanup_test_data(user_id)

if __name__ == "__main__":
    main()
