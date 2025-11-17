#!/bin/bash
# 检查批量处理进度

LOG_FILE="outputs/batch_all_hd_samples_processing.log"
OUTPUT_DIR="outputs/batch_all_hd_samples"
REPORT_FILE="$OUTPUT_DIR/batch_processing_report.txt"

echo "=========================================="
echo "批量处理进度检查"
echo "=========================================="
echo ""

# 检查进程是否运行
if ps aux | grep -v grep | grep -q "batch_process_all_hd_samples"; then
    echo "状态: ✅ 正在运行"
    PID=$(ps aux | grep -v grep | grep "batch_process_all_hd_samples" | awk '{print $2}')
    echo "进程ID: $PID"
else
    echo "状态: ❌ 未运行（可能已完成或出错）"
fi

echo ""

# 检查已完成的样本数
if [ -d "$OUTPUT_DIR" ]; then
    COMPLETED=$(ls -d "$OUTPUT_DIR"/*/ 2>/dev/null | wc -l | tr -d ' ')
    echo "已完成的样本: $COMPLETED 个"
    
    # 检查输出视频数
    VIDEO_COUNT=$(find "$OUTPUT_DIR" -name "*.mp4" 2>/dev/null | wc -l | tr -d ' ')
    echo "输出视频文件: $VIDEO_COUNT 个"
else
    echo "输出目录尚未创建"
fi

echo ""

# 显示最近日志
if [ -f "$LOG_FILE" ]; then
    echo "最近日志（最后10行）:"
    echo "----------------------------------------"
    tail -10 "$LOG_FILE"
    echo ""
else
    echo "日志文件尚未生成"
fi

# 显示报告（如果存在）
if [ -f "$REPORT_FILE" ]; then
    echo "处理报告摘要:"
    echo "----------------------------------------"
    head -15 "$REPORT_FILE"
    echo ""
    echo "查看完整报告: cat $REPORT_FILE"
fi

echo ""
echo "=========================================="
echo "常用命令:"
echo "  实时查看日志: tail -f $LOG_FILE"
echo "  查看所有样本: ls -d $OUTPUT_DIR/*/"
echo "  查看完整报告: cat $REPORT_FILE"
echo "=========================================="

