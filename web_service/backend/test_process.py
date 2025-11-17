#!/usr/bin/env python3
"""测试处理接口"""
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from beatsync_parallel_processor import process_beat_sync_parallel

dance_path = "test_data/input_allcases/fallingout_short/dance.mp4"
bgm_path = "test_data/input_allcases/fallingout_short/bgm.mp4"
output_dir = "outputs/test_web_process"
sample_name = "test"

print("测试处理...")
success = process_beat_sync_parallel(dance_path, bgm_path, output_dir, sample_name)
print(f"处理结果: {'成功' if success else '失败'}")
