#!/usr/bin/env python3
"""
BeatSync 并行处理器 - 内存优化版本
同时使用modular版本和V2版本处理样本，生成两个输出视频供用户选择
优化内存使用，避免内存泄漏
"""

import os
import sys
import subprocess
import argparse
import tempfile
import shutil
import gc
import time
import re
from datetime import datetime
from typing import Tuple

def get_memory_usage():
    """获取当前内存使用情况"""
    try:
        import psutil
        process = psutil.Process()
        return process.memory_info().rss / 1024 / 1024 / 1024  # GB
    except ImportError:
        # 如果没有psutil，返回0
        return 0.0

def log_memory_usage(stage: str):
    """记录内存使用情况"""
    memory_gb = get_memory_usage()
    print(f"[内存监控] {stage}: {memory_gb:.2f}GB")
    return memory_gb

def extract_alignment_info(output_text, program_name):
    """从程序输出中提取对齐信息"""
    info = {
        'program': program_name,
        'dance_alignment': 'UNKNOWN',
        'bgm_alignment': 'UNKNOWN',
        'confidence': 'UNKNOWN',
        'success': False
    }
    
    # 提取对齐点信息 - 更全面的正则表达式
    dance_patterns = [
        r'dance.*?(\d+\.?\d*)s',
        r'dance 开始.*?(\d+\.?\d*)s',
        r'dance 节拍点.*?(\d+\.?\d*)s',
        r'dance.*?(\d+\.?\d*)秒'
    ]
    
    bgm_patterns = [
        r'bgm.*?(\d+\.?\d*)s',
        r'bgm 开始.*?(\d+\.?\d*)s', 
        r'bgm 节拍点.*?(\d+\.?\d*)s',
        r'bgm.*?(\d+\.?\d*)秒'
    ]
    
    confidence_patterns = [
        r'置信度.*?(\d+\.?\d*)',
        r'confidence.*?(\d+\.?\d*)',
        r'最终得分.*?(\d+\.?\d*)'
    ]
    
    # 尝试匹配dance对齐点
    for pattern in dance_patterns:
        match = re.search(pattern, output_text, re.IGNORECASE)
        if match:
            info['dance_alignment'] = f"{match.group(1)}s"
            break
    
    # 尝试匹配bgm对齐点
    for pattern in bgm_patterns:
        match = re.search(pattern, output_text, re.IGNORECASE)
        if match:
            info['bgm_alignment'] = f"{match.group(1)}s"
            break
    
    # 尝试匹配置信度
    for pattern in confidence_patterns:
        match = re.search(pattern, output_text, re.IGNORECASE)
        if match:
            info['confidence'] = match.group(1)
            break
    
    # 检查是否成功
    success_indicators = ['处理成功', 'success', '完成', '模块解耦精剪模式处理成功']
    info['success'] = any(indicator in output_text for indicator in success_indicators)
    
    return info

def process_with_modular_optimized(dance_video: str, bgm_video: str, output_video: str) -> dict:
    """使用modular版本处理 - 内存优化"""
    try:
        print("  使用modular版本处理...")
        log_memory_usage("modular处理开始")
        
        # 强制垃圾回收
        gc.collect()
        
        cmd = [
            "python3", "beatsync_fine_cut_modular.py",
            "--dance", dance_video,
            "--bgm", bgm_video,
            "--output", output_video
        ]
        
        # 设置超时时间，避免无限等待
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)  # 10分钟
        
        log_memory_usage("modular处理完成")
        
        info = extract_alignment_info(result.stdout, "modular版本")
        info['return_code'] = result.returncode
        info['stderr'] = result.stderr
        return info
        
    except subprocess.TimeoutExpired:
        print("  modular版本处理超时，强制终止")
        return {'program': 'modular版本', 'success': False, 'error': '超时'}
    except Exception as e:
        print(f"  modular版本处理出错: {str(e)}")
        return {'program': 'modular版本', 'success': False, 'error': str(e)}
    finally:
        # 强制垃圾回收
        gc.collect()

def process_with_v2_optimized(dance_video: str, bgm_video: str, output_video: str) -> dict:
    """使用V2版本处理 - 内存优化"""
    try:
        print("  使用V2版本处理...")
        log_memory_usage("V2处理开始")
        
        # 强制垃圾回收
        gc.collect()
        
        cmd = [
            "python3", "beatsync_badcase_fix_trim_v2.py",
            "--dance", dance_video,
            "--bgm", bgm_video,
            "--output", output_video
        ]
        
        # 设置超时时间，避免无限等待
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)  # 10分钟
        
        log_memory_usage("V2处理完成")
        
        info = extract_alignment_info(result.stdout, "V2版本")
        info['return_code'] = result.returncode
        info['stderr'] = result.stderr
        return info
        
    except subprocess.TimeoutExpired:
        print("  V2版本处理超时，强制终止")
        return {'program': 'V2版本', 'success': False, 'error': '超时'}
    except Exception as e:
        print(f"  V2版本处理出错: {str(e)}")
        return {'program': 'V2版本', 'success': False, 'error': str(e)}
    finally:
        # 强制垃圾回收
        gc.collect()

def process_beat_sync_parallel_optimized(dance_video: str, bgm_video: str, output_dir: str, sample_name: str) -> bool:
    """并行处理主函数 - 内存优化版本"""
    print("=" * 60)
    print("BeatSync 并行处理器 - 内存优化版本")
    print("=" * 60)
    
    # 记录初始内存使用
    initial_memory = log_memory_usage("处理开始")
    
    # 检查输入文件
    if not os.path.exists(dance_video):
        print(f"错误: dance视频文件不存在: {dance_video}")
        return False
    if not os.path.exists(bgm_video):
        print(f"错误: bgm视频文件不存在: {bgm_video}")
        return False
    
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    # 生成输出文件名
    modular_output = os.path.join(output_dir, f"{sample_name}_modular.mp4")
    v2_output = os.path.join(output_dir, f"{sample_name}_v2.mp4")
    
    print(f"\n处理样本: {sample_name}")
    print(f"输入文件:")
    print(f"  dance: {dance_video}")
    print(f"  bgm: {bgm_video}")
    print(f"输出目录: {output_dir}")
    print("-" * 40)
    
    # 顺序处理而不是并行处理，避免内存翻倍
    print("\n步骤1: 顺序处理（避免内存问题）...")
    
    # 先处理modular版本
    print("\n处理modular版本...")
    modular_info = process_with_modular_optimized(dance_video, bgm_video, modular_output)
    modular_info['output_file'] = modular_output
    
    # 处理完成后强制垃圾回收
    gc.collect()
    time.sleep(2)  # 给系统时间释放内存
    
    # 再处理V2版本
    print("\n处理V2版本...")
    v2_info = process_with_v2_optimized(dance_video, bgm_video, v2_output)
    v2_info['output_file'] = v2_output
    
    # 最终垃圾回收
    gc.collect()
    final_memory = log_memory_usage("处理完成")
    
    # 显示结果
    print(f"\n步骤2: 处理结果")
    print("-" * 40)
    
    print(f"modular版本结果: {modular_info['success'] and '✅' or '❌'}")
    if modular_info['success']:
        print(f"  输出文件: {modular_output}")
        print(f"  对齐点: dance={modular_info['dance_alignment']}, bgm={modular_info['bgm_alignment']}")
        print(f"  置信度: {modular_info['confidence']}")
    else:
        print(f"  错误: {modular_info.get('error', '未知错误')}")
    
    print(f"\nV2版本结果: {v2_info['success'] and '✅' or '❌'}")
    if v2_info['success']:
        print(f"  输出文件: {v2_output}")
        print(f"  对齐点: dance={v2_info['dance_alignment']}, bgm={v2_info['bgm_alignment']}")
        print(f"  置信度: {v2_info['confidence']}")
    else:
        print(f"  错误: {v2_info.get('error', '未知错误')}")
    
    # 生成对比报告
    print(f"\n步骤3: 生成对比报告...")
    report_file = os.path.join(output_dir, f"{sample_name}_comparison_report.txt")
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(f"BeatSync 并行处理对比报告 - {sample_name}\n")
        f.write("=" * 60 + "\n")
        f.write(f"处理时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"输入文件:\n")
        f.write(f"  dance: {dance_video}\n")
        f.write(f"  bgm: {bgm_video}\n")
        f.write(f"内存使用: 开始={initial_memory:.2f}GB, 结束={final_memory:.2f}GB\n")
        f.write("=" * 60 + "\n\n")
        
        # modular版本结果
        f.write("modular版本处理结果:\n")
        f.write("-" * 30 + "\n")
        f.write(f"状态: {'成功' if modular_info['success'] else '失败'}\n")
        if modular_info['success']:
            f.write(f"输出文件: {modular_output}\n")
            f.write(f"对齐点: dance={modular_info['dance_alignment']}, bgm={modular_info['bgm_alignment']}\n")
            f.write(f"置信度: {modular_info['confidence']}\n")
        else:
            f.write(f"错误: {modular_info.get('error', '未知错误')}\n")
        
        f.write("\n")
        
        # V2版本结果
        f.write("V2版本处理结果:\n")
        f.write("-" * 30 + "\n")
        f.write(f"状态: {'成功' if v2_info['success'] else '失败'}\n")
        if v2_info['success']:
            f.write(f"输出文件: {v2_output}\n")
            f.write(f"对齐点: dance={v2_info['dance_alignment']}, bgm={v2_info['bgm_alignment']}\n")
            f.write(f"置信度: {v2_info['confidence']}\n")
        else:
            f.write(f"错误: {v2_info.get('error', '未知错误')}\n")
        
        f.write("\n")
        
        # 对比分析
        f.write("对比分析:\n")
        f.write("-" * 30 + "\n")
        if modular_info['success'] and v2_info['success']:
            f.write(f"两个版本都成功处理\n")
            f.write(f"对齐点差异:\n")
            f.write(f"  modular: dance={modular_info['dance_alignment']}, bgm={modular_info['bgm_alignment']}\n")
            f.write(f"  V2:      dance={v2_info['dance_alignment']}, bgm={v2_info['bgm_alignment']}\n")
            f.write(f"\n建议: 请观看两个输出视频，选择对齐效果更好的版本\n")
        elif modular_info['success']:
            f.write(f"只有modular版本成功处理\n")
            f.write(f"建议: 使用modular版本的输出视频\n")
        elif v2_info['success']:
            f.write(f"只有V2版本成功处理\n")
            f.write(f"建议: 使用V2版本的输出视频\n")
        else:
            f.write(f"两个版本都处理失败\n")
            f.write(f"建议: 检查输入文件或联系技术支持\n")
    
    print(f"✅ 对比报告已生成: {report_file}")
    
    # 最终结果
    success_count = sum([modular_info['success'], v2_info['success']])
    print(f"\n步骤4: 处理完成")
    print(f"成功处理: {success_count}/2 个版本")
    print(f"内存使用变化: {initial_memory:.2f}GB → {final_memory:.2f}GB")
    
    if success_count > 0:
        print(f"✅ 处理成功，请查看输出视频并选择最佳结果")
        print(f"📁 输出目录: {output_dir}")
        return True
    else:
        print(f"❌ 处理失败")
        return False

def main():
    parser = argparse.ArgumentParser(description='BeatSync 并行处理器 - 内存优化版本')
    parser.add_argument('--dance', required=True, help='dance视频文件路径')
    parser.add_argument('--bgm', required=True, help='bgm视频文件路径')
    parser.add_argument('--output-dir', required=True, help='输出目录路径')
    parser.add_argument('--sample-name', required=True, help='样本名称')
    
    args = parser.parse_args()
    
    success = process_beat_sync_parallel_optimized(args.dance, args.bgm, args.output_dir, args.sample_name)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
