# 测试脚本使用指南

## 📋 已创建的测试脚本

### 1. `test_daily_process_limit.py` - 每日处理次数上限测试

**功能**：
- 测试数据库设置
- 创建测试用户
- 模拟购买基础版订阅
- 测试每日处理次数上限检查
- 测试上限强制执行（第11次应该被拒绝）

**运行方式**：
```bash
cd web_service/backend
python3 test_daily_process_limit.py
```

**预期结果**：
- ✅ 数据库初始化成功
- ✅ 用户创建成功
- ✅ 订阅创建成功
- ✅ 前10次处理允许
- ✅ 第11次处理被拒绝（429错误）

---

### 2. `test_free_trial_new.py` - 免费体验测试（新逻辑）

**功能**：
- 测试新用户免费体验（前5次处理免费）
- 测试免费体验次数消费
- 测试免费体验用完后需要订阅

**运行方式**：
```bash
cd web_service/backend
python3 test_free_trial_new.py
```

**预期结果**：
- ✅ 新用户有5次免费体验
- ✅ 前5次可以免费处理
- ✅ 第6次需要订阅

---

## 🚀 快速开始

### 步骤 1：解决端口占用问题

**方法 1：使用修复脚本（推荐）**
```bash
cd web_service/backend
./fix_port_and_start.sh
```

**方法 2：手动处理**
```bash
# 查找占用端口的进程
lsof -i :8000

# 停止进程（替换 PID）
kill -9 <PID>

# 重新启动服务
cd web_service/backend
export SUBSCRIPTION_ENABLED=true
export SUBSCRIPTION_DB_PATH=./subscription.db
python3 main.py
```

### 步骤 2：运行测试脚本

**测试每日处理次数上限**：
```bash
cd web_service/backend
python3 test_daily_process_limit.py
```

**测试免费体验**：
```bash
cd web_service/backend
python3 test_free_trial_new.py
```

---

## 📊 测试结果解读

### 成功的标志

1. **数据库初始化**：
   - ✅ `process_logs` 表已创建
   - ✅ 索引已创建

2. **每日处理次数上限**：
   - ✅ 基础版：10次/天
   - ✅ 前10次允许处理
   - ✅ 第11次返回429错误

3. **免费体验**：
   - ✅ 新用户有5次免费体验
   - ✅ 前5次可以免费处理
   - ✅ 第6次需要订阅

---

## ⚠️ 注意事项

1. **测试数据清理**：
   - 测试脚本会自动清理测试数据
   - 不会影响真实用户数据

2. **数据库路径**：
   - 确保 `SUBSCRIPTION_DB_PATH` 环境变量正确设置
   - 默认路径：`./subscription.db`

3. **服务运行**：
   - 测试脚本可以独立运行（不需要服务运行）
   - API 集成测试需要服务运行

---

## 🔍 故障排查

### 问题 1：数据库表不存在

**错误**：`no such table: process_logs`

**解决方法**：
```bash
cd web_service/backend
python3 subscription_db.py
```

### 问题 2：导入错误

**错误**：`ModuleNotFoundError`

**解决方法**：
```bash
# 确保在正确的目录
cd web_service/backend

# 检查 Python 路径
python3 -c "import sys; print(sys.path)"
```

### 问题 3：端口占用

**错误**：`address already in use`

**解决方法**：
```bash
# 使用修复脚本
./fix_port_and_start.sh

# 或手动处理
lsof -i :8000
kill -9 <PID>
```

---

**开始测试吧！** 🚀
