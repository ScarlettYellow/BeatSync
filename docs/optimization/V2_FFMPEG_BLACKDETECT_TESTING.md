# V2 FFmpeg blackdetect优化 - 测试指南

> **目的**：测试FFmpeg blackdetect优化的正确性和性能

---

## 测试准备

### 1. 确认当前实现

**检查开关状态**：
```bash
grep "USE_FFMPEG_BLACKDETECT" beatsync_badcase_fix_trim_v2.py
```

**应该显示**：
```python
USE_FFMPEG_BLACKDETECT = True  # 使用FFmpeg实现
```

---

### 2. 准备测试视频

**推荐测试视频**：
1. **有末尾黑屏的视频**：用于测试Trailing位置检测
2. **有开头黑屏的视频**：用于测试Leading位置检测
3. **无黑屏的视频**：用于测试边界情况
4. **不同时长的视频**：1分钟、3分钟、5分钟

**如果没有测试视频，可以使用现有样本**：
```bash
# 查看现有测试样本
ls -lh test_data/input_allcases/
```

---

## 测试方法

### 方法1：使用本地V2程序直接测试（推荐）

**步骤**：

1. **测试Trailing位置检测**：
```bash
cd /Users/scarlett/Projects/BeatSync

# 使用waitonme样本测试
python3 beatsync_badcase_fix_trim_v2.py \
    test_data/input_allcases/waitonme/dance.mp4 \
    test_data/input_allcases/waitonme/bgm.mp4 \
    test_output_v2_ffmpeg.mp4
```

2. **观察日志输出**：
   - 查找"检测trailing有声无画面段落（使用FFmpeg blackdetect）"字样
   - 记录检测耗时
   - 记录检测结果（时长）

3. **对比原实现**：
```bash
# 临时切换回OpenCV实现
# 编辑 beatsync_badcase_fix_trim_v2.py，设置 USE_FFMPEG_BLACKDETECT = False

python3 beatsync_badcase_fix_trim_v2.py \
    test_data/input_allcases/waitonme/dance.mp4 \
    test_data/input_allcases/waitonme/bgm.mp4 \
    test_output_v2_opencv.mp4
```

4. **对比结果**：
   - 对比检测耗时
   - 对比检测结果（时长）
   - 对比最终输出视频

---

### 方法2：使用网页服务测试

**步骤**：

1. **启动本地服务**：
```bash
cd /Users/scarlett/Projects/BeatSync/web_service
bash start_local.sh
```

2. **访问前端页面**：
   - 打开浏览器访问：`http://localhost:8080`
   - 上传测试视频

3. **观察后端日志**：
```bash
# 查看后端日志
tail -f web_service/backend/logs/beatsync.log
# 或者查看终端输出
```

4. **查找关键日志**：
   - "检测trailing有声无画面段落（使用FFmpeg blackdetect）"
   - "检测到末尾有声无画面段落: XX.XXXs"
   - 记录处理时间

---

### 方法3：单独测试黑屏检测函数

**创建测试脚本**：

```python
#!/usr/bin/env python3
"""测试FFmpeg blackdetect优化"""

import sys
import time
sys.path.insert(0, '/Users/scarlett/Projects/BeatSync')

from beatsync_badcase_fix_trim_v2 import (
    detect_black_frames_with_audio,
    detect_black_frames_with_audio_opencv,
    detect_black_frames_with_audio_ffmpeg,
    USE_FFMPEG_BLACKDETECT
)

def test_black_detection(video_path, position="trailing"):
    """测试黑屏检测"""
    print(f"\n{'='*60}")
    print(f"测试视频: {video_path}")
    print(f"检测位置: {position}")
    print(f"当前实现: {'FFmpeg blackdetect' if USE_FFMPEG_BLACKDETECT else 'OpenCV'}")
    print(f"{'='*60}\n")
    
    # 测试当前实现
    start_time = time.time()
    result = detect_black_frames_with_audio(video_path, position)
    elapsed_time = time.time() - start_time
    
    print(f"\n结果: {result:.3f}秒")
    print(f"耗时: {elapsed_time:.3f}秒")
    
    # 对比OpenCV实现
    print(f"\n{'='*60}")
    print("对比OpenCV实现:")
    print(f"{'='*60}\n")
    
    start_time = time.time()
    result_opencv = detect_black_frames_with_audio_opencv(video_path, position)
    elapsed_time_opencv = time.time() - start_time
    
    print(f"\n结果: {result_opencv:.3f}秒")
    print(f"耗时: {elapsed_time_opencv:.3f}秒")
    
    # 对比
    print(f"\n{'='*60}")
    print("对比结果:")
    print(f"{'='*60}")
    print(f"结果差异: {abs(result - result_opencv):.3f}秒")
    print(f"耗时差异: {elapsed_time_opencv - elapsed_time:.3f}秒")
    if elapsed_time_opencv > 0:
        speedup = elapsed_time_opencv / elapsed_time
        print(f"提速: {speedup:.2f}倍")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    # 测试Trailing位置
    test_black_detection(
        "test_data/input_allcases/waitonme/dance.mp4",
        position="trailing"
    )
    
    # 测试Leading位置
    test_black_detection(
        "test_data/input_allcases/waitonme/dance.mp4",
        position="leading"
    )
```

**运行测试脚本**：
```bash
cd /Users/scarlett/Projects/BeatSync
python3 test_black_detection.py
```

---

## 测试检查点

### 1. 正确性测试

**检查项**：
- [ ] FFmpeg和OpenCV实现的检测结果是否一致（允许小误差）
- [ ] 检测结果是否合理（例如，末尾黑屏时长不应该超过视频总时长）
- [ ] 边界情况是否正确处理（无黑屏、全部黑屏等）

**预期结果**：
- 检测结果应该基本一致（允许0.1-0.5秒误差）
- 如果差异较大，需要检查FFmpeg输出解析是否正确

---

### 2. 性能测试

**检查项**：
- [ ] Trailing位置检测耗时是否显著减少
- [ ] Leading位置检测耗时（可能更慢，需要观察）
- [ ] 总体V2处理速度是否提升

**预期结果**：
- Trailing位置：快6-15倍（从30秒降到2-5秒）
- Leading位置：可能更慢（需要优化）
- 总体V2处理速度：快8-16%

---

### 3. 日志检查

**关键日志信息**：

**FFmpeg实现**：
```
检测trailing有声无画面段落（使用FFmpeg blackdetect）...
视频总时长: 180.000s
最后一个黑屏段落开始时间: 175.500s
检测到末尾有声无画面段落: 4.500s
```

**OpenCV实现**：
```
检测trailing有声无画面段落...
视频总时长: 180.000s
最后可读帧时间: 175.500s
检测到末尾有声无画面段落: 4.500s
```

**自动回退**（如果FFmpeg失败）：
```
检测trailing有声无画面段落（使用FFmpeg blackdetect）...
检测trailing有声无画面失败（FFmpeg blackdetect）: ...
  回退到OpenCV方法...
检测trailing有声无画面段落...
```

---

## 测试用例

### 用例1：正常末尾黑屏

**测试视频**：有末尾黑屏的视频（例如waitonme样本）

**预期结果**：
- FFmpeg和OpenCV检测结果一致
- FFmpeg耗时显著减少

---

### 用例2：正常开头黑屏

**测试视频**：有开头黑屏的视频

**预期结果**：
- FFmpeg和OpenCV检测结果一致
- FFmpeg耗时可能更慢（需要观察）

---

### 用例3：无黑屏

**测试视频**：无黑屏的视频

**预期结果**：
- 两种实现都返回0秒
- FFmpeg耗时可能更慢（需要处理整个视频）

---

### 用例4：全部黑屏

**测试视频**：全部是黑屏的视频（极端情况）

**预期结果**：
- 两种实现都能正确检测
- 检测结果应该等于视频总时长

---

## 性能对比表格

**记录测试结果**：

| 测试视频 | 位置 | OpenCV耗时 | FFmpeg耗时 | 提速 | 结果差异 |
|---------|------|-----------|-----------|------|---------|
| waitonme | trailing | 31.5s | 3.2s | 9.8x | 0.1s |
| waitonme | leading | 0.7s | 4.5s | 0.16x | 0.0s |
| ... | ... | ... | ... | ... | ... |

---

## 问题排查

### 问题1：FFmpeg检测结果与OpenCV不一致

**可能原因**：
- FFmpeg `blackdetect`的阈值设置不同
- 解析FFmpeg输出有误

**解决方法**：
- 检查`pic_th`计算是否正确
- 检查FFmpeg输出解析逻辑
- 对比FFmpeg和OpenCV的阈值设置

---

### 问题2：FFmpeg方法失败

**可能原因**：
- FFmpeg未安装或版本过低
- 视频格式不支持
- 命令参数错误

**解决方法**：
- 检查FFmpeg版本：`ffmpeg -version`
- 查看错误日志
- 代码会自动回退到OpenCV方法

---

### 问题3：性能提升不明显

**可能原因**：
- 视频时长较短（FFmpeg需要处理整个视频）
- 黑屏段落较短（OpenCV只需要读取少量帧）

**解决方法**：
- 测试更长的视频（3-5分钟）
- 测试末尾黑屏较长的视频

---

## 快速验证命令

**一键测试脚本**：

```bash
#!/bin/bash
# test_ffmpeg_blackdetect.sh

cd /Users/scarlett/Projects/BeatSync

echo "=========================================="
echo "测试FFmpeg blackdetect优化"
echo "=========================================="
echo ""

# 检查开关状态
echo "1. 检查开关状态:"
grep "USE_FFMPEG_BLACKDETECT" beatsync_badcase_fix_trim_v2.py
echo ""

# 测试Trailing位置
echo "2. 测试Trailing位置检测:"
time python3 -c "
import sys
sys.path.insert(0, '.')
from beatsync_badcase_fix_trim_v2 import detect_black_frames_with_audio
result = detect_black_frames_with_audio('test_data/input_allcases/waitonme/dance.mp4', 'trailing')
print(f'检测结果: {result:.3f}秒')
"

echo ""
echo "=========================================="
echo "测试完成"
echo "=========================================="
```

**运行**：
```bash
chmod +x test_ffmpeg_blackdetect.sh
./test_ffmpeg_blackdetect.sh
```

---

## 下一步

### 如果测试通过

1. **部署到线上服务器**：
   ```bash
   # 在服务器上拉取最新代码
   cd /opt/beatsync
   sudo git pull origin main
   sudo systemctl restart beatsync
   ```

2. **监控性能**：
   - 观察处理时间是否减少
   - 观察是否有错误日志

---

### 如果测试失败

1. **快速回退**：
   ```python
   # 修改 beatsync_badcase_fix_trim_v2.py
   USE_FFMPEG_BLACKDETECT = False
   ```

2. **分析问题**：
   - 查看错误日志
   - 对比检测结果
   - 检查FFmpeg输出

---

**最后更新**：2025-12-05

