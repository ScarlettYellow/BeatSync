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

# 导入性能日志记录器
try:
    from performance_logger import create_logger
    PERFORMANCE_LOGGING_ENABLED = True
except ImportError:
    PERFORMANCE_LOGGING_ENABLED = False
    print("WARNING: 性能日志记录器未找到，性能日志功能已禁用")

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
WEB_OUTPUTS_RETENTION_DAYS = 3  # Web输出保留3天

# 确保目录存在
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# 任务状态管理（用于异步处理）
TASK_STATUS_FILE = project_root / "outputs" / "task_status.json"
task_status: Dict[str, dict] = {}
task_lock = threading.RLock()  # 使用可重入锁，避免死锁


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


def cleanup_old_web_outputs():
    """清理超过3天的Web输出文件"""
    try:
        if not OUTPUT_DIR.exists():
            return
        
        cutoff_time = datetime.now() - timedelta(days=WEB_OUTPUTS_RETENTION_DAYS)
        cleaned_count = 0
        
        for task_dir in OUTPUT_DIR.iterdir():
            if not task_dir.is_dir():
                continue
            
            try:
                # 获取目录的修改时间
                mtime = datetime.fromtimestamp(task_dir.stat().st_mtime)
                if mtime < cutoff_time:
                    # 删除超过3天的目录
                    shutil.rmtree(task_dir)
                    cleaned_count += 1
                    print(f"INFO: 已清理旧的Web输出: {task_dir.name}")
            except Exception as e:
                print(f"WARNING: 清理Web输出失败 {task_dir}: {e}")
        
        if cleaned_count > 0:
            print(f"✅ 已清理 {cleaned_count} 个超过{WEB_OUTPUTS_RETENTION_DAYS}天的Web输出目录")
    except Exception as e:
        print(f"WARNING: 清理Web输出时出错: {e}")


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


# 注意：任务状态加载和清理操作已移至 @app.on_event("startup") 中执行
# 这样可以避免在导入模块时执行耗时操作


@app.get("/")
@app.head("/")
async def root():
    """
    根路径，返回API信息
    支持GET和HEAD请求（Render内部健康检查使用HEAD请求）
    """
    return {
        "name": "BeatSync API",
        "version": "1.0.0",
        "status": "running"
    }


@app.post("/api/process/test")
async def process_video_test(
    dance_file_id: str = Form(...),
    bgm_file_id: str = Form(...)
):
    """
    测试端点：直接返回响应，不执行任何处理
    """
    import sys
    print(f"INFO: [TEST] 收到测试请求 - dance_file_id: {dance_file_id}, bgm_file_id: {bgm_file_id}", file=sys.stderr, flush=True)
    result = {
        "task_id": "test-123",
        "status": "pending",
        "message": "测试响应"
    }
    print(f"INFO: [TEST] 返回测试响应: {result}", file=sys.stderr, flush=True)
    return JSONResponse(content=result)


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
    import sys
    print(f"INFO: 收到上传请求 - file_type: {file_type}, filename: {file.filename if file else 'None'}", file=sys.stderr, flush=True)
    
    # 验证文件类型
    allowed_extensions = ['.mp4', '.MP4', '.mov', '.MOV', '.avi', '.AVI', '.mkv', '.MKV']
    file_ext = Path(file.filename).suffix
    if file_ext not in allowed_extensions:
        import sys
        print(f"ERROR: 不支持的文件格式: {file_ext}", file=sys.stderr, flush=True)
        raise HTTPException(
            status_code=400,
            detail=f"不支持的文件格式，支持格式: {', '.join(allowed_extensions)}"
        )
    
    # 验证file_type
    if file_type not in ['dance', 'bgm']:
        import sys
        print(f"ERROR: 无效的file_type: {file_type}", file=sys.stderr, flush=True)
        raise HTTPException(
            status_code=400,
            detail="file_type必须是'dance'或'bgm'"
        )
    
    # 生成唯一文件名
    file_id = str(uuid.uuid4())
    file_path = UPLOAD_DIR / f"{file_id}_{file_type}{file_ext}"
    
    import sys
    print(f"INFO: 开始保存文件 - file_id: {file_id}, path: {file_path}", file=sys.stderr, flush=True)
    
    # 保存文件
    try:
        file_size = 0
        with open(file_path, "wb") as f:
            while True:
                chunk = await file.read(8192)  # 8KB chunks
                if not chunk:
                    break
                f.write(chunk)
                file_size += len(chunk)
        
        import sys
        print(f"INFO: 文件保存成功 - file_id: {file_id}, size: {file_size} bytes", file=sys.stderr, flush=True)
        
        result = {
            "file_id": file_id,
            "file_type": file_type,
            "filename": file.filename,
            "size": file_size,
            "message": "文件上传成功"
        }
        print(f"INFO: 返回上传响应: {result}", file=sys.stderr, flush=True)
        return result
    except Exception as e:
        import sys
        import traceback
        print(f"ERROR: 文件保存失败: {e}", file=sys.stderr, flush=True)
        traceback.print_exc(file=sys.stderr)
        if file_path.exists():
            os.remove(file_path)
        raise HTTPException(
            status_code=500,
            detail=f"文件上传失败: {str(e)}"
        )


def process_video_background(task_id: str, dance_path: Path, bgm_path: Path, output_dir: Path):
    """后台处理视频的函数"""
    # 创建性能日志记录器
    perf_logger = None
    if PERFORMANCE_LOGGING_ENABLED:
        perf_logger = create_logger(task_id, "视频处理")
        perf_logger.start()
        perf_logger.log_file_operation("读取输入文件", str(dance_path), 
                                       dance_path.stat().st_size if dance_path.exists() else None)
        perf_logger.log_file_operation("读取输入文件", str(bgm_path),
                                       bgm_path.stat().st_size if bgm_path.exists() else None)
    
    try:
        import traceback
        import time
        
        # 更新状态为处理中
        with task_lock:
            task_status[task_id] = {
                "status": "processing",
                "message": "正在处理，请稍候...",
                "started_at": datetime.now().isoformat(),
                "modular_status": "processing",
                "v2_status": "processing"
            }
        save_task_status()  # 保存到文件
        
        if perf_logger:
            perf_logger.log_step("初始化任务状态")
        
        # 确保可以导入并行处理器
        if str(project_root) not in sys.path:
            sys.path.insert(0, str(project_root))
        
        if perf_logger:
            perf_logger.log_step("导入并行处理器模块")
        
        from beatsync_parallel_processor import process_beat_sync_parallel
        
        # 启动并行处理（在单独线程中运行，以便监控进度）
        import threading
        
        processing_done = threading.Event()
        processing_success = [False]  # 使用列表以便在线程间共享
        
        processing_start_time = time.time()
        
        def run_processing():
            try:
                if perf_logger:
                    perf_logger.log_step("启动并行处理线程")
                success = process_beat_sync_parallel(
                    str(dance_path),
                    str(bgm_path),
                    str(output_dir),
                    task_id
                )
                processing_success[0] = success
                if perf_logger:
                    processing_duration = time.time() - processing_start_time
                    perf_logger.log_step("并行处理完成", processing_duration)
            except Exception as e:
                if perf_logger:
                    perf_logger.log_error(f"并行处理异常: {str(e)}", "EXCEPTION")
                raise
            finally:
                processing_done.set()
        
        processing_thread = threading.Thread(target=run_processing, daemon=False)
        processing_thread.start()
        
        if perf_logger:
            perf_logger.log_step("启动处理线程")
        
        # 监控处理进度（每10秒检查一次输出文件）
        modular_output = output_dir / f"{task_id}_modular.mp4"
        v2_output = output_dir / f"{task_id}_v2.mp4"
        
        # 也检查中间文件（modular版本可能生成中间文件）
        modular_intermediate = output_dir / f"{task_id}_modular_module1_aligned.mp4"
        
        check_interval = 10  # 10秒检查一次
        last_check_time = time.time()
        
        while not processing_done.is_set():
            current_time = time.time()
            if current_time - last_check_time >= check_interval:
                # 检查输出文件（modular版本只检查最终文件，不接受中间文件）
                modular_final_exists = modular_output.exists() and modular_output.stat().st_size > 0
                modular_intermediate_exists = modular_intermediate.exists() and modular_intermediate.stat().st_size > 0
                v2_exists = v2_output.exists() and v2_output.stat().st_size > 0
                
                # 如果只有中间文件，记录警告
                if modular_intermediate_exists and not modular_final_exists:
                    print(f"WARNING: Modular版本只生成了中间文件，模块2可能失败")
                
                # 更新状态
                with task_lock:
                    status = task_status.get(task_id, {})
                    
                    # 更新modular状态（使用modular_final_exists，因为这里只检查最终文件）
                    if modular_final_exists and status.get("modular_status") != "success":
                        status["modular_status"] = "success"
                        status["modular_output"] = str(modular_output)
                    
                    # 更新v2状态
                    if v2_exists and status.get("v2_status") != "success":
                        status["v2_status"] = "success"
                        status["v2_output"] = str(v2_output)
                    
                    # 更新消息
                    modular_done = status.get("modular_status") == "success"
                    v2_done = status.get("v2_status") == "success"
                    
                    if modular_done and v2_done:
                        status["message"] = "处理完成"
                    elif modular_done:
                        status["message"] = "modular版本已完成，V2版本处理中"
                    elif v2_done:
                        status["message"] = "V2版本已完成，modular版本处理中"
                    else:
                        status["message"] = "正在处理，请稍候..."
                    
                    task_status[task_id] = status
                save_task_status()  # 保存到文件
                
                last_check_time = current_time
            
            # 等待一小段时间再检查
            time.sleep(1)
        
        # 等待处理线程完成
        processing_thread.join()
        
        if perf_logger:
            perf_logger.log_step("等待处理线程完成")
        
        # 最终检查输出文件（包括中间文件）
        modular_final_exists = modular_output.exists() and modular_output.stat().st_size > 0
        modular_intermediate_exists = modular_intermediate.exists() and modular_intermediate.stat().st_size > 0
        modular_exists = modular_final_exists or modular_intermediate_exists
        v2_exists = v2_output.exists() and v2_output.stat().st_size > 0
        
        if perf_logger:
            if modular_final_exists:
                perf_logger.log_file_operation("检查输出文件（最终）", str(modular_output),
                                             modular_output.stat().st_size)
            elif modular_intermediate_exists:
                perf_logger.log_file_operation("检查输出文件（中间）", str(modular_intermediate),
                                             modular_intermediate.stat().st_size)
            if v2_exists:
                perf_logger.log_file_operation("检查输出文件", str(v2_output),
                                             v2_output.stat().st_size)
        
        # 更新最终状态
        # 注意：modular版本必须输出最终文件，不接受中间文件
        # 优先检查文件是否存在，即使处理过程中有异常，只要文件生成了就认为成功
        try:
            if modular_final_exists or v2_exists:
                result = {
                    "status": "success",
                    "message": "处理完成" if (modular_final_exists and v2_exists) else "部分处理完成",
                    "completed_at": datetime.now().isoformat()
                }
                
                if modular_final_exists:
                    result["modular_output"] = str(modular_output)
                    result["modular_status"] = "success"
                else:
                    # 如果只有中间文件，认为失败
                    if modular_intermediate_exists:
                        print(f"ERROR: Modular版本只生成了中间文件，未生成最终输出文件")
                        print(f"ERROR: 中间文件: {modular_intermediate}")
                        print(f"ERROR: 这表示模块2（裁剪模块）失败")
                    result["modular_status"] = "failed"
                    if modular_intermediate_exists:
                        result["modular_error"] = "模块2失败，只生成了中间文件，未生成最终输出"
                
                if v2_exists:
                    result["v2_output"] = str(v2_output)
                    result["v2_status"] = "success"
                else:
                    result["v2_status"] = "failed"
                
                with task_lock:
                    task_status[task_id].update(result)
                save_task_status()  # 保存到文件
                
                if perf_logger:
                    perf_logger.finish(success=True)
                
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
            else:
                # 记录失败原因
                error_msg = f"并行处理器返回失败，task_id: {task_id}"
                print(f"ERROR: {error_msg}")
                print(f"ERROR: 输出目录: {output_dir}")
                print(f"ERROR: 输出目录内容: {list(output_dir.glob('*'))}")
                
                with task_lock:
                    task_status[task_id] = {
                        "status": "failed",
                        "error": "处理失败",
                        "message": "处理失败",
                        "completed_at": datetime.now().isoformat(),
                        "modular_status": "failed",
                        "v2_status": "failed"
                    }
                save_task_status()  # 保存到文件
                
                if perf_logger:
                    perf_logger.finish(success=False, error_msg=error_msg)
                
                # 即使失败，也清理上传的文件（避免占用空间）
                try:
                    if dance_path.exists():
                        dance_path.unlink()
                        print(f"INFO: 已清理上传文件: {dance_path}")
                    if bgm_path.exists():
                        bgm_path.unlink()
                        print(f"INFO: 已清理上传文件: {bgm_path}")
                except Exception as cleanup_error:
                    print(f"WARNING: 清理上传文件失败: {cleanup_error}")
        except Exception as status_error:
            # 即使更新状态时出错，也要检查文件是否存在
            print(f"WARNING: 更新状态时出错: {status_error}")
            print(f"WARNING: 但继续检查输出文件...")
            
            # 重新检查文件（可能文件已经生成）
            try:
                modular_final_exists = modular_output.exists() and modular_output.stat().st_size > 0
                v2_exists = v2_output.exists() and v2_output.stat().st_size > 0
                
                if modular_final_exists or v2_exists:
                    # 文件已生成，应该标记为成功
                    result = {
                        "status": "success",
                        "message": "处理完成" if (modular_final_exists and v2_exists) else "部分处理完成",
                        "completed_at": datetime.now().isoformat()
                    }
                    
                    if modular_final_exists:
                        result["modular_output"] = str(modular_output)
                        result["modular_status"] = "success"
                    else:
                        result["modular_status"] = "failed"
                    
                    if v2_exists:
                        result["v2_output"] = str(v2_output)
                        result["v2_status"] = "success"
                    else:
                        result["v2_status"] = "failed"
                    
                    with task_lock:
                        task_status[task_id].update(result)
                    save_task_status()
                    print(f"INFO: 尽管更新状态时出错，但文件已生成，已标记为成功")
                else:
                    # 文件未生成，标记为失败
                    raise status_error
            except Exception:
                # 如果重新检查也失败，抛出原始异常
                raise status_error
    
    except ImportError as e:
        error_msg = f"导入并行处理器失败: {str(e)}"
        print(f"ERROR: {error_msg}")
        print(f"ERROR: sys.path: {sys.path}")
        print(f"ERROR: project_root: {project_root}")
        if perf_logger:
            perf_logger.log_error(error_msg, "IMPORT_ERROR")
            perf_logger.finish(success=False, error_msg=error_msg)
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
        
        # 即使有异常，也要检查文件是否已经生成
        # 如果文件已生成，应该标记为成功
        try:
            modular_output = output_dir / f"{task_id}_modular.mp4"
            v2_output = output_dir / f"{task_id}_v2.mp4"
            
            modular_final_exists = modular_output.exists() and modular_output.stat().st_size > 0
            v2_exists = v2_output.exists() and v2_output.stat().st_size > 0
            
            if modular_final_exists or v2_exists:
                # 文件已生成，应该标记为成功
                print(f"INFO: 尽管处理过程中有异常，但输出文件已生成，标记为成功")
                result = {
                    "status": "success",
                    "message": "处理完成" if (modular_final_exists and v2_exists) else "部分处理完成",
                    "completed_at": datetime.now().isoformat()
                }
                
                if modular_final_exists:
                    result["modular_output"] = str(modular_output)
                    result["modular_status"] = "success"
                else:
                    result["modular_status"] = "failed"
                
                if v2_exists:
                    result["v2_output"] = str(v2_output)
                    result["v2_status"] = "success"
                else:
                    result["v2_status"] = "failed"
                
                with task_lock:
                    task_status[task_id] = result
                save_task_status()
                
                if perf_logger:
                    perf_logger.finish(success=True)
                
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
            else:
                # 文件未生成，标记为失败
                if perf_logger:
                    perf_logger.log_error(error_msg, "EXCEPTION")
                    perf_logger.finish(success=False, error_msg=error_msg)
                with task_lock:
                    task_status[task_id] = {
                        "status": "failed",
                        "error": "处理失败",
                        "message": "服务器内部错误",
                        "completed_at": datetime.now().isoformat()
                    }
                save_task_status()  # 保存到文件
        except Exception as check_error:
            # 如果检查文件时也出错，记录原始错误
            print(f"ERROR: 检查输出文件时也出错: {check_error}")
            if perf_logger:
                perf_logger.log_error(error_msg, "EXCEPTION")
                perf_logger.finish(success=False, error_msg=error_msg)
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
    import sys
    import time
    start_time = time.time()
    print(f"INFO: [API/process] 收到处理请求 - dance_file_id: {dance_file_id}, bgm_file_id: {bgm_file_id}", file=sys.stderr, flush=True)
    sys.stderr.flush()
    
    try:
        # 查找文件（使用更精确的路径，避免glob扫描大量文件）
        print(f"INFO: 开始查找文件...", file=sys.stderr, flush=True)
        # 先尝试直接构建路径（更快的路径）
        dance_path = UPLOAD_DIR / f"{dance_file_id}_dance.mp4"
        bgm_path = UPLOAD_DIR / f"{bgm_file_id}_bgm.mp4"
        
        # 如果mp4不存在，再尝试其他格式
        if not dance_path.exists():
            dance_files = list(UPLOAD_DIR.glob(f"{dance_file_id}_dance.*"))
            if dance_files:
                dance_path = dance_files[0]
            else:
                dance_path = None
        else:
            dance_files = [dance_path]
        
        if not bgm_path.exists():
            bgm_files = list(UPLOAD_DIR.glob(f"{bgm_file_id}_bgm.*"))
            if bgm_files:
                bgm_path = bgm_files[0]
            else:
                bgm_path = None
        else:
            bgm_files = [bgm_path]
        
        print(f"INFO: 找到dance文件: {len(dance_files) if dance_path else 0} 个", file=sys.stderr, flush=True)
        print(f"INFO: 找到bgm文件: {len(bgm_files) if bgm_path else 0} 个", file=sys.stderr, flush=True)
        
        if not dance_path or not dance_path.exists():
            print(f"ERROR: 原始视频文件不存在: {dance_file_id}", file=sys.stderr, flush=True)
            raise HTTPException(status_code=404, detail="原始视频文件不存在")
        if not bgm_path or not bgm_path.exists():
            print(f"ERROR: 音源视频文件不存在: {bgm_file_id}", file=sys.stderr, flush=True)
            raise HTTPException(status_code=404, detail="音源视频文件不存在")
        
        print(f"INFO: dance文件路径: {dance_path}", file=sys.stderr, flush=True)
        print(f"INFO: bgm文件路径: {bgm_path}", file=sys.stderr, flush=True)
        
        # 生成任务ID和输出目录
        step_time = time.time()
        task_id = str(uuid.uuid4())
        output_dir = OUTPUT_DIR / task_id
        print(f"INFO: [步骤1] 生成任务ID完成 (耗时{time.time()-step_time:.3f}s): {task_id}", file=sys.stderr, flush=True)
        
        step_time = time.time()
        output_dir.mkdir(parents=True, exist_ok=True)
        print(f"INFO: [步骤2] 创建输出目录完成 (耗时{time.time()-step_time:.3f}s): {output_dir}", file=sys.stderr, flush=True)
        sys.stderr.flush()
        
        # 初始化任务状态（快速操作，使用锁但快速释放）
        step_time = time.time()
        try:
            with task_lock:
                task_status[task_id] = {
                    "status": "pending",
                    "message": "任务已提交，正在处理...",
                    "created_at": datetime.now().isoformat(),
                    "modular_status": "processing",
                    "v2_status": "processing"
                }
            print(f"INFO: [步骤3] 任务状态已初始化 (耗时{time.time()-step_time:.3f}s): {task_id}", file=sys.stderr, flush=True)
        except Exception as status_error:
            print(f"ERROR: [步骤3] 初始化任务状态失败: {status_error}", file=sys.stderr, flush=True)
            import traceback
            traceback.print_exc(file=sys.stderr)
            # 即使失败也继续，不阻塞响应
        
        # 启动后台处理线程
        step_time = time.time()
        try:
            thread = threading.Thread(
                target=process_video_background,
                args=(task_id, dance_path, bgm_path, output_dir),
                daemon=True  # 设置为守护线程，主进程退出时自动退出
            )
            thread.start()
            print(f"INFO: [步骤4] 后台处理线程已启动 (耗时{time.time()-step_time:.3f}s): {task_id}", file=sys.stderr, flush=True)
        except Exception as thread_error:
            print(f"ERROR: 启动后台处理线程失败: {thread_error}", file=sys.stderr, flush=True)
            import traceback
            traceback.print_exc(file=sys.stderr)
            raise HTTPException(status_code=500, detail=f"启动处理任务失败: {str(thread_error)}")
        
        # 立即返回任务ID（不等待文件保存）
        step_time = time.time()
        result = {
            "task_id": task_id,
            "status": "pending",
            "message": "任务已提交，正在处理..."
        }
        print(f"INFO: [步骤5] 准备返回响应 (耗时{time.time()-step_time:.3f}s)", file=sys.stderr, flush=True)
        print(f"INFO: [API/process] 总耗时: {time.time()-start_time:.3f}s, 返回结果: {result}", file=sys.stderr, flush=True)
        
        # 在后台线程中保存状态（不阻塞响应）
        def save_status_async():
            try:
                save_task_status()
            except Exception as e:
                print(f"WARNING: 异步保存任务状态失败: {e}", file=sys.stderr, flush=True)
        
        threading.Thread(target=save_status_async, daemon=True).start()
        
        # 确保在返回前所有日志都已输出
        sys.stderr.flush()
        
        # 直接返回JSON响应，避免FastAPI的自动序列化可能的问题
        print(f"INFO: [API/process] 即将返回响应...", file=sys.stderr, flush=True)
        sys.stderr.flush()
        
        return JSONResponse(content=result)
    except HTTPException:
        # 重新抛出HTTP异常
        import sys
        sys.stderr.flush()
        raise
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"ERROR: 处理请求时发生异常: {e}", file=sys.stderr, flush=True)
        print(f"ERROR: {error_trace}", file=sys.stderr, flush=True)
        import sys
        sys.stderr.flush()
        raise HTTPException(status_code=500, detail=f"处理请求失败: {str(e)}")


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
    
    # 添加modular和v2的状态
    result["modular_status"] = status.get("modular_status", "processing")
    result["v2_status"] = status.get("v2_status", "processing")
    
    # 如果成功，添加输出文件信息
    if status["status"] == "success":
        if "modular_output" in status:
            result["modular_output"] = status["modular_output"]
        if "v2_output" in status:
            result["v2_output"] = status["v2_output"]
    
    # 如果处理中，也返回已完成的输出文件
    if status["status"] == "processing":
        if "modular_output" in status:
            result["modular_output"] = status["modular_output"]
        if "v2_output" in status:
            result["v2_output"] = status["v2_output"]
    
    # 如果失败，添加错误信息
    if status["status"] == "failed":
        result["error"] = status.get("error", "处理失败")
    
    return result


@app.get("/api/preview/{task_id}")
async def preview_result(task_id: str, version: Optional[str] = None):
    """
    预览处理结果（在线播放）
    
    参数:
        task_id: 任务ID
        version: 版本类型 ("modular" 或 "v2")，如果不指定则预览modular版本
    
    返回:
        视频文件（用于在线播放）
    """
    # 查找输出文件
    output_dir = OUTPUT_DIR / task_id
    if not output_dir.exists():
        raise HTTPException(status_code=404, detail="任务不存在")
    
    modular_output = output_dir / f"{task_id}_modular.mp4"
    modular_intermediate = output_dir / f"{task_id}_modular_module1_aligned.mp4"
    v2_output = output_dir / f"{task_id}_v2.mp4"
    
    # 根据version参数选择文件（优先使用最终文件，如果没有则使用中间文件）
    if version == "v2" and v2_output.exists():
        output_file = v2_output
        filename = f"v2_{task_id}.mp4"
    elif version == "modular":
        if modular_output.exists():
            output_file = modular_output
            filename = f"modular_{task_id}.mp4"
        elif modular_intermediate.exists():
            output_file = modular_intermediate
            filename = f"modular_{task_id}_intermediate.mp4"
        else:
            raise HTTPException(status_code=404, detail="Modular版本输出文件不存在")
    elif modular_output.exists():
        # 默认返回modular版本
        output_file = modular_output
        filename = f"modular_{task_id}.mp4"
    elif v2_output.exists():
        output_file = v2_output
        filename = f"v2_{task_id}.mp4"
    else:
        raise HTTPException(status_code=404, detail="输出文件不存在")
    
    # 使用流式响应，支持在线播放（不设置attachment）
    return FileResponse(
        str(output_file),
        media_type='video/mp4',
        filename=filename,
        headers={
            "Accept-Ranges": "bytes",  # 支持断点续传和流式播放
            "Content-Disposition": f'inline; filename="{filename}"'  # inline表示在线播放，而不是下载
        }
    )


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
    modular_intermediate = output_dir / f"{task_id}_modular_module1_aligned.mp4"
    v2_output = output_dir / f"{task_id}_v2.mp4"
    
    # 根据version参数选择文件（优先使用最终文件，如果没有则使用中间文件）
    if version == "v2" and v2_output.exists():
        output_file = v2_output
        filename = f"v2_{task_id}.mp4"
    elif version == "modular":
        if modular_output.exists():
            output_file = modular_output
            filename = f"modular_{task_id}.mp4"
        elif modular_intermediate.exists():
            output_file = modular_intermediate
            filename = f"modular_{task_id}_intermediate.mp4"
        else:
            raise HTTPException(status_code=404, detail="Modular版本输出文件不存在")
    elif modular_output.exists():
        # 默认返回modular版本
        output_file = modular_output
        filename = f"modular_{task_id}.mp4"
    elif v2_output.exists():
        output_file = v2_output
        filename = f"v2_{task_id}.mp4"
    else:
        raise HTTPException(status_code=404, detail="输出文件不存在")
    
    # 使用流式响应，支持断点续传，提高下载速度
    return FileResponse(
        str(output_file),
        media_type='video/mp4',
        filename=filename,
        headers={
            "Accept-Ranges": "bytes",  # 支持断点续传
            "Content-Disposition": f'attachment; filename="{filename}"'  # 确保浏览器下载而不是播放
        }
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
    """启动时执行初始化操作（快速启动，清理操作在后台执行）"""
    # 加载任务状态（必须同步执行，但通常很快）
    load_task_status()
    
    # 清理操作在后台线程执行，不阻塞服务启动
    def background_cleanup():
        try:
            cleanup_old_tasks()
            cleanup_old_files()
            cleanup_old_web_outputs()
        except Exception as e:
            print(f"WARNING: 后台清理操作失败: {e}")
    
    # 在后台线程执行清理操作
    cleanup_thread = threading.Thread(target=background_cleanup, daemon=True)
    cleanup_thread.start()
    print("INFO: 后台清理任务已启动（不阻塞服务启动）")


def cleanup_old_files():
    """清理超过指定时间的临时文件（仅清理web_uploads，web_outputs由cleanup_old_web_outputs处理）"""
    now = datetime.now()
    # 只清理web_uploads目录，web_outputs由专门的函数处理
    if UPLOAD_DIR.exists():
        for item in UPLOAD_DIR.iterdir():
            try:
                if item.is_file():
                    file_time = datetime.fromtimestamp(item.stat().st_mtime)
                    if now - file_time > timedelta(hours=CLEANUP_AGE_HOURS):
                        item.unlink()
                        print(f"INFO: 已清理旧的上传文件: {item.name}")
            except Exception as e:
                print(f"WARNING: 清理上传文件失败 {item}: {e}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

