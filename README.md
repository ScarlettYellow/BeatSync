# BeatSync - 课堂跳舞视频音频替换工具

## 功能说明

专门为街舞课堂设计的音频替换工具，能够自动将课堂跳舞视频的现场收音替换为高质量范例视频的音轨。

## 核心特性

✅ **智能节拍对齐**：自动检测两个视频的音乐节拍，找到最佳对齐位置  
✅ **完全音轨替换**：完全移除课堂视频的原始音轨，只保留范例视频音轨  
✅ **保持视频质量**：保持原始视频的分辨率、帧率和时长  
✅ **自动处理**：无需手动调整，一键完成音频替换  
✅ **并行处理**：同时生成两个版本（modular和V2），用户选择最佳结果  
✅ **格式兼容**：支持 MP4、MOV、AVI、MKV、H.265 等多种视频格式  
✅ **智能裁剪**：自动检测并裁剪无效内容（开头/末尾静音、有声无画面段落）  
✅ **高性能优化**：高分辨率视频处理速度提升 2.7-3倍，支持硬件加速

## 使用场景

- 街舞课堂结课视频制作
- 现场表演视频音频优化
- 音乐视频音质提升
- 任何需要音频替换的视频处理

## 安装依赖

```bash
pip install numpy soundfile librosa opencv-python
```

**系统要求**：
- Python 3.7+
- FFmpeg（必须安装并在PATH中）

## 推荐使用方式

### ⭐ 并行处理器（推荐）

同时生成两个版本，用户选择最佳结果：

```bash
python3 beatsync_parallel_processor.py \
  --dance 课堂视频.mp4 \
  --bgm 范例视频.mp4 \
  --output-dir 输出目录 \
  --sample-name 样本名称
```

**输出文件**：
- `{样本名称}_modular.mp4` - Modular版本（多策略融合，精度高）
- `{样本名称}_v2.mp4` - V2版本（快速对齐，适合特定场景）

## 其他程序版本

### 1. Modular版本 (`beatsync_fine_cut_modular.py`)

**特点**：
- 多策略融合对齐算法（MFCC、Chroma、Spectral Contrast、Spectral Rolloff）
- 对齐精度高，适合大多数场景
- 自动裁剪无效内容段落

```bash
python3 beatsync_fine_cut_modular.py \
  --dance 课堂视频.mp4 \
  --bgm 范例视频.mp4 \
  --output 输出视频.mp4 \
  --fast-video \
  --enable-cache
```

### 2. V2版本 (`beatsync_badcase_fix_trim_v2.py`)

**特点**：
- 简化滑动窗口对齐算法
- 处理速度快
- 适合特定badcase类型（T2 > T1）

```bash
python3 beatsync_badcase_fix_trim_v2.py \
  --dance 课堂视频.mp4 \
  --bgm 范例视频.mp4 \
  --output 输出视频.mp4 \
  --fast-video \
  --enable-cache
```

## 参数说明

### 基础参数
- `--dance`：课堂跳舞视频文件路径（现场收音，音质较差）
- `--bgm`：范例视频文件路径（同首音乐，音质很好）
- `--output`：输出视频文件路径（modular/V2版本）
- `--output-dir`：输出目录（并行处理器）
- `--sample-name`：样本名称（并行处理器）

### 性能优化参数
- `--fast-video`：启用快速视频处理路径（默认启用）
- `--hwaccel videotoolbox`：启用硬件加速（macOS）
- `--video-encode x264_fast`：视频编码策略（copy/x264_fast/videotoolbox）
- `--enable-cache`：启用音频提取缓存（默认启用）
- `--cache-dir .beatsync_cache`：缓存目录
- `--threads 4`：FFmpeg编码线程数
- `--lib-threads 1`：数值计算库线程数

## 使用示例

### 并行处理器（推荐）

```bash
# 处理单个样本
python3 beatsync_parallel_processor.py \
  --dance input_allcases/echo/dance.mp4 \
  --bgm input_allcases/echo/bgm.mp4 \
  --output-dir outputs \
  --sample-name echo

# 批量处理（使用批量脚本）
python3 batch_parallel_processor.py
```

### Modular版本

```bash
python3 beatsync_fine_cut_modular.py \
  --dance dance.mp4 \
  --bgm bgm.mp4 \
  --output result_modular.mp4 \
  --fast-video \
  --enable-cache
```

### V2版本

```bash
python3 beatsync_badcase_fix_trim_v2.py \
  --dance dance.mp4 \
  --bgm bgm.mp4 \
  --output result_v2.mp4 \
  --fast-video \
  --enable-cache
```

## 工作原理

1. **格式标准化**：自动将非MP4格式转换为MP4（零损失）
2. **音频提取**：从两个视频文件中提取音频轨道（支持缓存）
3. **节拍检测**：使用 librosa 检测音频的节拍点和 BPM
4. **智能对齐**：
   - Modular版本：多策略融合对齐（MFCC、Chroma等）
   - V2版本：简化滑动窗口对齐（基于节拍检测）
5. **无效内容检测**：自动检测并裁剪开头/末尾静音、有声无画面段落
6. **视频合成**：将处理后的音频与原始视频合成

## 性能特性

### 高分辨率视频优化
- **处理速度**：1080p/4K视频处理速度提升 **2.7-3倍**（35s → 10-13s）
- **优化技术**：
  - 音频仅解码（`-vn`），避免视频解码开销
  - 视频流复制（`-c:v copy`），避免重新编码
  - 快速编码（`x264 ultrafast`）或硬件加速
  - 音频提取缓存，重复样本自动命中

### 内存优化
- **峰值内存**：从 26GB 降至 **2-4GB**
- **优化技术**：
  - 增加 `hop_length` 至 2048
  - 显式垃圾回收
  - 子进程隔离
  - Numba 本地缓存

## 格式兼容性

✅ **支持的输入格式**：
- MP4（H.264/H.265）
- MOV（iPhone常用）
- AVI
- MKV
- 其他FFmpeg支持的格式

**处理方式**：自动转换为MP4（使用stream copy，零损失）

## 异常处理

程序包含完善的异常处理机制：

- ✅ **输入验证**：文件格式、权限检查
- ✅ **详细错误信息**：FFmpeg命令失败时提供可能原因
- ✅ **安全回退**：异常时自动使用默认值或回退方案
- ✅ **超时保护**：所有FFmpeg命令都有超时设置

## 输出说明

### 并行处理器输出
- **modular版本**：多策略融合对齐，精度高，适合大多数场景
- **v2版本**：快速对齐，适合特定badcase类型
- **建议**：对比两个版本，选择对齐效果更好的

### 输出视频特性
- **视频内容**：来自课堂视频（保持原始分辨率、帧率）
- **音频内容**：完全替换为范例视频音轨
- **时长**：自动裁剪无效内容，保留有效部分
- **质量**：保持原始视频质量，音频替换自然

## 处理示例

```
BeatSync 模块解耦精剪模式开始处理...
  dance: dance.mp4
  bgm: bgm.mp4
  输出: result.mp4
提取音频片段（前30秒）...
加载音频...
音频长度: dance=30.00s, bgm=30.00s
对齐结果:
  dance 开始: 8.20s
  bgm 开始: 0.00s
  最终得分: 0.3103
创建对齐视频...
模块1完成: 对齐视频已生成
检测前面的无声段落...
检测末尾静音段落...
裁剪视频：起点=8.200s（对齐点），时长=22.500s
模块解耦精剪模式处理成功!
最终输出: result.mp4
```

## 注意事项

1. **音乐匹配**：两个视频的音频必须来自同一首歌曲
2. **节拍清晰**：建议音频有清晰的节拍特征，便于对齐
3. **版本选择**：
   - 推荐使用并行处理器，对比两个版本选择最佳结果
   - 大多数场景下，modular版本对齐效果更好
4. **音质提升**：范例视频的音质应该明显优于课堂视频
5. **格式支持**：支持多种视频格式，自动转换为MP4处理

## 故障排除

### 对齐效果不理想
1. 检查两个音频是否来自同一首歌曲
2. 确保音频有清晰的节拍特征
3. 使用并行处理器，对比两个版本选择最佳结果

### 处理速度慢
1. 启用 `--fast-video` 参数（默认已启用）
2. 启用 `--enable-cache` 参数（默认已启用）
3. 如果支持，使用 `--hwaccel videotoolbox` 硬件加速

### 内存不足
1. 程序已优化内存使用，峰值约2-4GB
2. 如果仍不足，考虑降低输入视频分辨率

### 文件格式不支持
1. 程序自动支持多种格式（MP4、MOV、AVI、MKV等）
2. 如果仍有问题，使用FFmpeg手动转换为MP4

## 技术优势

- **自动化程度高**：无需手动调整参数
- **对齐精度高**：基于多策略融合，比传统方法更准确
- **处理速度快**：高分辨率视频优化，处理效率高
- **输出质量好**：保持原始视频质量，音频替换自然
- **灵活选择**：并行处理器提供两个版本供选择
- **格式兼容**：支持多种视频格式，自动转换
- **异常处理完善**：详细的错误信息和安全回退

## 项目结构

```
BeatSync/
├── beatsync_parallel_processor.py    # ⭐ 并行处理器（推荐）
├── beatsync_fine_cut_modular.py      # Modular版本
├── beatsync_badcase_fix_trim_v2.py   # V2版本
├── beatsync_utils.py                  # 工具模块（异常处理）
├── batch_parallel_processor.py        # 批量处理脚本
├── regression_test.py                # 回归测试脚本
├── test_exception_handling.py        # 异常处理测试
├── README.md                          # 使用说明
├── PROJECT_STATUS.md                  # 项目状态
├── PROJECT_SUMMARY.md                 # 项目总结
├── EXCEPTION_HANDLING_GUIDE.md       # 异常处理指南
└── input_allcases/                   # 测试样本目录
```

## 更新日志

### 最新版本（2024-11）
- ✅ 高分辨率视频性能优化（2.7-3倍提速）
- ✅ 视频格式兼容性（支持MP4、MOV、AVI、MKV等）
- ✅ 异常处理增强（输入验证、详细错误信息）
- ✅ 音频提取缓存（重复样本自动命中）
- ✅ 内存优化（峰值从26GB降至2-4GB）

## 许可证

本项目仅供学习和研究使用。
