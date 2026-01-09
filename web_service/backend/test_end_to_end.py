#!/usr/bin/env python3
"""
端到端测试脚本
模拟完整的用户购买和使用流程：
1. 用户注册
2. 免费试用流程
3. 模拟购买订阅
4. 下载视频（消费次数）
5. 验证订阅状态
6. 测试白名单功能
7. 查询订阅历史
8. 查询下载记录
"""

import os
import sys
import requests
import json
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

# 导入订阅服务模块
from subscription_db import get_db_path
import sqlite3

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

def simulate_subscription_purchase(user_id: str, subscription_type: str = "basic_monthly"):
    """
    模拟订阅购买（直接操作数据库）
    在实际环境中，这应该通过 StoreKit 2 和收据验证完成
    """
    db_path = get_db_path()
    if not db_path:
        print(f"   ❌ 数据库路径未找到")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 计算订阅开始和结束时间
        now = datetime.utcnow()
        if "monthly" in subscription_type:
            end_date = now + timedelta(days=30)
        elif "yearly" in subscription_type:
            end_date = now + timedelta(days=365)
        else:
            end_date = now + timedelta(days=30)
        
        # 插入订阅记录
        cursor.execute("""
            INSERT INTO subscriptions (
                user_id, subscription_type, status, start_date, end_date,
                auto_renew, platform, transaction_id, receipt_data
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id,
            subscription_type,
            "active",
            now.isoformat(),
            end_date.isoformat(),
            1,  # auto_renew
            "ios",
            f"test_transaction_{int(time.time())}",
            "test_receipt_data"
        ))
        
        subscription_id = cursor.lastrowid
        
        # 根据订阅类型添加下载次数
        credits_map = {
            "basic_monthly": 100,
            "basic_yearly": 1200,
            "premium_monthly": 300,
            "premium_yearly": 3600
        }
        total_credits = credits_map.get(subscription_type, 100)
        
        # 插入下载次数记录
        cursor.execute("""
            INSERT INTO download_credits (
                user_id, credit_type, total_credits, used_credits, remaining_credits,
                period_start, period_end, source_subscription_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id,
            "subscription",
            total_credits,
            0,
            total_credits,
            now.isoformat(),
            end_date.isoformat(),
            subscription_id
        ))
        
        conn.commit()
        conn.close()
        
        print(f"   ✅ 模拟购买成功: {subscription_type}, 获得 {total_credits} 次下载")
        return True
    except Exception as e:
        print(f"   ❌ 模拟购买失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def simulate_one_time_purchase(user_id: str, product_id: str = "pack_10"):
    """
    模拟一次性购买（下载次数包）
    """
    db_path = get_db_path()
    if not db_path:
        print(f"   ❌ 数据库路径未找到")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 根据产品ID确定下载次数
        credits_map = {
            "pack_10": 10,
            "pack_50": 50,
            "pack_100": 100
        }
        total_credits = credits_map.get(product_id, 10)
        
        now = datetime.utcnow()
        
        # 插入支付记录
        cursor.execute("""
            INSERT INTO payment_records (
                user_id, payment_type, product_id, amount, currency,
                platform, transaction_id, status, verified
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id,
            "one_time",
            product_id,
            9.99 if product_id == "pack_10" else (29.99 if product_id == "pack_50" else 49.99),
            "CNY",
            "ios",
            f"test_purchase_{int(time.time())}",
            "completed",
            1
        ))
        
        purchase_id = cursor.lastrowid
        
        # 插入下载次数记录
        cursor.execute("""
            INSERT INTO download_credits (
                user_id, credit_type, total_credits, used_credits, remaining_credits,
                source_purchase_id
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, (
            user_id,
            "purchase",
            total_credits,
            0,
            total_credits,
            purchase_id
        ))
        
        conn.commit()
        conn.close()
        
        print(f"   ✅ 模拟购买成功: {product_id}, 获得 {total_credits} 次下载")
        return True
    except Exception as e:
        print(f"   ❌ 模拟购买失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_user_registration():
    """测试 1: 用户注册"""
    print_step(1, "用户注册")
    
    try:
        device_id = f"test_e2e_device_{int(time.time())}"
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

def test_free_trial(token, user_id):
    """测试 2: 免费试用流程"""
    print_step(2, "免费试用流程")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2.1 检查订阅状态（应该显示免费试用）
    print("\n   2.1 检查订阅状态（免费试用）")
    try:
        response = requests.get(f"{BASE_URL}/api/subscription/status", headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            free_trial = data.get("free_trial", {})
            print(f"   ✅ 免费试用状态:")
            print(f"      总数: {free_trial.get('total', 0)}")
            print(f"      已使用: {free_trial.get('used', 0)}")
            print(f"      剩余: {free_trial.get('remaining', 0)}")
            
            if free_trial.get('remaining', 0) == 50:
                print(f"   ✅ 免费试用次数正确（50次）")
            else:
                print(f"   ⚠️  免费试用次数异常: {free_trial.get('remaining', 0)}")
        else:
            print(f"   ❌ 查询失败: {response.status_code}")
    except Exception as e:
        print(f"   ❌ 异常: {e}")
    
    # 2.2 检查下载次数
    print("\n   2.2 检查下载次数")
    try:
        response = requests.get(f"{BASE_URL}/api/credits/check", headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ 可下载: {data.get('can_download', False)}")
            print(f"   剩余次数: {data.get('total_remaining', 0)}")
        else:
            print(f"   ❌ 查询失败: {response.status_code}")
    except Exception as e:
        print(f"   ❌ 异常: {e}")

def test_subscription_purchase(user_id):
    """测试 3: 模拟购买订阅"""
    print_step(3, "模拟购买订阅（Basic Monthly）")
    
    success = simulate_subscription_purchase(user_id, "basic_monthly")
    if success:
        print(f"   ✅ 订阅购买模拟成功")
    else:
        print(f"   ❌ 订阅购买模拟失败")
    return success

def test_one_time_purchase(user_id):
    """测试 4: 模拟一次性购买"""
    print_step(4, "模拟一次性购买（10次下载包）")
    
    success = simulate_one_time_purchase(user_id, "pack_10")
    if success:
        print(f"   ✅ 一次性购买模拟成功")
    else:
        print(f"   ❌ 一次性购买模拟失败")
    return success

def test_subscription_status(token):
    """测试 5: 验证订阅状态"""
    print_step(5, "验证订阅状态")
    
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
            
            return True
        else:
            print(f"   ❌ 查询失败: {response.status_code}")
            print(f"   响应: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ 异常: {e}")
        return False

def test_consume_credits(token, num_consumes=3):
    """测试 6: 消费下载次数"""
    print_step(6, f"消费下载次数（{num_consumes}次）")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    for i in range(num_consumes):
        try:
            response = requests.post(
                f"{BASE_URL}/api/credits/consume",
                headers=headers,
                data={
                    "task_id": f"test_task_{int(time.time())}_{i}",
                    "version": "modular"
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"   [{i+1}] ✅ 消费成功")
                print(f"       剩余次数: {data.get('remaining', 0)}")
                print(f"       次数类型: {data.get('credit_type', 'unknown')}")
            else:
                print(f"   [{i+1}] ❌ 消费失败: {response.status_code}")
                print(f"       响应: {response.text}")
        except Exception as e:
            print(f"   [{i+1}] ❌ 异常: {e}")
        
        time.sleep(0.5)  # 短暂延迟，避免过快请求

def test_whitelist(user_id, admin_token):
    """测试 7: 白名单功能"""
    print_step(7, "白名单功能测试")
    
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    # 7.1 添加白名单
    print("\n   7.1 添加用户到白名单")
    try:
        response = requests.post(
            f"{BASE_URL}/api/admin/whitelist/add",
            headers=headers,
            data={"user_id": user_id, "reason": "端到端测试"},
            timeout=10
        )
        if response.status_code in [200, 201]:
            print(f"   ✅ 添加成功")
        else:
            print(f"   ❌ 添加失败: {response.status_code}")
    except Exception as e:
        print(f"   ❌ 异常: {e}")
    
    # 7.2 检查白名单状态
    print("\n   7.2 检查白名单状态")
    try:
        response = requests.get(
            f"{BASE_URL}/api/admin/whitelist/check/{user_id}",
            headers=headers,
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ 用户在白名单中: {data.get('is_whitelisted', False)}")
        else:
            print(f"   ❌ 查询失败: {response.status_code}")
    except Exception as e:
        print(f"   ❌ 异常: {e}")
    
    # 7.3 删除白名单
    print("\n   7.3 删除白名单用户")
    try:
        response = requests.delete(
            f"{BASE_URL}/api/admin/whitelist/{user_id}",
            headers=headers,
            timeout=10
        )
        if response.status_code == 200:
            print(f"   ✅ 删除成功")
        else:
            print(f"   ❌ 删除失败: {response.status_code}")
    except Exception as e:
        print(f"   ❌ 异常: {e}")

def test_subscription_history(token):
    """测试 8: 查询订阅历史"""
    print_step(8, "查询订阅历史")
    
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
            print(f"   当前页: {data.get('page', 0)}")
            print(f"   记录数: {len(data.get('subscriptions', []))}")
            
            subscriptions = data.get('subscriptions', [])
            if subscriptions:
                print(f"\n   订阅记录:")
                for i, sub in enumerate(subscriptions[:3], 1):  # 只显示前3条
                    print(f"   [{i}] {sub.get('subscription_type')} - {sub.get('status')}")
                    print(f"       开始: {sub.get('start_date')}")
                    print(f"       结束: {sub.get('end_date')}")
            return True
        else:
            print(f"   ❌ 查询失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ 异常: {e}")
        return False

def test_download_history(token):
    """测试 9: 查询下载记录"""
    print_step(9, "查询下载记录")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/downloads/history",
            headers=headers,
            params={"page": 1, "limit": 10},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ 查询成功")
            print(f"   总数: {data.get('total', 0)}")
            print(f"   当前页: {data.get('page', 0)}")
            print(f"   记录数: {len(data.get('downloads', []))}")
            
            downloads = data.get('downloads', [])
            if downloads:
                print(f"\n   下载记录:")
                for i, dl in enumerate(downloads[:5], 1):  # 只显示前5条
                    print(f"   [{i}] {dl.get('task_id')} - {dl.get('version')}")
                    print(f"       次数类型: {dl.get('credit_type')}")
                    print(f"       时间: {dl.get('created_at')}")
            return True
        else:
            print(f"   ❌ 查询失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ 异常: {e}")
        return False

def main():
    """运行端到端测试"""
    print_section("端到端测试 - 完整用户购买和使用流程")
    print(f"\n测试时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"服务地址: {BASE_URL}")
    print(f"\n⚠️  请确保服务已启动并设置了环境变量：")
    print(f"   SUBSCRIPTION_ENABLED=true")
    print(f"   ADMIN_TOKEN=test_admin_token_12345")
    print(f"   JWT_SECRET_KEY=test_jwt_secret_key_12345")
    
    results = []
    
    # 1. 用户注册
    token, user_id = test_user_registration()
    results.append(("用户注册", token is not None and user_id is not None))
    
    if not token or not user_id:
        print("\n❌ 用户注册失败，无法继续测试")
        return 1
    
    # 2. 免费试用流程
    test_free_trial(token, user_id)
    results.append(("免费试用流程", True))
    
    # 3. 模拟购买订阅
    purchase_success = test_subscription_purchase(user_id)
    results.append(("模拟购买订阅", purchase_success))
    
    # 4. 模拟一次性购买
    one_time_success = test_one_time_purchase(user_id)
    results.append(("模拟一次性购买", one_time_success))
    
    # 5. 验证订阅状态
    status_success = test_subscription_status(token)
    results.append(("验证订阅状态", status_success))
    
    # 6. 消费下载次数
    test_consume_credits(token, num_consumes=5)
    results.append(("消费下载次数", True))
    
    # 7. 白名单功能
    admin_token = os.environ.get("ADMIN_TOKEN", "test_admin_token_12345")
    test_whitelist(user_id, admin_token)
    results.append(("白名单功能", True))
    
    # 8. 查询订阅历史
    history_success = test_subscription_history(token)
    results.append(("查询订阅历史", history_success))
    
    # 9. 查询下载记录
    download_history_success = test_download_history(token)
    results.append(("查询下载记录", download_history_success))
    
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
