#!/bin/bash
# 快速测试后端服务

cd "$(dirname "$0")"

echo "🔍 检查后端服务状态..."
echo ""

# 检查端口占用
if lsof -i :8000 > /dev/null 2>&1; then
    echo "⚠️  端口8000已被占用"
    lsof -i :8000
    echo ""
    echo "请先运行: ./stop_server.sh"
    exit 1
fi

echo "✅ 端口8000可用"
echo ""
echo "🚀 启动测试服务（5秒后自动停止）..."
echo ""

# 后台启动服务
python3 -m uvicorn main:app --host 127.0.0.1 --port 8000 > /tmp/beatsync_backend_test.log 2>&1 &
SERVER_PID=$!

# 等待服务启动
sleep 3

# 测试连接
echo "📡 测试服务连接..."
if curl -s http://127.0.0.1:8000/api/health > /dev/null; then
    echo "✅ 后端服务正常响应！"
    echo ""
    echo "服务地址: http://127.0.0.1:8000"
    echo "API文档: http://127.0.0.1:8000/docs"
    echo ""
    echo "⚠️  这是测试服务，5秒后自动停止"
    echo "   如需持续运行，请使用: ./start_server.sh"
    sleep 5
    kill $SERVER_PID 2>/dev/null
    echo "✅ 测试服务已停止"
else
    echo "❌ 后端服务无法响应"
    echo ""
    echo "查看日志:"
    cat /tmp/beatsync_backend_test.log
    kill $SERVER_PID 2>/dev/null
    exit 1
fi

