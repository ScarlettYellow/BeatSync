# BeatSync 异常处理机制文档

## 一、概述

BeatSync 项目实现了全面的异常处理机制，确保程序在各种异常情况下能够：
- 提供详细的错误信息
- 安全地处理异常并回退
- 不影响核心功能的准确性

## 二、异常处理架构

### 2.1 工具模块 (`beatsync_utils.py`)

所有异常处理辅助函数集中在 `beatsync_utils.py` 模块中，包括：

#### 核心函数

1. **`validate_input_files(dance_video, bgm_video, output_video)`**
   - **功能**: 验证输入文件的有效性
   - **检查项**:
     - 文件存在性
     - 视频格式有效性（使用 ffprobe）
     - 音频轨道存在性
     - 输出目录权限
   - **返回**: `(是否有效, 错误信息)`

2. **`run_ffmpeg_command(cmd, description, timeout)`**
   - **功能**: 执行 FFmpeg 命令并返回详细错误信息
   - **特性**:
     - 自动分析常见错误类型
     - 提供可能原因建议
     - 超时保护（默认300秒）
   - **返回**: `(是否成功, 错误信息)`

3. **`parse_fps_safely(fps_str, default)`**
   - **功能**: 安全解析视频帧率字符串
   - **支持格式**: 
     - 分数格式: "30/1"
     - 浮点数格式: "25.0"
   - **特性**: 合理性检查（0 < fps < 200）

4. **`get_video_fps(video_path, default)`**
   - **功能**: 获取视频帧率（增强错误处理）
   - **特性**: 
     - 自动处理各种异常情况
     - 提供默认值回退

5. **`validate_audio_file(audio_path)`**
   - **功能**: 验证音频文件是否有效
   - **检查项**:
     - 文件存在性
     - 文件大小（非空）
     - 格式有效性

### 2.2 向后兼容性

所有异常处理增强都采用**向后兼容**设计：
- 如果 `beatsync_utils` 模块不可用，自动回退到基础方法
- 不影响现有功能的正常运行

## 三、异常处理覆盖范围

### 3.1 输入验证异常 ⭐ 高优先级

**位置**: `beatsync_fine_cut_modular.py` 和 `beatsync_badcase_fix_trim_v2.py` 的 `main()` 函数

**处理内容**:
- ✅ 文件不存在
- ✅ 文件格式无效
- ✅ 缺少音频轨道
- ✅ 输出目录权限不足

**示例**:
```python
from beatsync_utils import validate_input_files
is_valid, error_msg = validate_input_files(args.dance, args.bgm, args.output)
if not is_valid:
    print("输入验证失败:")
    print(error_msg)
    return False
```

### 3.2 Trailing 检测解析异常 ⭐ 高优先级

**位置**: `beatsync_badcase_fix_trim_v2.py` 的 `detect_black_frames_with_audio()` 函数

**问题**: 原代码使用 `eval()` 解析 fps，存在安全风险且可能抛出异常

**解决方案**:
- 使用 `get_video_fps()` 函数安全解析
- 提供默认值回退（25.0 fps）
- 详细错误日志

**修复前**:
```python
fps = eval(result.stdout.strip()) if result.returncode == 0 else 25.0
```

**修复后**:
```python
from beatsync_utils import get_video_fps
fps = get_video_fps(video_path, default=25.0)
```

### 3.3 FFmpeg 命令执行异常 ⭐ 中优先级

**覆盖位置**:
- `extract_audio_optimized()` - 音频提取
- `create_aligned_video()` - 对齐视频创建
- `trim_silent_segments_module()` - 视频裁剪
- `create_trimmed_video()` - V2版本视频合成

**处理内容**:
- ✅ 命令执行失败
- ✅ 超时保护
- ✅ 错误类型分析（格式不支持、权限问题、编解码器问题等）
- ✅ 详细错误信息输出

**示例**:
```python
from beatsync_utils import run_ffmpeg_command
success, error_msg = run_ffmpeg_command(cmd, "提取音频")
if not success:
    print(f"音频提取失败: {error_msg}")
    return False
```

### 3.4 音频提取异常 ⭐ 中优先级

**位置**: `extract_audio_optimized()` 函数

**处理内容**:
- ✅ FFmpeg 命令执行失败
- ✅ 提取的音频文件验证
- ✅ 空文件检测

**示例**:
```python
from beatsync_utils import run_ffmpeg_command, validate_audio_file
success, error_msg = run_ffmpeg_command(cmd, "提取音频")
if not success:
    return False

is_valid, validation_error = validate_audio_file(audio_path)
if not is_valid:
    print(f"音频验证失败: {validation_error}")
    return False
```

## 四、错误信息格式

### 4.1 输入验证错误

```
============================================================
输入验证失败:
Dance视频文件不存在: /path/to/dance.mp4
BGM视频格式无效或无法读取: /path/to/bgm.mp4
  错误详情: Invalid data found when processing input
输出目录不可写（权限不足）: /path/to/output
============================================================
```

### 4.2 FFmpeg 命令错误

```
FFmpeg命令失败 (提取音频 dance.mp4):
  命令: ffmpeg -y -i dance.mp4 ...
  返回码: 1
  错误输出: Invalid data found when processing input
  可能原因: 输入文件格式不支持或损坏
```

### 4.3 帧率解析警告

```
  警告: 帧率解析失败 (30/0)，使用默认值 25.0: division by zero
  警告: 无法获取视频帧率，使用默认值 25.0
```

## 五、测试验证

### 5.1 异常测试用例

位置: `test_exception_handling.py`

**测试场景**:
1. ✅ 文件不存在
2. ✅ 权限不足（只读目录）
3. ✅ 损坏的视频文件
4. ✅ 输出目录不存在（自动创建）
5. ⏭️ 无音频轨道（需要特殊测试文件）

**运行测试**:
```bash
python3 test_exception_handling.py
```

**测试结果**: 所有核心场景通过率 100%

## 六、使用指南

### 6.1 开发者指南

#### 添加新的异常处理

1. **使用工具模块函数**:
```python
from beatsync_utils import run_ffmpeg_command, validate_input_files
```

2. **提供向后兼容**:
```python
try:
    from beatsync_utils import run_ffmpeg_command
    success, error_msg = run_ffmpeg_command(cmd, "操作描述")
    if not success:
        return False
except ImportError:
    # 回退到基础方法
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    if result.returncode != 0:
        return False
```

3. **提供详细错误信息**:
   - 使用描述性的操作名称
   - 包含文件路径信息
   - 提供可能原因建议

### 6.2 用户指南

#### 常见错误及解决方案

1. **"文件不存在"**
   - 检查文件路径是否正确
   - 检查文件是否被移动或删除

2. **"格式无效或无法读取"**
   - 检查视频文件是否损坏
   - 尝试使用其他视频播放器打开文件
   - 考虑重新编码视频

3. **"没有音频轨道"**
   - 确保视频文件包含音频
   - 使用格式转换工具添加音频轨道

4. **"权限不足"**
   - 检查输出目录的写入权限
   - 尝试使用其他输出目录

5. **"FFmpeg命令超时"**
   - 文件可能过大
   - 系统负载可能过高
   - 考虑降低视频分辨率或时长

## 七、性能影响

### 7.1 异常处理开销

- **输入验证**: < 1秒（ffprobe 调用）
- **FFmpeg 错误分析**: 无额外开销（仅失败时执行）
- **帧率解析增强**: 无性能影响（仅解析失败时使用默认值）

### 7.2 内存影响

- 异常处理函数本身不增加内存使用
- 错误信息字符串通常 < 1KB

## 八、未来改进方向

### 8.1 中优先级（上线后1-2周）

1. **内存溢出预警**
   - 监控内存使用情况
   - 超过阈值时发出警告

2. **对齐算法异常回退**
   - 节拍检测失败时的回退方案
   - 更宽松的参数设置

### 8.2 低优先级（后续优化）

1. **统一错误码系统**
   - 定义标准错误码
   - 便于错误追踪和统计

2. **异常日志记录**
   - 记录异常到日志文件
   - 便于问题排查

## 九、总结

### 9.1 已实现功能

- ✅ 输入验证（文件格式、权限检查）
- ✅ Trailing 检测解析异常修复
- ✅ FFmpeg 命令执行异常处理
- ✅ 音频提取验证
- ✅ 向后兼容性保证

### 9.2 测试覆盖

- ✅ 文件不存在
- ✅ 权限不足
- ✅ 损坏文件
- ✅ 输出目录自动创建

### 9.3 上线准备

所有高优先级异常处理已完成，程序已具备：
- 完善的错误处理机制
- 详细的错误信息
- 安全的异常回退
- 向后兼容性

**状态**: ✅ 已准备好上线

