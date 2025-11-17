#!/bin/bash
# 检查监控状态

# 获取项目根目录（脚本在scripts/git/目录下）
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
PID_FILE="$PROJECT_ROOT/.git_monitor.pid"
LOG_FILE="$PROJECT_ROOT/.git_monitor.log"

if [ ! -f "$PID_FILE" ]; then
    echo "状态: ❌ 未运行"
    exit 0
fi

PID=$(cat "$PID_FILE")

if ps -p "$PID" > /dev/null 2>&1; then
    echo "状态: ✅ 运行中 (PID: $PID)"
    echo ""
    echo "最近日志："
    if [ -f "$LOG_FILE" ]; then
        tail -5 "$LOG_FILE"
    else
        echo "  (暂无日志)"
    fi
    echo ""
    echo "停止监控: ./stop_monitor.sh"
else
    echo "状态: ❌ 进程不存在（PID文件可能过期）"
    rm -f "$PID_FILE"
fi

