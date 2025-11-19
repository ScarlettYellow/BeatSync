#!/bin/bash
# 停止BeatSync Web服务后端

echo "正在查找并停止运行在端口8000的服务..."

# 查找占用端口8000的进程
PID=$(lsof -ti :8000)

if [ -z "$PID" ]; then
    echo "✅ 端口8000未被占用，无需停止"
    exit 0
fi

echo "找到进程 PID: $PID"
echo "正在停止..."

# 停止进程
kill $PID

# 等待进程结束
sleep 2

# 检查是否成功停止
if lsof -i :8000 &> /dev/null; then
    echo "⚠️  进程仍在运行，强制停止..."
    kill -9 $PID
    sleep 1
fi

if lsof -i :8000 &> /dev/null; then
    echo "❌ 无法停止服务，请手动处理"
    exit 1
else
    echo "✅ 服务已停止"
fi

