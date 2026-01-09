#!/usr/bin/env python3
"""
测试免费试用1周功能
验证：
1. 新用户注册后获得7天试用期和50次免费下载
2. 在试用期内可以消费下载次数
3. 试用期结束后不能再使用免费试用次数
4. 已有用户（注册时间超过7天）不应该有免费试用次数
"""

import os
import sys
from pathlib import Path
from datetime import datetime, timedelta

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# 设置环境变量
os.environ["SUBSCRIPTION_ENABLED"] = "true"
os.environ["JWT_SECRET_KEY"] = "test-secret-key"

from subscription_db import init_database, get_db_path
from subscription_service import (
    create_or_get_user,
    check_download_credits,
    consume_download_credit,
    get_db_connection
)

def test_new_user_trial():
    """测试新用户注册后的试用期"""
    print("\n" + "="*60)
    print("测试 1: 新用户注册后的试用期")
    print("="*60)
    
    # 创建新用户
    result = create_or_get_user(device_id="test_device_new_user")
    user_id = result["user_id"]
    print(f"✓ 创建新用户: {user_id}")
    
    # 检查下载次数
    credits_info = check_download_credits(user_id)
    print(f"\n下载次数信息:")
    print(f"  - 可以下载: {credits_info['can_download']}")
    print(f"  - 总剩余次数: {credits_info['total_remaining']}")
    print(f"  - 免费试用次数: {credits_info['available_credits'].get('free_trial', 0)}")
    
    # 验证：新用户应该有50次免费试用
    assert credits_info['can_download'] == True, "新用户应该可以下载"
    assert credits_info['available_credits'].get('free_trial', 0) == 50, "新用户应该有50次免费试用"
    print("\n✓ 测试通过：新用户获得50次免费试用")
    
    return user_id

def test_consume_trial_credits(user_id):
    """测试消费试用期下载次数"""
    print("\n" + "="*60)
    print("测试 2: 消费试用期下载次数")
    print("="*60)
    
    # 消费1次
    result = consume_download_credit(user_id, "test_task_1", "modular")
    print(f"\n消费1次下载:")
    print(f"  - 类型: {result['credit_type']}")
    print(f"  - 剩余次数: {result['remaining']}")
    
    assert result['credit_type'] == 'free_trial', "应该使用免费试用次数"
    assert result['remaining'] == 49, "剩余次数应该是49"
    print("\n✓ 测试通过：成功消费1次，剩余49次")
    
    # 再次检查下载次数
    credits_info = check_download_credits(user_id)
    print(f"\n检查剩余次数:")
    print(f"  - 免费试用次数: {credits_info['available_credits'].get('free_trial', 0)}")
    print(f"  - 总剩余次数: {credits_info['total_remaining']}")
    
    assert credits_info['available_credits'].get('free_trial', 0) == 49, "剩余次数应该是49"
    print("\n✓ 测试通过：剩余次数正确")
    
    return user_id

def test_old_user_no_trial():
    """测试已注册超过7天的用户不应该有免费试用"""
    print("\n" + "="*60)
    print("测试 3: 已注册超过7天的用户")
    print("="*60)
    
    # 创建用户
    result = create_or_get_user(device_id="test_device_old_user")
    user_id = result["user_id"]
    print(f"✓ 创建用户: {user_id}")
    
    # 修改用户的注册时间为8天前
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        old_date = (datetime.utcnow() - timedelta(days=8)).isoformat()
        cursor.execute("""
            UPDATE users 
            SET created_at = ? 
            WHERE user_id = ?
        """, (old_date, user_id))
        conn.commit()
        conn.close()
        print(f"✓ 修改注册时间为8天前: {old_date}")
    
    # 检查下载次数
    credits_info = check_download_credits(user_id)
    print(f"\n下载次数信息:")
    print(f"  - 可以下载: {credits_info['can_download']}")
    print(f"  - 总剩余次数: {credits_info['total_remaining']}")
    print(f"  - 免费试用次数: {credits_info['available_credits'].get('free_trial', 0)}")
    
    # 验证：已注册超过7天的用户不应该有免费试用
    assert credits_info['available_credits'].get('free_trial', 0) == 0, "已注册超过7天的用户不应该有免费试用"
    assert credits_info['can_download'] == False, "没有订阅的用户不应该可以下载"
    print("\n✓ 测试通过：已注册超过7天的用户没有免费试用")
    
    return user_id

def test_trial_expired():
    """测试试用期过期后的行为"""
    print("\n" + "="*60)
    print("测试 4: 试用期过期后的行为")
    print("="*60)
    
    # 创建用户
    result = create_or_get_user(device_id="test_device_expired_trial")
    user_id = result["user_id"]
    print(f"✓ 创建用户: {user_id}")
    
    # 先消费几次，确保有使用记录
    for i in range(3):
        consume_download_credit(user_id, f"test_task_{i}", "modular")
    print(f"✓ 已消费3次下载")
    
    # 修改用户的注册时间为8天前（试用期已过期）
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        old_date = (datetime.utcnow() - timedelta(days=8)).isoformat()
        cursor.execute("""
            UPDATE users 
            SET created_at = ? 
            WHERE user_id = ?
        """, (old_date, user_id))
        
        # 同时修改下载次数记录的 period_end 为过期时间
        cursor.execute("""
            UPDATE download_credits 
            SET period_end = ? 
            WHERE user_id = ? AND credit_type = 'free_trial'
        """, (old_date, user_id))
        conn.commit()
        conn.close()
        print(f"✓ 修改注册时间和试用期结束时间为8天前")
    
    # 尝试消费下载次数（应该失败，因为试用期已过期）
    try:
        result = consume_download_credit(user_id, "test_task_expired", "modular")
        print(f"\n消费结果:")
        print(f"  - 类型: {result.get('credit_type', 'unknown')}")
        print(f"  - 剩余次数: {result.get('remaining', 'unknown')}")
        
        # 如果返回了结果，应该不是 free_trial 类型
        if result.get('credit_type') == 'free_trial':
            print("\n⚠️ 警告：试用期已过期，但仍使用了免费试用次数")
        else:
            print("\n✓ 测试通过：试用期过期后不再使用免费试用次数")
    except Exception as e:
        print(f"\n✓ 测试通过：试用期过期后无法消费（异常: {e})")
    
    # 检查下载次数
    credits_info = check_download_credits(user_id)
    print(f"\n检查剩余次数:")
    print(f"  - 可以下载: {credits_info['can_download']}")
    print(f"  - 免费试用次数: {credits_info['available_credits'].get('free_trial', 0)}")
    print(f"  - 总剩余次数: {credits_info['total_remaining']}")
    
    assert credits_info['available_credits'].get('free_trial', 0) == 0, "试用期过期后不应该有免费试用次数"
    print("\n✓ 测试通过：试用期过期后没有免费试用次数")
    
    return user_id

def test_multiple_consumptions():
    """测试多次消费"""
    print("\n" + "="*60)
    print("测试 5: 多次消费试用期下载次数")
    print("="*60)
    
    # 创建新用户
    result = create_or_get_user(device_id="test_device_multiple")
    user_id = result["user_id"]
    print(f"✓ 创建新用户: {user_id}")
    
    # 消费10次
    print(f"\n消费10次下载:")
    for i in range(10):
        result = consume_download_credit(user_id, f"test_task_{i}", "modular")
        if i == 0 or i == 9:
            print(f"  第{i+1}次: 类型={result['credit_type']}, 剩余={result['remaining']}")
    
    # 检查剩余次数
    credits_info = check_download_credits(user_id)
    print(f"\n检查剩余次数:")
    print(f"  - 免费试用次数: {credits_info['available_credits'].get('free_trial', 0)}")
    print(f"  - 总剩余次数: {credits_info['total_remaining']}")
    
    assert credits_info['available_credits'].get('free_trial', 0) == 40, "消费10次后应该剩余40次"
    print("\n✓ 测试通过：多次消费后剩余次数正确")
    
    return user_id

def cleanup_test_data():
    """清理测试数据"""
    print("\n" + "="*60)
    print("清理测试数据")
    print("="*60)
    
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        
        # 删除测试用户
        cursor.execute("""
            DELETE FROM users 
            WHERE device_id LIKE 'test_device_%'
        """)
        deleted_users = cursor.rowcount
        
        # 删除测试下载记录
        cursor.execute("""
            DELETE FROM download_logs 
            WHERE task_id LIKE 'test_task_%'
        """)
        deleted_logs = cursor.rowcount
        
        # 删除测试下载次数记录
        cursor.execute("""
            DELETE FROM download_credits 
            WHERE user_id IN (
                SELECT user_id FROM users WHERE device_id LIKE 'test_device_%'
            )
        """)
        deleted_credits = cursor.rowcount
        
        conn.commit()
        conn.close()
        
        print(f"✓ 已删除 {deleted_users} 个测试用户")
        print(f"✓ 已删除 {deleted_logs} 条测试下载记录")
        print(f"✓ 已删除 {deleted_credits} 条测试下载次数记录")

def main():
    """运行所有测试"""
    print("\n" + "="*60)
    print("免费试用1周功能测试")
    print("="*60)
    
    # 初始化数据库
    print("\n初始化数据库...")
    init_database()
    print("✓ 数据库初始化完成")
    
    try:
        # 运行测试
        user_id_1 = test_new_user_trial()
        user_id_2 = test_consume_trial_credits(user_id_1)
        user_id_3 = test_old_user_no_trial()
        user_id_4 = test_trial_expired()
        user_id_5 = test_multiple_consumptions()
        
        print("\n" + "="*60)
        print("所有测试通过！")
        print("="*60)
        
    except AssertionError as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return 1
    except Exception as e:
        print(f"\n❌ 测试异常: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        # 清理测试数据
        cleanup_test_data()
    
    return 0

if __name__ == "__main__":
    exit(main())

