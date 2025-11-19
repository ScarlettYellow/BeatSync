BeatSync 会话移交流 | SESSION_HANDOVER

更新时间：以当前提交为准

一、目的
- 在新聊天窗口无缝继承 BeatSync 的工程上下文，并以“非沙箱、前台、逐行流式日志”执行命令与调试。

二、当前关键状态
- 工程路径：/Users/scarlett/Projects/BeatSync
- 待办（Pending）：v2_fallingout_consistency — 排查 V2 对 fallingout 与定稿版结果不一致的原因并修复（影响较小，暂缓但保留追踪）。
- 最近验证（V2, waitonme）：
  - 日志：test_memory_verification/waitonme_v2.log
  - 结果：trailing 有声无画面检测阶段解析异常（could not convert string to float: ''），未产出最终视频。

三、日志与输出目录
- 并行处理历史：parallel_processing_outputs/
- 最近验证：test_memory_verification/
  - fallingout：fallingout_v2_22k.log、fallingout_v2_lowercase.log、fallingout_v2_fast_refine.log（若存在）
  - waitonme：waitonme_v2.log
- 批处理（若使用批处理脚本）：v2_batch_outputs/
- Numba 缓存：.numba_cache/

四、可直接复用的命令模板（前台 + 行缓冲回显）
- 初始化环境
```bash
cd /Users/scarlett/Projects/BeatSync
export NUMBA_CACHE_DIR="$(pwd)/.numba_cache"; mkdir -p "$NUMBA_CACHE_DIR" test_memory_verification
```

- 运行 V2（示例：waitonme，自动兼容大小写与两种目录名）
```bash
SAMPLE_DIR="input_allcases_lowp/waitonme_shorterbegin"; [ -d "$SAMPLE_DIR" ] || SAMPLE_DIR="input_allcases_lowp/waitonme";
DANCE="$SAMPLE_DIR/dance.MP4"; [ -f "$DANCE" ] || DANCE="$SAMPLE_DIR/dance.mp4";
BGM="$SAMPLE_DIR/bgm.MP4";   [ -f "$BGM" ]   || BGM="$SAMPLE_DIR/bgm.mp4";
python3 -u beatsync_badcase_fix_trim_v2.py \
  --dance "$DANCE" \
  --bgm   "$BGM" \
  --output test_memory_verification/waitonme_v2.mp4 \
  2>&1 | tee test_memory_verification/waitonme_v2.log
```

- fallingout 三项对照（22k / 小写容器 / 粗到细）
```bash
# 22k 采样
ffmpeg -y -i input_allcases_lowp/fallingout/dance.MP4 -c:v copy -c:a pcm_s16le -ar 22050 -ac 1 test_memory_verification/tmp_dance_22k.mp4
ffmpeg -y -i input_allcases_lowp/fallingout/bgm.MP4   -c:v copy -c:a pcm_s16le -ar 22050 -ac 1 test_memory_verification/tmp_bgm_22k.mp4
python3 -u beatsync_badcase_fix_trim_v2.py \
  --dance test_memory_verification/tmp_dance_22k.mp4 \
  --bgm   test_memory_verification/tmp_bgm_22k.mp4 \
  --output test_memory_verification/fallingout_v2_22k.mp4 \
  2>&1 | tee test_memory_verification/fallingout_v2_22k.log
rm -f test_memory_verification/tmp_dance_22k.mp4 test_memory_verification/tmp_bgm_22k.mp4

# 容器小写
cp -f input_allcases_lowp/fallingout/dance.MP4 input_allcases_lowp/fallingout/dance.mp4
cp -f input_allcases_lowp/fallingout/bgm.MP4   input_allcases_lowp/fallingout/bgm.mp4
python3 -u beatsync_badcase_fix_trim_v2.py \
  --dance input_allcases_lowp/fallingout/dance.mp4 \
  --bgm   input_allcases_lowp/fallingout/bgm.mp4 \
  --output test_memory_verification/fallingout_v2_lowercase.mp4 \
  2>&1 | tee test_memory_verification/fallingout_v2_lowercase.log

# 粗到细（快速版）
python3 -u beatsync_badcase_fix_trim_v2_fast.py \
  --dance input_allcases_lowp/fallingout/dance.MP4 \
  --bgm   input_allcases_lowp/fallingout/bgm.MP4 \
  --output test_memory_verification/fallingout_v2_fast_refine.mp4 \
  2>&1 | tee test_memory_verification/fallingout_v2_fast_refine.log
```

五、版本映射与处理策略（简要）
- NORMAL 与 bgm_zero：优先 `beatsync_fine_cut_modular.py`（多策略融合；音频统一为双声道）。
- SHORTERBEGIN（T2 > T1）：优先 `beatsync_badcase_fix_trim_v2.py`（简化滑窗裁剪）。
- 存疑样本：用 `beatsync_parallel_processor.py` 同时产出两版，人工选优，规避分类误判。

六、基准样本与期望对齐（摘录）
- fallingout：历史定稿对齐点约 dance=23.24s, bgm=23.99s（两版一致）；当前 V2 在特定预处理下存在偏差，待定位。
- killitgirl_full：优先 modular；V2 可能偏移（仅作参考）。
- nobody / nobody_shorterbegin：受输入一致性影响较大（容器/采样率），建议并行后选优。
- peaches_* / supergirl_*：确认 bgm 文件完整；缺失样本先跳过。

七、已知问题与兜底
- trailing 有声无画面检测：
  - 现象：解析阶段可能出现“could not convert string to float: ''”（疑似正则匹配空串）。
  - 兜底：创建副本 beatsync_badcase_fix_trim_v2_trailing_off.py，临时跳过 trailing 检测与后处理，仅产出基础裁剪成片；同时在原版增加调试打印定位未匹配行。
- 声道：终端输出视频统一双声道（FFmpeg `-ac 2`），确保 modular 与 V2 一致。
- 内存：显式回收（del + gc.collect）、librosa 参数（较大 hop_length）、子进程用 Popen + communicate/kill；若卡顿优先检查子进程。
- Numba：使用本地缓存目录 `.numba_cache/`，避免权限问题。
- 输出缓冲：Python `-u` 与脚本内 `line_buffering` 已开启。

八、验收标准
- 每次执行需汇报：BPM 概览、对齐点（dance,bgm）、badcase 类型、置信度、输出视频路径。
- 异常时至少生成“基础裁剪成片”，并将异常细节写入 `.log`。
- 批处理需生成汇总（成功/失败计数、失败样本列表、各样本输出路径），聊天内输出精简结论。

九、在新聊天窗口的首条消息（建议直接粘贴）
```
我确认使用非沙箱、前台、逐行流式通道，并长期授权你直接执行命令并实时回传日志。
请继承 BeatSync 工程当前上下文：关键状态与指令见 SESSION_HANDOVER.md、PROJECT_STATUS.md、MEMORY_OPTIMIZATION_SUMMARY.md。
按 SESSION_HANDOVER.md 的“fallingout 三项对照”依次执行（22k/小写容器/粗到细），将 stdout 实时流式回传，并在每一步结束时汇报：节拍点、对齐点、badcase 类型、输出视频路径。
若检测到 trailing 解析异常，请先按文档兜底策略生成基础裁剪成片，再单独记录异常片段用于排查。
```

十、后续执行清单（建议顺序）
1) 在新窗口验证 fallingout 的三项对照并比对对齐点；
2) 若差异集中在特定预处理，锁定并回归该分支参数；
3) 回写结论到 PROJECT_STATUS.md，并更新 v2_fallingout_consistency 的处理建议。


