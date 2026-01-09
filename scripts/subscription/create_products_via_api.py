#!/usr/bin/env python3
"""
使用 App Store Connect API 批量创建内购商品
需要 App Store Connect API Key
"""

import os
import json
import jwt
import time
import requests
from pathlib import Path

# 从环境变量获取 API 凭证
API_KEY_ID = os.getenv("APP_STORE_CONNECT_API_KEY_ID")
API_ISSUER_ID = os.getenv("APP_STORE_CONNECT_API_ISSUER_ID")
API_KEY_PATH = os.getenv("APP_STORE_CONNECT_API_KEY_PATH")  # .p8 文件路径

# App Store Connect API 基础 URL
API_BASE_URL = "https://api.appstoreconnect.apple.com/v1"

# 产品配置
PRODUCTS_CONFIG = Path(__file__).parent.parent.parent / "ios/App/Products_Config.json"


def generate_jwt_token():
    """生成 JWT Token 用于 API 认证"""
    if not all([API_KEY_ID, API_ISSUER_ID, API_KEY_PATH]):
        raise ValueError("缺少 API 凭证，请设置环境变量：APP_STORE_CONNECT_API_KEY_ID, APP_STORE_CONNECT_API_ISSUER_ID, APP_STORE_CONNECT_API_KEY_PATH")
    
    # 读取私钥
    with open(API_KEY_PATH, 'r') as f:
        private_key = f.read()
    
    # 生成 JWT
    headers = {
        "alg": "ES256",
        "kid": API_KEY_ID,
        "typ": "JWT"
    }
    
    payload = {
        "iss": API_ISSUER_ID,
        "iat": int(time.time()),
        "exp": int(time.time()) + 1200,  # 20分钟有效期
        "aud": "appstoreconnect-v1"
    }
    
    token = jwt.encode(payload, private_key, algorithm="ES256", headers=headers)
    return token


def get_app_id(app_name="BeatSync"):
    """获取 App ID"""
    token = generate_jwt_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    response = requests.get(
        f"{API_BASE_URL}/apps",
        headers=headers,
        params={"filter[name]": app_name}
    )
    
    if response.status_code == 200:
        data = response.json()
        if data.get("data"):
            return data["data"][0]["id"]
    
    raise Exception(f"找不到 App: {app_name}")


def create_subscription_group(group_name, reference_name):
    """创建订阅组"""
    token = generate_jwt_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    app_id = get_app_id()
    
    payload = {
        "data": {
            "type": "subscriptionGroups",
            "attributes": {
                "referenceName": reference_name
            },
            "relationships": {
                "app": {
                    "data": {
                        "type": "apps",
                        "id": app_id
                    }
                }
            }
        }
    }
    
    response = requests.post(
        f"{API_BASE_URL}/subscriptionGroups",
        headers=headers,
        json=payload
    )
    
    if response.status_code == 201:
        data = response.json()
        group_id = data["data"]["id"]
        print(f"✅ 订阅组创建成功: {group_name} (ID: {group_id})")
        return group_id
    else:
        print(f"❌ 订阅组创建失败: {response.status_code} - {response.text}")
        return None


def create_subscription_product(product_config, subscription_group_id):
    """创建订阅产品"""
    token = generate_jwt_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # 确定订阅期限代码
    duration_map = {
        "monthly": "P1M",
        "yearly": "P1Y"
    }
    duration = duration_map.get(product_config["duration"], "P1M")
    
    payload = {
        "data": {
            "type": "subscriptions",
            "attributes": {
                "name": product_config["name_zh"],
                "productId": product_config["product_id"],
                "subscriptionPeriod": duration,
                "familySharable": False,
                "reviewNote": f"BeatSync {product_config['name_zh']} 订阅"
            },
            "relationships": {
                "subscriptionGroup": {
                    "data": {
                        "type": "subscriptionGroups",
                        "id": subscription_group_id
                    }
                }
            }
        }
    }
    
    response = requests.post(
        f"{API_BASE_URL}/subscriptions",
        headers=headers,
        json=payload
    )
    
    if response.status_code == 201:
        data = response.json()
        subscription_id = data["data"]["id"]
        print(f"✅ 订阅产品创建成功: {product_config['product_id']} (ID: {subscription_id})")
        
        # 创建本地化信息
        create_subscription_localization(subscription_id, product_config)
        
        # 设置价格
        set_subscription_price(subscription_id, product_config)
        
        return subscription_id
    else:
        print(f"❌ 订阅产品创建失败: {response.status_code} - {response.text}")
        return None


def create_subscription_localization(subscription_id, product_config):
    """创建订阅本地化信息"""
    token = generate_jwt_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # 中文本地化
    payload_zh = {
        "data": {
            "type": "subscriptionLocalizations",
            "attributes": {
                "name": product_config["name_zh"],
                "description": product_config["description_zh"],
                "locale": "zh-Hans"
            },
            "relationships": {
                "subscription": {
                    "data": {
                        "type": "subscriptions",
                        "id": subscription_id
                    }
                }
            }
        }
    }
    
    response = requests.post(
        f"{API_BASE_URL}/subscriptionLocalizations",
        headers=headers,
        json=payload_zh
    )
    
    if response.status_code == 201:
        print(f"  ✅ 中文本地化创建成功")
    else:
        print(f"  ⚠️  中文本地化创建失败: {response.status_code}")
    
    # 英文本地化
    payload_en = {
        "data": {
            "type": "subscriptionLocalizations",
            "attributes": {
                "name": product_config["name_en"],
                "description": product_config["description_en"],
                "locale": "en-US"
            },
            "relationships": {
                "subscription": {
                    "data": {
                        "type": "subscriptions",
                        "id": subscription_id
                    }
                }
            }
        }
    }
    
    response = requests.post(
        f"{API_BASE_URL}/subscriptionLocalizations",
        headers=headers,
        json=payload_en
    )
    
    if response.status_code == 201:
        print(f"  ✅ 英文本地化创建成功")
    else:
        print(f"  ⚠️  英文本地化创建失败: {response.status_code}")


def set_subscription_price(subscription_id, product_config):
    """设置订阅价格"""
    token = generate_jwt_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # 获取价格时间表
    # 注意：价格设置需要先获取价格时间表ID，这里简化处理
    # 实际实现需要更复杂的逻辑
    
    print(f"  ⚠️  价格设置需要在 App Store Connect 网站手动完成")
    print(f"  💡 价格: {product_config['price_cny']} CNY")


def create_in_app_purchase(product_config):
    """创建一次性购买产品"""
    token = generate_jwt_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    app_id = get_app_id()
    
    payload = {
        "data": {
            "type": "inAppPurchases",
            "attributes": {
                "name": product_config["name_zh"],
                "productId": product_config["product_id"],
                "inAppPurchaseType": "NON_CONSUMABLE",
                "reviewNote": f"BeatSync {product_config['name_zh']} 一次性购买"
            },
            "relationships": {
                "app": {
                    "data": {
                        "type": "apps",
                        "id": app_id
                    }
                }
            }
        }
    }
    
    response = requests.post(
        f"{API_BASE_URL}/inAppPurchases",
        headers=headers,
        json=payload
    )
    
    if response.status_code == 201:
        data = response.json()
        iap_id = data["data"]["id"]
        print(f"✅ 内购产品创建成功: {product_config['product_id']} (ID: {iap_id})")
        
        # 创建本地化信息
        create_iap_localization(iap_id, product_config)
        
        return iap_id
    else:
        print(f"❌ 内购产品创建失败: {response.status_code} - {response.text}")
        return None


def create_iap_localization(iap_id, product_config):
    """创建内购产品本地化信息"""
    token = generate_jwt_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # 中文本地化
    payload_zh = {
        "data": {
            "type": "inAppPurchaseLocalizations",
            "attributes": {
                "name": product_config["name_zh"],
                "description": product_config["description_zh"],
                "locale": "zh-Hans"
            },
            "relationships": {
                "inAppPurchase": {
                    "data": {
                        "type": "inAppPurchases",
                        "id": iap_id
                    }
                }
            }
        }
    }
    
    response = requests.post(
        f"{API_BASE_URL}/inAppPurchaseLocalizations",
        headers=headers,
        json=payload_zh
    )
    
    if response.status_code == 201:
        print(f"  ✅ 中文本地化创建成功")
    else:
        print(f"  ⚠️  中文本地化创建失败: {response.status_code}")
    
    # 英文本地化
    payload_en = {
        "data": {
            "type": "inAppPurchaseLocalizations",
            "attributes": {
                "name": product_config["name_en"],
                "description": product_config["description_en"],
                "locale": "en-US"
            },
            "relationships": {
                "inAppPurchase": {
                    "data": {
                        "type": "inAppPurchases",
                        "id": iap_id
                    }
                }
            }
        }
    }
    
    response = requests.post(
        f"{API_BASE_URL}/inAppPurchaseLocalizations",
        headers=headers,
        json=payload_en
    )
    
    if response.status_code == 201:
        print(f"  ✅ 英文本地化创建成功")
    else:
        print(f"  ⚠️  英文本地化创建失败: {response.status_code}")


def main():
    """主函数：批量创建产品"""
    print("=" * 60)
    print("使用 App Store Connect API 批量创建内购商品")
    print("=" * 60)
    print()
    
    # 检查 API 凭证
    if not all([API_KEY_ID, API_ISSUER_ID, API_KEY_PATH]):
        print("❌ 缺少 API 凭证")
        print()
        print("请设置以下环境变量：")
        print("  APP_STORE_CONNECT_API_KEY_ID=your_key_id")
        print("  APP_STORE_CONNECT_API_ISSUER_ID=your_issuer_id")
        print("  APP_STORE_CONNECT_API_KEY_PATH=/path/to/AuthKey_XXX.p8")
        print()
        print("获取 API Key 步骤：")
        print("1. 登录 App Store Connect")
        print("2. 进入 '用户和访问' → '密钥' → 'App Store Connect API'")
        print("3. 创建新密钥并下载 .p8 文件")
        return 1
    
    # 读取产品配置
    if not PRODUCTS_CONFIG.exists():
        print(f"❌ 产品配置文件不存在: {PRODUCTS_CONFIG}")
        return 1
    
    with open(PRODUCTS_CONFIG, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    products = config.get("products", [])
    subscription_groups = config.get("subscription_groups", [])
    
    print(f"📦 准备创建 {len(products)} 个产品")
    print(f"📦 准备创建 {len(subscription_groups)} 个订阅组")
    print()
    
    # 创建订阅组
    group_map = {}
    for group in subscription_groups:
        group_id = create_subscription_group(group["name_zh"], group["reference_name"])
        if group_id:
            group_map[group["group_id"]] = group_id
        time.sleep(1)  # 避免请求过快
    
    print()
    
    # 创建产品
    for product in products:
        if product["type"] == "auto-renewable-subscription":
            # 订阅产品
            group_id = group_map.get(product.get("subscription_group"))
            if group_id:
                create_subscription_product(product, group_id)
            else:
                print(f"❌ 找不到订阅组: {product.get('subscription_group')}")
        elif product["type"] == "non-consumable":
            # 一次性购买
            create_in_app_purchase(product)
        
        time.sleep(2)  # 避免请求过快
    
    print()
    print("=" * 60)
    print("✅ 产品创建完成！")
    print("=" * 60)
    print()
    print("⚠️  注意：")
    print("1. 价格设置需要在 App Store Connect 网站手动完成")
    print("2. 产品创建后需要提交审核")
    print("3. 建议在 App Store Connect 网站验证所有产品信息")
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())

