# BeatSync 项目结构

## 项目目录结构

```
BeatSync/
├── README.md                          # 项目说明（根目录）
│
├── 核心程序
│   ├── beatsync_fine_cut_modular.py      # Modular版本
│   ├── beatsync_badcase_fix_trim_v2.py   # V2版本
│   ├── beatsync_parallel_processor.py    # 并行处理器（推荐）
│   └── beatsync_utils.py                 # 工具模块
│
├── 测试脚本
│   ├── test_exception_handling.py        # 异常处理测试
│   ├── regression_test.py                # 回归测试
│   ├── test_format_compatibility.py      # 格式兼容性测试
│   ├── convert_test_formats.py            # 格式转换工具
│   └── batch_parallel_processor.py       # 批量处理脚本
│
├── Git版本管理
│   ├── git_commit_important.sh           # 重要改动存档脚本
│   ├── auto_commit.sh / ac                # 自动提交脚本
│   ├── AUTO_COMMIT_MONITOR.sh             # 文件监控脚本
│   ├── start_monitor.sh                   # 启动监控
│   ├── stop_monitor.sh                    # 停止监控
│   ├── check_monitor.sh                   # 检查监控状态
│   └── setup_auto_git.sh                 # Git自动化设置
│
├── docs/                                  # 项目文档（分类整理）
│   ├── project/                           # 项目相关
│   │   ├── PROJECT_STATUS.md              # 项目状态
│   │   ├── PROJECT_STRUCTURE.md           # 项目结构
│   │   ├── PROJECT_SUMMARY.md             # 项目总结
│   │   └── SESSION_HANDOVER.md            # 会话交接
│   │
│   ├── deployment/                         # 部署相关
│   │   ├── DEPLOYMENT_README.md           # 部署指南
│   │   ├── DEPLOYMENT_CHECKLIST.md        # 部署检查清单
│   │   ├── DEPLOYMENT_GUIDE.md            # 详细部署指南
│   │   └── RENDER_PRICING_GUIDE.md       # Render定价指南
│   │
│   ├── development/                       # 开发相关
│   │   ├── DEVELOPMENT_PRINCIPLES.md     # 开发原则
│   │   ├── EXCEPTION_HANDLING_GUIDE.md   # 异常处理指南
│   │   ├── MEMORY_OPTIMIZATION_SUMMARY.md # 内存优化总结
│   │   └── PERFORMANCE_*.md               # 性能优化相关
│   │
│   ├── web-service/                       # Web服务相关
│   │   ├── WEB_SERVICE_ARCHITECTURE.md   # Web架构
│   │   ├── WEB_SERVICE_DESIGN.md         # Web设计
│   │   ├── WEB_UI_DESIGN.md              # UI设计
│   │   └── ASYNC_*.md                     # 异步处理相关
│   │
│   ├── troubleshooting/                   # 故障排除
│   │   ├── CORS_FIX_GUIDE.md             # CORS修复指南
│   │   ├── DEPENDENCIES_FIX.md           # 依赖修复
│   │   └── PROCESS_FAILED_*.md           # 处理失败相关
│   │
│   └── git/                               # Git相关
│       ├── GIT_COMMIT_GUIDE.md           # Git提交指南
│       ├── GIT_QUICK_REFERENCE.md       # Git快速参考
│       └── AUTO_*.md                     # 自动化相关
│
├── archive/                               # 历史版本归档
│   ├── beatsync_align_mode*.py            # 历史版本
│   ├── beatsync_main_controller*.py       # 历史版本
│   └── beatsync_badcase_fix.py            # 历史版本
│
├── 测试样本
│   ├── input_allcases/                    # 高分辨率测试样本（必须）
│   ├── input_allcases_lowp/               # 低分辨率测试样本
│   └── test_multiple_videoformats/        # 格式兼容性测试样本
│
├── .gitignore                             # Git忽略配置
└── .git/                                  # Git仓库
```

## 文件说明

### 核心程序（4个）

- **beatsync_fine_cut_modular.py**: Modular版本，多策略融合对齐算法
- **beatsync_badcase_fix_trim_v2.py**: V2版本，简化滑动窗口算法
- **beatsync_parallel_processor.py**: 并行处理器，同时运行两个版本（推荐）
- **beatsync_utils.py**: 工具模块，异常处理、输入验证等

### 测试脚本（5个）

- **test_exception_handling.py**: 异常处理测试
- **regression_test.py**: 回归测试
- **test_format_compatibility.py**: 格式兼容性测试
- **convert_test_formats.py**: 格式转换工具
- **batch_parallel_processor.py**: 批量处理脚本

### Git版本管理（7个脚本）

- **git_commit_important.sh**: 重要改动存档
- **auto_commit.sh / ac**: 自动提交（快捷方式）
- **AUTO_COMMIT_MONITOR.sh**: 文件监控
- **start_monitor.sh**: 启动监控
- **stop_monitor.sh**: 停止监控
- **check_monitor.sh**: 检查监控状态
- **setup_auto_git.sh**: Git自动化设置

### 文档目录（docs/）

按功能分类整理，约60+个文件：
- **project/**：项目状态、结构、总结
- **deployment/**：部署指南、检查清单、定价指南
- **development/**：开发原则、异常处理、性能优化
- **web-service/**：Web架构、设计、异步处理
- **troubleshooting/**：故障排除、修复指南
- **git/**：Git使用指南、自动化文档

### 归档目录（archive/）

包含历史版本程序，约10个文件：
- 历史版本的对齐算法
- 历史版本的主控程序
- 已废弃的功能实现

### 测试样本

- **input_allcases/**: 高分辨率测试样本（1.4GB，必须保留）
- **input_allcases_lowp/**: 低分辨率测试样本（316MB）
- **test_multiple_videoformats/**: 格式兼容性测试样本（66MB）

## 使用指南

### 快速开始

```bash
# 处理单个样本（推荐）
python3 beatsync_parallel_processor.py \
  --dance input_allcases/echo/dance.mp4 \
  --bgm input_allcases/echo/bgm.mp4 \
  --output-dir outputs \
  --sample-name echo
```

### 版本管理

```bash
# 启动文件监控
./start_monitor.sh

# 手动提交
./ac

# 重要改动提交
./git_commit_important.sh "类型: 描述"
```

### 查看文档

```bash
# 查看项目状态
cat docs/project/PROJECT_STATUS.md

# 查看部署指南
cat docs/deployment/DEPLOYMENT_README.md

# 查看Git指南
cat docs/git/GIT_QUICK_REFERENCE.md

# 查看故障排除
cat docs/troubleshooting/TROUBLESHOOTING.md
```

## 项目特点

- ✅ **结构清晰**: 核心程序、测试脚本、文档分离
- ✅ **版本管理**: 完整的Git自动化机制
- ✅ **文档完善**: 所有文档集中在docs/目录
- ✅ **历史归档**: 历史版本保存在archive/目录
- ✅ **干净整洁**: 无临时文件和输出目录

