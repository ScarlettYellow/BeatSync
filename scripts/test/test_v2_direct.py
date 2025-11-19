#!/usr/bin/env python3
"""
直接测试V2版本，查看具体错误信息
"""

import os
import sys
import subprocess
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

def test_v2_direct():
    """直接运行V2版本，查看错误"""
    
    # 使用最近一次测试的文件
    upload_dir = project_root / "outputs" / "web_uploads"
    
    # 查找最新的dance和bgm文件
    dance_files = list(upload_dir.glob("*_dance.*"))
    bgm_files = list(upload_dir.glob("*_bgm.*"))
    
    if not dance_files or not bgm_files:
        print("❌ 未找到测试文件")
        print(f"请确保 {upload_dir} 目录中有上传的文件")
        return
    
    dance_video = dance_files[0]
    bgm_video = bgm_files[0]
    
    print("=" * 60)
    print("V2版本直接测试")
    print("=" * 60)
    print(f"输入文件:")
    print(f"  dance: {dance_video}")
    print(f"  bgm: {bgm_video}")
    print()
    
    # 创建输出目录
    output_dir = project_root / "outputs" / "test_v2_direct"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_video = output_dir / "test_v2_output.mp4"
    
    print(f"输出文件: {output_video}")
    print()
    
    # 构建命令（与并行处理器中使用的相同）
    v2_script = project_root / "beatsync_badcase_fix_trim_v2.py"
    
    if not v2_script.exists():
        print(f"❌ V2脚本不存在: {v2_script}")
        return
    
    cmd = [
        "python3", str(v2_script),
        "--dance", str(dance_video),
        "--bgm", str(bgm_video),
        "--output", str(output_video),
        "--fast-video",
        "--video-encode", "x264_fast",
        "--enable-cache",
        "--cache-dir", ".beatsync_cache",
        "--threads", "4",
        "--lib-threads", "1"
    ]
    
    print("执行命令:")
    print(" ".join(cmd))
    print()
    print("=" * 60)
    print("开始执行...")
    print("=" * 60)
    print()
    
    # 执行命令，实时输出
    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True,
            cwd=str(project_root)
        )
        
        # 实时输出stdout和stderr
        import select
        import threading
        
        def read_output(pipe, label):
            for line in iter(pipe.readline, ''):
                if line:
                    print(f"[{label}] {line.rstrip()}")
            pipe.close()
        
        stdout_thread = threading.Thread(target=read_output, args=(process.stdout, "STDOUT"))
        stderr_thread = threading.Thread(target=read_output, args=(process.stderr, "STDERR"))
        
        stdout_thread.start()
        stderr_thread.start()
        
        # 等待进程完成
        return_code = process.wait()
        
        stdout_thread.join()
        stderr_thread.join()
        
        print()
        print("=" * 60)
        print(f"执行完成，返回码: {return_code}")
        print("=" * 60)
        
        if return_code == 0:
            if output_video.exists() and output_video.stat().st_size > 0:
                print(f"✅ 成功！输出文件: {output_video}")
                print(f"   文件大小: {output_video.stat().st_size / 1024 / 1024:.2f} MB")
            else:
                print(f"⚠️  返回码为0，但输出文件不存在或为空")
        else:
            print(f"❌ 失败，返回码: {return_code}")
            print()
            print("可能的原因:")
            print("1. 脚本参数错误")
            print("2. 文件路径问题")
            print("3. 依赖缺失")
            print("4. 脚本本身有错误")
            print()
            print("请查看上方的STDERR输出，查找具体错误信息")
        
    except Exception as e:
        print(f"❌ 执行异常: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_v2_direct()

