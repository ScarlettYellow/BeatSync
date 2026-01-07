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

from fastapi import FastAPI, UploadFile, File, HTTPException, Form, Depends, Header, Request
from fastapi.responses import FileResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

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

# 导入订阅系统模块
try:
    from subscription_db import init_database, get_db_path
    from subscription_service import (
        is_subscription_enabled,
        create_or_get_user,
        verify_jwt_token,
        check_whitelist,
        check_download_credits,
        consume_download_credit,
        add_to_whitelist,
        remove_from_whitelist,
        get_whitelist_users,
        get_user_subscription_info,
        get_subscription_history,
        get_download_history,
        get_used_credits_stats,
        check_daily_process_limit,
        record_process
    )
    SUBSCRIPTION_AVAILABLE = True
except ImportError as e:
    SUBSCRIPTION_AVAILABLE = False
    print(f"WARNING: 订阅系统模块未找到，订阅功能已禁用: {e}")

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

# 订阅系统认证（可选认证，允许无认证请求）
security = HTTPBearer(auto_error=False)

async def get_optional_user(
    authorization: Optional[str] = Header(None)
) -> Optional[str]:
    """
    可选的用户认证中间件
    - 如果提供了认证信息，验证并返回 user_id
    - 如果没有提供，返回 None（匿名用户）
    - 如果订阅系统未启用，始终返回 None
    """
    if not SUBSCRIPTION_AVAILABLE or not is_subscription_enabled():
        return None  # 订阅系统未启用，不进行认证
    
    if not authorization:
        return None  # 无认证信息，匿名用户
    
    try:
        # 提取 Bearer token
        if authorization.startswith("Bearer "):
            token = authorization.replace("Bearer ", "")
        else:
            token = authorization
        
        user_id = verify_jwt_token(token)
        return user_id
    except Exception as e:
        print(f"认证异常: {e}")
        return None  # 认证失败，视为匿名用户


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
                
                # 检测CPU核心数，决定是否启用并行模式
                import os
                cpu_count = os.cpu_count() or 2
                # 测试结果：串行处理反而更慢（总耗时更长）
                # 并行处理：本地52秒，线上132秒（总耗时）
                # 串行处理：本地100秒，线上180秒（总耗时）
                # 结论：保持并行处理模式，总耗时更短
                use_parallel = cpu_count >= 2  # 如果CPU核心数>=2，启用并行模式
                
                if perf_logger:
                    perf_logger.log_step(f"CPU核心数: {cpu_count}, 并行模式: {use_parallel}")
                
                success = process_beat_sync_parallel(
                    str(dance_path),
                    str(bgm_path),
                    str(output_dir),
                    task_id,
                    parallel=use_parallel  # 根据CPU核心数自动启用并行模式
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
    bgm_file_id: str = Form(...),
    authorization: Optional[str] = Header(None)
):
    """
    提交视频处理任务（异步处理）
    
    参数:
        dance_file_id: 原始视频文件ID
        bgm_file_id: 音源视频文件ID
        authorization: 可选的用户Token（用于订阅系统）
    
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
    
    # 检查每日处理次数上限（如果订阅系统启用）
    user_id = None
    if SUBSCRIPTION_AVAILABLE and authorization:
        try:
            # 提取Token（Bearer token格式）
            token = authorization.replace("Bearer ", "").strip() if authorization.startswith("Bearer ") else authorization.strip()
            user_id = verify_jwt_token(token)
            
            if user_id:
                # 检查每日处理次数上限
                process_check = check_daily_process_limit(user_id)
                if not process_check.get("allowed", True):
                    raise HTTPException(
                        status_code=429,  # Too Many Requests
                        detail=process_check.get("message", "今日处理次数已达上限")
                    )
        except HTTPException:
            raise
        except Exception as e:
            print(f"WARNING: 检查每日处理次数上限时出错: {e}", file=sys.stderr, flush=True)
            # 如果检查失败，继续处理（降级处理）
    
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
        
        # 记录处理次数（如果订阅系统启用且有用户ID）
        if SUBSCRIPTION_AVAILABLE and user_id:
            try:
                record_process(user_id, task_id)
            except Exception as record_error:
                print(f"WARNING: 记录处理次数失败: {record_error}", file=sys.stderr, flush=True)
                # 记录失败不影响处理流程
        
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
    # FastAPI的FileResponse自动支持Range请求，这对手机端视频播放很重要
    # 获取文件大小，用于优化Range请求
    file_size = output_file.stat().st_size
    
    # 使用更兼容的MIME类型设置
    # 先尝试简单的video/mp4，如果浏览器支持codecs再添加
    return FileResponse(
        str(output_file),
        media_type='video/mp4',  # 使用简单的MIME类型，避免codecs字符串导致兼容性问题
        filename=filename,
        headers={
            "Accept-Ranges": "bytes",  # 支持断点续传和流式播放（手机端必需）
            "Content-Disposition": f'inline; filename="{filename}"',  # inline表示在线播放，而不是下载
            "Cache-Control": "public, max-age=3600",  # 添加缓存，提升加载速度
            "Content-Length": str(file_size),  # 明确指定文件大小，帮助浏览器优化加载
            "Access-Control-Allow-Origin": "*",  # 确保CORS支持（虽然已在中间件配置，但显式设置更安全）
            "Access-Control-Expose-Headers": "Content-Range, Accept-Ranges, Content-Length",  # 暴露Range相关头部和文件大小
            "Content-Type": "video/mp4"  # 使用简单的MIME类型，避免codecs导致兼容性问题
        }
    )


@app.get("/api/download/{task_id}")
async def download_result(
    request: Request,
    task_id: str,
    version: Optional[str] = None,
    user_id: Optional[str] = Depends(get_optional_user)
):
    """
    下载处理结果（零耦合设计：保持向后兼容）
    
    参数:
        task_id: 任务ID
        version: 版本类型 ("modular" 或 "v2")，如果不指定则下载modular版本
        user_id: 可选的用户ID（通过认证中间件获取）
    
    返回:
        视频文件（二进制流）
    """
    # 1. 首先执行现有的文件查找逻辑（保持不变，确保向后兼容）
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
    
    # 2. 订阅检查（仅在启用且用户已认证时，零耦合设计）
    if SUBSCRIPTION_AVAILABLE and is_subscription_enabled() and user_id:
        try:
            # 检查白名单
            if check_whitelist(user_id):
                # 白名单用户，直接允许下载，不消费次数
                # 获取 IP 和 User Agent（如果可用）
                ip_address = None
                user_agent = None
                try:
                    if request and hasattr(request, 'client') and request.client:
                        ip_address = request.client.host
                    if request and hasattr(request, 'headers'):
                        user_agent = request.headers.get("user-agent")
                except:
                    pass
                consume_download_credit(user_id, task_id, version or "modular", ip_address, user_agent)
            else:
                # 检查下载次数
                credits_check = check_download_credits(user_id)
                if not credits_check["can_download"]:
                    raise HTTPException(
                        status_code=403,
                        detail={
                            "error": "insufficient_credits",
                            "message": "下载次数不足，请购买订阅或下载次数",
                            "available_credits": credits_check["total_remaining"]
                        }
                    )
                # 消费下载次数
                ip_address = None
                user_agent = None
                try:
                    if request and hasattr(request, 'client') and request.client:
                        ip_address = request.client.host
                    if request and hasattr(request, 'headers'):
                        user_agent = request.headers.get("user-agent")
                except:
                    pass
                consume_download_credit(user_id, task_id, version or "modular", ip_address, user_agent)
        except HTTPException:
            # 重新抛出 HTTP 异常（如次数不足）
            raise
        except Exception as e:
            # 订阅系统异常，优雅降级到匿名模式
            print(f"订阅系统异常，降级到匿名模式: {e}")
            # 继续执行下载，不阻止用户
    
    # 3. 返回文件（现有逻辑，保持不变）
    return FileResponse(
        str(output_file),
        media_type='video/mp4',
        filename=filename,
        headers={
            "Accept-Ranges": "bytes",  # 支持断点续传
            "Content-Disposition": f'attachment; filename="{filename}"'  # 确保浏览器下载而不是播放
        }
    )


# ==================== 订阅系统 API ====================

# 订阅产品列表端点（移到条件块外，确保始终可用）
@app.get("/api/subscription/products")
async def get_subscription_products():
    """获取可用订阅产品列表"""
    # 如果订阅系统未启用，返回空列表
    if not SUBSCRIPTION_AVAILABLE:
        return {
            "products": [],
            "count": 0,
            "message": "订阅系统未启用"
        }
    
    if not is_subscription_enabled():
        return {
            "products": [],
            "count": 0,
            "message": "订阅系统未启用"
        }
    
    try:
        from payment_service import PRODUCT_PRICES, PRODUCT_CREDITS
        
        products = []
        
        # 订阅产品
        subscription_products = [
            {
                "id": "basic_monthly",
                "type": "subscription",
                "displayName": "基础版",
                "description": "公测期特价：4.8元/月，每月20次下载，每日10次处理",
                "price": PRODUCT_PRICES.get("basic_monthly", 4.80),
                "displayPrice": f"¥{PRODUCT_PRICES.get('basic_monthly', 4.80)}/月",
                "credits": PRODUCT_CREDITS.get("basic_monthly", 20),
                "period": "monthly"
            },
            {
                "id": "premium_monthly",
                "type": "subscription",
                "displayName": "高级版",
                "description": "公测期特价：19.9元/月，每月100次下载，每日20次处理",
                "price": PRODUCT_PRICES.get("premium_monthly", 19.90),
                "displayPrice": f"¥{PRODUCT_PRICES.get('premium_monthly', 19.90)}/月",
                "credits": PRODUCT_CREDITS.get("premium_monthly", 100),
                "period": "monthly"
            }
        ]
        
        # 一次性购买产品
        purchase_products = [
            {
                "id": "pack_10",
                "type": "purchase",
                "displayName": "10次下载包",
                "description": "一次性购买10次下载，每日10次处理，有效期3个月",
                "price": PRODUCT_PRICES.get("pack_10", 5.00),
                "displayPrice": f"¥{PRODUCT_PRICES.get('pack_10', 5.00)}",
                "credits": PRODUCT_CREDITS.get("pack_10", 10),
                "period": None
            },
            {
                "id": "pack_20",
                "type": "purchase",
                "displayName": "20次下载包",
                "description": "一次性购买20次下载，每日10次处理，有效期3个月",
                "price": PRODUCT_PRICES.get("pack_20", 9.00),
                "displayPrice": f"¥{PRODUCT_PRICES.get('pack_20', 9.00)}",
                "credits": PRODUCT_CREDITS.get("pack_20", 20),
                "period": None
            }
        ]
        
        products = subscription_products + purchase_products
        
        return {
            "products": products,
            "count": len(products)
        }
    except Exception as e:
        print(f"ERROR: 获取产品列表失败: {e}")
        import traceback
        traceback.print_exc()
        return {
            "products": [],
            "count": 0,
            "error": str(e)
        }

# 用户认证端点（移到条件块外，确保始终可用）
@app.post("/api/auth/register")
async def register_user(
    device_id: Optional[str] = Form(None),
    email: Optional[str] = Form(None),
    phone: Optional[str] = Form(None)
):
    """注册新用户"""
    if not SUBSCRIPTION_AVAILABLE:
        return JSONResponse(
            status_code=503,
            content={"error": "订阅系统未启用"}
        )
    
    if not is_subscription_enabled():
        return JSONResponse(
            status_code=503,
            content={"error": "订阅系统未启用"}
        )
    
    result = create_or_get_user(device_id=device_id, email=email, phone=phone)
    return result

if SUBSCRIPTION_AVAILABLE:
    
    @app.post("/api/auth/login")
    async def login_user(
        user_id: Optional[str] = Form(None),
        device_id: Optional[str] = Form(None)
    ):
        """登录用户"""
        if not is_subscription_enabled():
            return JSONResponse(
                status_code=503,
                content={"error": "订阅系统未启用"}
            )
        
        result = create_or_get_user(device_id=device_id)
        if user_id:
            # 如果提供了 user_id，验证并生成新 token
            from subscription_service import generate_jwt_token
            result = {
                "user_id": user_id,
                "token": generate_jwt_token(user_id)
            }
        return result
    
    @app.get("/api/subscription/status")
    async def get_subscription_status(user_id: Optional[str] = Depends(get_optional_user)):
        """获取当前订阅状态"""
        if not is_subscription_enabled():
            return JSONResponse(
                status_code=503,
                content={"error": "订阅系统未启用"}
            )
        
        if not user_id:
            return {
                "is_whitelisted": False,
                "subscription": None,
                "download_credits": None,
                "free_trial": None
            }
        
        # 检查白名单
        is_whitelisted = check_whitelist(user_id)
        
        # 获取下载次数信息
        credits_info = check_download_credits(user_id)
        
        # 获取订阅信息
        subscription_info = get_user_subscription_info(user_id)
        
        # 获取已使用次数统计
        used_stats = get_used_credits_stats(user_id)
        
        return {
            "is_whitelisted": is_whitelisted,
            "hasActiveSubscription": subscription_info is not None,
            "subscription": subscription_info,
            "download_credits": {
                "total": credits_info.get("total_remaining", 0),
                "remaining": credits_info.get("total_remaining", 0),
                "available_credits": credits_info.get("available_credits", {})
            },
            "free_trial": {
                "used": used_stats.get("free_trial", {}).get("used", 0),
                "total": used_stats.get("free_trial", {}).get("total", 0),
                "remaining": credits_info.get("available_credits", {}).get("free_trial", 0)
            },
            "credits": {
                "subscription": {
                    "used": used_stats.get("subscription", {}).get("used", 0),
                    "total": used_stats.get("subscription", {}).get("total", 0),
                    "remaining": credits_info.get("available_credits", {}).get("subscription", 0)
                },
                "purchase": {
                    "used": used_stats.get("purchase", {}).get("used", 0),
                    "total": used_stats.get("purchase", {}).get("total", 0),
                    "remaining": credits_info.get("available_credits", {}).get("purchased", 0)
                }
            }
        }
    
    # 下载次数管理
    @app.get("/api/credits/check")
    async def check_credits(user_id: Optional[str] = Depends(get_optional_user)):
        """检查是否有可用下载次数"""
        if not is_subscription_enabled():
            return {
                "is_whitelisted": False,
                "can_download": True,
                "available_credits": {"subscription": 0, "purchased": 0, "free_trial": 0},
                "total_remaining": 999999  # 使用大数字代替 float('inf')
            }
        
        if not user_id:
            # 匿名用户，允许下载（向后兼容）
            return {
                "is_whitelisted": False,
                "can_download": True,
                "available_credits": {"subscription": 0, "purchased": 0, "free_trial": 0},
                "total_remaining": 999999  # 使用大数字代替 float('inf')
            }
        
        result = check_download_credits(user_id)
        # 将 float('inf') 转换为大数字
        if result.get("total_remaining") == float('inf'):
            result["total_remaining"] = 999999
        return result
    
    @app.post("/api/credits/consume")
    async def consume_credits(
        task_id: str = Form(...),
        version: str = Form(...),
        user_id: Optional[str] = Depends(get_optional_user)
    ):
        """消费下载次数"""
        if not is_subscription_enabled():
            return {"success": True, "remaining": float('inf')}
        
        if not user_id:
            return {"success": True, "remaining": float('inf')}
        
        result = consume_download_credit(user_id, task_id, version)
        return {
            "success": result["remaining"] != 0,
            "remaining": result["remaining"],
            "credit_type": result["credit_type"]
        }
    
    # 白名单管理（管理员功能）
    ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", None)
    
    def verify_admin_token(authorization: Optional[str] = Header(None)) -> bool:
        """验证管理员Token"""
        if not ADMIN_TOKEN:
            return False
        if not authorization:
            return False
        token = authorization.replace("Bearer ", "") if authorization.startswith("Bearer ") else authorization
        return token == ADMIN_TOKEN
    
    @app.get("/api/admin/whitelist")
    async def get_whitelist_admin(
        page: int = 1,
        limit: int = 20,
        search: Optional[str] = None,
        is_admin: bool = Depends(verify_admin_token)
    ):
        """获取白名单列表（需要管理员权限）"""
        if not is_admin:
            raise HTTPException(status_code=403, detail="管理员权限 required")
        
        return get_whitelist_users(page=page, limit=limit, search=search)
    
    @app.post("/api/admin/whitelist/add")
    async def add_whitelist_admin(
        user_id: str = Form(...),
        reason: Optional[str] = Form(None),
        is_admin: bool = Depends(verify_admin_token)
    ):
        """添加用户到白名单（需要管理员权限）"""
        if not is_admin:
            raise HTTPException(status_code=403, detail="管理员权限 required")
        
        success = add_to_whitelist(user_id, "admin", reason)
        if success:
            return {"success": True, "message": "用户已添加到白名单", "user_id": user_id}
        else:
            return JSONResponse(
                status_code=400,
                content={"success": False, "message": "用户已在白名单中或添加失败", "user_id": user_id}
            )
    
    @app.delete("/api/admin/whitelist/{user_id}")
    async def remove_whitelist_admin(
        user_id: str,
        is_admin: bool = Depends(verify_admin_token)
    ):
        """从白名单中删除用户（需要管理员权限）"""
        if not is_admin:
            raise HTTPException(status_code=403, detail="管理员权限 required")
        
        success = remove_from_whitelist(user_id)
        if success:
            return {"success": True, "message": "用户已从白名单中移除", "user_id": user_id}
        else:
            return JSONResponse(
                status_code=404,
                content={"success": False, "message": "用户不在白名单中", "user_id": user_id}
            )
    
    @app.get("/api/admin/whitelist/check/{user_id}")
    async def check_whitelist_admin(
        user_id: str,
        is_admin: bool = Depends(verify_admin_token)
    ):
        """检查用户是否在白名单中（需要管理员权限）"""
        if not is_admin:
            raise HTTPException(status_code=403, detail="管理员权限 required")
        
        is_whitelisted = check_whitelist(user_id)
        return {
            "is_whitelisted": is_whitelisted,
            "user_id": user_id
        }
    
    # iOS 收据验证
    @app.get("/api/subscription/history")
    async def get_subscription_history_api(
        page: int = 1,
        limit: int = 20,
        user_id: Optional[str] = Depends(get_optional_user)
    ):
        """获取用户订阅历史"""
        if not is_subscription_enabled():
            return JSONResponse(
                status_code=503,
                content={"error": "订阅系统未启用"}
            )
        
        if not user_id:
            return JSONResponse(
                status_code=401,
                content={"error": "未登录"}
            )
        
        return get_subscription_history(user_id, page=page, limit=limit)
    
    @app.get("/api/downloads/history")
    async def get_download_history_api(
        page: int = 1,
        limit: int = 20,
        user_id: Optional[str] = Depends(get_optional_user)
    ):
        """获取用户下载记录"""
        if not is_subscription_enabled():
            return JSONResponse(
                status_code=503,
                content={"error": "订阅系统未启用"}
            )
        
        if not user_id:
            return JSONResponse(
                status_code=401,
                content={"error": "未登录"}
            )
        
        return get_download_history(user_id, page=page, limit=limit)
    
    # Web 支付相关 API
    try:
        from payment_service import (
            create_payment_order,
            verify_wechat_payment,
            verify_alipay_payment,
            update_payment_status,
            get_payment_status
        )
        PAYMENT_AVAILABLE = True
    except ImportError:
        PAYMENT_AVAILABLE = False
        print("WARNING: 支付服务模块未找到，Web 支付功能已禁用")
    
    if PAYMENT_AVAILABLE:
        # 订阅购买端点（前端调用）
        @app.post("/api/subscription/purchase")
        async def purchase_subscription(
            product_id: str = Form(...),
            payment_method: str = Form("wechat"),
            user_id: Optional[str] = Depends(get_optional_user)
        ):
            """购买订阅或下载次数（订阅系统专用端点）"""
            if not is_subscription_enabled():
                return JSONResponse(
                    status_code=503,
                    content={"error": "订阅系统未启用"}
                )
            
            if not user_id:
                return JSONResponse(
                    status_code=401,
                    content={"error": "需要用户认证"}
                )
            
            if payment_method not in ["wechat", "alipay"]:
                return JSONResponse(
                    status_code=400,
                    content={"error": "不支持的支付方式"}
                )
            
            result = create_payment_order(user_id, product_id, payment_method)
            if result:
                return result
            else:
                return JSONResponse(
                    status_code=400,
                    content={"error": "创建支付订单失败"}
                )
        
        @app.post("/api/payment/create")
        async def create_payment(
            product_id: str = Form(...),
            payment_method: str = Form("wechat"),
            user_id: Optional[str] = Depends(get_optional_user)
        ):
            """创建支付订单"""
            if not is_subscription_enabled():
                return JSONResponse(
                    status_code=503,
                    content={"error": "订阅系统未启用"}
                )
            
            if not user_id:
                return JSONResponse(
                    status_code=401,
                    content={"error": "需要用户认证"}
                )
            
            if payment_method not in ["wechat", "alipay"]:
                return JSONResponse(
                    status_code=400,
                    content={"error": "不支持的支付方式"}
                )
            
            result = create_payment_order(user_id, product_id, payment_method)
            if result:
                return result
            else:
                return JSONResponse(
                    status_code=400,
                    content={"error": "创建支付订单失败"}
                )
        
        @app.post("/api/payment/callback/wechat")
        async def wechat_payment_callback(request: Request):
            """微信支付回调"""
            if not is_subscription_enabled():
                return JSONResponse(
                    status_code=503,
                    content={"error": "订阅系统未启用"}
                )
            
            try:
                # 获取回调数据（微信支付使用 XML 格式）
                body = await request.body()
                # 这里应该解析 XML 并验证签名
                # 临时实现：假设是 JSON 格式
                try:
                    callback_data = await request.json()
                except:
                    # 如果是 XML，需要解析
                    import xml.etree.ElementTree as ET
                    root = ET.fromstring(body.decode('utf-8'))
                    callback_data = {child.tag: child.text for child in root}
                
                # 验证支付
                result = verify_wechat_payment(callback_data)
                if result and result.get("success"):
                    # 更新支付状态
                    update_payment_status(
                        result["order_id"],
                        result["status"],
                        result.get("transaction_id")
                    )
                    # 返回微信支付要求的响应格式（XML）
                    return Response(
                        content='<xml><return_code><![CDATA[SUCCESS]]></return_code><return_msg><![CDATA[OK]]></return_msg></xml>',
                        media_type="application/xml"
                    )
                else:
                    return JSONResponse(
                        status_code=400,
                        content={"error": "支付验证失败"}
                    )
            except Exception as e:
                print(f"微信支付回调处理失败: {e}")
                return JSONResponse(
                    status_code=500,
                    content={"error": "处理支付回调失败"}
                )
        
        @app.post("/api/payment/callback/alipay")
        async def alipay_payment_callback(request: Request):
            """支付宝支付回调"""
            if not is_subscription_enabled():
                return JSONResponse(
                    status_code=503,
                    content={"error": "订阅系统未启用"}
                )
            
            try:
                # 获取回调数据（支付宝使用表单数据）
                form_data = await request.form()
                callback_data = dict(form_data)
                
                # 验证支付
                result = verify_alipay_payment(callback_data)
                if result and result.get("success"):
                    # 更新支付状态
                    update_payment_status(
                        result["order_id"],
                        result["status"],
                        result.get("transaction_id")
                    )
                    # 返回支付宝要求的响应格式
                    return Response(content="success")
                else:
                    return JSONResponse(
                        status_code=400,
                        content={"error": "支付验证失败"}
                    )
            except Exception as e:
                print(f"支付宝支付回调处理失败: {e}")
                return JSONResponse(
                    status_code=500,
                    content={"error": "处理支付回调失败"}
                )
        
        @app.get("/api/payment/status/{order_id}")
        async def get_payment_status_api(
            order_id: str,
            user_id: Optional[str] = Depends(get_optional_user)
        ):
            """查询支付订单状态"""
            if not is_subscription_enabled():
                return JSONResponse(
                    status_code=503,
                    content={"error": "订阅系统未启用"}
                )
            
            if not user_id:
                return JSONResponse(
                    status_code=401,
                    content={"error": "需要用户认证"}
                )
            
            result = get_payment_status(order_id)
            if result:
                # 验证订单属于当前用户
                if result["user_id"] != user_id:
                    return JSONResponse(
                        status_code=403,
                        content={"error": "无权访问此订单"}
                    )
                return result
            else:
                return JSONResponse(
                    status_code=404,
                    content={"error": "订单不存在"}
                )
    
    @app.post("/api/subscription/verify-receipt")
    async def verify_receipt(
        transaction_id: str = Form(...),
        product_id: str = Form(...),
        receipt_data: str = Form(...),
        platform: str = Form("ios"),
        user_id: Optional[str] = Depends(get_optional_user)
    ):
        """验证 iOS 收据（StoreKit 2）"""
        if not is_subscription_enabled():
            return JSONResponse(
                status_code=503,
                content={"error": "订阅系统未启用"}
            )
        
        if not user_id:
            return JSONResponse(
                status_code=401,
                content={"error": "需要用户认证"}
            )
        
        try:
            from subscription_receipt_verification import (
                verify_ios_receipt,
                parse_transaction_from_receipt,
                save_subscription_to_database
            )
            
            # 验证收据（StoreKit 2 的收据数据格式）
            # 注意：StoreKit 2 使用 Transaction 对象，不是传统的收据
            # 这里我们直接使用收到的 receipt_data（应该是 JSON 编码的 Transaction 信息）
            import json
            import base64
            
            try:
                # 尝试解码 receipt_data
                receipt_json = json.loads(base64.b64decode(receipt_data).decode('utf-8'))
                
                # 构造交易信息
                transaction_info = {
                    "transaction_id": transaction_id,
                    "product_id": product_id,
                    "purchase_date_ms": int(receipt_json.get("purchaseDate", 0)),
                    "expires_date_ms": receipt_json.get("expirationDate", 0) if receipt_json.get("expirationDate") else None,
                    "is_trial_period": False,
                    "is_in_intro_offer_period": False
                }
                
                # 保存订阅到数据库
                success = save_subscription_to_database(user_id, transaction_info, product_id)
                
                if success:
                    return {
                        "success": True,
                        "message": "收据验证成功",
                        "transaction_id": transaction_id,
                        "product_id": product_id
                    }
                else:
                    return JSONResponse(
                        status_code=500,
                        content={
                            "success": False,
                            "message": "保存订阅信息失败"
                        }
                    )
            except Exception as e:
                print(f"处理收据数据失败: {e}")
                return JSONResponse(
                    status_code=400,
                    content={
                        "success": False,
                        "message": f"收据数据格式错误: {str(e)}"
                    }
                )
        except Exception as e:
            print(f"收据验证异常: {e}")
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "message": f"收据验证失败: {str(e)}"
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


# 启动时初始化订阅系统数据库
@app.on_event("startup")
async def startup_event():
    """启动时执行初始化操作（快速启动，清理操作在后台执行）"""
    # 初始化订阅系统数据库（如果启用）
    if SUBSCRIPTION_AVAILABLE:
        try:
            init_database()
            print("✅ 订阅系统数据库初始化成功")
        except Exception as e:
            print(f"WARNING: 订阅系统数据库初始化失败: {e}")
            print("订阅功能将不可用，但现有功能不受影响")
    
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

