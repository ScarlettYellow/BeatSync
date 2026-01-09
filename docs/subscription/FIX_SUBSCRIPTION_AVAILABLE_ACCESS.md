# 修复 SUBSCRIPTION_AVAILABLE 访问问题

## 问题

`SUBSCRIPTION_AVAILABLE` 无法从 `main` 模块导入，端点函数无法访问它。

## 解决方案

检查 `main.py` 中 `SUBSCRIPTION_AVAILABLE` 的定义，确保端点函数可以访问它。

## 在服务器上执行：

```bash
cd /opt/beatsync && \
echo "=== 1. 检查 SUBSCRIPTION_AVAILABLE 定义 ===" && \
grep -n "SUBSCRIPTION_AVAILABLE" web_service/backend/main.py | head -5 && \
echo "" && \
echo "=== 2. 查看定义上下文 ===" && \
grep -B 10 -A 5 "SUBSCRIPTION_AVAILABLE = True" web_service/backend/main.py | head -20 && \
echo "" && \
echo "=== 3. 测试直接访问 ===" && \
cd web_service/backend && \
python3 << 'PYTHON_TEST'
import sys
import os
sys.path.insert(0, '/opt/beatsync/web_service/backend')

os.environ["SUBSCRIPTION_ENABLED"] = "true"

# 直接执行 main.py 中的相关代码
exec(open('/opt/beatsync/web_service/backend/main.py').read().split('app = FastAPI')[0])

print(f"SUBSCRIPTION_AVAILABLE = {SUBSCRIPTION_AVAILABLE}")

# 测试端点函数逻辑
try:
    subscription_available = SUBSCRIPTION_AVAILABLE
    print(f"✅ 可以访问 SUBSCRIPTION_AVAILABLE = {subscription_available}")
except NameError as e:
    print(f"❌ 无法访问 SUBSCRIPTION_AVAILABLE: {e}")
PYTHON_TEST
```

---

**请执行上述命令，检查 SUBSCRIPTION_AVAILABLE 的定义！** 🔍


# 修复 SUBSCRIPTION_AVAILABLE 访问问题

## 问题

`SUBSCRIPTION_AVAILABLE` 无法从 `main` 模块导入，端点函数无法访问它。

## 解决方案

检查 `main.py` 中 `SUBSCRIPTION_AVAILABLE` 的定义，确保端点函数可以访问它。

## 在服务器上执行：

```bash
cd /opt/beatsync && \
echo "=== 1. 检查 SUBSCRIPTION_AVAILABLE 定义 ===" && \
grep -n "SUBSCRIPTION_AVAILABLE" web_service/backend/main.py | head -5 && \
echo "" && \
echo "=== 2. 查看定义上下文 ===" && \
grep -B 10 -A 5 "SUBSCRIPTION_AVAILABLE = True" web_service/backend/main.py | head -20 && \
echo "" && \
echo "=== 3. 测试直接访问 ===" && \
cd web_service/backend && \
python3 << 'PYTHON_TEST'
import sys
import os
sys.path.insert(0, '/opt/beatsync/web_service/backend')

os.environ["SUBSCRIPTION_ENABLED"] = "true"

# 直接执行 main.py 中的相关代码
exec(open('/opt/beatsync/web_service/backend/main.py').read().split('app = FastAPI')[0])

print(f"SUBSCRIPTION_AVAILABLE = {SUBSCRIPTION_AVAILABLE}")

# 测试端点函数逻辑
try:
    subscription_available = SUBSCRIPTION_AVAILABLE
    print(f"✅ 可以访问 SUBSCRIPTION_AVAILABLE = {subscription_available}")
except NameError as e:
    print(f"❌ 无法访问 SUBSCRIPTION_AVAILABLE: {e}")
PYTHON_TEST
```

---

**请执行上述命令，检查 SUBSCRIPTION_AVAILABLE 的定义！** 🔍


# 修复 SUBSCRIPTION_AVAILABLE 访问问题

## 问题

`SUBSCRIPTION_AVAILABLE` 无法从 `main` 模块导入，端点函数无法访问它。

## 解决方案

检查 `main.py` 中 `SUBSCRIPTION_AVAILABLE` 的定义，确保端点函数可以访问它。

## 在服务器上执行：

```bash
cd /opt/beatsync && \
echo "=== 1. 检查 SUBSCRIPTION_AVAILABLE 定义 ===" && \
grep -n "SUBSCRIPTION_AVAILABLE" web_service/backend/main.py | head -5 && \
echo "" && \
echo "=== 2. 查看定义上下文 ===" && \
grep -B 10 -A 5 "SUBSCRIPTION_AVAILABLE = True" web_service/backend/main.py | head -20 && \
echo "" && \
echo "=== 3. 测试直接访问 ===" && \
cd web_service/backend && \
python3 << 'PYTHON_TEST'
import sys
import os
sys.path.insert(0, '/opt/beatsync/web_service/backend')

os.environ["SUBSCRIPTION_ENABLED"] = "true"

# 直接执行 main.py 中的相关代码
exec(open('/opt/beatsync/web_service/backend/main.py').read().split('app = FastAPI')[0])

print(f"SUBSCRIPTION_AVAILABLE = {SUBSCRIPTION_AVAILABLE}")

# 测试端点函数逻辑
try:
    subscription_available = SUBSCRIPTION_AVAILABLE
    print(f"✅ 可以访问 SUBSCRIPTION_AVAILABLE = {subscription_available}")
except NameError as e:
    print(f"❌ 无法访问 SUBSCRIPTION_AVAILABLE: {e}")
PYTHON_TEST
```

---

**请执行上述命令，检查 SUBSCRIPTION_AVAILABLE 的定义！** 🔍













