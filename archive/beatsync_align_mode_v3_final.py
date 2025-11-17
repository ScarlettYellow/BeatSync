#!/usr/bin/env python3
"""
BeatSync 对齐模式 - 最终优化版
专门针对第二类badcase优化，优先考虑bgm=0s的情况
"""

import os
import sys
import subprocess
import tempfile
import numpy as np
import librosa
import argparse
from typing import Tuple


def extract_audio_optimized(video_path: str, output_path: str, max_duration: float = 30.0) -> bool:
    """优化的音频提取 - 只提取前30秒进行节拍检测"""
    cmd = [
        'ffmpeg', '-y', '-i', video_path,
        '-vn', '-acodec', 'pcm_s16le', '-ar', '22050', '-ac', '1',  # 降低采样率
        '-t', str(max_duration),  # 限制时长
        output_path
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode == 0


def fast_beat_track(audio: np.ndarray, sr: int) -> Tuple[float, np.ndarray]:
    """快速节拍检测 - 使用更快的参数"""
    try:
        tempo, beats = librosa.beat.beat_track(
            y=audio, 
            sr=sr, 
            units='time',
            hop_length=512,
            start_bpm=120,
            tightness=100
        )
        return tempo[0] if len(tempo) > 0 else 120.0, beats
    except Exception as e:
        print(f"  节拍检测失败: {e}")
        return 120.0, np.array([])


def ultra_fast_correlation(ref_audio: np.ndarray, mov_audio: np.ndarray, 
                          ref_start: int, mov_start: int, sr: int) -> float:
    """超快速相关性计算"""
    window_samples = int(2.0 * sr)  # 2秒窗口
    
    ref_start_idx = ref_start
    ref_end_idx = ref_start_idx + window_samples
    mov_start_idx = mov_start
    mov_end_idx = mov_start_idx + window_samples
    
    # 检查边界
    if (ref_end_idx > len(ref_audio) or mov_end_idx > len(mov_audio) or
        ref_start_idx < 0 or mov_start_idx < 0):
        return 0.0
    
    # 提取音频段
    ref_seg = ref_audio[ref_start_idx:ref_end_idx]
    mov_seg = mov_audio[mov_start_idx:mov_end_idx]
    
    # 确保长度一致
    min_len = min(len(ref_seg), len(mov_seg))
    if min_len == 0:
        return 0.0
    
    ref_seg = ref_seg[:min_len]
    mov_seg = mov_seg[:min_len]
    
    # 超快速相关性计算
    try:
        ref_norm = ref_seg - np.mean(ref_seg)
        mov_norm = mov_seg - np.mean(mov_seg)
        
        numerator = np.sum(ref_norm * mov_norm)
        denominator = np.sqrt(np.sum(ref_norm**2) * np.sum(mov_norm**2))
        
        if denominator == 0:
            return 0.0
        else:
            return numerator / denominator
            
    except:
        return 0.0


def find_beat_alignment_final(ref_audio: np.ndarray, mov_audio: np.ndarray, sr: int) -> Tuple[int, int, float]:
    """
    最终优化的节拍对齐算法
    专门针对第二类badcase，优先考虑bgm=0s的情况
    """
    try:
        print("使用最终优化的节拍对齐算法...")
        
        # 快速节拍检测
        print("快速节拍检测...")
        ref_tempo, ref_beats = fast_beat_track(ref_audio, sr)
        mov_tempo, mov_beats = fast_beat_track(mov_audio, sr)
        
        print(f"节拍检测:")
        print(f"  dance: {len(ref_beats)} 个节拍点, BPM ≈ {ref_tempo:.1f}")
        print(f"  bgm: {len(mov_beats)} 个节拍点, BPM ≈ {mov_tempo:.1f}")
        
        # 检查 BPM 匹配度
        tempo_ratio = min(ref_tempo, mov_tempo) / max(ref_tempo, mov_tempo)
        if tempo_ratio < 0.85:
            print(f"  警告: BPM 差异较大 ({ref_tempo:.1f} vs {mov_tempo:.1f})")
        
        # 搜索参数
        max_offset = min(len(ref_audio), len(mov_audio)) / sr * 0.4
        step_size = 0.2
        
        best_score = 0
        best_ref_start = 0
        best_mov_start = 0
        
        print(f"最终搜索 (最大偏移: {max_offset:.1f}s, 步长: {step_size}s)...")
        
        search_count = 0
        
        # 两阶段搜索策略
        # 第一阶段：优先搜索bgm=0s的情况
        print("  第一阶段：搜索bgm=0s的情况...")
        mov_offset = 0  # bgm从0开始
        for ref_offset in np.arange(0, max_offset, step_size):
            ref_start = int(ref_offset * sr)
            mov_start = int(mov_offset * sr)
            search_count += 1
            
            score = ultra_fast_correlation(ref_audio, mov_audio, ref_start, mov_start, sr)
            
            if score > best_score:
                best_score = score
                best_ref_start = ref_offset
                best_mov_start = mov_offset
                print(f"    找到更好的对齐点: dance={ref_offset:.2f}s, bgm={mov_offset:.2f}s, 得分={score:.4f}")
        
        # 第二阶段：如果第一阶段结果不够好，搜索其他情况
        if best_score < 0.12:  # 降低阈值，更倾向于选择bgm=0s的结果
            print(f"  第二阶段：第一阶段得分较低({best_score:.4f})，搜索其他情况...")
            for ref_offset in np.arange(0, max_offset, step_size):
                ref_start = int(ref_offset * sr)
                
                for mov_offset in np.arange(step_size, max_offset, step_size):  # 跳过mov_offset=0
                    mov_start = int(mov_offset * sr)
                    search_count += 1
                    
                    score = ultra_fast_correlation(ref_audio, mov_audio, ref_start, mov_start, sr)
                    
                    if score > best_score:
                        best_score = score
                        best_ref_start = ref_offset
                        best_mov_start = mov_offset
                        print(f"    找到更好的对齐点: dance={ref_offset:.2f}s, bgm={mov_offset:.2f}s, 得分={score:.4f}")
        
        print(f"搜索完成，共检查 {search_count} 个位置")
        print(f"对齐结果:")
        print(f"  dance 开始: {best_ref_start:.2f}s")
        print(f"  bgm 开始: {best_mov_start:.2f}s")
        print(f"  综合得分: {best_score:.4f}")
        
        return int(best_ref_start * sr), int(best_mov_start * sr), best_score
        
    except Exception as e:
        print(f"最终节拍检测失败: {e}")
        return 0, 0, 0.0


def align_mode_final(dance_video: str, bgm_video: str, output_video: str) -> bool:
    """最终优化的对齐模式主函数"""
    print("BeatSync 最终优化对齐模式开始处理...")
    print(f"  dance: {dance_video}")
    print(f"  bgm: {bgm_video}")
    print(f"  输出: {output_video}")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # 优化的音频提取
        dance_audio_path = os.path.join(temp_dir, "dance.wav")
        bgm_audio_path = os.path.join(temp_dir, "bgm.wav")
        
        print("提取音频片段（前30秒）...")
        if not extract_audio_optimized(dance_video, dance_audio_path, 30.0):
            print("提取dance音频失败")
            return False
        
        if not extract_audio_optimized(bgm_video, bgm_audio_path, 30.0):
            print("提取bgm音频失败")
            return False
        
        # 加载音频
        print("加载音频...")
        dance_audio, sr = librosa.load(dance_audio_path, sr=22050)
        bgm_audio, _ = librosa.load(bgm_audio_path, sr=22050)
        
        print(f"音频长度: dance={len(dance_audio)/sr:.2f}s, bgm={len(bgm_audio)/sr:.2f}s")
        
        # 最终优化的节拍对齐
        ref_start, mov_start, confidence = find_beat_alignment_final(dance_audio, bgm_audio, sr)
        
        if confidence < 0.05:
            print("对齐置信度过低，处理失败")
            return False
        
        # 将对齐位置转换回原始采样率
        ref_start_44k = int(ref_start * 44100 / sr)
        mov_start_44k = int(mov_start * 44100 / sr)
        
        print(f"对齐位置转换: dance={ref_start_44k/44100:.2f}s, bgm={mov_start_44k/44100:.2f}s")
        
        # 创建最终视频 - 正确处理时间对齐，用静音填充前面的区间
        print("创建最终视频...")
        
        # 计算时间偏移：dance开始时间 - bgm开始时间
        time_offset = ref_start_44k/44100 - mov_start_44k/44100
        print(f"时间偏移: {time_offset:.3f}s (bgm需要延迟{time_offset:.3f}s)")
        
        if time_offset > 0:
            # dance开始时间 > bgm开始时间，创建静音+bgm的组合音频
            cmd = [
                'ffmpeg', '-y',
                '-i', dance_video,
                '-i', bgm_video,
                '-filter_complex', 
                f'[1:a]atrim=start={mov_start_44k/44100:.3f}[bgm_trim];'
                f'[bgm_trim]adelay={int(time_offset*1000)}[bgm_delayed];'
                f'[bgm_delayed]volume=0:enable=\'lt(t,{time_offset:.3f})\'[aout]',
                '-map', '0:v:0',  # 使用dance视频
                '-map', '[aout]',  # 使用处理后的音频
                '-c:v', 'copy',
                '-c:a', 'aac',
                '-shortest',
                output_video
            ]
        else:
            # bgm开始时间 >= dance开始时间，直接使用bgm
            cmd = [
                'ffmpeg', '-y',
                '-i', dance_video,
                '-i', bgm_video,
                '-filter_complex', 
                f'[1:a]atrim=start={mov_start_44k/44100:.3f}[aout]',
                '-map', '0:v:0',  # 使用dance视频
                '-map', '[aout]',  # 使用处理后的bgm音频
                '-c:v', 'copy',
                '-c:a', 'aac',
                '-shortest',
                output_video
            ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"创建最终视频失败: {result.stderr}")
            return False
        
        print("最终优化对齐模式处理成功!")
        return True


def main():
    parser = argparse.ArgumentParser(description='BeatSync 最终优化对齐模式')
    parser.add_argument('--dance', required=True, help='Dance视频路径')
    parser.add_argument('--bgm', required=True, help='BGM视频路径')
    parser.add_argument('--output', required=True, help='输出视频路径')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.dance):
        print(f"Dance视频不存在: {args.dance}")
        return 1
    
    if not os.path.exists(args.bgm):
        print(f"BGM视频不存在: {args.bgm}")
        return 1
    
    success = align_mode_final(args.dance, args.bgm, args.output)
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
