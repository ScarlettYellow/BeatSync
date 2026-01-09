#!/usr/bin/env python3
"""
测试新的免费体验逻辑（前5次处理免费）

测试场景：
1. 创建新用户
2. 验证前5次可以免费处理
3. 验证第6次需要订阅
"""

import sys
import os
import time
from pathlib import Path
from datetime import datetime

# 设置环境变量：启用订阅系统
os.environ["SUBSCRIPTION_ENABLED"] = "true"

# 添加项目路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# 导入订阅系统模块
from subscription_db import init_database, get_db_path
from subscription_service import (
    create_or_get_user,
    check_download_credits,
    consume_download_credit,
    get_daily_process_limit,
    check_daily_process_limit
)

def print_section(title):
    """打印分节标题"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)

def test_new_user_free_trial():
    """测试新用户免费体验"""
    print_section("1. 测试新用户免费体验（前5次处理免费）")
    
    # 初始化数据库
    init_database()
    
    # 创建新用户
    result = create_or_get_user(device_id="test_device_free_trial_new")
    user_id = result.get("user_id")
    token = result.get("token")
    
    print(f"✅ 用户创建成功")
    print(f"   User ID: {user_id}")
    
    # 检查下载次数
    credits_info = check_download_credits(user_id)
    print(f"\n   下载次数信息: {credits_info}")
    
    free_trial_credits = credits_info.get("available_credits", {}).get("free_trial", 0)
    print(f"   免费体验次数: {free_trial_credits}次")
    
    # 检查每日处理次数上限
    process_limit = get_daily_process_limit(user_id)
    print(f"   每日处理次数上限: {process_limit}次/天（免费体验期间无限制）")
    
    if free_trial_credits == 5:
        print("✅ 新用户有5次免费体验")
    else:
        print(f"⚠️  新用户免费体验次数异常: {free_trial_credits}（应该是5次）")
    
    return user_id

def test_consume_free_trial(user_id):
    """测试消费免费体验次数"""
    print_section("2. 测试消费免费体验次数")
    
    # 消费5次免费体验
    for i in range(5):
        task_id = f"test_task_free_{int(time.time())}_{i}"
        version = "modular"
        
        result = consume_download_credit(user_id, task_id, version)
        credit_type = result.get("credit_type")
        remaining = result.get("remaining", 0)
        
        print(f"   第 {i+1} 次下载:")
        print(f"     类型: {credit_type}")
        print(f"     剩余: {remaining}次")
        
        if credit_type == "free_trial":
            print(f"     ✅ 使用免费体验次数")
        else:
            print(f"     ⚠️  未使用免费体验次数")
        
        time.sleep(0.1)
    
    # 检查剩余次数
    credits_info = check_download_credits(user_id)
    free_trial_credits = credits_info.get("available_credits", {}).get("free_trial", 0)
    
    print(f"\n   剩余免费体验次数: {free_trial_credits}次")
    
    if free_trial_credits == 0:
        print("✅ 免费体验次数已用完")
    else:
        print(f"⚠️  免费体验次数未用完: {free_trial_credits}（应该是0）")
    
    return free_trial_credits == 0

def test_after_free_trial(user_id):
    """测试免费体验用完后"""
    print_section("3. 测试免费体验用完后")
    
    # 检查下载次数
    credits_info = check_download_credits(user_id)
    print(f"   下载次数信息: {credits_info}")
    
    can_download = credits_info.get("can_download", False)
    print(f"   是否可以下载: {can_download}")
    
    # 检查每日处理次数上限
    process_limit = get_daily_process_limit(user_id)
    print(f"   每日处理次数上限: {process_limit}次/天")
    
    if not can_download:
        print("✅ 免费体验用完后，无法下载（需要订阅）")
    else:
        print("⚠️  免费体验用完后，仍然可以下载（应该需要订阅）")
    
    if process_limit == 0:
        print("✅ 免费体验用完后，每日处理次数上限为0（需要订阅）")
    else:
        print(f"⚠️  免费体验用完后，每日处理次数上限异常: {process_limit}（应该是0）")
    
    return not can_download and process_limit == 0

def cleanup_test_data(user_id):
    """清理测试数据"""
    import sqlite3
    from subscription_db import get_db_path
    
    db_path = get_db_path()
    if not db_path:
        return
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    try:
        cursor.execute("DELETE FROM download_logs WHERE user_id = ?", (user_id,))
        cursor.execute("DELETE FROM download_credits WHERE user_id = ?", (user_id,))
        cursor.execute("DELETE FROM process_logs WHERE user_id = ?", (user_id,))
        cursor.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
        conn.commit()
        print("✅ 测试数据已清理")
    except Exception as e:
        print(f"⚠️  清理测试数据失败: {e}")
    finally:
        conn.close()

def main():
    """主测试函数"""
    print("\n" + "=" * 60)
    print("  免费体验功能测试（前5次处理免费）")
    print("=" * 60)
    
    # 初始化数据库
    init_database()
    
    # 创建测试用户
    user_id = test_new_user_free_trial()
    
    try:
        # 测试消费免费体验
        free_trial_consumed = test_consume_free_trial(user_id)
        
        # 测试免费体验用完后
        after_free_trial = test_after_free_trial(user_id)
        
        print_section("测试总结")
        if free_trial_consumed and after_free_trial:
            print("✅ 所有测试通过")
        else:
            print("⚠️  部分测试未通过，请检查")
        
    finally:
        # 清理测试数据
        cleanup_test_data(user_id)

if __name__ == "__main__":
    main()
