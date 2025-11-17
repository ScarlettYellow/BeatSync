#!/usr/bin/env python3
"""测试后端API是否能正确调用并行处理器"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

print(f"项目根目录: {project_root}")
print(f"sys.path: {sys.path[:3]}...")

try:
    from beatsync_parallel_processor import process_beat_sync_parallel
    print("✅ 成功导入并行处理器")
    
    # 测试调用
    dance_path = str(project_root / "test_data/input_allcases/fallingout_short/dance.mp4")
    bgm_path = str(project_root / "test_data/input_allcases/fallingout_short/bgm.mp4")
    output_dir = str(project_root / "outputs/test_backend_api")
    
    print(f"\n测试处理...")
    print(f"dance: {dance_path}")
    print(f"bgm: {bgm_path}")
    print(f"output: {output_dir}")
    
    success = process_beat_sync_parallel(dance_path, bgm_path, output_dir, "test_backend")
    
    if success:
        print("✅ 处理成功")
    else:
        print("❌ 处理失败")
        
except Exception as e:
    print(f"❌ 错误: {e}")
    import traceback
    traceback.print_exc()
