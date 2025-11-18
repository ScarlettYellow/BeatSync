#!/usr/bin/env python3
"""
BeatSync Web服务后端API
使用FastAPI实现同步处理接口
"""

import os
import sys
import uuid
import tempfile
import shutil
import threading
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict

from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

app = FastAPI(title="BeatSync API", version="1.0.0")

# 配置CORS（允许前端跨域访问）
# 从环境变量获取允许的域名，默认允许所有（开发环境）
allowed_origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")
if allowed_origins == ["*"]:
    # 开发环境：允许所有来源
    allow_origins_list = ["*"]
else:
    # 生产环境：限制具体域名
    allow_origins_list = [origin.strip() for origin in allowed_origins]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 配置
UPLOAD_DIR = project_root / "outputs" / "web_uploads"
OUTPUT_DIR = project_root / "outputs" / "web_outputs"
CLEANUP_AGE_HOURS = 24  # 24小时后清理临时文件

# 确保目录存在
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# 任务状态管理（用于异步处理）
TASK_STATUS_FILE = project_root / "outputs" / "task_status.json"
task_status: Dict[str, dict] = {}
task_lock = threading.Lock()


def save_task_status():
    """保存任务状态到文件"""
    try:
        with task_lock:
            # 创建临时文件，然后原子性替换
            temp_file = TASK_STATUS_FILE.with_suffix('.tmp')
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(task_status, f, ensure_ascii=False, indent=2)
            # 原子性替换
            temp_file.replace(TASK_STATUS_FILE)
    except Exception as e:
        print(f"WARNING: 保存任务状态失败: {e}")


def load_task_status():
    """从文件加载任务状态"""
    try:
        if TASK_STATUS_FILE.exists():
            with open(TASK_STATUS_FILE, 'r', encoding='utf-8') as f:
                loaded_status = json.load(f)
                with task_lock:
                    task_status.update(loaded_status)
                print(f"✅ 已加载 {len(loaded_status)} 个任务状态")
    except Exception as e:
        print(f"WARNING: 加载任务状态失败: {e}")


def cleanup_old_tasks():
    """清理24小时前的已完成任务状态"""
    try:
        cutoff_time = datetime.now() - timedelta(hours=24)
        with task_lock:
            to_remove = []
            for task_id, status in task_status.items():
                if status.get("status") in ["success", "failed"]:
                    completed_at_str = status.get("completed_at")
                    if completed_at_str:
                        try:
                            completed_at = datetime.fromisoformat(completed_at_str)
                            if completed_at < cutoff_time:
                                to_remove.append(task_id)
                        except (ValueError, TypeError):
                            # 如果时间格式错误，也清理掉
                            to_remove.append(task_id)
            
            for task_id in to_remove:
                del task_status[task_id]
            
            if to_remove:
                print(f"🧹 清理了 {len(to_remove)} 个旧任务状态")
                save_task_status()
    except Exception as e:
        print(f"WARNING: 清理任务状态失败: {e}")


# 启动时加载任务状态
load_task_status()

# 启动时清理旧任务
cleanup_old_tasks()


@app.get("/")
async def root():
    """根路径，返回API信息"""
    return {
        "name": "BeatSync API",
        "version": "1.0.0",
        "status": "running"
    }


@app.post("/api/upload")
async def upload_video(
    file: UploadFile = File(...),
    file_type: str = Form(...)  # "dance" 或 "bgm"
):
    """
    上传视频文件
    
    参数:
        file: 视频文件
        file_type: 文件类型 ("dance" 或 "bgm")
    
    返回:
        file_id: 文件ID（用于后续处理）
        filename: 文件名
        size: 文件大小（字节）
    """
    # 验证文件类型
    allowed_extensions = ['.mp4', '.MP4', '.mov', '.MOV', '.avi', '.AVI', '.mkv', '.MKV']
    file_ext = Path(file.filename).suffix
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的文件格式，支持格式: {', '.join(allowed_extensions)}"
        )
    
    # 验证file_type
    if file_type not in ['dance', 'bgm']:
        raise HTTPException(
            status_code=400,
            detail="file_type必须是'dance'或'bgm'"
        )
    
    # 生成唯一文件名
    file_id = str(uuid.uuid4())
    file_path = UPLOAD_DIR / f"{file_id}_{file_type}{file_ext}"
    
    # 保存文件
    try:
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        
        file_size = os.path.getsize(file_path)
        
        return {
            "file_id": file_id,
            "file_type": file_type,
            "filename": file.filename,
            "size": file_size,
            "message": "文件上传成功"
        }
    except Exception as e:
        if file_path.exists():
            os.remove(file_path)
        raise HTTPException(
            status_code=500,
            detail=f"文件上传失败: {str(e)}"
        )


def process_video_background(task_id: str, dance_path: Path, bgm_path: Path, output_dir: Path):
    """后台处理视频的函数"""
    try:
        import traceback
        
        # 更新状态为处理中
        with task_lock:
            task_status[task_id] = {
                "status": "processing",
                "message": "正在处理，请稍候...",
                "started_at": datetime.now().isoformat()
            }
        save_task_status()  # 保存到文件
        
        # 确保可以导入并行处理器
        if str(project_root) not in sys.path:
            sys.path.insert(0, str(project_root))
        
        from beatsync_parallel_processor import process_beat_sync_parallel
        
        # 使用并行处理器处理（并行运行两个版本）
        success = process_beat_sync_parallel(
            str(dance_path),
            str(bgm_path),
            str(output_dir),
            task_id
        )
        
        # 检查输出文件（即使success=False，也可能有部分成功）
        modular_output = output_dir / f"{task_id}_modular.mp4"
        v2_output = output_dir / f"{task_id}_v2.mp4"
        
        modular_exists = modular_output.exists() and modular_output.stat().st_size > 0
        v2_exists = v2_output.exists() and v2_output.stat().st_size > 0
        
        # 如果有任何一个输出文件，就认为部分成功
        if modular_exists or v2_exists:
            # 更新状态为成功（支持部分成功）
            result = {
                "status": "success",
                "message": "处理成功" if (modular_exists and v2_exists) else "部分处理成功",
                "completed_at": datetime.now().isoformat()
            }
            
            if modular_exists:
                result["modular_output"] = str(modular_output)
            if v2_exists:
                result["v2_output"] = str(v2_output)
            
            # 如果只有一个成功，添加提示
            if modular_exists and not v2_exists:
                result["message"] = "处理成功（modular版本）"
            elif v2_exists and not modular_exists:
                result["message"] = "处理成功（V2版本）"
            
            with task_lock:
                task_status[task_id].update(result)
            save_task_status()  # 保存到文件
        else:
            # 记录失败原因
            print(f"ERROR: 并行处理器返回失败，task_id: {task_id}")
            print(f"ERROR: 输出目录: {output_dir}")
            print(f"ERROR: 输出目录内容: {list(output_dir.glob('*'))}")
            
            with task_lock:
                task_status[task_id] = {
                    "status": "failed",
                    "error": "处理失败",
                    "message": "处理失败",
                    "completed_at": datetime.now().isoformat()
                }
            save_task_status()  # 保存到文件
    
    except ImportError as e:
        error_msg = f"导入并行处理器失败: {str(e)}"
        print(f"ERROR: {error_msg}")
        print(f"ERROR: sys.path: {sys.path}")
        print(f"ERROR: project_root: {project_root}")
        with task_lock:
            task_status[task_id] = {
                "status": "failed",
                "error": "处理失败",
                "message": f"系统错误: {error_msg}",
                "completed_at": datetime.now().isoformat()
            }
        save_task_status()  # 保存到文件
    except Exception as e:
        error_trace = traceback.format_exc()
        error_msg = f"处理异常: {str(e)}"
        print(f"ERROR: {error_msg}")
        print(f"ERROR: {error_trace}")
        with task_lock:
            task_status[task_id] = {
                "status": "failed",
                "error": "处理失败",
                "message": "服务器内部错误",
                "completed_at": datetime.now().isoformat()
            }
        save_task_status()  # 保存到文件


@app.post("/api/process")
async def process_video(
    dance_file_id: str = Form(...),
    bgm_file_id: str = Form(...)
):
    """
    提交视频处理任务（异步处理）
    
    参数:
        dance_file_id: 原始视频文件ID
        bgm_file_id: 音源视频文件ID
    
    返回:
        task_id: 任务ID
        status: 任务状态（pending）
        message: 提示信息
    """
    # 查找文件
    dance_files = list(UPLOAD_DIR.glob(f"{dance_file_id}_dance.*"))
    bgm_files = list(UPLOAD_DIR.glob(f"{bgm_file_id}_bgm.*"))
    
    if not dance_files:
        raise HTTPException(status_code=404, detail="原始视频文件不存在")
    if not bgm_files:
        raise HTTPException(status_code=404, detail="音源视频文件不存在")
    
    dance_path = dance_files[0]
    bgm_path = bgm_files[0]
    
    # 生成任务ID和输出目录
    task_id = str(uuid.uuid4())
    output_dir = OUTPUT_DIR / task_id
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 初始化任务状态
    with task_lock:
        task_status[task_id] = {
            "status": "pending",
            "message": "任务已提交，正在处理...",
            "created_at": datetime.now().isoformat()
        }
    save_task_status()  # 保存到文件
    
    # 启动后台处理线程
    thread = threading.Thread(
        target=process_video_background,
        args=(task_id, dance_path, bgm_path, output_dir),
        daemon=True  # 设置为守护线程，主进程退出时自动退出
    )
    thread.start()
    
    # 立即返回任务ID
    return {
        "task_id": task_id,
        "status": "pending",
        "message": "任务已提交，正在处理..."
    }


@app.get("/api/status/{task_id}")
async def get_task_status(task_id: str):
    """
    查询任务处理状态
    
    参数:
        task_id: 任务ID
    
    返回:
        task_id: 任务ID
        status: 任务状态（pending/processing/success/failed）
        message: 状态消息
        modular_output: modular版本输出文件（如果成功）
        v2_output: v2版本输出文件（如果成功）
        error: 错误信息（如果失败）
    """
    with task_lock:
        status = task_status.get(task_id)
    
    if not status:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    # 返回任务状态
    result = {
        "task_id": task_id,
        "status": status["status"],
        "message": status.get("message", "")
    }
    
    # 如果成功，添加输出文件信息
    if status["status"] == "success":
        if "modular_output" in status:
            result["modular_output"] = status["modular_output"]
        if "v2_output" in status:
            result["v2_output"] = status["v2_output"]
    
    # 如果失败，添加错误信息
    if status["status"] == "failed":
        result["error"] = status.get("error", "处理失败")
    
    return result


@app.get("/api/download/{task_id}")
async def download_result(task_id: str, version: Optional[str] = None):
    """
    下载处理结果
    
    参数:
        task_id: 任务ID
        version: 版本类型 ("modular" 或 "v2")，如果不指定则下载modular版本
    
    返回:
        视频文件（二进制流）
    """
    # 查找输出文件
    output_dir = OUTPUT_DIR / task_id
    if not output_dir.exists():
        raise HTTPException(status_code=404, detail="任务不存在")
    
    modular_output = output_dir / f"{task_id}_modular.mp4"
    v2_output = output_dir / f"{task_id}_v2.mp4"
    
    # 根据version参数选择文件
    if version == "v2" and v2_output.exists():
        output_file = v2_output
        filename = f"beatsync_{task_id}_v2.mp4"
    elif version == "modular" and modular_output.exists():
        output_file = modular_output
        filename = f"beatsync_{task_id}_modular.mp4"
    elif modular_output.exists():
        # 默认返回modular版本
        output_file = modular_output
        filename = f"beatsync_{task_id}_modular.mp4"
    elif v2_output.exists():
        output_file = v2_output
        filename = f"beatsync_{task_id}_v2.mp4"
    else:
        raise HTTPException(status_code=404, detail="输出文件不存在")
    
    return FileResponse(
        str(output_file),
        media_type='video/mp4',
        filename=filename
    )


@app.get("/api/health")
@app.head("/api/health")
async def health_check():
    """
    健康检查接口
    支持GET和HEAD请求（UptimeRobot等监控服务通常使用HEAD请求）
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }


# 启动时清理旧文件
@app.on_event("startup")
async def startup_event():
    """启动时清理超过24小时的临时文件"""
    cleanup_old_files()


def cleanup_old_files():
    """清理超过指定时间的临时文件"""
    now = datetime.now()
    for directory in [UPLOAD_DIR, OUTPUT_DIR]:
        if not directory.exists():
            continue
        for item in directory.iterdir():
            try:
                if item.is_file():
                    file_time = datetime.fromtimestamp(item.stat().st_mtime)
                    if now - file_time > timedelta(hours=CLEANUP_AGE_HOURS):
                        item.unlink()
                elif item.is_dir():
                    # 对于目录，检查目录内所有文件
                    dir_time = datetime.fromtimestamp(item.stat().st_mtime)
                    if now - dir_time > timedelta(hours=CLEANUP_AGE_HOURS):
                        shutil.rmtree(item)
            except Exception as e:
                print(f"清理文件失败 {item}: {e}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

