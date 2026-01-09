# BeatSync 项目交接文档（2025年最新版）

> **文档目的**：为新接手的AI Agent提供完整的项目历史上下文，确保能够流畅地继续处理项目后续工作。

**最后更新**：2025-01-06  
**项目状态**：✅ 核心功能已完成，Web服务已部署，订阅系统已实现，iOS App开发中（当前遇到启动崩溃问题）

---

## 📋 快速导航

- [一、项目概述](#一项目概述)
- [二、项目结构](#二项目结构)
- [三、核心处理程序](#三核心处理程序)
- [四、Web服务架构](#四web服务架构)
- [五、订阅系统](#五订阅系统)
- [六、iOS App开发](#六ios-app开发)
- [七、部署情况](#七部署情况)
- [八、当前问题和待办事项](#八当前问题和待办事项)
- [九、技术决策历史](#九技术决策历史)
- [十、重要文件和配置](#十重要文件和配置)
- [十一、调试和故障排除](#十一调试和故障排除)

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
- ✅ **订阅系统**：完整的订阅和支付系统，支持iOS内购和Web支付
- ✅ **多端支持**：Web端（GitHub Pages）和iOS App（Capacitor）

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
│
├── 核心处理程序（4个）
│   ├── beatsync_parallel_processor.py    # ⭐ 并行处理器（推荐）
│   ├── beatsync_fine_cut_modular.py      # Modular版本
│   ├── beatsync_badcase_fix_trim_v2.py   # V2版本
│   └── beatsync_utils.py                  # 工具模块
│
├── docs/                              # 项目文档（400+个文件）
│   ├── project/                       # 项目相关
│   │   ├── PROJECT_STATUS.md          # 项目状态
│   │   ├── PROJECT_STRUCTURE.md       # 项目结构
│   │   ├── PROJECT_SUMMARY.md         # 项目总结
│   │   ├── AGENT_HANDOVER.md          # 旧版交接文档
│   │   └── AGENT_HANDOVER_2025.md     # 本交接文档（最新）
│   ├── subscription/                  # 订阅系统相关（100+文档）
│   │   ├── SUBSCRIPTION_SYSTEM_DESIGN.md  # 订阅系统设计
│   │   └── ...                        # 大量订阅系统实现文档
│   ├── deployment/                    # 部署相关
│   ├── development/                   # 开发相关
│   ├── web-service/                   # Web服务相关
│   ├── mobile/                        # 移动端相关
│   ├── troubleshooting/               # 故障排除
│   └── git/                           # Git相关
│
├── scripts/                           # 脚本工具
│   ├── deployment/                    # 部署脚本
│   ├── git/                           # Git自动化脚本
│   ├── test/                          # 测试脚本
│   └── tools/                         # 工具脚本
│
├── web_service/                       # Web服务
│   ├── backend/                       # 后端（FastAPI）
│   │   ├── main.py                    # 主应用文件（1800+行）
│   │   ├── subscription_service.py    # 订阅服务
│   │   ├── subscription_db.py         # 订阅数据库
│   │   ├── payment_service.py         # 支付服务
│   │   ├── subscription_receipt_verification.py  # 收据验证
│   │   └── requirements.txt           # Python依赖
│   └── frontend/                      # 前端（HTML/CSS/JS）
│       ├── index.html                 # 主页面
│       ├── script.js                  # 前端逻辑（4500+行）
│       ├── subscription.js            # 订阅前端逻辑
│       ├── payment.js                  # 支付前端逻辑
│       ├── style.css                  # 样式文件
│       └── sw.js                       # Service Worker
│
├── ios/                               # iOS App（Capacitor）
│   ├── App/                           # Xcode项目
│   │   ├── App/                       # 应用代码
│   │   │   ├── AppDelegate.swift      # 应用委托
│   │   │   ├── Info.plist            # 应用配置
│   │   │   └── App-Bridging-Header.h # Bridging Header
│   │   ├── SaveToGalleryPlugin.swift # 保存插件（已禁用）
│   │   └── SaveToGalleryPlugin.m     # 插件注册（已禁用）
│   └── Plugins/                       # 插件目录
│
├── test_data/                         # 测试数据
├── outputs/                           # 输出目录
│   ├── web_uploads/                   # Web上传文件（自动清理）
│   ├── web_outputs/                   # Web输出文件（保留3天）
│   └── task_status.json               # 任务状态持久化
│
└── archive/                           # 历史版本归档
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

### 3.2 Modular版本

**文件**：`beatsync_fine_cut_modular.py`

**对齐算法**：多策略融合算法（MFCC、Chroma、Spectral Contrast、Spectral Rolloff）

### 3.3 V2版本

**文件**：`beatsync_badcase_fix_trim_v2.py`

**对齐算法**：简化滑动窗口算法（基于节拍检测）

---

## 四、Web服务架构

### 4.1 架构概述

**前端**：纯HTML/CSS/JavaScript，部署在GitHub Pages  
**后端**：FastAPI (Python)，部署在腾讯云轻量应用服务器  
**通信**：RESTful API，支持CORS跨域

### 4.2 后端API（FastAPI）

**文件**：`web_service/backend/main.py`（1800+行）

**主要端点**：
- `GET /api/health` - 健康检查
- `POST /api/upload` - 上传视频文件
- `POST /api/process` - 提交处理任务
- `GET /api/status/{task_id}` - 查询任务状态
- `GET /api/download/{task_id}?version=modular|v2` - 下载处理结果

**订阅系统端点**：
- `POST /api/auth/register` - 用户注册（设备ID自动注册）
- `POST /api/auth/login` - 用户登录
- `GET /api/subscription/products` - 获取订阅套餐
- `POST /api/subscription/purchase` - 购买订阅（Web支付）
- `POST /api/subscription/verify-receipt` - 验证iOS收据
- `GET /api/subscription/status` - 获取订阅状态
- `POST /api/credits/consume` - 消费下载次数
- `GET /api/credits/check` - 检查可用下载次数

**关键配置**：
```python
UPLOAD_DIR = project_root / "outputs" / "web_uploads"  # 上传目录
OUTPUT_DIR = project_root / "outputs" / "web_outputs"  # 输出目录
CLEANUP_AGE_HOURS = 24  # 上传文件保留时间
WEB_OUTPUTS_RETENTION_DAYS = 3  # Web输出保留3天
```

### 4.3 前端（HTML/JS）

**主要文件**：
- `web_service/frontend/index.html` - 主页面结构
- `web_service/frontend/script.js` - 前端逻辑（4500+行）
- `web_service/frontend/subscription.js` - 订阅前端逻辑
- `web_service/frontend/payment.js` - 支付前端逻辑

**环境检测**：
- 自动检测本地开发环境（`localhost` 或 `127.0.0.1`）
- 本地环境：使用 `http://localhost:8000`
- 生产环境（Web/PWA）：使用 `https://beatsync.site`
- Capacitor原生App环境：强制使用 `http://124.221.58.149`（HTTP，无端口）

---

## 五、订阅系统

### 5.1 系统概述

**设计理念**：
- ✅ **为下载付费**：用户只为满意的结果付费
- ✅ **处理免费**：允许用户无限次处理
- ✅ **多端同步**：iOS App 和网站共享同一套订阅系统
- ✅ **白名单功能**：管理员可添加用户到白名单
- ✅ **零耦合设计**：订阅系统与现有功能完全解耦

### 5.2 套餐设计

**免费体验套餐**：
- 每周可免费下载2个满意作品
- 处理次数：无限次

**基础版付费套餐**：
- 连续包月：15元/月，50次下载/月
- 连续包年：99元/年，600次下载/年

**高级版付费套餐**：
- 连续包月：69元/月，1000次下载/月
- 连续包年：499元/年，12000次下载/年

**购买下载次数套餐（一次性）**：
- 5元/10次
- 9元/20次
- 20元/50次

### 5.3 技术实现

**数据库**：SQLite（`data/subscription.db`）

**后端服务**：
- `subscription_service.py` - 订阅业务逻辑
- `subscription_db.py` - 数据库操作
- `payment_service.py` - 支付处理
- `subscription_receipt_verification.py` - iOS收据验证

**前端服务**：
- `subscription.js` - 订阅前端逻辑（设备ID自动登录）
- `payment.js` - 支付前端逻辑

**iOS集成**：
- 使用 StoreKit 2（iOS 15+）
- 通过 `/api/subscription/verify-receipt` 验证收据

### 5.4 用户认证

**设备ID自动登录**：
- iOS App：自动生成设备ID并注册
- Web端：使用 localStorage 存储设备ID
- 后端：通过 `/api/auth/register` 自动注册并返回token

**JWT Token**：
- 用于API认证
- 存储在 localStorage（Web）或 Capacitor Preferences（App）

### 5.5 当前状态

**✅ 已完成**：
- 数据库设计和初始化
- 后端API实现
- 前端订阅UI和逻辑
- 设备ID自动登录
- iOS收据验证接口
- Web支付接口（微信/支付宝，待集成）

**⚠️ 进行中**：
- iOS App内购集成（StoreKit 2）
- Web支付集成（微信/支付宝）

**📋 待办**：
- 完成iOS App内购测试
- 完成Web支付集成
- 测试端到端购买流程

---

## 六、iOS App开发

### 6.1 技术栈

**框架**：Capacitor 8.0  
**语言**：Swift + Objective-C  
**构建工具**：Xcode + Swift Package Manager

### 6.2 项目配置

**Capacitor配置**：`capacitor.config.json`
```json
{
  "appId": "com.beatsync.app",
  "appName": "BeatSync",
  "webDir": "web_service/frontend",
  "server": {
    "cleartext": true,
    "allowNavigation": ["124.221.58.149"]
  }
}
```

**Bundle ID**：`com.beatsync.app.dev`（开发版）

### 6.3 已安装的Capacitor插件

- `@capacitor/camera` - 相机功能（未使用）
- `@capacitor/filesystem` - 文件系统操作
- `@capacitor/share` - 原生分享功能（当前下载方案）

### 6.4 下载功能实现

**当前方案**：使用Capacitor Share插件
- 下载视频到Documents目录
- 使用Share插件打开原生分享菜单
- 用户手动选择"保存到相册"

**代码位置**：`web_service/frontend/script.js`
- `downloadFileNativeApp()`: 原生App下载逻辑
- `isCapacitorNative`: 全局变量，检测是否为原生环境

### 6.5 已知问题

**问题1：应用启动时SIGKILL崩溃** ⚠️ **当前最紧急**

**症状**：应用在启动时被系统强制终止，出现 `Thread 1: signal SIGKILL` 错误，发生在 `dyld`（动态链接器）阶段。

**可能原因**：
1. 启动超时（Watchdog终止）
2. 签名/证书问题
3. 动态库加载失败（Capacitor或插件）
4. 内存问题
5. Bridging Header配置问题

**已尝试的修复**：
- ✅ 修复了 `App-Bridging-Header.h`，添加了 `#import <Capacitor/Capacitor.h>`
- ✅ 检查了签名配置
- ✅ 清理了构建缓存

**待排查**：
- 检查插件注册问题
- 临时禁用 SaveToGalleryPlugin（已禁用但文件仍存在）
- 检查设备日志获取详细错误信息
- 使用模拟器测试

**相关文档**：
- `docs/mobile/FIX_SIGKILL_LAUNCH_ERROR.md`
- `docs/mobile/QUICK_FIX_SIGKILL.md`
- `docs/mobile/FIX_PLUGIN_LOADING_CRASH.md`

**问题2：自定义SaveToGallery插件无法注册**

**原因**：Capacitor 8的插件注册机制变化，自动发现失败

**当前状态**：已弃用自定义插件，使用Share插件作为回退

**注意**：SaveToGallery插件文件仍存在于`ios/App/SaveToGalleryPlugin.swift`和`ios/Plugins/SaveToGallery/`，但未在代码中使用

**问题3：UI布局修改后App端无变化**

**可能原因**：
- Service Worker缓存
- Capacitor WebView缓存
- CSS未正确加载
- 需要重新构建App

**已尝试方案**：
- 更新CSS/JS版本号
- 更新Service Worker版本
- 调整CSS选择器和优先级

---

## 七、部署情况

### 7.1 前端部署（GitHub Pages）

**地址**：`https://scarlettyellow.github.io/BeatSync/`  
**配置**：自动从 `main` 分支部署  
**文件位置**：`web_service/frontend/` 目录下的静态文件

### 7.2 后端部署（腾讯云轻量应用服务器）

**地址**：
- HTTP（App）：`http://124.221.58.149`
- HTTPS（Web）：`https://beatsync.site`（域名已备案）

**配置**：Nginx反向代理 + systemd服务管理

**环境**：
- Python 3.x
- 腾讯云轻量应用服务器
- 手动部署（通过SSH和部署脚本）

**性能优势**：
- 相比Render免费tier，性能大幅提升
- 支持并行处理模式
- 处理时间：2-4分钟（相比Render的10-20分钟）

**部署文档**：`docs/deployment/TENCENT_CLOUD_DEPLOYMENT_GUIDE.md`

### 7.3 部署历史

**已迁移**：从Render迁移到腾讯云轻量应用服务器
- **原因**：Render免费tier性能受限，处理时间过长（10-20分钟）
- **当前状态**：已成功迁移，性能大幅提升

---

## 八、当前问题和待办事项

### 8.1 高优先级 ⚠️

**1. 解决iOS App启动崩溃问题（SIGKILL）**

**问题**：应用在启动时被系统强制终止

**建议排查步骤**：
1. 查看设备日志（Window → Devices and Simulators → Open Console）
2. 检查插件注册问题
3. 临时禁用所有自定义插件
4. 使用模拟器测试
5. 检查签名和证书配置

**相关文档**：
- `docs/mobile/FIX_SIGKILL_LAUNCH_ERROR.md`
- `docs/mobile/QUICK_FIX_SIGKILL.md`
- `docs/mobile/FIX_PLUGIN_LOADING_CRASH.md`

**2. 完成iOS App内购测试**

**状态**：后端API已实现，前端逻辑已实现，需要测试完整流程

**待测试**：
- StoreKit 2产品配置
- 购买流程
- 收据验证
- 订阅状态更新

### 8.2 中优先级

**3. 完成Web支付集成**

**状态**：后端接口已实现，需要集成微信/支付宝SDK

**4. 优化iOS App下载体验**

**当前**：使用Share插件，用户需手动选择"保存到相册"

**理想**：直接保存到相册（需要自定义插件或使用其他方案）

### 8.3 低优先级

**5. 算法优化**

- 研究特征层策略优化
- 改进对齐算法精度
- 处理特殊样本

**6. 文档完善**

- 更新用户使用指南
- 补充API文档
- 记录更多故障排除案例

---

## 九、技术决策历史

### 9.1 性能优化

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

### 9.2 部署迁移

**从Render迁移到腾讯云**：
- **原因**：Render免费tier性能受限
- **结果**：处理时间从10-20分钟降至2-4分钟

### 9.3 订阅系统设计

**设备ID自动登录**：
- 无需用户手动注册
- 自动生成设备ID并注册
- 多端同步（iOS和Web共享同一套系统）

**零耦合设计**：
- 订阅系统与现有功能完全解耦
- 订阅系统不可用时，现有功能仍可用

---

## 十、重要文件和配置

### 10.1 核心代码文件

**后端**：
- `web_service/backend/main.py` - 主应用文件（1800+行）
- `web_service/backend/subscription_service.py` - 订阅服务
- `web_service/backend/subscription_db.py` - 数据库操作

**前端**：
- `web_service/frontend/script.js` - 前端逻辑（4500+行）
- `web_service/frontend/subscription.js` - 订阅前端逻辑
- `web_service/frontend/payment.js` - 支付前端逻辑

**iOS**：
- `ios/App/App/AppDelegate.swift` - 应用委托
- `ios/App/App/Info.plist` - 应用配置
- `ios/App/App-Bridging-Header.h` - Bridging Header

### 10.2 配置文件

**Capacitor**：`capacitor.config.json`  
**iOS项目**：`ios/App/App.xcodeproj/`  
**后端依赖**：`web_service/backend/requirements.txt`

### 10.3 数据库

**订阅数据库**：`data/subscription.db`（SQLite）

**表结构**：
- `users` - 用户表
- `subscriptions` - 订阅表
- `download_credits` - 下载次数表
- `payment_records` - 支付记录表
- `whitelist` - 白名单表

---

## 十一、调试和故障排除

### 11.1 本地开发环境

**启动后端**：
```bash
cd web_service/backend
./start_and_wait.sh
```

**启动前端**：
```bash
cd web_service/frontend
./start_frontend.sh
```

**同步iOS**：
```bash
npx cap sync ios
npx cap open ios
```

### 11.2 常见问题

**Q1: 上传文件卡住怎么办？**
- 检查后端是否运行：`curl http://localhost:8000/api/health`
- 查看浏览器控制台日志
- 查看后端终端日志

**Q2: iOS App启动崩溃？**
- 查看设备日志（Window → Devices and Simulators → Open Console）
- 检查签名配置
- 清理构建缓存：`rm -rf ~/Library/Developer/Xcode/DerivedData`
- 参考：`docs/mobile/FIX_SIGKILL_LAUNCH_ERROR.md`

**Q3: 订阅功能不工作？**
- 检查后端服务是否运行
- 检查数据库是否初始化
- 查看浏览器控制台日志
- 参考：`docs/subscription/` 目录下的文档

### 11.3 日志位置

**后端日志**：
- 本地：终端输出
- 服务器：`sudo journalctl -u beatsync -f`

**前端日志**：
- 浏览器控制台（F12）

**iOS日志**：
- Xcode控制台
- 设备日志（Window → Devices and Simulators → Open Console）

---

## 十二、重要文档索引

### 12.1 项目文档

- `README.md` - 项目主文档
- `docs/project/PROJECT_STATUS.md` - 项目状态
- `docs/project/PROJECT_STRUCTURE.md` - 项目结构
- `docs/project/AGENT_HANDOVER_2025.md` - 本交接文档

### 12.2 订阅系统文档

- `docs/subscription/SUBSCRIPTION_SYSTEM_DESIGN.md` - 订阅系统设计（1259行）
- `docs/subscription/` - 100+个订阅系统实现文档

### 12.3 移动端文档

- `docs/mobile/FIX_SIGKILL_LAUNCH_ERROR.md` - SIGKILL错误修复
- `docs/mobile/QUICK_FIX_SIGKILL.md` - 快速修复指南
- `docs/mobile/FIX_PLUGIN_LOADING_CRASH.md` - 插件加载崩溃修复

### 12.4 部署文档

- `docs/deployment/TENCENT_CLOUD_DEPLOYMENT_GUIDE.md` - 腾讯云部署指南
- `docs/deployment/QUICK_DEPLOYMENT_STEPS.md` - 快速部署步骤

---

## 十三、交接检查清单

新接手的Agent应该：

- [ ] 阅读本交接文档
- [ ] 了解项目结构和核心功能
- [ ] 熟悉Web服务架构
- [ ] 了解订阅系统设计
- [ ] 了解iOS App开发状态和当前问题
- [ ] 设置本地开发环境
- [ ] 测试核心处理程序
- [ ] 测试Web服务（本地）
- [ ] 查看当前待办事项（特别是iOS App启动崩溃问题）
- [ ] 了解已知问题和解决方案
- [ ] 熟悉调试技巧和日志查看
- [ ] 阅读订阅系统设计文档

---

## 十四、联系和资源

### 14.1 项目仓库

- **GitHub**: `https://github.com/ScarlettYellow/BeatSync`
- **前端地址**: `https://scarlettyellow.github.io/BeatSync/`
- **后端地址**: 
  - HTTP（App）: `http://124.221.58.149`
  - HTTPS（Web）: `https://beatsync.site`

### 14.2 关键代码文件

- **并行处理器**: `beatsync_parallel_processor.py`
- **后端API**: `web_service/backend/main.py`
- **前端逻辑**: `web_service/frontend/script.js`
- **订阅前端**: `web_service/frontend/subscription.js`

---

**文档维护**：每次重要变更后，请更新本文档的相关章节。

**最后更新**：2025-01-06  
**更新内容**：
- 添加订阅系统章节
- 更新iOS App开发状态和当前问题
- 添加SIGKILL崩溃问题说明
- 更新待办事项优先级

