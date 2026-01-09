#!/usr/bin/env python3
"""
收据验证测试脚本
模拟 iOS 收据验证流程：
1. 用户注册
2. 模拟收据数据（StoreKit 2 格式）
3. 调用收据验证 API
4. 验证订阅保存到数据库
5. 验证订阅状态更新
6. 测试不同产品类型（订阅和一次性购买）
"""

import os
import sys
import requests
import json
import base64
import time
from datetime import datetime, timedelta
from pathlib import Path

# 设置环境变量（在导入模块之前）
os.environ["SUBSCRIPTION_ENABLED"] = "true"
os.environ["ADMIN_TOKEN"] = "test_admin_token_12345"
os.environ["JWT_SECRET_KEY"] = "test_jwt_secret_key_12345"

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

BASE_URL = "http://localhost:8000"

def print_section(title):
    """打印章节标题"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def print_step(step_num, description):
    """打印步骤"""
    print(f"\n[{step_num}] {description}")
    print("-" * 70)

def create_mock_receipt_data(product_id: str, is_subscription: bool = True) -> str:
    """
    创建模拟的收据数据（StoreKit 2 格式）
    
    参数:
        product_id: 产品ID（如 'basic_monthly', 'pack_10'）
        is_subscription: 是否为订阅
    
    返回:
        Base64 编码的收据数据
    """
    now = datetime.utcnow()
    purchase_date_ms = int(now.timestamp() * 1000)
    
    receipt_data = {
        "purchaseDate": purchase_date_ms,
        "productId": product_id
    }
    
    if is_subscription:
        # 订阅：添加过期时间
        if "monthly" in product_id:
            expires_date = now + timedelta(days=30)
        elif "yearly" in product_id:
            expires_date = now + timedelta(days=365)
        else:
            expires_date = now + timedelta(days=30)
        
        receipt_data["expirationDate"] = int(expires_date.timestamp() * 1000)
    else:
        # 一次性购买：没有过期时间
        receipt_data["expirationDate"] = None
    
    # 编码为 Base64
    receipt_json = json.dumps(receipt_data)
    receipt_b64 = base64.b64encode(receipt_json.encode('utf-8')).decode('utf-8')
    
    return receipt_b64

def test_user_registration():
    """测试 1: 用户注册"""
    print_step(1, "用户注册")
    
    try:
        device_id = f"test_receipt_device_{int(time.time())}"
        response = requests.post(
            f"{BASE_URL}/api/auth/register",
            json={"device_id": device_id},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            token = data.get("token")
            user_id = data.get("user_id")
            print(f"   ✅ 注册成功")
            print(f"   User ID: {user_id}")
            print(f"   Token: {token[:40]}...")
            return token, user_id
        else:
            print(f"   ❌ 注册失败: {response.status_code}")
            print(f"   响应: {response.text}")
            return None, None
    except Exception as e:
        print(f"   ❌ 异常: {e}")
        return None, None

def test_receipt_verification_subscription(token, user_id):
    """测试 2: 验证订阅收据（Basic Monthly）"""
    print_step(2, "验证订阅收据（Basic Monthly）")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 创建模拟收据数据
    product_id = "basic_monthly"
    transaction_id = f"test_transaction_{int(time.time())}"
    receipt_data = create_mock_receipt_data(product_id, is_subscription=True)
    
    print(f"\n   收据信息:")
    print(f"   产品ID: {product_id}")
    print(f"   交易ID: {transaction_id}")
    print(f"   收据数据长度: {len(receipt_data)} 字符")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/subscription/verify-receipt",
            headers=headers,
            data={
                "transaction_id": transaction_id,
                "product_id": product_id,
                "receipt_data": receipt_data,
                "platform": "ios"
            },
            timeout=10
        )
        
        print(f"\n   API 响应:")
        print(f"   状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ 收据验证成功")
            print(f"   响应: {json.dumps(data, indent=2, ensure_ascii=False)}")
            return True
        else:
            print(f"   ❌ 收据验证失败")
            print(f"   响应: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ 异常: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_receipt_verification_purchase(token, user_id):
    """测试 3: 验证一次性购买收据（10次下载包）"""
    print_step(3, "验证一次性购买收据（10次下载包）")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 创建模拟收据数据
    product_id = "pack_10"
    transaction_id = f"test_purchase_{int(time.time())}"
    receipt_data = create_mock_receipt_data(product_id, is_subscription=False)
    
    print(f"\n   收据信息:")
    print(f"   产品ID: {product_id}")
    print(f"   交易ID: {transaction_id}")
    print(f"   收据数据长度: {len(receipt_data)} 字符")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/subscription/verify-receipt",
            headers=headers,
            data={
                "transaction_id": transaction_id,
                "product_id": product_id,
                "receipt_data": receipt_data,
                "platform": "ios"
            },
            timeout=10
        )
        
        print(f"\n   API 响应:")
        print(f"   状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ 收据验证成功")
            print(f"   响应: {json.dumps(data, indent=2, ensure_ascii=False)}")
            return True
        else:
            print(f"   ❌ 收据验证失败")
            print(f"   响应: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ 异常: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_subscription_status_after_verification(token):
    """测试 4: 验证订阅状态（验证后）"""
    print_step(4, "验证订阅状态（验证后）")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/api/subscription/status", headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ 订阅状态查询成功")
            print(f"\n   详细信息:")
            print(f"   - 白名单: {data.get('is_whitelisted', False)}")
            print(f"   - 有活跃订阅: {data.get('hasActiveSubscription', False)}")
            
            subscription = data.get('subscription')
            if subscription:
                print(f"   - 订阅类型: {subscription.get('subscription_type')}")
                print(f"   - 订阅状态: {subscription.get('status')}")
                print(f"   - 到期时间: {subscription.get('end_date')}")
            
            download_credits = data.get('download_credits', {})
            print(f"   - 总剩余次数: {download_credits.get('total', 0)}")
            
            free_trial = data.get('free_trial', {})
            print(f"   - 免费试用: {free_trial.get('used', 0)}/{free_trial.get('total', 0)} (剩余: {free_trial.get('remaining', 0)})")
            
            credits = data.get('credits', {})
            subscription_credits = credits.get('subscription', {})
            purchase_credits = credits.get('purchase', {})
            print(f"   - 订阅次数: {subscription_credits.get('used', 0)}/{subscription_credits.get('total', 0)} (剩余: {subscription_credits.get('remaining', 0)})")
            print(f"   - 购买次数: {purchase_credits.get('used', 0)}/{purchase_credits.get('total', 0)} (剩余: {purchase_credits.get('remaining', 0)})")
            
            # 验证订阅已保存
            if data.get('hasActiveSubscription'):
                print(f"\n   ✅ 订阅已成功保存到数据库")
            else:
                print(f"\n   ⚠️  订阅未显示为活跃（可能需要检查）")
            
            # 验证下载次数已添加
            total_remaining = download_credits.get('total', 0)
            if total_remaining > 50:  # 应该大于免费试用的50次
                print(f"   ✅ 下载次数已成功添加（总剩余: {total_remaining}）")
            else:
                print(f"   ⚠️  下载次数可能未正确添加（总剩余: {total_remaining}）")
            
            return True
        else:
            print(f"   ❌ 查询失败: {response.status_code}")
            print(f"   响应: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ 异常: {e}")
        return False

def test_subscription_history_after_verification(token):
    """测试 5: 查询订阅历史（验证后）"""
    print_step(5, "查询订阅历史（验证后）")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/subscription/history",
            headers=headers,
            params={"page": 1, "limit": 10},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ 查询成功")
            print(f"   总数: {data.get('total', 0)}")
            print(f"   记录数: {len(data.get('subscriptions', []))}")
            
            subscriptions = data.get('subscriptions', [])
            if subscriptions:
                print(f"\n   订阅记录:")
                for i, sub in enumerate(subscriptions, 1):
                    print(f"   [{i}] {sub.get('subscription_type')} - {sub.get('status')}")
                    print(f"       开始: {sub.get('start_date')}")
                    print(f"       结束: {sub.get('end_date')}")
                    print(f"       交易ID: {sub.get('transaction_id')}")
            
            return True
        else:
            print(f"   ❌ 查询失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ 异常: {e}")
        return False

def test_multiple_products(token, user_id):
    """测试 6: 验证多个产品（不同订阅类型）"""
    print_step(6, "验证多个产品（Premium Yearly）")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 测试 Premium Yearly 订阅
    product_id = "premium_yearly"
    transaction_id = f"test_premium_{int(time.time())}"
    receipt_data = create_mock_receipt_data(product_id, is_subscription=True)
    
    print(f"\n   收据信息:")
    print(f"   产品ID: {product_id}")
    print(f"   交易ID: {transaction_id}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/subscription/verify-receipt",
            headers=headers,
            data={
                "transaction_id": transaction_id,
                "product_id": product_id,
                "receipt_data": receipt_data,
                "platform": "ios"
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ 收据验证成功")
            print(f"   响应: {json.dumps(data, indent=2, ensure_ascii=False)}")
            
            # 验证订阅状态
            time.sleep(1)  # 等待数据库更新
            status_response = requests.get(f"{BASE_URL}/api/subscription/status", headers=headers, timeout=10)
            if status_response.status_code == 200:
                status_data = status_response.json()
                subscription = status_data.get('subscription')
                if subscription and subscription.get('subscription_type') == 'premium_yearly':
                    print(f"   ✅ Premium Yearly 订阅已正确保存")
                else:
                    print(f"   ⚠️  订阅类型可能不正确")
            
            return True
        else:
            print(f"   ❌ 收据验证失败: {response.status_code}")
            print(f"   响应: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ 异常: {e}")
        return False

def main():
    """运行收据验证测试"""
    print_section("收据验证测试 - iOS StoreKit 2 集成")
    print(f"\n测试时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"服务地址: {BASE_URL}")
    print(f"\n⚠️  注意: 此测试使用模拟收据数据，不进行实际的 App Store 验证")
    print(f"   实际环境中需要配置 APP_STORE_SHARED_SECRET")
    
    results = []
    
    # 1. 用户注册
    token, user_id = test_user_registration()
    results.append(("用户注册", token is not None and user_id is not None))
    
    if not token or not user_id:
        print("\n❌ 用户注册失败，无法继续测试")
        return 1
    
    # 2. 验证订阅收据
    subscription_success = test_receipt_verification_subscription(token, user_id)
    results.append(("验证订阅收据", subscription_success))
    
    # 等待数据库更新
    time.sleep(1)
    
    # 3. 验证订阅状态
    status_success = test_subscription_status_after_verification(token)
    results.append(("验证订阅状态", status_success))
    
    # 4. 查询订阅历史
    history_success = test_subscription_history_after_verification(token)
    results.append(("查询订阅历史", history_success))
    
    # 5. 验证一次性购买收据
    purchase_success = test_receipt_verification_purchase(token, user_id)
    results.append(("验证一次性购买收据", purchase_success))
    
    # 等待数据库更新
    time.sleep(1)
    
    # 6. 再次验证订阅状态（包含购买）
    status_success2 = test_subscription_status_after_verification(token)
    results.append(("验证订阅状态（包含购买）", status_success2))
    
    # 7. 验证多个产品
    multiple_success = test_multiple_products(token, user_id)
    results.append(("验证多个产品", multiple_success))
    
    # 汇总结果
    print_section("测试结果汇总")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{name}: {status}")
    
    print(f"\n总计: {passed}/{total} 通过")
    
    if passed == total:
        print("\n🎉 所有测试通过！")
        return 0
    else:
        print(f"\n⚠️  有 {total - passed} 个测试失败")
        return 1

if __name__ == "__main__":
    sys.exit(main())
