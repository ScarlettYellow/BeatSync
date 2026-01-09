#!/bin/bash
# 订阅系统 API 测试脚本

BASE_URL="http://localhost:8000"
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "=========================================="
echo "订阅系统 API 测试"
echo "=========================================="
echo ""

# 检查服务是否运行
echo "1. 检查后端服务状态..."
if curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/api/health" | grep -q "200"; then
    echo -e "${GREEN}✅ 后端服务正在运行${NC}"
else
    echo -e "${RED}❌ 后端服务未运行，请先启动服务${NC}"
    echo "启动命令: cd web_service/backend && python3 main.py"
    exit 1
fi
echo ""

# 测试场景 1: 订阅系统关闭（向后兼容测试）
echo "=========================================="
echo "测试场景 1: 订阅系统关闭（向后兼容）"
echo "=========================================="
echo ""

echo "1.1 测试健康检查接口..."
HEALTH_RESPONSE=$(curl -s "$BASE_URL/api/health")
echo "响应: $HEALTH_RESPONSE"
echo ""

echo "1.2 测试订阅状态查询（应返回未启用）..."
STATUS_RESPONSE=$(curl -s "$BASE_URL/api/subscription/status")
echo "响应: $STATUS_RESPONSE"
if echo "$STATUS_RESPONSE" | grep -q "订阅系统未启用\|error"; then
    echo -e "${GREEN}✅ 正确：订阅系统未启用${NC}"
else
    echo -e "${YELLOW}⚠️  注意：可能需要启用订阅系统才能看到完整响应${NC}"
fi
echo ""

echo "1.3 测试用户注册（应返回未启用）..."
REGISTER_RESPONSE=$(curl -s -X POST "$BASE_URL/api/auth/register" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "device_id=test_device_001")
echo "响应: $REGISTER_RESPONSE"
echo ""

# 测试场景 2: 启用订阅系统
echo "=========================================="
echo "测试场景 2: 启用订阅系统"
echo "=========================================="
echo -e "${YELLOW}注意：需要设置环境变量启用订阅系统${NC}"
echo "设置命令:"
echo "  export SUBSCRIPTION_ENABLED=true"
echo "  export ADMIN_TOKEN=test_admin_token_12345"
echo "  export JWT_SECRET_KEY=test_jwt_secret_key_12345"
echo "然后重启服务"
echo ""

# 如果设置了环境变量，进行完整测试
if [ "$SUBSCRIPTION_ENABLED" = "true" ]; then
    echo -e "${GREEN}检测到订阅系统已启用，进行完整测试...${NC}"
    echo ""
    
    echo "2.1 测试用户注册..."
    REGISTER_RESPONSE=$(curl -s -X POST "$BASE_URL/api/auth/register" \
      -H "Content-Type: application/x-www-form-urlencoded" \
      -d "device_id=test_device_$(date +%s)")
    echo "响应: $REGISTER_RESPONSE"
    
    # 提取 token 和 user_id
    TOKEN=$(echo "$REGISTER_RESPONSE" | grep -o '"token":"[^"]*' | cut -d'"' -f4)
    USER_ID=$(echo "$REGISTER_RESPONSE" | grep -o '"user_id":"[^"]*' | cut -d'"' -f4)
    
    if [ -n "$TOKEN" ] && [ -n "$USER_ID" ]; then
        echo -e "${GREEN}✅ 用户注册成功${NC}"
        echo "  User ID: $USER_ID"
        echo "  Token: ${TOKEN:0:20}..."
        echo ""
        
        echo "2.2 测试订阅状态查询..."
        STATUS_RESPONSE=$(curl -s -X GET "$BASE_URL/api/subscription/status" \
          -H "Authorization: Bearer $TOKEN")
        echo "响应: $STATUS_RESPONSE"
        echo ""
        
        echo "2.3 测试下载次数检查..."
        CREDITS_RESPONSE=$(curl -s -X GET "$BASE_URL/api/credits/check" \
          -H "Authorization: Bearer $TOKEN")
        echo "响应: $CREDITS_RESPONSE"
        echo ""
        
        if [ -n "$ADMIN_TOKEN" ]; then
            echo "2.4 测试白名单管理..."
            
            echo "  添加用户到白名单..."
            WHITELIST_ADD=$(curl -s -X POST "$BASE_URL/api/admin/whitelist/add" \
              -H "Authorization: Bearer $ADMIN_TOKEN" \
              -H "Content-Type: application/x-www-form-urlencoded" \
              -d "user_id=$USER_ID&reason=测试用户")
            echo "  响应: $WHITELIST_ADD"
            echo ""
            
            echo "  检查用户是否在白名单中..."
            WHITELIST_CHECK=$(curl -s -X GET "$BASE_URL/api/admin/whitelist/check/$USER_ID" \
              -H "Authorization: Bearer $ADMIN_TOKEN")
            echo "  响应: $WHITELIST_CHECK"
            echo ""
            
            echo "  获取白名单列表..."
            WHITELIST_LIST=$(curl -s -X GET "$BASE_URL/api/admin/whitelist?page=1&limit=10" \
              -H "Authorization: Bearer $ADMIN_TOKEN")
            echo "  响应: $WHITELIST_LIST"
            echo ""
            
            echo "  删除白名单用户..."
            WHITELIST_DELETE=$(curl -s -X DELETE "$BASE_URL/api/admin/whitelist/$USER_ID" \
              -H "Authorization: Bearer $ADMIN_TOKEN")
            echo "  响应: $WHITELIST_DELETE"
            echo ""
        else
            echo -e "${YELLOW}⚠️  ADMIN_TOKEN 未设置，跳过白名单测试${NC}"
            echo ""
        fi
    else
        echo -e "${RED}❌ 用户注册失败或响应格式不正确${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  订阅系统未启用，跳过完整功能测试${NC}"
    echo "要启用订阅系统，请设置环境变量并重启服务"
fi

echo "=========================================="
echo "测试完成"
echo "=========================================="

