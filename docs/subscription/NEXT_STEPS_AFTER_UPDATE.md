# 公测期套餐更新后的下一步行动

## ✅ 已完成的工作

1. ✅ 价格更新：基础版月付 4.8元/月
2. ✅ 产品ID更新：公测期产品ID
3. ✅ 免费体验逻辑：前5次处理免费
4. ✅ 每日处理次数上限检查：已实现
5. ✅ 加油包有效期：3个月

---

## 🚀 接下来需要做的事情

### 步骤 1：初始化数据库（重要！）⭐

**需要创建 `process_logs` 表**

运行数据库初始化：

```bash
cd web_service/backend
python3 subscription_db.py
```

或者如果数据库已存在，可以手动执行 SQL：

```sql
CREATE TABLE IF NOT EXISTS process_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    task_id TEXT NOT NULL,
    process_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE INDEX IF NOT EXISTS idx_process_logs_user_id ON process_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_process_logs_date ON process_logs(process_date);
CREATE INDEX IF NOT EXISTS idx_process_logs_user_date ON process_logs(user_id, process_date);
```

**验证**：
- 检查数据库文件是否存在
- 确认 `process_logs` 表已创建
- 确认索引已创建

---

### 步骤 2：重启后端服务

**确保新的代码生效**：

```bash
cd web_service/backend

# 停止旧服务
pkill -f "python3 main.py"

# 启动新服务（确保环境变量已设置）
export SUBSCRIPTION_ENABLED=true
export SUBSCRIPTION_DB_PATH=./subscription.db
export ADMIN_TOKEN=your_admin_token
export JWT_SECRET_KEY=your_jwt_secret
export APP_STORE_SHARED_SECRET=your_shared_secret

python3 main.py
```

**验证**：
- 检查服务是否正常启动
- 检查是否有错误日志
- 确认订阅系统已启用

---

### 步骤 3：测试功能

#### 3.1 测试数据库初始化

```bash
# 检查数据库表
sqlite3 data/subscription.db ".tables"

# 应该看到 process_logs 表
```

#### 3.2 测试每日处理次数上限

**测试场景**：
1. 创建一个测试用户
2. 购买基础版订阅（或模拟）
3. 连续提交11次处理请求
4. 第11次应该返回429错误

**测试脚本**（可以创建）：

```python
# test_daily_limit.py
import requests
import json

# 1. 创建用户并获取Token
# 2. 购买基础版订阅（或直接更新数据库）
# 3. 连续提交11次处理请求
# 4. 验证第11次返回429错误
```

#### 3.3 测试免费体验

**测试场景**：
1. 创建新用户（未购买订阅）
2. 提交处理请求
3. 应该可以处理（前5次免费）
4. 验证免费体验次数记录

#### 3.4 测试产品购买

**测试场景**：
1. 在 App Store Connect 中测试购买
2. 验证收据验证
3. 验证下载次数增加
4. 验证订阅状态更新

---

### 步骤 4：更新前端显示（如需要）

#### 4.1 更新产品价格显示

检查前端是否需要更新价格显示：
- `web_service/frontend/script.js` - 产品列表显示
- `web_service/frontend/index.html` - 静态价格显示（如有）

#### 4.2 更新产品列表

确保前端显示的产品列表与后端一致：
- 基础版月付：4.8元/月
- 高级版月付：19.9元/月
- 10次包：5元
- 20次包：9元

#### 4.3 添加每日处理次数显示（可选）

可以考虑在前端显示：
- 今日剩余处理次数
- 每日处理次数上限

---

### 步骤 5：iOS App 测试

#### 5.1 本地测试（StoreKit Configuration）

1. 在 Xcode 中启用 StoreKit Testing
2. 选择 `Products.storekit`
3. 运行 App 并测试产品列表获取
4. 测试购买流程

#### 5.2 沙盒测试（需要 App Store Connect）

1. 在设备上登录沙盒测试账号
2. 测试真实购买流程
3. 验证收据验证
4. 验证订阅状态更新

---

### 步骤 6：部署到生产环境

#### 6.1 数据库迁移

在生产服务器上：
1. 备份现有数据库
2. 运行数据库初始化脚本
3. 验证 `process_logs` 表已创建

#### 6.2 更新代码

1. 部署更新的代码
2. 重启后端服务
3. 验证服务正常运行

#### 6.3 环境变量配置

确保生产环境变量已设置：
```bash
export SUBSCRIPTION_ENABLED=true
export SUBSCRIPTION_DB_PATH=/path/to/subscription.db
export APP_STORE_SHARED_SECRET=your_production_secret
export ADMIN_TOKEN=your_production_admin_token
export JWT_SECRET_KEY=your_production_jwt_secret
```

---

## 📋 检查清单

### 数据库
- [ ] 运行数据库初始化脚本
- [ ] 验证 `process_logs` 表已创建
- [ ] 验证索引已创建

### 后端服务
- [ ] 重启后端服务
- [ ] 验证服务正常启动
- [ ] 验证订阅系统已启用
- [ ] 检查错误日志

### 功能测试
- [ ] 测试每日处理次数上限（基础版）
- [ ] 测试每日处理次数上限（高级版）
- [ ] 测试每日处理次数上限（购买包）
- [ ] 测试免费体验（前5次免费）
- [ ] 测试产品购买流程
- [ ] 测试收据验证
- [ ] 测试订阅状态查询

### 前端
- [ ] 更新产品价格显示（如需要）
- [ ] 更新产品列表（如需要）
- [ ] 测试前端UI

### iOS App
- [ ] 本地测试（StoreKit Configuration）
- [ ] 沙盒测试（App Store Connect）
- [ ] 测试产品列表获取
- [ ] 测试购买流程

### 部署
- [ ] 备份生产数据库
- [ ] 部署代码更新
- [ ] 运行数据库迁移
- [ ] 重启生产服务
- [ ] 验证生产环境正常运行

---

## 🎯 优先级

### 高优先级（立即执行）

1. **初始化数据库** ⭐
   - 创建 `process_logs` 表
   - 这是功能正常工作的前提

2. **重启后端服务**
   - 确保新代码生效

3. **测试每日处理次数上限**
   - 验证核心功能是否正常

### 中优先级（尽快完成）

4. **测试产品购买流程**
   - 验证 App Store Connect 集成

5. **更新前端显示**
   - 确保价格和产品信息正确

### 低优先级（可以稍后）

6. **iOS App 测试**
   - 可以在本地测试后，再进行沙盒测试

7. **生产环境部署**
   - 测试完成后部署

---

## 📚 相关文档

- `docs/subscription/UPDATE_COMPLETE.md` - 更新完成总结
- `docs/subscription/DAILY_PROCESS_LIMIT_IMPLEMENTATION.md` - 每日处理次数上限实现说明
- `docs/subscription/IOS_TESTING_GUIDE.md` - iOS 测试指南
- `docs/subscription/APP_STORE_CONNECT_SETUP.md` - App Store Connect 配置指南

---

**建议先执行步骤 1 和 2，然后进行测试！** 🚀
