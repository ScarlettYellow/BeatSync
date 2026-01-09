# 订阅系统 API 测试结果

## 测试日期
2025-12-24

## 测试环境
- 后端服务：FastAPI (Python 3.9)
- 数据库：SQLite
- 测试工具：curl, Python requests

## 测试结果总结

### ✅ 完整测试结果（启用订阅系统）

**测试时间**: 2025-12-24 13:58:45  
**测试脚本**: `test_full_api.py`  
**测试结果**: **5/5 通过** ✅

#### 测试详情

1. ✅ **健康检查** (`GET /api/health`)
   - 状态码：200
   - 响应正常

2. ✅ **用户注册** (`POST /api/auth/register`)
   - 状态码：200
   - 成功返回 `user_id` 和 `token`
   - JWT Token 生成正常

3. ✅ **订阅状态查询** (`GET /api/subscription/status`)
   - 状态码：200
   - 正确返回订阅信息
   - 免费周次数：2次（正确初始化）
   - 响应格式：
     ```json
     {
       "is_whitelisted": false,
       "subscription": null,
       "download_credits": {
         "total": 2,
         "remaining": 2,
         "available_credits": {
           "subscription": 0,
           "purchased": 0,
           "free_weekly": 2
         }
       },
       "free_weekly": {
         "used": 0,
         "remaining": 2
       }
     }
     ```

4. ✅ **下载次数检查** (`GET /api/credits/check`)
   - 状态码：200
   - 正确返回下载次数信息
   - `can_download`: true
   - `total_remaining`: 2

5. ✅ **白名单管理**
   - ✅ 添加用户到白名单 (`POST /api/admin/whitelist/add`)
   - ✅ 检查用户是否在白名单中 (`GET /api/admin/whitelist/check/{user_id}`)
   - ✅ 获取白名单列表 (`GET /api/admin/whitelist`)
   - ✅ 删除白名单用户 (`DELETE /api/admin/whitelist/{user_id}`)
   - 所有操作状态码：200
   - 所有操作响应格式正确

### ✅ 测试通过的功能（订阅系统关闭）

#### 1. 向后兼容性测试（订阅系统关闭）
- ✅ **健康检查接口** (`GET /api/health`)
  - 状态码：200
  - 响应正常
  
- ✅ **订阅状态查询** (`GET /api/subscription/status`)
  - 状态码：200
  - 正确返回 "订阅系统未启用" 错误
  - **验证零耦合设计**：订阅系统关闭时不影响现有功能

- ✅ **下载次数检查** (`GET /api/credits/check`)
  - 状态码：200
  - 无认证请求时正确返回允许下载
  - 响应格式：
    ```json
    {
      "is_whitelisted": false,
      "can_download": true,
      "available_credits": {
        "subscription": 0,
        "purchased": 0,
        "free_weekly": 0
      },
      "total_remaining": 999999
    }
    ```
  - **验证向后兼容**：匿名用户可以直接使用

#### 2. 代码修复
- ✅ 修复了 `float('inf')` JSON 序列化问题
  - 将所有 `float('inf')` 替换为 `999999`
  - 确保 JSON 响应可以正常序列化

### ⚠️ 需要手动测试的功能

由于环境变量需要在服务启动时设置，以下功能需要在**启用订阅系统**的情况下手动测试：

#### 启用订阅系统的方法

**方法 1：使用启动脚本（推荐）**
```bash
cd web_service/backend
./start_server_with_subscription.sh
```

**方法 2：手动设置环境变量**
```bash
cd web_service/backend
export SUBSCRIPTION_ENABLED=true
export ADMIN_TOKEN=test_admin_token_12345
export JWT_SECRET_KEY=test_jwt_secret_key_12345
python3 main.py
```

**方法 3：使用 nohup 后台运行**
```bash
cd web_service/backend
SUBSCRIPTION_ENABLED=true \
ADMIN_TOKEN=test_admin_token_12345 \
JWT_SECRET_KEY=test_jwt_secret_key_12345 \
nohup python3 main.py > server.log 2>&1 &
```

#### 需要测试的 API（启用订阅系统后）

1. **用户注册** (`POST /api/auth/register`)
   ```bash
   curl -X POST "http://localhost:8000/api/auth/register" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "device_id=test_device_001"
   ```
   - 预期：返回 `user_id` 和 `token`

2. **用户登录** (`POST /api/auth/login`)
   ```bash
   curl -X POST "http://localhost:8000/api/auth/login" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "device_id=test_device_001"
   ```

3. **订阅状态查询** (`GET /api/subscription/status`)
   ```bash
   curl -X GET "http://localhost:8000/api/subscription/status" \
     -H "Authorization: Bearer YOUR_TOKEN"
   ```

4. **下载次数检查** (`GET /api/credits/check`)
   ```bash
   curl -X GET "http://localhost:8000/api/credits/check" \
     -H "Authorization: Bearer YOUR_TOKEN"
   ```

5. **白名单管理**
   - 添加：`POST /api/admin/whitelist/add`
   - 查询：`GET /api/admin/whitelist/check/{user_id}`
   - 列表：`GET /api/admin/whitelist`
   - 删除：`DELETE /api/admin/whitelist/{user_id}`

6. **下载接口测试** (`GET /api/download/{task_id}`)
   - 无认证：应该正常下载（向后兼容）
   - 有认证：应该检查下载次数

## 测试脚本

### 自动化测试脚本

1. **基础功能测试**（订阅系统关闭）
   ```bash
   cd web_service/backend
   python3 test_subscription.py
   ```

2. **完整功能测试**（需要启用订阅系统）
   ```bash
   cd web_service/backend
   python3 test_api_enabled.py
   ```

3. **Shell 测试脚本**
   ```bash
   cd web_service/backend
   bash test_api_complete.sh
   ```

## 已知问题

1. **环境变量传递**
   - 环境变量必须在服务启动时设置
   - 模块导入时会读取环境变量，后续修改不会生效
   - **解决方案**：使用启动脚本或在前台运行服务时设置环境变量

2. **服务启动方式**
   - 后台运行 (`&`) 时，环境变量可能无法正确传递
   - **解决方案**：使用 `nohup` 或前台运行

## 测试建议

### 测试流程

1. **基础测试（订阅系统关闭）**
   ```bash
   # 启动服务（默认关闭订阅系统）
   cd web_service/backend
   python3 main.py
   
   # 在另一个终端运行测试
   bash test_api_complete.sh
   ```

2. **完整测试（启用订阅系统）**
   ```bash
   # 停止服务（Ctrl+C）
   # 使用启动脚本重新启动
   ./start_server_with_subscription.sh
   
   # 在另一个终端运行完整测试
   python3 test_api_enabled.py
   ```

### 验证清单

- [x] 订阅系统关闭时，现有功能正常
- [x] 无认证请求时，下载接口正常
- [x] JSON 响应格式正确
- [x] 启用订阅系统后，用户注册正常
- [x] 启用订阅系统后，白名单管理正常
- [x] 启用订阅系统后，下载次数检查正常
- [x] 启用订阅系统后，订阅状态查询正常
- [ ] 启用订阅系统后，下载接口检查次数正常（需要实际任务ID测试）

## 下一步

1. 手动测试启用订阅系统后的完整功能
2. 测试下载接口的零耦合设计
3. 进行压力测试
4. 开始 iOS App 集成

## 测试工具

- **curl**：命令行 HTTP 客户端
- **Python requests**：Python HTTP 库
- **test_api_enabled.py**：自动化测试脚本
- **test_api_complete.sh**：Shell 测试脚本

## 注意事项

1. **环境变量**：必须在服务启动前设置
2. **服务重启**：修改环境变量后需要重启服务
3. **数据库**：确保数据库已初始化（`python3 subscription_db.py`）
4. **端口占用**：确保 8000 端口未被占用

