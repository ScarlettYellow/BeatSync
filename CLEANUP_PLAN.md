# 项目清理方案

## 一、文件分类

### 1.1 核心程序文件（必须保留）✅

**位置**: 项目根目录

- `beatsync_fine_cut_modular.py` - Modular版本
- `beatsync_badcase_fix_trim_v2.py` - V2版本
- `beatsync_parallel_processor.py` - 并行处理器（推荐）
- `beatsync_utils.py` - 工具模块

### 1.2 测试和工具脚本（建议保留）✅

**位置**: 项目根目录

- `test_exception_handling.py` - 异常处理测试
- `regression_test.py` - 回归测试
- `test_format_compatibility.py` - 格式兼容性测试
- `convert_test_formats.py` - 格式转换工具
- `batch_parallel_processor.py` - 批量处理脚本

### 1.3 Git和版本管理（必须保留）✅

**位置**: 项目根目录

- `.git/` - Git仓库
- `.gitignore` - Git忽略配置
- `git_commit_important.sh` - 重要改动存档脚本
- `auto_commit.sh` / `ac` - 自动提交脚本
- `AUTO_COMMIT_MONITOR.sh` - 文件监控脚本
- `start_monitor.sh` - 启动监控
- `stop_monitor.sh` - 停止监控
- `check_monitor.sh` - 检查监控状态
- `setup_auto_git.sh` - Git自动化设置

### 1.4 项目文档（必须保留）✅

**位置**: 项目根目录

- `README.md` - 项目说明
- `PROJECT_STATUS.md` - 项目状态
- `PROJECT_SUMMARY.md` - 项目总结
- `EXCEPTION_HANDLING_GUIDE.md` - 异常处理指南
- `EXCEPTION_HANDLING_PLAN.md` - 异常处理计划
- `MEMORY_OPTIMIZATION_SUMMARY.md` - 内存优化总结
- `SESSION_HANDOVER.md` - 会话交接文档
- `TEST_PLAN_VIDEO_FORMAT.md` - 视频格式测试计划
- `VIDEO_FORMAT_COMPATIBILITY.md` - 视频格式兼容性文档
- `WEB_SERVICE_ARCHITECTURE.md` - Web服务架构文档
- `GIT_COMMIT_GUIDE.md` - Git提交指南
- `GIT_QUICK_REFERENCE.md` - Git快速参考
- `GIT_REMOTE_SETUP.md` - 远程仓库设置指南
- `GIT_PUSH_GUIDE.md` - Git推送指南
- `AUTO_GIT_GUIDE.md` - 自动化Git指南
- `AUTO_COMMIT_OPTIONS.md` - 自动化提交选项
- `FILE_MONITOR_GUIDE.md` - 文件监控指南
- `AUTO_VERSION_SUMMARY.md` - 自动化版本管理总结

### 1.5 测试输入数据（建议保留）✅

**位置**: 子目录

- `input_allcases/` - 所有测试样本（高分辨率）
- `input_allcases_lowp/` - 低分辨率测试样本（可选）
- `input_false/` - 特定badcase样本（可选）
- `newcases/` - 新增测试样本（可选）
- `test_multiple_videoformats/` - 格式兼容性测试样本

### 1.6 输出目录（建议删除或归档）❌

**位置**: 子目录

- `*_output/` - 各种输出目录
- `*_outputs/` - 各种输出目录
- `parallel_processing_outputs/` - 并行处理输出
- `regression_test_outputs/` - 回归测试输出
- `test_format_compatibility_outputs/` - 格式兼容性测试输出
- `corrected_*_output/` - 修正版本输出
- `program_*_output/` - 程序输出
- `v2_*_outputs/` - V2版本输出
- `batch_*_outputs/` - 批量处理输出

**建议**: 删除（输出视频可以重新生成）

### 1.7 临时文件（建议删除）❌

**位置**: 项目根目录

- `*.log` - 日志文件
- `*.pid` - 进程ID文件
- `*.time` - 时间记录文件
- `*.wav` - 临时音频文件
- `*.txt` - 临时文本文件（如 `stereo_test_log.txt`, `memory_test_log.txt`）
- `temp_*` - 临时文件
- `tmp_*` - 临时文件

**建议**: 删除（临时文件，可以重新生成）

### 1.8 历史版本程序（建议归档或删除）⚠️

**位置**: 项目根目录

- `beatsync_working.py` - 历史版本
- `beatsync_trim.py` - 历史版本
- `beatsync_badcase_fix.py` - 历史版本（填充版本）
- `beatsync_align_mode*.py` - 历史版本
- `beatsync_main_controller*.py` - 历史版本
- `beatsync_parallel_processor_optimized.py` - 优化版本（如果已合并）

**建议**: 
- 如果已不再使用，可以删除
- 如果需要保留作为参考，可以移到 `archive/` 目录

### 1.9 分析脚本（可选保留）⚠️

**位置**: 项目根目录

- `analyze_modular_performance.py` - 性能分析脚本
- `batch_process_v2_allcases.py` - 批量处理脚本（历史版本）

**建议**: 如果不再使用，可以删除或归档

### 1.10 聊天记录和备份脚本（建议删除或归档）❌

**位置**: 项目根目录

- `chat_history/` - 聊天记录目录
- `*.sh` - 备份/恢复脚本（如 `backup_cursor_chat.sh`, `restore_*.sh`）
- `merge_*.py` - 聊天记录合并脚本
- `save_chat_message.py` - 聊天记录保存脚本
- `聊天记录*.md` - 聊天记录文档

**建议**: 删除（这些是开发过程中的辅助工具，不需要保留在项目中）

### 1.11 测试场景目录（建议删除）❌

**位置**: 子目录

- `test_exception_scenarios/` - 异常测试场景（可以重新生成）
- `test_memory_verification/` - 内存验证测试
- `test_stereo_verification/` - 立体声验证测试
- `program_A_retest/` - 程序A重测
- `program_backup/` - 程序备份

**建议**: 删除（测试输出可以重新生成）

### 1.12 其他目录（需要检查）⚠️

- `angel_girlfront/` - 测试样本？
- `angel_girlfront_output/` - 输出目录
- `fallingout_output/` - 输出目录
- `fallingout_recheck/` - 重测目录
- `perf_logs/` - 性能日志
- `project_docs/` - 项目文档备份

**建议**: 根据实际情况决定

---

## 二、清理建议

### 2.1 必须保留 ✅

1. **核心程序文件**（4个）
2. **测试脚本**（5个）
3. **Git相关文件**（所有）
4. **项目文档**（所有.md文档）
5. **测试输入数据**（`input_allcases/` 必须，其他可选）

### 2.2 建议删除 ❌

1. **所有输出目录**（`*_output/`, `*_outputs/`）
2. **临时文件**（`*.log`, `*.pid`, `*.wav`, `*.txt`, `temp_*`, `tmp_*`）
3. **聊天记录和备份脚本**（`chat_history/`, `backup_*.sh`, `restore_*.sh`等）
4. **测试场景目录**（`test_*_scenarios/`, `test_*_verification/`）

### 2.3 建议归档或删除 ⚠️

1. **历史版本程序**（移到 `archive/` 或删除）
2. **分析脚本**（如果不再使用）

---

## 三、建议的项目结构

```
BeatSync/
├── README.md
├── beatsync_fine_cut_modular.py
├── beatsync_badcase_fix_trim_v2.py
├── beatsync_parallel_processor.py
├── beatsync_utils.py
├── test_exception_handling.py
├── regression_test.py
├── test_format_compatibility.py
├── convert_test_formats.py
├── batch_parallel_processor.py
├── git_commit_important.sh
├── auto_commit.sh
├── ac -> auto_commit.sh
├── AUTO_COMMIT_MONITOR.sh
├── start_monitor.sh
├── stop_monitor.sh
├── check_monitor.sh
├── setup_auto_git.sh
├── docs/                          # 新建：文档目录
│   ├── PROJECT_STATUS.md
│   ├── PROJECT_SUMMARY.md
│   ├── EXCEPTION_HANDLING_GUIDE.md
│   ├── EXCEPTION_HANDLING_PLAN.md
│   ├── MEMORY_OPTIMIZATION_SUMMARY.md
│   ├── SESSION_HANDOVER.md
│   ├── TEST_PLAN_VIDEO_FORMAT.md
│   ├── VIDEO_FORMAT_COMPATIBILITY.md
│   ├── WEB_SERVICE_ARCHITECTURE.md
│   ├── GIT_COMMIT_GUIDE.md
│   ├── GIT_QUICK_REFERENCE.md
│   ├── GIT_REMOTE_SETUP.md
│   ├── GIT_PUSH_GUIDE.md
│   ├── AUTO_GIT_GUIDE.md
│   ├── AUTO_COMMIT_OPTIONS.md
│   ├── FILE_MONITOR_GUIDE.md
│   └── AUTO_VERSION_SUMMARY.md
├── archive/                        # 新建：历史版本归档
│   └── (历史版本程序)
├── input_allcases/                 # 保留：测试样本
├── test_multiple_videoformats/     # 保留：格式测试样本
├── .gitignore
└── .git/
```

---

## 四、清理步骤（待确认）

### 步骤1：创建文档目录并移动文档

```bash
mkdir -p docs
mv PROJECT_STATUS.md PROJECT_SUMMARY.md EXCEPTION_HANDLING_*.md \
   MEMORY_OPTIMIZATION_SUMMARY.md SESSION_HANDOVER.md \
   TEST_PLAN_VIDEO_FORMAT.md VIDEO_FORMAT_COMPATIBILITY.md \
   WEB_SERVICE_ARCHITECTURE.md GIT_*.md AUTO_*.md FILE_MONITOR_GUIDE.md \
   docs/
```

### 步骤2：创建归档目录（可选）

```bash
mkdir -p archive
# 移动历史版本程序到archive/
```

### 步骤3：删除输出目录

```bash
rm -rf *_output/ *_outputs/ parallel_processing_outputs/ \
       regression_test_outputs/ test_format_compatibility_outputs/ \
       corrected_*_output/ program_*_output/ v2_*_outputs/ \
       batch_*_outputs/ angel_girlfront_output/ fallingout_output/
```

### 步骤4：删除临时文件

```bash
rm -f *.log *.pid *.time *.wav temp_* tmp_* *.txt
rm -rf test_exception_scenarios/ test_*_verification/ \
       program_A_retest/ program_backup/
```

### 步骤5：删除聊天记录和备份脚本

```bash
rm -rf chat_history/
rm -f backup_*.sh restore_*.sh merge_*.py save_*.py \
     transfer_*.py update_*.py rebuild_*.py \
     聊天记录*.md
```

### 步骤6：清理其他

```bash
# 删除其他不需要的目录
rm -rf fallingout_recheck/ perf_logs/ project_docs/ \
       angel_girlfront/ batch_memory_recheck/
```

---

## 五、需要你确认的问题

1. **历史版本程序**：是否保留？如果保留，是否移到 `archive/` 目录？
2. **低分辨率测试样本**：`input_allcases_lowp/` 是否保留？
3. **其他测试样本**：`input_false/`, `newcases/` 是否保留？
4. **分析脚本**：`analyze_modular_performance.py` 是否保留？
5. **文档组织**：是否将所有文档移到 `docs/` 目录？

---

## 六、清理后的预期效果

- ✅ 项目根目录只保留核心程序、测试脚本、Git脚本
- ✅ 所有文档集中在 `docs/` 目录
- ✅ 历史版本归档到 `archive/` 目录（如果保留）
- ✅ 删除所有输出目录和临时文件
- ✅ 项目结构清晰、干净

