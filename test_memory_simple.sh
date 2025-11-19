#!/bin/bash
# 简单的内存测试脚本

echo "=========================================="
echo "内存使用测试 - BeatSync并行处理器"
echo "=========================================="
echo ""

# 检查输入文件
DANCE_VIDEO="input_allcases_lowp/killitgirl_full/dance.mp4"
BGM_VIDEO="input_allcases_lowp/killitgirl_full/bgm.mp4"
OUTPUT_DIR="test_memory_verification"
SAMPLE_NAME="killitgirl_memory_test"

if [ ! -f "$DANCE_VIDEO" ]; then
    echo "错误: 找不到dance视频: $DANCE_VIDEO"
    exit 1
fi

if [ ! -f "$BGM_VIDEO" ]; then
    echo "错误: 找不到bgm视频: $BGM_VIDEO"
    exit 1
fi

echo "测试样本: $SAMPLE_NAME"
echo "输入文件:"
echo "  dance: $DANCE_VIDEO"
echo "  bgm: $BGM_VIDEO"
echo "输出目录: $OUTPUT_DIR"
echo ""
echo "=========================================="
echo "开始处理..."
echo "=========================================="
echo ""
echo "提示: 请在另一个终端窗口运行以下命令监控内存:"
echo "  watch -n 2 'ps aux | grep python | grep -v grep | sort -k4 -rn | head -5'"
echo ""
echo "或者使用Activity Monitor监控Python进程的内存使用"
echo ""
echo "按回车键开始处理..."
read

# 记录开始时间
START_TIME=$(date +%s)

# 运行并行处理器
python3 beatsync_parallel_processor.py \
    --dance "$DANCE_VIDEO" \
    --bgm "$BGM_VIDEO" \
    --output-dir "$OUTPUT_DIR" \
    --sample-name "$SAMPLE_NAME" 2>&1 | tee memory_test_output.log

# 记录结束时间
END_TIME=$(date +%s)
ELAPSED=$((END_TIME - START_TIME))

echo ""
echo "=========================================="
echo "处理完成"
echo "=========================================="
echo "处理时间: ${ELAPSED} 秒"
echo ""
echo "检查Python进程内存使用:"
ps aux | grep python | grep -v grep | sort -k4 -rn | head -5 | awk '{printf "PID: %-8s Memory: %8s (%.2f GB)  Command: %s\n", $2, $6, $6/1024/1024, $11" "$12" "$13" "$14" "$15}'

echo ""
echo "如果看到大量内存占用，可能是:"
echo "1. 进程仍在运行（检查PID）"
echo "2. 操作系统尚未回收内存（等待几秒后再次检查）"
echo "3. 其他Python进程占用内存"



