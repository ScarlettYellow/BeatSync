#!/usr/bin/env python3
"""
BeatSync Badcase修复程序 - 裁剪版本
采用裁剪而不是填充的方法，避免生成黑色画面
"""

import os
import sys
import subprocess
import tempfile
import argparse
#
# 启用行缓冲，确保日志实时写出（不影响功能/算法）
try:
    sys.stdout.reconfigure(line_buffering=True)
    sys.stderr.reconfigure(line_buffering=True)
except Exception:
    pass
import numpy as np
import soundfile as sf
import librosa
import cv2
import hashlib
import json
from typing import Optional, Tuple

# ==================== 视频格式兼容性 ====================

def normalize_video_format(video_path: str, output_path: str = None, 
                          temp_dir: str = None) -> Tuple[str, bool]:
    """
    将视频统一转换为MP4格式（使用stream copy，零损失）
    
    参数:
        video_path: 输入视频路径
        output_path: 输出路径（如果为None，自动生成临时文件）
        temp_dir: 临时目录（如果为None，使用系统临时目录）
    
    返回:
        (转换后的文件路径, 是否进行了转换)
    """
    # 检查文件扩展名
    ext = os.path.splitext(video_path)[1].lower()
    
    # 如果已经是mp4，直接返回
    if ext == '.mp4':
        return video_path, False
    
    # 生成输出路径
    if output_path is None:
        if temp_dir is None:
            temp_dir = tempfile.gettempdir()
        base_name = os.path.splitext(os.path.basename(video_path))[0]
        output_path = os.path.join(temp_dir, f"{base_name}_normalized_{hash(video_path) % 10000}.mp4")
    
    # 使用 stream copy 转换（零损失）
    print(f"检测到非MP4格式 ({ext})，转换为MP4（零损失转换）...")
    cmd = [
        'ffmpeg', '-y',
        '-i', video_path,
        '-c', 'copy',  # stream copy，不重新编码
        '-movflags', '+faststart',  # 优化MP4结构，便于流式播放
        output_path
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"格式转换失败: {result.stderr[:200]}")
        print(f"使用原文件继续处理（兜底策略）")
        return video_path, False  # 转换失败，返回原文件（让后续处理尝试）
    
    print(f"格式转换完成: {os.path.basename(output_path)}")
    return output_path, True

def ensure_dir(path: str):
    if path and not os.path.exists(path):
        os.makedirs(path, exist_ok=True)

def file_quick_signature(path: str, max_bytes: int = 4 * 1024 * 1024) -> dict:
    st = os.stat(path)
    sig = {"size": st.st_size, "mtime": int(st.st_mtime), "sha1_head": None}
    try:
        h = hashlib.sha1()
        with open(path, "rb") as f:
            h.update(f.read(max_bytes))
        sig["sha1_head"] = h.hexdigest()
    except Exception:
        sig["sha1_head"] = None
    return sig

def build_cache_key(input_path: str, sr: int, channels: int, code_ver: str = "v2_trim_v1") -> str:
    key_obj = {
        "input": input_path,
        "sig": file_quick_signature(input_path),
        "sr": sr,
        "channels": channels,
        "code_ver": code_ver,
    }
    key_str = json.dumps(key_obj, sort_keys=True, ensure_ascii=False)
    return hashlib.sha1(key_str.encode("utf-8")).hexdigest()

def extract_audio_from_video(video_path: str, output_path: str, sr: int = 44100,
                             enable_cache: bool = False, cache_dir: Optional[str] = None) -> bool:
    """从视频中提取音频为 WAV 格式"""
    try:
        if enable_cache and cache_dir:
            ensure_dir(cache_dir)
            # 缓存管理：在提取前检查并清理缓存
            try:
                from beatsync_utils import manage_cache
                manage_cache(cache_dir, max_files=100, max_size_mb=5000)
            except ImportError:
                pass  # 如果工具模块不可用，跳过缓存管理
            
            cache_key = build_cache_key(video_path, sr=sr, channels=2)
            cache_wav = os.path.join(cache_dir, f"{cache_key}.wav")
            if os.path.exists(cache_wav):
                shutil.copyfile(cache_wav, output_path)
                return True
        cmd = [
            "ffmpeg", "-y", "-nostdin", "-hide_banner", "-v", "error",
            "-i", video_path,
            "-vn",  # 禁用视频
            "-acodec", "pcm_s16le",  # 16-bit PCM
            "-ar", str(sr),  # 采样率
            "-ac", "2",  # 双声道
            output_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        ok = result.returncode == 0
        if ok and enable_cache and cache_dir:
            try:
                cache_key = build_cache_key(video_path, sr=sr, channels=2)
                cache_wav = os.path.join(cache_dir, f"{cache_key}.wav")
                if not os.path.exists(cache_wav):
                    shutil.copyfile(output_path, cache_wav)
            except Exception:
                pass
        return ok
    except Exception as e:
        print(f"音频提取失败: {e}")
        return False

def find_beat_alignment(ref_audio: np.ndarray, mov_audio: np.ndarray, sr: int) -> tuple:
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

def detect_badcase_type(ref_start: int, mov_start: int, sr: int) -> tuple:
    """检测badcase类型"""
    T1 = ref_start / sr  # dance视频中节拍点之前的时长
    T2 = mov_start / sr  # bgm视频中节拍点之前的时长
    
    print(f"Badcase检测:")
    print(f"  T1 (dance视频中节拍点之前的时长): {T1:.2f}s")
    print(f"  T2 (bgm视频中节拍点之前的时长): {T2:.2f}s")
    print(f"  T1 - T2: {T1 - T2:.2f}s")
    
    if T1 > T2:
        gap_duration = T1 - T2
        print(f"  检测到T1 > T2 badcase，需要裁剪dance视频前{gap_duration:.2f}s")
        return "T1_GT_T2", gap_duration
    elif T2 > T1:
        gap_duration = T2 - T1
        print(f"  检测到T2 > T1 badcase，需要裁剪BGM音频前{gap_duration:.2f}s")
        return "T2_GT_T1", gap_duration
    else:
        print("  不是badcase，T1 = T2")
        return "NORMAL", 0

def detect_silent_segment_length(audio_path: str, sr: int = 22050) -> float:
    """
    检测音频前面连续无声段落的长度
    返回需要裁剪的时长（秒）
    """
    try:
        # 1. 加载音频
        audio, _ = sf.read(audio_path)
        
        # 2. 计算音频能量（RMS）- 滑动窗口
        window_size = int(0.1 * sr)  # 100ms窗口
        hop_size = int(0.05 * sr)    # 50ms步长
        
        rms_values = []
        for i in range(0, len(audio) - window_size, hop_size):
            segment = audio[i:i + window_size]
            rms = np.sqrt(np.mean(segment ** 2))
            rms_values.append(rms)
        
        # 3. 找到第一个有声音的位置
        silence_threshold = 0.01  # 静音阈值
        
        for i, rms in enumerate(rms_values):
            if rms > silence_threshold:
                # 找到第一个有声音的位置
                silent_duration = (i * hop_size) / sr
                return silent_duration
        
        # 如果整段都是静音，返回0
        return 0.0
        
    except Exception as e:
        print(f"检测无声段落失败: {e}")
        return 0.0

def detect_silent_segments_with_video(video_path: str, position: str = "trailing", sr: int = 22050, video_duration: float = None) -> float:
    """
    检测视频中有画面但无声段落的长度（复用beatsync_fine_cut_modular.py的成功逻辑）
    
    参数:
        video_path: 视频文件路径
        position: "leading" 检测开头, "trailing" 检测末尾
        sr: 音频采样率
    
    返回:
        需要裁剪的时长（秒）
    """
    try:
        print(f"  检测{position}有画面但无声段落...")
        
        # 提取音频
        temp_audio = "temp_silent_detection.wav"
        cmd_extract = [
            'ffmpeg', '-y',
            '-i', video_path,
            '-vn', '-acodec', 'pcm_s16le', '-ar', str(sr), '-ac', '1',
            temp_audio
        ]
        result = subprocess.run(cmd_extract, capture_output=True, text=True)
        if result.returncode != 0:
            print("  提取音频失败")
            return 0.0
        
        # 使用beatsync_fine_cut_modular.py中已验证的检测逻辑
        if position == "leading":
            # 检测开头的静音段落
            silent_duration = detect_silent_segment_length(temp_audio, sr)
            print(f"  检测到开头静音段落: {silent_duration:.3f}s")
            return silent_duration
            
        else:  # trailing
            # 检测末尾的静音段落 - 使用宽松的静音检测策略
            # 加载音频并计算RMS值
            audio, _ = sf.read(temp_audio)
            
            # 计算音频能量（RMS）- 滑动窗口
            window_size = int(0.1 * sr)  # 100ms窗口
            hop_size = int(0.05 * sr)    # 50ms步长
            
            rms_values = []
            for i in range(0, len(audio) - window_size, hop_size):
                segment = audio[i:i + window_size]
                rms = np.sqrt(np.mean(segment ** 2))
                rms_values.append(rms)
            
            # 获取视频总时长
            if video_duration is None:
                # 如果没有传入视频总时长，使用ffprobe获取
                cmd_duration = [
                    'ffprobe', '-v', 'quiet', '-show_entries', 'format=duration',
                    '-of', 'csv=p=0', video_path
                ]
                result = subprocess.run(cmd_duration, capture_output=True, text=True)
                video_duration = float(result.stdout.strip())
            
            # 步骤1：检测末尾N秒的静音比例
            check_duration = 3.0  # 检查末尾3秒
            check_frames = int(check_duration * sr / hop_size)
            start_check_frame = max(0, len(rms_values) - check_frames)
            
            # 计算末尾N秒的静音比例
            silence_threshold = 0.01
            silent_frames = sum(1 for i in range(start_check_frame, len(rms_values)) if rms_values[i] < silence_threshold)
            total_check_frames = len(rms_values) - start_check_frame
            silence_ratio = silent_frames / total_check_frames if total_check_frames > 0 else 0
            
            print(f"  末尾{check_duration:.1f}秒静音比例: {silence_ratio:.1%}")
            
            # 步骤2：如果静音比例超过60%，使用"音频衰减检测"找到最后一个强音位置
            if silence_ratio >= 0.6:
                # 计算前80%音频的平均能量（排除末尾20%）
                cutoff_frame = int(len(rms_values) * 0.8)
                avg_rms = np.mean(rms_values[:cutoff_frame])
                
                # 设置阈值：如果音频能量低于平均值的30%，认为是衰减段落
                fade_threshold = avg_rms * 0.3
                
                print(f"  前80%平均RMS: {avg_rms:.4f}, 衰减阈值(30%): {fade_threshold:.4f}")
                
                # 从后往前扫描，找到"连续衰减段落"的起点
                # 如果从某个位置开始，后续80%以上的帧都低于阈值，就认为是衰减段落起点
                last_strong_frame = -1
                for start_idx in range(len(rms_values) - 1, -1, -1):
                    # 检查从这个位置开始到结束的帧
                    weak_frames = sum(1 for i in range(start_idx, len(rms_values)) if rms_values[i] < fade_threshold)
                    total_frames = len(rms_values) - start_idx
                    weak_ratio = weak_frames / total_frames if total_frames > 0 else 0
                    
                    # 如果70%以上是弱音，认为这是衰减段落的起点
                    if weak_ratio >= 0.7:
                        # 继续向前查找，找到最后一个强音位置
                        for i in range(start_idx - 1, -1, -1):
                            if rms_values[i] >= fade_threshold:
                                last_strong_frame = i
                                break
                        break
                
                if last_strong_frame >= 0:
                    last_strong_time = last_strong_frame * hop_size / sr
                    trailing_silent_duration = video_duration - last_strong_time
                    print(f"  检测到音频衰减: 最后强音位置第{last_strong_time:.2f}s")
                    print(f"  建议裁剪末尾衰减段落: {trailing_silent_duration:.3f}s")
                    return trailing_silent_duration
            
            # 步骤3：如果静音比例不足60%，使用原来的逻辑（找到最后一个有声音的位置）
            last_sound_frame = -1
            for i in range(len(rms_values) - 1, -1, -1):
                if rms_values[i] >= silence_threshold:
                    last_sound_frame = i
                    break
            
            if last_sound_frame >= 0:
                last_sound_time = last_sound_frame * hop_size / sr
                trailing_silent_duration = video_duration - last_sound_time
                print(f"  最后一个有声音的位置: 第{last_sound_time:.2f}s")
                print(f"  检测到末尾静音段落: {trailing_silent_duration:.3f}s")
                return trailing_silent_duration
            else:
                print(f"  未找到有声音的位置，整个音频都是静音")
                return len(audio) / sr
        
        # 清理临时文件
        if os.path.exists(temp_audio):
            os.remove(temp_audio)
        
    except Exception as e:
        print(f"检测{position}静音段落失败: {e}")
        return 0.0

def detect_black_frames_with_audio(video_path: str, position: str = "trailing", threshold: float = 0.1) -> float:
    """
    检测视频中有声无画面段落的长度（统一处理开头和末尾）
    
    参数:
        video_path: 视频文件路径
        position: "leading" 检测开头, "trailing" 检测末尾
        threshold: 黑色画面阈值
    
    返回:
        需要裁剪的时长（秒）
    """
    try:
        print(f"  检测{position}有声无画面段落...")
        
        # 获取视频总时长
        cmd_duration = [
            'ffprobe', '-v', 'quiet',
            '-show_entries', 'format=duration',
            '-of', 'csv=p=0',
            video_path
        ]
        result = subprocess.run(cmd_duration, capture_output=True, text=True)
        total_duration = float(result.stdout.strip())
        
        # 获取视频帧率（增强错误处理）
        try:
            from beatsync_utils import get_video_fps
            fps = get_video_fps(video_path, default=25.0)
        except ImportError:
            # 如果工具模块不可用，使用基础方法
            cmd_fps = [
                'ffprobe', '-v', 'error',
                '-select_streams', 'v:0',
                '-show_entries', 'stream=r_frame_rate',
                '-of', 'csv=p=0',
                video_path
            ]
            result = subprocess.run(cmd_fps, capture_output=True, text=True, timeout=10)
            if result.returncode == 0 and result.stdout.strip():
                fps_str = result.stdout.strip()
                # 安全解析分数格式（如 "30/1"）
                if '/' in fps_str:
                    try:
                        num, den = map(int, fps_str.split('/'))
                        fps = num / den if den != 0 else 25.0
                    except (ValueError, ZeroDivisionError):
                        print(f"  警告: 帧率解析失败 ({fps_str})，使用默认值 25.0")
                        fps = 25.0
                else:
                    try:
                        fps = float(fps_str)
                    except ValueError:
                        print(f"  警告: 帧率解析失败 ({fps_str})，使用默认值 25.0")
                        fps = 25.0
            else:
                print(f"  警告: 无法获取视频帧率，使用默认值 25.0")
                fps = 25.0
        
        # 计算理论总帧数
        theoretical_frames = int(total_duration * fps)
        
        # 使用OpenCV检测实际可读帧数
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print("无法打开视频文件")
            return 0.0
        
        if position == "leading":
            # 检测开头的有声无画面段落
            first_readable_frame = -1
            for frame_idx in range(theoretical_frames):
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
                ret, frame = cap.read()
                if ret:
                    # 检查是否为黑色画面
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    mean_brightness = np.mean(gray) / 255.0
                    is_black = mean_brightness < threshold
                    
                    if not is_black:
                        first_readable_frame = frame_idx
                        break
            
            if first_readable_frame == -1:
                print("  无法找到可读帧")
                return 0.0
            
            # 计算开头有声无画面段落的时长
            leading_duration = first_readable_frame / fps
            print(f"  视频总时长: {total_duration:.3f}s")
            print(f"  第一个可读帧时间: {leading_duration:.3f}s")
            print(f"  检测到开头有声无画面段落: {leading_duration:.3f}s")
            return leading_duration
            
        else:  # trailing
            # 检测末尾的有声无画面段落
            last_readable_frame = -1
            for frame_idx in range(theoretical_frames - 1, -1, -1):
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
                ret, frame = cap.read()
                if ret:
                    last_readable_frame = frame_idx
                    break
            
            if last_readable_frame == -1:
                print("  无法读取任何帧")
                return 0.0
            
            # 计算末尾有声无画面段落的时长
            last_readable_time = last_readable_frame / fps
            trailing_duration = total_duration - last_readable_time
            
            print(f"  视频总时长: {total_duration:.3f}s")
            print(f"  最后可读帧时间: {last_readable_time:.3f}s")
            print(f"  检测到末尾有声无画面段落: {trailing_duration:.3f}s")
            return trailing_duration
        
        cap.release()
        
    except Exception as e:
        print(f"检测{position}有声无画面失败: {e}")
        return 0.0

def create_trimmed_video(dance_video: str, bgm_video: str, output_video: str, 
                        badcase_type: str, gap_duration: float,
                        fast_video: bool = True,
                        hwaccel: Optional[str] = None,
                        video_encode: str = "encode") -> bool:
    """创建裁剪后的视频（不生成黑色画面）+ 末尾静音裁剪"""
    print(f"创建裁剪视频...")
    print(f"  Badcase类型: {badcase_type}")
    print(f"  裁剪时长: {gap_duration:.2f}s")
    
    try:
        # 第一步：创建基础裁剪视频
        temp_video = "temp_trimmed_video.mp4"
        
        if badcase_type == "T1_GT_T2":
            # T1 > T2: 裁剪dance视频的前gap_duration秒
            print("  裁剪dance视频前段...")
            cmd = ['ffmpeg', '-y', '-nostdin', '-hide_banner', '-v', 'error']
            if hwaccel:
                cmd += ['-hwaccel', hwaccel]
            cmd += ['-ss', str(gap_duration), '-i', dance_video, '-i', bgm_video]
            if video_encode == 'videotoolbox':
                cmd += ['-c:v', 'h264_videotoolbox', '-b:v', '6M', '-maxrate', '8M', '-bufsize', '12M', '-pix_fmt', 'yuv420p']
            else:
                preset = 'ultrafast' if fast_video else 'fast'
                cmd += ['-c:v', 'libx264', '-preset', preset, '-crf', '23']  # CRF 23：高质量输出
            cmd += ['-c:a', 'aac', '-b:a', '192k']
            # 添加faststart，将moov atom移到文件开头，实现快速播放
            cmd += ['-movflags', '+faststart']
            cmd += ['-map', '0:v:0', '-map', '1:a:0', temp_video]
        elif badcase_type == "T2_GT_T1":
            # T2 > T1: 裁剪BGM音频的前gap_duration秒
            print("  裁剪BGM音频前段...")
            cmd = ['ffmpeg', '-y', '-nostdin', '-hide_banner', '-v', 'error']
            if hwaccel:
                cmd += ['-hwaccel', hwaccel]
            cmd += ['-i', dance_video, '-ss', str(gap_duration), '-i', bgm_video]
            if video_encode == 'videotoolbox':
                cmd += ['-c:v', 'h264_videotoolbox', '-b:v', '6M', '-maxrate', '8M', '-bufsize', '12M', '-pix_fmt', 'yuv420p']
            else:
                preset = 'ultrafast' if fast_video else 'fast'
                cmd += ['-c:v', 'libx264', '-preset', preset, '-crf', '23']  # CRF 23：高质量输出
            cmd += ['-c:a', 'aac', '-b:a', '192k', '-map', '0:v:0', '-map', '1:a:0', temp_video]
        else:
            # NORMAL: 直接合成
            print("  直接合成视频...")
            cmd = ['ffmpeg', '-y', '-nostdin', '-hide_banner', '-v', 'error']
            if hwaccel:
                cmd += ['-hwaccel', hwaccel]
            cmd += ['-i', dance_video, '-i', bgm_video, '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k']
            # 添加faststart，将moov atom移到文件开头，实现快速播放
            cmd += ['-movflags', '+faststart']
            cmd += ['-map', '0:v:0', '-map', '1:a:0', temp_video]
        
        # 增强异常处理
        try:
            from beatsync_utils import run_ffmpeg_command
            success, error_msg = run_ffmpeg_command(cmd, f"视频合成 {os.path.basename(temp_video)}")
            if not success:
                print(f"视频合成失败: {error_msg}")
                return False
        except ImportError:
            # 如果工具模块不可用，使用基础方法
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            if result.returncode != 0:
                print(f"视频合成失败: {result.stderr[:200]}")
                return False
        
        print(f"  基础裁剪视频创建成功")
        
        # 第二步：检测并裁剪无效内容段落
        # 2.1 检测末尾有声无画面段落
        trailing_black_duration = detect_black_frames_with_audio(temp_video, "trailing")
        
        # 获取视频总时长
        cmd_duration = [
            'ffprobe', '-v', 'quiet', '-show_entries', 'format=duration',
            '-of', 'csv=p=0', temp_video
        ]
        result = subprocess.run(cmd_duration, capture_output=True, text=True)
        total_duration = float(result.stdout.strip())
        
        # 2.2 检测末尾有画面但无声段落（传入视频总时长）
        trailing_silent_duration = detect_silent_segments_with_video(temp_video, "trailing", video_duration=total_duration)
        
        # 2.3 检测开头有画面但无声段落
        leading_silent_duration = detect_silent_segments_with_video(temp_video, "leading")
        
        # 计算需要裁剪的总时长
        # 对于末尾裁剪，应该使用最后一个有声音的位置作为最终时长
        if trailing_silent_duration > 0:
            # 如果有末尾静音，最终时长应该是最后一个有声音的位置
            # 计算最后一个有声音的位置
            last_sound_time = total_duration - trailing_silent_duration
            final_duration = last_sound_time
        else:
            # 如果没有末尾静音，使用原来的逻辑
            total_trim_duration = max(trailing_black_duration, trailing_silent_duration)
            final_duration = total_duration - total_trim_duration
        
        trim_start = leading_silent_duration
        
        # 计算总裁剪时长（用于日志显示）
        total_trim_duration = max(trailing_black_duration, trailing_silent_duration)
        
        print(f"  检测结果:")
        print(f"    开头静音段落: {leading_silent_duration:.3f}s")
        print(f"    末尾有声无画面: {trailing_black_duration:.3f}s")
        print(f"    末尾静音段落: {trailing_silent_duration:.3f}s")
        print(f"    总裁剪时长: {total_trim_duration:.3f}s")
        
        if total_trim_duration > 0.5 or trim_start > 0.5:  # 如果有无效内容超过0.5秒，进行裁剪
            # 获取视频总时长
            cmd_duration = [
                'ffprobe', '-v', 'quiet',
                '-show_entries', 'format=duration',
                '-of', 'csv=p=0',
                temp_video
            ]
            result = subprocess.run(cmd_duration, capture_output=True, text=True)
            total_duration = float(result.stdout.strip())
            
            # 计算最终裁剪参数
            final_start = trim_start
            final_duration = total_duration - total_trim_duration
            
            if final_duration > 0:
                # 如果只需要裁剪末尾，使用-t参数指定最终时长
                if trim_start == 0:
                    cmd_trim = ['ffmpeg', '-y', '-nostdin', '-hide_banner', '-v', 'error',
                                '-i', temp_video, '-t', str(final_duration),
                                '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', output_video]
                else:
                    # 如果需要裁剪开头和末尾，使用-ss和-t参数
                    cmd_trim = ['ffmpeg', '-y', '-nostdin', '-hide_banner', '-v', 'error',
                                '-ss', str(final_start), '-t', str(final_duration), '-i', temp_video]
                    if video_encode == 'videotoolbox':
                        cmd_trim += ['-c:v', 'h264_videotoolbox', '-b:v', '6M', '-maxrate', '8M', '-bufsize', '12M', '-pix_fmt', 'yuv420p']
                    else:
                        preset = 'ultrafast' if fast_video else 'fast'
                        cmd_trim += ['-c:v', 'libx264', '-preset', preset, '-crf', '23']
                    cmd_trim += ['-c:a', 'aac', '-b:a', '192k']
                    # 添加faststart，将moov atom移到文件开头，实现快速播放（10秒内开始播放）
                    cmd_trim += ['-movflags', '+faststart']
                    cmd_trim += [output_video]
                
                # 增强异常处理
                try:
                    from beatsync_utils import run_ffmpeg_command
                    success, error_msg = run_ffmpeg_command(cmd_trim, f"裁剪无效内容 {os.path.basename(output_video)}")
                    if not success:
                        print(f"裁剪无效内容失败: {error_msg}")
                        return False
                except ImportError:
                    # 如果工具模块不可用，使用基础方法
                    result = subprocess.run(cmd_trim, capture_output=True, text=True, timeout=300)
                    if result.returncode != 0:
                        print(f"裁剪无效内容失败: {result.stderr[:200]}")
                        return False
                
                print(f"  无效内容裁剪完成: 起点={final_start:.3f}s, 时长={final_duration:.3f}s")
            else:
                print(f"  裁剪后时长过短，直接复制")
                cmd_copy = [
                    'ffmpeg', '-y',
                    '-i', temp_video,
                    '-c', 'copy',
                    output_video
                ]
                # 增强异常处理
                try:
                    from beatsync_utils import run_ffmpeg_command
                    success, error_msg = run_ffmpeg_command(cmd_copy, f"复制视频 {os.path.basename(output_video)}")
                    if not success:
                        print(f"复制视频失败: {error_msg}")
                        return False
                except ImportError:
                    # 如果工具模块不可用，使用基础方法
                    result = subprocess.run(cmd_copy, capture_output=True, text=True, timeout=300)
                    if result.returncode != 0:
                        print(f"复制视频失败: {result.stderr[:200]}")
                        return False
        else:
            print(f"  无效内容段落较短，无需裁剪")
            # 直接复制
            cmd_copy = [
                'ffmpeg', '-y',
                '-i', temp_video,
                '-c', 'copy',
                output_video
            ]
            result = subprocess.run(cmd_copy, capture_output=True, text=True)
            if result.returncode != 0:
                print(f"复制视频失败: {result.stderr}")
                return False
        
        # 清理临时文件
        if os.path.exists(temp_video):
            os.remove(temp_video)
        
        print(f"  最终裁剪视频创建成功: {output_video}")
        return True
        
    except Exception as e:
        print(f"创建裁剪视频失败: {e}")
        return False

def process_badcase_fix_trim(dance_video: str, bgm_video: str, output_video: str, sr: int = 44100,
                             fast_video: bool = True,
                             hwaccel: Optional[str] = None,
                             video_encode: str = "encode",
                             enable_cache: bool = True,
                             cache_dir: Optional[str] = ".beatsync_cache",
                             threads: Optional[int] = 4,
                             lib_threads: Optional[int] = 1) -> bool:
    """处理badcase修复（裁剪版本）"""
    import time
    from datetime import datetime
    total_start = time.time()
    
    print("=" * 60)
    print(f"BeatSync Badcase修复（裁剪版本）开始处理...")
    print(f"[总开始] 时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"[输入] dance: {dance_video}")
    print(f"[输入] bgm: {bgm_video}")
    print(f"[输出] output: {output_video}")
    print("=" * 60)
    
    # 创建临时目录
    temp_dir = tempfile.mkdtemp()
    print(f"[步骤0] 创建临时目录: {temp_dir}")
    
    try:
        # 提取音频
        print("[步骤1] 提取音频...")
        step_start = time.time()
        dance_audio_path = os.path.join(temp_dir, "dance.wav")
        bgm_audio_path = os.path.join(temp_dir, "bgm.wav")
        
        if lib_threads is not None:
            os.environ['OMP_NUM_THREADS'] = str(lib_threads)
            os.environ['MKL_NUM_THREADS'] = str(lib_threads)
            os.environ['NUMEXPR_NUM_THREADS'] = str(lib_threads)
        if not extract_audio_from_video(dance_video, dance_audio_path, sr,
                                        enable_cache=enable_cache, cache_dir=cache_dir):
            print("dance音频提取失败")
            return False
            
        if not extract_audio_from_video(bgm_video, bgm_audio_path, sr,
                                        enable_cache=enable_cache, cache_dir=cache_dir):
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
        
        if badcase_type != "NORMAL":
            print(f"[步骤6] 检测到badcase，使用裁剪方法修复...")
            step_start = time.time()
            success = create_trimmed_video(dance_video, bgm_video, output_video, badcase_type, gap_duration,
                                           fast_video=fast_video, hwaccel=hwaccel, video_encode=video_encode)
            print(f"[步骤6] 完成，耗时: {time.time() - step_start:.1f}秒")
        else:
            print("[步骤6] 不是badcase，直接合成...")
            step_start = time.time()
            success = create_trimmed_video(dance_video, bgm_video, output_video, badcase_type, 0,
                                           fast_video=fast_video, hwaccel=hwaccel, video_encode=video_encode)
            print(f"[步骤6] 完成，耗时: {time.time() - step_start:.1f}秒")
        
        total_elapsed = time.time() - total_start
        print("=" * 60)
        if success:
            print(f"Badcase修复（裁剪版本）成功! 类型: {badcase_type}, 裁剪时间: {gap_duration:.2f}s")
        else:
            print("Badcase修复（裁剪版本）失败!")
        print(f"[总完成] 时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"[总耗时] {total_elapsed:.1f}秒 ({total_elapsed/60:.1f}分钟)")
        print("=" * 60)
        
        return success
        
    except Exception as e:
        print(f"处理失败: {e}")
        return False
    finally:
        # 清理临时文件
        import shutil
        shutil.rmtree(temp_dir)
        print("临时文件已清理")

def main():
    parser = argparse.ArgumentParser(description="BeatSync Badcase修复程序（裁剪版本）")
    parser.add_argument('--dance', type=str, required=True, help='Dance视频路径')
    parser.add_argument('--bgm', type=str, required=True, help='BGM视频路径')
    parser.add_argument('--output', type=str, required=True, help='输出视频路径')
    parser.add_argument('--fast-video', action='store_true', help='启用快速路径（更快的编码/可选硬件加速）')
    parser.add_argument('--hwaccel', type=str, default=None, choices=[None, 'videotoolbox', 'auto'], help='硬件加速选项')
    parser.add_argument('--video-encode', type=str, default='x264_fast', choices=['copy', 'x264_fast', 'videotoolbox'], help='出片阶段的视频编码策略')
    parser.add_argument('--enable-cache', action='store_true', help='启用音频提取缓存（基于输入签名）')
    parser.add_argument('--cache-dir', type=str, default='.beatsync_cache', help='缓存目录')
    parser.add_argument('--threads', type=int, default=4, help='ffmpeg 线程数（不指定则使用默认）')
    parser.add_argument('--lib-threads', type=int, default=1, help='数值库线程（OMP/MKL/NUMEXPR）')
    
    args = parser.parse_args()
    
    # 输入验证（增强异常处理）
    try:
        from beatsync_utils import validate_input_files
        is_valid, error_msg = validate_input_files(args.dance, args.bgm, args.output)
        if not is_valid:
            print("=" * 60)
            print("输入验证失败:")
            print(error_msg)
            print("=" * 60)
            return False
    except ImportError:
        # 如果工具模块不可用，使用基础检查
        if not os.path.exists(args.dance):
            print(f"Dance视频文件不存在: {args.dance}")
            return False
        if not os.path.exists(args.bgm):
            print(f"BGM视频文件不存在: {args.bgm}")
            return False
    except Exception as e:
        print(f"输入验证异常: {e}")
        return False
    
    # 格式标准化（新增）
    format_temp_dir = tempfile.mkdtemp(prefix="beatsync_format_")
    normalized_files = []  # 记录需要清理的临时文件
    
    try:
        # 对dance和bgm视频进行格式转换
        dance_video, converted_dance = normalize_video_format(args.dance, temp_dir=format_temp_dir)
        if converted_dance:
            normalized_files.append(dance_video)
        
        bgm_video, converted_bgm = normalize_video_format(args.bgm, temp_dir=format_temp_dir)
        if converted_bgm:
            normalized_files.append(bgm_video)
        
        # 规范化编码策略与默认加速（不改变对齐逻辑）
        video_encode = 'copy'
        if args.video_encode == 'x264_fast':
            video_encode = 'encode'
        elif args.video_encode == 'videotoolbox':
            video_encode = 'videotoolbox'
        hwaccel = None if args.hwaccel in (None, 'auto') else args.hwaccel
        # 默认启用快速路径与缓存
        if not args.fast_video:
            args.fast_video = True
        if not args.enable_cache:
            args.enable_cache = True
        success = process_badcase_fix_trim(dance_video, bgm_video, args.output,
                                           fast_video=True if args.fast_video else True,
                                           hwaccel=hwaccel,
                                           video_encode=video_encode,
                                           enable_cache=args.enable_cache,
                                           cache_dir=args.cache_dir,
                                           threads=args.threads,
                                           lib_threads=args.lib_threads)
        return success
        
    finally:
        # 清理临时转换文件
        for temp_file in normalized_files:
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            except Exception as e:
                print(f"清理临时文件失败: {e}")
        try:
            if os.path.exists(format_temp_dir) and not os.listdir(format_temp_dir):
                os.rmdir(format_temp_dir)
        except Exception:
            pass

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
