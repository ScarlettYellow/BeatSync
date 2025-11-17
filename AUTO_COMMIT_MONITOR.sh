#!/bin/bash
# 文件监控自动提示脚本
# 监控重要文件改动，检测到改动时提示用户

# 配置
MONITOR_INTERVAL=30  # 检查间隔（秒）
IMPORTANT_FILES="beatsync_fine_cut_modular.py beatsync_badcase_fix_trim_v2.py beatsync_parallel_processor.py beatsync_utils.py README.md PROJECT_STATUS.md EXCEPTION_HANDLING_GUIDE.md"
PID_FILE=".git_monitor.pid"
LOG_FILE=".git_monitor.log"

# 检查是否已在运行
if [ -f "$PID_FILE" ]; then
    OLD_PID=$(cat "$PID_FILE")
    if ps -p "$OLD_PID" > /dev/null 2>&1; then
        echo "⚠️  监控已在运行 (PID: $OLD_PID)"
        echo "   停止监控: kill $OLD_PID 或 ./stop_monitor.sh"
        exit 1
    else
        # PID文件存在但进程不存在，清理
        rm -f "$PID_FILE"
    fi
fi

# 获取文件状态（修改时间和大小）
get_file_state() {
    for file in $IMPORTANT_FILES; do
        if [ -f "$file" ]; then
            # macOS使用stat -f，Linux使用stat -c
            stat -f "%m %z %N" "$file" 2>/dev/null || stat -c "%Y %s %n" "$file" 2>/dev/null
        fi
    done
}

# 检查Git改动
check_git_changes() {
    if ! git diff --quiet 2>/dev/null || ! git diff --cached --quiet 2>/dev/null; then
        return 0  # 有改动
    else
        return 1  # 无改动
    fi
}

# 显示提示
show_notification() {
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    local changed_files=$(git status --short 2>/dev/null | head -5 | sed 's/^/    /')
    
    echo ""
    echo "========================================"
    echo "📝 [$timestamp] 检测到文件改动"
    echo "========================================"
    echo ""
    echo "改动的文件："
    echo "$changed_files"
    if [ $(git status --short 2>/dev/null | wc -l) -gt 5 ]; then
        echo "    ... 还有更多文件"
    fi
    echo ""
    echo "💡 提示：可以运行以下命令提交："
    echo "   ./ac"
    echo ""
    echo "========================================"
    echo ""
    
    # 记录到日志
    echo "[$timestamp] 检测到改动，提示用户提交" >> "$LOG_FILE"
}

# 主监控循环
monitor_loop() {
    echo "开始监控文件改动..."
    echo "监控间隔: ${MONITOR_INTERVAL}秒"
    echo "监控文件: $IMPORTANT_FILES"
    echo "日志文件: $LOG_FILE"
    echo ""
    echo "按 Ctrl+C 停止监控"
    echo ""
    
    INITIAL_STATE=$(get_file_state)
    LAST_NOTIFY_TIME=0
    NOTIFY_COOLDOWN=300  # 5分钟内不重复提示
    
    while true; do
        sleep $MONITOR_INTERVAL
        
        CURRENT_STATE=$(get_file_state)
        CURRENT_TIME=$(date +%s)
        
        # 检查文件状态是否改变
        if [ "$INITIAL_STATE" != "$CURRENT_STATE" ]; then
            # 检查Git改动（避免提示未保存的改动）
            if check_git_changes; then
                # 检查冷却时间（避免频繁提示）
                if [ $((CURRENT_TIME - LAST_NOTIFY_TIME)) -ge $NOTIFY_COOLDOWN ]; then
                    show_notification
                    LAST_NOTIFY_TIME=$CURRENT_TIME
                fi
            fi
            
            # 更新初始状态
            INITIAL_STATE=$CURRENT_STATE
        fi
    done
}

# 启动监控
start_monitor() {
    if [ "$1" = "--background" ] || [ "$1" = "-b" ]; then
        # 后台运行
        monitor_loop > "$LOG_FILE" 2>&1 &
        MONITOR_PID=$!
        echo $MONITOR_PID > "$PID_FILE"
        echo "✅ 监控已在后台启动 (PID: $MONITOR_PID)"
        echo "   查看日志: tail -f $LOG_FILE"
        echo "   停止监控: ./stop_monitor.sh 或 kill $MONITOR_PID"
    else
        # 前台运行
        monitor_loop
    fi
}

# 清理函数
cleanup() {
    echo ""
    echo "停止监控..."
    rm -f "$PID_FILE"
    exit 0
}

trap cleanup SIGINT SIGTERM

# 启动
start_monitor "$@"
