#!/bin/bash
# 启用订阅系统并运行完整测试

cd "$(dirname "$0")"

echo "=========================================="
echo "启用订阅系统并运行完整测试"
echo "=========================================="

# 设置环境变量
export SUBSCRIPTION_ENABLED=true
export ADMIN_TOKEN=test_admin_token_12345
export JWT_SECRET_KEY=test_jwt_secret_key_12345

echo "✅ 环境变量已设置"
echo "   SUBSCRIPTION_ENABLED=true"
echo "   ADMIN_TOKEN=test_admin_token_12345"
echo "   JWT_SECRET_KEY=test_jwt_secret_key_12345"
echo ""

# 运行测试
echo "开始运行测试..."
python3 test_subscription.py
