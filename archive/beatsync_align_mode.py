#!/usr/bin/env python3
"""
BeatSync - 仅对齐模式 (基于已验证的beatsync_working.py)
保持两个视频的完整时长，输出一个合成视频：dance视频 + BGM音频
"""

import os
import sys
import argparse
import subprocess
import tempfile
from typing import Tuple
import numpy as np
import soundfile as sf
import librosa


def extract_audio_from_video(video_path: str, output_path: str, sr: int = 44100) -> bool:
    """从视频中提取音频为 WAV 格式"""
    try:
        cmd = [
            "ffmpeg", "-y",
            "-i", video_path,
            "-vn",  # 禁用视频
            "-acodec", "pcm_s16le",  # 16-bit PCM
            "-ar", str(sr),  # 采样率
            "-ac", "2",  # 双声道
            output_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.returncode == 0
    except Exception as e:
        print(f"音频提取失败: {e}")
        return False


def find_beat_alignment(ref_audio: np.ndarray, mov_audio: np.ndarray, sr: int) -> Tuple[int, int, float]:
    """使用节拍检测找到最佳对齐位置 (复用已验证的逻辑)"""
    try:
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
        print(f"  dance 开始: {best_ref_start:.2f}s")
        print(f"  bgm 开始: {best_mov_start:.2f}s")
        print(f"  置信度: {best_score:.4f}")
        
        return int(best_ref_start * sr), int(best_mov_start * sr), best_score
        
    except Exception as e:
        print(f"节拍检测失败: {e}")
        return 0, 0, 0.0


def create_aligned_audio(ref_audio: np.ndarray, mov_audio: np.ndarray, 
                        ref_start: int, mov_start: int, sr: int) -> np.ndarray:
    """创建对齐后的音频 - 仅对齐模式"""
    print("创建对齐音频...")
    
    # 计算重叠长度
    ref_remaining = len(ref_audio) - ref_start
    mov_remaining = len(mov_audio) - mov_start
    overlap_len = min(ref_remaining, mov_remaining)
    
    print(f"重叠区域: {overlap_len/sr:.2f}秒")
    print(f"对齐信息: dance从{ref_start/sr:.2f}s开始, bgm从{mov_start/sr:.2f}s开始")
    
    # 计算时间偏移：bgm需要延迟多少才能与dance对齐
    time_offset = ref_start - mov_start  # dance_start - bgm_start
    offset_samples = int(time_offset)
    
    print(f"时间偏移: {time_offset/sr:.2f}秒 (bgm需要延迟{time_offset/sr:.2f}秒)")
    
    # 仅对齐模式：创建一个与ref_audio相同长度的输出音频
    output_audio = np.zeros_like(ref_audio)
    
    if offset_samples >= 0:
        # bgm需要延迟播放（正偏移）
        # 在输出音频中，从offset_samples位置开始放置bgm音频
        if offset_samples < len(output_audio):
            # 计算可以放置的bgm音频长度
            available_len = len(output_audio) - offset_samples
            bgm_len = min(available_len, len(mov_audio))
            
            # 放置bgm音频
            output_audio[offset_samples:offset_samples + bgm_len] = mov_audio[:bgm_len]
            
            print(f"音频放置: 从{offset_samples/sr:.2f}s开始，放置{bgm_len/sr:.2f}s的bgm音频")
    else:
        # bgm需要提前播放（负偏移，实际上是从bgm的某个位置开始）
        # 这种情况比较复杂，暂时处理为从bgm开始位置播放
        bgm_len = min(len(output_audio), len(mov_audio))
        output_audio[:bgm_len] = mov_audio[:bgm_len]
        
        print(f"音频放置: 从0s开始，放置{bgm_len/sr:.2f}s的bgm音频")
    
    return output_audio


def process_video_audio_sync(dance_video: str, bgm_video: str, output_video: str, sr: int = 44100) -> bool:
    """处理视频音频同步 (基于已验证的逻辑)"""
    print(f"BeatSync 仅对齐模式开始处理...")
    print(f"  dance: {dance_video}")
    print(f"  bgm: {bgm_video}")
    print(f"  输出: {output_video}")
    
    # 创建临时目录
    temp_dir = tempfile.mkdtemp()
    print(f"临时目录: {temp_dir}")
    
    try:
        # 提取音频
        print("提取音频...")
        dance_audio_path = os.path.join(temp_dir, "dance.wav")
        bgm_audio_path = os.path.join(temp_dir, "bgm.wav")
        
        if not extract_audio_from_video(dance_video, dance_audio_path, sr):
            print("dance音频提取失败")
            return False
            
        if not extract_audio_from_video(bgm_video, bgm_audio_path, sr):
            print("bgm音频提取失败")
            return False
        
        # 读取音频
        dance_audio, _ = sf.read(dance_audio_path)
        bgm_audio, _ = sf.read(bgm_audio_path)
        
        print(f"音频长度: dance={len(dance_audio)/sr:.2f}s, bgm={len(bgm_audio)/sr:.2f}s")
        
        # 转换为单声道进行节拍检测
        if dance_audio.ndim > 1:
            dance_mono = librosa.to_mono(dance_audio.T)
        else:
            dance_mono = dance_audio
            
        if bgm_audio.ndim > 1:
            bgm_mono = librosa.to_mono(bgm_audio.T)
        else:
            bgm_mono = bgm_audio
        
        # 节拍检测对齐
        ref_start, mov_start, confidence = find_beat_alignment(dance_mono, bgm_mono, sr)
        
        # 创建对齐音频
        aligned_audio = create_aligned_audio(dance_audio, bgm_audio, ref_start, mov_start, sr)
        
        # 保存对齐后的音频
        aligned_audio_path = os.path.join(temp_dir, "aligned.wav")
        sf.write(aligned_audio_path, aligned_audio, sr, subtype="PCM_16")
        
        print(f"音频处理完成:")
        print(f"  最终音频: 来自BGM视频 ({len(aligned_audio)/sr:.2f}s)")
        
        # 合成视频
        print("合成视频...")
        
        cmd = [
            "ffmpeg", "-y",
            "-i", dance_video,  # 视频源
            "-i", aligned_audio_path,  # 音频源
            "-c:v", "copy",  # 复制视频流
            "-c:a", "aac",  # 音频编码
            "-map", "0:v:0",  # 映射视频流
            "-map", "1:a:0",  # 映射音频流
            "-shortest",  # 以最短的流为准
            output_video
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"视频合成完成: {output_video}")
            else:
                print(f"视频合成失败: {result.stderr}")
                return False
        except Exception as e:
            print(f"视频合成异常: {e}")
            return False
        
        print("完成!")
        return True
        
    finally:
        # 清理临时目录
        import shutil
        shutil.rmtree(temp_dir)
        print("临时文件已清理")


def main():
    parser = argparse.ArgumentParser(description='BeatSync - 仅对齐模式 (基于已验证逻辑)')
    parser.add_argument('--dance', required=True, help='dance视频文件路径')
    parser.add_argument('--bgm', required=True, help='bgm视频文件路径')
    parser.add_argument('--output', required=True, help='输出视频路径')
    parser.add_argument('--sample-rate', type=int, default=44100, help='音频采样率')
    
    args = parser.parse_args()
    
    # 检查输入文件
    if not os.path.exists(args.dance):
        print(f"错误: dance视频文件不存在: {args.dance}")
        sys.exit(1)
        
    if not os.path.exists(args.bgm):
        print(f"错误: bgm视频文件不存在: {args.bgm}")
        sys.exit(1)
    
    # 检查ffmpeg
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("错误: 未找到ffmpeg，请先安装ffmpeg")
        sys.exit(1)
    
    # 处理视频
    success = process_video_audio_sync(
        args.dance, args.bgm, 
        args.output, 
        args.sample_rate
    )
    
    if success:
        print("处理成功!")
        sys.exit(0)
    else:
        print("处理失败!")
        sys.exit(1)


if __name__ == "__main__":
    main()
