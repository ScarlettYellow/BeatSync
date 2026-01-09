#!/bin/bash
# 启用订阅系统并启动服务

cd "$(dirname "$0")"

echo "=========================================="
echo "启动后端服务（启用订阅系统）"
echo "=========================================="

# 设置环境变量
export SUBSCRIPTION_ENABLED=true
export ADMIN_TOKEN=test_admin_token_12345
export JWT_SECRET_KEY=test_jwt_secret_key_12345

echo "✅ 环境变量已设置："
echo "   SUBSCRIPTION_ENABLED=true"
echo "   ADMIN_TOKEN=test_admin_token_12345"
echo "   JWT_SECRET_KEY=test_jwt_secret_key_12345"
echo ""

echo "启动服务..."
python3 main.py

