# 项目清理方案总结

## 📊 当前项目状态

- **根目录文件数**: 92个
- **根目录目录数**: 38个（包括.git）
- **总大小**: 约10GB+（主要是输出视频和测试样本）

---

## 📁 文件分类和清理建议

### ✅ 必须保留（核心文件）

| 类别 | 文件/目录 | 数量 | 说明 |
|------|----------|------|------|
| **核心程序** | `beatsync_*.py` (4个) | 4 | Modular、V2、并行处理器、工具模块 |
| **测试脚本** | `test_*.py`, `regression_test.py`, `convert_test_formats.py`, `batch_parallel_processor.py` | 5 | 测试和工具脚本 |
| **Git脚本** | `git_*.sh`, `auto_*.sh`, `*_monitor.sh`, `setup_*.sh` | 9 | Git版本管理相关 |
| **README** | `README.md` | 1 | 项目说明（保留在根目录） |
| **测试输入** | `input_allcases/` | 1 | 高分辨率测试样本（必须） |

### 📚 建议移到docs/目录（文档）

| 文件 | 说明 |
|------|------|
| `PROJECT_STATUS.md` | 项目状态 |
| `PROJECT_SUMMARY.md` | 项目总结 |
| `EXCEPTION_HANDLING_*.md` | 异常处理相关（2个） |
| `MEMORY_OPTIMIZATION_SUMMARY.md` | 内存优化总结 |
| `SESSION_HANDOVER.md` | 会话交接 |
| `TEST_PLAN_VIDEO_FORMAT.md` | 测试计划 |
| `VIDEO_FORMAT_COMPATIBILITY.md` | 格式兼容性 |
| `WEB_SERVICE_ARCHITECTURE.md` | Web架构 |
| `GIT_*.md` | Git相关文档（5个） |
| `AUTO_*.md` | 自动化相关文档（4个） |
| `FILE_MONITOR_GUIDE.md` | 文件监控指南 |
| `CLEANUP_PLAN.md` | 清理方案（本文件） |

**总计**: 约18个文档文件

### ⚠️ 建议归档（历史版本，可选保留）

| 文件 | 说明 | 建议 |
|------|------|------|
| `beatsync_align_mode*.py` | 历史版本（4个） | 移到archive/或删除 |
| `beatsync_main_controller*.py` | 历史版本（3个） | 移到archive/或删除 |
| `beatsync_badcase_fix.py` | 历史版本（填充版本） | 移到archive/或删除 |
| `beatsync_parallel_processor_optimized.py` | 优化版本 | 如果已合并到主版本，可删除 |
| `beatsync_badcase_fix_trim_v2_fast.py` | 快速版本 | 如果已合并，可删除 |
| `analyze_modular_performance.py` | 性能分析脚本 | 移到archive/或删除 |
| `batch_process_v2_allcases.py` | 历史批量处理脚本 | 移到archive/或删除 |

### ❌ 建议删除（输出目录，约8GB+）

| 目录 | 大小 | 说明 |
|------|------|------|
| `regression_test_outputs/` | 3.9GB | 回归测试输出 |
| `parallel_processing_outputs_22:44/` | 1.5GB | 并行处理输出 |
| `test_memory_verification/` | 1.2GB | 内存验证测试 |
| `test_format_compatibility_outputs/` | 1.1GB | 格式兼容性测试输出 |
| `test_multiple_videoformats_converted/` | 783MB | 格式转换测试文件 |
| `parallel_processing_outputs_1025/` | 263MB | 并行处理输出 |
| `output_1/` | 257MB | 输出目录 |
| `program_B_corrected_v2_output/` | 288MB | 程序输出 |
| `parallel_processing_outputs/` | 271MB | 并行处理输出 |
| `v2_batch_outputs/` | 135MB | V2批量输出 |
| `corrected_v3_outputs/` | 130MB | 修正版本输出 |
| `program_B_output/` | 125MB | 程序输出 |
| `corrected_v2_output/` | 124MB | 修正版本输出 |
| `parallel_processing_outputs_lowp_22:53/` | 115MB | 并行处理输出 |
| `perf_logs/` | 112MB | 性能日志 |
| `program_A_retest/` | 141MB | 程序重测 |
| `*_output/`, `*_outputs/` | 其他 | 各种输出目录 |

**总计**: 约10GB+（可以重新生成）

### ❌ 建议删除（临时文件）

| 文件类型 | 示例 | 说明 |
|----------|------|------|
| `*.log` | `.git_monitor.log`, `fallingout_*.log`, `v2_memory_validation.log` | 日志文件 |
| `*.pid` | `.git_monitor.pid` | 进程ID文件 |
| `*.wav` | `temp_*.wav`, `tmp_*.wav`, `test_*.wav` | 临时音频文件 |
| `*.txt` | `memory_test_log.txt`, `stereo_test_log.txt` | 临时文本文件 |

### ❌ 建议删除（聊天记录和备份脚本）

| 文件/目录 | 说明 |
|----------|------|
| `chat_history/` | 聊天记录目录 |
| `backup_*.sh` | 备份脚本 |
| `restore_*.sh` | 恢复脚本 |
| `merge_*.py` | 合并脚本 |
| `save_*.py`, `transfer_*.py`, `update_*.py`, `rebuild_*.py` | 其他辅助脚本 |
| `聊天记录*.md` | 聊天记录文档 |
| `Cursor收藏功能说明.md` | Cursor相关文档 |

### ❌ 建议删除（测试场景目录）

| 目录 | 说明 |
|------|------|
| `test_exception_scenarios/` | 异常测试场景 |
| `test_memory_verification/` | 内存验证测试 |
| `test_stereo_verification/` | 立体声验证测试 |
| `program_A_retest/` | 程序重测 |
| `program_backup/` | 程序备份 |
| `fallingout_recheck/` | 重测目录 |
| `batch_memory_recheck/` | 内存重测 |

### ⚠️ 需要确认（测试样本）

| 目录 | 大小 | 说明 | 建议 |
|------|------|------|------|
| `input_allcases/` | 1.4GB | 高分辨率测试样本 | ✅ **必须保留** |
| `input_allcases_lowp/` | 316MB | 低分辨率测试样本 | ⚠️ 可选保留 |
| `input_false/` | ? | 特定badcase样本 | ⚠️ 可选保留 |
| `input_false_2/` | 78MB | 特定badcase样本 | ⚠️ 可选保留 |
| `newcases/` | ? | 新增测试样本 | ⚠️ 可选保留 |
| `test_multiple_videoformats/` | 66MB | 格式兼容性测试样本 | ✅ **建议保留** |
| `angel_girlfront/` | ? | 测试样本？ | ⚠️ 需要确认 |

### ⚠️ 需要确认（其他）

| 目录/文件 | 说明 | 建议 |
|----------|------|------|
| `project_docs/` | 项目文档备份 | 如果docs/目录已包含，可删除 |
| `test_format_compatibility_fixed.py` | 修复版本测试脚本 | 如果已合并到主版本，可删除 |
| `run_*.sh`, `check_*.sh`, `clear_*.sh`, `monitor_*.sh`, `test_*.sh` | 其他辅助脚本 | 根据实际需要决定 |

---

## 🎯 清理后预期结构

```
BeatSync/
├── README.md                          # 项目说明（根目录）
├── beatsync_fine_cut_modular.py      # 核心程序
├── beatsync_badcase_fix_trim_v2.py
├── beatsync_parallel_processor.py
├── beatsync_utils.py
├── test_exception_handling.py         # 测试脚本
├── regression_test.py
├── test_format_compatibility.py
├── convert_test_formats.py
├── batch_parallel_processor.py
├── git_commit_important.sh            # Git脚本
├── auto_commit.sh
├── ac -> auto_commit.sh
├── AUTO_COMMIT_MONITOR.sh
├── start_monitor.sh
├── stop_monitor.sh
├── check_monitor.sh
├── setup_auto_git.sh
├── docs/                               # 文档目录（新建）
│   └── (所有.md文档，除了README.md)
├── archive/                            # 历史版本（可选，新建）
│   └── (历史版本程序)
├── input_allcases/                     # 测试样本
├── test_multiple_videoformats/         # 格式测试样本
├── .gitignore
└── .git/
```

---

## ❓ 需要你确认的问题

1. **历史版本程序**：
   - [ ] 删除所有历史版本
   - [ ] 保留并移到 `archive/` 目录

2. **低分辨率测试样本** (`input_allcases_lowp/`)：
   - [ ] 保留
   - [ ] 删除

3. **其他测试样本** (`input_false/`, `input_false_2/`, `newcases/`)：
   - [ ] 保留
   - [ ] 删除

4. **分析脚本** (`analyze_modular_performance.py`)：
   - [ ] 保留
   - [ ] 移到 `archive/`
   - [ ] 删除

5. **文档组织**：
   - [ ] 将所有文档移到 `docs/` 目录
   - [ ] 保持现状（所有文档在根目录）

6. **其他辅助脚本** (`run_*.sh`, `check_*.sh`等)：
   - [ ] 保留
   - [ ] 删除

---

## 📋 清理步骤（待确认后执行）

### 步骤1：创建目录结构
```bash
mkdir -p docs archive
```

### 步骤2：移动文档（如果选择）
```bash
# 移动所有文档到docs/（除了README.md）
mv PROJECT_*.md EXCEPTION_*.md MEMORY_*.md SESSION_*.md \
   TEST_*.md VIDEO_*.md WEB_*.md GIT_*.md AUTO_*.md \
   FILE_*.md CLEANUP_*.md docs/ 2>/dev/null
```

### 步骤3：归档历史版本（如果选择）
```bash
# 移动历史版本到archive/
mv beatsync_align_mode*.py beatsync_main_controller*.py \
   beatsync_badcase_fix.py beatsync_parallel_processor_optimized.py \
   beatsync_badcase_fix_trim_v2_fast.py analyze_modular_performance.py \
   batch_process_v2_allcases.py archive/ 2>/dev/null
```

### 步骤4：删除输出目录
```bash
rm -rf *_output/ *_outputs/ parallel_processing_outputs* \
       regression_test_outputs/ test_format_compatibility_outputs/ \
       corrected_*_output/ program_*_output/ v2_*_outputs/ \
       batch_*_outputs/ angel_girlfront_output/ fallingout_output/
```

### 步骤5：删除临时文件
```bash
rm -f *.log *.pid *.time *.wav temp_* tmp_* *.txt
```

### 步骤6：删除测试场景目录
```bash
rm -rf test_exception_scenarios/ test_*_verification/ \
       program_A_retest/ program_backup/ fallingout_recheck/ \
       batch_memory_recheck/
```

### 步骤7：删除聊天记录和备份脚本
```bash
rm -rf chat_history/
rm -f backup_*.sh restore_*.sh merge_*.py save_*.py \
     transfer_*.py update_*.py rebuild_*.py \
     聊天记录*.md "Cursor收藏功能说明.md"
```

### 步骤8：删除其他（根据确认）
```bash
# 如果确认删除
rm -rf perf_logs/ project_docs/ angel_girlfront/
rm -f test_format_compatibility_fixed.py
rm -f run_*.sh check_python_processes.sh clear_*.sh \
     monitor_*.sh test_memory_*.sh launch_*.sh \
     setup_auto_backup.sh
```

---

## 📊 清理效果预估

**清理前**:
- 根目录文件: 92个
- 根目录目录: 38个
- 总大小: 约10GB+

**清理后**:
- 根目录文件: 约20个（核心程序+测试脚本+Git脚本）
- 根目录目录: 约5个（docs/, archive/, input_allcases/, test_multiple_videoformats/, .git/）
- 总大小: 约2GB（主要是测试样本）

**释放空间**: 约8GB+

---

请确认以上分类和清理建议，确认后我将执行清理操作。
