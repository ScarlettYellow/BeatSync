# 调试 404 错误

## 问题

即使重新部署后，API 端点 `/api/subscription/products` 仍然返回 404 Not Found。

## 排查步骤

### 步骤 1：确认代码已更新到服务器

在服务器上执行：

```bash
# 检查代码中是否有端点定义
grep -n "subscription/products" /opt/beatsync/web_service/backend/main.py
```

**应该看到**：`1133:@app.get("/api/subscription/products")`

### 步骤 2：检查端点是否在条件块外

```bash
# 查看端点定义前后的代码
sed -n '1128,1220p' /opt/beatsync/web_service/backend/main.py
```

**应该看到**：
- 端点定义在 `if SUBSCRIPTION_AVAILABLE:` 之前
- 端点不在任何条件块内

### 步骤 3：检查服务日志

```bash
# 查看服务启动日志
sudo journalctl -u beatsync -n 50 | grep -i "error\|exception\|traceback"
```

**查找**：
- 是否有 Python 语法错误
- 是否有导入错误
- 是否有其他异常

### 步骤 4：直接测试后端服务（绕过 Nginx）

```bash
# 直接访问后端服务（端口 8000）
curl http://127.0.0.1:8000/api/subscription/products
```

**如果返回 404**：说明后端代码有问题
**如果返回产品列表**：说明 Nginx 配置有问题

### 步骤 5：检查 FastAPI 路由注册

在服务器上创建一个测试脚本：

```bash
cat > /tmp/test_routes.py << 'EOF'
import sys
sys.path.insert(0, '/opt/beatsync/web_service/backend')
from main import app

# 列出所有路由
for route in app.routes:
    if hasattr(route, 'path'):
        print(f"{route.methods if hasattr(route, 'methods') else 'N/A'}: {route.path}")
EOF

python3 /tmp/test_routes.py | grep subscription
```

**应该看到**：`{'GET'}: /api/subscription/products`

### 步骤 6：检查 Python 语法

```bash
# 检查 main.py 是否有语法错误
python3 -m py_compile /opt/beatsync/web_service/backend/main.py
```

**如果报错**：说明代码有语法错误，需要修复

---

## 常见问题

### 问题 1：代码未更新

**检查**：
```bash
cd /opt/beatsync
git log -1 --oneline
git status
```

**解决**：
```bash
sudo git pull origin main
sudo systemctl restart beatsync
```

### 问题 2：服务未重启

**检查**：
```bash
sudo systemctl status beatsync
```

**解决**：
```bash
sudo systemctl restart beatsync
sleep 3
sudo systemctl status beatsync
```

### 问题 3：代码有语法错误

**检查**：
```bash
python3 -m py_compile /opt/beatsync/web_service/backend/main.py
```

**如果报错**：修复代码后重新部署

### 问题 4：Nginx 配置问题

**检查**：
```bash
# 直接访问后端（绕过 Nginx）
curl http://127.0.0.1:8000/api/subscription/products
```

**如果直接访问可以，但通过 Nginx 不行**：检查 Nginx 配置

---

## 快速诊断命令

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



# 调试 404 错误

## 问题

即使重新部署后，API 端点 `/api/subscription/products` 仍然返回 404 Not Found。

## 排查步骤

### 步骤 1：确认代码已更新到服务器

在服务器上执行：

```bash
# 检查代码中是否有端点定义
grep -n "subscription/products" /opt/beatsync/web_service/backend/main.py
```

**应该看到**：`1133:@app.get("/api/subscription/products")`

### 步骤 2：检查端点是否在条件块外

```bash
# 查看端点定义前后的代码
sed -n '1128,1220p' /opt/beatsync/web_service/backend/main.py
```

**应该看到**：
- 端点定义在 `if SUBSCRIPTION_AVAILABLE:` 之前
- 端点不在任何条件块内

### 步骤 3：检查服务日志

```bash
# 查看服务启动日志
sudo journalctl -u beatsync -n 50 | grep -i "error\|exception\|traceback"
```

**查找**：
- 是否有 Python 语法错误
- 是否有导入错误
- 是否有其他异常

### 步骤 4：直接测试后端服务（绕过 Nginx）

```bash
# 直接访问后端服务（端口 8000）
curl http://127.0.0.1:8000/api/subscription/products
```

**如果返回 404**：说明后端代码有问题
**如果返回产品列表**：说明 Nginx 配置有问题

### 步骤 5：检查 FastAPI 路由注册

在服务器上创建一个测试脚本：

```bash
cat > /tmp/test_routes.py << 'EOF'
import sys
sys.path.insert(0, '/opt/beatsync/web_service/backend')
from main import app

# 列出所有路由
for route in app.routes:
    if hasattr(route, 'path'):
        print(f"{route.methods if hasattr(route, 'methods') else 'N/A'}: {route.path}")
EOF

python3 /tmp/test_routes.py | grep subscription
```

**应该看到**：`{'GET'}: /api/subscription/products`

### 步骤 6：检查 Python 语法

```bash
# 检查 main.py 是否有语法错误
python3 -m py_compile /opt/beatsync/web_service/backend/main.py
```

**如果报错**：说明代码有语法错误，需要修复

---

## 常见问题

### 问题 1：代码未更新

**检查**：
```bash
cd /opt/beatsync
git log -1 --oneline
git status
```

**解决**：
```bash
sudo git pull origin main
sudo systemctl restart beatsync
```

### 问题 2：服务未重启

**检查**：
```bash
sudo systemctl status beatsync
```

**解决**：
```bash
sudo systemctl restart beatsync
sleep 3
sudo systemctl status beatsync
```

### 问题 3：代码有语法错误

**检查**：
```bash
python3 -m py_compile /opt/beatsync/web_service/backend/main.py
```

**如果报错**：修复代码后重新部署

### 问题 4：Nginx 配置问题

**检查**：
```bash
# 直接访问后端（绕过 Nginx）
curl http://127.0.0.1:8000/api/subscription/products
```

**如果直接访问可以，但通过 Nginx 不行**：检查 Nginx 配置

---

## 快速诊断命令

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



# 调试 404 错误

## 问题

即使重新部署后，API 端点 `/api/subscription/products` 仍然返回 404 Not Found。

## 排查步骤

### 步骤 1：确认代码已更新到服务器

在服务器上执行：

```bash
# 检查代码中是否有端点定义
grep -n "subscription/products" /opt/beatsync/web_service/backend/main.py
```

**应该看到**：`1133:@app.get("/api/subscription/products")`

### 步骤 2：检查端点是否在条件块外

```bash
# 查看端点定义前后的代码
sed -n '1128,1220p' /opt/beatsync/web_service/backend/main.py
```

**应该看到**：
- 端点定义在 `if SUBSCRIPTION_AVAILABLE:` 之前
- 端点不在任何条件块内

### 步骤 3：检查服务日志

```bash
# 查看服务启动日志
sudo journalctl -u beatsync -n 50 | grep -i "error\|exception\|traceback"
```

**查找**：
- 是否有 Python 语法错误
- 是否有导入错误
- 是否有其他异常

### 步骤 4：直接测试后端服务（绕过 Nginx）

```bash
# 直接访问后端服务（端口 8000）
curl http://127.0.0.1:8000/api/subscription/products
```

**如果返回 404**：说明后端代码有问题
**如果返回产品列表**：说明 Nginx 配置有问题

### 步骤 5：检查 FastAPI 路由注册

在服务器上创建一个测试脚本：

```bash
cat > /tmp/test_routes.py << 'EOF'
import sys
sys.path.insert(0, '/opt/beatsync/web_service/backend')
from main import app

# 列出所有路由
for route in app.routes:
    if hasattr(route, 'path'):
        print(f"{route.methods if hasattr(route, 'methods') else 'N/A'}: {route.path}")
EOF

python3 /tmp/test_routes.py | grep subscription
```

**应该看到**：`{'GET'}: /api/subscription/products`

### 步骤 6：检查 Python 语法

```bash
# 检查 main.py 是否有语法错误
python3 -m py_compile /opt/beatsync/web_service/backend/main.py
```

**如果报错**：说明代码有语法错误，需要修复

---

## 常见问题

### 问题 1：代码未更新

**检查**：
```bash
cd /opt/beatsync
git log -1 --oneline
git status
```

**解决**：
```bash
sudo git pull origin main
sudo systemctl restart beatsync
```

### 问题 2：服务未重启

**检查**：
```bash
sudo systemctl status beatsync
```

**解决**：
```bash
sudo systemctl restart beatsync
sleep 3
sudo systemctl status beatsync
```

### 问题 3：代码有语法错误

**检查**：
```bash
python3 -m py_compile /opt/beatsync/web_service/backend/main.py
```

**如果报错**：修复代码后重新部署

### 问题 4：Nginx 配置问题

**检查**：
```bash
# 直接访问后端（绕过 Nginx）
curl http://127.0.0.1:8000/api/subscription/products
```

**如果直接访问可以，但通过 Nginx 不行**：检查 Nginx 配置

---

## 快速诊断命令

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














