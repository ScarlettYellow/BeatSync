#!/usr/bin/env python3
"""
测试新增的 API 端点
- 订阅详情查询（完善版）
- 订阅历史查询
- 下载记录查询
- 已使用次数统计
"""

import os
import sys
import requests
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# 设置环境变量
os.environ["SUBSCRIPTION_ENABLED"] = "true"
os.environ["JWT_SECRET_KEY"] = "test-secret-key"

BASE_URL = "http://localhost:8000"

def test_subscription_status_detailed():
    """测试完善的订阅状态查询 API"""
    print("\n" + "="*60)
    print("测试 1: 完善的订阅状态查询 API")
    print("="*60)
    
    # 1. 先注册一个用户
    response = requests.post(f"{BASE_URL}/api/auth/register", json={
        "device_id": "test_device_api_1"
    })
    assert response.status_code == 200, f"注册失败: {response.status_code}"
    data = response.json()
    token = data.get("token")
    user_id = data.get("user_id")
    print(f"✓ 注册用户成功: {user_id}")
    
    # 2. 查询订阅状态
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/subscription/status", headers=headers)
    assert response.status_code == 200, f"查询订阅状态失败: {response.status_code}"
    
    result = response.json()
    print(f"\n订阅状态信息:")
    print(f"  - 白名单: {result.get('is_whitelisted')}")
    print(f"  - 有活跃订阅: {result.get('hasActiveSubscription')}")
    print(f"  - 订阅信息: {result.get('subscription')}")
    print(f"  - 总剩余次数: {result.get('download_credits', {}).get('total', 0)}")
    print(f"  - 免费试用:")
    print(f"     已使用: {result.get('free_trial', {}).get('used', 0)}")
    print(f"     总数: {result.get('free_trial', {}).get('total', 0)}")
    print(f"     剩余: {result.get('free_trial', {}).get('remaining', 0)}")
    
    # 验证响应格式
    assert "hasActiveSubscription" in result, "缺少 hasActiveSubscription 字段"
    assert "free_trial" in result, "缺少 free_trial 字段"
    assert "credits" in result, "缺少 credits 字段"
    print("\n✓ 测试通过：订阅状态查询 API 格式正确")
    
    return token, user_id

def test_subscription_history():
    """测试订阅历史查询 API"""
    print("\n" + "="*60)
    print("测试 2: 订阅历史查询 API")
    print("="*60)
    
    # 注册用户
    response = requests.post(f"{BASE_URL}/api/auth/register", json={
        "device_id": "test_device_api_2"
    })
    token = response.json().get("token")
    headers = {"Authorization": f"Bearer {token}"}
    
    # 查询订阅历史
    response = requests.get(f"{BASE_URL}/api/subscription/history", headers=headers, params={"page": 1, "limit": 10})
    assert response.status_code == 200, f"查询订阅历史失败: {response.status_code}"
    
    result = response.json()
    print(f"\n订阅历史信息:")
    print(f"  - 总数: {result.get('total', 0)}")
    print(f"  - 当前页: {result.get('page', 0)}")
    print(f"  - 每页数量: {result.get('limit', 0)}")
    print(f"  - 订阅记录数: {len(result.get('subscriptions', []))}")
    
    # 验证响应格式
    assert "total" in result, "缺少 total 字段"
    assert "page" in result, "缺少 page 字段"
    assert "limit" in result, "缺少 limit 字段"
    assert "subscriptions" in result, "缺少 subscriptions 字段"
    print("\n✓ 测试通过：订阅历史查询 API 格式正确")
    
    return token

def test_download_history():
    """测试下载记录查询 API"""
    print("\n" + "="*60)
    print("测试 3: 下载记录查询 API")
    print("="*60)
    
    # 注册用户
    response = requests.post(f"{BASE_URL}/api/auth/register", json={
        "device_id": "test_device_api_3"
    })
    token = response.json().get("token")
    user_id = response.json().get("user_id")
    headers = {"Authorization": f"Bearer {token}"}
    
    # 模拟一次下载（消费次数）
    response = requests.post(f"{BASE_URL}/api/credits/consume", 
                            headers=headers,
                            data={"task_id": "test_task_1", "version": "modular"})
    print(f"✓ 模拟消费1次下载")
    
    # 查询下载记录
    response = requests.get(f"{BASE_URL}/api/downloads/history", headers=headers, params={"page": 1, "limit": 10})
    assert response.status_code == 200, f"查询下载记录失败: {response.status_code}"
    
    result = response.json()
    print(f"\n下载记录信息:")
    print(f"  - 总数: {result.get('total', 0)}")
    print(f"  - 当前页: {result.get('page', 0)}")
    print(f"  - 每页数量: {result.get('limit', 0)}")
    print(f"  - 下载记录数: {len(result.get('downloads', []))}")
    
    if result.get('downloads'):
        download = result['downloads'][0]
        print(f"  - 第一条记录:")
        print(f"     任务ID: {download.get('task_id')}")
        print(f"     版本: {download.get('version')}")
        print(f"     次数类型: {download.get('credit_type')}")
    
    # 验证响应格式
    assert "total" in result, "缺少 total 字段"
    assert "page" in result, "缺少 page 字段"
    assert "limit" in result, "缺少 limit 字段"
    assert "downloads" in result, "缺少 downloads 字段"
    print("\n✓ 测试通过：下载记录查询 API 格式正确")
    
    return token

def test_used_credits_stats():
    """测试已使用次数统计"""
    print("\n" + "="*60)
    print("测试 4: 已使用次数统计")
    print("="*60)
    
    # 注册用户
    response = requests.post(f"{BASE_URL}/api/auth/register", json={
        "device_id": "test_device_api_4"
    })
    token = response.json().get("token")
    headers = {"Authorization": f"Bearer {token}"}
    
    # 消费几次下载
    for i in range(3):
        requests.post(f"{BASE_URL}/api/credits/consume", 
                     headers=headers,
                     data={"task_id": f"test_task_{i}", "version": "modular"})
    print(f"✓ 已消费3次下载")
    
    # 查询订阅状态（包含已使用次数统计）
    response = requests.get(f"{BASE_URL}/api/subscription/status", headers=headers)
    result = response.json()
    
    print(f"\n已使用次数统计:")
    free_trial = result.get('free_trial', {})
    print(f"  - 免费试用:")
    print(f"     已使用: {free_trial.get('used', 0)}")
    print(f"     总数: {free_trial.get('total', 0)}")
    print(f"     剩余: {free_trial.get('remaining', 0)}")
    
    credits = result.get('credits', {})
    subscription = credits.get('subscription', {})
    purchase = credits.get('purchase', {})
    print(f"  - 订阅次数:")
    print(f"     已使用: {subscription.get('used', 0)}")
    print(f"     总数: {subscription.get('total', 0)}")
    print(f"     剩余: {subscription.get('remaining', 0)}")
    print(f"  - 购买次数:")
    print(f"     已使用: {purchase.get('used', 0)}")
    print(f"     总数: {purchase.get('total', 0)}")
    print(f"     剩余: {purchase.get('remaining', 0)}")
    
    # 验证统计正确
    assert free_trial.get('used', 0) == 3, f"免费试用已使用次数不正确: {free_trial.get('used')}"
    assert free_trial.get('remaining', 0) == 47, f"免费试用剩余次数不正确: {free_trial.get('remaining')}"
    print("\n✓ 测试通过：已使用次数统计正确")
    
    return token

def main():
    """运行所有测试"""
    print("\n" + "="*60)
    print("新增 API 端点测试")
    print("="*60)
    
    try:
        # 测试完善的订阅状态查询
        token1, user_id1 = test_subscription_status_detailed()
        
        # 测试订阅历史查询
        token2 = test_subscription_history()
        
        # 测试下载记录查询
        token3 = test_download_history()
        
        # 测试已使用次数统计
        token4 = test_used_credits_stats()
        
        print("\n" + "="*60)
        print("所有测试通过！")
        print("="*60)
        
        return 0
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

if __name__ == "__main__":
    exit(main())
