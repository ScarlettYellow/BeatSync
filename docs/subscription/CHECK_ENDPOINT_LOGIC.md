# 检查端点逻辑

## 问题

数据库已初始化，`is_subscription_enabled()` 返回 `True`，但端点仍返回未启用。

可能是端点函数中的 `SUBSCRIPTION_AVAILABLE` 检查有问题。

## 诊断步骤

在服务器上执行：

```bash
cd /opt/beatsync && \
echo "=== 1. 检查端点函数代码 ===" && \
ENDPOINT_LINE=$(grep -n "@app.get.*subscription/products" web_service/backend/main.py | cut -d: -f1) && \
sed -n "$((ENDPOINT_LINE)),$((ENDPOINT_LINE+30))p" web_service/backend/main.py && \
echo "" && \
echo "=== 2. 检查 SUBSCRIPTION_AVAILABLE 的值 ===" && \
cd web_service/backend && \
python3 << 'PYTHON_CHECK'
import sys
import os
sys.path.insert(0, '/opt/beatsync/web_service/backend')

os.environ["SUBSCRIPTION_ENABLED"] = "true"

# 清除模块缓存
import importlib
modules_to_reload = ['main', 'subscription_service', 'subscription_db']
for mod in modules_to_reload:
    if mod in sys.modules:
        del sys.modules[mod]

# 导入 main 模块
from main import app, SUBSCRIPTION_AVAILABLE
from subscription_service import is_subscription_enabled

print(f"SUBSCRIPTION_AVAILABLE = {SUBSCRIPTION_AVAILABLE}")
print(f"is_subscription_enabled() = {is_subscription_enabled()}")

# 模拟端点函数逻辑
try:
    subscription_available = SUBSCRIPTION_AVAILABLE
except NameError:
    subscription_available = False

try:
    subscription_enabled = is_subscription_enabled()
except NameError:
    subscription_enabled = False

print(f"\n端点函数逻辑检查:")
print(f"  subscription_available = {subscription_available}")
print(f"  subscription_enabled = {subscription_enabled}")

if not subscription_available:
    print("  ❌ subscription_available 为 False，会返回未启用")
if not subscription_enabled:
    print("  ❌ subscription_enabled 为 False，会返回未启用")
if subscription_available and subscription_enabled:
    print("  ✅ 两个检查都通过，应该返回产品列表")
PYTHON_CHECK
echo "" && \
echo "=== 3. 检查服务日志（导入错误）===" && \
sudo journalctl -u beatsync --since "5 minutes ago" | grep -i "warning\|error\|import" | tail -10
```

---

**请执行上述命令，检查端点逻辑！** 🔍


# 检查端点逻辑

## 问题

数据库已初始化，`is_subscription_enabled()` 返回 `True`，但端点仍返回未启用。

可能是端点函数中的 `SUBSCRIPTION_AVAILABLE` 检查有问题。

## 诊断步骤

在服务器上执行：

```bash
cd /opt/beatsync && \
echo "=== 1. 检查端点函数代码 ===" && \
ENDPOINT_LINE=$(grep -n "@app.get.*subscription/products" web_service/backend/main.py | cut -d: -f1) && \
sed -n "$((ENDPOINT_LINE)),$((ENDPOINT_LINE+30))p" web_service/backend/main.py && \
echo "" && \
echo "=== 2. 检查 SUBSCRIPTION_AVAILABLE 的值 ===" && \
cd web_service/backend && \
python3 << 'PYTHON_CHECK'
import sys
import os
sys.path.insert(0, '/opt/beatsync/web_service/backend')

os.environ["SUBSCRIPTION_ENABLED"] = "true"

# 清除模块缓存
import importlib
modules_to_reload = ['main', 'subscription_service', 'subscription_db']
for mod in modules_to_reload:
    if mod in sys.modules:
        del sys.modules[mod]

# 导入 main 模块
from main import app, SUBSCRIPTION_AVAILABLE
from subscription_service import is_subscription_enabled

print(f"SUBSCRIPTION_AVAILABLE = {SUBSCRIPTION_AVAILABLE}")
print(f"is_subscription_enabled() = {is_subscription_enabled()}")

# 模拟端点函数逻辑
try:
    subscription_available = SUBSCRIPTION_AVAILABLE
except NameError:
    subscription_available = False

try:
    subscription_enabled = is_subscription_enabled()
except NameError:
    subscription_enabled = False

print(f"\n端点函数逻辑检查:")
print(f"  subscription_available = {subscription_available}")
print(f"  subscription_enabled = {subscription_enabled}")

if not subscription_available:
    print("  ❌ subscription_available 为 False，会返回未启用")
if not subscription_enabled:
    print("  ❌ subscription_enabled 为 False，会返回未启用")
if subscription_available and subscription_enabled:
    print("  ✅ 两个检查都通过，应该返回产品列表")
PYTHON_CHECK
echo "" && \
echo "=== 3. 检查服务日志（导入错误）===" && \
sudo journalctl -u beatsync --since "5 minutes ago" | grep -i "warning\|error\|import" | tail -10
```

---

**请执行上述命令，检查端点逻辑！** 🔍


# 检查端点逻辑

## 问题

数据库已初始化，`is_subscription_enabled()` 返回 `True`，但端点仍返回未启用。

可能是端点函数中的 `SUBSCRIPTION_AVAILABLE` 检查有问题。

## 诊断步骤

在服务器上执行：

```bash
cd /opt/beatsync && \
echo "=== 1. 检查端点函数代码 ===" && \
ENDPOINT_LINE=$(grep -n "@app.get.*subscription/products" web_service/backend/main.py | cut -d: -f1) && \
sed -n "$((ENDPOINT_LINE)),$((ENDPOINT_LINE+30))p" web_service/backend/main.py && \
echo "" && \
echo "=== 2. 检查 SUBSCRIPTION_AVAILABLE 的值 ===" && \
cd web_service/backend && \
python3 << 'PYTHON_CHECK'
import sys
import os
sys.path.insert(0, '/opt/beatsync/web_service/backend')

os.environ["SUBSCRIPTION_ENABLED"] = "true"

# 清除模块缓存
import importlib
modules_to_reload = ['main', 'subscription_service', 'subscription_db']
for mod in modules_to_reload:
    if mod in sys.modules:
        del sys.modules[mod]

# 导入 main 模块
from main import app, SUBSCRIPTION_AVAILABLE
from subscription_service import is_subscription_enabled

print(f"SUBSCRIPTION_AVAILABLE = {SUBSCRIPTION_AVAILABLE}")
print(f"is_subscription_enabled() = {is_subscription_enabled()}")

# 模拟端点函数逻辑
try:
    subscription_available = SUBSCRIPTION_AVAILABLE
except NameError:
    subscription_available = False

try:
    subscription_enabled = is_subscription_enabled()
except NameError:
    subscription_enabled = False

print(f"\n端点函数逻辑检查:")
print(f"  subscription_available = {subscription_available}")
print(f"  subscription_enabled = {subscription_enabled}")

if not subscription_available:
    print("  ❌ subscription_available 为 False，会返回未启用")
if not subscription_enabled:
    print("  ❌ subscription_enabled 为 False，会返回未启用")
if subscription_available and subscription_enabled:
    print("  ✅ 两个检查都通过，应该返回产品列表")
PYTHON_CHECK
echo "" && \
echo "=== 3. 检查服务日志（导入错误）===" && \
sudo journalctl -u beatsync --since "5 minutes ago" | grep -i "warning\|error\|import" | tail -10
```

---

**请执行上述命令，检查端点逻辑！** 🔍













