#!/usr/bin/env python3
"""
回归测试脚本
随机选择8个样本，使用并行处理器测试性能和结果
"""

import os
import sys
import subprocess
import random
import time
import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List

def get_all_samples(input_dir: str = "input_allcases") -> List[str]:
    """获取所有可用样本"""
    samples = []
    input_path = Path(input_dir)
    if not input_path.exists():
        print(f"错误: 输入目录不存在: {input_dir}")
        return samples
    
    for sample_dir in sorted(input_path.iterdir()):
        if sample_dir.is_dir():
            # 检查是否有dance和bgm文件
            dance_files = list(sample_dir.glob("dance.*"))
            bgm_files = list(sample_dir.glob("bgm.*"))
            if dance_files and bgm_files:
                samples.append(sample_dir.name)
    
    return samples

def find_video_files(sample_dir: Path) -> tuple:
    """查找dance和bgm视频文件"""
    dance_files = list(sample_dir.glob("dance.*"))
    bgm_files = list(sample_dir.glob("bgm.*"))
    
    if not dance_files or not bgm_files:
        return None, None
    
    return str(dance_files[0]), str(bgm_files[0])

def run_parallel_processor(dance_path: str, bgm_path: str, output_dir: str, sample_name: str) -> Dict:
    """运行并行处理器"""
    print(f"\n{'='*60}")
    print(f"处理样本: {sample_name}")
    print(f"{'='*60}")
    print(f"  dance: {os.path.basename(dance_path)}")
    print(f"  bgm: {os.path.basename(bgm_path)}")
    print(f"  输出目录: {output_dir}")
    
    # 构建命令
    cmd = [
        'python3', '-u', 'beatsync_parallel_processor.py',
        '--dance', dance_path,
        '--bgm', bgm_path,
        '--output-dir', output_dir,
        '--sample-name', sample_name
    ]
    
    # 记录开始时间
    start_time = time.time()
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        elapsed_time = time.time() - start_time
        
        # 解析输出
        output_text = result.stdout + result.stderr
        
        # 提取对齐信息
        info = {
            'sample_name': sample_name,
            'dance_path': dance_path,
            'bgm_path': bgm_path,
            'return_code': result.returncode,
            'elapsed_time': elapsed_time,
            'success': result.returncode == 0,
            'stdout_length': len(result.stdout),
            'stderr_length': len(result.stderr),
        }
        
        # 查找输出视频
        modular_output = Path(output_dir) / f"{sample_name}_modular.mp4"
        v2_output = Path(output_dir) / f"{sample_name}_v2.mp4"
        
        info['modular_output'] = str(modular_output) if modular_output.exists() else None
        info['v2_output'] = str(v2_output) if v2_output.exists() else None
        
        # 提取对齐点信息（如果成功）
        if result.returncode == 0:
            # 尝试从输出中提取对齐信息
            modular_match = re.search(r'modular.*?dance.*?(\d+\.?\d*)s', output_text, re.IGNORECASE)
            v2_match = re.search(r'v2.*?dance.*?(\d+\.?\d*)s', output_text, re.IGNORECASE)
            
            if modular_match:
                info['modular_dance_alignment'] = float(modular_match.group(1))
            if v2_match:
                info['v2_dance_alignment'] = float(v2_match.group(1))
        
        if result.returncode == 0:
            print(f"  ✅ 成功 (耗时: {elapsed_time:.2f}秒)")
            if info.get('modular_dance_alignment'):
                print(f"    modular对齐点: {info['modular_dance_alignment']:.2f}s")
            if info.get('v2_dance_alignment'):
                print(f"    v2对齐点: {info['v2_dance_alignment']:.2f}s")
        else:
            print(f"  ❌ 失败 (耗时: {elapsed_time:.2f}秒)")
            print(f"    错误: {result.stderr[:200]}")
        
        return info
        
    except subprocess.TimeoutExpired:
        elapsed_time = time.time() - start_time
        print(f"  ⏱️  超时 (耗时: {elapsed_time:.2f}秒)")
        return {
            'sample_name': sample_name,
            'success': False,
            'elapsed_time': elapsed_time,
            'error': 'timeout'
        }
    except Exception as e:
        elapsed_time = time.time() - start_time
        print(f"  ❌ 异常: {e}")
        return {
            'sample_name': sample_name,
            'success': False,
            'elapsed_time': elapsed_time,
            'error': str(e)
        }

def get_video_info(video_path: str) -> Dict:
    """获取视频信息"""
    if not video_path or not os.path.exists(video_path):
        return {'duration': None, 'size': None}
    
    try:
        # 获取时长
        cmd = [
            'ffprobe', '-v', 'quiet',
            '-show_entries', 'format=duration',
            '-of', 'csv=p=0',
            video_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        duration = float(result.stdout.strip()) if result.returncode == 0 else None
        
        # 获取文件大小
        size = os.path.getsize(video_path) / (1024 * 1024)  # MB
        
        return {'duration': duration, 'size_mb': size}
    except:
        return {'duration': None, 'size_mb': None}

def main():
    print("=" * 60)
    print("BeatSync 回归测试")
    print("=" * 60)
    
    # 1. 获取所有样本
    print("\n步骤1: 获取所有可用样本...")
    all_samples = get_all_samples()
    print(f"找到 {len(all_samples)} 个可用样本")
    
    if len(all_samples) < 8:
        print(f"错误: 可用样本数量不足（需要8个，实际{len(all_samples)}个）")
        return 1
    
    # 2. 随机选择8个样本
    print("\n步骤2: 随机选择8个样本...")
    random.seed(42)  # 固定随机种子，便于复现
    selected_samples = random.sample(all_samples, 8)
    print(f"选中的样本: {', '.join(selected_samples)}")
    
    # 3. 创建输出目录
    output_base_dir = Path("regression_test_outputs")
    output_base_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = output_base_dir / f"test_{timestamp}"
    output_dir.mkdir(exist_ok=True)
    
    print(f"\n步骤3: 创建输出目录: {output_dir}")
    
    # 4. 处理每个样本
    print("\n步骤4: 开始处理样本...")
    results = []
    
    for i, sample_name in enumerate(selected_samples, 1):
        print(f"\n[{i}/8] 处理样本: {sample_name}")
        
        sample_dir = Path("input_allcases") / sample_name
        dance_path, bgm_path = find_video_files(sample_dir)
        
        if not dance_path or not bgm_path:
            print(f"  ⚠️  跳过：找不到dance或bgm文件")
            results.append({
                'sample_name': sample_name,
                'success': False,
                'error': 'missing_files'
            })
            continue
        
        result = run_parallel_processor(dance_path, bgm_path, str(output_dir), sample_name)
        results.append(result)
    
    # 5. 获取输出视频信息
    print("\n步骤5: 收集输出视频信息...")
    for result in results:
        if result.get('modular_output'):
            result['modular_video_info'] = get_video_info(result['modular_output'])
        if result.get('v2_output'):
            result['v2_video_info'] = get_video_info(result['v2_output'])
    
    # 6. 生成测试报告
    print("\n步骤6: 生成测试报告...")
    
    report_path = output_dir / "test_report.txt"
    json_path = output_dir / "test_results.json"
    
    # 统计信息
    success_count = sum(1 for r in results if r.get('success', False))
    total_time = sum(r.get('elapsed_time', 0) for r in results)
    avg_time = total_time / len(results) if results else 0
    
    # 生成文本报告
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("# BeatSync 回归测试报告\n\n")
        f.write(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"测试样本数: {len(selected_samples)}\n")
        f.write(f"成功样本数: {success_count}\n")
        f.write(f"失败样本数: {len(results) - success_count}\n")
        f.write(f"总耗时: {total_time:.2f}秒\n")
        f.write(f"平均耗时: {avg_time:.2f}秒\n")
        f.write(f"成功率: {success_count/len(results)*100:.1f}%\n\n")
        
        f.write("## 测试样本列表\n\n")
        f.write(f"{', '.join(selected_samples)}\n\n")
        
        f.write("## 详细结果\n\n")
        f.write("| 样本 | 状态 | 耗时(秒) | modular对齐点 | v2对齐点 | modular输出 | v2输出 |\n")
        f.write("|------|------|----------|---------------|----------|-------------|--------|\n")
        
        for result in results:
            sample = result['sample_name']
            success = result.get('success', False)
            elapsed = result.get('elapsed_time', 0)
            modular_align = result.get('modular_dance_alignment', 'N/A')
            v2_align = result.get('v2_dance_alignment', 'N/A')
            modular_out = '✅' if result.get('modular_output') else '❌'
            v2_out = '✅' if result.get('v2_output') else '❌'
            status = '✅' if success else '❌'
            
            f.write(f"| {sample} | {status} | {elapsed:.2f} | {modular_align} | {v2_align} | {modular_out} | {v2_out} |\n")
        
        f.write("\n## 性能统计\n\n")
        f.write("| 样本 | 耗时(秒) | modular视频时长 | v2视频时长 | modular文件大小(MB) | v2文件大小(MB) |\n")
        f.write("|------|----------|-----------------|------------|---------------------|----------------|\n")
        
        for result in results:
            sample = result['sample_name']
            elapsed = result.get('elapsed_time', 0)
            modular_info = result.get('modular_video_info', {})
            v2_info = result.get('v2_video_info', {})
            
            modular_duration = f"{modular_info.get('duration', 'N/A'):.2f}" if modular_info.get('duration') else 'N/A'
            v2_duration = f"{v2_info.get('duration', 'N/A'):.2f}" if v2_info.get('duration') else 'N/A'
            modular_size = f"{modular_info.get('size_mb', 'N/A'):.2f}" if modular_info.get('size_mb') else 'N/A'
            v2_size = f"{v2_info.get('size_mb', 'N/A'):.2f}" if v2_info.get('size_mb') else 'N/A'
            
            f.write(f"| {sample} | {elapsed:.2f} | {modular_duration} | {v2_duration} | {modular_size} | {v2_size} |\n")
        
        if success_count < len(results):
            f.write("\n## 失败详情\n\n")
            for result in results:
                if not result.get('success', False):
                    f.write(f"### {result['sample_name']}\n")
                    f.write(f"- 错误: {result.get('error', 'unknown')}\n")
                    if result.get('return_code'):
                        f.write(f"- 返回码: {result['return_code']}\n")
                    f.write("\n")
    
    # 保存JSON结果
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'selected_samples': selected_samples,
            'results': results,
            'summary': {
                'total': len(results),
                'success': success_count,
                'failed': len(results) - success_count,
                'total_time': total_time,
                'avg_time': avg_time,
                'success_rate': success_count/len(results)*100 if results else 0
            }
        }, f, indent=2, ensure_ascii=False)
    
    # 输出摘要
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)
    print(f"总样本数: {len(results)}")
    print(f"成功: {success_count}")
    print(f"失败: {len(results) - success_count}")
    print(f"总耗时: {total_time:.2f}秒")
    print(f"平均耗时: {avg_time:.2f}秒")
    print(f"成功率: {success_count/len(results)*100:.1f}%")
    print(f"\n输出目录: {output_dir}")
    print(f"测试报告: {report_path}")
    print(f"JSON结果: {json_path}")
    
    return 0 if success_count == len(results) else 1

if __name__ == "__main__":
    sys.exit(main())

