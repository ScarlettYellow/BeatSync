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
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional

from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

app = FastAPI(title="BeatSync API", version="1.0.0")

# 配置CORS（允许前端跨域访问）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应限制具体域名
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


@app.post("/api/process")
async def process_video(
    dance_file_id: str = Form(...),
    bgm_file_id: str = Form(...)
):
    """
    处理视频（同步处理）
    
    注意：处理时间可能较长（几分钟到十几分钟），
    如果浏览器或代理有超时限制，可能需要改为异步处理。
    """
    """
    处理视频（同步处理）
    
    参数:
        dance_file_id: 原始视频文件ID
        bgm_file_id: 音源视频文件ID
    
    返回:
        task_id: 任务ID
        status: 处理状态
        output_file: 输出文件路径（如果成功）
        error: 错误信息（如果失败）
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
    
    # 生成输出文件路径
    task_id = str(uuid.uuid4())
    output_dir = OUTPUT_DIR / task_id
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 调用并行处理器
    try:
        import sys
        import traceback
        
        # 确保可以导入并行处理器（添加项目根目录到路径）
        if str(project_root) not in sys.path:
            sys.path.insert(0, str(project_root))
        
        from beatsync_parallel_processor import process_beat_sync_parallel
        
        # 使用并行处理器处理
        success = process_beat_sync_parallel(
            str(dance_path),
            str(bgm_path),
            str(output_dir),
            task_id
        )
        
        if success:
            # 查找输出文件（优先modular版本，其次v2版本）
            modular_output = output_dir / f"{task_id}_modular.mp4"
            v2_output = output_dir / f"{task_id}_v2.mp4"
            
            if modular_output.exists():
                output_file = modular_output
            elif v2_output.exists():
                output_file = v2_output
            else:
                # 记录详细错误
                error_msg = f"处理完成但未找到输出文件。输出目录: {output_dir}，文件列表: {list(output_dir.glob('*'))}"
                print(f"ERROR: {error_msg}")
                return {
                    "task_id": task_id,
                    "status": "failed",
                    "error": "处理失败",
                    "message": "处理完成但未找到输出文件"
                }
            
            return {
                "task_id": task_id,
                "status": "success",
                "output_file": str(output_file),
                "message": "处理成功"
            }
        else:
            # 记录失败原因
            print(f"ERROR: 并行处理器返回失败，task_id: {task_id}")
            return {
                "task_id": task_id,
                "status": "failed",
                "error": "处理失败",
                "message": "处理失败"
            }
    
    except ImportError as e:
        error_msg = f"导入并行处理器失败: {str(e)}"
        print(f"ERROR: {error_msg}")
        print(f"ERROR: sys.path: {sys.path}")
        print(f"ERROR: project_root: {project_root}")
        return {
            "task_id": task_id,
            "status": "failed",
            "error": "处理失败",
            "message": f"系统错误: {error_msg}"
        }
    except Exception as e:
        # 记录详细错误信息
        error_trace = traceback.format_exc()
        error_msg = f"处理异常: {str(e)}"
        print(f"ERROR: {error_msg}")
        print(f"ERROR: {error_trace}")
        return {
            "task_id": task_id,
            "status": "failed",
            "error": "处理失败",
            "message": error_msg
        }


@app.get("/api/download/{task_id}")
async def download_result(task_id: str):
    """
    下载处理结果
    
    参数:
        task_id: 任务ID
    
    返回:
        视频文件（二进制流）
    """
    # 查找输出文件
    output_dir = OUTPUT_DIR / task_id
    if not output_dir.exists():
        raise HTTPException(status_code=404, detail="任务不存在")
    
    # 优先查找modular版本，其次v2版本
    modular_output = output_dir / f"{task_id}_modular.mp4"
    v2_output = output_dir / f"{task_id}_v2.mp4"
    
    if modular_output.exists():
        output_file = modular_output
    elif v2_output.exists():
        output_file = v2_output
    else:
        raise HTTPException(status_code=404, detail="输出文件不存在")
    
    return FileResponse(
        str(output_file),
        media_type='video/mp4',
        filename=f"beatsync_{task_id}.mp4"
    )


@app.get("/api/health")
async def health_check():
    """健康检查"""
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

