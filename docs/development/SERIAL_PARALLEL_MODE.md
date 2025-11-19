# 串行/并行模式切换说明

## 概述

`beatsync_parallel_processor.py` 现在支持两种处理模式：
- **串行模式**（默认）：适合资源受限环境（如Render免费层）
- **并行模式**（可选）：适合资源充足环境（需要升级服务器后使用）

## 模式对比

### 串行模式（默认）

**特点**：
- 先运行V2版本，完成后运行modular版本
- 每个版本独占所有系统资源
- 避免资源竞争，处理速度更快

**适用场景**：
- Render免费层（1个CPU核心，512MB内存）
- 资源受限的服务器
- 需要稳定性的生产环境

**性能**：
- 总耗时：约10-12分钟（串行）
- 比并行模式快约50%（在资源受限环境下）

### 并行模式（可选）

**特点**：
- 同时运行两个版本
- 需要多核CPU和充足内存
- 理论上总耗时 = max(版本1, 版本2)

**适用场景**：
- 多核CPU服务器（2+核心）
- 充足内存（2GB+）
- 资源充足的环境

**性能**：
- 总耗时：约10分钟（并行，资源充足时）
- 在资源受限环境下可能更慢（资源竞争）

## 使用方法

### 命令行

```bash
# 串行模式（默认）
python3 beatsync_parallel_processor.py \
  --dance dance.mp4 \
  --bgm bgm.mp4 \
  --output-dir outputs \
  --sample-name test

# 并行模式（需要升级服务器后使用）
python3 beatsync_parallel_processor.py \
  --dance dance.mp4 \
  --bgm bgm.mp4 \
  --output-dir outputs \
  --sample-name test \
  --parallel
```

### Web服务

当前Web服务使用串行模式（默认），适合Render免费层。

如需切换到并行模式，需要：
1. 升级Render计划（Standard或Pro）
2. 修改 `web_service/backend/main.py` 中调用 `process_beat_sync_parallel` 的地方，添加 `parallel=True` 参数

## 代码实现

### 函数签名

```python
def process_beat_sync_parallel(
    dance_video: str, 
    bgm_video: str, 
    output_dir: str, 
    sample_name: str, 
    parallel: bool = False  # 默认False（串行模式）
) -> bool:
```

### 模式切换逻辑

```python
if parallel:
    # 并行处理模式
    t1 = threading.Thread(target=modular_thread, daemon=False)
    t2 = threading.Thread(target=v2_thread, daemon=False)
    t1.start()
    t2.start()
    t1.join()
    t2.join()
else:
    # 串行处理模式
    v2_thread()
    modular_thread()
```

## 前端交互

### 串行模式下的前端

- **单个下载按钮**：点击后下载两个版本的结果
- **处理状态**：显示整体处理进度
- **下载行为**：自动下载两个版本（如果都成功）

### 并行模式下的前端（未来）

- 可以保留两个独立下载按钮
- 显示每个版本的独立状态
- 支持部分成功下载

## 升级建议

### 何时切换到并行模式？

1. **服务器资源充足**：
   - 2+ CPU核心
   - 2GB+ 内存
   - 充足的磁盘I/O

2. **性能测试**：
   - 在升级后的服务器上测试并行模式
   - 对比串行和并行的实际耗时
   - 确认并行模式确实更快

3. **稳定性验证**：
   - 确保并行模式不会导致资源竞争
   - 验证处理成功率
   - 监控系统资源使用

## 当前配置

- **默认模式**：串行模式（`parallel=False`）
- **Web服务**：使用串行模式
- **命令行**：可通过 `--parallel` 参数启用并行模式

