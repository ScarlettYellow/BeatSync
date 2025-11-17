# 视频格式兼容性解决方案

## 一、问题分析

### 当前状态
- 程序使用 ffmpeg 处理视频，ffmpeg 本身支持多种格式
- 但代码中部分地方硬编码了 `.mp4` 扩展名
- 用户可能输入 MOV、AVI、MKV 等格式

### 风险点
- 不同格式可能导致处理失败
- 硬编码扩展名可能导致临时文件命名错误

---

## 二、解决方案（最简单、最低风险）

### 2.1 核心思路
**在入口处统一转换为 MP4，使用 stream copy（零损失转换）**

- ✅ **零风险**：stream copy 只是换容器，不重新编码，不改变内容
- ✅ **保证准确性**：时间轴、音频质量完全不变
- ✅ **最小改动**：只需在入口处添加转换函数
- ✅ **不影响现有逻辑**：后续所有处理逻辑完全不变

### 2.2 实现方案

#### 步骤1：创建格式转换工具函数
```python
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
        output_path = os.path.join(temp_dir, f"{base_name}_normalized.mp4")
    
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
        print(f"格式转换失败: {result.stderr}")
        return video_path, False  # 转换失败，返回原文件（让后续处理尝试）
    
    print(f"格式转换完成: {output_path}")
    return output_path, True
```

#### 步骤2：在主函数入口处调用
```python
def main():
    parser = argparse.ArgumentParser(description="BeatSync 模块解耦精剪模式")
    parser.add_argument('--dance', type=str, required=True, help='Dance视频路径')
    parser.add_argument('--bgm', type=str, required=True, help='BGM视频路径')
    parser.add_argument('--output', type=str, required=True, help='输出视频路径')
    # ... 其他参数 ...
    
    args = parser.parse_args()
    
    # 验证输入文件
    if not os.path.exists(args.dance):
        print(f"Dance视频文件不存在: {args.dance}")
        return False
    
    if not os.path.exists(args.bgm):
        print(f"BGM视频文件不存在: {args.bgm}")
        return False
    
    # 格式标准化（新增）
    temp_dir = tempfile.mkdtemp()
    normalized_files = []  # 记录需要清理的临时文件
    
    try:
        dance_video, converted_dance = normalize_video_format(args.dance, temp_dir=temp_dir)
        if converted_dance:
            normalized_files.append(dance_video)
        
        bgm_video, converted_bgm = normalize_video_format(args.bgm, temp_dir=temp_dir)
        if converted_bgm:
            normalized_files.append(bgm_video)
        
        # 后续处理逻辑完全不变
        success = fine_cut_modular_mode(dance_video, bgm_video, args.output, ...)
        
        return success
        
    finally:
        # 清理临时转换文件
        for temp_file in normalized_files:
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            except:
                pass
        try:
            os.rmdir(temp_dir)
        except:
            pass
```

---

## 三、为什么这个方案最简单、最低风险？

### 3.1 零损失转换
- **stream copy (`-c copy`)**：只复制流，不重新编码
- **不改变内容**：视频帧、音频采样完全不变
- **不改变时间轴**：时间戳、帧率完全保持
- **保证准确性**：对齐算法基于音频，音频不变则结果不变

### 3.2 最小改动
- **只添加一个函数**：`normalize_video_format()`
- **只在入口处调用**：main函数开始处调用一次
- **后续逻辑不变**：所有处理函数完全不需要修改

### 3.3 向后兼容
- **MP4文件**：直接跳过转换，性能无影响
- **其他格式**：自动转换，用户无感知
- **转换失败**：返回原文件，让后续处理尝试（兜底）

### 3.4 安全性
- **临时文件管理**：自动清理转换后的临时文件
- **错误处理**：转换失败不影响主流程
- **资源管理**：使用临时目录，避免文件堆积

---

## 四、支持的格式

### 4.1 理论上支持所有ffmpeg支持的格式
- **常见格式**：MOV, AVI, MKV, FLV, WMV, WebM 等
- **手机格式**：iPhone MOV, Android MP4/MOV
- **专业格式**：ProRes, DNxHD 等（如果ffmpeg支持）

### 4.2 转换策略
- **MP4**：直接使用，不转换
- **其他格式**：stream copy 转换为 MP4
- **不支持格式**：转换失败，返回原文件让后续处理尝试

---

## 五、性能影响

### 5.1 转换时间
- **stream copy**：非常快，通常 < 1秒（只是复制，不编码）
- **对总处理时间影响**：几乎可以忽略（< 1%）

### 5.2 存储影响
- **临时文件**：转换后的文件大小与原文件相同（stream copy）
- **自动清理**：处理完成后自动删除

---

## 六、实施步骤

### 步骤1：在工具模块添加转换函数
- 创建 `beatsync_utils.py` 或直接在现有文件中添加
- 实现 `normalize_video_format()` 函数

### 步骤2：修改主函数入口
- `beatsync_fine_cut_modular.py` 的 `main()` 函数
- `beatsync_badcase_fix_trim_v2.py` 的 `main()` 函数
- `beatsync_parallel_processor.py` 的入口函数

### 步骤3：测试验证
- 测试不同格式（MOV, AVI, MKV等）
- 验证转换后的结果准确性
- 验证性能影响

---

## 七、注意事项

### 7.1 特殊情况
- **损坏文件**：转换可能失败，需要兜底处理
- **超大文件**：stream copy 很快，但需要足够磁盘空间
- **特殊编码**：某些特殊编码可能不支持 stream copy，需要重新编码（但这种情况很少）

### 7.2 错误处理
- **转换失败**：返回原文件，让后续处理尝试
- **文件不存在**：在转换前已检查，不会进入转换流程
- **权限问题**：转换失败，返回原文件

---

## 八、总结

### 8.1 方案优势
- ✅ **最简单**：只添加一个函数，入口处调用
- ✅ **最低风险**：stream copy 零损失，不影响准确性
- ✅ **向后兼容**：MP4文件无影响，其他格式自动处理
- ✅ **性能影响小**：转换时间 < 1秒

### 8.2 实施建议
1. **先实施**：在 modular 和 v2 版本中添加
2. **测试验证**：用不同格式测试
3. **逐步推广**：确认无问题后，应用到并行处理器

---

**下一步**：开始实施格式转换函数，并在主函数入口处集成。

