#!/bin/bash
# 修复端口占用并启动服务

cd "$(dirname "$0")"

echo "🔍 检查端口 8000 占用情况..."
echo ""

# 查找占用端口 8000 的进程
PID=$(lsof -ti :8000)

if [ -n "$PID" ]; then
    echo "⚠️  发现端口 8000 被占用"
    echo "   进程 PID: $PID"
    echo ""
    echo "正在停止进程..."
    kill -9 $PID 2>/dev/null
    sleep 1
    
    # 再次检查
    PID2=$(lsof -ti :8000)
    if [ -n "$PID2" ]; then
        echo "❌ 无法停止进程，请手动处理"
        echo "   运行: kill -9 $PID2"
        exit 1
    else
        echo "✅ 端口 8000 已释放"
    fi
else
    echo "✅ 端口 8000 可用"
fi

echo ""
echo "🚀 启动后端服务..."
echo ""

# 设置环境变量
export SUBSCRIPTION_ENABLED=true
export SUBSCRIPTION_DB_PATH=./subscription.db

# 启动服务
python3 main.py
