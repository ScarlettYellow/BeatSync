# 强制更新服务器代码

## 问题诊断

从诊断结果看：
- ❌ `grep` 没有找到端点定义 → **代码未更新到服务器**
- ⚠️ `Permission denied` → 权限问题（不影响功能）

## 解决方案

### 步骤 1：强制更新代码

在服务器上执行：

```bash
cd /opt/beatsync

# 强制拉取最新代码
sudo git fetch origin
sudo git reset --hard origin/main
sudo git pull origin main

# 验证代码已更新
grep -n "subscription/products" web_service/backend/main.py
```

**应该看到**：`1133:@app.get("/api/subscription/products")`

### 步骤 2：修复权限问题（可选）

```bash
# 修复 __pycache__ 目录权限
sudo chown -R ubuntu:ubuntu /opt/beatsync/web_service/backend/__pycache__ 2>/dev/null || true
sudo chmod -R 755 /opt/beatsync/web_service/backend/__pycache__ 2>/dev/null || true
```

### 步骤 3：检查语法（使用临时目录）

```bash
# 使用临时目录编译，避免权限问题
python3 -c "import py_compile; py_compile.compile('/opt/beatsync/web_service/backend/main.py', doraise=True)" && echo "✅ 语法正确"
```

### 步骤 4：重启服务

```bash
sudo systemctl restart beatsync
sleep 3
sudo systemctl status beatsync | head -10
```

### 步骤 5：测试端点

```bash
# 直接测试后端
curl -s http://127.0.0.1:8000/api/subscription/products | head -30

# 通过 Nginx 测试
curl -s https://beatsync.site/api/subscription/products | head -30
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
echo "=== 验证代码已更新 ===" && \
grep -n "subscription/products" web_service/backend/main.py && \
echo "=== 检查语法（使用临时目录）===" && \
python3 -c "import py_compile; py_compile.compile('/opt/beatsync/web_service/backend/main.py', doraise=True)" && echo "✅ 语法正确" || echo "❌ 语法错误" && \
echo "=== 重启服务 ===" && \
sudo systemctl restart beatsync && \
sleep 3 && \
echo "=== 测试端点 ===" && \
curl -s http://127.0.0.1:8000/api/subscription/products | head -30
```

---

## 预期结果

执行后应该看到：

1. **代码已更新**：
   ```
   1133:@app.get("/api/subscription/products")
   ```

2. **语法正确**：
   ```
   ✅ 语法正确
   ```

3. **端点返回产品列表**：
   ```json
   {
     "products": [
       {
         "id": "basic_monthly",
         ...
       }
     ],
     "count": 4
   }
   ```

---

**请执行上述一键修复命令，并告诉我输出结果！** 🚀



# 强制更新服务器代码

## 问题诊断

从诊断结果看：
- ❌ `grep` 没有找到端点定义 → **代码未更新到服务器**
- ⚠️ `Permission denied` → 权限问题（不影响功能）

## 解决方案

### 步骤 1：强制更新代码

在服务器上执行：

```bash
cd /opt/beatsync

# 强制拉取最新代码
sudo git fetch origin
sudo git reset --hard origin/main
sudo git pull origin main

# 验证代码已更新
grep -n "subscription/products" web_service/backend/main.py
```

**应该看到**：`1133:@app.get("/api/subscription/products")`

### 步骤 2：修复权限问题（可选）

```bash
# 修复 __pycache__ 目录权限
sudo chown -R ubuntu:ubuntu /opt/beatsync/web_service/backend/__pycache__ 2>/dev/null || true
sudo chmod -R 755 /opt/beatsync/web_service/backend/__pycache__ 2>/dev/null || true
```

### 步骤 3：检查语法（使用临时目录）

```bash
# 使用临时目录编译，避免权限问题
python3 -c "import py_compile; py_compile.compile('/opt/beatsync/web_service/backend/main.py', doraise=True)" && echo "✅ 语法正确"
```

### 步骤 4：重启服务

```bash
sudo systemctl restart beatsync
sleep 3
sudo systemctl status beatsync | head -10
```

### 步骤 5：测试端点

```bash
# 直接测试后端
curl -s http://127.0.0.1:8000/api/subscription/products | head -30

# 通过 Nginx 测试
curl -s https://beatsync.site/api/subscription/products | head -30
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
echo "=== 验证代码已更新 ===" && \
grep -n "subscription/products" web_service/backend/main.py && \
echo "=== 检查语法（使用临时目录）===" && \
python3 -c "import py_compile; py_compile.compile('/opt/beatsync/web_service/backend/main.py', doraise=True)" && echo "✅ 语法正确" || echo "❌ 语法错误" && \
echo "=== 重启服务 ===" && \
sudo systemctl restart beatsync && \
sleep 3 && \
echo "=== 测试端点 ===" && \
curl -s http://127.0.0.1:8000/api/subscription/products | head -30
```

---

## 预期结果

执行后应该看到：

1. **代码已更新**：
   ```
   1133:@app.get("/api/subscription/products")
   ```

2. **语法正确**：
   ```
   ✅ 语法正确
   ```

3. **端点返回产品列表**：
   ```json
   {
     "products": [
       {
         "id": "basic_monthly",
         ...
       }
     ],
     "count": 4
   }
   ```

---

**请执行上述一键修复命令，并告诉我输出结果！** 🚀



# 强制更新服务器代码

## 问题诊断

从诊断结果看：
- ❌ `grep` 没有找到端点定义 → **代码未更新到服务器**
- ⚠️ `Permission denied` → 权限问题（不影响功能）

## 解决方案

### 步骤 1：强制更新代码

在服务器上执行：

```bash
cd /opt/beatsync

# 强制拉取最新代码
sudo git fetch origin
sudo git reset --hard origin/main
sudo git pull origin main

# 验证代码已更新
grep -n "subscription/products" web_service/backend/main.py
```

**应该看到**：`1133:@app.get("/api/subscription/products")`

### 步骤 2：修复权限问题（可选）

```bash
# 修复 __pycache__ 目录权限
sudo chown -R ubuntu:ubuntu /opt/beatsync/web_service/backend/__pycache__ 2>/dev/null || true
sudo chmod -R 755 /opt/beatsync/web_service/backend/__pycache__ 2>/dev/null || true
```

### 步骤 3：检查语法（使用临时目录）

```bash
# 使用临时目录编译，避免权限问题
python3 -c "import py_compile; py_compile.compile('/opt/beatsync/web_service/backend/main.py', doraise=True)" && echo "✅ 语法正确"
```

### 步骤 4：重启服务

```bash
sudo systemctl restart beatsync
sleep 3
sudo systemctl status beatsync | head -10
```

### 步骤 5：测试端点

```bash
# 直接测试后端
curl -s http://127.0.0.1:8000/api/subscription/products | head -30

# 通过 Nginx 测试
curl -s https://beatsync.site/api/subscription/products | head -30
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
echo "=== 验证代码已更新 ===" && \
grep -n "subscription/products" web_service/backend/main.py && \
echo "=== 检查语法（使用临时目录）===" && \
python3 -c "import py_compile; py_compile.compile('/opt/beatsync/web_service/backend/main.py', doraise=True)" && echo "✅ 语法正确" || echo "❌ 语法错误" && \
echo "=== 重启服务 ===" && \
sudo systemctl restart beatsync && \
sleep 3 && \
echo "=== 测试端点 ===" && \
curl -s http://127.0.0.1:8000/api/subscription/products | head -30
```

---

## 预期结果

执行后应该看到：

1. **代码已更新**：
   ```
   1133:@app.get("/api/subscription/products")
   ```

2. **语法正确**：
   ```
   ✅ 语法正确
   ```

3. **端点返回产品列表**：
   ```json
   {
     "products": [
       {
         "id": "basic_monthly",
         ...
       }
     ],
     "count": 4
   }
   ```

---

**请执行上述一键修复命令，并告诉我输出结果！** 🚀














