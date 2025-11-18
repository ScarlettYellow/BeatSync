# 异步处理解决方案

## 问题描述

当前同步处理方式的问题：
- Render免费层HTTP请求有30秒超时限制
- 视频处理需要几分钟甚至更长时间
- 请求在30秒后被Render强制关闭
- 导致处理失败

## 解决方案：改为异步处理

### 架构设计

1. **提交任务**（立即返回）
   - 前端调用 `/api/process` 提交任务
   - 后端立即返回 `task_id` 和状态 `pending`
   - 不等待处理完成

2. **后台处理**
   - 后端在后台启动处理任务
   - 使用线程或进程处理视频
   - 更新任务状态（processing → success/failed）

3. **状态轮询**
   - 前端定期调用 `/api/status/{task_id}` 查询状态
   - 直到状态变为 `success` 或 `failed`
   - 显示处理进度

### API设计

#### 1. 提交处理任务

```
POST /api/process
Request:
  - dance_file_id: string
  - bgm_file_id: string

Response:
{
  "task_id": "uuid",
  "status": "pending",
  "message": "任务已提交，正在处理..."
}
```

#### 2. 查询处理状态

```
GET /api/status/{task_id}

Response (处理中):
{
  "task_id": "uuid",
  "status": "processing",
  "message": "正在处理，请稍候...",
  "progress": 50  // 可选：处理进度百分比
}

Response (成功):
{
  "task_id": "uuid",
  "status": "success",
  "message": "处理完成",
  "modular_output": "path/to/modular.mp4",
  "v2_output": "path/to/v2.mp4"
}

Response (失败):
{
  "task_id": "uuid",
  "status": "failed",
  "message": "处理失败",
  "error": "错误详情"
}
```

### 实现方式

#### 方案1：使用线程（简单，适合Render免费层）

**优点**：
- 实现简单
- 不需要额外服务
- 适合Render免费层

**缺点**：
- 服务重启会丢失任务
- 无法跨实例共享状态

**实现**：
```python
import threading
from queue import Queue

# 任务队列
task_queue = Queue()
task_status = {}  # {task_id: status}

def process_video_async(task_id, dance_path, bgm_path, output_dir):
    """后台处理函数"""
    try:
        task_status[task_id] = {"status": "processing"}
        # 调用并行处理器
        success = process_beat_sync_parallel(...)
        if success:
            task_status[task_id] = {"status": "success", ...}
        else:
            task_status[task_id] = {"status": "failed", ...}
    except Exception as e:
        task_status[task_id] = {"status": "failed", "error": str(e)}

@app.post("/api/process")
async def process_video(...):
    task_id = str(uuid.uuid4())
    # 启动后台线程
    thread = threading.Thread(
        target=process_video_async,
        args=(task_id, dance_path, bgm_path, output_dir)
    )
    thread.start()
    return {"task_id": task_id, "status": "pending"}
```

#### 方案2：使用Celery + Redis（推荐，但需要付费服务）

**优点**：
- 任务持久化
- 支持任务重试
- 可以跨实例共享
- 更好的可扩展性

**缺点**：
- 需要Redis服务（需要付费）
- 实现较复杂

#### 方案3：使用Render Background Workers（推荐，如果升级计划）

**优点**：
- Render原生支持
- 任务持久化
- 自动重试

**缺点**：
- 需要付费计划

### 前端实现

```javascript
// 提交任务
async function processVideo() {
    // 提交任务
    const response = await fetch(`${API_BASE_URL}/api/process`, {
        method: 'POST',
        body: formData
    });
    const result = await response.json();
    const taskId = result.task_id;
    
    // 开始轮询
    pollStatus(taskId);
}

// 轮询状态
async function pollStatus(taskId) {
    const maxAttempts = 60; // 最多轮询60次（5分钟）
    let attempts = 0;
    
    const interval = setInterval(async () => {
        attempts++;
        
        try {
            const response = await fetch(`${API_BASE_URL}/api/status/${taskId}`);
            const result = await response.json();
            
            if (result.status === 'success') {
                clearInterval(interval);
                // 处理成功
                updateStatus('处理完成！', 'success');
                // 显示下载按钮
            } else if (result.status === 'failed') {
                clearInterval(interval);
                // 处理失败
                updateStatus(`处理失败: ${result.error}`, 'error');
            } else if (result.status === 'processing') {
                // 继续处理中
                updateStatus(`正在处理... (${attempts * 5}秒)`, 'processing');
            }
        } catch (error) {
            console.error('Poll error:', error);
        }
        
        // 超时检查
        if (attempts >= maxAttempts) {
            clearInterval(interval);
            updateStatus('处理超时，请稍后重试', 'error');
        }
    }, 5000); // 每5秒轮询一次
}
```

## 实施建议

### 阶段1：快速修复（使用线程）

1. 修改后端API，改为异步处理
2. 使用线程在后台处理
3. 添加状态查询接口
4. 前端改为轮询方式

**优点**：快速实现，不需要额外服务

**缺点**：服务重启会丢失任务

### 阶段2：长期方案（升级计划）

1. 升级Render到付费计划
2. 使用Render Background Workers
3. 或使用Celery + Redis

**优点**：任务持久化，更好的可靠性

## 临时解决方案

在实现异步处理之前，可以：

1. **使用较小的测试视频**
   - 几MB的小视频
   - 几秒钟的时长
   - 可以在30秒内完成处理

2. **本地处理**
   - 在本地运行后端服务
   - 不受超时限制

3. **升级Render计划**
   - 付费计划支持更长的超时时间

## 需要帮助？

如果需要实现异步处理，我可以：
1. 修改后端API支持异步处理
2. 添加状态查询接口
3. 修改前端改为轮询方式

请告诉我是否要开始实施异步处理方案。

