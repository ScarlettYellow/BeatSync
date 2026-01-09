# 检查 SUBSCRIPTION_AVAILABLE 定义

## 问题

端点函数已修复为使用 `globals()`，但仍返回未启用。需要检查 `SUBSCRIPTION_AVAILABLE` 的实际定义和值。

## 诊断步骤

在服务器上执行：

```bash
cd /opt/beatsync && \
echo "=== 1. 查找 SUBSCRIPTION_AVAILABLE 的定义 ===" && \
grep -n "SUBSCRIPTION_AVAILABLE" web_service/backend/main.py && \
echo "" && \
echo "=== 2. 查看导入订阅模块的代码 ===" && \
sed -n '36,60p' web_service/backend/main.py && \
echo "" && \
echo "=== 3. 测试模块导入和 SUBSCRIPTION_AVAILABLE 的值 ===" && \
cd web_service/backend && \
python3 << 'PYTHON_TEST'
import sys
import os
sys.path.insert(0, '/opt/beatsync/web_service/backend')

os.environ["SUBSCRIPTION_ENABLED"] = "true"

# 清除模块缓存
import importlib
if 'main' in sys.modules:
    del sys.modules['main']

# 导入 main 模块
import main

# 检查 SUBSCRIPTION_AVAILABLE
if hasattr(main, 'SUBSCRIPTION_AVAILABLE'):
    print(f"✅ SUBSCRIPTION_AVAILABLE = {main.SUBSCRIPTION_AVAILABLE}")
else:
    print("❌ main 模块中没有 SUBSCRIPTION_AVAILABLE 属性")

# 检查 globals()
print(f"\n检查 globals():")
if 'SUBSCRIPTION_AVAILABLE' in globals():
    print(f"  globals()['SUBSCRIPTION_AVAILABLE'] = {globals()['SUBSCRIPTION_AVAILABLE']}")
else:
    print("  globals() 中没有 SUBSCRIPTION_AVAILABLE")

# 检查 main 模块的 globals
if hasattr(main, '__dict__'):
    if 'SUBSCRIPTION_AVAILABLE' in main.__dict__:
        print(f"  main.__dict__['SUBSCRIPTION_AVAILABLE'] = {main.__dict__['SUBSCRIPTION_AVAILABLE']}")
    else:
        print("  main.__dict__ 中没有 SUBSCRIPTION_AVAILABLE")

# 测试端点函数逻辑
print(f"\n测试端点函数逻辑:")
try:
    # 模拟端点函数中的代码
    subscription_available = globals().get("SUBSCRIPTION_AVAILABLE", False)
    print(f"  globals().get('SUBSCRIPTION_AVAILABLE', False) = {subscription_available}")
    
    # 尝试从 main 模块获取
    if hasattr(main, 'SUBSCRIPTION_AVAILABLE'):
        subscription_available = main.SUBSCRIPTION_AVAILABLE
        print(f"  main.SUBSCRIPTION_AVAILABLE = {subscription_available}")
except Exception as e:
    print(f"  ❌ 错误: {e}")

# 测试 is_subscription_enabled
from subscription_service import is_subscription_enabled
print(f"\nis_subscription_enabled() = {is_subscription_enabled()}")
PYTHON_TEST
echo "" && \
echo "=== 4. 检查服务日志（导入错误）===" && \
sudo journalctl -u beatsync --since "10 minutes ago" | grep -iE "warning|error|import|subscription" | tail -20
```

---

**请执行上述命令，检查 SUBSCRIPTION_AVAILABLE 的定义和值！** 🔍


# 检查 SUBSCRIPTION_AVAILABLE 定义

## 问题

端点函数已修复为使用 `globals()`，但仍返回未启用。需要检查 `SUBSCRIPTION_AVAILABLE` 的实际定义和值。

## 诊断步骤

在服务器上执行：

```bash
cd /opt/beatsync && \
echo "=== 1. 查找 SUBSCRIPTION_AVAILABLE 的定义 ===" && \
grep -n "SUBSCRIPTION_AVAILABLE" web_service/backend/main.py && \
echo "" && \
echo "=== 2. 查看导入订阅模块的代码 ===" && \
sed -n '36,60p' web_service/backend/main.py && \
echo "" && \
echo "=== 3. 测试模块导入和 SUBSCRIPTION_AVAILABLE 的值 ===" && \
cd web_service/backend && \
python3 << 'PYTHON_TEST'
import sys
import os
sys.path.insert(0, '/opt/beatsync/web_service/backend')

os.environ["SUBSCRIPTION_ENABLED"] = "true"

# 清除模块缓存
import importlib
if 'main' in sys.modules:
    del sys.modules['main']

# 导入 main 模块
import main

# 检查 SUBSCRIPTION_AVAILABLE
if hasattr(main, 'SUBSCRIPTION_AVAILABLE'):
    print(f"✅ SUBSCRIPTION_AVAILABLE = {main.SUBSCRIPTION_AVAILABLE}")
else:
    print("❌ main 模块中没有 SUBSCRIPTION_AVAILABLE 属性")

# 检查 globals()
print(f"\n检查 globals():")
if 'SUBSCRIPTION_AVAILABLE' in globals():
    print(f"  globals()['SUBSCRIPTION_AVAILABLE'] = {globals()['SUBSCRIPTION_AVAILABLE']}")
else:
    print("  globals() 中没有 SUBSCRIPTION_AVAILABLE")

# 检查 main 模块的 globals
if hasattr(main, '__dict__'):
    if 'SUBSCRIPTION_AVAILABLE' in main.__dict__:
        print(f"  main.__dict__['SUBSCRIPTION_AVAILABLE'] = {main.__dict__['SUBSCRIPTION_AVAILABLE']}")
    else:
        print("  main.__dict__ 中没有 SUBSCRIPTION_AVAILABLE")

# 测试端点函数逻辑
print(f"\n测试端点函数逻辑:")
try:
    # 模拟端点函数中的代码
    subscription_available = globals().get("SUBSCRIPTION_AVAILABLE", False)
    print(f"  globals().get('SUBSCRIPTION_AVAILABLE', False) = {subscription_available}")
    
    # 尝试从 main 模块获取
    if hasattr(main, 'SUBSCRIPTION_AVAILABLE'):
        subscription_available = main.SUBSCRIPTION_AVAILABLE
        print(f"  main.SUBSCRIPTION_AVAILABLE = {subscription_available}")
except Exception as e:
    print(f"  ❌ 错误: {e}")

# 测试 is_subscription_enabled
from subscription_service import is_subscription_enabled
print(f"\nis_subscription_enabled() = {is_subscription_enabled()}")
PYTHON_TEST
echo "" && \
echo "=== 4. 检查服务日志（导入错误）===" && \
sudo journalctl -u beatsync --since "10 minutes ago" | grep -iE "warning|error|import|subscription" | tail -20
```

---

**请执行上述命令，检查 SUBSCRIPTION_AVAILABLE 的定义和值！** 🔍


# 检查 SUBSCRIPTION_AVAILABLE 定义

## 问题

端点函数已修复为使用 `globals()`，但仍返回未启用。需要检查 `SUBSCRIPTION_AVAILABLE` 的实际定义和值。

## 诊断步骤

在服务器上执行：

```bash
cd /opt/beatsync && \
echo "=== 1. 查找 SUBSCRIPTION_AVAILABLE 的定义 ===" && \
grep -n "SUBSCRIPTION_AVAILABLE" web_service/backend/main.py && \
echo "" && \
echo "=== 2. 查看导入订阅模块的代码 ===" && \
sed -n '36,60p' web_service/backend/main.py && \
echo "" && \
echo "=== 3. 测试模块导入和 SUBSCRIPTION_AVAILABLE 的值 ===" && \
cd web_service/backend && \
python3 << 'PYTHON_TEST'
import sys
import os
sys.path.insert(0, '/opt/beatsync/web_service/backend')

os.environ["SUBSCRIPTION_ENABLED"] = "true"

# 清除模块缓存
import importlib
if 'main' in sys.modules:
    del sys.modules['main']

# 导入 main 模块
import main

# 检查 SUBSCRIPTION_AVAILABLE
if hasattr(main, 'SUBSCRIPTION_AVAILABLE'):
    print(f"✅ SUBSCRIPTION_AVAILABLE = {main.SUBSCRIPTION_AVAILABLE}")
else:
    print("❌ main 模块中没有 SUBSCRIPTION_AVAILABLE 属性")

# 检查 globals()
print(f"\n检查 globals():")
if 'SUBSCRIPTION_AVAILABLE' in globals():
    print(f"  globals()['SUBSCRIPTION_AVAILABLE'] = {globals()['SUBSCRIPTION_AVAILABLE']}")
else:
    print("  globals() 中没有 SUBSCRIPTION_AVAILABLE")

# 检查 main 模块的 globals
if hasattr(main, '__dict__'):
    if 'SUBSCRIPTION_AVAILABLE' in main.__dict__:
        print(f"  main.__dict__['SUBSCRIPTION_AVAILABLE'] = {main.__dict__['SUBSCRIPTION_AVAILABLE']}")
    else:
        print("  main.__dict__ 中没有 SUBSCRIPTION_AVAILABLE")

# 测试端点函数逻辑
print(f"\n测试端点函数逻辑:")
try:
    # 模拟端点函数中的代码
    subscription_available = globals().get("SUBSCRIPTION_AVAILABLE", False)
    print(f"  globals().get('SUBSCRIPTION_AVAILABLE', False) = {subscription_available}")
    
    # 尝试从 main 模块获取
    if hasattr(main, 'SUBSCRIPTION_AVAILABLE'):
        subscription_available = main.SUBSCRIPTION_AVAILABLE
        print(f"  main.SUBSCRIPTION_AVAILABLE = {subscription_available}")
except Exception as e:
    print(f"  ❌ 错误: {e}")

# 测试 is_subscription_enabled
from subscription_service import is_subscription_enabled
print(f"\nis_subscription_enabled() = {is_subscription_enabled()}")
PYTHON_TEST
echo "" && \
echo "=== 4. 检查服务日志（导入错误）===" && \
sudo journalctl -u beatsync --since "10 minutes ago" | grep -iE "warning|error|import|subscription" | tail -20
```

---

**请执行上述命令，检查 SUBSCRIPTION_AVAILABLE 的定义和值！** 🔍













