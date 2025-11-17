#!/usr/bin/env python3
"""
BeatSync Badcase修复程序
自动检测T1 > T2类型的badcases并修复
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
    """使用节拍检测找到最佳对齐位置"""
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
        print(f"  dance 节拍点: {best_ref_start:.2f}s")
        print(f"  bgm 节拍点: {best_mov_start:.2f}s")
        print(f"  置信度: {best_score:.4f}")
        
        return int(best_ref_start * sr), int(best_mov_start * sr), best_score
        
    except Exception as e:
        print(f"节拍检测失败: {e}")
        return 0, 0, 0.0

def detect_badcase_type(ref_start: int, mov_start: int, sr: int) -> str:
    """检测badcase类型"""
    # 重新理解：T1和T2是相对于各自视频开始点的节拍点时间
    # T1 = dance视频中节拍点之前的时长
    # T2 = bgm视频中节拍点之前的时长
    T1 = ref_start / sr  # dance视频中节拍点之前的时长
    T2 = mov_start / sr  # bgm视频中节拍点之前的时长
    
    print(f"Badcase检测:")
    print(f"  T1 (dance视频中节拍点之前的时长): {T1:.2f}s")
    print(f"  T2 (bgm视频中节拍点之前的时长): {T2:.2f}s")
    print(f"  T1 - T2: {T1 - T2:.2f}s")
    
    if T1 > T2:
        gap_duration = T1 - T2
        print(f"  检测到T1 > T2 badcase，需要填充{gap_duration:.2f}s黑色画面")
        return "T1_GT_T2", gap_duration
    elif T2 > T1:
        gap_duration = T2 - T1
        print(f"  检测到T2 > T1 badcase，需要填充{gap_duration:.2f}s黑色画面")
        return "T2_GT_T1", gap_duration
    else:
        print("  不是badcase，T1 = T2")
        return "NORMAL", 0

def create_badcase_fixed_video(dance_video: str, bgm_video: str, output_video: str, 
                              gap_duration: float, sr: int = 44100) -> bool:
    """创建badcase修复后的视频"""
    print(f"创建badcase修复视频...")
    print(f"  黑色画面持续时间: {gap_duration:.2f}s")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # 获取dance视频的分辨率和帧率
        cmd_info = [
            'ffprobe', '-v', 'quiet', '-select_streams', 'v:0',
            '-show_entries', 'stream=width,height,r_frame_rate',
            '-of', 'csv=p=0', dance_video
        ]
        result = subprocess.run(cmd_info, capture_output=True, text=True)
        info = result.stdout.strip().split(',')
        width = int(info[0])
        height = int(info[1])
        fps = eval(info[2])  # 例如 "30/1" -> 30.0
        
        print(f"  视频信息: {width}x{height}, {fps}fps")
        
        # 获取dance视频的编码格式
        cmd_codec = [
            'ffprobe', '-v', 'quiet', '-select_streams', 'v:0',
            '-show_entries', 'stream=codec_name',
            '-of', 'csv=p=0', dance_video
        ]
        result_codec = subprocess.run(cmd_codec, capture_output=True, text=True)
        dance_codec = result_codec.stdout.strip()
        print(f"  dance视频编码: {dance_codec}")
        
        # 直接使用filter_complex创建复合视频，避免创建中间文件
        composite_video = os.path.join(temp_dir, "composite.mp4")
        
        cmd_composite = [
            'ffmpeg', '-y',
            '-f', 'lavfi',
            '-i', f'color=black:size={width}x{height}:duration={gap_duration}',
            '-i', dance_video,
            '-filter_complex', '[0:v][1:v]concat=n=2:v=1:a=0[outv]',
            '-map', '[outv]',
            '-c:v', 'libx264',  # 统一输出为H.264
            '-preset', 'ultrafast',
            '-crf', '28',
            '-pix_fmt', 'yuv420p',
            composite_video
        ]
        
        print("  创建复合视频...")
        result = subprocess.run(cmd_composite, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"创建复合视频失败: {result.stderr}")
            return False
        
        print("  复合视频创建成功")
        
        # 最终合成：复合视频 + bgm音频
        cmd_final = [
            'ffmpeg', '-y',
            '-i', composite_video,
            '-i', bgm_video,
            '-c:v', 'copy',  # 直接复制视频
            '-c:a', 'aac',
            '-map', '0:v:0',
            '-map', '1:a:0',
            # 不使用 -shortest，让视频决定长度
            output_video
        ]
        
        result = subprocess.run(cmd_final, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"最终合成失败: {result.stderr}")
            return False
        
        print(f"  Badcase修复完成: {output_video}")
        return True

def process_badcase_fix(dance_video: str, bgm_video: str, output_video: str, sr: int = 44100) -> bool:
    """处理badcase修复"""
    print(f"BeatSync Badcase修复开始处理...")
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
        
        # 检测badcase类型
        badcase_type, gap_duration = detect_badcase_type(ref_start, mov_start, sr)
        
        if badcase_type == "NORMAL":
            print("不是badcase，使用标准对齐模式")
            # 这里可以调用标准的beatsync_align_mode.py
            return False
        
        # 创建badcase修复视频
        success = create_badcase_fixed_video(dance_video, bgm_video, output_video, gap_duration, sr)
        
        if success:
            print(f"Badcase修复成功! 类型: {badcase_type}, 填充时间: {gap_duration:.2f}s")
        
        return success
        
    finally:
        # 清理临时目录
        import shutil
        shutil.rmtree(temp_dir)
        print("临时文件已清理")

def main():
    parser = argparse.ArgumentParser(description='BeatSync Badcase修复程序')
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
    
    # 处理badcase修复
    success = process_badcase_fix(
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
