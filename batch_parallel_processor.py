#!/usr/bin/env python3
"""
批量并行处理器
使用并行处理器处理多个测试样本
"""

import os
import subprocess
import sys
from datetime import datetime

def process_all_samples_parallel():
    """批量并行处理所有测试样本"""
    input_dir = "input_allcases_lowp"
    output_dir = "parallel_processing_outputs"
    
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    # 获取所有测试样本
    samples = []
    for item in os.listdir(input_dir):
        item_path = os.path.join(input_dir, item)
        if os.path.isdir(item_path):
            dance_path = os.path.join(item_path, "dance.mp4")
            bgm_path = os.path.join(item_path, "bgm.mp4")
            if os.path.exists(dance_path) and os.path.exists(bgm_path):
                samples.append(item)
    
    print(f"BeatSync 批量并行处理器")
    print("=" * 60)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"找到 {len(samples)} 个测试样本")
    print(f"输出目录: {output_dir}")
    print("=" * 60)
    
    # 处理每个样本
    success_count = 0
    total_count = len(samples)
    
    for i, sample in enumerate(samples, 1):
        print(f"\n[{i}/{total_count}] 处理样本: {sample}")
        print("-" * 50)
        
        dance_video = os.path.join(input_dir, sample, "dance.mp4")
        bgm_video = os.path.join(input_dir, sample, "bgm.mp4")
        
        # 运行并行处理器
        cmd = [
            "python3", "beatsync_parallel_processor.py",
            "--dance", dance_video,
            "--bgm", bgm_video,
            "--output-dir", output_dir,
            "--sample-name", sample
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
            
            if result.returncode == 0:
                print(f"✅ {sample} 处理成功")
                success_count += 1
            else:
                print(f"❌ {sample} 处理失败")
                print(f"错误信息: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            print(f"⏰ {sample} 处理超时")
        except Exception as e:
            print(f"❌ {sample} 处理异常: {e}")
    
    # 生成汇总报告
    print("\n" + "=" * 60)
    print("生成汇总报告...")
    
    summary_report = os.path.join(output_dir, "batch_processing_summary.txt")
    with open(summary_report, 'w', encoding='utf-8') as f:
        f.write("BeatSync 批量并行处理汇总报告\n")
        f.write("=" * 60 + "\n")
        f.write(f"处理时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"总样本数: {total_count}\n")
        f.write(f"成功处理: {success_count}\n")
        f.write(f"失败处理: {total_count - success_count}\n")
        f.write(f"成功率: {success_count/total_count*100:.1f}%\n")
        f.write("=" * 60 + "\n\n")
        
        f.write("处理结果:\n")
        f.write("-" * 30 + "\n")
        f.write(f"✅ 成功: {success_count} 个样本\n")
        f.write(f"❌ 失败: {total_count - success_count} 个样本\n")
        f.write(f"📁 输出目录: {output_dir}\n")
        f.write(f"📋 每个样本都有独立的对比报告\n")
        f.write(f"🎬 每个样本都有两个输出视频供选择\n")
        
        f.write("\n使用说明:\n")
        f.write("-" * 30 + "\n")
        f.write("1. 查看每个样本的对比报告了解处理详情\n")
        f.write("2. 观看两个输出视频（modular版本和V2版本）\n")
        f.write("3. 选择对齐效果更好的版本作为最终结果\n")
        f.write("4. 删除不需要的输出视频以节省空间\n")
    
    print(f"✅ 汇总报告已生成: {summary_report}")
    print(f"✅ 批量处理完成！")
    print(f"📁 所有输出文件保存在: {output_dir}/")
    print(f"📊 处理统计: {success_count}/{total_count} 成功")

def process_specific_samples():
    """处理指定的测试样本"""
    # 指定要处理的样本
    target_samples = [
        "killitgirl_full",
        "sweetjuice_full", 
        "likethat_full",
        "fallingout_shorterbegin",
        "kissandmakeup_shorterbegin",
        "waitonme_shorterbegin",
        "liangnan_shorterbegin",
        "nobody_shorterbegin"
    ]
    
    input_dir = "input_allcases_lowp"
    output_dir = "parallel_processing_specific"
    
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"BeatSync 指定样本并行处理器")
    print("=" * 60)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"目标样本数: {len(target_samples)}")
    print(f"输出目录: {output_dir}")
    print("=" * 60)
    
    # 处理每个样本
    success_count = 0
    total_count = len(target_samples)
    
    for i, sample in enumerate(target_samples, 1):
        print(f"\n[{i}/{total_count}] 处理样本: {sample}")
        print("-" * 50)
        
        dance_video = os.path.join(input_dir, sample, "dance.mp4")
        bgm_video = os.path.join(input_dir, sample, "bgm.mp4")
        
        # 检查样本是否存在
        if not os.path.exists(dance_video) or not os.path.exists(bgm_video):
            print(f"❌ 样本 {sample} 文件不存在，跳过")
            continue
        
        # 运行并行处理器
        cmd = [
            "python3", "beatsync_parallel_processor.py",
            "--dance", dance_video,
            "--bgm", bgm_video,
            "--output-dir", output_dir,
            "--sample-name", sample
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
            
            if result.returncode == 0:
                print(f"✅ {sample} 处理成功")
                success_count += 1
            else:
                print(f"❌ {sample} 处理失败")
                print(f"错误信息: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            print(f"⏰ {sample} 处理超时")
        except Exception as e:
            print(f"❌ {sample} 处理异常: {e}")
    
    print(f"\n✅ 指定样本处理完成！")
    print(f"📁 输出文件保存在: {output_dir}/")
    print(f"📊 处理统计: {success_count}/{total_count} 成功")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--specific":
        process_specific_samples()
    else:
        process_all_samples_parallel()
