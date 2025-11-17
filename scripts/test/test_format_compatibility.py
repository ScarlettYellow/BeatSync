#!/usr/bin/env python3
"""
批量测试不同格式组合的兼容性
"""

import os
import sys
import subprocess
import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple

def extract_alignment_info(log_text: str) -> Dict:
    """从日志中提取对齐信息"""
    info = {
        'dance_alignment': None,
        'bgm_alignment': None,
        'confidence': None,
        'output_duration': None,
        'success': False
    }
    
    # 提取dance对齐点（优先匹配"dance 开始"，避免匹配到音频长度）
    dance_patterns = [
        r'dance 开始.*?(\d+\.?\d*)s',
        r'dance 节拍点.*?(\d+\.?\d*)s',
        r'dance.*?开始.*?(\d+\.?\d*)s',
    ]
    for pattern in dance_patterns:
        match = re.search(pattern, log_text, re.IGNORECASE)
        if match:
            info['dance_alignment'] = float(match.group(1))
            break
    
    # 提取bgm对齐点（优先匹配"bgm 开始"，避免匹配到音频长度）
    bgm_patterns = [
        r'bgm 开始.*?(\d+\.?\d*)s',
        r'bgm 节拍点.*?(\d+\.?\d*)s',
        r'bgm.*?开始.*?(\d+\.?\d*)s',
    ]
    for pattern in bgm_patterns:
        match = re.search(pattern, log_text, re.IGNORECASE)
        if match:
            info['bgm_alignment'] = float(match.group(1))
            break
    
    # 提取置信度
    confidence_patterns = [
        r'置信度.*?(\d+\.?\d*)',
        r'最终得分.*?(\d+\.?\d*)',
    ]
    for pattern in confidence_patterns:
        match = re.search(pattern, log_text, re.IGNORECASE)
        if match:
            info['confidence'] = float(match.group(1))
            break
    
    # 检查是否成功
    success_indicators = ['处理成功', 'success', '完成', '模块解耦精剪模式处理成功']
    info['success'] = any(indicator in log_text for indicator in success_indicators)
    
    return info

def get_video_duration(video_path: str) -> float:
    """获取视频时长"""
    try:
        cmd = [
            'ffprobe', '-v', 'quiet',
            '-show_entries', 'format=duration',
            '-of', 'csv=p=0',
            video_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return float(result.stdout.strip())
    except:
        return 0.0

def run_test(dance_path: str, bgm_path: str, output_path: str, 
             sample_name: str, format_combo: str) -> Dict:
    """运行单个测试"""
    print(f"\n测试: {sample_name} - {format_combo}")
    print(f"  dance: {os.path.basename(dance_path)}")
    print(f"  bgm: {os.path.basename(bgm_path)}")
    
    log_path = output_path.replace('.mp4', '.log')
    
    # 运行modular版本
    cmd = [
        'python3', '-u', 'beatsync_fine_cut_modular.py',
        '--dance', dance_path,
        '--bgm', bgm_path,
        '--output', output_path
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        # 保存日志
        with open(log_path, 'w', encoding='utf-8') as f:
            f.write(result.stdout)
            if result.stderr:
                f.write("\n--- STDERR ---\n")
                f.write(result.stderr)
        
        # 提取信息
        info = extract_alignment_info(result.stdout)
        info['return_code'] = result.returncode
        info['log_path'] = log_path
    
        # 获取输出视频时长
        if os.path.exists(output_path):
            info['output_duration'] = get_video_duration(output_path)
            info['output_path'] = output_path
        else:
            info['output_path'] = None
        
        if info['success']:
            print(f"  ✅ 成功: dance={info['dance_alignment']}s, bgm={info['bgm_alignment']}s")
        else:
            print(f"  ❌ 失败: return_code={result.returncode}")
        
        return info
        
    except subprocess.TimeoutExpired:
        print(f"  ❌ 超时")
        return {'success': False, 'error': 'timeout'}
    except Exception as e:
        print(f"  ❌ 异常: {e}")
        return {'success': False, 'error': str(e)}

def main():
    # 测试配置
    base_dir = Path('test_data/test_multiple_videoformats')
    converted_dir = Path('test_data/test_multiple_videoformats_converted')
    output_dir = Path('test_format_compatibility_outputs')
    output_dir.mkdir(exist_ok=True)
    
    # 测试场景定义
    test_scenarios = [
        # 核心场景（实际用户场景）
        {'sample': 'echo', 'dance_format': 'original', 'bgm_format': 'original', 'priority': 'high'},
        {'sample': 'echo', 'dance_format': 'mov', 'bgm_format': 'original', 'priority': 'high'},
        {'sample': 'echo', 'dance_format': 'original', 'bgm_format': 'mov', 'priority': 'high'},
        {'sample': 'echo', 'dance_format': 'mov', 'bgm_format': 'mov', 'priority': 'high'},
        {'sample': 'echo', 'dance_format': 'h265', 'bgm_format': 'original', 'priority': 'high'},
        {'sample': 'echo', 'dance_format': 'original', 'bgm_format': 'h265', 'priority': 'high'},
        {'sample': 'fallingout_short', 'dance_format': 'original', 'bgm_format': 'original', 'priority': 'high'},
        {'sample': 'fallingout_short', 'dance_format': 'mov', 'bgm_format': 'mov', 'priority': 'high'},
        {'sample': 'fallingout_short', 'dance_format': 'h265', 'bgm_format': 'h265', 'priority': 'high'},
        {'sample': 'famous_short', 'dance_format': 'original', 'bgm_format': 'original', 'priority': 'high'},
        {'sample': 'famous_short', 'dance_format': 'mov', 'bgm_format': 'h265', 'priority': 'high'},
        {'sample': 'famous_short', 'dance_format': 'compressed', 'bgm_format': 'compressed', 'priority': 'high'},
        # 兼容性场景
        {'sample': 'echo', 'dance_format': 'avi', 'bgm_format': 'original', 'priority': 'medium'},
        {'sample': 'echo', 'dance_format': 'mkv', 'bgm_format': 'original', 'priority': 'low'},
    ]
    
    print("=" * 60)
    print("视频格式兼容性测试")
    print("=" * 60)
    print(f"测试场景数: {len(test_scenarios)}")
    print(f"输出目录: {output_dir}")
    print("-" * 60)
    
    results = []
    baseline_results = {}  # 存储基准测试结果
    
    for i, scenario in enumerate(test_scenarios, 1):
        sample_name = scenario['sample']
        dance_format = scenario['dance_format']
        bgm_format = scenario['bgm_format']
        priority = scenario['priority']
        
        # 确定文件路径
        if dance_format == 'original':
            dance_path = list((base_dir / sample_name).glob("dance.*"))[0]
        else:
            dance_path = list((converted_dir / sample_name / dance_format).glob("dance.*"))[0]
        
        if bgm_format == 'original':
            bgm_path = list((base_dir / sample_name).glob("bgm.*"))[0]
        else:
            bgm_path = list((converted_dir / sample_name / bgm_format).glob("bgm.*"))[0]
        
        format_combo = f"{dance_format}/{bgm_format}"
        output_path = output_dir / f"{sample_name}_{format_combo.replace('/', '_')}.mp4"
        
        # 运行测试
        result = run_test(
            str(dance_path),
            str(bgm_path),
            str(output_path),
            sample_name,
            format_combo
        )
        
        result['sample'] = sample_name
        result['format_combo'] = format_combo
        result['priority'] = priority
        result['scenario_num'] = i
        results.append(result)
        
        # 保存基准测试结果
        if dance_format == 'original' and bgm_format == 'original':
            baseline_results[sample_name] = result
    
    # 生成报告
    print("\n" + "=" * 60)
    print("生成测试报告...")
    
    report_path = output_dir / "test_report.txt"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("# 视频格式兼容性测试报告\n\n")
        f.write(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"测试场景数: {len(test_scenarios)}\n")
        f.write(f"核心场景: {sum(1 for r in results if r.get('priority') == 'high')}\n")
        f.write(f"兼容性场景: {sum(1 for r in results if r.get('priority') != 'high')}\n\n")
        
        # 统计
        success_count = sum(1 for r in results if r.get('success'))
        high_priority_success = sum(1 for r in results if r.get('success') and r.get('priority') == 'high')
        high_priority_total = sum(1 for r in results if r.get('priority') == 'high')
        
        f.write("## 测试结果汇总\n\n")
        f.write(f"- 总测试场景: {len(results)}\n")
        f.write(f"- 成功场景: {success_count}\n")
        f.write(f"- 失败场景: {len(results) - success_count}\n")
        f.write(f"- 总成功率: {success_count/len(results)*100:.1f}%\n")
        f.write(f"- 核心场景成功率: {high_priority_success}/{high_priority_total} ({high_priority_success/high_priority_total*100:.1f}%)\n\n")
        
        # 对齐点对比
        f.write("## 对齐点对比\n\n")
        f.write("| 样本 | 格式组合 | dance对齐点 | bgm对齐点 | 置信度 | 与基准差异 | 状态 |\n")
        f.write("|------|----------|-------------|-----------|--------|------------|------|\n")
        
        for result in results:
            sample = result['sample']
            combo = result['format_combo']
            dance_align = result.get('dance_alignment', 'N/A')
            bgm_align = result.get('bgm_alignment', 'N/A')
            confidence = result.get('confidence', 'N/A')
            success = result.get('success', False)
            
            # 计算与基准的差异
            if sample in baseline_results and success:
                baseline = baseline_results[sample]
                dance_diff = abs(dance_align - baseline.get('dance_alignment', 0)) if isinstance(dance_align, (int, float)) and isinstance(baseline.get('dance_alignment'), (int, float)) else 'N/A'
                bgm_diff = abs(bgm_align - baseline.get('bgm_alignment', 0)) if isinstance(bgm_align, (int, float)) and isinstance(baseline.get('bgm_alignment'), (int, float)) else 'N/A'
                if isinstance(dance_diff, (int, float)) and isinstance(bgm_diff, (int, float)):
                    diff_str = f"dance:{dance_diff:.3f}s, bgm:{bgm_diff:.3f}s"
                else:
                    diff_str = 'N/A'
            else:
                diff_str = 'N/A' if combo == 'original/original' else '未对比'
            
            status = '✅' if success else '❌'
            f.write(f"| {sample} | {combo} | {dance_align} | {bgm_align} | {confidence} | {diff_str} | {status} |\n")
        
        # 输出时长对比
        f.write("\n## 输出时长对比\n\n")
        f.write("| 样本 | 格式组合 | 输出时长 | 与基准差异 | 状态 |\n")
        f.write("|------|----------|----------|------------|------|\n")
        
        for result in results:
            sample = result['sample']
            combo = result['format_combo']
            duration = result.get('output_duration', 'N/A')
            success = result.get('success', False)
            
            if sample in baseline_results and success and isinstance(duration, (int, float)):
                baseline_duration = baseline_results[sample].get('output_duration', 0)
                if isinstance(baseline_duration, (int, float)):
                    diff = abs(duration - baseline_duration)
                    diff_str = f"{diff:.3f}s"
                else:
                    diff_str = 'N/A'
            else:
                diff_str = 'N/A' if combo == 'original/original' else '未对比'
            
            status = '✅' if success else '❌'
            f.write(f"| {sample} | {combo} | {duration} | {diff_str} | {status} |\n")
        
        # 结论
        f.write("\n## 结论\n\n")
        if high_priority_success == high_priority_total:
            f.write("✅ 核心场景全部通过\n")
        else:
            f.write(f"⚠️ 核心场景有 {high_priority_total - high_priority_success} 个失败\n")
        
        if success_count == len(results):
            f.write("✅ 所有格式组合处理成功\n")
        else:
            f.write(f"⚠️ 有 {len(results) - success_count} 个格式组合处理失败\n")
    
    print(f"✅ 测试报告已生成: {report_path}")
    print(f"✅ 核心场景成功率: {high_priority_success}/{high_priority_total} ({high_priority_success/high_priority_total*100:.1f}%)")
    
    return 0 if high_priority_success == high_priority_total else 1

if __name__ == "__main__":
    sys.exit(main())

