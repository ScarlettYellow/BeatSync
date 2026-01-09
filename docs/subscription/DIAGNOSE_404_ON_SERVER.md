# 在服务器上诊断 404 错误

## 快速诊断

在服务器上执行以下诊断脚本：

```bash
# 上传诊断脚本到服务器（从本地 Mac）
scp scripts/deployment/diagnose_subscription_api.sh ubuntu@beatsync.site:/tmp/

# SSH 登录服务器
ssh ubuntu@beatsync.site

# 执行诊断脚本
sudo bash /tmp/diagnose_subscription_api.sh
```

## 手动诊断步骤

### 步骤 1：确认代码已更新

```bash
# 检查端点是否在代码中
grep -n "subscription/products" /opt/beatsync/web_service/backend/main.py
```

**应该看到**：`1133:@app.get("/api/subscription/products")`

### 步骤 2：检查端点位置

```bash
# 查看端点前后的代码（确认不在条件块内）
sed -n '1128,1140p' /opt/beatsync/web_service/backend/main.py
```

**应该看到**：
- 端点定义在 `if SUBSCRIPTION_AVAILABLE:` 之前
- 端点不在任何条件块内

### 步骤 3：检查 Python 语法

```bash
python3 -m py_compile /opt/beatsync/web_service/backend/main.py
```

**如果报错**：说明代码有语法错误，需要修复

### 步骤 4：直接测试后端（绕过 Nginx）

```bash
# 直接访问后端服务
curl http://127.0.0.1:8000/api/subscription/products
```

**如果返回 404**：问题在后端代码
**如果返回产品列表**：问题在 Nginx 配置

### 步骤 5：检查服务日志

```bash
# 查看最近 50 行日志
sudo journalctl -u beatsync -n 50 | grep -i "error\|exception\|traceback"
```

**查找**：
- Python 语法错误
- 导入错误
- 其他异常

### 步骤 6：检查 FastAPI 路由注册

```bash
cat > /tmp/check_routes.py << 'EOF'
import sys
sys.path.insert(0, '/opt/beatsync/web_service/backend')
from main import app

# 列出所有路由
for route in app.routes:
    if hasattr(route, 'path'):
        methods = getattr(route, 'methods', set())
        if 'subscription' in route.path:
            print(f"{methods}: {route.path}")
EOF

python3 /tmp/check_routes.py
```

**应该看到**：`{'GET'}: /api/subscription/products`

---

## 常见问题及解决方案

### 问题 1：代码未更新

**症状**：`grep` 找不到端点定义

**解决**：
```bash
cd /opt/beatsync
sudo git pull origin main
sudo systemctl restart beatsync
```

### 问题 2：代码有语法错误

**症状**：`python3 -m py_compile` 报错

**解决**：修复代码后重新部署

### 问题 3：服务未重启

**症状**：服务状态显示旧版本

**解决**：
```bash
sudo systemctl restart beatsync
sleep 3
sudo systemctl status beatsync
```

### 问题 4：端点未注册

**症状**：直接访问后端也返回 404

**可能原因**：
- 代码有语法错误，导致端点未注册
- 端点定义在条件块内，条件不满足

**解决**：
- 检查代码语法
- 确认端点不在条件块内

---

## 一键诊断命令

在服务器上执行：

```bash
echo "=== 1. 检查代码 ===" && \
grep -n "subscription/products" /opt/beatsync/web_service/backend/main.py && \
echo "" && \
echo "=== 2. 检查语法 ===" && \
python3 -m py_compile /opt/beatsync/web_service/backend/main.py 2>&1 && echo "✅ 语法正确" || echo "❌ 语法错误" && \
echo "" && \
echo "=== 3. 检查服务状态 ===" && \
sudo systemctl status beatsync | head -10 && \
echo "" && \
echo "=== 4. 直接测试后端 ===" && \
curl -s http://127.0.0.1:8000/api/subscription/products | head -20 && \
echo "" && \
echo "=== 5. 通过 Nginx 测试 ===" && \
curl -s https://beatsync.site/api/subscription/products | head -20
```

---

**请执行上述诊断命令，并告诉我输出结果！** 🔍



# 在服务器上诊断 404 错误

## 快速诊断

在服务器上执行以下诊断脚本：

```bash
# 上传诊断脚本到服务器（从本地 Mac）
scp scripts/deployment/diagnose_subscription_api.sh ubuntu@beatsync.site:/tmp/

# SSH 登录服务器
ssh ubuntu@beatsync.site

# 执行诊断脚本
sudo bash /tmp/diagnose_subscription_api.sh
```

## 手动诊断步骤

### 步骤 1：确认代码已更新

```bash
# 检查端点是否在代码中
grep -n "subscription/products" /opt/beatsync/web_service/backend/main.py
```

**应该看到**：`1133:@app.get("/api/subscription/products")`

### 步骤 2：检查端点位置

```bash
# 查看端点前后的代码（确认不在条件块内）
sed -n '1128,1140p' /opt/beatsync/web_service/backend/main.py
```

**应该看到**：
- 端点定义在 `if SUBSCRIPTION_AVAILABLE:` 之前
- 端点不在任何条件块内

### 步骤 3：检查 Python 语法

```bash
python3 -m py_compile /opt/beatsync/web_service/backend/main.py
```

**如果报错**：说明代码有语法错误，需要修复

### 步骤 4：直接测试后端（绕过 Nginx）

```bash
# 直接访问后端服务
curl http://127.0.0.1:8000/api/subscription/products
```

**如果返回 404**：问题在后端代码
**如果返回产品列表**：问题在 Nginx 配置

### 步骤 5：检查服务日志

```bash
# 查看最近 50 行日志
sudo journalctl -u beatsync -n 50 | grep -i "error\|exception\|traceback"
```

**查找**：
- Python 语法错误
- 导入错误
- 其他异常

### 步骤 6：检查 FastAPI 路由注册

```bash
cat > /tmp/check_routes.py << 'EOF'
import sys
sys.path.insert(0, '/opt/beatsync/web_service/backend')
from main import app

# 列出所有路由
for route in app.routes:
    if hasattr(route, 'path'):
        methods = getattr(route, 'methods', set())
        if 'subscription' in route.path:
            print(f"{methods}: {route.path}")
EOF

python3 /tmp/check_routes.py
```

**应该看到**：`{'GET'}: /api/subscription/products`

---

## 常见问题及解决方案

### 问题 1：代码未更新

**症状**：`grep` 找不到端点定义

**解决**：
```bash
cd /opt/beatsync
sudo git pull origin main
sudo systemctl restart beatsync
```

### 问题 2：代码有语法错误

**症状**：`python3 -m py_compile` 报错

**解决**：修复代码后重新部署

### 问题 3：服务未重启

**症状**：服务状态显示旧版本

**解决**：
```bash
sudo systemctl restart beatsync
sleep 3
sudo systemctl status beatsync
```

### 问题 4：端点未注册

**症状**：直接访问后端也返回 404

**可能原因**：
- 代码有语法错误，导致端点未注册
- 端点定义在条件块内，条件不满足

**解决**：
- 检查代码语法
- 确认端点不在条件块内

---

## 一键诊断命令

在服务器上执行：

```bash
echo "=== 1. 检查代码 ===" && \
grep -n "subscription/products" /opt/beatsync/web_service/backend/main.py && \
echo "" && \
echo "=== 2. 检查语法 ===" && \
python3 -m py_compile /opt/beatsync/web_service/backend/main.py 2>&1 && echo "✅ 语法正确" || echo "❌ 语法错误" && \
echo "" && \
echo "=== 3. 检查服务状态 ===" && \
sudo systemctl status beatsync | head -10 && \
echo "" && \
echo "=== 4. 直接测试后端 ===" && \
curl -s http://127.0.0.1:8000/api/subscription/products | head -20 && \
echo "" && \
echo "=== 5. 通过 Nginx 测试 ===" && \
curl -s https://beatsync.site/api/subscription/products | head -20
```

---

**请执行上述诊断命令，并告诉我输出结果！** 🔍



# 在服务器上诊断 404 错误

## 快速诊断

在服务器上执行以下诊断脚本：

```bash
# 上传诊断脚本到服务器（从本地 Mac）
scp scripts/deployment/diagnose_subscription_api.sh ubuntu@beatsync.site:/tmp/

# SSH 登录服务器
ssh ubuntu@beatsync.site

# 执行诊断脚本
sudo bash /tmp/diagnose_subscription_api.sh
```

## 手动诊断步骤

### 步骤 1：确认代码已更新

```bash
# 检查端点是否在代码中
grep -n "subscription/products" /opt/beatsync/web_service/backend/main.py
```

**应该看到**：`1133:@app.get("/api/subscription/products")`

### 步骤 2：检查端点位置

```bash
# 查看端点前后的代码（确认不在条件块内）
sed -n '1128,1140p' /opt/beatsync/web_service/backend/main.py
```

**应该看到**：
- 端点定义在 `if SUBSCRIPTION_AVAILABLE:` 之前
- 端点不在任何条件块内

### 步骤 3：检查 Python 语法

```bash
python3 -m py_compile /opt/beatsync/web_service/backend/main.py
```

**如果报错**：说明代码有语法错误，需要修复

### 步骤 4：直接测试后端（绕过 Nginx）

```bash
# 直接访问后端服务
curl http://127.0.0.1:8000/api/subscription/products
```

**如果返回 404**：问题在后端代码
**如果返回产品列表**：问题在 Nginx 配置

### 步骤 5：检查服务日志

```bash
# 查看最近 50 行日志
sudo journalctl -u beatsync -n 50 | grep -i "error\|exception\|traceback"
```

**查找**：
- Python 语法错误
- 导入错误
- 其他异常

### 步骤 6：检查 FastAPI 路由注册

```bash
cat > /tmp/check_routes.py << 'EOF'
import sys
sys.path.insert(0, '/opt/beatsync/web_service/backend')
from main import app

# 列出所有路由
for route in app.routes:
    if hasattr(route, 'path'):
        methods = getattr(route, 'methods', set())
        if 'subscription' in route.path:
            print(f"{methods}: {route.path}")
EOF

python3 /tmp/check_routes.py
```

**应该看到**：`{'GET'}: /api/subscription/products`

---

## 常见问题及解决方案

### 问题 1：代码未更新

**症状**：`grep` 找不到端点定义

**解决**：
```bash
cd /opt/beatsync
sudo git pull origin main
sudo systemctl restart beatsync
```

### 问题 2：代码有语法错误

**症状**：`python3 -m py_compile` 报错

**解决**：修复代码后重新部署

### 问题 3：服务未重启

**症状**：服务状态显示旧版本

**解决**：
```bash
sudo systemctl restart beatsync
sleep 3
sudo systemctl status beatsync
```

### 问题 4：端点未注册

**症状**：直接访问后端也返回 404

**可能原因**：
- 代码有语法错误，导致端点未注册
- 端点定义在条件块内，条件不满足

**解决**：
- 检查代码语法
- 确认端点不在条件块内

---

## 一键诊断命令

在服务器上执行：

```bash
echo "=== 1. 检查代码 ===" && \
grep -n "subscription/products" /opt/beatsync/web_service/backend/main.py && \
echo "" && \
echo "=== 2. 检查语法 ===" && \
python3 -m py_compile /opt/beatsync/web_service/backend/main.py 2>&1 && echo "✅ 语法正确" || echo "❌ 语法错误" && \
echo "" && \
echo "=== 3. 检查服务状态 ===" && \
sudo systemctl status beatsync | head -10 && \
echo "" && \
echo "=== 4. 直接测试后端 ===" && \
curl -s http://127.0.0.1:8000/api/subscription/products | head -20 && \
echo "" && \
echo "=== 5. 通过 Nginx 测试 ===" && \
curl -s https://beatsync.site/api/subscription/products | head -20
```

---

**请执行上述诊断命令，并告诉我输出结果！** 🔍














