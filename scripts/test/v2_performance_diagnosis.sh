#!/bin/bash
# V2版本性能诊断脚本
# 用于分析V2版本各步骤的耗时

set -e

echo "=========================================="
echo "V2版本性能诊断"
echo "=========================================="
echo ""

# 测试数据路径
DANCE_VIDEO="test_data/input_allcases/waitonme/dance.MP4"
BGM_VIDEO="test_data/input_allcases/waitonme/bgm.MP4"
OUTPUT_VIDEO="outputs/test_v2_waitonme_diagnosis_$(date +%Y%m%d_%H%M%S).mp4"

# 检查文件是否存在
if [ ! -f "$DANCE_VIDEO" ]; then
    echo "错误: 找不到dance视频: $DANCE_VIDEO"
    exit 1
fi

if [ ! -f "$BGM_VIDEO" ]; then
    echo "错误: 找不到bgm视频: $BGM_VIDEO"
    exit 1
fi

# 创建输出目录
mkdir -p outputs

echo "测试样本:"
echo "  Dance视频: $DANCE_VIDEO"
echo "  BGM视频: $BGM_VIDEO"
echo "  输出视频: $OUTPUT_VIDEO"
echo ""

# 获取视频信息
echo "=========================================="
echo "视频信息"
echo "=========================================="
echo "Dance视频:"
ffprobe -v quiet -print_format json -show_format -show_streams "$DANCE_VIDEO" | python3 -c "
import sys, json
data = json.load(sys.stdin)
video_stream = next((s for s in data['streams'] if s['codec_type'] == 'video'), None)
if video_stream:
    print(f\"  分辨率: {video_stream.get('width', 'N/A')}x{video_stream.get('height', 'N/A')}\")
    print(f\"  帧率: {video_stream.get('r_frame_rate', 'N/A')}\")
    print(f\"  时长: {float(data['format'].get('duration', 0)):.2f}秒\")
    print(f\"  文件大小: {int(data['format'].get('size', 0)) / 1024 / 1024:.2f}MB\")
"

echo ""
echo "BGM视频:"
ffprobe -v quiet -print_format json -show_format -show_streams "$BGM_VIDEO" | python3 -c "
import sys, json
data = json.load(sys.stdin)
video_stream = next((s for s in data['streams'] if s['codec_type'] == 'video'), None)
if video_stream:
    print(f\"  分辨率: {video_stream.get('width', 'N/A')}x{video_stream.get('height', 'N/A')}\")
    print(f\"  帧率: {video_stream.get('r_frame_rate', 'N/A')}\")
    print(f\"  时长: {float(data['format'].get('duration', 0)):.2f}秒\")
    print(f\"  文件大小: {int(data['format'].get('size', 0)) / 1024 / 1024:.2f}MB\")
"

echo ""
echo "=========================================="
echo "开始性能测试"
echo "=========================================="
echo "开始时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# 运行V2程序并记录时间
START_TIME=$(date +%s.%N)

python3 beatsync_badcase_fix_trim_v2.py \
  --dance "$DANCE_VIDEO" \
  --bgm "$BGM_VIDEO" \
  --output "$OUTPUT_VIDEO" \
  --fast-video \
  --video-encode x264_fast \
  --enable-cache \
  --cache-dir .beatsync_cache \
  --threads 2 \
  --lib-threads 1 \
  2>&1 | tee /tmp/v2_diagnosis_$(date +%Y%m%d_%H%M%S).log

END_TIME=$(date +%s.%N)
ELAPSED=$(echo "$END_TIME - $START_TIME" | bc)

echo ""
echo "=========================================="
echo "测试完成"
echo "=========================================="
echo "结束时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo "总耗时: ${ELAPSED}秒 ($(echo "scale=2; $ELAPSED / 60" | bc)分钟)"
echo ""

# 检查输出文件
if [ -f "$OUTPUT_VIDEO" ]; then
    OUTPUT_SIZE=$(du -h "$OUTPUT_VIDEO" | cut -f1)
    echo "输出文件: $OUTPUT_VIDEO"
    echo "文件大小: $OUTPUT_SIZE"
    echo ""
    echo "✅ 处理成功"
else
    echo "❌ 处理失败：未生成输出文件"
fi

echo ""
echo "详细日志已保存到: /tmp/v2_diagnosis_*.log"
echo "=========================================="

