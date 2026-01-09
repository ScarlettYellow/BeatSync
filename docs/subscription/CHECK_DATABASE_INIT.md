# 检查数据库初始化

## 问题

环境变量已设置，但订阅系统仍显示未启用。可能是数据库未初始化。

## 诊断步骤

在服务器上执行：

```bash
cd /opt/beatsync && \
echo "=== 1. 检查数据库文件是否存在 ===" && \
ls -la /opt/beatsync/data/subscription.db 2>/dev/null || echo "❌ 数据库文件不存在" && \
echo "" && \
echo "=== 2. 检查数据库是否已初始化 ===" && \
python3 << 'PYTHON_CHECK'
import sys
sys.path.insert(0, '/opt/beatsync/web_service/backend')

from subscription_db import get_db_path, init_database
import sqlite3

db_path = get_db_path()
print(f"数据库路径: {db_path}")

if db_path.exists():
    print(f"✅ 数据库文件存在")
    # 检查表是否存在
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print(f"✅ 数据库表: {[t[0] for t in tables]}")
    conn.close()
else:
    print("❌ 数据库文件不存在，需要初始化")
    print("正在初始化数据库...")
    try:
        init_database()
        print("✅ 数据库初始化成功")
    except Exception as e:
        print(f"❌ 数据库初始化失败: {e}")
        import traceback
        traceback.print_exc()
PYTHON_CHECK
echo "" && \
echo "=== 3. 测试订阅服务状态 ===" && \
python3 << 'PYTHON_TEST'
import os
import sys
sys.path.insert(0, '/opt/beatsync/web_service/backend')

# 设置环境变量（模拟 systemd）
os.environ["SUBSCRIPTION_ENABLED"] = "true"

from subscription_service import is_subscription_enabled, SUBSCRIPTION_ENABLED
print(f"SUBSCRIPTION_ENABLED = {SUBSCRIPTION_ENABLED}")
print(f"is_subscription_enabled() = {is_subscription_enabled()}")

# 检查数据库路径
from subscription_db import get_db_path
db_path = get_db_path()
print(f"数据库路径: {db_path}")
print(f"数据库路径存在: {db_path is not None}")
PYTHON_TEST
```

---

**请执行上述命令，检查数据库状态！** 🔍


# 检查数据库初始化

## 问题

环境变量已设置，但订阅系统仍显示未启用。可能是数据库未初始化。

## 诊断步骤

在服务器上执行：

```bash
cd /opt/beatsync && \
echo "=== 1. 检查数据库文件是否存在 ===" && \
ls -la /opt/beatsync/data/subscription.db 2>/dev/null || echo "❌ 数据库文件不存在" && \
echo "" && \
echo "=== 2. 检查数据库是否已初始化 ===" && \
python3 << 'PYTHON_CHECK'
import sys
sys.path.insert(0, '/opt/beatsync/web_service/backend')

from subscription_db import get_db_path, init_database
import sqlite3

db_path = get_db_path()
print(f"数据库路径: {db_path}")

if db_path.exists():
    print(f"✅ 数据库文件存在")
    # 检查表是否存在
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print(f"✅ 数据库表: {[t[0] for t in tables]}")
    conn.close()
else:
    print("❌ 数据库文件不存在，需要初始化")
    print("正在初始化数据库...")
    try:
        init_database()
        print("✅ 数据库初始化成功")
    except Exception as e:
        print(f"❌ 数据库初始化失败: {e}")
        import traceback
        traceback.print_exc()
PYTHON_CHECK
echo "" && \
echo "=== 3. 测试订阅服务状态 ===" && \
python3 << 'PYTHON_TEST'
import os
import sys
sys.path.insert(0, '/opt/beatsync/web_service/backend')

# 设置环境变量（模拟 systemd）
os.environ["SUBSCRIPTION_ENABLED"] = "true"

from subscription_service import is_subscription_enabled, SUBSCRIPTION_ENABLED
print(f"SUBSCRIPTION_ENABLED = {SUBSCRIPTION_ENABLED}")
print(f"is_subscription_enabled() = {is_subscription_enabled()}")

# 检查数据库路径
from subscription_db import get_db_path
db_path = get_db_path()
print(f"数据库路径: {db_path}")
print(f"数据库路径存在: {db_path is not None}")
PYTHON_TEST
```

---

**请执行上述命令，检查数据库状态！** 🔍


# 检查数据库初始化

## 问题

环境变量已设置，但订阅系统仍显示未启用。可能是数据库未初始化。

## 诊断步骤

在服务器上执行：

```bash
cd /opt/beatsync && \
echo "=== 1. 检查数据库文件是否存在 ===" && \
ls -la /opt/beatsync/data/subscription.db 2>/dev/null || echo "❌ 数据库文件不存在" && \
echo "" && \
echo "=== 2. 检查数据库是否已初始化 ===" && \
python3 << 'PYTHON_CHECK'
import sys
sys.path.insert(0, '/opt/beatsync/web_service/backend')

from subscription_db import get_db_path, init_database
import sqlite3

db_path = get_db_path()
print(f"数据库路径: {db_path}")

if db_path.exists():
    print(f"✅ 数据库文件存在")
    # 检查表是否存在
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print(f"✅ 数据库表: {[t[0] for t in tables]}")
    conn.close()
else:
    print("❌ 数据库文件不存在，需要初始化")
    print("正在初始化数据库...")
    try:
        init_database()
        print("✅ 数据库初始化成功")
    except Exception as e:
        print(f"❌ 数据库初始化失败: {e}")
        import traceback
        traceback.print_exc()
PYTHON_CHECK
echo "" && \
echo "=== 3. 测试订阅服务状态 ===" && \
python3 << 'PYTHON_TEST'
import os
import sys
sys.path.insert(0, '/opt/beatsync/web_service/backend')

# 设置环境变量（模拟 systemd）
os.environ["SUBSCRIPTION_ENABLED"] = "true"

from subscription_service import is_subscription_enabled, SUBSCRIPTION_ENABLED
print(f"SUBSCRIPTION_ENABLED = {SUBSCRIPTION_ENABLED}")
print(f"is_subscription_enabled() = {is_subscription_enabled()}")

# 检查数据库路径
from subscription_db import get_db_path
db_path = get_db_path()
print(f"数据库路径: {db_path}")
print(f"数据库路径存在: {db_path is not None}")
PYTHON_TEST
```

---

**请执行上述命令，检查数据库状态！** 🔍













