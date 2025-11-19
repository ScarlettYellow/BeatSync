# BeatSync 项目目录整理方案

## 当前问题分析

### 1. 根目录文件过多（14个文件）
- **文档文件**（应移到docs/）：
  - `DEPLOYMENT_README.md` → `docs/DEPLOYMENT_README.md`
  - `MEMORY_ISSUE_ANALYSIS.md` → `docs/MEMORY_ISSUE_ANALYSIS.md`
  - `MEMORY_OPTIMIZATION_SUMMARY.md` → `docs/MEMORY_OPTIMIZATION_SUMMARY.md`
  - `SESSION_HANDOVER.md` → `docs/SESSION_HANDOVER.md`

- **测试/工具脚本**（应移到scripts/）：
  - `check_python_processes.sh` → `scripts/tools/check_python_processes.sh`
  - `monitor_memory.sh` → `scripts/tools/monitor_memory.sh`
  - `run_memory_test.sh` → `scripts/tools/run_memory_test.sh`
  - `test_memory_simple.sh` → `scripts/tools/test_memory_simple.sh`
  - `test_memory_usage.py` → `scripts/tools/test_memory_usage.py`

- **重复/临时文件**（应删除或归档）：
  - `beatsync_badcase_fix_trim_v2_fast.py` → `archive/`（已废弃的fast版本）
  - `temp_silent_detection.wav` → 删除（临时文件）

- **保留在根目录**：
  - `README.md` ✅
  - `render.yaml` ✅
  - `beatsync_fine_cut_modular.py` ✅
  - `beatsync_badcase_fix_trim_v2.py` ✅
  - `beatsync_parallel_processor.py` ✅
  - `beatsync_utils.py` ✅

### 2. docs目录文件过多（60+个文件）
需要按类别分类整理：

#### 方案A：按功能分类（推荐）
```
docs/
├── project/              # 项目相关
│   ├── PROJECT_STATUS.md
│   ├── PROJECT_STRUCTURE.md
│   ├── PROJECT_SUMMARY.md
│   └── SESSION_HANDOVER.md
│
├── deployment/           # 部署相关
│   ├── DEPLOYMENT_README.md
│   ├── DEPLOYMENT_CHECKLIST.md
│   ├── DEPLOYMENT_GUIDE.md
│   ├── DEPLOYMENT_UPDATE.md
│   ├── RENDER_PRICING_GUIDE.md
│   └── ...
│
├── development/         # 开发相关
│   ├── DEVELOPMENT_PRINCIPLES.md
│   ├── EXCEPTION_HANDLING_GUIDE.md
│   ├── MEMORY_OPTIMIZATION_SUMMARY.md
│   └── ...
│
├── web-service/         # Web服务相关
│   ├── WEB_SERVICE_ARCHITECTURE.md
│   ├── WEB_SERVICE_DESIGN.md
│   ├── WEB_UI_DESIGN.md
│   └── ...
│
├── troubleshooting/     # 故障排除
│   ├── CORS_FIX_GUIDE.md
│   ├── DEPENDENCIES_FIX.md
│   ├── PROCESS_FAILED_TROUBLESHOOTING.md
│   └── ...
│
└── git/                 # Git相关
    ├── GIT_COMMIT_GUIDE.md
    ├── GIT_QUICK_REFERENCE.md
    └── ...
```

#### 方案B：保持扁平结构，但删除过时文档
- 删除重复的文档（如多个EXCEPTION_HANDLING_*.md）
- 删除过时的文档（如CLEANUP_PLAN.md, CLEANUP_SUMMARY.md）
- 合并相似的文档

### 3. web_service目录
- **日志文件**（应删除或移到outputs/）：
  - `backend.log` → 删除（临时日志）
  - `frontend.log` → 删除（临时日志）

- **临时调试文件**（应删除）：
  - `check_backend_connection.html` → 删除

- **文档文件**（应移到docs/web-service/）：
  - `DEBUG_TASK_ISSUE.md` → `docs/web-service/`
  - `DEPLOYMENT_STEPS.md` → `docs/deployment/`
  - `ENVIRONMENT_ISOLATION.md` → `docs/web-service/`
  - `LOCAL_DEVELOPMENT.md` → `docs/web-service/`
  - `MOBILE_TESTING_GUIDE.md` → `docs/web-service/`
  - `QUICK_FIX.md` → `docs/troubleshooting/`
  - `TROUBLESHOOTING.md` → `docs/troubleshooting/`
  - `TROUBLESHOOTING_LOCAL.md` → `docs/troubleshooting/`

## 整理方案

### 方案1：全面整理（推荐）
1. **根目录**：只保留核心文件和配置文件
2. **docs目录**：按功能分类整理
3. **scripts目录**：保持现状（已较整洁）
4. **web_service目录**：清理临时文件，文档移到docs/

### 方案2：最小整理
1. **根目录**：只移动文档和测试脚本
2. **docs目录**：保持扁平结构，只删除过时文档
3. **web_service目录**：只清理临时文件

### 方案3：保守整理
1. **根目录**：只移动明显不应该在根目录的文件
2. **其他目录**：保持现状

## 推荐方案：方案1（全面整理）

### 执行步骤

1. **整理根目录**
   - 移动文档到 `docs/`
   - 移动测试脚本到 `scripts/tools/`
   - 移动fast版本到 `archive/`
   - 删除临时文件

2. **整理docs目录**
   - 创建子目录：`project/`, `deployment/`, `development/`, `web-service/`, `troubleshooting/`, `git/`
   - 按类别移动文档
   - 删除过时/重复文档

3. **整理web_service目录**
   - 删除日志文件
   - 删除临时调试文件
   - 移动文档到 `docs/web-service/` 或 `docs/troubleshooting/`

4. **更新README.md**
   - 更新项目结构说明
   - 更新文档路径引用

## 整理后的目录结构

```
BeatSync/
├── README.md                    # 项目说明
├── render.yaml                   # Render部署配置
│
├── 核心程序（4个）
│   ├── beatsync_fine_cut_modular.py
│   ├── beatsync_badcase_fix_trim_v2.py
│   ├── beatsync_parallel_processor.py
│   └── beatsync_utils.py
│
├── docs/                        # 文档（分类整理）
│   ├── project/                 # 项目相关
│   ├── deployment/             # 部署相关
│   ├── development/            # 开发相关
│   ├── web-service/            # Web服务相关
│   ├── troubleshooting/        # 故障排除
│   └── git/                    # Git相关
│
├── scripts/                     # 脚本（已整洁）
│   ├── git/                    # Git脚本
│   ├── test/                   # 测试脚本
│   └── tools/                  # 工具脚本
│
├── web_service/                 # Web服务（已清理）
│   ├── backend/                # 后端
│   ├── frontend/              # 前端
│   └── README.md              # Web服务说明
│
├── test_data/                  # 测试数据
├── outputs/                    # 输出目录
├── archive/                    # 历史版本
└── .gitignore                 # Git配置
```

## 需要确认的问题

1. **docs目录分类**：选择方案A（按功能分类）还是方案B（保持扁平）？
2. **过时文档**：是否删除明显过时的文档（如CLEANUP_PLAN.md）？
3. **重复文档**：是否合并相似的文档（如多个EXCEPTION_HANDLING_*.md）？
4. **fast版本**：`beatsync_badcase_fix_trim_v2_fast.py` 是否移到archive/？

