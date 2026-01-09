#!/bin/bash
# 检查并修复 /api/auth/register 端点

MAIN_PY="/opt/beatsync/web_service/backend/main.py"

echo "🔍 检查 /api/auth/register 端点位置..."

# 检查端点是否已修复
if grep -q "用户认证端点（移到条件块外，确保始终可用）" "$MAIN_PY"; then
    echo "✅ 端点已在条件块外，无需修复"
    exit 0
fi

# 查找端点位置
REGISTER_LINE=$(grep -n '@app.post("/api/auth/register")' "$MAIN_PY" | cut -d: -f1)
SUBSCRIPTION_IF_LINE=$(grep -n '^if SUBSCRIPTION_AVAILABLE:' "$MAIN_PY" | head -1 | cut -d: -f1)

if [ -z "$REGISTER_LINE" ]; then
    echo "❌ 未找到 @app.post(\"/api/auth/register\") 端点"
    exit 1
fi

if [ -z "$SUBSCRIPTION_IF_LINE" ]; then
    echo "❌ 未找到 if SUBSCRIPTION_AVAILABLE: 条件块"
    exit 1
fi

echo "📍 端点位置：第 $REGISTER_LINE 行"
echo "📍 条件块位置：第 $SUBSCRIPTION_IF_LINE 行"

# 检查端点是否在条件块内
if [ "$REGISTER_LINE" -gt "$SUBSCRIPTION_IF_LINE" ]; then
    echo "⚠️  端点在条件块内，需要修复"
    echo "   请使用 Python 脚本或手动编辑文件"
    echo "   参考：docs/deployment/MANUAL_FIX_AUTH_REGISTER.md"
    exit 1
else
    echo "✅ 端点已在条件块外，无需修复"
    exit 0
fi



