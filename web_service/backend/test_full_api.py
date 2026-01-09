#!/usr/bin/env python3
"""
完整的订阅系统 API 测试（启用订阅系统）
"""

import os
import sys
import requests
import json
import time

# 设置环境变量（在导入模块之前）
os.environ["SUBSCRIPTION_ENABLED"] = "true"
os.environ["ADMIN_TOKEN"] = "test_admin_token_12345"
os.environ["JWT_SECRET_KEY"] = "test_jwt_secret_key_12345"

BASE_URL = "http://localhost:8000"

def print_section(title):
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)

def test_health():
    """测试健康检查"""
    print_section("1. 健康检查")
    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=5)
        print(f"✅ 状态码: {response.status_code}")
        print(f"   响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False

def test_register():
    """测试用户注册"""
    print_section("2. 用户注册")
    try:
        device_id = f"test_device_{int(time.time())}"
        response = requests.post(
            f"{BASE_URL}/api/auth/register",
            data={"device_id": device_id},
            timeout=5
        )
        print(f"   状态码: {response.status_code}")
        data = response.json()
        print(f"   响应: {json.dumps(data, indent=2, ensure_ascii=False)}")
        
        if response.status_code == 200 and "token" in data and "user_id" in data:
            print(f"   ✅ 用户注册成功")
            print(f"   User ID: {data['user_id']}")
            print(f"   Token: {data['token'][:40]}...")
            return data["token"], data["user_id"]
        else:
            print(f"   ❌ 用户注册失败")
            if "error" in data:
                print(f"   错误信息: {data['error']}")
            return None, None
    except Exception as e:
        print(f"   ❌ 异常: {e}")
        return None, None

def test_subscription_status(token):
    """测试订阅状态查询"""
    print_section("3. 订阅状态查询")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(
            f"{BASE_URL}/api/subscription/status",
            headers=headers,
            timeout=5
        )
        print(f"   状态码: {response.status_code}")
        data = response.json()
        print(f"   响应: {json.dumps(data, indent=2, ensure_ascii=False)}")
        
        if response.status_code == 200:
            print(f"   ✅ 订阅状态查询成功")
            if data.get("is_whitelisted"):
                print(f"   ⭐ 用户在白名单中")
            print(f"   剩余下载次数: {data.get('download_credits', {}).get('total', 0)}")
        return response.status_code == 200
    except Exception as e:
        print(f"   ❌ 异常: {e}")
        return False

def test_credits_check(token):
    """测试下载次数检查"""
    print_section("4. 下载次数检查")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(
            f"{BASE_URL}/api/credits/check",
            headers=headers,
            timeout=5
        )
        print(f"   状态码: {response.status_code}")
        data = response.json()
        print(f"   响应: {json.dumps(data, indent=2, ensure_ascii=False)}")
        
        if response.status_code == 200:
            print(f"   ✅ 下载次数检查成功")
            print(f"   可下载: {data.get('can_download', False)}")
            print(f"   剩余次数: {data.get('total_remaining', 0)}")
        return response.status_code == 200
    except Exception as e:
        print(f"   ❌ 异常: {e}")
        return False

def test_whitelist(user_id, admin_token):
    """测试白名单管理"""
    print_section("5. 白名单管理")
    
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    # 添加白名单
    print("\n   5.1 添加用户到白名单")
    try:
        response = requests.post(
            f"{BASE_URL}/api/admin/whitelist/add",
            headers=headers,
            data={"user_id": user_id, "reason": "API测试用户"},
            timeout=5
        )
        print(f"      状态码: {response.status_code}")
        data = response.json()
        print(f"      响应: {json.dumps(data, indent=2, ensure_ascii=False)}")
        add_success = response.status_code in [200, 201]
    except Exception as e:
        print(f"      ❌ 异常: {e}")
        add_success = False
    
    # 检查白名单
    print("\n   5.2 检查用户是否在白名单中")
    try:
        response = requests.get(
            f"{BASE_URL}/api/admin/whitelist/check/{user_id}",
            headers=headers,
            timeout=5
        )
        print(f"      状态码: {response.status_code}")
        data = response.json()
        print(f"      响应: {json.dumps(data, indent=2, ensure_ascii=False)}")
        check_success = response.status_code == 200
    except Exception as e:
        print(f"      ❌ 异常: {e}")
        check_success = False
    
    # 获取白名单列表
    print("\n   5.3 获取白名单列表")
    try:
        response = requests.get(
            f"{BASE_URL}/api/admin/whitelist?page=1&limit=10",
            headers=headers,
            timeout=5
        )
        print(f"      状态码: {response.status_code}")
        data = response.json()
        print(f"      总数: {data.get('total', 0)}")
        print(f"      用户数: {len(data.get('users', []))}")
        list_success = response.status_code == 200
    except Exception as e:
        print(f"      ❌ 异常: {e}")
        list_success = False
    
    # 删除白名单
    print("\n   5.4 删除白名单用户")
    try:
        response = requests.delete(
            f"{BASE_URL}/api/admin/whitelist/{user_id}",
            headers=headers,
            timeout=5
        )
        print(f"      状态码: {response.status_code}")
        data = response.json()
        print(f"      响应: {json.dumps(data, indent=2, ensure_ascii=False)}")
        delete_success = response.status_code == 200
    except Exception as e:
        print(f"      ❌ 异常: {e}")
        delete_success = False
    
    return add_success and check_success and list_success and delete_success

def main():
    """运行所有测试"""
    print("=" * 60)
    print("订阅系统完整 API 测试（启用订阅系统）")
    print("=" * 60)
    print(f"\n测试时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"服务地址: {BASE_URL}")
    print(f"\n⚠️  请确保服务已启动并设置了环境变量：")
    print(f"   SUBSCRIPTION_ENABLED=true")
    print(f"   ADMIN_TOKEN=test_admin_token_12345")
    print(f"   JWT_SECRET_KEY=test_jwt_secret_key_12345")
    
    results = []
    
    # 1. 健康检查
    results.append(("健康检查", test_health()))
    
    # 2. 用户注册
    token, user_id = test_register()
    results.append(("用户注册", token is not None and user_id is not None))
    
    if not token or not user_id:
        print("\n❌ 用户注册失败，无法继续测试")
        print_summary(results)
        return 1
    
    # 3. 订阅状态查询
    results.append(("订阅状态查询", test_subscription_status(token)))
    
    # 4. 下载次数检查
    results.append(("下载次数检查", test_credits_check(token)))
    
    # 5. 白名单管理
    admin_token = os.environ.get("ADMIN_TOKEN", "test_admin_token_12345")
    results.append(("白名单管理", test_whitelist(user_id, admin_token)))
    
    # 汇总结果
    print_summary(results)
    
    return 0 if all(r[1] for r in results) else 1

def print_summary(results):
    """打印测试结果汇总"""
    print_section("测试结果汇总")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{name}: {status}")
    
    print(f"\n总计: {passed}/{total} 通过")
    
    if passed == total:
        print("\n🎉 所有测试通过！")
    else:
        print(f"\n⚠️  有 {total - passed} 个测试失败")

if __name__ == "__main__":
    sys.exit(main())

