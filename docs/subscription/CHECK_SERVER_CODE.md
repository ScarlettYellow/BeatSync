# 检查服务器上的实际代码

## 问题

代码已更新，但端点仍然返回 404。需要检查服务器上的实际代码。

## 诊断步骤

### 步骤 1：查看服务器上的端点定义

在服务器上执行：

```bash
# 查看端点定义前后的代码（第 1128-1140 行）
sed -n '1128,1140p' /opt/beatsync/web_service/backend/main.py
```

**应该看到**：
```python
# ==================== 订阅系统 API ==================

# 订阅产品列表端点（移到条件块外，确保始终可用）
@app.get("/api/subscription/products")
async def get_subscription_products():
```

### 步骤 2：查看完整的端点函数

```bash
# 查看完整的端点函数（第 1133-1220 行）
sed -n '1133,1220p' /opt/beatsync/web_service/backend/main.py
```

### 步骤 3：检查语法错误的具体位置

```bash
# 查看具体的语法错误
python3 -c "
import py_compile
try:
    py_compile.compile('/opt/beatsync/web_service/backend/main.py', doraise=True)
    print('✅ 语法正确')
except py_compile.PyCompileError as e:
    print(f'❌ 语法错误: {e}')
    print(f'文件: {e.file}')
    print(f'行号: {e.lineno}')
    print(f'错误: {e.msg}')
except Exception as e:
    print(f'❌ 其他错误: {e}')
    import traceback
    traceback.print_exc()
"
```

### 步骤 4：检查端点是否在条件块内

```bash
# 查找端点定义和条件块的位置
grep -n -E "subscription/products|if SUBSCRIPTION_AVAILABLE:" /opt/beatsync/web_service/backend/main.py | head -5
```

**应该看到**：
- 端点定义在 `if SUBSCRIPTION_AVAILABLE:` 之前

### 步骤 5：手动测试导入

```bash
cd /opt/beatsync/web_service/backend
python3 -c "
import sys
sys.path.insert(0, '/opt/beatsync/web_service/backend')
try:
    from main import app
    print('✅ 导入成功')
    # 检查路由
    routes = [r for r in app.routes if hasattr(r, 'path') and 'subscription/products' in r.path]
    if routes:
        print(f'✅ 找到路由: {routes[0].path}')
    else:
        print('❌ 未找到路由')
        print('所有路由（前20个）：')
        all_routes = [r for r in app.routes if hasattr(r, 'path')][:20]
        for r in all_routes:
            print(f'  {r.path}')
except Exception as e:
    print(f'❌ 导入失败: {e}')
    import traceback
    traceback.print_exc()
"
```

---

## 一键诊断命令

在服务器上执行：

```bash
echo "=== 1. 查看端点定义 ===" && \
sed -n '1128,1140p' /opt/beatsync/web_service/backend/main.py && \
echo "" && \
echo "=== 2. 检查语法错误 ===" && \
python3 -c "
import py_compile
try:
    py_compile.compile('/opt/beatsync/web_service/backend/main.py', doraise=True)
    print('✅ 语法正确')
except py_compile.PyCompileError as e:
    print(f'❌ 语法错误')
    print(f'文件: {e.file}')
    print(f'行号: {e.lineno}')
    print(f'错误: {e.msg}')
except Exception as e:
    print(f'❌ 其他错误: {e}')
" && \
echo "" && \
echo "=== 3. 检查端点位置 ===" && \
grep -n -E "subscription/products|if SUBSCRIPTION_AVAILABLE:" /opt/beatsync/web_service/backend/main.py | head -5 && \
echo "" && \
echo "=== 4. 测试导入和路由 ===" && \
cd /opt/beatsync/web_service/backend && \
python3 -c "
import sys
sys.path.insert(0, '/opt/beatsync/web_service/backend')
try:
    from main import app
    routes = [r for r in app.routes if hasattr(r, 'path') and 'subscription/products' in r.path]
    if routes:
        print(f'✅ 找到路由: {routes[0].path}')
    else:
        print('❌ 未找到路由')
except Exception as e:
    print(f'❌ 导入失败: {e}')
    import traceback
    traceback.print_exc()
"
```

---

**请执行上述诊断命令，特别是步骤 2（查看具体的语法错误）！** 🔍



# 检查服务器上的实际代码

## 问题

代码已更新，但端点仍然返回 404。需要检查服务器上的实际代码。

## 诊断步骤

### 步骤 1：查看服务器上的端点定义

在服务器上执行：

```bash
# 查看端点定义前后的代码（第 1128-1140 行）
sed -n '1128,1140p' /opt/beatsync/web_service/backend/main.py
```

**应该看到**：
```python
# ==================== 订阅系统 API ==================

# 订阅产品列表端点（移到条件块外，确保始终可用）
@app.get("/api/subscription/products")
async def get_subscription_products():
```

### 步骤 2：查看完整的端点函数

```bash
# 查看完整的端点函数（第 1133-1220 行）
sed -n '1133,1220p' /opt/beatsync/web_service/backend/main.py
```

### 步骤 3：检查语法错误的具体位置

```bash
# 查看具体的语法错误
python3 -c "
import py_compile
try:
    py_compile.compile('/opt/beatsync/web_service/backend/main.py', doraise=True)
    print('✅ 语法正确')
except py_compile.PyCompileError as e:
    print(f'❌ 语法错误: {e}')
    print(f'文件: {e.file}')
    print(f'行号: {e.lineno}')
    print(f'错误: {e.msg}')
except Exception as e:
    print(f'❌ 其他错误: {e}')
    import traceback
    traceback.print_exc()
"
```

### 步骤 4：检查端点是否在条件块内

```bash
# 查找端点定义和条件块的位置
grep -n -E "subscription/products|if SUBSCRIPTION_AVAILABLE:" /opt/beatsync/web_service/backend/main.py | head -5
```

**应该看到**：
- 端点定义在 `if SUBSCRIPTION_AVAILABLE:` 之前

### 步骤 5：手动测试导入

```bash
cd /opt/beatsync/web_service/backend
python3 -c "
import sys
sys.path.insert(0, '/opt/beatsync/web_service/backend')
try:
    from main import app
    print('✅ 导入成功')
    # 检查路由
    routes = [r for r in app.routes if hasattr(r, 'path') and 'subscription/products' in r.path]
    if routes:
        print(f'✅ 找到路由: {routes[0].path}')
    else:
        print('❌ 未找到路由')
        print('所有路由（前20个）：')
        all_routes = [r for r in app.routes if hasattr(r, 'path')][:20]
        for r in all_routes:
            print(f'  {r.path}')
except Exception as e:
    print(f'❌ 导入失败: {e}')
    import traceback
    traceback.print_exc()
"
```

---

## 一键诊断命令

在服务器上执行：

```bash
echo "=== 1. 查看端点定义 ===" && \
sed -n '1128,1140p' /opt/beatsync/web_service/backend/main.py && \
echo "" && \
echo "=== 2. 检查语法错误 ===" && \
python3 -c "
import py_compile
try:
    py_compile.compile('/opt/beatsync/web_service/backend/main.py', doraise=True)
    print('✅ 语法正确')
except py_compile.PyCompileError as e:
    print(f'❌ 语法错误')
    print(f'文件: {e.file}')
    print(f'行号: {e.lineno}')
    print(f'错误: {e.msg}')
except Exception as e:
    print(f'❌ 其他错误: {e}')
" && \
echo "" && \
echo "=== 3. 检查端点位置 ===" && \
grep -n -E "subscription/products|if SUBSCRIPTION_AVAILABLE:" /opt/beatsync/web_service/backend/main.py | head -5 && \
echo "" && \
echo "=== 4. 测试导入和路由 ===" && \
cd /opt/beatsync/web_service/backend && \
python3 -c "
import sys
sys.path.insert(0, '/opt/beatsync/web_service/backend')
try:
    from main import app
    routes = [r for r in app.routes if hasattr(r, 'path') and 'subscription/products' in r.path]
    if routes:
        print(f'✅ 找到路由: {routes[0].path}')
    else:
        print('❌ 未找到路由')
except Exception as e:
    print(f'❌ 导入失败: {e}')
    import traceback
    traceback.print_exc()
"
```

---

**请执行上述诊断命令，特别是步骤 2（查看具体的语法错误）！** 🔍



# 检查服务器上的实际代码

## 问题

代码已更新，但端点仍然返回 404。需要检查服务器上的实际代码。

## 诊断步骤

### 步骤 1：查看服务器上的端点定义

在服务器上执行：

```bash
# 查看端点定义前后的代码（第 1128-1140 行）
sed -n '1128,1140p' /opt/beatsync/web_service/backend/main.py
```

**应该看到**：
```python
# ==================== 订阅系统 API ==================

# 订阅产品列表端点（移到条件块外，确保始终可用）
@app.get("/api/subscription/products")
async def get_subscription_products():
```

### 步骤 2：查看完整的端点函数

```bash
# 查看完整的端点函数（第 1133-1220 行）
sed -n '1133,1220p' /opt/beatsync/web_service/backend/main.py
```

### 步骤 3：检查语法错误的具体位置

```bash
# 查看具体的语法错误
python3 -c "
import py_compile
try:
    py_compile.compile('/opt/beatsync/web_service/backend/main.py', doraise=True)
    print('✅ 语法正确')
except py_compile.PyCompileError as e:
    print(f'❌ 语法错误: {e}')
    print(f'文件: {e.file}')
    print(f'行号: {e.lineno}')
    print(f'错误: {e.msg}')
except Exception as e:
    print(f'❌ 其他错误: {e}')
    import traceback
    traceback.print_exc()
"
```

### 步骤 4：检查端点是否在条件块内

```bash
# 查找端点定义和条件块的位置
grep -n -E "subscription/products|if SUBSCRIPTION_AVAILABLE:" /opt/beatsync/web_service/backend/main.py | head -5
```

**应该看到**：
- 端点定义在 `if SUBSCRIPTION_AVAILABLE:` 之前

### 步骤 5：手动测试导入

```bash
cd /opt/beatsync/web_service/backend
python3 -c "
import sys
sys.path.insert(0, '/opt/beatsync/web_service/backend')
try:
    from main import app
    print('✅ 导入成功')
    # 检查路由
    routes = [r for r in app.routes if hasattr(r, 'path') and 'subscription/products' in r.path]
    if routes:
        print(f'✅ 找到路由: {routes[0].path}')
    else:
        print('❌ 未找到路由')
        print('所有路由（前20个）：')
        all_routes = [r for r in app.routes if hasattr(r, 'path')][:20]
        for r in all_routes:
            print(f'  {r.path}')
except Exception as e:
    print(f'❌ 导入失败: {e}')
    import traceback
    traceback.print_exc()
"
```

---

## 一键诊断命令

在服务器上执行：

```bash
echo "=== 1. 查看端点定义 ===" && \
sed -n '1128,1140p' /opt/beatsync/web_service/backend/main.py && \
echo "" && \
echo "=== 2. 检查语法错误 ===" && \
python3 -c "
import py_compile
try:
    py_compile.compile('/opt/beatsync/web_service/backend/main.py', doraise=True)
    print('✅ 语法正确')
except py_compile.PyCompileError as e:
    print(f'❌ 语法错误')
    print(f'文件: {e.file}')
    print(f'行号: {e.lineno}')
    print(f'错误: {e.msg}')
except Exception as e:
    print(f'❌ 其他错误: {e}')
" && \
echo "" && \
echo "=== 3. 检查端点位置 ===" && \
grep -n -E "subscription/products|if SUBSCRIPTION_AVAILABLE:" /opt/beatsync/web_service/backend/main.py | head -5 && \
echo "" && \
echo "=== 4. 测试导入和路由 ===" && \
cd /opt/beatsync/web_service/backend && \
python3 -c "
import sys
sys.path.insert(0, '/opt/beatsync/web_service/backend')
try:
    from main import app
    routes = [r for r in app.routes if hasattr(r, 'path') and 'subscription/products' in r.path]
    if routes:
        print(f'✅ 找到路由: {routes[0].path}')
    else:
        print('❌ 未找到路由')
except Exception as e:
    print(f'❌ 导入失败: {e}')
    import traceback
    traceback.print_exc()
"
```

---

**请执行上述诊断命令，特别是步骤 2（查看具体的语法错误）！** 🔍














