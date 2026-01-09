# 强制更新服务器代码（版本2）

## 问题诊断

服务器输出显示：
- ✅ 语法正确（代码可以导入）
- ❌ 第 1128-1140 行是空的（没有端点定义）
- ❌ 路由列表中没有 `/api/subscription/products` 端点

这说明服务器上的代码版本不对，需要强制更新。

## 强制更新命令

在服务器上执行：

```bash
cd /opt/beatsync && \
echo "=== 1. 检查当前文件行数 ===" && \
wc -l web_service/backend/main.py && \
echo "" && \
echo "=== 2. 检查 Git 状态 ===" && \
sudo git status --short && \
echo "" && \
echo "=== 3. 强制重置到远程 main 分支 ===" && \
sudo git fetch origin main && \
sudo git reset --hard origin/main && \
echo "" && \
echo "=== 4. 验证文件行数 ===" && \
wc -l web_service/backend/main.py && \
echo "" && \
echo "=== 5. 验证端点定义存在 ===" && \
grep -n "@app.get.*subscription/products" web_service/backend/main.py && \
echo "" && \
echo "=== 6. 检查语法 ===" && \
python3 -c "
import py_compile
try:
    py_compile.compile('/opt/beatsync/web_service/backend/main.py', doraise=True)
    print('✅ 语法正确')
except py_compile.PyCompileError as e:
    print(f'❌ 语法错误: 行 {e.lineno}, {e.msg}')
except Exception as e:
    print(f'❌ 其他错误: {e}')
" && \
echo "" && \
echo "=== 7. 测试路由注册 ===" && \
cd web_service/backend && \
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
        print('检查所有路由（包含 subscription 的）：')
        all_routes = [r for r in app.routes if hasattr(r, 'path') and 'subscription' in r.path]
        for r in all_routes:
            methods = getattr(r, 'methods', set())
            print(f'  {list(methods)[0] if methods else \"N/A\"}: {r.path}')
except Exception as e:
    print(f'❌ 导入失败: {e}')
    import traceback
    traceback.print_exc()
" && \
echo "" && \
echo "=== 8. 重启服务 ===" && \
sudo systemctl restart beatsync && \
sleep 3 && \
echo "" && \
echo "=== 9. 测试端点 ===" && \
curl -s http://127.0.0.1:8000/api/subscription/products | python3 -m json.tool | head -50
```

---

## 如果仍然失败

如果步骤 5 仍然找不到端点定义，可能需要：

### 选项 A：检查文件是否被锁定

```bash
# 检查是否有其他进程在使用文件
sudo lsof /opt/beatsync/web_service/backend/main.py

# 如果有进程，停止服务后再更新
sudo systemctl stop beatsync
cd /opt/beatsync && sudo git reset --hard origin/main
sudo systemctl start beatsync
```

### 选项 B：手动检查文件内容

```bash
# 查看第 1130-1140 行的实际内容
sed -n '1130,1140p' /opt/beatsync/web_service/backend/main.py

# 查看文件总行数
wc -l /opt/beatsync/web_service/backend/main.py
```

**本地文件应该有 1800 行，端点定义在第 1133 行。**

---

**请执行上述强制更新命令，并告诉我所有步骤的输出！** 🔄



# 强制更新服务器代码（版本2）

## 问题诊断

服务器输出显示：
- ✅ 语法正确（代码可以导入）
- ❌ 第 1128-1140 行是空的（没有端点定义）
- ❌ 路由列表中没有 `/api/subscription/products` 端点

这说明服务器上的代码版本不对，需要强制更新。

## 强制更新命令

在服务器上执行：

```bash
cd /opt/beatsync && \
echo "=== 1. 检查当前文件行数 ===" && \
wc -l web_service/backend/main.py && \
echo "" && \
echo "=== 2. 检查 Git 状态 ===" && \
sudo git status --short && \
echo "" && \
echo "=== 3. 强制重置到远程 main 分支 ===" && \
sudo git fetch origin main && \
sudo git reset --hard origin/main && \
echo "" && \
echo "=== 4. 验证文件行数 ===" && \
wc -l web_service/backend/main.py && \
echo "" && \
echo "=== 5. 验证端点定义存在 ===" && \
grep -n "@app.get.*subscription/products" web_service/backend/main.py && \
echo "" && \
echo "=== 6. 检查语法 ===" && \
python3 -c "
import py_compile
try:
    py_compile.compile('/opt/beatsync/web_service/backend/main.py', doraise=True)
    print('✅ 语法正确')
except py_compile.PyCompileError as e:
    print(f'❌ 语法错误: 行 {e.lineno}, {e.msg}')
except Exception as e:
    print(f'❌ 其他错误: {e}')
" && \
echo "" && \
echo "=== 7. 测试路由注册 ===" && \
cd web_service/backend && \
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
        print('检查所有路由（包含 subscription 的）：')
        all_routes = [r for r in app.routes if hasattr(r, 'path') and 'subscription' in r.path]
        for r in all_routes:
            methods = getattr(r, 'methods', set())
            print(f'  {list(methods)[0] if methods else \"N/A\"}: {r.path}')
except Exception as e:
    print(f'❌ 导入失败: {e}')
    import traceback
    traceback.print_exc()
" && \
echo "" && \
echo "=== 8. 重启服务 ===" && \
sudo systemctl restart beatsync && \
sleep 3 && \
echo "" && \
echo "=== 9. 测试端点 ===" && \
curl -s http://127.0.0.1:8000/api/subscription/products | python3 -m json.tool | head -50
```

---

## 如果仍然失败

如果步骤 5 仍然找不到端点定义，可能需要：

### 选项 A：检查文件是否被锁定

```bash
# 检查是否有其他进程在使用文件
sudo lsof /opt/beatsync/web_service/backend/main.py

# 如果有进程，停止服务后再更新
sudo systemctl stop beatsync
cd /opt/beatsync && sudo git reset --hard origin/main
sudo systemctl start beatsync
```

### 选项 B：手动检查文件内容

```bash
# 查看第 1130-1140 行的实际内容
sed -n '1130,1140p' /opt/beatsync/web_service/backend/main.py

# 查看文件总行数
wc -l /opt/beatsync/web_service/backend/main.py
```

**本地文件应该有 1800 行，端点定义在第 1133 行。**

---

**请执行上述强制更新命令，并告诉我所有步骤的输出！** 🔄



# 强制更新服务器代码（版本2）

## 问题诊断

服务器输出显示：
- ✅ 语法正确（代码可以导入）
- ❌ 第 1128-1140 行是空的（没有端点定义）
- ❌ 路由列表中没有 `/api/subscription/products` 端点

这说明服务器上的代码版本不对，需要强制更新。

## 强制更新命令

在服务器上执行：

```bash
cd /opt/beatsync && \
echo "=== 1. 检查当前文件行数 ===" && \
wc -l web_service/backend/main.py && \
echo "" && \
echo "=== 2. 检查 Git 状态 ===" && \
sudo git status --short && \
echo "" && \
echo "=== 3. 强制重置到远程 main 分支 ===" && \
sudo git fetch origin main && \
sudo git reset --hard origin/main && \
echo "" && \
echo "=== 4. 验证文件行数 ===" && \
wc -l web_service/backend/main.py && \
echo "" && \
echo "=== 5. 验证端点定义存在 ===" && \
grep -n "@app.get.*subscription/products" web_service/backend/main.py && \
echo "" && \
echo "=== 6. 检查语法 ===" && \
python3 -c "
import py_compile
try:
    py_compile.compile('/opt/beatsync/web_service/backend/main.py', doraise=True)
    print('✅ 语法正确')
except py_compile.PyCompileError as e:
    print(f'❌ 语法错误: 行 {e.lineno}, {e.msg}')
except Exception as e:
    print(f'❌ 其他错误: {e}')
" && \
echo "" && \
echo "=== 7. 测试路由注册 ===" && \
cd web_service/backend && \
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
        print('检查所有路由（包含 subscription 的）：')
        all_routes = [r for r in app.routes if hasattr(r, 'path') and 'subscription' in r.path]
        for r in all_routes:
            methods = getattr(r, 'methods', set())
            print(f'  {list(methods)[0] if methods else \"N/A\"}: {r.path}')
except Exception as e:
    print(f'❌ 导入失败: {e}')
    import traceback
    traceback.print_exc()
" && \
echo "" && \
echo "=== 8. 重启服务 ===" && \
sudo systemctl restart beatsync && \
sleep 3 && \
echo "" && \
echo "=== 9. 测试端点 ===" && \
curl -s http://127.0.0.1:8000/api/subscription/products | python3 -m json.tool | head -50
```

---

## 如果仍然失败

如果步骤 5 仍然找不到端点定义，可能需要：

### 选项 A：检查文件是否被锁定

```bash
# 检查是否有其他进程在使用文件
sudo lsof /opt/beatsync/web_service/backend/main.py

# 如果有进程，停止服务后再更新
sudo systemctl stop beatsync
cd /opt/beatsync && sudo git reset --hard origin/main
sudo systemctl start beatsync
```

### 选项 B：手动检查文件内容

```bash
# 查看第 1130-1140 行的实际内容
sed -n '1130,1140p' /opt/beatsync/web_service/backend/main.py

# 查看文件总行数
wc -l /opt/beatsync/web_service/backend/main.py
```

**本地文件应该有 1800 行，端点定义在第 1133 行。**

---

**请执行上述强制更新命令，并告诉我所有步骤的输出！** 🔄














