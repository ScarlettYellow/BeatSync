#!/usr/bin/env python3
"""
批量处理高清视频样本（随机选择10个）
使用并行处理器处理test_data/input_allcases/中的样本
"""

import os
import subprocess
import sys
import random
from datetime import datetime
from pathlib import Path

def get_all_samples(input_dir: str = "test_data/input_allcases") -> list:
    """获取所有可用样本"""
    samples = []
    input_path = Path(input_dir)
    if not input_path.exists():
        print(f"错误: 输入目录不存在: {input_dir}")
        return samples
    
    for item in input_path.iterdir():
        if item.is_dir():
            dance_path = item / "dance.mp4"
            bgm_path = item / "bgm.mp4"
            if dance_path.exists() and bgm_path.exists():
                samples.append(item.name)
    
    return samples

def process_sample(sample_name: str, input_dir: str, output_dir: str, project_root: str) -> dict:
    """处理单个样本"""
    sample_dir = Path(input_dir) / sample_name
    dance_path = sample_dir / "dance.mp4"
    bgm_path = sample_dir / "bgm.mp4"
    
    if not dance_path.exists() or not bgm_path.exists():
        return {
            'sample': sample_name,
            'success': False,
            'error': '文件不存在'
        }
    
    # 创建样本输出目录
    sample_output_dir = Path(output_dir) / sample_name
    sample_output_dir.mkdir(parents=True, exist_ok=True)
    
    # 运行并行处理器
    cmd = [
        sys.executable,
        str(Path(project_root) / "beatsync_parallel_processor.py"),
        "--dance", str(dance_path),
        "--bgm", str(bgm_path),
        "--output-dir", str(sample_output_dir),
        "--sample-name", sample_name
    ]
    
    print(f"\n处理样本: {sample_name}")
    print(f"  命令: {' '.join(cmd[:6])}...")
    print("-" * 60)
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=600  # 10分钟超时
        )
        
        if result.returncode == 0:
            # 检查输出文件
            modular_output = sample_output_dir / f"{sample_name}_modular.mp4"
            v2_output = sample_output_dir / f"{sample_name}_v2.mp4"
            
            success = modular_output.exists() or v2_output.exists()
            
            return {
                'sample': sample_name,
                'success': success,
                'modular_output': str(modular_output) if modular_output.exists() else None,
                'v2_output': str(v2_output) if v2_output.exists() else None,
                'stdout': result.stdout[-500:] if result.stdout else '',  # 最后500字符
                'stderr': result.stderr[-500:] if result.stderr else ''
            }
        else:
            return {
                'sample': sample_name,
                'success': False,
                'error': f'返回码: {result.returncode}',
                'stderr': result.stderr[-500:] if result.stderr else ''
            }
    except subprocess.TimeoutExpired:
        return {
            'sample': sample_name,
            'success': False,
            'error': '处理超时（超过10分钟）'
        }
    except Exception as e:
        return {
            'sample': sample_name,
            'success': False,
            'error': str(e)
        }

def main():
    # 配置
    input_dir = "test_data/input_allcases"
    output_dir = "outputs/batch_hd_samples"
    project_root = Path(__file__).parent.parent.parent
    
    # 获取所有样本
    print("=" * 60)
    print("BeatSync 高清视频批量处理")
    print("=" * 60)
    print(f"输入目录: {input_dir}")
    print(f"输出目录: {output_dir}")
    print(f"处理时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    all_samples = get_all_samples(input_dir)
    
    if len(all_samples) == 0:
        print(f"错误: 在 {input_dir} 中未找到任何样本")
        return 1
    
    print(f"找到 {len(all_samples)} 个样本")
    
    # 随机选择10个样本
    if len(all_samples) >= 10:
        selected_samples = random.sample(all_samples, 10)
    else:
        selected_samples = all_samples
        print(f"  注意: 样本数少于10个，将处理所有 {len(selected_samples)} 个样本")
    
    print(f"随机选择 {len(selected_samples)} 个样本:")
    for i, sample in enumerate(selected_samples, 1):
        print(f"  {i}. {sample}")
    print()
    
    # 创建输出目录
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # 处理每个样本
    results = []
    total = len(selected_samples)
    
    for i, sample_name in enumerate(selected_samples, 1):
        print(f"\n[{i}/{total}] 开始处理: {sample_name}")
        result = process_sample(sample_name, input_dir, output_dir, str(project_root))
        results.append(result)
        
        if result['success']:
            print(f"  ✅ 成功")
            if result.get('modular_output'):
                print(f"     Modular输出: {result['modular_output']}")
            if result.get('v2_output'):
                print(f"     V2输出: {result['v2_output']}")
        else:
            print(f"  ❌ 失败: {result.get('error', '未知错误')}")
    
    # 生成报告
    print("\n" + "=" * 60)
    print("处理完成")
    print("=" * 60)
    
    success_count = sum(1 for r in results if r['success'])
    fail_count = total - success_count
    
    print(f"总计: {total} 个样本")
    print(f"成功: {success_count} 个")
    print(f"失败: {fail_count} 个")
    print()
    
    if fail_count > 0:
        print("失败的样本:")
        for result in results:
            if not result['success']:
                print(f"  - {result['sample']}: {result.get('error', '未知错误')}")
        print()
    
    # 保存报告
    report_file = output_path / "batch_processing_report.txt"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("BeatSync 高清视频批量处理报告\n")
        f.write("=" * 60 + "\n")
        f.write(f"处理时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"输入目录: {input_dir}\n")
        f.write(f"输出目录: {output_dir}\n")
        f.write(f"样本总数: {total}\n")
        f.write(f"成功: {success_count}\n")
        f.write(f"失败: {fail_count}\n")
        f.write("\n" + "=" * 60 + "\n\n")
        
        for result in results:
            f.write(f"样本: {result['sample']}\n")
            f.write(f"  状态: {'✅ 成功' if result['success'] else '❌ 失败'}\n")
            if result['success']:
                if result.get('modular_output'):
                    f.write(f"  Modular输出: {result['modular_output']}\n")
                if result.get('v2_output'):
                    f.write(f"  V2输出: {result['v2_output']}\n")
            else:
                f.write(f"  错误: {result.get('error', '未知错误')}\n")
            f.write("\n")
    
    print(f"报告已保存: {report_file}")
    
    return 0 if fail_count == 0 else 1

if __name__ == "__main__":
    sys.exit(main())

