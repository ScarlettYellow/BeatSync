#!/bin/bash
# 文件监控自动提交脚本
# 监控重要文件改动，自动检测并提示提交

# 配置
MONITOR_INTERVAL=60  # 检查间隔（秒）
IMPORTANT_FILES="beatsync_fine_cut_modular.py beatsync_badcase_fix_trim_v2.py beatsync_parallel_processor.py beatsync_utils.py README.md PROJECT_STATUS.md"
AUTO_COMMIT_ENABLED=false  # 是否完全自动提交（不询问）

echo "=========================================="
echo "文件监控自动提交"
echo "=========================================="
echo "监控间隔: ${MONITOR_INTERVAL}秒"
echo "监控文件: $IMPORTANT_FILES"
echo ""

# 获取初始状态
get_file_hashes() {
    for file in $IMPORTANT_FILES; do
        if [ -f "$file" ]; then
            stat -f "%m %z" "$file" 2>/dev/null || stat -c "%Y %s" "$file" 2>/dev/null
        fi
    done
}

INITIAL_STATE=$(get_file_hashes)

echo "开始监控... (按 Ctrl+C 停止)"
echo ""

while true; do
    sleep $MONITOR_INTERVAL
    
    CURRENT_STATE=$(get_file_hashes)
    
    if [ "$INITIAL_STATE" != "$CURRENT_STATE" ]; then
        echo ""
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] 检测到文件改动"
        
        # 检查是否有未提交的改动
        if ! git diff --quiet || ! git diff --cached --quiet; then
            echo "发现未提交的改动"
            git status --short | head -5
            
            if [ "$AUTO_COMMIT_ENABLED" = "true" ]; then
                echo "自动提交中..."
                ./auto_commit.sh --auto
            else
                echo ""
                echo "提示：检测到改动，可以运行以下命令提交："
                echo "  ./ac"
                echo ""
            fi
        fi
        
        # 更新初始状态
        INITIAL_STATE=$CURRENT_STATE
    fi
done

