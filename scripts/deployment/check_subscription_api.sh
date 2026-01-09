#!/bin/bash
# 检查服务器上的订阅API端点

echo "🔍 检查服务器上的订阅API端点..."
echo ""

# SSH连接并执行检查命令
ssh ubuntu@124.221.58.149 << 'EOF'
echo "=== 1. 检查端点是否存在 ==="
cd /opt/beatsync/web_service/backend
if grep -q "/api/subscription/products" main.py; then
    echo "✅ 端点已找到"
    grep -n "/api/subscription/products" main.py | head -1
else
    echo "❌ 端点未找到"
fi

echo ""
echo "=== 2. 检查服务状态 ==="
sudo systemctl status beatsync --no-pager | head -10

echo ""
echo "=== 3. 检查最近的日志 ==="
sudo journalctl -u beatsync -n 20 --no-pager | grep -i "subscription\|error\|404" || echo "无相关日志"

echo ""
echo "=== 4. 检查订阅系统是否启用 ==="
cd /opt/beatsync/web_service/backend
if [ -f ".env" ]; then
    echo "环境变量文件存在:"
    grep SUBSCRIPTION_ENABLED .env || echo "未找到 SUBSCRIPTION_ENABLED"
else
    echo "环境变量文件不存在"
    echo "检查systemd服务配置:"
    sudo systemctl show beatsync | grep SUBSCRIPTION_ENABLED || echo "未在服务配置中找到"
fi

echo ""
echo "=== 5. 测试API端点（本地） ==="
curl -s http://localhost:8000/api/subscription/products | head -20

EOF

echo ""
echo "✅ 检查完成！"

