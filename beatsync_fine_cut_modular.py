#!/usr/bin/env python3
"""
BeatSync 模块解耦精剪模式
模块1: 对齐模块（基于多策略融合算法）
模块2: 裁剪模块（检测并剪掉前面的无声段落）
"""

import os
import sys
import librosa
import numpy as np
import soundfile as sf
import subprocess
import argparse
import shutil
import tempfile
from typing import Tuple, Optional
import hashlib
import json
from datetime import datetime
#
# 启用行缓冲，确保日志实时写出（不影响功能/算法）
try:
    sys.stdout.reconfigure(line_buffering=True)
    sys.stderr.reconfigure(line_buffering=True)
except Exception:
    pass

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

# ==================== 模块1: 对齐模块 ====================

def ensure_dir(path: str):
    if path and not os.path.exists(path):
        os.makedirs(path, exist_ok=True)

def file_quick_signature(path: str, max_bytes: int = 4 * 1024 * 1024) -> dict:
    """
    生成文件签名：size + mtime + 前4MB sha1，避免全量hash带来的IO
    """
    st = os.stat(path)
    sig = {
        "size": st.st_size,
        "mtime": int(st.st_mtime),
        "sha1_head": None
    }
    try:
        h = hashlib.sha1()
        with open(path, "rb") as f:
            chunk = f.read(max_bytes)
            h.update(chunk)
        sig["sha1_head"] = h.hexdigest()
    except Exception:
        sig["sha1_head"] = None
    return sig

def build_cache_key(input_path: str, duration: float, sr: int, channels: int, code_ver: str = "modular_v1") -> str:
    """
    基于输入文件签名与关键参数构建缓存key
    """
    sig = file_quick_signature(input_path)
    key_obj = {
        "input": input_path,
        "sig": sig,
        "duration": duration,
        "sr": sr,
        "channels": channels,
        "code_ver": code_ver,
    }
    key_str = json.dumps(key_obj, sort_keys=True, ensure_ascii=False)
    return hashlib.sha1(key_str.encode("utf-8")).hexdigest()

def extract_audio_optimized(video_path: str, audio_path: str, duration: float = 30.0,
                            enable_cache: bool = False, cache_dir: Optional[str] = None) -> bool:
    """优化的音频提取"""
    try:
        if enable_cache and cache_dir:
            ensure_dir(cache_dir)
            # 缓存管理：在提取前检查并清理缓存
            try:
                from beatsync_utils import manage_cache
                manage_cache(cache_dir, max_files=100, max_size_mb=5000)
            except ImportError:
                pass  # 如果工具模块不可用，跳过缓存管理
            
            cache_key = build_cache_key(video_path, duration, 22050, 2)
            cache_wav = os.path.join(cache_dir, f"{cache_key}.wav")
            if os.path.exists(cache_wav):
                # 命中缓存
                shutil.copyfile(cache_wav, audio_path)
                return True
        cmd = [
            'ffmpeg', '-y',
            '-nostdin', '-hide_banner', '-v', 'error',
            '-i', video_path,
            '-t', str(duration),
            '-vn', '-acodec', 'pcm_s16le', '-ar', '22050', '-ac', '2',
            audio_path
        ]
        
        # 增强异常处理
        try:
            from beatsync_utils import run_ffmpeg_command, validate_audio_file
            success, error_msg = run_ffmpeg_command(cmd, f"提取音频 {os.path.basename(video_path)}")
            if not success:
                print(f"音频提取失败: {error_msg}")
                return False
            
            # 验证提取的音频文件
            is_valid, validation_error = validate_audio_file(audio_path)
            if not is_valid:
                print(f"音频验证失败: {validation_error}")
                return False
        except ImportError:
            # 如果工具模块不可用，使用基础方法
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            if result.returncode != 0:
                print(f"音频提取失败: {result.stderr[:200]}")
                return False
        
        ok = True
        if ok and enable_cache and cache_dir:
            try:
                cache_key = build_cache_key(video_path, duration, 22050, 2)
                cache_wav = os.path.join(cache_dir, f"{cache_key}.wav")
                if not os.path.exists(cache_wav):
                    shutil.copyfile(audio_path, cache_wav)
            except Exception:
                pass
        return ok
    except:
        return False

def extract_music_features(audio: np.ndarray, sr: int):
    """提取音乐特征"""
    try:
        # MFCC特征
        mfcc = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=13)
        
        # 音乐特征
        chroma = librosa.feature.chroma_stft(y=audio, sr=sr)
        spectral_contrast = librosa.feature.spectral_contrast(y=audio, sr=sr)
        spectral_rolloff = librosa.feature.spectral_rolloff(y=audio, sr=sr)
        
        return mfcc, chroma, spectral_contrast, spectral_rolloff
    except:
        return None, None, None, None

def calculate_feature_similarity(feat1: np.ndarray, feat2: np.ndarray) -> float:
    """计算特征相似度"""
    try:
        corr_matrix = np.corrcoef(feat1.flatten(), feat2.flatten())
        return abs(corr_matrix[0, 1])
    except:
        return 0.0

def calculate_original_correlation(ref_audio: np.ndarray, mov_audio: np.ndarray, 
                                   ref_start: int, mov_start: int, sr: int) -> float:
    """计算原始音频相关性"""
    window_samples = int(2.0 * sr)  # 2秒窗口
    
    ref_start_idx = ref_start
    ref_end_idx = ref_start_idx + window_samples
    mov_start_idx = mov_start
    mov_end_idx = mov_start_idx + window_samples
    
    if (ref_end_idx > len(ref_audio) or mov_end_idx > len(mov_audio) or
        ref_start_idx < 0 or mov_start_idx < 0):
        return 0.0
    
    ref_seg = ref_audio[ref_start_idx:ref_end_idx]
    mov_seg = mov_audio[mov_start_idx:mov_end_idx]
    
    min_len = min(len(ref_seg), len(mov_seg))
    if min_len == 0:
        return 0.0
    
    ref_seg = ref_seg[:min_len]
    mov_seg = mov_seg[:min_len]
    
    ref_norm = ref_seg - np.mean(ref_seg)
    mov_norm = mov_seg - np.mean(mov_seg)
    numerator = np.sum(ref_norm * mov_norm)
    denominator = np.sqrt(np.sum(ref_norm**2) * np.sum(mov_norm**2))
    
    if denominator == 0:
        return 0.0
    else:
        return numerator / denominator

def calculate_music_feature_correlation(ref_audio: np.ndarray, mov_audio: np.ndarray, 
                                        ref_start: int, mov_start: int, sr: int) -> float:
    """使用音乐特征进行相关性计算"""
    window_samples = int(2.0 * sr)  # 2秒窗口
    
    ref_start_idx = ref_start
    ref_end_idx = ref_start_idx + window_samples
    mov_start_idx = mov_start
    mov_end_idx = mov_start_idx + window_samples
    
    if (ref_end_idx > len(ref_audio) or mov_end_idx > len(mov_audio) or
        ref_start_idx < 0 or mov_start_idx < 0):
        return 0.0
    
    ref_seg = ref_audio[ref_start_idx:ref_end_idx]
    mov_seg = mov_audio[mov_start_idx:mov_end_idx]
    
    min_len = min(len(ref_seg), len(mov_seg))
    if min_len == 0:
        return 0.0
    
    ref_seg = ref_seg[:min_len]
    mov_seg = mov_seg[:min_len]
    
    try:
        ref_features = extract_music_features(ref_seg, sr)
        mov_features = extract_music_features(mov_seg, sr)
        
        if any(f is None for f in ref_features) or any(f is None for f in mov_features):
            return 0.0
        
        similarities = []
        # 调整后的权重
        similarities.append(calculate_feature_similarity(ref_features[0], mov_features[0]) * 0.4) # MFCC
        similarities.append(calculate_feature_similarity(ref_features[1], mov_features[1]) * 0.3) # Chroma
        similarities.append(calculate_feature_similarity(ref_features[2], mov_features[2]) * 0.2) # Spectral Contrast
        similarities.append(calculate_feature_similarity(ref_features[3], mov_features[3]) * 0.1) # Spectral Rolloff
        
        return sum(similarities)
            
    except Exception as e:
        return 0.0

def find_best_alignment_score(ref_audio: np.ndarray, mov_audio: np.ndarray, 
                              ref_start: int, mov_start: int, sr: int) -> Tuple[float, float, float, str]:
    """计算并融合多种策略的对齐得分"""
    original_score = calculate_original_correlation(ref_audio, mov_audio, ref_start, mov_start, sr)
    music_score = calculate_music_feature_correlation(ref_audio, mov_audio, ref_start, mov_start, sr)
    
    # 多策略融合决策 - 更保守的策略选择
    if original_score < 0.05:
        final_score = original_score
        strategy = "original"
    elif music_score > original_score * 1.5 and (music_score - original_score) > 0.1:
        final_score = music_score
        strategy = "music_features"
    else:
        final_score = original_score
        strategy = "original"
    
    return final_score, original_score, music_score, strategy

def find_beat_alignment_multi_strategy(ref_audio: np.ndarray, mov_audio: np.ndarray, sr: int) -> Tuple[int, int, float]:
    """多策略融合的节拍对齐算法"""
    print("使用多策略融合节拍对齐算法...")
    
    # 快速节拍检测
    print("快速节拍检测...")
    ref_tempo, ref_beats = librosa.beat.beat_track(y=ref_audio, sr=sr)
    mov_tempo, mov_beats = librosa.beat.beat_track(y=mov_audio, sr=sr)
    
    print(f"节拍检测:")
    print(f"  dance: {len(ref_beats)} 个节拍点, BPM ≈ {ref_tempo[0]:.1f}")
    print(f"  bgm: {len(mov_beats)} 个节拍点, BPM ≈ {mov_tempo[0]:.1f}")
    
    # 搜索参数
    max_offset = min(len(ref_audio), len(mov_audio)) / sr * 0.4
    step_size = 0.2
    print(f"多策略搜索 (最大偏移: {max_offset:.1f}s, 步长: {step_size:.1f}s)...")
    
    best_score = 0.0
    best_ref_start = 0
    best_mov_start = 0
    best_strategy = "original"
    
    # 第一阶段：搜索bgm=0s的情况
    print(f"  第一阶段：搜索bgm=0s的情况...")
    mov_start_samples = 0
    
    for ref_offset in np.arange(0, max_offset * sr, step_size * sr):
        ref_start_samples = int(ref_offset)
        
        if ref_start_samples >= len(ref_audio):
            break
            
        final_score, original_score, music_score, strategy = find_best_alignment_score(
            ref_audio, mov_audio, ref_start_samples, mov_start_samples, sr
        )
        
        if final_score > best_score:
            best_score = final_score
            best_ref_start = ref_start_samples
            best_mov_start = mov_start_samples
            best_strategy = strategy
            print(f"    找到更好的对齐点: dance={ref_start_samples/sr:.2f}s, bgm={mov_start_samples/sr:.2f}s")
            print(f"      原始得分: {original_score:.4f}, 音乐特征得分: {music_score:.4f}")
            print(f"      最终得分: {final_score:.4f}, 选择策略: {strategy}")
    
    # 第二阶段：已禁用（第二步修复）
    print(f"  第二阶段：已禁用（第二步修复）")
    
    print("搜索完成")
    return best_ref_start, best_mov_start, best_score

def create_aligned_video(dance_video: str, bgm_video: str, output_video: str, 
                        ref_start: int, mov_start: int, sr: int,
                        fast_video: bool = False,
                        hwaccel: Optional[str] = None,
                        video_encode: str = "copy",
                        enable_cache: bool = False,
                        cache_dir: Optional[str] = None) -> bool:
    """创建对齐视频（模块1的输出）"""
    try:
        print("创建对齐视频...")
        
        # 计算时间偏移
        time_offset = ref_start / sr
        print(f"时间偏移: {time_offset:.3f}s (bgm需要延迟{time_offset:.3f}s)")
        
        # 创建静音音频
        silence_duration = time_offset
        silence_samples = int(silence_duration * sr)
        # 读取BGM以确定声道数，保证拼接维度一致
        bgm_audio_path = "temp_bgm_audio.wav"
        if not extract_audio_optimized(bgm_video, bgm_audio_path, 60.0,
                                       enable_cache=enable_cache, cache_dir=cache_dir):
            print("提取BGM音频失败")
            return False
        bgm_audio, _ = sf.read(bgm_audio_path, dtype="float32", always_2d=True)  # (samples, channels)
        num_channels = bgm_audio.shape[1] if bgm_audio.ndim == 2 else 1
        # 生成与BGM相同声道数的静音
        if num_channels > 1:
            silence_audio = np.zeros((silence_samples, num_channels), dtype=np.float32)
        else:
            silence_audio = np.zeros(silence_samples, dtype=np.float32)
        
        # 加载BGM音频（已在上面读取为float32、2D保证）
        
        # 拼接静音 + BGM
        combined_audio = np.concatenate([silence_audio, bgm_audio], axis=0)
        
        # 保存组合音频
        combined_audio_path = "temp_combined_audio.wav"
        sf.write(combined_audio_path, combined_audio, sr)
        
        # 创建最终视频
        cmd = ['ffmpeg', '-y']
        # 硬件加速（对解码阶段有效；对copy无显著影响，但保持参数一致性）
        if hwaccel:
            cmd += ['-hwaccel', hwaccel]
        cmd += [
            '-i', dance_video,
            '-i', combined_audio_path,
        ]
        # 对齐阶段不改变视频像素，仅替换音轨 → 优先视频流复制
        cmd += ['-c:v', 'copy']
        # 音频编码采用aac，保持与现有输出一致（不影响对齐准确性）
        cmd += ['-c:a', 'aac']
        cmd += [
            '-map', '0:v:0',
            '-map', '1:a:0',
            output_video
        ]
        
        # 增强异常处理
        try:
            from beatsync_utils import run_ffmpeg_command
            success, error_msg = run_ffmpeg_command(cmd, f"创建对齐视频 {os.path.basename(output_video)}")
            if not success:
                print(f"创建对齐视频失败: {error_msg}")
                # 清理临时文件
                for temp_file in [bgm_audio_path, combined_audio_path]:
                    if os.path.exists(temp_file):
                        try:
                            os.remove(temp_file)
                        except:
                            pass
                return False
        except ImportError:
            # 如果工具模块不可用，使用基础方法
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            if result.returncode != 0:
                print(f"创建对齐视频失败: {result.stderr[:200]}")
                # 清理临时文件
                for temp_file in [bgm_audio_path, combined_audio_path]:
                    if os.path.exists(temp_file):
                        try:
                            os.remove(temp_file)
                        except:
                            pass
                return False
        
        # 清理临时文件
        for temp_file in [bgm_audio_path, combined_audio_path]:
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except:
                    pass
        
        return True
        
    except Exception as e:
        print(f"创建对齐视频失败: {e}")
        return False

def alignment_module(dance_video: str, bgm_video: str, result_video: str,
                     fast_video: bool = False,
                     hwaccel: Optional[str] = None,
                     video_encode: str = "copy",
                     enable_cache: bool = False,
                     cache_dir: Optional[str] = None,
                     ffmpeg_threads: Optional[int] = None) -> tuple:
    """
    对齐模块：输出对齐后的视频
    返回: (success: bool, dance_alignment: float) - 成功标志和dance视频的对齐点（秒）
    """
    try:
        import time
        step_start = time.time()
        print("=== 模块1: 对齐模块 ===")
        
        # 提取音频
        print("[步骤1.1] 提取音频片段（前30秒）...")
        step_time = time.time()
        if not extract_audio_optimized(dance_video, "temp_dance_audio.wav", 30.0,
                                       enable_cache=enable_cache, cache_dir=cache_dir):
            print("提取dance音频失败")
            return False, 0.0
        print(f"[步骤1.1] 完成，耗时: {time.time() - step_time:.1f}秒")
            
        step_time = time.time()
        if not extract_audio_optimized(bgm_video, "temp_bgm_audio.wav", 30.0,
                                       enable_cache=enable_cache, cache_dir=cache_dir):
            print("提取bgm音频失败")
            return False, 0.0
        print(f"[步骤1.2] 完成，耗时: {time.time() - step_time:.1f}秒")
        
        # 加载音频（以float32降低峰值内存），并在分析阶段转换为单声道
        print("[步骤1.3] 加载音频...")
        step_time = time.time()
        dance_audio, sr = sf.read("temp_dance_audio.wav", dtype="float32", always_2d=False)
        bgm_audio, _ = sf.read("temp_bgm_audio.wav", dtype="float32", always_2d=False)
        print(f"[步骤1.3] 完成，耗时: {time.time() - step_time:.1f}秒")
        print(f"音频长度: dance={len(dance_audio)/sr:.2f}s, bgm={len(bgm_audio)/sr:.2f}s")
        
        # 仅用于对齐分析的单声道转换（输出仍保持双声道，不影响功能与精度）
        print("[步骤1.4] 转换为单声道...")
        step_time = time.time()
        if isinstance(dance_audio, np.ndarray) and dance_audio.ndim > 1:
            dance_mono = librosa.to_mono(dance_audio.T)
        else:
            dance_mono = dance_audio
        if isinstance(bgm_audio, np.ndarray) and bgm_audio.ndim > 1:
            bgm_mono = librosa.to_mono(bgm_audio.T)
        else:
            bgm_mono = bgm_audio
        print(f"[步骤1.4] 完成，耗时: {time.time() - step_time:.1f}秒")
        
        # 执行多策略融合对齐算法（使用单声道分析以控制内存）
        print("[步骤1.5] 执行多策略融合对齐算法...")
        step_time = time.time()
        ref_start, mov_start, confidence = find_beat_alignment_multi_strategy(dance_mono, bgm_mono, sr)
        print(f"[步骤1.5] 完成，耗时: {time.time() - step_time:.1f}秒")
        
        dance_alignment = ref_start / sr  # 保存dance对齐点（秒）
        
        print(f"[模块1] 总耗时: {time.time() - step_start:.1f}秒")
        print(f"对齐结果:")
        print(f"  dance 开始: {dance_alignment:.2f}s")
        print(f"  bgm 开始: {mov_start/sr:.2f}s")
        print(f"  最终得分: {confidence:.4f}")
        
        # 释放仅用于分析的大数组，避免后续步骤峰值累积
        del dance_mono, bgm_mono
        
        # 创建对齐视频
        print("[步骤1.6] 创建对齐视频...")
        step_time = time.time()
        if not create_aligned_video(dance_video, bgm_video, result_video, ref_start, mov_start, sr,
                                    fast_video=fast_video, hwaccel=hwaccel, video_encode=video_encode,
                                    enable_cache=enable_cache, cache_dir=cache_dir):
            print("创建对齐视频失败")
            return False, 0.0
        print(f"[步骤1.6] 完成，耗时: {time.time() - step_time:.1f}秒")
        
        print("模块1完成: 对齐视频已生成")
        return True, dance_alignment
        
    except Exception as e:
        print(f"对齐模块失败: {e}")
        return False, 0.0
    finally:
        # 清理临时文件
        for temp_file in ["temp_dance_audio.wav", "temp_bgm_audio.wav"]:
            if os.path.exists(temp_file):
                os.remove(temp_file)

# ==================== 模块2: 裁剪模块 ====================

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

def detect_trailing_silent_with_decay(audio_path: str, video_duration: float, sr: int = 22050) -> float:
    """
    检测末尾静音段落，使用音频衰减检测（从V2版本复用）
    
    参数:
        audio_path: 音频文件路径
        video_duration: 视频总时长
        sr: 音频采样率
    
    返回:
        需要裁剪的时长（秒）
    """
    try:
        # 加载音频并计算RMS值
        audio, _ = sf.read(audio_path)
        
        # 计算音频能量（RMS）- 滑动窗口
        window_size = int(0.1 * sr)  # 100ms窗口
        hop_size = int(0.05 * sr)    # 50ms步长
        
        rms_values = []
        for i in range(0, len(audio) - window_size, hop_size):
            segment = audio[i:i + window_size]
            rms = np.sqrt(np.mean(segment ** 2))
            rms_values.append(rms)
        
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
            return video_duration
            
    except Exception as e:
        print(f"检测末尾静音段落失败: {e}")
        return 0.0

def get_video_duration(video_path: str) -> float:
    """获取视频时长"""
    cmd = [
        'ffprobe', '-v', 'quiet',
        '-show_entries', 'format=duration',
        '-of', 'csv=p=0',
        video_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return float(result.stdout.strip())

def trim_silent_segments_module(input_video: str, output_video: str, dance_video: str, dance_alignment: float,
                                fast_video: bool = False,
                                hwaccel: Optional[str] = None,
                                video_encode: str = "encode",
                                ffmpeg_threads: Optional[int] = None) -> bool:
    """
    裁剪模块：剪掉视频前面的连续无声段落，以及后面超出dance有效内容的部分
    
    参数:
        input_video: 模块1输出的对齐视频
        output_video: 最终输出视频
        dance_video: 原始dance视频路径（用于计算有效时长）
        dance_alignment: dance视频的对齐点（秒）
    """
    try:
        import time
        step_start = time.time()
        print("=== 模块2: 裁剪模块 ===")
        
        # 1. 提取音频
        temp_audio = "temp_audio_for_detection.wav"
        step_time = time.time()
        cmd_extract = [
            'ffmpeg', '-y',
            '-nostdin', '-hide_banner', '-v', 'error',
            '-i', input_video,
            '-vn', '-acodec', 'pcm_s16le', '-ar', '22050', '-ac', '2',
            temp_audio
        ]
        # 增强异常处理
        try:
            from beatsync_utils import run_ffmpeg_command
            success, error_msg = run_ffmpeg_command(cmd_extract, f"提取音频用于检测 {os.path.basename(input_video)}")
            if not success:
                print(f"提取音频失败: {error_msg}")
                return False
        except ImportError:
            # 如果工具模块不可用，使用基础方法
            result = subprocess.run(cmd_extract, capture_output=True, text=True, timeout=300)
            if result.returncode != 0:
                print(f"提取音频失败: {result.stderr[:200]}")
                return False
        print(f"[步骤2.1] 完成，耗时: {time.time() - step_time:.1f}秒")
        
        # 2. 检测前面的无声段落长度（用于验证）
        print("[步骤2.2] 检测前面的无声段落...")
        step_time = time.time()
        silent_duration = detect_silent_segment_length(temp_audio)
        print(f"[步骤2.2] 完成，耗时: {time.time() - step_time:.1f}秒")
        print(f"检测到前面无声段落长度: {silent_duration:.3f}s")
        
        # 3. 计算dance视频的有效内容时长
        print("[步骤2.3] 计算dance视频有效内容时长...")
        step_time = time.time()
        dance_duration = get_video_duration(dance_video)
        dance_effective_duration = dance_duration - dance_alignment
        print(f"[步骤2.3] 完成，耗时: {time.time() - step_time:.1f}秒")
        print(f"dance视频总时长: {dance_duration:.3f}s")
        print(f"dance对齐点: {dance_alignment:.3f}s")
        print(f"dance有效内容时长: {dance_effective_duration:.3f}s")
        
        # 4. 检测末尾静音段落（使用音频衰减检测）
        print("[步骤2.4] 检测末尾静音段落...")
        step_time = time.time()
        input_video_duration = get_video_duration(input_video)
        trailing_silent_duration = detect_trailing_silent_with_decay(temp_audio, input_video_duration)
        print(f"[步骤2.4] 完成，耗时: {time.time() - step_time:.1f}秒")
        
        # 5. 计算最终的有效时长
        # 使用dance有效内容时长和末尾静音检测结果的较小值
        final_duration = min(dance_effective_duration, input_video_duration - dance_alignment - trailing_silent_duration)
        print(f"根据dance有效内容: {dance_effective_duration:.3f}s")
        print(f"根据末尾静音检测: {input_video_duration - dance_alignment - trailing_silent_duration:.3f}s")
        print(f"最终有效时长: {final_duration:.3f}s")
        
        # 6. 使用对齐点作为裁剪起点（更精确）
        trim_start = dance_alignment
        print(f"裁剪视频：起点={trim_start:.3f}s（对齐点），时长={final_duration:.3f}s")
        # 选择编码策略：默认保持原逻辑（libx264 fast），在fast_video下使用更快预设或硬件编码。
        cmd_trim = ['ffmpeg', '-y']
        if hwaccel:
            cmd_trim += ['-hwaccel', hwaccel]
        if ffmpeg_threads is not None:
            cmd_trim += ['-threads', str(ffmpeg_threads)]
        cmd_trim += [
            '-ss', str(trim_start),
            '-t', str(final_duration),
            '-i', input_video,
        ]
        # 保证时间精度：输出阶段统一重新编码（除非明确选择copy且起点为0）
        use_copy = (video_encode == 'copy' and abs(trim_start) < 1e-3)
        if use_copy:
            # 仅当从0开始裁剪时安全复制，避免关键帧误差
            cmd_trim += ['-c:v', 'copy']
        else:
            if video_encode == 'videotoolbox':
                # macOS 硬件编码（H.264），质量用crf等价控制不可用，这里使用比特率/质量平衡的默认
                # 为避免“Error setting bitrate property”之类报错，显式设置码率控制参数
                # 并固定像素格式为 yuv420p，提升兼容性
                cmd_trim += [
                    '-c:v', 'h264_videotoolbox',
                    '-b:v', '6M',
                    '-maxrate', '8M',
                    '-bufsize', '12M',
                    '-pix_fmt', 'yuv420p'
                ]
            else:
                # x264 编码：在fast_video 下用 ultrafast，否则保持 fast，保证与原有输出一致性
                preset = 'ultrafast' if fast_video else 'fast'
                cmd_trim += ['-c:v', 'libx264', '-preset', preset, '-crf', '28']  # 从23改为28，减小文件大小约40-50%
        cmd_trim += ['-c:a', 'aac', '-b:a', '192k', output_video]
        
        # 增强异常处理
        try:
            from beatsync_utils import run_ffmpeg_command
            success, error_msg = run_ffmpeg_command(cmd_trim, f"裁剪视频 {os.path.basename(output_video)}")
            if not success:
                # 若硬件编码失败，自动回退到 x264 ultrafast，保证功能与时间轴不变
                if video_encode == 'videotoolbox':
                    print("硬件编码失败，回退到 x264 ultrafast ...")
                    cmd_trim_fallback = ['ffmpeg', '-y']
                    if hwaccel:
                        cmd_trim_fallback += ['-hwaccel', hwaccel]
                    if ffmpeg_threads is not None:
                        cmd_trim_fallback += ['-threads', str(ffmpeg_threads)]
                    cmd_trim_fallback += [
                        '-ss', str(trim_start),
                        '-t', str(final_duration),
                        '-i', input_video,
                        '-c:v', 'libx264', '-preset', 'ultrafast', '-crf', '28',  # 从23改为28，减小文件大小
                        '-c:a', 'aac', '-b:a', '192k',
                        output_video
                    ]
                    fb_success, fb_error_msg = run_ffmpeg_command(cmd_trim_fallback, f"裁剪视频（回退方案） {os.path.basename(output_video)}")
                    if not fb_success:
                        print(f"裁剪视频失败（回退方案也失败）: {fb_error_msg}")
                        return False
                else:
                    print(f"裁剪视频失败: {error_msg}")
                    return False
        except ImportError:
            # 如果工具模块不可用，使用基础方法
            result = subprocess.run(cmd_trim, capture_output=True, text=True, timeout=300)
            if result.returncode != 0:
                # 若硬件编码失败，自动回退到 x264 ultrafast，保证功能与时间轴不变
                if video_encode == 'videotoolbox':
                    print("硬件编码失败，回退到 x264 ultrafast ...")
                    cmd_trim_fallback = ['ffmpeg', '-y']
                    if hwaccel:
                        cmd_trim_fallback += ['-hwaccel', hwaccel]
                    if ffmpeg_threads is not None:
                        cmd_trim_fallback += ['-threads', str(ffmpeg_threads)]
                    cmd_trim_fallback += [
                        '-ss', str(trim_start),
                        '-t', str(final_duration),
                        '-i', input_video,
                        '-c:v', 'libx264', '-preset', 'ultrafast', '-crf', '28',  # 从23改为28，减小文件大小
                        '-c:a', 'aac', '-b:a', '192k',
                        output_video
                    ]
                    fb = subprocess.run(cmd_trim_fallback, capture_output=True, text=True, timeout=300)
                    if fb.returncode != 0:
                        print(f"裁剪视频失败（回退后仍失败）: {result.stderr}\nFB: {fb.stderr}")
                        return False
                else:
                    print(f"裁剪视频失败: {result.stderr[:200]}")
                    return False
            # 如果returncode是0，继续执行（不进入else）
        
        print(f"[步骤2.5] 完成，耗时: {time.time() - step_time:.1f}秒")
        
        print(f"[模块2] 总耗时: {time.time() - step_start:.1f}秒")
        
        # 5. 清理临时文件
        if os.path.exists(temp_audio):
            os.remove(temp_audio)
        
        print("模块2完成: 精剪视频已生成")
        return True
        
    except Exception as e:
        print(f"裁剪模块失败: {e}")
        return False

# ==================== 主程序 ====================

def fine_cut_modular_mode(dance_video: str, bgm_video: str, output_video: str,
                          fast_video: bool = False,
                          hwaccel: Optional[str] = None,
                          video_encode: str = "copy",
                          enable_cache: bool = False,
                          cache_dir: Optional[str] = None,
                          ffmpeg_threads: Optional[int] = None,
                          lib_threads: Optional[int] = None) -> bool:
    """模块解耦精剪模式主函数"""
    try:
        print("BeatSync 模块解耦精剪模式开始处理...")
        print(f"  dance: {dance_video}")
        print(f"  bgm: {bgm_video}")
        print(f"  输出: {output_video}")
        
        # 生成模块1的输出文件名
        base_name = os.path.splitext(os.path.basename(output_video))[0]
        output_dir = os.path.dirname(output_video) if os.path.dirname(output_video) else "."
        result_video = os.path.join(output_dir, f"{base_name}_module1_aligned.mp4")
        
        # 模块1: 对齐模块
        success, dance_alignment = alignment_module(dance_video, bgm_video, result_video,
                                                    fast_video=fast_video, hwaccel=hwaccel, video_encode=video_encode,
                                                    enable_cache=enable_cache, cache_dir=cache_dir,
                                                    ffmpeg_threads=ffmpeg_threads)
        if not success:
            print("对齐模块失败")
            return False
        
        print(f"模块1输出已保存: {result_video}")
        
        # 模块2: 裁剪模块
        if not trim_silent_segments_module(result_video, output_video, dance_video, dance_alignment,
                                           fast_video=fast_video, hwaccel=hwaccel,
                                           video_encode=("encode" if video_encode == "copy" else video_encode),
                                           ffmpeg_threads=ffmpeg_threads):
            print("裁剪模块失败")
            return False
        
        # 删除中间文件
        try:
            if os.path.exists(result_video):
                os.remove(result_video)
                print(f"已删除中间文件: {result_video}")
        except Exception as e:
            print(f"删除中间文件失败: {e}")
        
        print("模块解耦精剪模式处理成功!")
        print(f"最终输出: {output_video}")
        return True
        
    except Exception as e:
        print(f"模块解耦精剪模式处理失败: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="BeatSync 模块解耦精剪模式")
    parser.add_argument('--dance', type=str, required=True, help='Dance视频路径')
    parser.add_argument('--bgm', type=str, required=True, help='BGM视频路径')
    parser.add_argument('--output', type=str, required=True, help='输出视频路径')
    parser.add_argument('--fast-video', action='store_true', help='启用快速视频路径（更快的编码/可选硬件加速），不改变对齐逻辑')
    parser.add_argument('--hwaccel', type=str, default=None, choices=[None, 'videotoolbox', 'auto'], help='硬件加速选项（如 macOS 的 videotoolbox）')
    parser.add_argument('--video-encode', type=str, default='x264_fast', choices=['copy', 'x264_fast', 'videotoolbox'], help='出片阶段的视频编码策略')
    parser.add_argument('--enable-cache', action='store_true', help='启用音频提取缓存（基于输入签名）')
    parser.add_argument('--cache-dir', type=str, default='.beatsync_cache', help='缓存目录')
    parser.add_argument('--threads', type=int, default=None, help='ffmpeg 线程数（不指定则使用默认）')
    parser.add_argument('--lib-threads', type=int, default=None, help='数值库线程（OMP/MKL/NUMEXPR），不指定则不干预')
    
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
    temp_dir = tempfile.mkdtemp(prefix="beatsync_format_")
    normalized_files = []  # 记录需要清理的临时文件
    
    try:
        # 对dance和bgm视频进行格式转换
        dance_video, converted_dance = normalize_video_format(args.dance, temp_dir=temp_dir)
        if converted_dance:
            normalized_files.append(dance_video)
        
        bgm_video, converted_bgm = normalize_video_format(args.bgm, temp_dir=temp_dir)
        if converted_bgm:
            normalized_files.append(bgm_video)
        
        # 默认策略（用户未显式指定时）：启用快速路径、启用缓存、设置线程
        if not args.fast_video:
            args.fast_video = True
        if not args.enable_cache:
            args.enable_cache = True
        if args.threads is None:
            args.threads = 4
        if args.lib_threads is None:
            args.lib_threads = 1

        # 规范化编码策略
        video_encode = 'copy'
        if args.video_encode == 'x264_fast':
            video_encode = 'encode'
        elif args.video_encode == 'videotoolbox':
            video_encode = 'videotoolbox'
        hwaccel = None if args.hwaccel in (None, 'auto') else args.hwaccel
        # 线程环境（可选）：不影响数值结果，仅影响并行
        if args.lib_threads is not None:
            os.environ['OMP_NUM_THREADS'] = str(args.lib_threads)
            os.environ['MKL_NUM_THREADS'] = str(args.lib_threads)
            os.environ['NUMEXPR_NUM_THREADS'] = str(args.lib_threads)
        success = fine_cut_modular_mode(dance_video, bgm_video, args.output,
                                        fast_video=args.fast_video,
                                        hwaccel=hwaccel,
                                        video_encode=video_encode,
                                        enable_cache=args.enable_cache,
                                        cache_dir=args.cache_dir,
                                        ffmpeg_threads=args.threads,
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
            if os.path.exists(temp_dir) and not os.listdir(temp_dir):
                os.rmdir(temp_dir)
        except Exception:
            pass

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
