# BeatSync 项目交接文档

> **文档目的**：为新接手的AI Agent提供完整的项目历史上下文，确保能够流畅地继续处理项目后续工作。

**最后更新**：2025-11-27  
**项目状态**：✅ 核心功能已完成，Web服务已部署，本地开发环境优化中

---

## 一、项目概述

### 1.1 项目简介

**BeatSync** 是一个专门为街舞课堂设计的视频音轨自动对齐和替换工具。核心功能是自动将课堂跳舞视频的现场收音替换为高质量范例视频的音轨，通过智能节拍对齐算法实现精确的音频同步。

### 1.2 核心特性

- ✅ **智能节拍对齐**：自动检测两个视频的音乐节拍，找到最佳对齐位置
- ✅ **完全音轨替换**：完全移除课堂视频的原始音轨，只保留范例视频音轨
- ✅ **保持视频质量**：保持原始视频的分辨率、帧率和时长
- ✅ **自动处理**：无需手动调整，一键完成音频替换
- ✅ **双版本输出**：同时生成两个版本（modular和V2），用户选择最佳结果
- ✅ **格式兼容**：支持 MP4、MOV、AVI、MKV、H.265 等多种视频格式
- ✅ **智能裁剪**：自动检测并裁剪无效内容（开头/末尾静音、有声无画面段落）
- ✅ **高性能优化**：高分辨率视频处理速度提升 2.7-3倍，支持硬件加速

### 1.3 使用场景

- 街舞课堂结课视频制作
- 现场表演视频音频优化
- 音乐视频音质提升
- 任何需要音频替换的视频处理

---

## 二、项目结构

```
BeatSync/
├── README.md                          # 项目主文档
├── render.yaml                        # Render部署配置
│
├── 核心程序（4个）
│   ├── beatsync_parallel_processor.py    # ⭐ 并行处理器（推荐）
│   ├── beatsync_fine_cut_modular.py      # Modular版本
│   ├── beatsync_badcase_fix_trim_v2.py   # V2版本
│   └── beatsync_utils.py                  # 工具模块
│
├── docs/                              # 项目文档（分类整理）
│   ├── project/                       # 项目相关
│   │   ├── PROJECT_STATUS.md          # 项目状态
│   │   ├── PROJECT_STRUCTURE.md       # 项目结构
│   │   ├── PROJECT_SUMMARY.md         # 项目总结
│   │   └── AGENT_HANDOVER.md          # 本交接文档
│   ├── deployment/                    # 部署相关
│   │   ├── DEPLOYMENT_README.md        # 部署指南
│   │   ├── CHINA_CLOUD_PLATFORMS_ANALYSIS.md  # 中国云平台分析
│   │   └── ...
│   ├── development/                   # 开发相关
│   │   ├── DEVELOPMENT_PRINCIPLES.md   # 开发原则
│   │   ├── SERIAL_PARALLEL_MODE.md     # 串行/并行模式说明
│   │   ├── AUTO_CLEANUP_IMPLEMENTATION.md  # 自动清理实现
│   │   └── ...
│   ├── web-service/                   # Web服务相关
│   │   ├── WEB_SERVICE_ARCHITECTURE.md # Web服务架构
│   │   ├── ASYNC_PROCESSING_SOLUTION.md # 异步处理方案
│   │   └── ...
│   ├── troubleshooting/               # 故障排除
│   │   ├── UPLOAD_FAILED_QUICK_FIX.md  # 上传失败快速修复
│   │   ├── BACKEND_STARTUP_ISSUE.md    # 后端启动问题
│   │   └── ...
│   └── git/                           # Git相关
│
├── scripts/                           # 脚本工具
│   ├── git/                           # Git自动化脚本
│   ├── test/                          # 测试脚本
│   └── tools/                         # 工具脚本
│
├── web_service/                       # Web服务
│   ├── backend/                       # 后端（FastAPI）
│   │   ├── main.py                    # 主应用文件
│   │   ├── requirements.txt           # Python依赖
│   │   ├── start_server.sh            # 启动脚本
│   │   ├── stop_server.sh             # 停止脚本
│   │   ├── restart_server.sh          # 重启脚本
│   │   ├── start_and_wait.sh          # 启动并等待就绪
│   │   └── test_backend.sh            # 测试脚本
│   └── frontend/                      # 前端（HTML/CSS/JS）
│       ├── index.html                 # 主页面
│       ├── script.js                  # 前端逻辑
│       ├── style.css                  # 样式文件
│       └── start_frontend.sh          # 启动脚本
│
├── test_data/                         # 测试数据
│   ├── input_allcases/                # 高分辨率测试样本
│   ├── input_allcases_lowp/           # 低分辨率测试样本
│   └── test_multiple_videoformats/    # 格式兼容性测试
│
├── outputs/                           # 输出目录
│   ├── batch_all_hd_samples/          # 批量处理结果
│   ├── web_uploads/                   # Web上传文件（自动清理）
│   ├── web_outputs/                   # Web输出文件（保留3天）
│   ├── logs/                          # 日志文件
│   └── task_status.json               # 任务状态持久化
│
├── archive/                           # 历史版本归档
└── .gitignore                         # Git配置
```

---

## 三、核心处理程序

### 3.1 并行处理器（推荐）⭐

**文件**：`beatsync_parallel_processor.py`

**功能**：同时使用modular版本和V2版本处理样本，生成两个输出视频供用户选择。

**特点**：
- 绕过复杂的badcase分类问题
- 用户可以直接对比选择最佳结果
- 两个版本使用统一的音频配置（双声道）

**使用方法**：
```bash
python3 beatsync_parallel_processor.py \
  --dance 课堂视频.mp4 \
  --bgm 范例视频.mp4 \
  --output-dir 输出目录 \
  --sample-name 样本名称
```

**输出文件**：
- `{样本名称}_modular.mp4` - Modular版本（多策略融合，精度高）
- `{样本名称}_v2.mp4` - V2版本（快速对齐，适合特定场景）

**处理模式**：
- **默认模式**：串行处理（`parallel=False`），适合资源受限环境（如Render免费 tier）
- **并行模式**：使用 `--parallel` 参数启用，适合高性能服务器

**超时设置**：
- 每个版本处理超时：1200秒（20分钟）

### 3.2 Modular版本

**文件**：`beatsync_fine_cut_modular.py`

**功能**：使用多策略融合对齐算法进行视频音频同步。

**对齐算法**：
- 多策略融合算法（MFCC、Chroma、Spectral Contrast、Spectral Rolloff）
- 对齐精度高，适合大多数场景
- 自动裁剪无效内容段落

**音频配置**：双声道 (`-ac 2`)

**使用方法**：
```bash
python3 beatsync_fine_cut_modular.py \
  --dance 课堂视频.mp4 \
  --bgm 范例视频.mp4 \
  --output 输出视频.mp4 \
  --fast-video \
  --enable-cache
```

### 3.3 V2版本

**文件**：`beatsync_badcase_fix_trim_v2.py`

**功能**：使用简化滑动窗口对齐算法进行视频音频同步。

**对齐算法**：
- 简化滑动窗口算法（基于节拍检测）
- 处理速度快
- 适合特定badcase类型（T2 > T1）

**音频配置**：双声道 (`-ac 2`)

**使用方法**：
```bash
python3 beatsync_badcase_fix_trim_v2.py \
  --dance 课堂视频.mp4 \
  --bgm 范例视频.mp4 \
  --output 输出视频.mp4 \
  --fast-video \
  --enable-cache
```

### 3.4 工具模块

**文件**：`beatsync_utils.py`

**功能**：提供通用的工具函数，包括：
- 音频提取和缓存
- 视频格式转换
- FFmpeg命令封装
- 性能优化相关函数

---

## 四、Web服务架构

### 4.1 架构概述

**前端**：纯HTML/CSS/JavaScript，部署在GitHub Pages  
**后端**：FastAPI (Python)，部署在Render  
**通信**：RESTful API，支持CORS跨域

### 4.2 后端API（FastAPI）

**文件**：`web_service/backend/main.py`

**主要端点**：
- `GET /api/health` - 健康检查
- `POST /api/upload` - 上传视频文件（dance或bgm）
- `POST /api/process` - 提交处理任务
- `GET /api/status/{task_id}` - 查询任务状态
- `GET /api/download/{task_id}?version=modular|v2` - 下载处理结果

**关键配置**：
```python
UPLOAD_DIR = project_root / "outputs" / "web_uploads"  # 上传目录
OUTPUT_DIR = project_root / "outputs" / "web_outputs"  # 输出目录
CLEANUP_AGE_HOURS = 24  # 上传文件保留时间
WEB_OUTPUTS_RETENTION_DAYS = 3  # Web输出保留3天
```

**任务状态管理**：
- 使用 `task_status.json` 持久化任务状态
- 支持任务状态恢复（服务重启后）
- 自动清理超过7天的旧任务状态

**自动清理机制**：
1. **上传文件清理**：处理完成后立即删除（无论成功或失败）
2. **输出文件清理**：保留最近3天，自动删除更早的文件
3. **任务状态清理**：保留最近7天，自动删除更早的状态

**启动优化**：
- 所有阻塞操作（加载任务状态、清理旧文件）都移到 `@app.on_event("startup")` 中
- 确保服务快速启动，不阻塞模块导入

**日志输出**：
- 所有 `print` 语句都重定向到 `stderr` 并 `flush`
- 确保日志在终端中可见（特别是在后台运行时）

### 4.3 前端（HTML/JS）

**文件**：
- `web_service/frontend/index.html` - 主页面结构
- `web_service/frontend/script.js` - 前端逻辑
- `web_service/frontend/style.css` - 样式文件

**环境检测**：
- 自动检测本地开发环境（`localhost` 或 `127.0.0.1`）
- 本地环境：使用 `http://localhost:8000`
- 生产环境：使用 `https://beatsync-backend-asha.onrender.com`

**主要功能**：
1. **文件上传**：
   - 支持拖拽上传
   - 显示上传进度
   - 动态超时设置（小文件2分钟，大文件10分钟）
   - 后端健康检查

2. **任务处理**：
   - 异步提交处理任务
   - 轮询任务状态（每2秒）
   - 显示处理进度（modular和V2分别显示）

3. **结果下载**：
   - 两个独立的下载按钮（V2版本和Modular版本）
   - 下载前重新获取最新状态（避免闭包问题）
   - 按钮大小一致，V2在左，Modular在右

**调试日志**：
- 详细的请求/响应日志（使用emoji标记）
- 包括耗时、响应文本、错误详情

### 4.4 本地开发环境

**启动后端**：
```bash
cd web_service/backend
./start_and_wait.sh  # 启动并等待就绪
# 或
./start_server.sh    # 直接启动
```

**启动前端**：
```bash
cd web_service/frontend
./start_frontend.sh  # 使用Python HTTP服务器
```

**停止服务**：
```bash
cd web_service/backend
./stop_server.sh     # 停止后端
```

**测试后端**：
```bash
cd web_service/backend
./test_backend.sh    # 测试后端连接
```

**快速启动（开发）**：
```bash
cd web_service/backend
./quick_start.sh     # 同时启动前后端
```

---

## 五、部署情况

### 5.1 前端部署（GitHub Pages）

**地址**：`https://scarlettyellow.github.io/BeatSync/`  
**配置**：自动从 `main` 分支部署  
**文件位置**：`web_service/frontend/` 目录下的静态文件

### 5.2 后端部署（Render）

**地址**：`https://beatsync-backend-asha.onrender.com`  
**配置**：`render.yaml`  
**环境**：
- Python 3.11.0
- 免费 tier（资源受限）
- 自动部署（GitHub推送触发）

**性能限制**：
- 免费 tier 资源有限，并行处理反而更慢
- 默认使用串行处理模式
- 处理超时：1200秒（20分钟）

### 5.3 云平台分析

**文档**：`docs/deployment/CHINA_CLOUD_PLATFORMS_ANALYSIS.md`

**推荐方案**：腾讯云轻量应用服务器（Lighthouse）
- **配置**：2核4G
- **价格**：约88元/年（活动价）
- **优势**：性价比高，适合个人项目
- **性能**：可支持并行处理，处理时间可降至2分钟以内

**其他选项**：
- 阿里云轻量应用服务器
- 华为云弹性云服务器
- 百度智能云

---

## 六、技术决策和优化历史

### 6.1 性能优化

**高分辨率视频优化**（2024-11）：
- 处理速度提升 **2.7-3倍**（35s → 10-13s）
- 优化技术：
  - 音频仅解码（`-vn`），避免视频解码开销
  - 视频流复制（`-c:v copy`），避免重新编码
  - 快速编码（`x264 ultrafast`）或硬件加速
  - 音频提取缓存，重复样本自动命中

**内存优化**（2024-11）：
- 峰值内存：从 26GB 降至 **2-4GB**
- 优化技术：
  - 增加 `hop_length` 至 2048
  - 显式垃圾回收
  - 子进程隔离
  - Numba 本地缓存

### 6.2 串行 vs 并行处理

**问题**：Render免费 tier上并行处理反而更慢（近20分钟）

**原因**：资源受限，并行处理导致CPU/内存竞争

**解决方案**：
- 默认使用串行处理（`parallel=False`）
- 保留并行逻辑作为备选（`--parallel` 参数）
- 等服务器升级后再启用并行模式

**文档**：`docs/development/SERIAL_PARALLEL_MODE.md`

### 6.3 自动清理机制

**需求**：
1. `web_uploads/`：处理完成后自动删除
2. `web_outputs/`：仅保留最近3天

**实现**：
- 上传文件：在 `process_video_background` 中处理完成后立即删除
- 输出文件：`cleanup_old_web_outputs()` 函数，在启动时和定期清理
- 任务状态：`cleanup_old_tasks()` 函数，清理超过7天的旧任务

**文档**：`docs/development/AUTO_CLEANUP_IMPLEMENTATION.md`

### 6.4 输出文件命名

**旧格式**：`beatsync_{task_id}_v2.mp4`、`beatsync_{task_id}_modular.mp4`  
**新格式**：`v2_{task_id}.mp4`、`modular_{task_id}.mp4`

**原因**：用户要求将版本标识放在开头，移除"BeatSync"字段

### 6.5 音频配置统一

**问题**：V2版本音量更大更亮  
**原因**：modular版本使用单声道（`-ac 1`），V2版本使用双声道（`-ac 2`）  
**解决**：将modular版本改为双声道（`-ac 2`），统一两个版本的音频配置

---

## 七、已知问题和解决方案

### 7.1 本地开发环境问题

**问题1**：前端卡在"正在上传原始视频..."，后端没有日志

**可能原因**：
- 后端服务未启动
- 网络连接问题
- 文件过大，上传超时

**解决方案**：
1. 检查后端服务状态：`curl http://localhost:8000/api/health`
2. 查看浏览器控制台日志（详细调试信息）
3. 查看后端终端日志（`tail -f /tmp/beatsync_backend.log`）
4. 使用 `start_and_wait.sh` 确保后端完全就绪

**文档**：`docs/troubleshooting/UPLOAD_FAILED_QUICK_FIX.md`

**问题2**：端口8000已被占用

**解决方案**：
```bash
cd web_service/backend
./stop_server.sh    # 停止现有服务
./start_server.sh   # 重新启动
```

**文档**：`docs/troubleshooting/PORT_8000_IN_USE.md`

**问题3**：后端启动慢或卡住

**原因**：启动时执行了阻塞操作（加载任务状态、清理文件）

**解决方案**：已优化，将所有阻塞操作移到 `@app.on_event("startup")` 中

**文档**：`docs/troubleshooting/BACKEND_STARTUP_ISSUE.md`

### 7.2 线上服务问题

**问题1**：处理超时（600秒）

**解决方案**：将超时时间增加到1200秒（20分钟）

**问题2**：并行处理反而更慢

**解决方案**：默认使用串行处理，保留并行逻辑作为备选

**文档**：`docs/troubleshooting/PROCESSING_TIMEOUT_ANALYSIS.md`

### 7.3 对齐算法问题

**问题**：某些样本对齐效果不理想（如 `fallingout`、`killitgirl_full`）

**结论**：
- 放弃针对特定样本的微调优化（采样率、容器名等）
- 优先使用并行处理方案，让用户选择最佳结果
- 如需继续深入，应转向特征层策略（如节拍/Chroma权重、窗口与步长自适应）

**文档**：`docs/project/PROJECT_STATUS.md`（第8节）

---

## 八、开发环境设置

### 8.1 系统要求

- Python 3.7+
- FFmpeg（必须安装并在PATH中）
- 依赖包：`numpy`, `soundfile`, `librosa`, `opencv-python`, `fastapi`, `uvicorn`

### 8.2 安装依赖

**核心程序**：
```bash
pip install numpy soundfile librosa opencv-python
```

**Web服务后端**：
```bash
cd web_service/backend
pip install -r requirements.txt
```

### 8.3 本地开发流程

1. **启动后端**：
   ```bash
   cd web_service/backend
   ./start_and_wait.sh
   ```

2. **启动前端**：
   ```bash
   cd web_service/frontend
   ./start_frontend.sh
   ```

3. **访问应用**：
   - 前端：`http://localhost:8080/`
   - 后端API文档：`http://localhost:8000/docs`

4. **测试上传和处理**：
   - 选择两个视频文件（dance和bgm）
   - 点击"开始处理"
   - 等待处理完成
   - 下载结果

### 8.4 调试技巧

**前端调试**：
- 打开浏览器开发者工具（F12）
- 查看Console标签的详细日志
- 查看Network标签的请求/响应详情

**后端调试**：
- 查看终端日志（`tail -f /tmp/beatsync_backend.log`）
- 使用 `curl` 测试API端点
- 检查 `outputs/task_status.json` 查看任务状态

---

## 九、当前状态和待办事项

### 9.1 已完成功能 ✅

- [x] 核心处理程序（并行处理器、Modular版本、V2版本）
- [x] Web服务前后端
- [x] 前端部署（GitHub Pages）
- [x] 后端部署（Render）
- [x] 自动清理机制（上传文件、输出文件、任务状态）
- [x] 性能优化（高分辨率视频、内存优化）
- [x] 串行/并行模式切换
- [x] 输出文件命名优化
- [x] 音频配置统一（双声道）
- [x] 本地开发环境优化（启动脚本、调试日志）

### 9.2 进行中的工作 🔄

**本地开发环境调试**：
- 前端上传请求卡住问题
- 后端日志输出优化
- 前端调试日志增强

**状态**：已添加详细调试日志，等待用户测试反馈

### 9.3 待办事项 📋

**高优先级**：
1. **解决本地开发环境上传问题**
   - 诊断前端卡在"正在上传原始视频..."的原因
   - 确保后端正确接收和处理上传请求
   - 验证文件保存和响应返回

2. **验证线上服务稳定性**
   - 测试串行处理模式在Render上的表现
   - 监控处理时间和成功率
   - 优化超时和错误处理

**中优先级**：
3. **考虑服务器升级**
   - 评估腾讯云Lighthouse方案
   - 迁移到高性能服务器
   - 启用并行处理模式

4. **用户体验优化**
   - 改进前端错误提示
   - 添加处理进度条
   - 优化移动端体验

**低优先级**：
5. **算法优化**
   - 研究特征层策略优化
   - 改进对齐算法精度
   - 处理特殊样本（如fallingout）

6. **文档完善**
   - 更新用户使用指南
   - 补充API文档
   - 记录更多故障排除案例

---

## 十、关键文件和配置说明

### 10.1 核心配置文件

**`render.yaml`**：
- Render部署配置
- Python版本：3.11.0
- 启动命令：`uvicorn main:app --host 0.0.0.0 --port $PORT`

**`.gitignore`**：
- 忽略 `outputs/` 目录（除 `task_status.json`）
- 忽略缓存和临时文件
- 忽略日志文件（除特定日志）

### 10.2 任务状态文件

**`outputs/task_status.json`**：
- 格式：JSON对象，key为task_id，value为任务状态
- 状态字段：
  - `status`: "processing" | "success" | "failed"
  - `modular_status`: "processing" | "success" | "failed"
  - `v2_status`: "processing" | "success" | "failed"
  - `modular_output`: 输出文件路径（如果成功）
  - `v2_output`: 输出文件路径（如果成功）
  - `error`: 错误信息（如果失败）
  - `created_at`: 创建时间
  - `updated_at`: 更新时间

### 10.3 环境变量

**后端环境变量**：
- `ALLOWED_ORIGINS`: 允许的CORS来源（默认：`*`）
- `PORT`: 服务端口（Render自动设置）

**前端环境变量**：
- `API_BASE_URL`: 后端API地址（自动检测，可通过 `window.API_BASE_URL` 覆盖）

### 10.4 日志文件

**后端日志**：
- 位置：`/tmp/beatsync_backend.log`（本地开发）
- 格式：Uvicorn访问日志 + 自定义INFO/ERROR日志

**性能日志**：
- 位置：`outputs/logs/performance_YYYYMMDD.log`
- 内容：处理时间、文件大小、内存使用等

---

## 十一、重要技术细节

### 11.1 对齐算法

**Modular版本（多策略融合）**：
1. 快速节拍检测（librosa.beat.beat_track）
2. 多策略搜索（原始相关性 + 音乐特征）
3. 特征提取：MFCC、Chroma、Spectral Contrast、Spectral Rolloff
4. 融合决策：根据得分选择最佳策略

**V2版本（简化滑动窗口）**：
1. 快速节拍检测
2. 滑动窗口搜索（基于节拍点）
3. 计算相关性得分
4. 选择最佳对齐点

### 11.2 视频处理流程

1. **格式标准化**：非MP4格式转换为MP4（stream copy，零损失）
2. **音频提取**：提取音频轨道（支持缓存）
3. **节拍检测**：使用librosa检测节拍点和BPM
4. **智能对齐**：根据版本选择不同算法
5. **无效内容检测**：检测并裁剪开头/末尾静音
6. **视频合成**：将处理后的音频与原始视频合成

### 11.3 异步处理机制

**Web服务处理流程**：
1. 用户上传两个视频文件（dance和bgm）
2. 后端保存文件，返回file_id
3. 用户提交处理任务
4. 后端在后台线程中处理（`process_video_background`）
5. 前端轮询任务状态（每2秒）
6. 处理完成后，前端显示下载按钮
7. 用户下载结果

**任务状态持久化**：
- 使用 `task_status.json` 保存任务状态
- 服务重启后可以恢复任务状态
- 定期清理旧任务状态

---

## 十二、常见问题快速参考

### Q1: 如何启动本地开发环境？

```bash
# 终端1：启动后端
cd web_service/backend
./start_and_wait.sh

# 终端2：启动前端
cd web_service/frontend
./start_frontend.sh

# 访问：http://localhost:8080/
```

### Q2: 上传文件卡住怎么办？

1. 检查后端是否运行：`curl http://localhost:8000/api/health`
2. 查看浏览器控制台日志
3. 查看后端终端日志
4. 检查文件大小（是否过大）

### Q3: 如何处理超时问题？

- 本地：检查文件大小，大文件可能需要更长时间
- 线上：Render免费tier资源有限，考虑升级服务器

### Q4: 如何切换串行/并行模式？

**并行处理器**：
```bash
python3 beatsync_parallel_processor.py --parallel ...
```

**Web服务**：
- 默认串行（适合免费tier）
- 需要修改 `beatsync_parallel_processor.py` 中的 `parallel` 参数

### Q5: 如何清理旧文件？

- 上传文件：自动清理（处理完成后）
- 输出文件：自动清理（保留3天）
- 任务状态：自动清理（保留7天）
- 手动清理：删除 `outputs/web_outputs/` 中的旧目录

---

## 十三、联系和资源

### 13.1 项目仓库

- **GitHub**: `https://github.com/ScarlettYellow/BeatSync`
- **前端地址**: `https://scarlettyellow.github.io/BeatSync/`
- **后端地址**: `https://beatsync-backend-asha.onrender.com`

### 13.2 重要文档索引

- **项目状态**: `docs/project/PROJECT_STATUS.md`
- **项目结构**: `docs/project/PROJECT_STRUCTURE.md`
- **部署指南**: `docs/deployment/DEPLOYMENT_README.md`
- **开发原则**: `docs/development/DEVELOPMENT_PRINCIPLES.md`
- **故障排除**: `docs/troubleshooting/` 目录

### 13.3 关键代码文件

- **并行处理器**: `beatsync_parallel_processor.py`
- **后端API**: `web_service/backend/main.py`
- **前端逻辑**: `web_service/frontend/script.js`
- **Modular版本**: `beatsync_fine_cut_modular.py`
- **V2版本**: `beatsync_badcase_fix_trim_v2.py`

---

## 十四、交接检查清单

新接手的Agent应该：

- [ ] 阅读本交接文档
- [ ] 了解项目结构和核心功能
- [ ] 熟悉Web服务架构
- [ ] 设置本地开发环境
- [ ] 测试核心处理程序
- [ ] 测试Web服务（本地）
- [ ] 查看当前待办事项
- [ ] 了解已知问题和解决方案
- [ ] 熟悉调试技巧和日志查看

---

**文档维护**：每次重要变更后，请更新本文档的相关章节。

**最后更新**：2025-11-27  
**更新内容**：添加本地开发环境调试、前端上传问题、后端日志优化等最新进展

