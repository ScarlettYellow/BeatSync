#!/bin/bash
# 完整的 API 测试脚本（包括启用订阅系统）

BASE_URL="http://localhost:8000"
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "=========================================="
echo "订阅系统 API 完整测试"
echo "=========================================="
echo ""

# 检查服务是否运行
check_service() {
    if curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/api/health" | grep -q "200"; then
        return 0
    else
        return 1
    fi
}

# 测试场景 1: 订阅系统关闭（向后兼容）
echo -e "${BLUE}==========================================${NC}"
echo -e "${BLUE}测试场景 1: 订阅系统关闭（向后兼容）${NC}"
echo -e "${BLUE}==========================================${NC}"
echo ""

if ! check_service; then
    echo -e "${RED}❌ 后端服务未运行${NC}"
    echo "请先启动服务: cd web_service/backend && python3 main.py"
    exit 1
fi

echo "1.1 测试健康检查接口..."
HEALTH=$(curl -s "$BASE_URL/api/health")
echo "$HEALTH" | python3 -m json.tool 2>/dev/null || echo "$HEALTH"
echo ""

echo "1.2 测试订阅状态查询（应返回未启用）..."
STATUS=$(curl -s "$BASE_URL/api/subscription/status")
echo "$STATUS" | python3 -m json.tool 2>/dev/null || echo "$STATUS"
if echo "$STATUS" | grep -q "订阅系统未启用\|error"; then
    echo -e "${GREEN}✅ 正确：订阅系统未启用（向后兼容）${NC}"
fi
echo ""

echo "1.3 测试下载次数检查（无认证，应允许）..."
CREDITS=$(curl -s "$BASE_URL/api/credits/check")
echo "$CREDITS" | python3 -m json.tool 2>/dev/null || echo "$CREDITS"
if echo "$CREDITS" | grep -q "can_download.*true\|total_remaining"; then
    echo -e "${GREEN}✅ 正确：无认证时允许下载（向后兼容）${NC}"
fi
echo ""

# 测试场景 2: 启用订阅系统
echo -e "${BLUE}==========================================${NC}"
echo -e "${BLUE}测试场景 2: 启用订阅系统进行完整测试${NC}"
echo -e "${BLUE}==========================================${NC}"
echo ""

echo -e "${YELLOW}注意：需要重启服务并设置环境变量${NC}"
echo "停止当前服务，然后运行："
echo "  cd web_service/backend"
echo "  SUBSCRIPTION_ENABLED=true ADMIN_TOKEN=test_admin_token JWT_SECRET_KEY=test_jwt_secret python3 main.py"
echo ""

# 如果检测到订阅系统已启用，进行完整测试
STATUS_CHECK=$(curl -s "$BASE_URL/api/subscription/status")
if ! echo "$STATUS_CHECK" | grep -q "订阅系统未启用\|error"; then
    echo -e "${GREEN}检测到订阅系统已启用，进行完整测试...${NC}"
    echo ""
    
    echo "2.1 测试用户注册..."
    REGISTER_RESPONSE=$(curl -s -X POST "$BASE_URL/api/auth/register" \
      -H "Content-Type: application/x-www-form-urlencoded" \
      -d "device_id=test_device_$(date +%s)")
    echo "$REGISTER_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$REGISTER_RESPONSE"
    
    # 提取 token 和 user_id
    TOKEN=$(echo "$REGISTER_RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('token', ''))" 2>/dev/null)
    USER_ID=$(echo "$REGISTER_RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('user_id', ''))" 2>/dev/null)
    
    if [ -n "$TOKEN" ] && [ -n "$USER_ID" ]; then
        echo -e "${GREEN}✅ 用户注册成功${NC}"
        echo "  User ID: $USER_ID"
        echo "  Token: ${TOKEN:0:30}..."
        echo ""
        
        echo "2.2 测试订阅状态查询..."
        STATUS_RESPONSE=$(curl -s -X GET "$BASE_URL/api/subscription/status" \
          -H "Authorization: Bearer $TOKEN")
        echo "$STATUS_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$STATUS_RESPONSE"
        echo ""
        
        echo "2.3 测试下载次数检查..."
        CREDITS_RESPONSE=$(curl -s -X GET "$BASE_URL/api/credits/check" \
          -H "Authorization: Bearer $TOKEN")
        echo "$CREDITS_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$CREDITS_RESPONSE"
        echo ""
        
        echo "2.4 测试白名单管理（需要 ADMIN_TOKEN）..."
        ADMIN_TOKEN="${ADMIN_TOKEN:-test_admin_token_12345}"
        
        echo "  添加用户到白名单..."
        WHITELIST_ADD=$(curl -s -X POST "$BASE_URL/api/admin/whitelist/add" \
          -H "Authorization: Bearer $ADMIN_TOKEN" \
          -H "Content-Type: application/x-www-form-urlencoded" \
          -d "user_id=$USER_ID&reason=API测试用户")
        echo "$WHITELIST_ADD" | python3 -m json.tool 2>/dev/null || echo "$WHITELIST_ADD"
        echo ""
        
        echo "  检查用户是否在白名单中..."
        WHITELIST_CHECK=$(curl -s -X GET "$BASE_URL/api/admin/whitelist/check/$USER_ID" \
          -H "Authorization: Bearer $ADMIN_TOKEN")
        echo "$WHITELIST_CHECK" | python3 -m json.tool 2>/dev/null || echo "$WHITELIST_CHECK"
        echo ""
        
        echo "  再次查询订阅状态（应显示在白名单中）..."
        STATUS_WHITELIST=$(curl -s -X GET "$BASE_URL/api/subscription/status" \
          -H "Authorization: Bearer $TOKEN")
        echo "$STATUS_WHITELIST" | python3 -m json.tool 2>/dev/null || echo "$STATUS_WHITELIST"
        echo ""
        
        echo "  删除白名单用户..."
        WHITELIST_DELETE=$(curl -s -X DELETE "$BASE_URL/api/admin/whitelist/$USER_ID" \
          -H "Authorization: Bearer $ADMIN_TOKEN")
        echo "$WHITELIST_DELETE" | python3 -m json.tool 2>/dev/null || echo "$WHITELIST_DELETE"
        echo ""
    else
        echo -e "${RED}❌ 用户注册失败或响应格式不正确${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  订阅系统未启用，跳过完整功能测试${NC}"
fi

echo -e "${BLUE}==========================================${NC}"
echo -e "${BLUE}测试完成${NC}"
echo -e "${BLUE}==========================================${NC}"

