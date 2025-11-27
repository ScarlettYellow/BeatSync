#!/bin/bash
# 启动服务并等待就绪

cd "$(dirname "$0")"

echo "🚀 启动后端服务..."
echo "工作目录: $(pwd)"
echo ""

# 后台启动服务
python3 -m uvicorn main:app --host 127.0.0.1 --port 8000 > /tmp/beatsync_backend.log 2>&1 &
SERVER_PID=$!

echo "服务进程 PID: $SERVER_PID"
echo "等待服务启动..."

# 等待服务启动（最多30秒）
for i in {1..30}; do
    sleep 1
    if curl -s http://127.0.0.1:8000/api/health > /dev/null 2>&1; then
        echo ""
        echo "✅ 服务已启动并响应！"
        echo "服务地址: http://127.0.0.1:8000"
        echo "API文档: http://127.0.0.1:8000/docs"
        echo ""
        echo "按 Ctrl+C 停止服务"
        echo ""
        echo "查看日志: tail -f /tmp/beatsync_backend.log"
        echo ""
        
        # 显示服务日志
        tail -f /tmp/beatsync_backend.log &
        TAIL_PID=$!
        
        # 等待用户中断
        wait $SERVER_PID
        
        # 停止tail
        kill $TAIL_PID 2>/dev/null
        exit 0
    fi
    echo -n "."
done

echo ""
echo "❌ 服务启动超时（30秒）"
echo "查看日志:"
cat /tmp/beatsync_backend.log
kill $SERVER_PID 2>/dev/null
exit 1

