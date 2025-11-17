#!/usr/bin/env python3
"""
BeatSync Badcase修复（裁剪版本）- 快速对齐版（副本）
不修改原程序：使用“粗到细”二维搜索，加速并降低内存压力。
流程：
1) 提取音频到临时目录（单声道，sr=22050）
2) 粗扫（步长0.5s，最大偏移按音频长度比例限制）
3) 细化（在粗扫最佳附近±1s范围，步长0.1s）
4) 根据对齐点判定badcase类型，调用原程序的裁剪合成函数
"""

import os
import sys
import argparse
import tempfile
import shutil
import numpy as np
import soundfile as sf
import librosa
from typing import Tuple

# 复用原程序中的工具与最终合成逻辑
from beatsync_badcase_fix_trim_v2 import (
    extract_audio_from_video,
    detect_badcase_type,
    create_trimmed_video,
)


def corr(ref_seg: np.ndarray, mov_seg: np.ndarray) -> float:
    """简化的归一化互相关（与原逻辑一致性足够用于搜索）"""
    m = min(len(ref_seg), len(mov_seg))
    if m <= 0:
        return 0.0
    a = ref_seg[:m]
    b = mov_seg[:m]
    a = a - np.mean(a)
    b = b - np.mean(b)
    denom = np.sqrt(np.sum(a * a) * np.sum(b * b)) + 1e-12
    if denom == 0:
        return 0.0
    return float(np.sum(a * b) / denom)


def coarse_to_fine_find_alignment(
    ref_audio: np.ndarray,
    mov_audio: np.ndarray,
    sr: int,
    window_sec: float = 2.0,
    coarse_step_sec: float = 0.5,
    fine_step_sec: float = 0.1,
    refine_radius_sec: float = 1.0,
    topk: int = 5,
) -> Tuple[int, int, float]:
    """二维粗到细搜索（Top-K 候选细化 + 兜底），返回 (ref_start, mov_start, best_score)"""
    window = int(window_sec * sr)
    audio_dur_sec = min(len(ref_audio), len(mov_audio)) / sr
    # 动态最大偏移：最长40%或不超过30秒
    max_offset_sec = min(audio_dur_sec * 0.4, 30.0)

    print(f"粗扫阶段: 步长={coarse_step_sec:.2f}s, 窗口={window_sec:.1f}s, 最大偏移={max_offset_sec:.1f}s")

    best = (0, 0, 0.0)
    # 保存Top-K候选 (score, rs, ms)
    top_candidates: list[Tuple[float, int, int]] = []
    # 粗扫
    ref_grid = np.arange(0, max_offset_sec, coarse_step_sec)
    mov_grid = np.arange(0, max_offset_sec, coarse_step_sec)
    total_steps = len(ref_grid) * len(mov_grid)
    step = 0
    for ref_t in ref_grid:
        rs = int(ref_t * sr)
        re = rs + window
        if re > len(ref_audio):
            continue
        ref_seg = ref_audio[rs:re]
        for mov_t in mov_grid:
            ms = int(mov_t * sr)
            me = ms + window
            if me > len(mov_audio):
                continue
            mov_seg = mov_audio[ms:me]
            score = corr(ref_seg, mov_seg)
            if score > best[2]:
                best = (rs, ms, score)
            # 维护Top-K
            top_candidates.append((score, rs, ms))
            if len(top_candidates) > topk * 4:  # 暂存更大池，后续截断
                top_candidates.sort(reverse=True)
                top_candidates = top_candidates[:topk * 2]
            step += 1
        if step % 200 == 0:
            print(f"  粗扫进度: {step}/{total_steps} ({step/total_steps*100:.1f}%)  当前最佳={best[2]:.4f}")

    # 截断Top-K候选
    top_candidates.sort(reverse=True)
    top_candidates = top_candidates[:max(1, topk)]

    # 额外加入一条“bgm=0”先验候选（处理如 fallingout 的常见情形）
    zero_bgm_rs = None
    best_zero = (0.0, 0, 0)
    for ref_t in np.arange(0, max_offset_sec, coarse_step_sec):
        rs = int(ref_t * sr)
        re = rs + window
        if re > len(ref_audio):
            break
        score = corr(ref_audio[rs:re], mov_audio[0:window])
        if score > best_zero[0]:
            best_zero = (score, rs, 0)
    # 将bgm=0候选加入队列
    top_candidates.append((best_zero[0], best_zero[1], best_zero[2]))
    top_candidates.sort(reverse=True)
    top_candidates = top_candidates[:max(1, topk)]

    # 细化
    print(f"细化阶段: 步长={fine_step_sec:.2f}s, 半径={refine_radius_sec:.1f}s")
    refined_best = best
    for score0, rs0, ms0 in top_candidates:
        ref_center = rs0 / sr
        mov_center = ms0 / sr
        ref_range = np.arange(
            max(0.0, ref_center - refine_radius_sec),
            min(max_offset_sec, ref_center + refine_radius_sec) + 1e-9,
            fine_step_sec,
        )
        mov_range = np.arange(
            max(0.0, mov_center - refine_radius_sec),
            min(max_offset_sec, mov_center + refine_radius_sec) + 1e-9,
            fine_step_sec,
        )
        for ref_t in ref_range:
            rs = int(ref_t * sr)
            re = rs + window
            if re > len(ref_audio):
                continue
            ref_seg = ref_audio[rs:re]
            for mov_t in mov_range:
                ms = int(mov_t * sr)
                me = ms + window
                if me > len(mov_audio):
                    continue
                mov_seg = mov_audio[ms:me]
                score = corr(ref_seg, mov_seg)
                if score > refined_best[2]:
                    refined_best = (rs, ms, score)

    # 兜底：如果细化后的分数仍不高，执行一次“单维精扫”（保持bgm=0或保持dance=0的两条线）
    best_fallback = refined_best
    if refined_best[2] < 0.2:
        print("细化得分偏低，执行兜底线性精扫...")
        # 扫描bgm=0线
        for ref_t in np.arange(0, max_offset_sec, fine_step_sec):
            rs = int(ref_t * sr)
            re = rs + window
            if re > len(ref_audio):
                break
            score = corr(ref_audio[rs:re], mov_audio[0:window])
            if score > best_fallback[2]:
                best_fallback = (rs, 0, score)
        # 扫描dance=0线
        for mov_t in np.arange(0, max_offset_sec, fine_step_sec):
            ms = int(mov_t * sr)
            me = ms + window
            if me > len(mov_audio):
                break
            score = corr(ref_audio[0:window], mov_audio[ms:me])
            if score > best_fallback[2]:
                best_fallback = (0, ms, score)
        refined_best = best_fallback
    print(f"搜索完成: dance={refined_best[0]/sr:.2f}s, bgm={refined_best[1]/sr:.2f}s, score={refined_best[2]:.4f}")
    return refined_best


def process_fast_v2(dance_video: str, bgm_video: str, output_video: str, sr: int = 22050) -> bool:
    print("BeatSync Badcase修复（快速对齐版）开始处理...")
    print(f"  dance: {dance_video}")
    print(f"  bgm:   {bgm_video}")
    print(f"  输出:  {output_video}")

    temp_dir = tempfile.mkdtemp()
    print(f"临时目录: {temp_dir}")
    try:
        # 提取音频（单声道，sr=22050）
        dance_audio_path = os.path.join(temp_dir, "dance.wav")
        bgm_audio_path = os.path.join(temp_dir, "bgm.wav")
        if not extract_audio_from_video(dance_video, dance_audio_path, sr):
            print("dance音频提取失败")
            return False
        if not extract_audio_from_video(bgm_video, bgm_audio_path, sr):
            print("bgm音频提取失败")
            return False

        dance_audio, _ = sf.read(dance_audio_path)
        bgm_audio, _ = sf.read(bgm_audio_path)
        print(f"音频长度: dance={len(dance_audio)/sr:.2f}s, bgm={len(bgm_audio)/sr:.2f}s")

        # 转单声道（若有需要）
        if dance_audio.ndim > 1:
            dance_audio = librosa.to_mono(dance_audio.T)
        if bgm_audio.ndim > 1:
            bgm_audio = librosa.to_mono(bgm_audio.T)

        # 粗到细对齐
        ref_start, mov_start, score = coarse_to_fine_find_alignment(dance_audio, bgm_audio, sr)

        # 判定badcase
        badcase_type, gap_duration = detect_badcase_type(ref_start, mov_start, sr)

        # 合成输出（调用原程序的裁剪合成逻辑）
        if badcase_type != "NORMAL":
            print("检测到badcase，使用裁剪方法修复...")
            success = create_trimmed_video(dance_video, bgm_video, output_video, badcase_type, gap_duration)
        else:
            print("不是badcase，直接合成...")
            success = create_trimmed_video(dance_video, bgm_video, output_video, badcase_type, 0)

        print("完成!" if success else "失败!")
        return success
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)
        print("临时文件已清理")


def main():
    parser = argparse.ArgumentParser(description="BeatSync Badcase修复（快速对齐版，副本）")
    parser.add_argument("--dance", required=True, help="Dance视频路径")
    parser.add_argument("--bgm", required=True, help="BGM视频路径")
    parser.add_argument("--output", required=True, help="输出视频路径")
    args = parser.parse_args()
    ok = process_fast_v2(args.dance, args.bgm, args.output)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()


