#!/bin/bash
# 诊断订阅 API 端点 404 问题

echo "=========================================="
echo "诊断订阅 API 端点问题"
echo "=========================================="
echo ""

# 1. 检查代码是否存在端点定义
echo "=== 1. 检查代码中的端点定义 ==="
if grep -q "@app.get(\"/api/subscription/products\")" /opt/beatsync/web_service/backend/main.py; then
    echo "✅ 端点定义存在于代码中"
    echo "位置："
    grep -n "@app.get(\"/api/subscription/products\")" /opt/beatsync/web_service/backend/main.py
else
    echo "❌ 端点定义不存在于代码中！"
    echo "请检查代码是否已更新"
fi
echo ""

# 2. 检查端点是否在条件块外
echo "=== 2. 检查端点是否在条件块外 ==="
LINE_NUM=$(grep -n "@app.get(\"/api/subscription/products\")" /opt/beatsync/web_service/backend/main.py | cut -d: -f1)
if [ -n "$LINE_NUM" ]; then
    # 检查前面是否有 if SUBSCRIPTION_AVAILABLE
    BEFORE_LINES=$(sed -n "1,$((LINE_NUM-1))p" /opt/beatsync/web_service/backend/main.py | grep -c "if SUBSCRIPTION_AVAILABLE:" || echo "0")
    if [ "$BEFORE_LINES" -eq 0 ]; then
        echo "✅ 端点在条件块外（正确）"
    else
        echo "⚠️  端点可能在条件块内，检查前面的代码："
        sed -n "$((LINE_NUM-10)),$LINE_NUM p" /opt/beatsync/web_service/backend/main.py
    fi
fi
echo ""

# 3. 检查 Python 语法
echo "=== 3. 检查 Python 语法 ==="
if python3 -m py_compile /opt/beatsync/web_service/backend/main.py 2>&1; then
    echo "✅ Python 语法正确"
else
    echo "❌ Python 语法错误！"
    python3 -m py_compile /opt/beatsync/web_service/backend/main.py 2>&1
fi
echo ""

# 4. 检查服务状态
echo "=== 4. 检查服务状态 ==="
if systemctl is-active --quiet beatsync; then
    echo "✅ 服务正在运行"
    systemctl status beatsync | head -10
else
    echo "❌ 服务未运行！"
    systemctl status beatsync | head -10
fi
echo ""

# 5. 检查服务日志（最近错误）
echo "=== 5. 检查服务日志（最近错误） ==="
ERRORS=$(sudo journalctl -u beatsync -n 50 --no-pager | grep -i "error\|exception\|traceback" | tail -5)
if [ -n "$ERRORS" ]; then
    echo "⚠️  发现错误日志："
    echo "$ERRORS"
else
    echo "✅ 没有发现错误日志"
fi
echo ""

# 6. 直接测试后端服务（绕过 Nginx）
echo "=== 6. 直接测试后端服务（端口 8000） ==="
RESPONSE=$(curl -s -w "\nHTTP_CODE:%{http_code}" http://127.0.0.1:8000/api/subscription/products 2>&1)
HTTP_CODE=$(echo "$RESPONSE" | grep "HTTP_CODE:" | cut -d: -f2)
BODY=$(echo "$RESPONSE" | grep -v "HTTP_CODE:")

if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ 后端服务正常，返回 200"
    echo "响应内容："
    echo "$BODY" | head -10
elif [ "$HTTP_CODE" = "404" ]; then
    echo "❌ 后端服务返回 404（端点未注册）"
    echo "响应内容："
    echo "$BODY"
else
    echo "⚠️  后端服务返回 $HTTP_CODE"
    echo "响应内容："
    echo "$BODY" | head -10
fi
echo ""

# 7. 通过 Nginx 测试
echo "=== 7. 通过 Nginx 测试 ==="
NGINX_RESPONSE=$(curl -s -w "\nHTTP_CODE:%{http_code}" https://beatsync.site/api/subscription/products 2>&1)
NGINX_HTTP_CODE=$(echo "$NGINX_RESPONSE" | grep "HTTP_CODE:" | cut -d: -f2)
NGINX_BODY=$(echo "$NGINX_RESPONSE" | grep -v "HTTP_CODE:")

if [ "$NGINX_HTTP_CODE" = "200" ]; then
    echo "✅ 通过 Nginx 访问正常，返回 200"
elif [ "$NGINX_HTTP_CODE" = "404" ]; then
    echo "❌ 通过 Nginx 访问返回 404"
    if [ "$HTTP_CODE" = "200" ]; then
        echo "⚠️  后端正常，但 Nginx 返回 404，可能是 Nginx 配置问题"
    else
        echo "⚠️  后端也返回 404，问题在后端代码"
    fi
else
    echo "⚠️  通过 Nginx 访问返回 $NGINX_HTTP_CODE"
fi
echo ""

# 8. 检查 FastAPI 路由（如果可能）
echo "=== 8. 检查 FastAPI 路由注册 ==="
cat > /tmp/check_routes.py << 'EOF'
import sys
sys.path.insert(0, '/opt/beatsync/web_service/backend')
try:
    from main import app
    routes = [route for route in app.routes if hasattr(route, 'path') and 'subscription' in route.path]
    if routes:
        print("✅ 找到订阅相关路由：")
        for route in routes:
            methods = getattr(route, 'methods', set())
            print(f"  {methods}: {route.path}")
    else:
        print("❌ 未找到订阅相关路由")
        print("所有路由：")
        all_routes = [route for route in app.routes if hasattr(route, 'path')]
        for route in all_routes[:20]:  # 只显示前20个
            methods = getattr(route, 'methods', set())
            print(f"  {methods}: {route.path}")
except Exception as e:
    print(f"❌ 导入失败: {e}")
    import traceback
    traceback.print_exc()
EOF

python3 /tmp/check_routes.py 2>&1
echo ""

# 9. 总结
echo "=========================================="
echo "诊断总结"
echo "=========================================="
echo ""
echo "如果后端直接访问返回 404："
echo "  → 问题在后端代码，端点未正确注册"
echo ""
echo "如果后端直接访问正常，但通过 Nginx 返回 404："
echo "  → 问题在 Nginx 配置"
echo ""
echo "如果两者都返回 404："
echo "  → 检查代码是否正确更新，服务是否正确重启"
echo ""



#!/bin/bash
# 诊断订阅 API 端点 404 问题

echo "=========================================="
echo "诊断订阅 API 端点问题"
echo "=========================================="
echo ""

# 1. 检查代码是否存在端点定义
echo "=== 1. 检查代码中的端点定义 ==="
if grep -q "@app.get(\"/api/subscription/products\")" /opt/beatsync/web_service/backend/main.py; then
    echo "✅ 端点定义存在于代码中"
    echo "位置："
    grep -n "@app.get(\"/api/subscription/products\")" /opt/beatsync/web_service/backend/main.py
else
    echo "❌ 端点定义不存在于代码中！"
    echo "请检查代码是否已更新"
fi
echo ""

# 2. 检查端点是否在条件块外
echo "=== 2. 检查端点是否在条件块外 ==="
LINE_NUM=$(grep -n "@app.get(\"/api/subscription/products\")" /opt/beatsync/web_service/backend/main.py | cut -d: -f1)
if [ -n "$LINE_NUM" ]; then
    # 检查前面是否有 if SUBSCRIPTION_AVAILABLE
    BEFORE_LINES=$(sed -n "1,$((LINE_NUM-1))p" /opt/beatsync/web_service/backend/main.py | grep -c "if SUBSCRIPTION_AVAILABLE:" || echo "0")
    if [ "$BEFORE_LINES" -eq 0 ]; then
        echo "✅ 端点在条件块外（正确）"
    else
        echo "⚠️  端点可能在条件块内，检查前面的代码："
        sed -n "$((LINE_NUM-10)),$LINE_NUM p" /opt/beatsync/web_service/backend/main.py
    fi
fi
echo ""

# 3. 检查 Python 语法
echo "=== 3. 检查 Python 语法 ==="
if python3 -m py_compile /opt/beatsync/web_service/backend/main.py 2>&1; then
    echo "✅ Python 语法正确"
else
    echo "❌ Python 语法错误！"
    python3 -m py_compile /opt/beatsync/web_service/backend/main.py 2>&1
fi
echo ""

# 4. 检查服务状态
echo "=== 4. 检查服务状态 ==="
if systemctl is-active --quiet beatsync; then
    echo "✅ 服务正在运行"
    systemctl status beatsync | head -10
else
    echo "❌ 服务未运行！"
    systemctl status beatsync | head -10
fi
echo ""

# 5. 检查服务日志（最近错误）
echo "=== 5. 检查服务日志（最近错误） ==="
ERRORS=$(sudo journalctl -u beatsync -n 50 --no-pager | grep -i "error\|exception\|traceback" | tail -5)
if [ -n "$ERRORS" ]; then
    echo "⚠️  发现错误日志："
    echo "$ERRORS"
else
    echo "✅ 没有发现错误日志"
fi
echo ""

# 6. 直接测试后端服务（绕过 Nginx）
echo "=== 6. 直接测试后端服务（端口 8000） ==="
RESPONSE=$(curl -s -w "\nHTTP_CODE:%{http_code}" http://127.0.0.1:8000/api/subscription/products 2>&1)
HTTP_CODE=$(echo "$RESPONSE" | grep "HTTP_CODE:" | cut -d: -f2)
BODY=$(echo "$RESPONSE" | grep -v "HTTP_CODE:")

if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ 后端服务正常，返回 200"
    echo "响应内容："
    echo "$BODY" | head -10
elif [ "$HTTP_CODE" = "404" ]; then
    echo "❌ 后端服务返回 404（端点未注册）"
    echo "响应内容："
    echo "$BODY"
else
    echo "⚠️  后端服务返回 $HTTP_CODE"
    echo "响应内容："
    echo "$BODY" | head -10
fi
echo ""

# 7. 通过 Nginx 测试
echo "=== 7. 通过 Nginx 测试 ==="
NGINX_RESPONSE=$(curl -s -w "\nHTTP_CODE:%{http_code}" https://beatsync.site/api/subscription/products 2>&1)
NGINX_HTTP_CODE=$(echo "$NGINX_RESPONSE" | grep "HTTP_CODE:" | cut -d: -f2)
NGINX_BODY=$(echo "$NGINX_RESPONSE" | grep -v "HTTP_CODE:")

if [ "$NGINX_HTTP_CODE" = "200" ]; then
    echo "✅ 通过 Nginx 访问正常，返回 200"
elif [ "$NGINX_HTTP_CODE" = "404" ]; then
    echo "❌ 通过 Nginx 访问返回 404"
    if [ "$HTTP_CODE" = "200" ]; then
        echo "⚠️  后端正常，但 Nginx 返回 404，可能是 Nginx 配置问题"
    else
        echo "⚠️  后端也返回 404，问题在后端代码"
    fi
else
    echo "⚠️  通过 Nginx 访问返回 $NGINX_HTTP_CODE"
fi
echo ""

# 8. 检查 FastAPI 路由（如果可能）
echo "=== 8. 检查 FastAPI 路由注册 ==="
cat > /tmp/check_routes.py << 'EOF'
import sys
sys.path.insert(0, '/opt/beatsync/web_service/backend')
try:
    from main import app
    routes = [route for route in app.routes if hasattr(route, 'path') and 'subscription' in route.path]
    if routes:
        print("✅ 找到订阅相关路由：")
        for route in routes:
            methods = getattr(route, 'methods', set())
            print(f"  {methods}: {route.path}")
    else:
        print("❌ 未找到订阅相关路由")
        print("所有路由：")
        all_routes = [route for route in app.routes if hasattr(route, 'path')]
        for route in all_routes[:20]:  # 只显示前20个
            methods = getattr(route, 'methods', set())
            print(f"  {methods}: {route.path}")
except Exception as e:
    print(f"❌ 导入失败: {e}")
    import traceback
    traceback.print_exc()
EOF

python3 /tmp/check_routes.py 2>&1
echo ""

# 9. 总结
echo "=========================================="
echo "诊断总结"
echo "=========================================="
echo ""
echo "如果后端直接访问返回 404："
echo "  → 问题在后端代码，端点未正确注册"
echo ""
echo "如果后端直接访问正常，但通过 Nginx 返回 404："
echo "  → 问题在 Nginx 配置"
echo ""
echo "如果两者都返回 404："
echo "  → 检查代码是否正确更新，服务是否正确重启"
echo ""



#!/bin/bash
# 诊断订阅 API 端点 404 问题

echo "=========================================="
echo "诊断订阅 API 端点问题"
echo "=========================================="
echo ""

# 1. 检查代码是否存在端点定义
echo "=== 1. 检查代码中的端点定义 ==="
if grep -q "@app.get(\"/api/subscription/products\")" /opt/beatsync/web_service/backend/main.py; then
    echo "✅ 端点定义存在于代码中"
    echo "位置："
    grep -n "@app.get(\"/api/subscription/products\")" /opt/beatsync/web_service/backend/main.py
else
    echo "❌ 端点定义不存在于代码中！"
    echo "请检查代码是否已更新"
fi
echo ""

# 2. 检查端点是否在条件块外
echo "=== 2. 检查端点是否在条件块外 ==="
LINE_NUM=$(grep -n "@app.get(\"/api/subscription/products\")" /opt/beatsync/web_service/backend/main.py | cut -d: -f1)
if [ -n "$LINE_NUM" ]; then
    # 检查前面是否有 if SUBSCRIPTION_AVAILABLE
    BEFORE_LINES=$(sed -n "1,$((LINE_NUM-1))p" /opt/beatsync/web_service/backend/main.py | grep -c "if SUBSCRIPTION_AVAILABLE:" || echo "0")
    if [ "$BEFORE_LINES" -eq 0 ]; then
        echo "✅ 端点在条件块外（正确）"
    else
        echo "⚠️  端点可能在条件块内，检查前面的代码："
        sed -n "$((LINE_NUM-10)),$LINE_NUM p" /opt/beatsync/web_service/backend/main.py
    fi
fi
echo ""

# 3. 检查 Python 语法
echo "=== 3. 检查 Python 语法 ==="
if python3 -m py_compile /opt/beatsync/web_service/backend/main.py 2>&1; then
    echo "✅ Python 语法正确"
else
    echo "❌ Python 语法错误！"
    python3 -m py_compile /opt/beatsync/web_service/backend/main.py 2>&1
fi
echo ""

# 4. 检查服务状态
echo "=== 4. 检查服务状态 ==="
if systemctl is-active --quiet beatsync; then
    echo "✅ 服务正在运行"
    systemctl status beatsync | head -10
else
    echo "❌ 服务未运行！"
    systemctl status beatsync | head -10
fi
echo ""

# 5. 检查服务日志（最近错误）
echo "=== 5. 检查服务日志（最近错误） ==="
ERRORS=$(sudo journalctl -u beatsync -n 50 --no-pager | grep -i "error\|exception\|traceback" | tail -5)
if [ -n "$ERRORS" ]; then
    echo "⚠️  发现错误日志："
    echo "$ERRORS"
else
    echo "✅ 没有发现错误日志"
fi
echo ""

# 6. 直接测试后端服务（绕过 Nginx）
echo "=== 6. 直接测试后端服务（端口 8000） ==="
RESPONSE=$(curl -s -w "\nHTTP_CODE:%{http_code}" http://127.0.0.1:8000/api/subscription/products 2>&1)
HTTP_CODE=$(echo "$RESPONSE" | grep "HTTP_CODE:" | cut -d: -f2)
BODY=$(echo "$RESPONSE" | grep -v "HTTP_CODE:")

if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ 后端服务正常，返回 200"
    echo "响应内容："
    echo "$BODY" | head -10
elif [ "$HTTP_CODE" = "404" ]; then
    echo "❌ 后端服务返回 404（端点未注册）"
    echo "响应内容："
    echo "$BODY"
else
    echo "⚠️  后端服务返回 $HTTP_CODE"
    echo "响应内容："
    echo "$BODY" | head -10
fi
echo ""

# 7. 通过 Nginx 测试
echo "=== 7. 通过 Nginx 测试 ==="
NGINX_RESPONSE=$(curl -s -w "\nHTTP_CODE:%{http_code}" https://beatsync.site/api/subscription/products 2>&1)
NGINX_HTTP_CODE=$(echo "$NGINX_RESPONSE" | grep "HTTP_CODE:" | cut -d: -f2)
NGINX_BODY=$(echo "$NGINX_RESPONSE" | grep -v "HTTP_CODE:")

if [ "$NGINX_HTTP_CODE" = "200" ]; then
    echo "✅ 通过 Nginx 访问正常，返回 200"
elif [ "$NGINX_HTTP_CODE" = "404" ]; then
    echo "❌ 通过 Nginx 访问返回 404"
    if [ "$HTTP_CODE" = "200" ]; then
        echo "⚠️  后端正常，但 Nginx 返回 404，可能是 Nginx 配置问题"
    else
        echo "⚠️  后端也返回 404，问题在后端代码"
    fi
else
    echo "⚠️  通过 Nginx 访问返回 $NGINX_HTTP_CODE"
fi
echo ""

# 8. 检查 FastAPI 路由（如果可能）
echo "=== 8. 检查 FastAPI 路由注册 ==="
cat > /tmp/check_routes.py << 'EOF'
import sys
sys.path.insert(0, '/opt/beatsync/web_service/backend')
try:
    from main import app
    routes = [route for route in app.routes if hasattr(route, 'path') and 'subscription' in route.path]
    if routes:
        print("✅ 找到订阅相关路由：")
        for route in routes:
            methods = getattr(route, 'methods', set())
            print(f"  {methods}: {route.path}")
    else:
        print("❌ 未找到订阅相关路由")
        print("所有路由：")
        all_routes = [route for route in app.routes if hasattr(route, 'path')]
        for route in all_routes[:20]:  # 只显示前20个
            methods = getattr(route, 'methods', set())
            print(f"  {methods}: {route.path}")
except Exception as e:
    print(f"❌ 导入失败: {e}")
    import traceback
    traceback.print_exc()
EOF

python3 /tmp/check_routes.py 2>&1
echo ""

# 9. 总结
echo "=========================================="
echo "诊断总结"
echo "=========================================="
echo ""
echo "如果后端直接访问返回 404："
echo "  → 问题在后端代码，端点未正确注册"
echo ""
echo "如果后端直接访问正常，但通过 Nginx 返回 404："
echo "  → 问题在 Nginx 配置"
echo ""
echo "如果两者都返回 404："
echo "  → 检查代码是否正确更新，服务是否正确重启"
echo ""














