#!/usr/bin/env python3
"""
BeatSync 工具模块
包含异常处理、输入验证等辅助函数
"""

import os
import subprocess
import traceback
import gc
from typing import Tuple, Optional

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

def validate_input_files(dance_video: str, bgm_video: str, output_video: str) -> Tuple[bool, str]:
    """
    验证输入文件的有效性
    
    参数:
        dance_video: Dance视频路径
        bgm_video: BGM视频路径
        output_video: 输出视频路径
    
    返回:
        (是否有效, 错误信息)
    """
    errors = []
    
    # 1. 检查文件存在性
    if not os.path.exists(dance_video):
        errors.append(f"Dance视频文件不存在: {dance_video}")
    if not os.path.exists(bgm_video):
        errors.append(f"BGM视频文件不存在: {bgm_video}")
    
    # 2. 检查文件格式（使用ffprobe）
    for video_path, name in [(dance_video, "dance"), (bgm_video, "bgm")]:
        if os.path.exists(video_path):
            # 检查视频流
            cmd = [
                'ffprobe', '-v', 'error',
                '-select_streams', 'v:0',
                '-show_entries', 'stream=codec_name',
                '-of', 'csv=p=0',
                video_path
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            if result.returncode != 0:
                errors.append(f"{name}视频格式无效或无法读取: {video_path}")
                if result.stderr:
                    errors.append(f"  错误详情: {result.stderr[:200]}")
                continue
            
            # 检查是否有音频轨道
            cmd = [
                'ffprobe', '-v', 'error',
                '-select_streams', 'a:0',
                '-show_entries', 'stream=codec_name',
                '-of', 'csv=p=0',
                video_path
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            if result.returncode != 0:
                errors.append(f"{name}视频没有音频轨道: {video_path}")
    
    # 3. 检查输出目录权限
    output_dir = os.path.dirname(output_video) if os.path.dirname(output_video) else "."
    if not os.path.exists(output_dir):
        try:
            os.makedirs(output_dir, exist_ok=True)
        except PermissionError as e:
            errors.append(f"无法创建输出目录（权限不足）: {output_dir} - {e}")
        except Exception as e:
            errors.append(f"创建输出目录失败: {output_dir} - {e}")
    elif not os.access(output_dir, os.W_OK):
        errors.append(f"输出目录不可写（权限不足）: {output_dir}")
    
    if errors:
        return False, "\n".join(errors)
    return True, ""

def run_ffmpeg_command(cmd: list, description: str = "", timeout: int = 300) -> Tuple[bool, str]:
    """
    执行FFmpeg命令，返回详细错误信息
    
    参数:
        cmd: FFmpeg命令列表
        description: 命令描述（用于错误信息）
        timeout: 超时时间（秒）
    
    返回:
        (是否成功, 错误信息)
    """
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        if result.returncode != 0:
            error_msg = f"FFmpeg命令失败 ({description}):\n"
            error_msg += f"  命令: {' '.join(cmd[:10])}{'...' if len(cmd) > 10 else ''}\n"
            error_msg += f"  返回码: {result.returncode}\n"
            
            # 限制错误输出长度
            stderr_preview = result.stderr[:500] if result.stderr else "无错误输出"
            error_msg += f"  错误输出: {stderr_preview}"
            
            # 分析常见错误类型
            stderr_lower = result.stderr.lower() if result.stderr else ""
            if "invalid data found" in stderr_lower or "invalid" in stderr_lower:
                error_msg += "\n  可能原因: 输入文件格式不支持或损坏"
            elif "permission denied" in stderr_lower:
                error_msg += "\n  可能原因: 文件权限不足"
            elif "no such file" in stderr_lower or "cannot find" in stderr_lower:
                error_msg += "\n  可能原因: 输入文件路径错误"
            elif "codec" in stderr_lower:
                error_msg += "\n  可能原因: 编解码器不支持"
            elif "out of memory" in stderr_lower or "memory" in stderr_lower:
                error_msg += "\n  可能原因: 内存不足"
            
            return False, error_msg
        
        return True, ""
        
    except subprocess.TimeoutExpired:
        return False, f"FFmpeg命令超时 ({description})，可能文件过大或系统负载过高"
    except FileNotFoundError:
        return False, "FFmpeg未安装或不在PATH中，请确保已安装FFmpeg"
    except Exception as e:
        return False, f"FFmpeg命令执行异常 ({description}): {e}\n详细错误: {traceback.format_exc()}"

def parse_fps_safely(fps_str: str, default: float = 25.0) -> float:
    """
    安全解析视频帧率字符串
    
    参数:
        fps_str: 帧率字符串（如 "30/1", "25", "29.97"）
        default: 解析失败时的默认值
    
    返回:
        帧率（浮点数）
    """
    if not fps_str or fps_str.strip() == '':
        print(f"  警告: 帧率字符串为空，使用默认值 {default}")
        return default
    
    fps_str = fps_str.strip()
    
    try:
        # 处理分数格式（如 "30/1"）
        if '/' in fps_str:
            parts = fps_str.split('/')
            if len(parts) == 2:
                num = int(parts[0])
                den = int(parts[1])
                if den != 0:
                    fps = num / den
                    if fps > 0 and fps < 200:  # 合理性检查
                        return fps
                    else:
                        print(f"  警告: 帧率值不合理 ({fps})，使用默认值 {default}")
                        return default
                else:
                    print(f"  警告: 帧率分母为0，使用默认值 {default}")
                    return default
            else:
                print(f"  警告: 帧率格式错误 ({fps_str})，使用默认值 {default}")
                return default
        else:
            # 直接解析浮点数
            fps = float(fps_str)
            if fps > 0 and fps < 200:  # 合理性检查
                return fps
            else:
                print(f"  警告: 帧率值不合理 ({fps})，使用默认值 {default}")
                return default
    except (ValueError, ZeroDivisionError) as e:
        print(f"  警告: 帧率解析失败 ({fps_str})，使用默认值 {default}: {e}")
        return default

def get_video_fps(video_path: str, default: float = 25.0) -> float:
    """
    获取视频帧率（增强错误处理）
    
    参数:
        video_path: 视频路径
        default: 获取失败时的默认值
    
    返回:
        帧率（浮点数）
    """
    try:
        cmd = [
            'ffprobe', '-v', 'error',  # 改为 error 级别，避免警告干扰
            '-select_streams', 'v:0',
            '-show_entries', 'stream=r_frame_rate',
            '-of', 'csv=p=0',
            video_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        
        if result.returncode != 0:
            print(f"  警告: 无法获取视频帧率（ffprobe返回码 {result.returncode}），使用默认值 {default}")
            if result.stderr:
                print(f"  错误详情: {result.stderr[:200]}")
            return default
        
        fps_str = result.stdout.strip()
        return parse_fps_safely(fps_str, default)
        
    except subprocess.TimeoutExpired:
        print(f"  警告: 获取视频帧率超时，使用默认值 {default}")
        return default
    except Exception as e:
        print(f"  警告: 获取视频帧率异常，使用默认值 {default}: {e}")
        return default

def validate_audio_file(audio_path: str) -> Tuple[bool, str]:
    """
    验证音频文件是否有效
    
    参数:
        audio_path: 音频文件路径
    
    返回:
        (是否有效, 错误信息)
    """
    if not os.path.exists(audio_path):
        return False, f"音频文件不存在: {audio_path}"
    
    if os.path.getsize(audio_path) == 0:
        return False, f"音频文件为空: {audio_path}"
    
    # 尝试使用ffprobe验证
    try:
        cmd = [
            'ffprobe', '-v', 'error',
            '-select_streams', 'a:0',
            '-show_entries', 'stream=codec_name',
            '-of', 'csv=p=0',
            audio_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        if result.returncode != 0:
            return False, f"音频文件格式无效: {audio_path}"
    except Exception as e:
        return False, f"验证音频文件失败: {e}"
    
    return True, ""

def check_memory_usage(warning_threshold_mb: int = 6000, critical_threshold_mb: int = 8000) -> Tuple[bool, str]:
    """
    检查内存使用情况，超过阈值返回警告
    
    参数:
        warning_threshold_mb: 警告阈值（MB）
        critical_threshold_mb: 严重警告阈值（MB）
    
    返回:
        (是否正常, 状态信息)
    """
    if not PSUTIL_AVAILABLE:
        # 如果psutil不可用，返回正常（不阻止处理）
        return True, "内存监控不可用（psutil未安装）"
    
    try:
        process = psutil.Process(os.getpid())
        memory_mb = process.memory_info().rss / 1024 / 1024
        
        if memory_mb > critical_threshold_mb:
            # 严重警告：尝试垃圾回收
            print(f"  ⚠️  严重警告: 内存使用过高 ({memory_mb:.1f}MB > {critical_threshold_mb}MB)，尝试垃圾回收...")
            gc.collect()
            memory_mb_after = process.memory_info().rss / 1024 / 1024
            print(f"  垃圾回收后: {memory_mb_after:.1f}MB")
            
            if memory_mb_after > critical_threshold_mb:
                return False, f"内存使用仍然过高 ({memory_mb_after:.1f}MB)，可能影响处理性能"
            else:
                return True, f"垃圾回收后内存正常 ({memory_mb_after:.1f}MB)"
        elif memory_mb > warning_threshold_mb:
            # 警告：建议垃圾回收
            print(f"  ⚠️  警告: 内存使用较高 ({memory_mb:.1f}MB > {warning_threshold_mb}MB)")
            gc.collect()
            memory_mb_after = process.memory_info().rss / 1024 / 1024
            if memory_mb_after < memory_mb * 0.9:  # 如果回收了至少10%
                print(f"  垃圾回收后: {memory_mb_after:.1f}MB (释放了 {memory_mb - memory_mb_after:.1f}MB)")
            return True, f"内存使用正常 ({memory_mb_after:.1f}MB)"
        else:
            return True, f"内存使用正常 ({memory_mb:.1f}MB)"
            
    except Exception as e:
        # 监控失败不影响处理
        return True, f"内存监控异常: {e}"

def get_memory_usage_mb() -> Optional[float]:
    """
    获取当前进程内存使用量（MB）
    
    返回:
        内存使用量（MB），如果不可用则返回None
    """
    if not PSUTIL_AVAILABLE:
        return None
    
    try:
        process = psutil.Process(os.getpid())
        return process.memory_info().rss / 1024 / 1024
    except:
        return None

def manage_cache(cache_dir: str, max_files: int = 100, max_size_mb: int = 5000) -> Tuple[int, float]:
    """
    管理缓存目录，清理旧文件以保持缓存大小在限制内
    
    参数:
        cache_dir: 缓存目录路径
        max_files: 最大缓存文件数
        max_size_mb: 最大缓存大小（MB）
    
    返回:
        (删除的文件数, 释放的空间MB)
    """
    if not os.path.exists(cache_dir):
        return 0, 0.0
    
    try:
        # 获取所有缓存文件及其信息
        cache_files = []
        for filename in os.listdir(cache_dir):
            if filename.endswith('.wav'):
                filepath = os.path.join(cache_dir, filename)
                try:
                    stat = os.stat(filepath)
                    cache_files.append({
                        'path': filepath,
                        'size': stat.st_size,
                        'mtime': stat.st_mtime
                    })
                except:
                    continue
        
        if len(cache_files) == 0:
            return 0, 0.0
        
        # 按修改时间排序（最旧的在前）
        cache_files.sort(key=lambda x: x['mtime'])
        
        # 计算总大小
        total_size_mb = sum(f['size'] for f in cache_files) / (1024 * 1024)
        
        deleted_count = 0
        freed_mb = 0.0
        
        # 如果文件数超过限制，删除最旧的文件
        if len(cache_files) > max_files:
            to_delete = len(cache_files) - max_files
            for i in range(to_delete):
                try:
                    file_size_mb = cache_files[i]['size'] / (1024 * 1024)
                    os.remove(cache_files[i]['path'])
                    deleted_count += 1
                    freed_mb += file_size_mb
                except Exception as e:
                    print(f"  警告: 删除缓存文件失败 {cache_files[i]['path']}: {e}")
        
        # 如果总大小超过限制，继续删除最旧的文件
        if total_size_mb > max_size_mb:
            current_size_mb = total_size_mb - freed_mb
            for cache_file in cache_files[deleted_count:]:
                if current_size_mb <= max_size_mb:
                    break
                try:
                    file_size_mb = cache_file['size'] / (1024 * 1024)
                    os.remove(cache_file['path'])
                    deleted_count += 1
                    freed_mb += file_size_mb
                    current_size_mb -= file_size_mb
                except Exception as e:
                    print(f"  警告: 删除缓存文件失败 {cache_file['path']}: {e}")
        
        if deleted_count > 0:
            print(f"  缓存清理: 删除了 {deleted_count} 个文件，释放了 {freed_mb:.2f}MB")
        
        return deleted_count, freed_mb
        
    except Exception as e:
        print(f"  警告: 缓存管理失败: {e}")
        return 0, 0.0

def get_cache_info(cache_dir: str) -> dict:
    """
    获取缓存目录信息
    
    参数:
        cache_dir: 缓存目录路径
    
    返回:
        缓存信息字典
    """
    if not os.path.exists(cache_dir):
        return {
            'exists': False,
            'file_count': 0,
            'total_size_mb': 0.0
        }
    
    try:
        cache_files = []
        for filename in os.listdir(cache_dir):
            if filename.endswith('.wav'):
                filepath = os.path.join(cache_dir, filename)
                try:
                    stat = os.stat(filepath)
                    cache_files.append({
                        'path': filepath,
                        'size': stat.st_size,
                        'mtime': stat.st_mtime
                    })
                except:
                    continue
        
        total_size_mb = sum(f['size'] for f in cache_files) / (1024 * 1024)
        
        return {
            'exists': True,
            'file_count': len(cache_files),
            'total_size_mb': total_size_mb
        }
    except Exception as e:
        return {
            'exists': True,
            'error': str(e),
            'file_count': 0,
            'total_size_mb': 0.0
        }

