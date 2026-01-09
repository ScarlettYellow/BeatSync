# BeatSync 项目完整交接文档

> **文档目的**：为新接手的AI Agent提供完整的项目历史上下文，确保能够流畅地继续处理项目后续工作。

**最后更新**：2025-01-06  
**项目状态**：✅ 核心功能已完成，Web服务已部署，订阅系统已实现，iOS App开发进行中（当前遇到启动崩溃问题）

---

## 📋 目录

1. [项目概述](#一项目概述)
2. [技术架构](#二技术架构)
3. [核心功能](#三核心功能)
4. [订阅系统](#四订阅系统)
5. [Web服务](#五web服务)
6. [iOS App开发](#六ios-app开发)
7. [部署情况](#七部署情况)
8. [当前问题和待办事项](#八当前问题和待办事项)
9. [开发环境设置](#九开发环境设置)
10. [重要技术细节](#十重要技术细节)
11. [常见问题快速参考](#十一常见问题快速参考)

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

### 1.3 使用场景

- 街舞课堂结课视频制作
- 现场表演视频音频优化
- 音乐视频音质提升
- 任何需要音频替换的视频处理

---

## 二、技术架构

### 2.1 整体架构

```
┌─────────────────┐         ┌─────────────────┐
│   iOS App       │         │   Web Frontend  │
│  (Capacitor)    │         │  (GitHub Pages) │
└────────┬────────┘         └────────┬────────┘
         │                            │
         │  HTTP/HTTPS API            │  HTTPS API
         │                            │
         └────────────┬───────────────┘
                      │
         ┌────────────▼────────────┐
         │   FastAPI Backend       │
         │  (腾讯云服务器)          │
         │                         │
         │  - 视频处理              │
         │  - 订阅管理              │
         │  - 支付集成              │
         │  - 用户认证              │
         │  - 下载次数管理          │
         └────────────┬────────────┘
                      │
         ┌────────────▼────────────┐
         │   SQLite Database      │
         │  (subscription.db)      │
         │                         │
         │  - users                │
         │  - subscriptions        │
         │  - download_credits     │
         │  - payment_records      │
         │  - whitelist            │
         └─────────────────────────┘
```

### 2.2 技术栈

**后端**：
- Python 3.7+
- FastAPI (Web框架)
- SQLite (订阅系统数据库)
- FFmpeg (视频处理)
- librosa (音频处理)
- numpy, soundfile, opencv-python

**前端**：
- 纯HTML/CSS/JavaScript (无框架)
- Capacitor 8 (iOS App)
- Service Worker (PWA支持)

**iOS App**：
- Capacitor 8.0.0
- Swift 5.0
- StoreKit 2 (内购)
- Xcode 15+

---

## 三、核心功能

### 3.1 核心处理程序

#### 并行处理器（推荐）⭐

**文件**：`beatsync_parallel_processor.py`

**功能**：同时使用modular版本和V2版本处理样本，生成两个输出视频供用户选择。

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

#### Modular版本

**文件**：`beatsync_fine_cut_modular.py`

**对齐算法**：多策略融合算法（MFCC、Chroma、Spectral Contrast、Spectral Rolloff）

#### V2版本

**文件**：`beatsync_badcase_fix_trim_v2.py`

**对齐算法**：简化滑动窗口算法（基于节拍检测）

---

## 四、订阅系统

### 4.1 系统设计

**设计理念**：
- ✅ **为下载付费**：用户只为满意的结果付费
- ✅ **处理免费**：允许用户无限次处理
- ✅ **多端同步**：iOS App 和网站共享同一套订阅系统
- ✅ **白名单功能**：管理员可添加用户到白名单
- ✅ **零耦合设计**：订阅系统与现有功能完全解耦

### 4.2 套餐设计

#### 免费体验套餐
- **限制**：每周可免费下载2个满意作品
- **处理次数**：无限次（仅限制下载）

#### 基础版付费套餐
- **连续包月**：15元/月，50次下载/月
- **连续包年**：99元/年，600次下载/年

#### 高级版付费套餐
- **连续包月**：69元/月，1000次下载/月
- **连续包年**：499元/年，12000次下载/年

#### 购买下载次数套餐（一次性）
- **5元/10次**
- **9元/20次**
- **20元/50次**

### 4.3 技术实现

**后端API**：
- `POST /api/auth/register` - 用户注册（设备ID自动注册）
- `POST /api/auth/login` - 用户登录
- `GET /api/subscription/products` - 获取订阅套餐列表
- `POST /api/subscription/purchase` - 购买订阅（iOS内购）
- `POST /api/subscription/verify-receipt` - 验证iOS收据
- `GET /api/subscription/status` - 获取订阅状态
- `POST /api/subscription/restore-purchases` - 恢复购买
- `GET /api/credits/check` - 检查下载次数
- `POST /api/credits/consume` - 消费下载次数

**数据库**：
- SQLite数据库：`web_service/backend/subscription.db`
- 表结构：users, subscriptions, download_credits, payment_records, whitelist

**前端实现**：
- `web_service/frontend/subscription.js` - 订阅服务
- `web_service/frontend/payment.js` - 支付服务（Web支付，当前暂停）
- 设备ID自动登录机制

**iOS实现**：
- StoreKit 2 内购
- 收据验证（后端验证）
- 自动恢复购买

### 4.4 当前状态

**✅ 已完成**：
- 后端API全部实现
- 数据库设计和初始化
- 前端订阅UI和逻辑
- 设备ID自动登录
- iOS内购集成（StoreKit 2）
- 收据验证流程

**⚠️ 已知问题**：
- iOS App启动崩溃（SIGKILL）- 当前最紧急问题
- `/api/auth/register` 端点已在服务器上添加（2025-01-06修复）

**📋 待办事项**：
- 解决iOS App启动崩溃问题
- 测试完整的购买流程
- Web支付功能（当前暂停，优先iOS）

---

## 五、Web服务

### 5.1 后端API（FastAPI）

**文件**：`web_service/backend/main.py`

**主要端点**：
- `GET /api/health` - 健康检查
- `POST /api/upload` - 上传视频文件
- `POST /api/process` - 提交处理任务
- `GET /api/status/{task_id}` - 查询任务状态
- `GET /api/download/{task_id}?version=modular|v2` - 下载处理结果

**订阅相关端点**：见[订阅系统](#四订阅系统)

**关键配置**：
```python
UPLOAD_DIR = project_root / "outputs" / "web_uploads"
OUTPUT_DIR = project_root / "outputs" / "web_outputs"
CLEANUP_AGE_HOURS = 24  # 上传文件保留时间
WEB_OUTPUTS_RETENTION_DAYS = 3  # Web输出保留3天
```

### 5.2 前端（HTML/JS）

**文件**：
- `web_service/frontend/index.html` - 主页面
- `web_service/frontend/script.js` - 前端逻辑
- `web_service/frontend/subscription.js` - 订阅服务
- `web_service/frontend/style.css` - 样式文件

**环境检测**：
- 自动检测本地开发环境（`localhost` 或 `127.0.0.1`）
- 本地环境：使用 `http://localhost:8000`
- 生产环境：使用 `https://beatsync.site` 或 `http://124.221.58.149`
- Capacitor原生App环境：强制使用 `http://124.221.58.149`

---

## 六、iOS App开发

### 6.1 项目配置

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

### 6.2 iOS项目结构

```
ios/
├── App/
│   ├── App/
│   │   ├── AppDelegate.swift          # 应用委托
│   │   ├── App-Bridging-Header.h     # Bridging Header（已添加Capacitor导入）
│   │   ├── Info.plist                 # 应用配置
│   │   └── Assets.xcassets/          # 图标和启动画面
│   ├── SaveToGalleryPlugin.swift     # 自定义插件（已禁用，文件仍存在）
│   ├── SaveToGalleryPlugin.m         # 插件注册（已禁用）
│   └── CapApp-SPM/                    # Swift Package Manager配置
└── Plugins/                           # 自定义插件目录
```

### 6.3 已安装的Capacitor插件

- `@capacitor/camera` - 相机功能（未使用）
- `@capacitor/filesystem` - 文件系统操作
- `@capacitor/share` - 原生分享功能（当前下载方案）

### 6.4 当前问题：iOS App启动崩溃

**问题描述**：
- 应用启动时出现 `Thread 1: signal SIGKILL` 错误
- 发生在 `dyld`（动态链接器）阶段
- 错误位置：`dyld`lldb_image_notifier`

**可能原因**：
1. 启动超时（Watchdog终止）
2. 签名/证书问题
3. 动态库加载失败
4. 插件注册问题
5. Bridging Header配置问题（已修复）

**已尝试的修复**：
- ✅ 修复了 `App-Bridging-Header.h`，添加了 `#import <Capacitor/Capacitor.h>`
- ✅ 检查了插件注册（SaveToGalleryPlugin已禁用）
- ⚠️ 需要进一步排查：清理构建缓存、检查签名配置

**修复文档**：
- `docs/mobile/FIX_SIGKILL_LAUNCH_ERROR.md` - 详细诊断指南
- `docs/mobile/QUICK_FIX_SIGKILL.md` - 快速修复步骤
- `docs/mobile/FIX_PLUGIN_LOADING_CRASH.md` - 插件加载问题修复

---

## 七、部署情况

### 7.1 前端部署（GitHub Pages）

**地址**：`https://scarlettyellow.github.io/BeatSync/`  
**配置**：自动从 `main` 分支部署  
**文件位置**：`web_service/frontend/` 目录下的静态文件

### 7.2 后端部署（腾讯云轻量应用服务器）

**地址**：
- HTTP：`http://124.221.58.149`（Capacitor App使用）
- HTTPS：`https://beatsync.site` 或 `https://124.221.58.149`（Web/PWA使用）
- 本地开发：`http://localhost:8000`

**配置**：
- Nginx反向代理
- systemd服务管理（服务名：`beatsync`）
- Python 3.x
- 手动部署（通过SSH和部署脚本）

**性能优势**：
- 相比Render免费tier，性能大幅提升
- 支持并行处理模式
- 处理时间：2-4分钟（相比Render的10-20分钟）

**部署文档**：
- `docs/deployment/TENCENT_CLOUD_DEPLOYMENT_GUIDE.md`
- `docs/deployment/QUICK_DEPLOYMENT_STEPS.md`

### 7.3 最近修复（2025-01-06）

**问题**：`/api/auth/register` 端点返回404

**原因**：服务器代码版本较旧，缺少该端点

**解决方案**：在服务器上直接添加端点
- 使用Python脚本：`scripts/deployment/add_auth_register_endpoint.py`
- 端点已添加到 `main.py` 第1003行
- 验证：端点正常工作，返回 `user_id` 和 `token`

**修复文档**：
- `docs/deployment/ADD_AUTH_REGISTER_ENDPOINT.md`
- `docs/deployment/QUICK_ADD_AUTH_REGISTER.md`

---

## 八、当前问题和待办事项

### 8.1 紧急问题 ⚠️

**1. iOS App启动崩溃（SIGKILL）**

**状态**：进行中  
**优先级**：最高

**问题描述**：
- 应用启动时被系统强制终止
- 错误：`Thread 1: signal SIGKILL`
- 发生在 `dyld` 阶段

**已尝试**：
- ✅ 修复了 Bridging Header
- ⚠️ 需要进一步排查：清理构建缓存、检查签名、临时禁用插件

**下一步**：
1. 清理 DerivedData 和构建缓存
2. 检查签名配置
3. 如果仍失败，临时禁用 SaveToGalleryPlugin
4. 查看设备日志获取详细错误信息

**相关文档**：
- `docs/mobile/FIX_SIGKILL_LAUNCH_ERROR.md`
- `docs/mobile/QUICK_FIX_SIGKILL.md`
- `docs/mobile/FIX_PLUGIN_LOADING_CRASH.md`

### 8.2 高优先级待办事项

**1. 解决iOS App启动崩溃**
- 见上述紧急问题

**2. 测试完整的订阅购买流程**
- iOS内购流程测试
- 收据验证测试
- 下载次数消费测试

**3. 验证线上服务稳定性**
- 测试腾讯云服务器的处理性能
- 监控处理时间和成功率
- 优化超时和错误处理

### 8.3 中优先级待办事项

**1. 域名备案完成后的配置更新**
- 域名备案通过后，将IP地址改为域名
- 更新前端API地址配置
- 配置HTTPS证书

**2. 用户体验优化**
- 改进前端错误提示
- 添加处理进度条
- 优化移动端体验

### 8.4 低优先级待办事项

**1. 算法优化**
- 研究特征层策略优化
- 改进对齐算法精度
- 处理特殊样本

**2. Web支付功能**
- 当前暂停，优先iOS
- 微信支付集成
- 支付宝支付集成

**3. 文档完善**
- 更新用户使用指南
- 补充API文档
- 记录更多故障排除案例

---

## 九、开发环境设置

### 9.1 系统要求

- Python 3.7+
- FFmpeg（必须安装并在PATH中）
- Node.js 16+（Capacitor）
- Xcode 15+（iOS开发）

### 9.2 安装依赖

**核心程序**：
```bash
pip install numpy soundfile librosa opencv-python
```

**Web服务后端**：
```bash
cd web_service/backend
pip install -r requirements.txt
```

**Capacitor**：
```bash
npm install
```

### 9.3 本地开发流程

**1. 启动后端**：
```bash
cd web_service/backend
./start_and_wait.sh
```

**2. 启动前端**：
```bash
cd web_service/frontend
./start_frontend.sh
```

**3. iOS App开发**：
```bash
# 同步前端代码到iOS
npx cap sync ios

# 打开Xcode项目
npx cap open ios
```

---

## 十、重要技术细节

### 10.1 对齐算法

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

### 10.2 订阅系统实现

**设备ID自动登录**：
- 前端生成设备ID（UUID）
- 存储在 `localStorage` 和 `Capacitor.Preferences`
- 自动调用 `/api/auth/register` 注册
- 获取 `user_id` 和 `token`
- Token存储在 `localStorage`

**下载次数管理**：
- 检查白名单（免费）
- 检查订阅（自动续订）
- 检查购买次数（一次性）
- 检查免费试用（每周2次）
- 消费时按优先级扣除

### 10.3 关键文件说明

**后端**：
- `web_service/backend/main.py` - 主应用文件（1807行）
- `web_service/backend/subscription_service.py` - 订阅服务
- `web_service/backend/subscription_db.py` - 数据库操作
- `web_service/backend/subscription_receipt_verification.py` - 收据验证

**前端**：
- `web_service/frontend/script.js` - 主逻辑（4598行）
- `web_service/frontend/subscription.js` - 订阅服务（1000+行）
- `web_service/frontend/payment.js` - 支付服务（Web支付，当前暂停）

**iOS**：
- `ios/App/App/AppDelegate.swift` - 应用委托
- `ios/App/App/App-Bridging-Header.h` - Bridging Header（已修复）
- `ios/App/App/Info.plist` - 应用配置

---

## 十一、常见问题快速参考

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

### Q2: iOS App启动崩溃怎么办？

1. 清理 DerivedData：`rm -rf ~/Library/Developer/Xcode/DerivedData`
2. 在Xcode中：Product → Clean Build Folder (Shift+Cmd+K)
3. 在设备上删除应用
4. 检查签名配置
5. 查看设备日志获取详细错误信息

**详细指南**：`docs/mobile/QUICK_FIX_SIGKILL.md`

### Q3: 订阅系统如何工作？

1. 用户打开App，自动生成设备ID
2. 自动调用 `/api/auth/register` 注册
3. 获取 `user_id` 和 `token`
4. 购买订阅时，使用StoreKit 2
5. 收据发送到后端验证
6. 后端更新订阅状态和下载次数

**详细文档**：`docs/subscription/SUBSCRIPTION_SYSTEM_DESIGN.md`

### Q4: 如何部署后端代码到服务器？

```bash
# 方法1：使用Git（如果网络正常）
ssh user@124.221.58.149
cd /opt/beatsync
git pull origin main
sudo systemctl restart beatsync

# 方法2：使用scp（如果Git失败）
scp web_service/backend/main.py user@124.221.58.149:/opt/beatsync/web_service/backend/
ssh user@124.221.58.149
sudo systemctl restart beatsync
```

**详细文档**：`docs/deployment/TENCENT_CLOUD_DEPLOYMENT_GUIDE.md`

### Q5: 如何测试订阅功能？

**本地测试**：
1. 启动后端服务
2. 在浏览器中打开前端
3. 查看订阅状态
4. 测试设备ID自动注册

**iOS测试**：
1. 在Xcode中运行App
2. 使用Sandbox测试账号
3. 测试购买流程
4. 验证收据

**详细文档**：`docs/subscription/IOS_LOCAL_TESTING_GUIDE.md`

---

## 十二、重要文档索引

### 项目文档
- `README.md` - 项目主文档
- `docs/project/PROJECT_STATUS.md` - 项目状态
- `docs/project/PROJECT_STRUCTURE.md` - 项目结构
- `docs/project/AGENT_HANDOVER.md` - 旧版交接文档

### 订阅系统文档
- `docs/subscription/SUBSCRIPTION_SYSTEM_DESIGN.md` - 订阅系统设计（1259行）
- `docs/subscription/BACKEND_API_IMPLEMENTATION.md` - 后端API实现
- `docs/subscription/IOS_LOCAL_TESTING_GUIDE.md` - iOS测试指南

### 部署文档
- `docs/deployment/TENCENT_CLOUD_DEPLOYMENT_GUIDE.md` - 腾讯云部署指南
- `docs/deployment/QUICK_DEPLOYMENT_STEPS.md` - 快速部署步骤
- `docs/deployment/ADD_AUTH_REGISTER_ENDPOINT.md` - 添加认证端点

### 故障排除文档
- `docs/mobile/FIX_SIGKILL_LAUNCH_ERROR.md` - iOS启动崩溃修复
- `docs/mobile/QUICK_FIX_SIGKILL.md` - 快速修复步骤
- `docs/troubleshooting/` - 其他故障排除文档

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
- [ ] 查看当前紧急问题（iOS App启动崩溃）
- [ ] 了解已知问题和解决方案
- [ ] 熟悉调试技巧和日志查看

---

**文档维护**：每次重要变更后，请更新本文档的相关章节。

**最后更新**：2025-01-06  
**更新内容**：
- 添加订阅系统完整说明
- 更新iOS App当前问题（SIGKILL崩溃）
- 添加最近修复记录（/api/auth/register端点）
- 更新待办事项和优先级
- 添加常见问题快速参考
