# 项目目录进一步重组方案

## 当前状态分析

### 一级目录文件分布

**核心程序**（4个）:
- `beatsync_fine_cut_modular.py`
- `beatsync_badcase_fix_trim_v2.py`
- `beatsync_parallel_processor.py`
- `beatsync_utils.py`

**测试脚本**（5个）:
- `test_exception_handling.py`
- `regression_test.py`
- `test_format_compatibility.py`
- `convert_test_formats.py`
- `batch_parallel_processor.py`

**Git脚本**（7个）:
- `git_commit_important.sh`
- `auto_commit.sh` / `ac`
- `AUTO_COMMIT_MONITOR.sh`
- `start_monitor.sh`
- `stop_monitor.sh`
- `check_monitor.sh`
- `setup_auto_git.sh`

**其他文件**:
- `README.md`（项目说明，保留在根目录）
- 临时文件（`*.log`, `*.wav`，应该删除）

**目录**（5个）:
- `docs/` - 文档
- `archive/` - 历史版本
- `input_allcases/` - 测试样本
- `input_allcases_lowp/` - 测试样本
- `test_multiple_videoformats/` - 测试样本

---

## 重组方案

### 方案1：创建scripts/目录（推荐）

**优点**:
- 测试脚本集中管理
- 根目录更简洁
- 符合常见项目结构

**结构**:
```
BeatSync/
├── README.md
├── 核心程序（4个，保留在根目录）
├── scripts/                    # 新建
│   ├── test/                   # 测试脚本
│   │   ├── test_exception_handling.py
│   │   ├── regression_test.py
│   │   └── test_format_compatibility.py
│   ├── tools/                  # 工具脚本
│   │   ├── convert_test_formats.py
│   │   └── batch_parallel_processor.py
│   └── git/                    # Git脚本
│       ├── git_commit_important.sh
│       ├── auto_commit.sh
│       ├── AUTO_COMMIT_MONITOR.sh
│       ├── start_monitor.sh
│       ├── stop_monitor.sh
│       ├── check_monitor.sh
│       └── setup_auto_git.sh
├── docs/
├── archive/
└── 测试样本目录
```

**根目录文件**: 5个（4个核心程序 + README.md）

---

### 方案2：只创建tests/目录

**优点**:
- 简单，只移动测试脚本
- Git脚本保留在根目录（便于使用）

**结构**:
```
BeatSync/
├── README.md
├── 核心程序（4个）
├── tests/                      # 新建
│   ├── test_exception_handling.py
│   ├── regression_test.py
│   ├── test_format_compatibility.py
│   ├── convert_test_formats.py
│   └── batch_parallel_processor.py
├── Git脚本（7个，保留在根目录）
├── docs/
├── archive/
└── 测试样本目录
```

**根目录文件**: 12个（4个核心程序 + 7个Git脚本 + README.md）

---

### 方案3：创建scripts/和tests/分离

**优点**:
- 测试和工具脚本分离
- Git脚本保留在根目录

**结构**:
```
BeatSync/
├── README.md
├── 核心程序（4个）
├── tests/                      # 新建
│   ├── test_exception_handling.py
│   ├── regression_test.py
│   └── test_format_compatibility.py
├── scripts/                    # 新建
│   ├── convert_test_formats.py
│   └── batch_parallel_processor.py
├── Git脚本（7个，保留在根目录）
├── docs/
├── archive/
└── 测试样本目录
```

**根目录文件**: 12个（4个核心程序 + 7个Git脚本 + README.md）

---

## 推荐方案

**推荐方案1**，原因：
1. **最简洁**: 根目录只有5个文件（核心程序 + README）
2. **结构清晰**: 所有脚本都在scripts/目录下，分类明确
3. **易于维护**: 测试、工具、Git脚本分离
4. **符合惯例**: 大多数项目都有scripts/目录

**注意事项**:
- Git脚本移动到scripts/git/后，需要更新：
  - `ac` 符号链接路径
  - `AUTO_COMMIT_MONITOR.sh` 中的路径引用
  - 文档中的使用说明

---

## 实施步骤

### 步骤1：创建目录结构
```bash
mkdir -p scripts/test scripts/tools scripts/git
```

### 步骤2：移动测试脚本
```bash
mv test_exception_handling.py regression_test.py \
   test_format_compatibility.py scripts/test/
```

### 步骤3：移动工具脚本
```bash
mv convert_test_formats.py batch_parallel_processor.py \
   scripts/tools/
```

### 步骤4：移动Git脚本
```bash
mv git_commit_important.sh auto_commit.sh \
   AUTO_COMMIT_MONITOR.sh start_monitor.sh \
   stop_monitor.sh check_monitor.sh setup_auto_git.sh \
   scripts/git/
```

### 步骤5：更新符号链接
```bash
rm ac
ln -s scripts/git/auto_commit.sh ac
```

### 步骤6：更新路径引用
- 更新 `AUTO_COMMIT_MONITOR.sh` 中的监控文件路径
- 更新文档中的使用说明

### 步骤7：清理临时文件
```bash
rm -f *.log *.wav temp_* tmp_*
```

---

## 重组后的预期效果

**根目录**:
- 文件: 5个（4个核心程序 + README.md）
- 目录: 6个（scripts/, docs/, archive/, 3个测试样本目录）

**结构清晰度**: ⭐⭐⭐⭐⭐

---

## 需要确认的问题

1. **选择哪个方案**？
   - [ ] 方案1：创建scripts/目录（推荐）
   - [ ] 方案2：只创建tests/目录
   - [ ] 方案3：创建scripts/和tests/分离
   - [ ] 保持现状

2. **Git脚本位置**？
   - [ ] 移到scripts/git/（方案1）
   - [ ] 保留在根目录（方案2/3）

3. **是否需要更新使用说明**？
   - [ ] 是，更新README.md和文档
   - [ ] 否，保持现状

