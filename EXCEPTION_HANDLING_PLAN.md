# BeatSync 异常处理增强计划

## 一、当前异常处理现状

### 1.1 已实现的异常处理
- ✅ 基础 try-except 覆盖主要函数
- ✅ 文件存在性检查
- ✅ FFmpeg 命令执行结果检查
- ✅ 子进程超时处理（并行处理器）

### 1.2 存在的问题
- ⚠️ 异常信息不够详细（很多地方只是 `except Exception`）
- ⚠️ 缺少文件格式验证
- ⚠️ 缺少内存溢出预警
- ⚠️ trailing 检测解析异常未完全解决
- ⚠️ 缺少输入参数验证

---

## 二、需要增强的异常处理

### 2.1 输入验证异常 ⭐ 高优先级

#### 问题
- 当前只检查文件是否存在，不验证文件格式
- 不检查视频是否可读、是否有音频轨道
- 不检查输出目录权限

#### 增强方案
```python
def validate_input_files(dance_video: str, bgm_video: str, output_video: str) -> Tuple[bool, str]:
    """验证输入文件的有效性"""
    errors = []
    
    # 1. 检查文件存在性
    if not os.path.exists(dance_video):
        errors.append(f"Dance视频文件不存在: {dance_video}")
    if not os.path.exists(bgm_video):
        errors.append(f"BGM视频文件不存在: {bgm_video}")
    
    # 2. 检查文件格式（使用ffprobe）
    for video_path, name in [(dance_video, "dance"), (bgm_video, "bgm")]:
        if os.path.exists(video_path):
            cmd = ['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 
                   'stream=codec_name', '-of', 'csv=p=0', video_path]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                errors.append(f"{name}视频格式无效或无法读取: {video_path}")
            
            # 检查是否有音频轨道
            cmd = ['ffprobe', '-v', 'error', '-select_streams', 'a:0', '-show_entries', 
                   'stream=codec_name', '-of', 'csv=p=0', video_path]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                errors.append(f"{name}视频没有音频轨道: {video_path}")
    
    # 3. 检查输出目录权限
    output_dir = os.path.dirname(output_video) or "."
    if not os.path.exists(output_dir):
        try:
            os.makedirs(output_dir, exist_ok=True)
        except PermissionError:
            errors.append(f"无法创建输出目录（权限不足）: {output_dir}")
    elif not os.access(output_dir, os.W_OK):
        errors.append(f"输出目录不可写（权限不足）: {output_dir}")
    
    if errors:
        return False, "\n".join(errors)
    return True, ""
```

### 2.2 Trailing 检测解析异常 ⭐ 高优先级

#### 问题
- 已知问题：`could not convert string to float: ''`（正则匹配空串）
- 当前只有基础异常捕获，没有详细定位

#### 增强方案
```python
def detect_black_frames_with_audio_enhanced(video_path: str, position: str = "trailing", 
                                           threshold: float = 0.1) -> float:
    """增强版：检测视频中有声无画面段落"""
    try:
        # ... 原有逻辑 ...
        
        # 获取视频帧率（增强错误处理）
        cmd_fps = [
            'ffprobe', '-v', 'error',  # 改为 error 级别，避免警告干扰
            '-select_streams', 'v:0',
            '-show_entries', 'stream=r_frame_rate',
            '-of', 'csv=p=0',
            video_path
        ]
        result = subprocess.run(cmd_fps, capture_output=True, text=True, check=True)
        fps_str = result.stdout.strip()
        
        # 详细验证 fps_str
        if not fps_str or fps_str == '':
            print(f"  警告: 无法获取视频帧率，使用默认值 25.0")
            fps = 25.0
        else:
            try:
                # 安全解析分数（如 "30/1"）
                if '/' in fps_str:
                    num, den = map(int, fps_str.split('/'))
                    fps = num / den if den != 0 else 25.0
                else:
                    fps = float(fps_str)
            except (ValueError, ZeroDivisionError) as e:
                print(f"  警告: 帧率解析失败 ({fps_str})，使用默认值 25.0: {e}")
                fps = 25.0
        
        # ... 其余逻辑 ...
        
    except subprocess.CalledProcessError as e:
        print(f"  FFprobe命令执行失败: {e}")
        print(f"  错误输出: {e.stderr}")
        return 0.0
    except Exception as e:
        print(f"  检测{position}有声无画面失败: {e}")
        import traceback
        print(f"  详细错误: {traceback.format_exc()}")
        return 0.0
```

### 2.3 内存溢出预警 ⭐ 中优先级

#### 问题
- 处理大文件时可能内存溢出
- 当前没有内存监控和预警

#### 增强方案
```python
import psutil
import gc

def check_memory_usage(warning_threshold_mb: int = 6000) -> bool:
    """检查内存使用情况，超过阈值返回False"""
    process = psutil.Process(os.getpid())
    memory_mb = process.memory_info().rss / 1024 / 1024
    
    if memory_mb > warning_threshold_mb:
        print(f"  警告: 内存使用过高 ({memory_mb:.1f}MB)，尝试垃圾回收...")
        gc.collect()
        memory_mb_after = process.memory_info().rss / 1024 / 1024
        print(f"  垃圾回收后: {memory_mb_after:.1f}MB")
        
        if memory_mb_after > warning_threshold_mb:
            print(f"  严重警告: 内存使用仍然过高，可能影响处理性能")
            return False
    return True

# 在关键位置调用
def find_beat_alignment_multi_strategy(ref_audio, mov_audio, sr):
    """多策略融合的节拍对齐算法（增强内存监控）"""
    try:
        # 在循环中定期检查内存
        for i, ref_offset in enumerate(np.arange(0, max_offset * sr, step_size * sr)):
            if i % 10 == 0:  # 每10次迭代检查一次
                if not check_memory_usage():
                    print("  内存使用过高，建议降低搜索范围或使用更小的hop_length")
            # ... 原有逻辑 ...
    except MemoryError as e:
        print(f"  内存溢出: {e}")
        print(f"  建议: 降低hop_length或缩小搜索范围")
        raise
```

### 2.4 FFmpeg 命令执行异常 ⭐ 中优先级

#### 问题
- FFmpeg 命令失败时，错误信息不够详细
- 不区分不同类型的失败（格式不支持、编码失败、权限问题等）

#### 增强方案
```python
def run_ffmpeg_command(cmd: list, description: str = "") -> Tuple[bool, str]:
    """执行FFmpeg命令，返回详细错误信息"""
    try:
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True,
            timeout=300  # 5分钟超时
        )
        
        if result.returncode != 0:
            error_msg = f"FFmpeg命令失败 ({description}):\n"
            error_msg += f"  命令: {' '.join(cmd)}\n"
            error_msg += f"  返回码: {result.returncode}\n"
            error_msg += f"  错误输出: {result.stderr[:500]}"  # 限制长度
            
            # 分析常见错误类型
            if "Invalid data found" in result.stderr:
                error_msg += "\n  可能原因: 输入文件格式不支持或损坏"
            elif "Permission denied" in result.stderr:
                error_msg += "\n  可能原因: 文件权限不足"
            elif "No such file" in result.stderr:
                error_msg += "\n  可能原因: 输入文件路径错误"
            elif "codec" in result.stderr.lower():
                error_msg += "\n  可能原因: 编解码器不支持"
            
            return False, error_msg
        
        return True, ""
        
    except subprocess.TimeoutExpired:
        return False, f"FFmpeg命令超时 ({description})，可能文件过大或系统负载过高"
    except FileNotFoundError:
        return False, "FFmpeg未安装或不在PATH中"
    except Exception as e:
        return False, f"FFmpeg命令执行异常 ({description}): {e}"
```

### 2.5 音频提取异常 ⭐ 中优先级

#### 问题
- 音频提取失败时，错误信息不够详细
- 不检查提取的音频是否有效

#### 增强方案
```python
def extract_audio_optimized_enhanced(video_path: str, audio_path: str, 
                                     duration: float = 30.0) -> Tuple[bool, str]:
    """增强版音频提取，返回详细错误信息"""
    try:
        cmd = [
            'ffmpeg', '-y',
            '-i', video_path,
            '-t', str(duration),
            '-vn', '-acodec', 'pcm_s16le', '-ar', '22050', '-ac', '2',
            audio_path
        ]
        
        success, error_msg = run_ffmpeg_command(cmd, f"提取音频 {os.path.basename(video_path)}")
        if not success:
            return False, error_msg
        
        # 验证提取的音频文件
        if not os.path.exists(audio_path) or os.path.getsize(audio_path) == 0:
            return False, f"音频提取失败: 输出文件为空或不存在"
        
        # 尝试读取音频验证有效性
        try:
            audio, sr = sf.read(audio_path)
            if len(audio) == 0:
                return False, f"音频提取失败: 音频文件为空"
        except Exception as e:
            return False, f"音频提取失败: 无法读取音频文件 - {e}"
        
        return True, ""
        
    except Exception as e:
        return False, f"音频提取异常: {e}"
```

### 2.6 对齐算法异常 ⭐ 低优先级

#### 问题
- 节拍检测失败时，没有详细错误信息
- 对齐搜索失败时，没有回退方案

#### 增强方案
```python
def find_beat_alignment_multi_strategy_enhanced(ref_audio, mov_audio, sr):
    """增强版多策略对齐，包含详细错误处理和回退"""
    try:
        # 节拍检测（增强错误处理）
        try:
            ref_tempo, ref_beats = librosa.beat.beat_track(y=ref_audio, sr=sr)
            mov_tempo, mov_beats = librosa.beat.beat_track(y=mov_audio, sr=sr)
        except Exception as e:
            print(f"  节拍检测失败: {e}")
            print(f"  尝试使用更宽松的参数...")
            # 回退方案：使用更宽松的参数
            try:
                ref_tempo, ref_beats = librosa.beat.beat_track(
                    y=ref_audio, sr=sr, hop_length=2048, start_bpm=120
                )
                mov_tempo, mov_beats = librosa.beat.beat_track(
                    y=mov_audio, sr=sr, hop_length=2048, start_bpm=120
                )
            except Exception as e2:
                print(f"  回退方案也失败: {e2}")
                return 0, 0, 0.0
        
        # 验证节拍检测结果
        if len(ref_beats) == 0 or len(mov_beats) == 0:
            print(f"  警告: 节拍检测结果为空，可能音频质量较差")
            return 0, 0, 0.0
        
        # ... 原有对齐逻辑 ...
        
    except MemoryError as e:
        print(f"  对齐算法内存溢出: {e}")
        return 0, 0, 0.0
    except Exception as e:
        print(f"  对齐算法异常: {e}")
        import traceback
        print(f"  详细错误: {traceback.format_exc()}")
        return 0, 0, 0.0
```

---

## 三、实施优先级

### 高优先级（上线前完成）
1. ✅ **输入验证异常**：文件格式、权限检查
2. ✅ **Trailing 检测解析异常**：详细错误定位和回退

### 中优先级（上线后1-2周）
3. ⚠️ **内存溢出预警**：内存监控和预警机制
4. ⚠️ **FFmpeg 命令执行异常**：详细错误分析和分类
5. ⚠️ **音频提取异常**：验证提取结果有效性

### 低优先级（后续优化）
6. ⚠️ **对齐算法异常**：回退方案和详细错误信息

---

## 四、实施建议

### 4.1 代码结构
- 创建 `beatsync_utils.py` 工具模块，包含所有异常处理辅助函数
- 在主程序中导入并使用这些函数

### 4.2 日志增强
- 所有异常都记录到日志文件
- 关键异常同时输出到控制台
- 使用统一的错误码和错误消息格式

### 4.3 测试验证
- 创建异常测试用例（损坏文件、无权限目录、超大文件等）
- 验证异常处理是否正常工作

---

## 五、性能方面的待优化问题

### 5.1 当前性能状态 ✅
- 高分辨率：10-30s（已优化）
- 低分辨率：13-38s（已优化）
- 内存峰值：2-4GB（已优化）

### 5.2 潜在优化点

#### 1. 超长视频处理 ⚠️ 中优先级
- **问题**：liangnan_short（bgm 62s）处理时间 100s
- **优化方向**：
  - 分段处理（将长视频分段对齐，再合并）
  - 降低搜索精度（对于超长视频，可以增大步长）
  - 硬件编码（如果设备支持）

#### 2. 批量处理并发控制 ⚠️ 低优先级
- **问题**：批量处理时，多个样本同时处理可能导致系统负载过高
- **优化方向**：
  - 限制并发数（如最多同时处理2个样本）
  - 错峰启动（延迟启动第二个样本）

#### 3. 缓存优化 ⚠️ 低优先级
- **问题**：缓存目录可能无限增长
- **优化方向**：
  - 缓存大小限制（如最多保留100个缓存文件）
  - 缓存清理策略（LRU或按时间清理）

### 5.3 上线前建议
**当前性能已满足上线要求**，上述优化点可以在上线后根据实际使用情况再优化。

---

## 六、总结

### 6.1 异常处理增强
- **必须完成**：输入验证、Trailing检测异常（上线前）
- **建议完成**：内存预警、FFmpeg错误分析（上线后1-2周）
- **可选完成**：对齐算法回退（后续优化）

### 6.2 性能优化
- **当前状态**：已满足上线要求
- **后续优化**：超长视频、批量并发、缓存管理（根据实际需求）

### 6.3 实施时间
- **上线前（1周）**：完成高优先级异常处理
- **上线后（1-2周）**：完成中优先级异常处理
- **后续（按需）**：性能优化和低优先级异常处理

