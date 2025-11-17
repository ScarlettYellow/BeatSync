# 项目重组完成

## 重组内容

### 1. 创建scripts/目录结构

**scripts/test/** - 测试脚本（3个）
- `test_exception_handling.py`
- `regression_test.py`
- `test_format_compatibility.py`

**scripts/tools/** - 工具脚本（2个）
- `convert_test_formats.py`
- `batch_parallel_processor.py`

**scripts/git/** - Git脚本（7个）
- `git_commit_important.sh`
- `auto_commit.sh`
- `AUTO_COMMIT_MONITOR.sh`
- `start_monitor.sh`
- `stop_monitor.sh`
- `check_monitor.sh`
- `setup_auto_git.sh`

### 2. 创建test_data/目录

**test_data/** - 测试样本目录
- `input_allcases/` - 高分辨率测试样本
- `input_allcases_lowp/` - 低分辨率测试样本
- `test_multiple_videoformats/` - 格式兼容性测试样本

### 3. 更新路径引用

**已更新的脚本**:
- `scripts/test/regression_test.py` - 更新为 `test_data/input_allcases`
- `scripts/tools/batch_parallel_processor.py` - 更新为 `test_data/input_allcases_lowp`
- `scripts/test/test_format_compatibility.py` - 更新为 `test_data/test_multiple_videoformats`
- `scripts/test/test_exception_handling.py` - 更新为 `test_data/test_multiple_videoformats`
- `scripts/tools/convert_test_formats.py` - 更新为 `test_data/test_multiple_videoformats`

**已更新的Git脚本**:
- `scripts/git/AUTO_COMMIT_MONITOR.sh` - 更新文件路径为绝对路径
- `scripts/git/start_monitor.sh` - 更新脚本路径
- `scripts/git/stop_monitor.sh` - 更新PID文件路径
- `scripts/git/check_monitor.sh` - 更新PID和日志文件路径

**符号链接**:
- `ac` -> `scripts/git/auto_commit.sh`（已更新）

---

## 重组后的项目结构

```
BeatSync/
├── README.md                          # 项目说明
├── 核心程序（4个，根目录）
│   ├── beatsync_fine_cut_modular.py
│   ├── beatsync_badcase_fix_trim_v2.py
│   ├── beatsync_parallel_processor.py
│   └── beatsync_utils.py
├── scripts/                           # 脚本目录
│   ├── test/                          # 测试脚本
│   │   ├── test_exception_handling.py
│   │   ├── regression_test.py
│   │   └── test_format_compatibility.py
│   ├── tools/                          # 工具脚本
│   │   ├── convert_test_formats.py
│   │   └── batch_parallel_processor.py
│   └── git/                            # Git脚本
│       ├── git_commit_important.sh
│       ├── auto_commit.sh
│       ├── AUTO_COMMIT_MONITOR.sh
│       ├── start_monitor.sh
│       ├── stop_monitor.sh
│       ├── check_monitor.sh
│       └── setup_auto_git.sh
├── docs/                               # 文档目录
├── archive/                            # 历史版本
├── test_data/                          # 测试样本目录
│   ├── input_allcases/                 # 高分辨率测试样本
│   ├── input_allcases_lowp/            # 低分辨率测试样本
│   └── test_multiple_videoformats/     # 格式兼容性测试样本
└── ac -> scripts/git/auto_commit.sh    # 快捷方式
```

---

## 重组效果

**根目录**:
- 文件: 5个（4个核心程序 + README.md）
- 目录: 4个（scripts/, docs/, archive/, test_data/）

**结构清晰度**: ⭐⭐⭐⭐⭐

---

## 使用说明

### 运行测试脚本

```bash
# 回归测试
python3 scripts/test/regression_test.py

# 异常处理测试
python3 scripts/test/test_exception_handling.py

# 格式兼容性测试
python3 scripts/test/test_format_compatibility.py
```

### 运行工具脚本

```bash
# 格式转换工具
python3 scripts/tools/convert_test_formats.py

# 批量处理
python3 scripts/tools/batch_parallel_processor.py
```

### 使用Git脚本

```bash
# 自动提交（快捷方式）
./ac

# 启动文件监控
./scripts/git/start_monitor.sh
# 或使用快捷方式（如果创建了）
```

### 访问测试样本

```bash
# 高分辨率测试样本
test_data/input_allcases/

# 低分辨率测试样本
test_data/input_allcases_lowp/

# 格式兼容性测试样本
test_data/test_multiple_videoformats/
```

---

## 注意事项

1. **路径更新**: 所有脚本中的路径引用已更新，但如果在其他脚本中直接引用了旧路径，需要手动更新。

2. **Git监控**: Git监控脚本已更新为使用绝对路径，可以在任何目录下运行。

3. **测试样本**: 所有测试样本现在统一放在 `test_data/` 目录下，便于管理。

4. **符号链接**: `ac` 符号链接已更新，可以在项目根目录直接使用 `./ac`。

---

## 后续建议

1. 更新README.md中的使用说明，反映新的目录结构
2. 更新其他文档中的路径引用（如果有）
3. 考虑在根目录创建快捷脚本（如 `run_test.sh`）方便使用

