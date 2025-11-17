#!/usr/bin/env python3
"""
将测试样本转换为不同格式，用于格式兼容性测试
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

def convert_to_format(input_path: str, output_path: str, format_type: str) -> bool:
    """将视频转换为指定格式"""
    try:
        if format_type == "mov":
            # MOV格式（H.264，iPhone常用）- stream copy
            cmd = [
                'ffmpeg', '-y',
                '-i', input_path,
                '-c', 'copy',  # stream copy，零损失
                '-movflags', '+faststart',
                output_path
            ]
        elif format_type == "h265":
            # MP4格式（H.265/HEVC，新安卓手机）- 需要重新编码
            cmd = [
                'ffmpeg', '-y',
                '-i', input_path,
                '-c:v', 'libx265',
                '-preset', 'fast',
                '-crf', '23',
                '-c:a', 'copy',  # 音频stream copy
                output_path
            ]
        elif format_type == "compressed":
            # 压缩MP4（低码率，模拟社交媒体下载）
            cmd = [
                'ffmpeg', '-y',
                '-i', input_path,
                '-c:v', 'libx264',
                '-preset', 'fast',
                '-crf', '28',
                '-b:v', '1M',
                '-c:a', 'aac',
                '-b:a', '128k',
                output_path
            ]
        elif format_type == "avi":
            # AVI格式 - stream copy
            cmd = [
                'ffmpeg', '-y',
                '-i', input_path,
                '-c', 'copy',
                output_path
            ]
        elif format_type == "mkv":
            # MKV格式 - stream copy
            cmd = [
                'ffmpeg', '-y',
                '-i', input_path,
                '-c', 'copy',
                output_path
            ]
        else:
            print(f"不支持的格式类型: {format_type}")
            return False
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"转换失败: {result.stderr[:200]}")
            return False
        
        print(f"✅ 转换成功: {os.path.basename(output_path)}")
        return True
        
    except Exception as e:
        print(f"转换异常: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="将测试样本转换为不同格式")
    parser.add_argument('--input-dir', type=str, default='test_data/test_multiple_videoformats',
                       help='输入目录（包含样本子目录）')
    parser.add_argument('--output-dir', type=str, default='test_data/test_multiple_videoformats_converted',
                       help='输出目录')
    parser.add_argument('--formats', type=str, nargs='+', 
                       default=['mov', 'h265', 'compressed', 'avi', 'mkv'],
                       help='要转换的格式列表')
    
    args = parser.parse_args()
    
    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True)
    
    # 查找所有样本目录
    sample_dirs = [d for d in input_dir.iterdir() if d.is_dir()]
    
    print(f"找到 {len(sample_dirs)} 个样本目录")
    print(f"转换格式: {args.formats}")
    print("-" * 60)
    
    total_files = 0
    success_files = 0
    
    for sample_dir in sample_dirs:
        sample_name = sample_dir.name
        print(f"\n处理样本: {sample_name}")
        
        # 查找dance和bgm文件
        dance_files = list(sample_dir.glob("dance.*"))
        bgm_files = list(sample_dir.glob("bgm.*"))
        
        if not dance_files or not bgm_files:
            print(f"  ⚠️  跳过：缺少dance或bgm文件")
            continue
        
        dance_file = dance_files[0]
        bgm_file = bgm_files[0]
        
        # 为每个格式创建输出目录
        for format_type in args.formats:
            format_output_dir = output_dir / sample_name / format_type
            format_output_dir.mkdir(parents=True, exist_ok=True)
            
            # 转换dance
            dance_ext = '.mov' if format_type == 'mov' else '.mp4' if format_type in ['h265', 'compressed'] else f'.{format_type}'
            dance_output = format_output_dir / f"dance{dance_ext}"
            total_files += 1
            if convert_to_format(str(dance_file), str(dance_output), format_type):
                success_files += 1
            
            # 转换bgm
            bgm_ext = '.mov' if format_type == 'mov' else '.mp4' if format_type in ['h265', 'compressed'] else f'.{format_type}'
            bgm_output = format_output_dir / f"bgm{bgm_ext}"
            total_files += 1
            if convert_to_format(str(bgm_file), str(bgm_output), format_type):
                success_files += 1
    
    print("\n" + "=" * 60)
    print(f"转换完成: {success_files}/{total_files} 个文件成功")
    print(f"输出目录: {output_dir}")
    
    return 0 if success_files == total_files else 1

if __name__ == "__main__":
    sys.exit(main())
