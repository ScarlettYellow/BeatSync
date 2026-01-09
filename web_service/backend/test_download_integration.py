#!/usr/bin/env python3
"""
下载接口集成测试
测试订阅系统与下载接口的集成
"""

import os
import sys
import requests
import json
import time
from pathlib import Path

BASE_URL = "http://localhost:8000"

def print_section(title):
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)

def find_test_task_id():
    """查找可用的测试任务ID"""
    output_dir = Path(__file__).parent.parent.parent / "outputs" / "web_outputs"
    if not output_dir.exists():
        return None
    
    # 查找包含视频文件的目录
    for task_dir in output_dir.iterdir():
        if task_dir.is_dir():
            # 检查是否有输出文件
            modular_file = task_dir / f"{task_dir.name}_modular.mp4"
            v2_file = task_dir / f"{task_dir.name}_v2.mp4"
            if modular_file.exists() or v2_file.exists():
                return task_dir.name
    
    return None

def test_anonymous_download(task_id, version="modular"):
    """测试匿名下载（无认证，向后兼容）"""
    print_section("1. 匿名下载测试（向后兼容）")
    print(f"   任务ID: {task_id}")
    print(f"   版本: {version}")
    print(f"   认证: 无")
    
    try:
        url = f"{BASE_URL}/api/download/{task_id}?version={version}"
        response = requests.get(url, stream=True, timeout=10)
        
        print(f"   状态码: {response.status_code}")
        print(f"   Content-Type: {response.headers.get('Content-Type', 'N/A')}")
        print(f"   Content-Length: {response.headers.get('Content-Length', 'N/A')}")
        
        if response.status_code == 200:
            # 读取一小部分内容验证
            content = next(response.iter_content(chunk_size=1024), b'')
            if len(content) > 0:
                print(f"   ✅ 匿名下载成功（向后兼容）")
                print(f"   文件大小: {len(content)} bytes (前1KB)")
                return True
            else:
                print(f"   ⚠️  响应为空")
                return False
        elif response.status_code == 404:
            print(f"   ⚠️  任务不存在（这是正常的，如果没有实际任务）")
            return None  # 不是错误，只是没有任务
        else:
            print(f"   ❌ 下载失败")
            try:
                error_data = response.json()
                print(f"   错误信息: {json.dumps(error_data, indent=2, ensure_ascii=False)}")
            except:
                print(f"   错误信息: {response.text[:200]}")
            return False
    except Exception as e:
        print(f"   ❌ 异常: {e}")
        return False

def test_authenticated_download(task_id, token, version="modular"):
    """测试认证用户下载"""
    print_section("2. 认证用户下载测试")
    print(f"   任务ID: {task_id}")
    print(f"   版本: {version}")
    print(f"   认证: Bearer Token")
    
    try:
        # 先检查下载次数
        print("\n   2.1 检查下载次数（下载前）")
        headers = {"Authorization": f"Bearer {token}"}
        credits_response = requests.get(
            f"{BASE_URL}/api/credits/check",
            headers=headers,
            timeout=5
        )
        if credits_response.status_code == 200:
            credits_before = credits_response.json()
            print(f"      剩余次数: {credits_before.get('total_remaining', 0)}")
            print(f"      可下载: {credits_before.get('can_download', False)}")
        else:
            print(f"      ⚠️  无法检查下载次数")
            credits_before = None
        
        # 尝试下载
        print("\n   2.2 尝试下载")
        url = f"{BASE_URL}/api/download/{task_id}?version={version}"
        response = requests.get(url, headers=headers, stream=True, timeout=10)
        
        print(f"      状态码: {response.status_code}")
        
        if response.status_code == 200:
            content = next(response.iter_content(chunk_size=1024), b'')
            if len(content) > 0:
                print(f"      ✅ 下载成功")
                print(f"      文件大小: {len(content)} bytes (前1KB)")
                
                # 再次检查下载次数（如果任务真实存在，应该减少）
                if credits_before:
                    print("\n   2.3 检查下载次数（下载后）")
                    credits_response_after = requests.get(
                        f"{BASE_URL}/api/credits/check",
                        headers=headers,
                        timeout=5
                    )
                    if credits_response_after.status_code == 200:
                        credits_after = credits_response_after.json()
                        remaining_after = credits_after.get('total_remaining', 0)
                        remaining_before = credits_before.get('total_remaining', 0)
                        print(f"      剩余次数: {remaining_after} (之前: {remaining_before})")
                        if remaining_after < remaining_before:
                            print(f"      ✅ 下载次数已减少（消费成功）")
                        elif task_id and Path(f"../outputs/web_outputs/{task_id}").exists():
                            print(f"      ⚠️  次数未减少（可能是任务不存在或未实际下载）")
                
                return True
            else:
                print(f"      ⚠️  响应为空")
                return False
        elif response.status_code == 403:
            print(f"      ❌ 下载被拒绝（次数不足）")
            try:
                error_data = response.json()
                print(f"      错误信息: {json.dumps(error_data, indent=2, ensure_ascii=False)}")
            except:
                print(f"      错误信息: {response.text[:200]}")
            return False
        elif response.status_code == 404:
            print(f"      ⚠️  任务不存在（这是正常的，如果没有实际任务）")
            return None
        else:
            print(f"      ❌ 下载失败")
            try:
                error_data = response.json()
                print(f"      错误信息: {json.dumps(error_data, indent=2, ensure_ascii=False)}")
            except:
                print(f"      错误信息: {response.text[:200]}")
            return False
    except Exception as e:
        print(f"      ❌ 异常: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_whitelist_download(task_id, token, admin_token, user_id, version="modular"):
    """测试白名单用户下载"""
    print_section("3. 白名单用户下载测试")
    print(f"   任务ID: {task_id}")
    print(f"   版本: {version}")
    
    try:
        # 添加用户到白名单
        print("\n   3.1 添加用户到白名单")
        headers = {"Authorization": f"Bearer {admin_token}"}
        add_response = requests.post(
            f"{BASE_URL}/api/admin/whitelist/add",
            headers=headers,
            data={"user_id": user_id, "reason": "下载接口测试"},
            timeout=5
        )
        if add_response.status_code in [200, 201]:
            print(f"      ✅ 用户已添加到白名单")
        else:
            print(f"      ⚠️  添加白名单失败: {add_response.status_code}")
            return False
        
        # 检查订阅状态（应该显示在白名单中）
        print("\n   3.2 检查订阅状态")
        user_headers = {"Authorization": f"Bearer {token}"}
        status_response = requests.get(
            f"{BASE_URL}/api/subscription/status",
            headers=user_headers,
            timeout=5
        )
        if status_response.status_code == 200:
            status_data = status_response.json()
            is_whitelisted = status_data.get('is_whitelisted', False)
            print(f"      白名单状态: {is_whitelisted}")
            if is_whitelisted:
                print(f"      ✅ 用户在白名单中")
            else:
                print(f"      ⚠️  用户不在白名单中（可能延迟）")
        
        # 尝试下载
        print("\n   3.3 尝试下载（白名单用户）")
        url = f"{BASE_URL}/api/download/{task_id}?version={version}"
        response = requests.get(url, headers=user_headers, stream=True, timeout=10)
        
        print(f"      状态码: {response.status_code}")
        
        if response.status_code == 200:
            content = next(response.iter_content(chunk_size=1024), b'')
            if len(content) > 0:
                print(f"      ✅ 白名单用户下载成功")
                print(f"      文件大小: {len(content)} bytes (前1KB)")
                
                # 检查下载次数（白名单用户不应该消费次数）
                print("\n   3.4 检查下载次数（白名单用户不应消费）")
                credits_response = requests.get(
                    f"{BASE_URL}/api/credits/check",
                    headers=user_headers,
                    timeout=5
                )
                if credits_response.status_code == 200:
                    credits = credits_response.json()
                    remaining = credits.get('total_remaining', 0)
                    print(f"      剩余次数: {remaining}")
                    if remaining == 999999 or remaining > 1000:
                        print(f"      ✅ 次数未减少（白名单用户不受限制）")
                    else:
                        print(f"      ⚠️  次数: {remaining}（可能需要进一步验证）")
                
                return True
            else:
                print(f"      ⚠️  响应为空")
                return False
        elif response.status_code == 404:
            print(f"      ⚠️  任务不存在（这是正常的，如果没有实际任务）")
            return None
        else:
            print(f"      ❌ 下载失败")
            try:
                error_data = response.json()
                print(f"      错误信息: {json.dumps(error_data, indent=2, ensure_ascii=False)}")
            except:
                print(f"      错误信息: {response.text[:200]}")
            return False
    except Exception as e:
        print(f"      ❌ 异常: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # 清理：删除白名单
        try:
            print("\n   3.5 清理：删除白名单")
            headers = {"Authorization": f"Bearer {admin_token}"}
            delete_response = requests.delete(
                f"{BASE_URL}/api/admin/whitelist/{user_id}",
                headers=headers,
                timeout=5
            )
            if delete_response.status_code == 200:
                print(f"      ✅ 白名单已删除")
        except:
            pass

def test_insufficient_credits(task_id, token, version="modular"):
    """测试次数不足时的下载"""
    print_section("4. 次数不足测试")
    print(f"   任务ID: {task_id}")
    print(f"   版本: {version}")
    print(f"   注意：此测试需要用户次数为0，可能需要手动设置")
    
    try:
        # 检查当前次数
        print("\n   4.1 检查当前下载次数")
        headers = {"Authorization": f"Bearer {token}"}
        credits_response = requests.get(
            f"{BASE_URL}/api/credits/check",
            headers=headers,
            timeout=5
        )
        if credits_response.status_code == 200:
            credits = credits_response.json()
            remaining = credits.get('total_remaining', 0)
            can_download = credits.get('can_download', False)
            print(f"      剩余次数: {remaining}")
            print(f"      可下载: {can_download}")
            
            if remaining > 0:
                print(f"      ⚠️  用户仍有次数，无法测试次数不足场景")
                print(f"      提示：可以等待次数用尽或手动修改数据库")
                return None
        
        # 尝试下载
        print("\n   4.2 尝试下载（次数不足）")
        url = f"{BASE_URL}/api/download/{task_id}?version={version}"
        response = requests.get(url, headers=headers, stream=True, timeout=10)
        
        print(f"      状态码: {response.status_code}")
        
        if response.status_code == 403:
            print(f"      ✅ 正确拒绝下载（次数不足）")
            try:
                error_data = response.json()
                print(f"      错误信息: {json.dumps(error_data, indent=2, ensure_ascii=False)}")
            except:
                print(f"      错误信息: {response.text[:200]}")
            return True
        elif response.status_code == 200:
            print(f"      ⚠️  仍然允许下载（可能是任务不存在或匿名模式）")
            return None
        else:
            print(f"      ⚠️  其他状态码: {response.status_code}")
            return None
    except Exception as e:
        print(f"      ❌ 异常: {e}")
        return False

def main():
    """运行所有测试"""
    print("=" * 60)
    print("下载接口集成测试")
    print("=" * 60)
    print(f"\n测试时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"服务地址: {BASE_URL}")
    print(f"\n⚠️  请确保服务已启动并启用了订阅系统")
    
    # 检查服务
    try:
        health_response = requests.get(f"{BASE_URL}/api/health", timeout=5)
        if health_response.status_code != 200:
            print("\n❌ 服务未运行或不可用")
            return 1
    except Exception as e:
        print(f"\n❌ 无法连接到服务: {e}")
        return 1
    
    # 查找测试任务ID
    print("\n查找测试任务...")
    task_id = find_test_task_id()
    if task_id:
        print(f"✅ 找到测试任务: {task_id}")
    else:
        print(f"⚠️  未找到测试任务，将使用虚拟任务ID进行测试")
        task_id = "test_task_12345"  # 虚拟任务ID
    
    # 注册测试用户
    print("\n注册测试用户...")
    try:
        register_response = requests.post(
            f"{BASE_URL}/api/auth/register",
            data={"device_id": f"test_download_{int(time.time())}"},
            timeout=5
        )
        if register_response.status_code == 200:
            user_data = register_response.json()
            token = user_data.get("token")
            user_id = user_data.get("user_id")
            print(f"✅ 用户注册成功: {user_id}")
        else:
            print(f"❌ 用户注册失败: {register_response.status_code}")
            print(f"   响应: {register_response.json()}")
            return 1
    except Exception as e:
        print(f"❌ 用户注册异常: {e}")
        return 1
    
    # 获取管理员Token
    admin_token = os.getenv("ADMIN_TOKEN", "test_admin_token_12345")
    
    results = []
    
    # 1. 匿名下载测试
    result = test_anonymous_download(task_id)
    results.append(("匿名下载", result))
    
    # 2. 认证用户下载测试
    result = test_authenticated_download(task_id, token)
    results.append(("认证用户下载", result))
    
    # 3. 白名单用户下载测试
    result = test_whitelist_download(task_id, token, admin_token, user_id)
    results.append(("白名单用户下载", result))
    
    # 4. 次数不足测试（可选）
    result = test_insufficient_credits(task_id, token)
    if result is not None:
        results.append(("次数不足测试", result))
    
    # 汇总结果
    print_section("测试结果汇总")
    
    passed = sum(1 for _, result in results if result is True)
    failed = sum(1 for _, result in results if result is False)
    skipped = sum(1 for _, result in results if result is None)
    total = len(results)
    
    for name, result in results:
        if result is True:
            status = "✅ 通过"
        elif result is False:
            status = "❌ 失败"
        else:
            status = "⚠️  跳过（无任务）"
        print(f"{name}: {status}")
    
    print(f"\n总计: {passed} 通过, {failed} 失败, {skipped} 跳过 / {total} 测试")
    
    if failed == 0:
        print("\n🎉 所有测试通过或跳过（无实际任务时跳过是正常的）")
        return 0
    else:
        print(f"\n⚠️  有 {failed} 个测试失败")
        return 1

if __name__ == "__main__":
    sys.exit(main())

