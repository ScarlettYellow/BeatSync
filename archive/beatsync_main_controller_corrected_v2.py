#!/usr/bin/env python3
"""
BeatSync 主控程序 - 修正版V2
实现分支处理逻辑，支持所有case类型：
- 第一类badcase: 使用beatsync_fine_cut_modular.py
- 第二类badcase: 使用beatsync_badcase_fix_trim_v2.py
- 正常case: 使用beatsync_fine_cut_modular.py
"""

import os
import sys
import subprocess
import argparse
import tempfile
import shutil
import numpy as np
import soundfile as sf
import librosa
from typing import Tuple

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

def find_beat_alignment(ref_audio: np.ndarray, mov_audio: np.ndarray, sr: int = 22050) -> Tuple[int, int, float]:
    """使用节拍检测找到最佳对齐位置（V2版本简化算法）"""
    try:
        # 转换为单声道
        if ref_audio.ndim > 1:
            ref_audio = librosa.to_mono(ref_audio.T)
        if mov_audio.ndim > 1:
            mov_audio = librosa.to_mono(mov_audio.T)
        
        # 检测节拍点
        ref_tempo, ref_beats = librosa.beat.beat_track(y=ref_audio, sr=sr, units='time')
        mov_tempo, mov_beats = librosa.beat.beat_track(y=mov_audio, sr=sr, units='time')
        
        print(f"节拍检测:")
        print(f"  dance: {len(ref_beats)} 个节拍点, BPM ≈ {ref_tempo[0]:.1f}")
        print(f"  bgm: {len(mov_beats)} 个节拍点, BPM ≈ {mov_tempo[0]:.1f}")
        
        # 检查 BPM 匹配度
        tempo_ratio = min(ref_tempo[0], mov_tempo[0]) / max(ref_tempo[0], mov_tempo[0])
        if tempo_ratio < 0.85:
            print(f"  警告: BPM 差异较大 ({ref_tempo[0]:.1f} vs {mov_tempo[0]:.1f})")
        
        # 使用滑动窗口搜索最佳对齐
        window_size = 2.0  # 2秒窗口
        max_offset = min(len(ref_audio), len(mov_audio)) / sr * 0.4  # 最多搜索40%重叠
        
        best_score = 0
        best_ref_start = 0
        best_mov_start = 0
        
        print(f"搜索对齐位置 (最大偏移: {max_offset:.1f}秒)...")
        
        for ref_offset in np.arange(0, max_offset, 0.1):
            ref_start = int(ref_offset * sr)
            ref_end = ref_start + int(window_size * sr)
            
            if ref_end > len(ref_audio):
                continue
                
            for mov_offset in np.arange(0, max_offset, 0.1):
                mov_start = int(mov_offset * sr)
                mov_end = mov_start + int(window_size * sr)
                
                if mov_end > len(mov_audio):
                    continue
                
                # 提取音频段
                ref_seg = ref_audio[ref_start:ref_end]
                mov_seg = mov_audio[mov_start:mov_end]
                
                # 计算相关性
                try:
                    corr = np.corrcoef(ref_seg.flatten(), mov_seg.flatten())[0, 1]
                    if np.isnan(corr):
                        corr = 0
                except:
                    corr = 0
                
                if corr > best_score:
                    best_score = corr
                    best_ref_start = ref_offset
                    best_mov_start = mov_offset
        
        print(f"对齐结果:")
        print(f"  dance 节拍点: {best_ref_start:.2f}s")
        print(f"  bgm 节拍点: {best_mov_start:.2f}s")
        print(f"  置信度: {best_score:.4f}")
        
        return int(best_ref_start * sr), int(best_mov_start * sr), best_score
        
    except Exception as e:
        print(f"节拍检测失败: {e}")
        return 0, 0, 0.0

def detect_badcase_type(dance_video: str, bgm_video: str, sr: int = 22050) -> Tuple[str, float]:
    """检测badcase类型"""
    try:
        # 创建临时目录
        temp_dir = tempfile.mkdtemp()
        
        # 提取音频
        dance_audio_path = os.path.join(temp_dir, "dance.wav")
        bgm_audio_path = os.path.join(temp_dir, "bgm.wav")
        
        if not extract_audio_from_video(dance_video, dance_audio_path, sr):
            print("dance音频提取失败")
            return "ERROR", 0.0
            
        if not extract_audio_from_video(bgm_video, bgm_audio_path, sr):
            print("bgm音频提取失败")
            return "ERROR", 0.0
        
        # 读取音频
        dance_audio, _ = sf.read(dance_audio_path)
        bgm_audio, _ = sf.read(bgm_audio_path)
        
        # 节拍对齐
        dance_start, bgm_start, confidence = find_beat_alignment(dance_audio, bgm_audio, sr)
        
        # 转换为时间（与V2版本定义一致）
        T1 = dance_start / sr  # dance视频在原始音乐中的开始时间
        T2 = bgm_start / sr    # bgm视频在原始音乐中的开始时间
        
        print(f"时间分析:")
        print(f"  T1 (dance开始): {T1:.2f}s")
        print(f"  T2 (bgm开始): {T2:.2f}s")
        
        # 判断badcase类型
        gap_duration = abs(T1 - T2)
        
        if T1 > T2:
            print(f"检测到第一类badcase (T1 > T2), 时间差: {gap_duration:.2f}s")
            return "T1_GT_T2", gap_duration
        elif T2 > T1:
            print(f"检测到第二类badcase (T2 > T1), 时间差: {gap_duration:.2f}s")
            return "T2_GT_T1", gap_duration
        else:
            print("检测到正常case (T1 ≈ T2)")
            return "NORMAL", gap_duration
            
    except Exception as e:
        print(f"badcase检测失败: {e}")
        return "ERROR", 0.0
    finally:
        # 清理临时目录
        if 'temp_dir' in locals():
            shutil.rmtree(temp_dir, ignore_errors=True)

def process_first_type_badcase(dance_video: str, bgm_video: str, output_video: str) -> bool:
    """处理第一类badcase - 使用modular版本"""
    try:
        print("使用modular版本处理第一类badcase...")
        cmd = [
            "python3", "beatsync_fine_cut_modular.py",
            "--dance", dance_video,
            "--bgm", bgm_video,
            "--output", output_video
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.returncode == 0
    except Exception as e:
        print(f"第一类badcase处理失败: {e}")
        return False

def process_second_type_badcase(dance_video: str, bgm_video: str, output_video: str) -> bool:
    """处理第二类badcase - 使用V2版本"""
    try:
        print("使用V2版本处理第二类badcase...")
        cmd = [
            "python3", "beatsync_badcase_fix_trim_v2.py",
            "--dance", dance_video,
            "--bgm", bgm_video,
            "--output", output_video
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.returncode == 0
    except Exception as e:
        print(f"第二类badcase处理失败: {e}")
        return False

def process_normal_case(dance_video: str, bgm_video: str, output_video: str) -> bool:
    """处理正常case - 使用modular版本"""
    try:
        print("使用modular版本处理正常case...")
        cmd = [
            "python3", "beatsync_fine_cut_modular.py",
            "--dance", dance_video,
            "--bgm", bgm_video,
            "--output", output_video
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.returncode == 0
    except Exception as e:
        print(f"正常case处理失败: {e}")
        return False

def process_beat_sync(dance_video: str, bgm_video: str, output_video: str) -> bool:
    """主处理函数"""
    print("=" * 60)
    print("BeatSync 主控程序 - 修正版V2")
    print("=" * 60)
    
    # 检查输入文件
    if not os.path.exists(dance_video):
        print(f"错误: dance视频文件不存在: {dance_video}")
        return False
    if not os.path.exists(bgm_video):
        print(f"错误: bgm视频文件不存在: {bgm_video}")
        return False
    
    # 检测badcase类型
    print("\n步骤1: 检测badcase类型...")
    badcase_type, gap_duration = detect_badcase_type(dance_video, bgm_video)
    
    # 根据badcase类型选择处理程序
    print(f"\n步骤2: 选择处理程序...")
    success = False
    
    if badcase_type == "T1_GT_T2":
        print("检测到第一类badcase，使用modular版本处理...")
        success = process_first_type_badcase(dance_video, bgm_video, output_video)
    elif badcase_type == "T2_GT_T1":
        print("检测到第二类badcase，使用V2版本处理...")
        success = process_second_type_badcase(dance_video, bgm_video, output_video)
    else:
        print("检测到正常case，使用modular版本处理...")
        success = process_normal_case(dance_video, bgm_video, output_video)
    
    # 输出结果
    print(f"\n步骤3: 处理完成")
    if success:
        print(f"✅ 处理成功: {output_video}")
    else:
        print(f"❌ 处理失败")
    
    return success

def main():
    parser = argparse.ArgumentParser(description='BeatSync 主控程序 - 修正版V2')
    parser.add_argument('--dance', required=True, help='dance视频文件路径')
    parser.add_argument('--bgm', required=True, help='bgm视频文件路径')
    parser.add_argument('--output', required=True, help='输出视频文件路径')
    
    args = parser.parse_args()
    
    success = process_beat_sync(args.dance, args.bgm, args.output)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
