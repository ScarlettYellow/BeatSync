#!/usr/bin/env python3
"""
启用订阅系统后的完整 API 测试
"""

import os
import sys
import requests
import json
import time
from pathlib import Path

# 设置环境变量
os.environ["SUBSCRIPTION_ENABLED"] = "true"
os.environ["ADMIN_TOKEN"] = "test_admin_token_12345"
os.environ["JWT_SECRET_KEY"] = "test_jwt_secret_key_12345"

BASE_URL = "http://localhost:8000"

def test_health():
    """测试健康检查"""
    print("1. 测试健康检查接口...")
    response = requests.get(f"{BASE_URL}/api/health")
    print(f"   状态码: {response.status_code}")
    print(f"   响应: {response.json()}")
    print()

def test_register():
    """测试用户注册"""
    print("2. 测试用户注册...")
    device_id = f"test_device_{int(time.time())}"
    response = requests.post(
        f"{BASE_URL}/api/auth/register",
        data={"device_id": device_id}
    )
    print(f"   状态码: {response.status_code}")
    data = response.json()
    print(f"   响应: {json.dumps(data, indent=2, ensure_ascii=False)}")
    
    if "token" in data and "user_id" in data:
        print(f"   ✅ 用户注册成功")
        print(f"   User ID: {data['user_id']}")
        print(f"   Token: {data['token'][:30]}...")
        return data["token"], data["user_id"]
    else:
        print(f"   ❌ 用户注册失败")
        return None, None

def test_subscription_status(token):
    """测试订阅状态查询"""
    print("\n3. 测试订阅状态查询...")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/subscription/status", headers=headers)
    print(f"   状态码: {response.status_code}")
    data = response.json()
    print(f"   响应: {json.dumps(data, indent=2, ensure_ascii=False)}")
    print()

def test_credits_check(token):
    """测试下载次数检查"""
    print("4. 测试下载次数检查...")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/credits/check", headers=headers)
    print(f"   状态码: {response.status_code}")
    data = response.json()
    print(f"   响应: {json.dumps(data, indent=2, ensure_ascii=False)}")
    print()

def test_whitelist(user_id, admin_token):
    """测试白名单管理"""
    print("5. 测试白名单管理...")
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    # 添加白名单
    print("   5.1 添加用户到白名单...")
    response = requests.post(
        f"{BASE_URL}/api/admin/whitelist/add",
        headers=headers,
        data={"user_id": user_id, "reason": "API测试用户"}
    )
    print(f"      状态码: {response.status_code}")
    print(f"      响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    
    # 检查白名单
    print("\n   5.2 检查用户是否在白名单中...")
    response = requests.get(
        f"{BASE_URL}/api/admin/whitelist/check/{user_id}",
        headers=headers
    )
    print(f"      状态码: {response.status_code}")
    print(f"      响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    
    # 获取白名单列表
    print("\n   5.3 获取白名单列表...")
    response = requests.get(
        f"{BASE_URL}/api/admin/whitelist?page=1&limit=10",
        headers=headers
    )
    print(f"      状态码: {response.status_code}")
    data = response.json()
    print(f"      总数: {data.get('total', 0)}")
    print(f"      用户数: {len(data.get('users', []))}")
    
    # 删除白名单
    print("\n   5.4 删除白名单用户...")
    response = requests.delete(
        f"{BASE_URL}/api/admin/whitelist/{user_id}",
        headers=headers
    )
    print(f"      状态码: {response.status_code}")
    print(f"      响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    print()

def main():
    """运行所有测试"""
    print("=" * 60)
    print("订阅系统 API 完整测试（启用订阅系统）")
    print("=" * 60)
    print()
    
    # 检查服务是否运行
    try:
        test_health()
    except Exception as e:
        print(f"❌ 无法连接到服务: {e}")
        print("请先启动服务: cd web_service/backend && python3 main.py")
        return 1
    
    # 测试用户注册
    token, user_id = test_register()
    if not token or not user_id:
        print("❌ 用户注册失败，无法继续测试")
        return 1
    
    # 测试订阅状态
    test_subscription_status(token)
    
    # 测试下载次数检查
    test_credits_check(token)
    
    # 测试白名单管理
    admin_token = os.environ.get("ADMIN_TOKEN", "test_admin_token_12345")
    test_whitelist(user_id, admin_token)
    
    print("=" * 60)
    print("✅ 所有测试完成")
    print("=" * 60)
    return 0

if __name__ == "__main__":
    sys.exit(main())

