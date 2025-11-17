# BeatSync Web服务架构设计

**目标平台**：微信小程序 / Web网页  
**生成时间**：2024年11月

---

## 一、当前架构分析

### 1.1 当前架构特点
- ✅ **命令行工具**：直接处理本地文件
- ✅ **同步处理**：单线程顺序执行
- ✅ **本地存储**：输入输出都在本地文件系统
- ✅ **实时日志**：stdout直接输出

### 1.2 Web服务适配挑战
- ⚠️ **长时间处理**：10-100s的处理时间，需要异步任务
- ⚠️ **文件上传**：需要处理用户上传的视频文件
- ⚠️ **资源限制**：服务器内存、CPU、存储限制
- ⚠️ **并发处理**：多个用户同时请求
- ⚠️ **进度反馈**：用户需要实时了解处理进度
- ⚠️ **错误处理**：需要友好的错误提示和日志

---

## 二、Web服务架构设计

### 2.1 整体架构

```
┌─────────────────┐
│  微信小程序/Web  │
│    (前端)       │
└────────┬────────┘
         │ HTTP/WebSocket
         │
┌────────▼─────────────────────────────────┐
│          API Gateway                     │
│  (Nginx/负载均衡)                        │
└────────┬─────────────────────────────────┘
         │
┌────────▼─────────────────────────────────┐
│       Web服务层 (Flask/FastAPI)          │
│  - 文件上传接口                           │
│  - 任务提交接口                           │
│  - 进度查询接口                           │
│  - 结果下载接口                           │
└────────┬─────────────────────────────────┘
         │
┌────────▼─────────────────────────────────┐
│      任务队列 (Celery/Redis)              │
│  - 任务排队                               │
│  - 任务调度                               │
│  - 状态管理                               │
└────────┬─────────────────────────────────┘
         │
┌────────▼─────────────────────────────────┐
│      工作节点 (Worker)                    │
│  - beatsync_fine_cut_modular.py          │
│  - beatsync_badcase_fix_trim_v2.py        │
│  - beatsync_parallel_processor.py         │
│  - 资源监控                               │
└────────┬─────────────────────────────────┘
         │
┌────────▼─────────────────────────────────┐
│      存储层                               │
│  - 对象存储 (OSS/S3) 或本地存储            │
│  - Redis (任务状态)                       │
│  - 数据库 (任务记录)                      │
└──────────────────────────────────────────┘
```

### 2.2 技术栈建议

#### 后端框架
- **FastAPI**（推荐）：异步支持好、自动API文档、性能高
- **Flask**（备选）：简单易用、生态成熟

#### 任务队列
- **Celery + Redis**：成熟稳定、支持分布式
- **RQ (Redis Queue)**：轻量级、简单易用

#### 存储方案
- **对象存储**：阿里云OSS / 腾讯云COS / AWS S3（推荐）
- **本地存储**：仅用于开发测试

#### 数据库
- **PostgreSQL / MySQL**：任务记录、用户信息
- **Redis**：任务状态缓存、进度信息

---

## 三、核心业务逻辑调整

### 3.1 异步任务处理 ⭐ 必须

#### 当前问题
- 同步处理，用户需要等待10-100s
- 无法处理并发请求
- 无法提供进度反馈

#### 解决方案
```python
# tasks.py - Celery任务定义
from celery import Celery
from celery.result import AsyncResult
import os
import tempfile

app = Celery('beatsync', broker='redis://localhost:6379/0')

@app.task(bind=True, max_retries=3)
def process_video_async(self, dance_file_path, bgm_file_path, output_file_path, 
                       use_parallel=True, user_id=None):
    """异步处理视频任务"""
    try:
        # 更新任务状态
        self.update_state(state='PROCESSING', meta={'progress': 0, 'message': '开始处理...'})
        
        # 调用并行处理器（带进度回调）
        if use_parallel:
            result = process_with_progress_callback(
                dance_file_path, 
                bgm_file_path, 
                output_file_path,
                progress_callback=lambda p, msg: self.update_state(
                    state='PROCESSING', 
                    meta={'progress': p, 'message': msg}
                )
            )
        else:
            # 单版本处理
            result = process_single_version(
                dance_file_path,
                bgm_file_path,
                output_file_path,
                progress_callback=lambda p, msg: self.update_state(
                    state='PROCESSING',
                    meta={'progress': p, 'message': msg}
                )
            )
        
        return {
            'status': 'SUCCESS',
            'output_file': output_file_path,
            'result': result
        }
        
    except Exception as e:
        # 重试机制
        if self.request.retries < self.max_retries:
            raise self.retry(exc=e, countdown=60)
        return {
            'status': 'FAILED',
            'error': str(e)
        }
```

### 3.2 进度反馈机制 ⭐ 必须

#### 当前问题
- 无法实时反馈处理进度
- 用户不知道任务是否卡住

#### 解决方案
```python
# 修改核心处理函数，添加进度回调
def fine_cut_modular_mode(dance_video: str, bgm_video: str, output_video: str,
                          progress_callback=None) -> bool:
    """模块解耦精剪模式主函数（带进度回调）"""
    try:
        if progress_callback:
            progress_callback(0, "开始处理...")
        
        # 模块1: 对齐模块
        if progress_callback:
            progress_callback(10, "提取音频...")
        success, dance_alignment = alignment_module(dance_video, bgm_video, result_video)
        if not success:
            return False
        
        if progress_callback:
            progress_callback(50, "对齐完成，开始裁剪...")
        
        # 模块2: 裁剪模块
        if not trim_silent_segments_module(result_video, output_video, dance_video, dance_alignment):
            return False
        
        if progress_callback:
            progress_callback(100, "处理完成!")
        
        return True
    except Exception as e:
        if progress_callback:
            progress_callback(-1, f"处理失败: {e}")
        return False
```

### 3.3 资源限制与监控 ⭐ 必须

#### 当前问题
- 没有资源限制，可能导致服务器过载
- 没有资源监控，无法预警

#### 解决方案
```python
import psutil
import resource

class ResourceLimiter:
    """资源限制器"""
    
    def __init__(self, max_memory_mb=4000, max_cpu_percent=80):
        self.max_memory_mb = max_memory_mb
        self.max_cpu_percent = max_cpu_percent
    
    def check_resources(self) -> Tuple[bool, str]:
        """检查系统资源"""
        # 检查内存
        process = psutil.Process()
        memory_mb = process.memory_info().rss / 1024 / 1024
        if memory_mb > self.max_memory_mb:
            return False, f"内存使用过高: {memory_mb:.1f}MB > {self.max_memory_mb}MB"
        
        # 检查CPU
        cpu_percent = psutil.cpu_percent(interval=1)
        if cpu_percent > self.max_cpu_percent:
            return False, f"CPU使用过高: {cpu_percent:.1f}% > {self.max_cpu_percent}%"
        
        return True, ""
    
    def limit_memory(self, max_memory_mb: int):
        """设置内存限制（Linux）"""
        try:
            max_bytes = max_memory_mb * 1024 * 1024
            resource.setrlimit(resource.RLIMIT_AS, (max_bytes, max_bytes))
        except Exception as e:
            print(f"无法设置内存限制: {e}")

# 在任务开始时检查资源
@app.task(bind=True)
def process_video_async(self, ...):
    limiter = ResourceLimiter()
    ok, msg = limiter.check_resources()
    if not ok:
        return {'status': 'FAILED', 'error': f'资源不足: {msg}'}
    
    # 设置资源限制
    limiter.limit_memory(4000)  # 4GB限制
    
    # 继续处理...
```

### 3.4 文件上传与存储 ⭐ 必须

#### 当前问题
- 需要处理用户上传的文件
- 需要临时存储和清理

#### 解决方案
```python
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
import uuid
import os
import shutil
from datetime import datetime, timedelta

app = FastAPI()

# 配置
UPLOAD_DIR = "/tmp/beatsync_uploads"
OUTPUT_DIR = "/tmp/beatsync_outputs"
CLEANUP_AGE_HOURS = 24  # 24小时后清理

@app.post("/api/upload")
async def upload_video(file: UploadFile = File(...)):
    """上传视频文件"""
    # 验证文件类型
    if not file.filename.endswith(('.mp4', '.MP4', '.mov', '.MOV')):
        raise HTTPException(status_code=400, detail="不支持的文件格式")
    
    # 生成唯一文件名
    file_id = str(uuid.uuid4())
    file_ext = os.path.splitext(file.filename)[1]
    file_path = os.path.join(UPLOAD_DIR, f"{file_id}{file_ext}")
    
    # 保存文件
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    
    # 验证文件大小（限制100MB）
    file_size = os.path.getsize(file_path)
    if file_size > 100 * 1024 * 1024:
        os.remove(file_path)
        raise HTTPException(status_code=400, detail="文件过大（最大100MB）")
    
    return {"file_id": file_id, "file_path": file_path}

@app.post("/api/process")
async def process_video(dance_file_id: str, bgm_file_id: str, use_parallel: bool = True):
    """提交处理任务"""
    # 查找文件
    dance_path = find_file_by_id(dance_file_id)
    bgm_path = find_file_by_id(bgm_file_id)
    
    if not dance_path or not bgm_path:
        raise HTTPException(status_code=404, detail="文件不存在")
    
    # 生成输出路径
    task_id = str(uuid.uuid4())
    output_path = os.path.join(OUTPUT_DIR, f"{task_id}.mp4")
    
    # 提交异步任务
    task = process_video_async.delay(
        dance_path, bgm_path, output_path, use_parallel
    )
    
    return {"task_id": task.id, "status": "PENDING"}

@app.get("/api/task/{task_id}")
async def get_task_status(task_id: str):
    """查询任务状态"""
    task = AsyncResult(task_id, app=app)
    
    if task.state == 'PENDING':
        return {"status": "PENDING", "progress": 0}
    elif task.state == 'PROCESSING':
        return {
            "status": "PROCESSING",
            "progress": task.info.get('progress', 0),
            "message": task.info.get('message', '')
        }
    elif task.state == 'SUCCESS':
        return {
            "status": "SUCCESS",
            "progress": 100,
            "output_file": task.result.get('output_file')
        }
    else:
        return {
            "status": "FAILED",
            "error": task.result.get('error', '未知错误')
        }

@app.get("/api/download/{task_id}")
async def download_result(task_id: str):
    """下载处理结果"""
    task = AsyncResult(task_id, app=app)
    if task.state != 'SUCCESS':
        raise HTTPException(status_code=404, detail="任务未完成")
    
    output_file = task.result.get('output_file')
    if not os.path.exists(output_file):
        raise HTTPException(status_code=404, detail="文件不存在")
    
    return FileResponse(
        output_file,
        media_type='video/mp4',
        filename=f"beatsync_{task_id}.mp4"
    )

# 定期清理临时文件
@app.on_event("startup")
async def startup_event():
    schedule_cleanup()

def schedule_cleanup():
    """定期清理旧文件"""
    import schedule
    import time
    
    def cleanup():
        now = datetime.now()
        for directory in [UPLOAD_DIR, OUTPUT_DIR]:
            if not os.path.exists(directory):
                continue
            for filename in os.listdir(directory):
                filepath = os.path.join(directory, filename)
                file_time = datetime.fromtimestamp(os.path.getmtime(filepath))
                if now - file_time > timedelta(hours=CLEANUP_AGE_HOURS):
                    try:
                        os.remove(filepath)
                    except:
                        pass
    
    schedule.every().hour.do(cleanup)
    
    # 在后台线程运行
    import threading
    def run_schedule():
        while True:
            schedule.run_pending()
            time.sleep(60)
    threading.Thread(target=run_schedule, daemon=True).start()
```

### 3.5 并发控制 ⭐ 必须

#### 当前问题
- 没有并发限制，可能导致服务器过载

#### 解决方案
```python
# Celery配置
app.conf.update(
    # 每个worker最多同时处理1个任务（避免内存溢出）
    worker_prefetch_multiplier=1,
    # 任务超时时间（5分钟）
    task_time_limit=300,
    # 任务软超时（4分钟，优雅退出）
    task_soft_time_limit=240,
    # 最大并发worker数
    worker_max_tasks_per_child=10,  # 处理10个任务后重启worker（防止内存泄漏）
)

# 或者使用信号量限制并发
from celery import group
from celery.signals import task_prerun

# 全局信号量
processing_semaphore = threading.Semaphore(2)  # 最多2个任务同时处理

@task_prerun.connect
def task_prerun_handler(sender=None, task_id=None, **kwargs):
    """任务开始前获取信号量"""
    processing_semaphore.acquire()

@task_postrun.connect
def task_postrun_handler(sender=None, task_id=None, **kwargs):
    """任务结束后释放信号量"""
    processing_semaphore.release()
```

### 3.6 错误处理与用户反馈 ⭐ 必须

#### 当前问题
- 错误信息不够友好
- 没有统一的错误码

#### 解决方案
```python
# 错误码定义
class ErrorCode:
    FILE_NOT_FOUND = "FILE_NOT_FOUND"
    FILE_TOO_LARGE = "FILE_TOO_LARGE"
    INVALID_FORMAT = "INVALID_FORMAT"
    PROCESSING_FAILED = "PROCESSING_FAILED"
    RESOURCE_LIMIT = "RESOURCE_LIMIT"
    TIMEOUT = "TIMEOUT"

# 错误消息映射（中文）
ERROR_MESSAGES = {
    ErrorCode.FILE_NOT_FOUND: "文件不存在或已过期",
    ErrorCode.FILE_TOO_LARGE: "文件过大，请上传小于100MB的文件",
    ErrorCode.INVALID_FORMAT: "不支持的文件格式，请上传MP4或MOV格式",
    ErrorCode.PROCESSING_FAILED: "视频处理失败，请检查视频文件是否损坏",
    ErrorCode.RESOURCE_LIMIT: "服务器繁忙，请稍后重试",
    ErrorCode.TIMEOUT: "处理超时，请尝试上传较小的视频文件",
}

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """全局异常处理"""
    if isinstance(exc, HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error_code": "HTTP_ERROR",
                "message": exc.detail,
                "detail": str(exc)
            }
        )
    
    # 记录详细错误日志
    logger.error(f"未处理的异常: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "error_code": ErrorCode.PROCESSING_FAILED,
            "message": ERROR_MESSAGES[ErrorCode.PROCESSING_FAILED],
            "detail": "服务器内部错误"
        }
    )
```

---

## 四、性能优化建议

### 4.1 针对Web服务的优化

#### 1. 文件大小限制 ⭐ 必须
```python
# 限制上传文件大小
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB

# 在FastAPI中配置
app = FastAPI()
app.add_middleware(
    LimitUploadSize,
    max_upload_size=MAX_FILE_SIZE
)
```

#### 2. 视频预处理（可选）
```python
# 对于超大文件，先压缩再处理
def preprocess_video(input_path: str, output_path: str, max_resolution: str = "1080p"):
    """预处理视频：压缩分辨率"""
    cmd = [
        'ffmpeg', '-y', '-i', input_path,
        '-vf', f'scale={max_resolution}:-1',
        '-c:v', 'libx264', '-preset', 'fast', '-crf', '23',
        '-c:a', 'copy',
        output_path
    ]
    subprocess.run(cmd, check=True)
```

#### 3. 缓存优化
```python
# 使用Redis缓存处理结果（相同输入文件）
import hashlib
import redis

redis_client = redis.Redis(host='localhost', port=6379, db=1)

def get_cache_key(dance_path: str, bgm_path: str) -> str:
    """生成缓存键"""
    # 使用文件内容hash
    dance_hash = hashlib.md5(open(dance_path, 'rb').read()).hexdigest()
    bgm_hash = hashlib.md5(open(bgm_path, 'rb').read()).hexdigest()
    return f"beatsync:{dance_hash}:{bgm_hash}"

def check_cache(dance_path: str, bgm_path: str) -> Optional[str]:
    """检查缓存"""
    cache_key = get_cache_key(dance_path, bgm_path)
    cached_result = redis_client.get(cache_key)
    if cached_result:
        return cached_result.decode()
    return None

def save_cache(dance_path: str, bgm_path: str, output_path: str):
    """保存缓存"""
    cache_key = get_cache_key(dance_path, bgm_path)
    redis_client.setex(cache_key, 3600 * 24, output_path)  # 24小时过期
```

### 4.2 鲁棒性增强

#### 1. 任务重试机制
```python
@app.task(bind=True, max_retries=3, default_retry_delay=60)
def process_video_async(self, ...):
    try:
        # 处理逻辑
        pass
    except MemoryError as e:
        # 内存错误，不重试
        return {'status': 'FAILED', 'error': '内存不足'}
    except subprocess.TimeoutExpired as e:
        # 超时，重试
        raise self.retry(exc=e, countdown=120)
    except Exception as e:
        # 其他错误，重试
        if self.request.retries < self.max_retries:
            raise self.retry(exc=e, countdown=60)
        return {'status': 'FAILED', 'error': str(e)}
```

#### 2. 健康检查
```python
@app.get("/api/health")
async def health_check():
    """健康检查"""
    # 检查Redis连接
    try:
        redis_client.ping()
        redis_ok = True
    except:
        redis_ok = False
    
    # 检查磁盘空间
    disk_usage = shutil.disk_usage(UPLOAD_DIR)
    disk_free_gb = disk_usage.free / (1024**3)
    disk_ok = disk_free_gb > 1  # 至少1GB空间
    
    # 检查内存
    memory = psutil.virtual_memory()
    memory_ok = memory.percent < 90
    
    status = "healthy" if (redis_ok and disk_ok and memory_ok) else "unhealthy"
    
    return {
        "status": status,
        "redis": "ok" if redis_ok else "error",
        "disk_free_gb": round(disk_free_gb, 2),
        "memory_percent": memory.percent
    }
```

---

## 五、部署建议

### 5.1 服务器配置
- **CPU**：4核以上（推荐8核）
- **内存**：8GB以上（推荐16GB）
- **存储**：SSD，至少100GB可用空间
- **网络**：带宽足够（上传下载）

### 5.2 容器化部署（推荐）
```dockerfile
# Dockerfile
FROM python:3.9-slim

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

# 安装Python依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制代码
COPY . /app
WORKDIR /app

# 启动命令
CMD ["celery", "worker", "-A", "tasks", "--loglevel=info"]
```

### 5.3 监控与日志
- **日志**：使用ELK或类似方案集中管理
- **监控**：Prometheus + Grafana
- **告警**：资源使用超过阈值时告警

---

## 六、实施优先级

### 必须完成（上线前）
1. ✅ **异步任务处理**：Celery + Redis
2. ✅ **进度反馈机制**：WebSocket或轮询
3. ✅ **文件上传接口**：FastAPI文件上传
4. ✅ **资源限制**：内存、CPU限制
5. ✅ **错误处理**：统一错误码和消息

### 建议完成（上线后1-2周）
6. ⚠️ **缓存机制**：Redis缓存处理结果
7. ⚠️ **健康检查**：服务健康监控
8. ⚠️ **日志系统**：集中日志管理

### 可选完成（后续优化）
9. ⚠️ **视频预处理**：自动压缩超大文件
10. ⚠️ **容器化部署**：Docker部署
11. ⚠️ **监控告警**：Prometheus监控

---

## 七、总结

### 7.1 核心调整
- **架构**：从命令行工具转为异步Web服务
- **处理**：从同步转为异步任务队列
- **存储**：从本地文件转为对象存储
- **反馈**：从stdout转为API/WebSocket

### 7.2 关键点
1. **异步处理**：必须使用任务队列（Celery）
2. **进度反馈**：必须提供实时进度（WebSocket/轮询）
3. **资源限制**：必须限制内存和CPU使用
4. **错误处理**：必须提供友好的错误提示
5. **文件管理**：必须自动清理临时文件

### 7.3 实施时间
- **架构调整**：2-3周
- **测试验证**：1-2周
- **上线准备**：1周

---

**下一步**：根据此架构设计，开始实施核心API和任务队列集成。

