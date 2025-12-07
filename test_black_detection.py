#!/usr/bin/env python3
"""测试FFmpeg blackdetect优化"""

import sys
import time
import os

# 添加项目路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from beatsync_badcase_fix_trim_v2 import (
    detect_black_frames_with_audio,
    detect_black_frames_with_audio_opencv,
    detect_black_frames_with_audio_ffmpeg,
    USE_FFMPEG_BLACKDETECT
)

def test_black_detection(video_path, position="trailing"):
    """测试黑屏检测"""
    if not os.path.exists(video_path):
        print(f"❌ 视频文件不存在: {video_path}")
        return
    
    print(f"\n{'='*60}")
    print(f"测试视频: {video_path}")
    print(f"检测位置: {position}")
    print(f"当前实现: {'FFmpeg blackdetect' if USE_FFMPEG_BLACKDETECT else 'OpenCV'}")
    print(f"{'='*60}\n")
    
    # 测试当前实现
    print("🔍 测试当前实现...")
    start_time = time.time()
    try:
        result = detect_black_frames_with_audio(video_path, position)
        elapsed_time = time.time() - start_time
        print(f"✅ 结果: {result:.3f}秒")
        print(f"⏱️  耗时: {elapsed_time:.3f}秒")
    except Exception as e:
        print(f"❌ 错误: {e}")
        elapsed_time = time.time() - start_time
        result = None
    
    # 对比OpenCV实现
    print(f"\n{'='*60}")
    print("🔍 对比OpenCV实现:")
    print(f"{'='*60}\n")
    
    start_time = time.time()
    try:
        result_opencv = detect_black_frames_with_audio_opencv(video_path, position)
        elapsed_time_opencv = time.time() - start_time
        print(f"✅ 结果: {result_opencv:.3f}秒")
        print(f"⏱️  耗时: {elapsed_time_opencv:.3f}秒")
    except Exception as e:
        print(f"❌ 错误: {e}")
        elapsed_time_opencv = time.time() - start_time
        result_opencv = None
    
    # 对比
    if result is not None and result_opencv is not None:
        print(f"\n{'='*60}")
        print("📊 对比结果:")
        print(f"{'='*60}")
        result_diff = abs(result - result_opencv)
        print(f"结果差异: {result_diff:.3f}秒")
        if result_diff < 0.5:
            print("✅ 结果基本一致（差异 < 0.5秒）")
        else:
            print("⚠️  结果差异较大，需要检查")
        
        if elapsed_time > 0 and elapsed_time_opencv > 0:
            speedup = elapsed_time_opencv / elapsed_time
            print(f"耗时差异: {elapsed_time_opencv - elapsed_time:.3f}秒")
            if speedup > 1:
                print(f"🚀 提速: {speedup:.2f}倍")
            else:
                print(f"⚠️  变慢: {1/speedup:.2f}倍")
        print(f"{'='*60}\n")

if __name__ == "__main__":
    # 默认测试视频路径
    test_video = "test_data/input_allcases/waitonme/dance.mp4"
    
    # 如果提供了命令行参数，使用参数
    if len(sys.argv) > 1:
        test_video = sys.argv[1]
    
    # 测试Trailing位置
    print("\n" + "="*60)
    print("测试1: Trailing位置检测（末尾黑屏）")
    print("="*60)
    test_black_detection(test_video, position="trailing")
    
    # 测试Leading位置
    print("\n" + "="*60)
    print("测试2: Leading位置检测（开头黑屏）")
    print("="*60)
    test_black_detection(test_video, position="leading")

