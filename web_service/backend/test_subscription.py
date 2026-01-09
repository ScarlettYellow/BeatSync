#!/usr/bin/env python3
"""
订阅系统测试脚本
用于验证基础功能是否正常工作
"""

import sys
import os
from pathlib import Path

# 添加当前目录到路径（确保可以导入同目录的模块）
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

def test_database_init():
    """测试数据库初始化"""
    print("测试1: 数据库初始化...")
    try:
        from subscription_db import init_database
        result = init_database()
        if result:
            print("✅ 数据库初始化成功")
            return True
        else:
            print("❌ 数据库初始化失败")
            return False
    except Exception as e:
        print(f"❌ 数据库初始化异常: {e}")
        return False

def test_user_creation():
    """测试用户创建"""
    print("\n测试2: 用户创建...")
    try:
        from subscription_service import create_or_get_user, is_subscription_enabled
        
        if not is_subscription_enabled():
            print("⚠️  订阅系统未启用，跳过测试")
            return True
        
        result = create_or_get_user(device_id="test_device_123")
        if result.get("user_id") and result.get("token"):
            print(f"✅ 用户创建成功: {result['user_id']}")
            return result
        else:
            print("❌ 用户创建失败")
            return None
    except Exception as e:
        print(f"❌ 用户创建异常: {e}")
        return None

def test_whitelist():
    """测试白名单功能"""
    print("\n测试3: 白名单功能...")
    try:
        from subscription_service import (
            is_subscription_enabled,
            add_to_whitelist,
            check_whitelist,
            remove_from_whitelist,
            create_or_get_user
        )
        
        if not is_subscription_enabled():
            print("⚠️  订阅系统未启用，跳过测试")
            return True
        
        # 创建测试用户
        user_result = create_or_get_user(device_id="test_whitelist_device")
        user_id = user_result.get("user_id")
        
        if not user_id:
            print("❌ 无法创建测试用户")
            return False
        
        # 测试添加白名单
        if add_to_whitelist(user_id, "test", "测试用户"):
            print(f"✅ 用户已添加到白名单: {user_id}")
        else:
            print(f"⚠️  用户可能已在白名单中: {user_id}")
        
        # 测试检查白名单
        if check_whitelist(user_id):
            print(f"✅ 白名单检查成功: {user_id}")
        else:
            print(f"❌ 白名单检查失败: {user_id}")
            return False
        
        # 测试删除白名单
        if remove_from_whitelist(user_id):
            print(f"✅ 用户已从白名单删除: {user_id}")
        else:
            print(f"❌ 删除白名单失败: {user_id}")
            return False
        
        # 再次检查（应该不在白名单中）
        if not check_whitelist(user_id):
            print(f"✅ 删除后检查成功: {user_id}")
        else:
            print(f"❌ 删除后检查失败: {user_id}")
            return False
        
        return True
    except Exception as e:
        print(f"❌ 白名单测试异常: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_download_credits():
    """测试下载次数检查"""
    print("\n测试4: 下载次数检查...")
    try:
        from subscription_service import (
            is_subscription_enabled,
            check_download_credits,
            create_or_get_user
        )
        
        if not is_subscription_enabled():
            print("⚠️  订阅系统未启用，跳过测试")
            return True
        
        # 创建测试用户
        user_result = create_or_get_user(device_id="test_credits_device")
        user_id = user_result.get("user_id")
        
        if not user_id:
            print("❌ 无法创建测试用户")
            return False
        
        # 检查下载次数
        credits_info = check_download_credits(user_id)
        print(f"✅ 下载次数检查成功:")
        print(f"   - 白名单: {credits_info.get('is_whitelisted', False)}")
        print(f"   - 可下载: {credits_info.get('can_download', False)}")
        print(f"   - 剩余次数: {credits_info.get('total_remaining', 0)}")
        
        return True
    except Exception as e:
        print(f"❌ 下载次数检查异常: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """运行所有测试"""
    print("=" * 50)
    print("订阅系统基础功能测试")
    print("=" * 50)
    
    results = []
    
    # 测试1: 数据库初始化
    results.append(("数据库初始化", test_database_init()))
    
    # 测试2: 用户创建
    user_result = test_user_creation()
    results.append(("用户创建", user_result is not None))
    
    # 测试3: 白名单功能
    results.append(("白名单功能", test_whitelist()))
    
    # 测试4: 下载次数检查
    results.append(("下载次数检查", test_download_credits()))
    
    # 汇总结果
    print("\n" + "=" * 50)
    print("测试结果汇总")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{name}: {status}")
        if result:
            passed += 1
    
    print(f"\n总计: {passed}/{total} 通过")
    
    if passed == total:
        print("\n🎉 所有测试通过！")
        return 0
    else:
        print(f"\n⚠️  有 {total - passed} 个测试失败")
        return 1

if __name__ == "__main__":
    sys.exit(main())


