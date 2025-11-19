#!/usr/bin/env python3
"""
BeatSync 并行处理器
同时使用modular版本和V2版本处理样本，生成两个输出视频供用户选择
"""

import os
import sys
import subprocess
import argparse
import tempfile
import shutil
import threading
import numpy as np
import soundfile as sf
import librosa
import re
from datetime import datetime
from typing import Tuple
from pathlib import Path

# 启用行缓冲，确保日志实时写出（不影响功能/算法）
try:
    sys.stdout.reconfigure(line_buffering=True)
    sys.stderr.reconfigure(line_buffering=True)
except Exception:
    pass

def extract_audio_from_video(video_path: str, output_path: str, sr: int = 44100) -> bool:
    """从视频中提取音频为 WAV 格式"""
    try:
        cmd = [
            'ffmpeg', '-y',
            '-i', video_path,
            '-vn', '-acodec', 'pcm_s16le', '-ar', str(sr), '-ac', '1',
            output_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.returncode == 0
    except:
        return False

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
    
    # 检查是否成功 - 扩展成功标志列表
    success_indicators = [
        '处理成功', 
        'success', 
        '完成', 
        '模块解耦精剪模式处理成功',
        'Badcase修复（裁剪版本）成功',  # V2版本成功标志
        'Badcase修复.*成功',  # V2版本成功标志（正则）
        '精剪视频已生成',
        '最终输出:',
        '最终裁剪视频创建成功'
    ]
    info['success'] = any(indicator in output_text for indicator in success_indicators)
    
    return info

def process_with_modular(dance_video: str, bgm_video: str, output_video: str) -> dict:
    """使用modular版本处理"""
    start_time = None
    try:
        print("  使用modular版本处理...")
        start_time = datetime.now()
        print(f"  [时间] 开始时间: {start_time.strftime('%H:%M:%S')}")
        # 获取项目根目录（脚本所在目录的父目录）
        script_dir = Path(__file__).parent.absolute()
        project_root = script_dir
        
        modular_script = project_root / "beatsync_fine_cut_modular.py"
        if not modular_script.exists():
            # 如果找不到，尝试当前工作目录
            modular_script = Path("beatsync_fine_cut_modular.py")
        
        cmd = [
            "python3", str(modular_script),
            "--dance", dance_video,
            "--bgm", bgm_video,
            "--output", output_video,
            "--fast-video",
            "--video-encode", "x264_fast",
            "--enable-cache",
            "--cache-dir", ".beatsync_cache",
            "--threads", "4",
            "--lib-threads", "1"
        ]
        
        print(f"  [命令] 执行命令: {' '.join(cmd[:3])} ... (参数已省略)")
        print(f"  [状态] 开始执行subprocess...")
        
        # 设置工作目录为项目根目录
        # 增加超时时间到1200秒（20分钟），适应Render免费层的性能限制
        start_time = datetime.now()
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=1200, cwd=str(project_root))
        end_time = datetime.now()
        elapsed = (end_time - start_time).total_seconds()
        print(f"  [时间] 完成时间: {end_time.strftime('%H:%M:%S')}, 耗时: {elapsed:.1f}秒")
        print(f"  [结果] 返回码: {result.returncode}")
        if result.stdout:
            print(f"  [输出] stdout长度: {len(result.stdout)}字符")
        if result.stderr:
            print(f"  [错误] stderr长度: {len(result.stderr)}字符")
            # 如果失败，打印stderr内容（前500字符）
            if result.returncode != 0:
                print(f"  [错误详情] stderr内容:")
                stderr_lines = result.stderr.strip().split('\n')
                for i, line in enumerate(stderr_lines[:10]):  # 只显示前10行
                    print(f"    {line}")
                if len(stderr_lines) > 10:
                    print(f"    ... (还有 {len(stderr_lines) - 10} 行)")
        info = extract_alignment_info(result.stdout, "modular版本")
        info['return_code'] = result.returncode
        info['stderr'] = result.stderr
        
        # 检查输出文件（modular版本必须输出最终文件，不接受中间文件）
        output_is_intermediate = '_module1_aligned' in output_video
        
        # 如果失败，提取错误信息
        if result.returncode != 0:
            # 优先从stderr提取错误信息
            if result.stderr:
                # 提取关键错误信息（前500字符）
                error_lines = result.stderr.strip().split('\n')
                # 查找包含"Error"、"error"、"失败"、"Exception"的行
                error_msg = None
                for line in error_lines:
                    if any(keyword in line.lower() for keyword in ['error', '失败', 'exception', 'traceback']):
                        error_msg = line.strip()
                        break
                if not error_msg and error_lines:
                    # 如果没有找到关键词，使用最后一行
                    error_msg = error_lines[-1].strip()
                if error_msg:
                    info['error'] = error_msg[:200]  # 限制长度
                else:
                    info['error'] = f"返回码: {result.returncode}, stderr: {result.stderr[:200]}"
            else:
                info['error'] = f"返回码: {result.returncode}，无错误输出"
        
        # 增强成功判断：如果返回码为0且输出文件存在，则认为成功
        # 注意：modular版本必须输出最终文件，不接受中间文件
        if result.returncode == 0 and os.path.exists(output_video) and os.path.getsize(output_video) > 0:
            # 检查是否是中间文件（modular版本可能生成中间文件）
            if output_is_intermediate:
                # 这是中间文件，不是最终输出，应该认为失败
                info['success'] = False
                if not info.get('error'):
                    info['error'] = '只生成了中间文件，未生成最终输出文件（模块2失败）'
                print(f"  ⚠️  警告: 检测到中间文件，但未找到最终输出文件")
                print(f"  ⚠️  中间文件: {output_video}")
                print(f"  ⚠️  这表示模块2（裁剪模块）失败")
            else:
                info['success'] = True
        elif result.returncode != 0:
            # 如果返回码不是0，检查是否有中间文件
            intermediate_file = output_video.replace('.mp4', '_module1_aligned.mp4')
            if os.path.exists(intermediate_file) and os.path.getsize(intermediate_file) > 0:
                if not info.get('error'):
                    info['error'] = f'模块2失败，只生成了中间文件（返回码: {result.returncode}）'
                print(f"  ⚠️  警告: 返回码{result.returncode}，但检测到中间文件")
                print(f"  ⚠️  中间文件: {intermediate_file}")
                print(f"  ⚠️  这表示模块2（裁剪模块）失败")
            # 即使extract_alignment_info认为成功，如果返回码不是0，也应该认为失败
            if info.get('success') and result.returncode != 0:
                info['success'] = False
                if not info.get('error'):
                    info['error'] = f'返回码: {result.returncode}，处理失败'
        
        return info
        
    except subprocess.TimeoutExpired as e:
        elapsed = (datetime.now() - start_time).total_seconds() if start_time else 0
        print(f"  [错误] modular版本处理超时（已运行{elapsed:.1f}秒）")
        return {'program': 'modular版本', 'success': False, 'error': f'超时（已运行{elapsed:.1f}秒，限制1200秒）'}
    except Exception as e:
        return {'program': 'modular版本', 'success': False, 'error': str(e)}

def process_with_v2(dance_video: str, bgm_video: str, output_video: str) -> dict:
    """使用V2版本处理"""
    start_time = None
    try:
        print("  使用V2版本处理...")
        start_time = datetime.now()
        print(f"  [时间] 开始时间: {start_time.strftime('%H:%M:%S')}")
        # 获取项目根目录（脚本所在目录的父目录）
        script_dir = Path(__file__).parent.absolute()
        project_root = script_dir
        
        v2_script = project_root / "beatsync_badcase_fix_trim_v2.py"
        if not v2_script.exists():
            # 如果找不到，尝试当前工作目录
            v2_script = Path("beatsync_badcase_fix_trim_v2.py")
        
        cmd = [
            "python3", str(v2_script),
            "--dance", dance_video,
            "--bgm", bgm_video,
            "--output", output_video,
            "--fast-video",
            "--video-encode", "x264_fast",
            "--enable-cache",
            "--cache-dir", ".beatsync_cache",
            "--threads", "4",
            "--lib-threads", "1"
        ]
        
        print(f"  [命令] 执行命令: {' '.join(cmd[:3])} ... (参数已省略)")
        print(f"  [状态] 开始执行subprocess...")
        
        # 设置工作目录为项目根目录
        # 增加超时时间到1200秒（20分钟），适应Render免费层的性能限制
        start_time = datetime.now()
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=1200, cwd=str(project_root))
        end_time = datetime.now()
        elapsed = (end_time - start_time).total_seconds()
        print(f"  [时间] 完成时间: {end_time.strftime('%H:%M:%S')}, 耗时: {elapsed:.1f}秒")
        print(f"  [结果] 返回码: {result.returncode}")
        if result.stdout:
            print(f"  [输出] stdout长度: {len(result.stdout)}字符")
        if result.stderr:
            print(f"  [错误] stderr长度: {len(result.stderr)}字符")
            # 如果失败，打印stderr内容（前500字符）
            if result.returncode != 0:
                print(f"  [错误详情] stderr内容:")
                stderr_lines = result.stderr.strip().split('\n')
                for i, line in enumerate(stderr_lines[:10]):  # 只显示前10行
                    print(f"    {line}")
                if len(stderr_lines) > 10:
                    print(f"    ... (还有 {len(stderr_lines) - 10} 行)")
        info = extract_alignment_info(result.stdout, "V2版本")
        info['return_code'] = result.returncode
        info['stderr'] = result.stderr
        
        # 如果失败，提取错误信息
        if result.returncode != 0:
            # 优先从stderr提取错误信息
            if result.stderr:
                # 提取关键错误信息（前500字符）
                error_lines = result.stderr.strip().split('\n')
                # 查找包含"Error"、"error"、"失败"、"Exception"的行
                error_msg = None
                for line in error_lines:
                    if any(keyword in line.lower() for keyword in ['error', '失败', 'exception', 'traceback']):
                        error_msg = line.strip()
                        break
                if not error_msg and error_lines:
                    # 如果没有找到关键词，使用最后一行
                    error_msg = error_lines[-1].strip()
                if error_msg:
                    info['error'] = error_msg[:200]  # 限制长度
                else:
                    info['error'] = f"返回码: {result.returncode}, stderr: {result.stderr[:200]}"
            else:
                info['error'] = f"返回码: {result.returncode}，无错误输出"
        
        # 增强成功判断：如果返回码为0且输出文件存在，则认为成功
        if result.returncode == 0 and os.path.exists(output_video) and os.path.getsize(output_video) > 0:
            info['success'] = True
        
        return info
        
    except subprocess.TimeoutExpired as e:
        elapsed = (datetime.now() - start_time).total_seconds() if 'start_time' in locals() else 0
        print(f"  [错误] V2版本处理超时（已运行{elapsed:.1f}秒）")
        return {'program': 'V2版本', 'success': False, 'error': f'超时（已运行{elapsed:.1f}秒，限制1200秒）'}
    except Exception as e:
        return {'program': 'V2版本', 'success': False, 'error': str(e)}

def process_beat_sync_parallel(dance_video: str, bgm_video: str, output_dir: str, sample_name: str, parallel: bool = False) -> bool:
    """
    处理主函数（支持串行和并行模式）
    
    参数:
        dance_video: dance视频路径
        bgm_video: bgm视频路径
        output_dir: 输出目录
        sample_name: 样本名称
        parallel: 是否使用并行模式（默认False，使用串行模式）
                  - False: 串行模式（适合资源受限环境，如Render免费层）
                  - True: 并行模式（适合资源充足环境，需要升级服务器后使用）
    """
    mode_name = "并行处理器" if parallel else "串行处理器"
    print("=" * 60)
    print(f"BeatSync {mode_name}")
    print("=" * 60)
    
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
    
    # 处理（串行或并行）
    mode_text = "并行处理" if parallel else "串行处理"
    print(f"\n步骤1: {mode_text}...")
    
    # 使用线程真正并行处理两个版本
    # 使用线程安全的字典存储结果
    modular_result = {}
    v2_result = {}
    result_lock = threading.Lock()
    
    def modular_thread():
        """Modular版本处理线程"""
        try:
            result = process_with_modular(dance_video, bgm_video, modular_output)
            result['output_file'] = modular_output
            with result_lock:
                modular_result.update(result)
            print(f"  ✅ modular版本处理完成: {'成功' if result.get('success') else '失败'}")
        except Exception as e:
            error_info = {
                'program': 'modular版本',
                'success': False,
                'error': str(e)
            }
            with result_lock:
                modular_result.update(error_info)
            print(f"  ❌ modular版本处理异常: {str(e)}")
    
    def v2_thread():
        """V2版本处理线程"""
        try:
            result = process_with_v2(dance_video, bgm_video, v2_output)
            result['output_file'] = v2_output
            with result_lock:
                v2_result.update(result)
            print(f"  ✅ V2版本处理完成: {'成功' if result.get('success') else '失败'}")
        except Exception as e:
            error_info = {
                'program': 'V2版本',
                'success': False,
                'error': str(e)
            }
            with result_lock:
                v2_result.update(error_info)
            print(f"  ❌ V2版本处理异常: {str(e)}")
    
    # 根据parallel参数选择串行或并行模式
    if parallel:
        # 并行处理模式（适合资源充足环境）
        print("  启动modular版本和V2版本并行处理...")
        t1 = threading.Thread(target=modular_thread, daemon=False)
        t2 = threading.Thread(target=v2_thread, daemon=False)
        
        t1.start()
        t2.start()
        
        # 等待两个线程完成（即使一个失败，另一个也会继续）
        t1.join()
        t2.join()
    else:
        # 串行处理模式（适合资源受限环境，如Render免费层）
        # Render免费层资源有限，并行处理会导致资源竞争，反而更慢
        # 串行处理：先运行V2版本（通常更快），再运行modular版本
        print("  启动V2版本处理（串行模式，避免资源竞争）...")
        v2_thread()
        
        print("  启动modular版本处理（串行模式）...")
        modular_thread()
    
    # 获取结果（线程安全）
    with result_lock:
        modular_info = modular_result.copy()
        v2_info = v2_result.copy()
    
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
    
    if success_count > 0:
        print(f"✅ 处理成功，请查看输出视频并选择最佳结果")
        print(f"📁 输出目录: {output_dir}")
        return True
    else:
        print(f"❌ 处理失败")
        return False

def main():
    parser = argparse.ArgumentParser(description='BeatSync 处理器（支持串行和并行模式）')
    parser.add_argument('--dance', required=True, help='dance视频文件路径')
    parser.add_argument('--bgm', required=True, help='bgm视频文件路径')
    parser.add_argument('--output-dir', required=True, help='输出目录路径')
    parser.add_argument('--sample-name', required=True, help='样本名称')
    parser.add_argument('--parallel', action='store_true', help='使用并行模式（默认：串行模式，适合资源受限环境）')
    
    args = parser.parse_args()
    
    success = process_beat_sync_parallel(args.dance, args.bgm, args.output_dir, args.sample_name, parallel=args.parallel)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
