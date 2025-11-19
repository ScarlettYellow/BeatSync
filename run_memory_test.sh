#!/bin/bash
# 内存测试脚本 - 运行并行处理器并显示内存使用

echo "=========================================="
echo "BeatSync 内存使用测试"
echo "=========================================="
echo ""

# 测试参数
DANCE_VIDEO="input_allcases_lowp/killitgirl_full/dance.mp4"
BGM_VIDEO="input_allcases_lowp/killitgirl_full/bgm.mp4"
OUTPUT_DIR="test_memory_verification"
SAMPLE_NAME="killitgirl_memory_test"

# 检查输入文件
if [ ! -f "$DANCE_VIDEO" ]; then
    echo "❌ 错误: 找不到dance视频: $DANCE_VIDEO"
    exit 1
fi

if [ ! -f "$BGM_VIDEO" ]; then
    echo "❌ 错误: 找不到bgm视频: $BGM_VIDEO"
    exit 1
fi

echo "✅ 输入文件检查通过"
echo ""
echo "测试配置:"
echo "  样本名称: $SAMPLE_NAME"
echo "  dance视频: $DANCE_VIDEO"
echo "  bgm视频: $BGM_VIDEO"
echo "  输出目录: $OUTPUT_DIR"
echo ""

# 检查当前Python进程
echo "处理前的Python进程:"
PYTHON_BEFORE=$(ps aux | grep python | grep -v grep | wc -l | tr -d ' ')
echo "  当前Python进程数: $PYTHON_BEFORE"

if [ "$PYTHON_BEFORE" -gt 0 ]; then
    echo "  警告: 检测到Python进程正在运行"
    ps aux | grep python | grep -v grep | head -3
    echo ""
    read -p "是否继续? (y/n): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo ""
echo "=========================================="
echo "开始处理..."
echo "=========================================="
echo ""
echo "💡 提示: 请在Activity Monitor中监控Python进程的内存使用"
echo "   或者运行以下命令实时监控:"
echo "   watch -n 1 'ps aux | grep python | grep -v grep | sort -k4 -rn | head -3'"
echo ""

# 记录开始时间
START_TIME=$(date +%s)

# 运行并行处理器
echo "正在运行并行处理器..."
python3 beatsync_parallel_processor.py \
    --dance "$DANCE_VIDEO" \
    --bgm "$BGM_VIDEO" \
    --output-dir "$OUTPUT_DIR" \
    --sample-name "$SAMPLE_NAME"

EXIT_CODE=$?

# 记录结束时间
END_TIME=$(date +%s)
ELAPSED=$((END_TIME - START_TIME))

echo ""
echo "=========================================="
echo "处理完成"
echo "=========================================="
echo "处理时间: ${ELAPSED} 秒"
echo "退出代码: $EXIT_CODE"
echo ""

# 等待2秒，让系统回收内存
echo "等待2秒，让系统回收内存..."
sleep 2

# 检查处理后的Python进程
echo ""
echo "处理后的Python进程:"
PYTHON_AFTER=$(ps aux | grep python | grep -v grep | wc -l | tr -d ' ')
echo "  当前Python进程数: $PYTHON_AFTER"

if [ "$PYTHON_AFTER" -gt 0 ]; then
    echo ""
    echo "⚠️  检测到Python进程仍在运行:"
    ps aux | grep python | grep -v grep | sort -k4 -rn | head -5 | awk '{printf "  PID: %-8s Memory: %8s (%.2f GB)  %s\n", $2, $6, $6/1024/1024, $11" "$12" "$13" "$14" "$15}'
    
    # 计算总内存
    TOTAL_MEM=$(ps aux | grep python | grep -v grep | awk '{sum+=$6} END {print sum/1024/1024}')
    echo ""
    echo "  所有Python进程总内存: ${TOTAL_MEM} GB"
    
    if (( $(echo "$TOTAL_MEM > 5" | bc -l) )); then
        echo ""
        echo "❌ 警告: Python进程内存占用仍然很高 (${TOTAL_MEM} GB)"
        echo "   可能的原因:"
        echo "   1. 进程仍在运行（检查PID）"
        echo "   2. 操作系统尚未回收内存（等待更长时间）"
        echo "   3. 其他Python进程占用内存"
    else
        echo ""
        echo "✅ Python进程内存占用正常 (${TOTAL_MEM} GB)"
    fi
else
    echo ""
    echo "✅ 没有Python进程在运行，内存已释放"
fi

echo ""
echo "=========================================="
echo "测试完成"
echo "=========================================="



