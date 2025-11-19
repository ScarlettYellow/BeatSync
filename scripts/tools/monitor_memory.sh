#!/bin/bash
# 内存监控脚本 - 监控Python进程的内存使用

echo "开始监控Python进程内存使用..."
echo "按 Ctrl+C 停止监控"
echo ""

# 获取当前Python进程的PID
PYTHON_PID=$(ps aux | grep "beatsync_parallel_processor.py" | grep -v grep | awk '{print $2}')

if [ -z "$PYTHON_PID" ]; then
    echo "未找到运行中的beatsync_parallel_processor.py进程"
    echo "请先运行程序，然后重新运行此监控脚本"
    exit 1
fi

echo "监控进程 PID: $PYTHON_PID"
echo "时间戳 | 内存使用(GB) | 内存使用(MB)"
echo "----------------------------------------"

# 持续监控
while kill -0 $PYTHON_PID 2>/dev/null; do
    MEMORY_KB=$(ps -o rss= -p $PYTHON_PID 2>/dev/null)
    if [ ! -z "$MEMORY_KB" ]; then
        MEMORY_MB=$((MEMORY_KB / 1024))
        MEMORY_GB=$(echo "scale=2; $MEMORY_MB / 1024" | bc)
        TIMESTAMP=$(date '+%H:%M:%S')
        printf "%s | %8.2f GB | %8d MB\n" "$TIMESTAMP" "$MEMORY_GB" "$MEMORY_MB"
    fi
    sleep 2
done

echo ""
echo "进程已结束，监控停止"



