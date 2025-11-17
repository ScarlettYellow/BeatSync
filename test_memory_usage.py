#!/usr/bin/env python3
"""
内存使用测试脚本
运行并行处理器并监控内存使用
"""

import subprocess
import time
import psutil
import os
import sys

def get_memory_usage_mb():
    """获取当前进程的内存使用（MB）"""
    try:
        process = psutil.Process()
        return process.memory_info().rss / 1024 / 1024
    except:
        return 0.0

def monitor_memory_during_processing():
    """在处理过程中监控内存使用"""
    print("=" * 60)
    print("内存使用监控测试")
    print("=" * 60)
    
    # 检查输入文件
    dance_video = "input_allcases_lowp/killitgirl_full/dance.mp4"
    bgm_video = "input_allcases_lowp/killitgirl_full/bgm.mp4"
    
    if not os.path.exists(dance_video):
        print(f"错误: 找不到dance视频: {dance_video}")
        return
    
    if not os.path.exists(bgm_video):
        print(f"错误: 找不到bgm视频: {bgm_video}")
        return
    
    output_dir = "test_memory_verification"
    sample_name = "killitgirl_memory_test"
    
    print(f"\n测试样本: {sample_name}")
    print(f"输入文件:")
    print(f"  dance: {dance_video}")
    print(f"  bgm: {bgm_video}")
    print(f"输出目录: {output_dir}")
    print("-" * 60)
    
    # 记录初始内存
    initial_memory = get_memory_usage_mb()
    print(f"\n初始内存使用: {initial_memory:.2f} MB")
    
    # 运行并行处理器
    print("\n开始运行并行处理器...")
    print("时间戳 | 内存使用(MB) | 内存使用(GB)")
    print("-" * 60)
    
    start_time = time.time()
    
    try:
        cmd = [
            "python3", "beatsync_parallel_processor.py",
            "--dance", dance_video,
            "--bgm", bgm_video,
            "--output-dir", output_dir,
            "--sample-name", sample_name
        ]
        
        # 启动进程
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        
        # 监控内存
        max_memory = initial_memory
        check_count = 0
        
        while process.poll() is None:
            current_memory = get_memory_usage_mb()
            max_memory = max(max_memory, current_memory)
            check_count += 1
            
            if check_count % 5 == 0:  # 每5次检查打印一次
                timestamp = time.strftime('%H:%M:%S')
                memory_gb = current_memory / 1024
                print(f"{timestamp} | {current_memory:10.2f} MB | {memory_gb:8.2f} GB")
            
            time.sleep(1)
        
        # 等待进程完成
        stdout, _ = process.communicate()
        
        # 最终内存
        final_memory = get_memory_usage_mb()
        elapsed_time = time.time() - start_time
        
        print("-" * 60)
        print(f"\n处理完成!")
        print(f"处理时间: {elapsed_time:.1f} 秒")
        print(f"初始内存: {initial_memory:.2f} MB ({initial_memory/1024:.2f} GB)")
        print(f"峰值内存: {max_memory:.2f} MB ({max_memory/1024:.2f} GB)")
        print(f"最终内存: {final_memory:.2f} MB ({final_memory/1024:.2f} GB)")
        print(f"内存增长: {max_memory - initial_memory:.2f} MB ({(max_memory - initial_memory)/1024:.2f} GB)")
        
        if max_memory > 10240:  # 超过10GB
            print(f"\n⚠️  警告: 峰值内存超过10GB，可能仍有内存问题")
        elif max_memory > 5120:  # 超过5GB
            print(f"\n⚠️  注意: 峰值内存超过5GB，但比之前的20GB+已有改善")
        else:
            print(f"\n✅ 内存使用正常: 峰值内存 {max_memory/1024:.2f} GB")
        
        # 显示部分输出
        if stdout:
            print("\n程序输出（最后50行）:")
            print("-" * 60)
            lines = stdout.split('\n')
            for line in lines[-50:]:
                if line.strip():
                    print(line)
        
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    try:
        import psutil
    except ImportError:
        print("错误: 需要安装psutil库")
        print("请运行: pip3 install psutil")
        sys.exit(1)
    
    monitor_memory_during_processing()



