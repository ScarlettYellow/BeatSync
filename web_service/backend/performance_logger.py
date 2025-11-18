#!/usr/bin/env python3
"""
性能日志记录模块
用于记录处理过程中的详细性能指标
"""

import time
import logging
import psutil
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional
from contextlib import contextmanager

# 配置日志
LOG_DIR = Path(__file__).parent.parent.parent / "outputs" / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

# 创建性能日志记录器
perf_logger = logging.getLogger("performance")
perf_logger.setLevel(logging.INFO)

# 创建文件处理器（按日期分割）
log_file = LOG_DIR / f"performance_{datetime.now().strftime('%Y%m%d')}.log"
file_handler = logging.FileHandler(log_file, encoding='utf-8')
file_handler.setLevel(logging.INFO)

# 创建格式器
formatter = logging.Formatter(
    '%(asctime)s | %(levelname)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
file_handler.setFormatter(formatter)
perf_logger.addHandler(file_handler)

# 同时输出到控制台
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)
perf_logger.addHandler(console_handler)


class PerformanceLogger:
    """性能日志记录器"""
    
    def __init__(self, task_id: str, operation: str):
        self.task_id = task_id
        self.operation = operation
        self.start_time = None
        self.steps: Dict[str, float] = {}
        self.resources: Dict[str, list] = {
            'cpu_percent': [],
            'memory_mb': [],
            'disk_io_read_mb': [],
            'disk_io_write_mb': []
        }
    
    def start(self):
        """开始记录"""
        self.start_time = time.time()
        self._log_resource_usage("START")
        perf_logger.info(f"[{self.task_id}] [{self.operation}] 开始处理")
    
    def log_step(self, step_name: str, duration: Optional[float] = None):
        """记录步骤耗时"""
        if duration is None:
            duration = time.time() - (self.start_time or time.time())
        self.steps[step_name] = duration
        self._log_resource_usage(step_name)
        perf_logger.info(
            f"[{self.task_id}] [{self.operation}] 步骤: {step_name} | "
            f"耗时: {duration:.2f}秒"
        )
    
    def log_subprocess(self, cmd_name: str, duration: float, return_code: int, 
                      stdout_size: int = 0, stderr_size: int = 0):
        """记录子进程执行信息"""
        self._log_resource_usage(f"SUBPROCESS_{cmd_name}")
        perf_logger.info(
            f"[{self.task_id}] [{self.operation}] 子进程: {cmd_name} | "
            f"耗时: {duration:.2f}秒 | 返回码: {return_code} | "
            f"stdout: {stdout_size}字节 | stderr: {stderr_size}字节"
        )
    
    def log_file_operation(self, operation: str, file_path: str, 
                          file_size: Optional[int] = None, duration: Optional[float] = None):
        """记录文件操作"""
        size_str = f" | 大小: {file_size / 1024 / 1024:.2f}MB" if file_size else ""
        duration_str = f" | 耗时: {duration:.2f}秒" if duration else ""
        perf_logger.info(
            f"[{self.task_id}] [{self.operation}] 文件操作: {operation} | "
            f"路径: {file_path}{size_str}{duration_str}"
        )
    
    def log_error(self, error_msg: str, error_type: str = "ERROR"):
        """记录错误"""
        perf_logger.error(
            f"[{self.task_id}] [{self.operation}] {error_type}: {error_msg}"
        )
    
    def finish(self, success: bool = True, error_msg: Optional[str] = None):
        """结束记录，输出总结"""
        total_duration = time.time() - (self.start_time or time.time())
        self._log_resource_usage("FINISH")
        
        # 计算资源使用统计
        avg_cpu = sum(self.resources['cpu_percent']) / len(self.resources['cpu_percent']) if self.resources['cpu_percent'] else 0
        max_memory = max(self.resources['memory_mb']) if self.resources['memory_mb'] else 0
        avg_memory = sum(self.resources['memory_mb']) / len(self.resources['memory_mb']) if self.resources['memory_mb'] else 0
        
        status = "成功" if success else "失败"
        perf_logger.info(
            f"[{self.task_id}] [{self.operation}] ========== 处理完成 =========="
        )
        perf_logger.info(
            f"[{self.task_id}] [{self.operation}] 状态: {status} | "
            f"总耗时: {total_duration:.2f}秒"
        )
        
        # 输出各步骤耗时
        if self.steps:
            perf_logger.info(
                f"[{self.task_id}] [{self.operation}] 步骤耗时明细:"
            )
            for step_name, step_duration in sorted(self.steps.items(), key=lambda x: x[1], reverse=True):
                percentage = (step_duration / total_duration * 100) if total_duration > 0 else 0
                perf_logger.info(
                    f"[{self.task_id}] [{self.operation}]   - {step_name}: "
                    f"{step_duration:.2f}秒 ({percentage:.1f}%)"
                )
        
        # 输出资源使用
        perf_logger.info(
            f"[{self.task_id}] [{self.operation}] 资源使用: "
            f"平均CPU: {avg_cpu:.1f}% | "
            f"最大内存: {max_memory:.1f}MB | "
            f"平均内存: {avg_memory:.1f}MB"
        )
        
        if error_msg:
            perf_logger.error(
                f"[{self.task_id}] [{self.operation}] 错误信息: {error_msg}"
            )
        
        perf_logger.info(
            f"[{self.task_id}] [{self.operation}] =============================="
        )
    
    def _log_resource_usage(self, step: str):
        """记录资源使用情况"""
        try:
            process = psutil.Process(os.getpid())
            cpu_percent = process.cpu_percent(interval=0.1)
            memory_info = process.memory_info()
            memory_mb = memory_info.rss / 1024 / 1024
            
            # 磁盘I/O（需要累计）
            io_counters = process.io_counters()
            disk_read_mb = io_counters.read_bytes / 1024 / 1024
            disk_write_mb = io_counters.write_bytes / 1024 / 1024
            
            self.resources['cpu_percent'].append(cpu_percent)
            self.resources['memory_mb'].append(memory_mb)
            self.resources['disk_io_read_mb'].append(disk_read_mb)
            self.resources['disk_io_write_mb'].append(disk_write_mb)
            
            perf_logger.debug(
                f"[{self.task_id}] [{self.operation}] 资源 [{step}]: "
                f"CPU: {cpu_percent:.1f}% | "
                f"内存: {memory_mb:.1f}MB | "
                f"磁盘读: {disk_read_mb:.2f}MB | "
                f"磁盘写: {disk_write_mb:.2f}MB"
            )
        except Exception as e:
            # 如果无法获取资源信息，静默失败
            pass
    
    @contextmanager
    def step_context(self, step_name: str):
        """上下文管理器，自动记录步骤耗时"""
        step_start = time.time()
        try:
            yield
        finally:
            duration = time.time() - step_start
            self.log_step(step_name, duration)


# 全局函数，方便使用
def create_logger(task_id: str, operation: str) -> PerformanceLogger:
    """创建性能日志记录器"""
    return PerformanceLogger(task_id, operation)

