# 验证环境变量配置

## 问题

端点已正常工作，但仍显示"订阅系统未启用"，说明环境变量可能未正确传递。

## 诊断步骤

在服务器上执行：

```bash
cd /opt/beatsync && \
echo "=== 1. 检查服务配置文件 ===" && \
sudo cat /etc/systemd/system/beatsync.service && \
echo "" && \
echo "=== 2. 检查服务实际读取的环境变量 ===" && \
sudo systemctl show beatsync | grep -E "Environment" && \
echo "" && \
echo "=== 3. 检查服务进程的环境变量 ===" && \
sudo cat /proc/$(sudo systemctl show beatsync -p MainPID --value)/environ | tr '\0' '\n' | grep -E "SUBSCRIPTION" || echo "未找到 SUBSCRIPTION 环境变量" && \
echo "" && \
echo "=== 4. 测试 Python 读取环境变量 ===" && \
cd web_service/backend && \
python3 << 'PYTHON_TEST'
import os
import sys
sys.path.insert(0, '/opt/beatsync/web_service/backend')

# 检查环境变量
subscription_enabled = os.getenv("SUBSCRIPTION_ENABLED", "not_set")
print(f"SUBSCRIPTION_ENABLED = {subscription_enabled}")

# 测试订阅服务
try:
    from subscription_service import is_subscription_enabled, SUBSCRIPTION_ENABLED
    print(f"subscription_service.SUBSCRIPTION_ENABLED = {SUBSCRIPTION_ENABLED}")
    print(f"is_subscription_enabled() = {is_subscription_enabled()}")
except Exception as e:
    print(f"❌ 导入失败: {e}")
    import traceback
    traceback.print_exc()
PYTHON_TEST
```

---

**请执行上述命令，并告诉我输出结果！** 🔍


# 验证环境变量配置

## 问题

端点已正常工作，但仍显示"订阅系统未启用"，说明环境变量可能未正确传递。

## 诊断步骤

在服务器上执行：

```bash
cd /opt/beatsync && \
echo "=== 1. 检查服务配置文件 ===" && \
sudo cat /etc/systemd/system/beatsync.service && \
echo "" && \
echo "=== 2. 检查服务实际读取的环境变量 ===" && \
sudo systemctl show beatsync | grep -E "Environment" && \
echo "" && \
echo "=== 3. 检查服务进程的环境变量 ===" && \
sudo cat /proc/$(sudo systemctl show beatsync -p MainPID --value)/environ | tr '\0' '\n' | grep -E "SUBSCRIPTION" || echo "未找到 SUBSCRIPTION 环境变量" && \
echo "" && \
echo "=== 4. 测试 Python 读取环境变量 ===" && \
cd web_service/backend && \
python3 << 'PYTHON_TEST'
import os
import sys
sys.path.insert(0, '/opt/beatsync/web_service/backend')

# 检查环境变量
subscription_enabled = os.getenv("SUBSCRIPTION_ENABLED", "not_set")
print(f"SUBSCRIPTION_ENABLED = {subscription_enabled}")

# 测试订阅服务
try:
    from subscription_service import is_subscription_enabled, SUBSCRIPTION_ENABLED
    print(f"subscription_service.SUBSCRIPTION_ENABLED = {SUBSCRIPTION_ENABLED}")
    print(f"is_subscription_enabled() = {is_subscription_enabled()}")
except Exception as e:
    print(f"❌ 导入失败: {e}")
    import traceback
    traceback.print_exc()
PYTHON_TEST
```

---

**请执行上述命令，并告诉我输出结果！** 🔍


# 验证环境变量配置

## 问题

端点已正常工作，但仍显示"订阅系统未启用"，说明环境变量可能未正确传递。

## 诊断步骤

在服务器上执行：

```bash
cd /opt/beatsync && \
echo "=== 1. 检查服务配置文件 ===" && \
sudo cat /etc/systemd/system/beatsync.service && \
echo "" && \
echo "=== 2. 检查服务实际读取的环境变量 ===" && \
sudo systemctl show beatsync | grep -E "Environment" && \
echo "" && \
echo "=== 3. 检查服务进程的环境变量 ===" && \
sudo cat /proc/$(sudo systemctl show beatsync -p MainPID --value)/environ | tr '\0' '\n' | grep -E "SUBSCRIPTION" || echo "未找到 SUBSCRIPTION 环境变量" && \
echo "" && \
echo "=== 4. 测试 Python 读取环境变量 ===" && \
cd web_service/backend && \
python3 << 'PYTHON_TEST'
import os
import sys
sys.path.insert(0, '/opt/beatsync/web_service/backend')

# 检查环境变量
subscription_enabled = os.getenv("SUBSCRIPTION_ENABLED", "not_set")
print(f"SUBSCRIPTION_ENABLED = {subscription_enabled}")

# 测试订阅服务
try:
    from subscription_service import is_subscription_enabled, SUBSCRIPTION_ENABLED
    print(f"subscription_service.SUBSCRIPTION_ENABLED = {SUBSCRIPTION_ENABLED}")
    print(f"is_subscription_enabled() = {is_subscription_enabled()}")
except Exception as e:
    print(f"❌ 导入失败: {e}")
    import traceback
    traceback.print_exc()
PYTHON_TEST
```

---

**请执行上述命令，并告诉我输出结果！** 🔍













