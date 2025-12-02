# 项目服务架构概览

> **目的**：说明BeatSync项目的服务架构和各组件角色

---

## 当前服务架构

### 架构图

```
┌─────────────────┐
│   用户浏览器    │
└────────┬────────┘
         │ HTTPS
         ▼
┌─────────────────────────────────┐
│      GitHub Pages (前端)        │
│  https://scarlettyellow.github.io/BeatSync/ │
└────────┬────────────────────────┘
         │ HTTPS API请求
         ▼
┌─────────────────────────────────┐
│   腾讯云轻量应用服务器 (后端)    │
│      IP: 124.221.58.149         │
│                                 │
│  ┌──────────────────────────┐  │
│  │   Nginx (反向代理)       │  │
│  │   端口: 443 (HTTPS)      │  │
│  └──────────┬───────────────┘  │
│             │                  │
│             ▼                  │
│  ┌──────────────────────────┐  │
│  │   FastAPI (后端服务)     │  │
│  │   端口: 8000 (HTTP)      │  │
│  │   systemd服务: beatsync  │  │
│  └──────────────────────────┘  │
│                                 │
│  ┌──────────────────────────┐  │
│  │   视频处理程序            │  │
│  │   - FFmpeg               │  │
│  │   - Python处理脚本       │  │
│  └──────────────────────────┘  │
└─────────────────────────────────┘
```

---

## 各组件角色

### 1. GitHub Pages（前端）

**角色**：静态网站托管

**功能**：
- 托管前端HTML/CSS/JavaScript文件
- 提供用户界面
- 处理文件上传、任务提交、状态查询、结果下载

**访问地址**：
- https://scarlettyellow.github.io/BeatSync/

**特点**：
- ✅ 免费
- ✅ 自动部署（Git推送后自动更新）
- ✅ HTTPS支持
- ❌ 只能托管静态文件（不能运行后端代码）

**部署方式**：
- 代码推送到GitHub后自动部署
- 通常1-3分钟完成部署

---

### 2. Render（已弃用，需要停用）

**角色**：之前使用的后端服务托管平台

**状态**：❌ **已不再使用，但服务仍在运行**

**历史**：
- 之前用于托管FastAPI后端服务
- 已迁移到腾讯云服务器

**当前**：
- ❌ 不再使用，所有后端服务都在腾讯云服务器上
- ⚠️ **但Render服务仍在运行，会自动部署**
- ⚠️ **建议暂停或删除Render服务，避免资源浪费**

**操作建议**：
- 登录Render控制台：https://dashboard.render.com/
- 找到服务：`beatsync-backend`
- 暂停服务或禁用自动部署
- 详细步骤见：`docs/deployment/DEPRECATE_RENDER.md`

---

### 3. 腾讯云轻量应用服务器（后端）

**角色**：后端服务托管和视频处理

**功能**：
- 托管FastAPI后端服务
- 处理视频上传
- 执行视频处理任务
- 提供API接口
- 存储上传和处理结果

**服务器信息**：
- **IP地址**：124.221.58.149
- **配置**：4核4GB 3M带宽
- **系统**：Ubuntu 22.04 LTS

**组件**：

#### 3.1 Nginx（反向代理）

**角色**：HTTPS反向代理

**功能**：
- 接收HTTPS请求（端口443）
- 转发到FastAPI后端（端口8000）
- 提供SSL/TLS加密
- HTTP自动重定向到HTTPS

**配置位置**：
- `/etc/nginx/sites-available/beatsync`
- `/etc/nginx/ssl/`（SSL证书）

**管理命令**：
```bash
sudo systemctl status nginx
sudo systemctl restart nginx
```

---

#### 3.2 FastAPI（后端服务）

**角色**：API服务

**功能**：
- 提供RESTful API接口
- 处理文件上传
- 管理处理任务
- 提供健康检查和API文档

**服务信息**：
- **端口**：8000（内部，通过Nginx访问）
- **systemd服务**：beatsync
- **工作目录**：`/opt/beatsync/web_service/backend`

**API端点**：
- `/api/health` - 健康检查
- `/api/upload` - 文件上传
- `/api/process` - 提交处理任务
- `/api/status/{task_id}` - 查询任务状态
- `/api/download/{task_id}` - 下载处理结果
- `/api/preview/{task_id}` - 预览处理结果
- `/docs` - API文档

**管理命令**：
```bash
sudo systemctl status beatsync
sudo systemctl restart beatsync
```

---

#### 3.3 视频处理程序

**角色**：视频处理引擎

**功能**：
- 执行视频对齐和音轨替换
- 使用FFmpeg进行视频编码
- 使用Librosa进行音频分析

**处理程序**：
- `beatsync_parallel_processor.py` - 并行处理器（推荐）
- `beatsync_fine_cut_modular.py` - Modular版本
- `beatsync_badcase_fix_trim_v2.py` - V2版本

**依赖**：
- FFmpeg（视频处理）
- Python库（numpy, librosa, soundfile等）

---

## 数据流向

### 1. 用户上传视频

```
用户浏览器
  ↓ (HTTPS POST)
GitHub Pages前端
  ↓ (HTTPS POST)
Nginx (124.221.58.149:443)
  ↓ (HTTP POST)
FastAPI后端 (127.0.0.1:8000)
  ↓ (保存文件)
服务器磁盘 (/opt/beatsync/web_uploads/)
```

---

### 2. 提交处理任务

```
用户浏览器
  ↓ (HTTPS POST)
GitHub Pages前端
  ↓ (HTTPS POST)
Nginx
  ↓ (HTTP POST)
FastAPI后端
  ↓ (启动后台线程)
视频处理程序
  ↓ (处理视频)
服务器磁盘 (/opt/beatsync/web_outputs/)
```

---

### 3. 查询任务状态

```
用户浏览器
  ↓ (HTTPS GET)
GitHub Pages前端
  ↓ (HTTPS GET)
Nginx
  ↓ (HTTP GET)
FastAPI后端
  ↓ (读取任务状态)
task_status.json
  ↓ (返回JSON)
用户浏览器
```

---

### 4. 下载处理结果

```
用户浏览器
  ↓ (HTTPS GET)
GitHub Pages前端
  ↓ (HTTPS GET)
Nginx
  ↓ (HTTP GET)
FastAPI后端
  ↓ (读取文件)
服务器磁盘 (/opt/beatsync/web_outputs/)
  ↓ (流式传输)
用户浏览器
```

---

## 文件存储位置

### 服务器文件结构

```
/opt/beatsync/
├── web_service/
│   ├── frontend/          # 前端文件（已部署到GitHub Pages）
│   └── backend/
│       ├── main.py        # FastAPI后端主程序
│       └── requirements.txt
├── web_uploads/           # 上传的视频文件
├── web_outputs/           # 处理结果视频文件
├── outputs/
│   └── logs/              # 性能日志
└── logs/                  # 其他日志
```

---

## 服务依赖关系

### 启动顺序

1. **系统启动**
   - Ubuntu系统启动

2. **Nginx启动**
   - systemd自动启动Nginx服务
   - 监听443端口（HTTPS）

3. **FastAPI后端启动**
   - systemd自动启动beatsync服务
   - 监听8000端口（HTTP，内部）

4. **服务就绪**
   - 前端可以访问后端API
   - 用户可以上传和处理视频

---

## 安全配置

### HTTPS加密

- **前端到Nginx**：HTTPS（GitHub Pages → Nginx）
- **Nginx到后端**：HTTP（内部网络，127.0.0.1）
- **SSL证书**：自签名证书（浏览器会显示警告）

### 防火墙

- **443端口**：开放（HTTPS访问）
- **8000端口**：开放（可选，直接访问后端）

---

## 扩展性

### 当前架构限制

1. **单服务器**：所有服务在一台服务器上
2. **带宽限制**：3M带宽可能成为瓶颈
3. **存储限制**：服务器磁盘空间有限

### 未来扩展方向

1. **CDN加速**：使用CDN加速视频下载
2. **对象存储**：使用COS存储视频文件
3. **负载均衡**：多服务器部署（如果需要）
4. **数据库**：使用数据库存储任务状态（替代JSON文件）

---

## 总结

**当前架构**：
- **前端**：GitHub Pages（静态网站）
- **后端**：腾讯云服务器（FastAPI + Nginx）
- **Render**：已弃用，不再使用

**数据流**：
- 用户 → GitHub Pages → Nginx → FastAPI → 视频处理 → 结果返回

**特点**：
- 简单可靠
- 成本低（GitHub Pages免费，服务器按需付费）
- 易于维护

---

**最后更新**：2025-12-02

