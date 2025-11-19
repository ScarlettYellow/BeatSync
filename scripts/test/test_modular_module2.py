#!/usr/bin/env python3
"""
测试modular版本的模块2（裁剪模块），诊断为什么失败
"""

import os
import sys
import subprocess
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

def test_modular_module2():
    """测试modular版本的模块2"""
    
    # 使用最近一次测试的文件
    upload_dir = project_root / "outputs" / "web_uploads"
    
    # 查找最新的dance和bgm文件
    dance_files = list(upload_dir.glob("*_dance.*"))
    bgm_files = list(upload_dir.glob("*_bgm.*"))
    
    if not dance_files or not bgm_files:
        print("❌ 未找到测试文件")
        return
    
    dance_video = dance_files[0]
    bgm_video = bgm_files[0]
    
    print("=" * 60)
    print("Modular版本模块2诊断测试")
    print("=" * 60)
    print(f"输入文件:")
    print(f"  dance: {dance_video}")
    print(f"  bgm: {bgm_video}")
    print()
    
    # 创建输出目录
    output_dir = project_root / "outputs" / "test_modular_module2"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_video = output_dir / "test_modular_final.mp4"
    
    print(f"输出文件: {output_video}")
    print()
    
    # 构建命令
    modular_script = project_root / "beatsync_fine_cut_modular.py"
    
    if not modular_script.exists():
        print(f"❌ Modular脚本不存在: {modular_script}")
        return
    
    cmd = [
        "python3", str(modular_script),
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
        
        # 检查输出文件
        final_output = output_video
        intermediate_output = output_dir / f"{output_video.stem}_module1_aligned.mp4"
        
        print()
        print("检查输出文件:")
        if final_output.exists():
            print(f"  ✅ 最终输出文件存在: {final_output}")
            print(f"     文件大小: {final_output.stat().st_size / 1024 / 1024:.2f} MB")
        else:
            print(f"  ❌ 最终输出文件不存在: {final_output}")
        
        if intermediate_output.exists():
            print(f"  ⚠️  中间文件存在: {intermediate_output}")
            print(f"     文件大小: {intermediate_output.stat().st_size / 1024 / 1024:.2f} MB")
            print(f"  ⚠️  这表示模块2（裁剪模块）失败")
        
        if return_code == 0 and final_output.exists():
            print()
            print("✅ 成功！模块2正常工作")
        elif intermediate_output.exists():
            print()
            print("❌ 失败：只生成了中间文件，模块2失败")
            print("   可能的原因：")
            print("   1. 裁剪模块的ffmpeg命令失败")
            print("   2. 视频编码失败")
            print("   3. 文件路径问题")
            print("   4. 权限问题")
        else:
            print()
            print("❌ 失败：未生成任何输出文件")
        
    except Exception as e:
        print(f"❌ 执行异常: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_modular_module2()

