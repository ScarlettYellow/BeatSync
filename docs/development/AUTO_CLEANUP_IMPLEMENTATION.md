# 自动清理机制实现说明

## 概述

实现了两个自动清理机制，用于管理Web服务的临时文件和输出文件：

1. **web_uploads自动清理**：处理完成后立即删除上传文件
2. **web_outputs自动清理**：仅保留最近3天的输出文件

## 实现细节

### 1. web_uploads自动清理

**触发时机**：
- 视频处理完成后（无论成功或失败）
- 在`process_video_background`函数中，处理完成时自动清理

**清理逻辑**：
```python
# 处理完成后，清理上传的文件
try:
    if dance_path.exists():
        dance_path.unlink()
        print(f"INFO: 已清理上传文件: {dance_path}")
    if bgm_path.exists():
        bgm_path.unlink()
        print(f"INFO: 已清理上传文件: {bgm_path}")
except Exception as cleanup_error:
    print(f"WARNING: 清理上传文件失败: {cleanup_error}")
```

**清理位置**：
- 处理成功时（3处）
- 处理失败时（1处）
- 异常处理时（1处）

### 2. web_outputs自动清理

**触发时机**：
- 应用启动时（`startup_event`）
- 启动时直接调用（`cleanup_old_web_outputs()`）

**清理逻辑**：
```python
def cleanup_old_web_outputs():
    """清理超过3天的Web输出文件"""
    cutoff_time = datetime.now() - timedelta(days=WEB_OUTPUTS_RETENTION_DAYS)
    # 遍历web_outputs目录，删除超过3天的任务目录
```

**配置**：
- `WEB_OUTPUTS_RETENTION_DAYS = 3` - 保留3天

### 3. 启动时清理

**启动清理流程**：
1. 加载任务状态（`load_task_status()`）
2. 清理旧任务状态（`cleanup_old_tasks()`）
3. 清理旧的Web输出（`cleanup_old_web_outputs()`）
4. 启动事件中清理旧文件（`cleanup_old_files()` + `cleanup_old_web_outputs()`）

## 配置参数

```python
CLEANUP_AGE_HOURS = 24  # 24小时后清理临时文件
WEB_OUTPUTS_RETENTION_DAYS = 3  # Web输出保留3天
```

## 清理效果

### web_uploads
- ✅ 处理完成后立即删除
- ✅ 避免占用磁盘空间
- ✅ 用户上传的文件不会长期保留

### web_outputs
- ✅ 仅保留最近3天的输出
- ✅ 自动清理旧任务输出
- ✅ 节省磁盘空间

## 日志输出

清理操作会输出日志：
- `INFO: 已清理上传文件: {file_path}`
- `INFO: 已清理旧的Web输出: {task_dir}`
- `✅ 已清理 {count} 个超过3天的Web输出目录`

## 注意事项

1. **清理失败不影响主流程**：所有清理操作都在try-except中，失败不会影响视频处理
2. **保留时间可配置**：通过`WEB_OUTPUTS_RETENTION_DAYS`可以调整保留时间
3. **启动时清理**：每次应用启动都会自动清理，确保磁盘空间

