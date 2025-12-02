#!/bin/bash
# 停止本地开发环境服务

echo "=========================================="
echo "BeatSync 本地开发环境停止脚本"
echo "=========================================="
echo ""

# 查找并停止后端服务（uvicorn）
echo "🔍 查找后端服务进程..."
BACKEND_PIDS=$(ps aux | grep "uvicorn main:app" | grep -v grep | awk '{print $2}')
if [ -n "$BACKEND_PIDS" ]; then
    echo "   找到后端进程: $BACKEND_PIDS"
    echo "   正在停止..."
    echo $BACKEND_PIDS | xargs kill 2>/dev/null
    sleep 1
    # 如果还在运行，强制停止
    REMAINING=$(ps aux | grep "uvicorn main:app" | grep -v grep | awk '{print $2}')
    if [ -n "$REMAINING" ]; then
        echo "   强制停止..."
        echo $REMAINING | xargs kill -9 2>/dev/null
    fi
    echo "   ✅ 后端服务已停止"
else
    echo "   ℹ️  未找到运行中的后端服务"
fi

# 查找并停止前端服务（http.server）
echo ""
echo "🔍 查找前端服务进程..."
FRONTEND_PIDS=$(ps aux | grep "http.server 8080" | grep -v grep | awk '{print $2}')
if [ -n "$FRONTEND_PIDS" ]; then
    echo "   找到前端进程: $FRONTEND_PIDS"
    echo "   正在停止..."
    echo $FRONTEND_PIDS | xargs kill 2>/dev/null
    sleep 1
    # 如果还在运行，强制停止
    REMAINING=$(ps aux | grep "http.server 8080" | grep -v grep | awk '{print $2}')
    if [ -n "$REMAINING" ]; then
        echo "   强制停止..."
        echo $REMAINING | xargs kill -9 2>/dev/null
    fi
    echo "   ✅ 前端服务已停止"
else
    echo "   ℹ️  未找到运行中的前端服务"
fi

# 检查端口占用
echo ""
echo "🔍 检查端口占用..."
if lsof -i :8000 >/dev/null 2>&1; then
    echo "   ⚠️  端口8000仍被占用"
    lsof -i :8000 | grep -v COMMAND
else
    echo "   ✅ 端口8000已释放"
fi

if lsof -i :8080 >/dev/null 2>&1; then
    echo "   ⚠️  端口8080仍被占用"
    lsof -i :8080 | grep -v COMMAND
else
    echo "   ✅ 端口8080已释放"
fi

echo ""
echo "=========================================="
echo "✅ 停止完成"
echo "=========================================="

