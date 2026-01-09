# 修复服务器 404 错误

## 问题诊断

从诊断结果看：
- ✅ 服务正在运行
- ❌ 直接测试后端返回 404
- ❌ 通过 Nginx 也返回 404
- ⚠️ 代码可能未更新或有语法错误

## 解决方案

### 步骤 1：确认代码已更新

在服务器上执行：

```bash
# 检查端点是否在代码中
grep -n "subscription/products" /opt/beatsync/web_service/backend/main.py
```

**如果没有输出**：说明代码未更新

**如果有输出**：应该看到类似 `1133:@app.get("/api/subscription/products")`

### 步骤 2：查看具体的语法错误

```bash
# 查看具体的语法错误
python3 -m py_compile /opt/beatsync/web_service/backend/main.py 2>&1
```

**如果报错**：会显示具体的错误位置和原因

### 步骤 3：强制更新代码

```bash
# 强制拉取最新代码
cd /opt/beatsync
sudo git fetch origin
sudo git reset --hard origin/main
sudo git pull origin main
```

### 步骤 4：检查代码语法

```bash
# 检查语法
python3 -m py_compile /opt/beatsync/web_service/backend/main.py
```

**如果通过**：继续下一步
**如果失败**：查看错误信息并修复

### 步骤 5：重启服务

```bash
sudo systemctl restart beatsync
sleep 3
sudo systemctl status beatsync
```

### 步骤 6：测试端点

```bash
# 直接测试后端
curl http://127.0.0.1:8000/api/subscription/products

# 通过 Nginx 测试
curl https://beatsync.site/api/subscription/products
```

---

## 一键修复命令

在服务器上执行：

```bash
cd /opt/beatsync && \
sudo git config --global --add safe.directory /opt/beatsync && \
sudo git fetch origin && \
sudo git reset --hard origin/main && \
sudo git pull origin main && \
echo "=== 检查代码 ===" && \
grep -n "subscription/products" web_service/backend/main.py && \
echo "=== 检查语法 ===" && \
python3 -m py_compile web_service/backend/main.py 2>&1 && echo "✅ 语法正确" || echo "❌ 语法错误" && \
echo "=== 重启服务 ===" && \
sudo systemctl restart beatsync && \
sleep 3 && \
echo "=== 测试端点 ===" && \
curl -s http://127.0.0.1:8000/api/subscription/products | head -20
```

---

## 如果仍然返回 404

### 检查服务日志

```bash
# 查看服务启动日志
sudo journalctl -u beatsync -n 100 | grep -i "error\|exception\|traceback\|subscription"
```

### 手动测试导入

```bash
cd /opt/beatsync/web_service/backend
python3 -c "from main import app; print('导入成功')"
```

**如果导入失败**：会显示具体错误

### 检查路由注册

```bash
cat > /tmp/check_routes.py << 'EOF'
import sys
sys.path.insert(0, '/opt/beatsync/web_service/backend')
try:
    from main import app
    routes = [r for r in app.routes if hasattr(r, 'path') and 'subscription' in r.path]
    if routes:
        print("✅ 找到订阅路由：")
        for r in routes:
            print(f"  {r.path}")
    else:
        print("❌ 未找到订阅路由")
        print("所有路由（前20个）：")
        all_routes = [r for r in app.routes if hasattr(r, 'path')][:20]
        for r in all_routes:
            print(f"  {r.path}")
except Exception as e:
    print(f"❌ 导入失败: {e}")
    import traceback
    traceback.print_exc()
EOF

python3 /tmp/check_routes.py
```

---

**请执行上述一键修复命令，并告诉我输出结果！** 🔧



# 修复服务器 404 错误

## 问题诊断

从诊断结果看：
- ✅ 服务正在运行
- ❌ 直接测试后端返回 404
- ❌ 通过 Nginx 也返回 404
- ⚠️ 代码可能未更新或有语法错误

## 解决方案

### 步骤 1：确认代码已更新

在服务器上执行：

```bash
# 检查端点是否在代码中
grep -n "subscription/products" /opt/beatsync/web_service/backend/main.py
```

**如果没有输出**：说明代码未更新

**如果有输出**：应该看到类似 `1133:@app.get("/api/subscription/products")`

### 步骤 2：查看具体的语法错误

```bash
# 查看具体的语法错误
python3 -m py_compile /opt/beatsync/web_service/backend/main.py 2>&1
```

**如果报错**：会显示具体的错误位置和原因

### 步骤 3：强制更新代码

```bash
# 强制拉取最新代码
cd /opt/beatsync
sudo git fetch origin
sudo git reset --hard origin/main
sudo git pull origin main
```

### 步骤 4：检查代码语法

```bash
# 检查语法
python3 -m py_compile /opt/beatsync/web_service/backend/main.py
```

**如果通过**：继续下一步
**如果失败**：查看错误信息并修复

### 步骤 5：重启服务

```bash
sudo systemctl restart beatsync
sleep 3
sudo systemctl status beatsync
```

### 步骤 6：测试端点

```bash
# 直接测试后端
curl http://127.0.0.1:8000/api/subscription/products

# 通过 Nginx 测试
curl https://beatsync.site/api/subscription/products
```

---

## 一键修复命令

在服务器上执行：

```bash
cd /opt/beatsync && \
sudo git config --global --add safe.directory /opt/beatsync && \
sudo git fetch origin && \
sudo git reset --hard origin/main && \
sudo git pull origin main && \
echo "=== 检查代码 ===" && \
grep -n "subscription/products" web_service/backend/main.py && \
echo "=== 检查语法 ===" && \
python3 -m py_compile web_service/backend/main.py 2>&1 && echo "✅ 语法正确" || echo "❌ 语法错误" && \
echo "=== 重启服务 ===" && \
sudo systemctl restart beatsync && \
sleep 3 && \
echo "=== 测试端点 ===" && \
curl -s http://127.0.0.1:8000/api/subscription/products | head -20
```

---

## 如果仍然返回 404

### 检查服务日志

```bash
# 查看服务启动日志
sudo journalctl -u beatsync -n 100 | grep -i "error\|exception\|traceback\|subscription"
```

### 手动测试导入

```bash
cd /opt/beatsync/web_service/backend
python3 -c "from main import app; print('导入成功')"
```

**如果导入失败**：会显示具体错误

### 检查路由注册

```bash
cat > /tmp/check_routes.py << 'EOF'
import sys
sys.path.insert(0, '/opt/beatsync/web_service/backend')
try:
    from main import app
    routes = [r for r in app.routes if hasattr(r, 'path') and 'subscription' in r.path]
    if routes:
        print("✅ 找到订阅路由：")
        for r in routes:
            print(f"  {r.path}")
    else:
        print("❌ 未找到订阅路由")
        print("所有路由（前20个）：")
        all_routes = [r for r in app.routes if hasattr(r, 'path')][:20]
        for r in all_routes:
            print(f"  {r.path}")
except Exception as e:
    print(f"❌ 导入失败: {e}")
    import traceback
    traceback.print_exc()
EOF

python3 /tmp/check_routes.py
```

---

**请执行上述一键修复命令，并告诉我输出结果！** 🔧



# 修复服务器 404 错误

## 问题诊断

从诊断结果看：
- ✅ 服务正在运行
- ❌ 直接测试后端返回 404
- ❌ 通过 Nginx 也返回 404
- ⚠️ 代码可能未更新或有语法错误

## 解决方案

### 步骤 1：确认代码已更新

在服务器上执行：

```bash
# 检查端点是否在代码中
grep -n "subscription/products" /opt/beatsync/web_service/backend/main.py
```

**如果没有输出**：说明代码未更新

**如果有输出**：应该看到类似 `1133:@app.get("/api/subscription/products")`

### 步骤 2：查看具体的语法错误

```bash
# 查看具体的语法错误
python3 -m py_compile /opt/beatsync/web_service/backend/main.py 2>&1
```

**如果报错**：会显示具体的错误位置和原因

### 步骤 3：强制更新代码

```bash
# 强制拉取最新代码
cd /opt/beatsync
sudo git fetch origin
sudo git reset --hard origin/main
sudo git pull origin main
```

### 步骤 4：检查代码语法

```bash
# 检查语法
python3 -m py_compile /opt/beatsync/web_service/backend/main.py
```

**如果通过**：继续下一步
**如果失败**：查看错误信息并修复

### 步骤 5：重启服务

```bash
sudo systemctl restart beatsync
sleep 3
sudo systemctl status beatsync
```

### 步骤 6：测试端点

```bash
# 直接测试后端
curl http://127.0.0.1:8000/api/subscription/products

# 通过 Nginx 测试
curl https://beatsync.site/api/subscription/products
```

---

## 一键修复命令

在服务器上执行：

```bash
cd /opt/beatsync && \
sudo git config --global --add safe.directory /opt/beatsync && \
sudo git fetch origin && \
sudo git reset --hard origin/main && \
sudo git pull origin main && \
echo "=== 检查代码 ===" && \
grep -n "subscription/products" web_service/backend/main.py && \
echo "=== 检查语法 ===" && \
python3 -m py_compile web_service/backend/main.py 2>&1 && echo "✅ 语法正确" || echo "❌ 语法错误" && \
echo "=== 重启服务 ===" && \
sudo systemctl restart beatsync && \
sleep 3 && \
echo "=== 测试端点 ===" && \
curl -s http://127.0.0.1:8000/api/subscription/products | head -20
```

---

## 如果仍然返回 404

### 检查服务日志

```bash
# 查看服务启动日志
sudo journalctl -u beatsync -n 100 | grep -i "error\|exception\|traceback\|subscription"
```

### 手动测试导入

```bash
cd /opt/beatsync/web_service/backend
python3 -c "from main import app; print('导入成功')"
```

**如果导入失败**：会显示具体错误

### 检查路由注册

```bash
cat > /tmp/check_routes.py << 'EOF'
import sys
sys.path.insert(0, '/opt/beatsync/web_service/backend')
try:
    from main import app
    routes = [r for r in app.routes if hasattr(r, 'path') and 'subscription' in r.path]
    if routes:
        print("✅ 找到订阅路由：")
        for r in routes:
            print(f"  {r.path}")
    else:
        print("❌ 未找到订阅路由")
        print("所有路由（前20个）：")
        all_routes = [r for r in app.routes if hasattr(r, 'path')][:20]
        for r in all_routes:
            print(f"  {r.path}")
except Exception as e:
    print(f"❌ 导入失败: {e}")
    import traceback
    traceback.print_exc()
EOF

python3 /tmp/check_routes.py
```

---

**请执行上述一键修复命令，并告诉我输出结果！** 🔧














