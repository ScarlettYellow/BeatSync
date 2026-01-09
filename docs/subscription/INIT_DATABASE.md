# 初始化订阅系统数据库

## 问题

环境变量已设置，但数据库文件不存在，导致 `is_subscription_enabled()` 返回 `False`。

## 解决方案

初始化数据库。

## 在服务器上执行：

```bash
cd /opt/beatsync && \
echo "=== 1. 创建数据目录 ===" && \
sudo mkdir -p /opt/beatsync/data && \
echo "✅ 目录已创建" && \
echo "" && \
echo "=== 2. 初始化数据库 ===" && \
cd web_service/backend && \
python3 << 'PYTHON_INIT'
import sys
import os
sys.path.insert(0, '/opt/beatsync/web_service/backend')

# 设置环境变量
os.environ["SUBSCRIPTION_ENABLED"] = "true"

from subscription_db import init_database, get_db_path

print("正在初始化数据库...")
try:
    init_database()
    db_path = get_db_path()
    print(f"✅ 数据库初始化成功")
    print(f"数据库路径: {db_path}")
    
    # 验证数据库文件
    if db_path.exists():
        print(f"✅ 数据库文件已创建")
        import sqlite3
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f"✅ 数据库表: {[t[0] for t in tables]}")
        conn.close()
    else:
        print("❌ 数据库文件未创建")
except Exception as e:
    print(f"❌ 数据库初始化失败: {e}")
    import traceback
    traceback.print_exc()
PYTHON_INIT
echo "" && \
echo "=== 3. 验证订阅服务状态 ===" && \
python3 << 'PYTHON_TEST'
import sys
import os
sys.path.insert(0, '/opt/beatsync/web_service/backend')

os.environ["SUBSCRIPTION_ENABLED"] = "true"

from subscription_service import is_subscription_enabled, SUBSCRIPTION_ENABLED
from subscription_db import get_db_path

print(f"SUBSCRIPTION_ENABLED = {SUBSCRIPTION_ENABLED}")
db_path = get_db_path()
print(f"数据库路径: {db_path}")
print(f"数据库路径存在: {db_path is not None}")
print(f"is_subscription_enabled() = {is_subscription_enabled()}")
PYTHON_TEST
echo "" && \
echo "=== 4. 重启服务 ===" && \
sudo systemctl restart beatsync && sleep 3 && echo "✅ 服务已重启" && \
echo "" && \
echo "=== 5. 测试端点 ===" && \
curl -s http://127.0.0.1:8000/api/subscription/products | python3 -m json.tool | head -50
```

---

**请执行上述命令，初始化数据库！** 🚀


# 初始化订阅系统数据库

## 问题

环境变量已设置，但数据库文件不存在，导致 `is_subscription_enabled()` 返回 `False`。

## 解决方案

初始化数据库。

## 在服务器上执行：

```bash
cd /opt/beatsync && \
echo "=== 1. 创建数据目录 ===" && \
sudo mkdir -p /opt/beatsync/data && \
echo "✅ 目录已创建" && \
echo "" && \
echo "=== 2. 初始化数据库 ===" && \
cd web_service/backend && \
python3 << 'PYTHON_INIT'
import sys
import os
sys.path.insert(0, '/opt/beatsync/web_service/backend')

# 设置环境变量
os.environ["SUBSCRIPTION_ENABLED"] = "true"

from subscription_db import init_database, get_db_path

print("正在初始化数据库...")
try:
    init_database()
    db_path = get_db_path()
    print(f"✅ 数据库初始化成功")
    print(f"数据库路径: {db_path}")
    
    # 验证数据库文件
    if db_path.exists():
        print(f"✅ 数据库文件已创建")
        import sqlite3
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f"✅ 数据库表: {[t[0] for t in tables]}")
        conn.close()
    else:
        print("❌ 数据库文件未创建")
except Exception as e:
    print(f"❌ 数据库初始化失败: {e}")
    import traceback
    traceback.print_exc()
PYTHON_INIT
echo "" && \
echo "=== 3. 验证订阅服务状态 ===" && \
python3 << 'PYTHON_TEST'
import sys
import os
sys.path.insert(0, '/opt/beatsync/web_service/backend')

os.environ["SUBSCRIPTION_ENABLED"] = "true"

from subscription_service import is_subscription_enabled, SUBSCRIPTION_ENABLED
from subscription_db import get_db_path

print(f"SUBSCRIPTION_ENABLED = {SUBSCRIPTION_ENABLED}")
db_path = get_db_path()
print(f"数据库路径: {db_path}")
print(f"数据库路径存在: {db_path is not None}")
print(f"is_subscription_enabled() = {is_subscription_enabled()}")
PYTHON_TEST
echo "" && \
echo "=== 4. 重启服务 ===" && \
sudo systemctl restart beatsync && sleep 3 && echo "✅ 服务已重启" && \
echo "" && \
echo "=== 5. 测试端点 ===" && \
curl -s http://127.0.0.1:8000/api/subscription/products | python3 -m json.tool | head -50
```

---

**请执行上述命令，初始化数据库！** 🚀


# 初始化订阅系统数据库

## 问题

环境变量已设置，但数据库文件不存在，导致 `is_subscription_enabled()` 返回 `False`。

## 解决方案

初始化数据库。

## 在服务器上执行：

```bash
cd /opt/beatsync && \
echo "=== 1. 创建数据目录 ===" && \
sudo mkdir -p /opt/beatsync/data && \
echo "✅ 目录已创建" && \
echo "" && \
echo "=== 2. 初始化数据库 ===" && \
cd web_service/backend && \
python3 << 'PYTHON_INIT'
import sys
import os
sys.path.insert(0, '/opt/beatsync/web_service/backend')

# 设置环境变量
os.environ["SUBSCRIPTION_ENABLED"] = "true"

from subscription_db import init_database, get_db_path

print("正在初始化数据库...")
try:
    init_database()
    db_path = get_db_path()
    print(f"✅ 数据库初始化成功")
    print(f"数据库路径: {db_path}")
    
    # 验证数据库文件
    if db_path.exists():
        print(f"✅ 数据库文件已创建")
        import sqlite3
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f"✅ 数据库表: {[t[0] for t in tables]}")
        conn.close()
    else:
        print("❌ 数据库文件未创建")
except Exception as e:
    print(f"❌ 数据库初始化失败: {e}")
    import traceback
    traceback.print_exc()
PYTHON_INIT
echo "" && \
echo "=== 3. 验证订阅服务状态 ===" && \
python3 << 'PYTHON_TEST'
import sys
import os
sys.path.insert(0, '/opt/beatsync/web_service/backend')

os.environ["SUBSCRIPTION_ENABLED"] = "true"

from subscription_service import is_subscription_enabled, SUBSCRIPTION_ENABLED
from subscription_db import get_db_path

print(f"SUBSCRIPTION_ENABLED = {SUBSCRIPTION_ENABLED}")
db_path = get_db_path()
print(f"数据库路径: {db_path}")
print(f"数据库路径存在: {db_path is not None}")
print(f"is_subscription_enabled() = {is_subscription_enabled()}")
PYTHON_TEST
echo "" && \
echo "=== 4. 重启服务 ===" && \
sudo systemctl restart beatsync && sleep 3 && echo "✅ 服务已重启" && \
echo "" && \
echo "=== 5. 测试端点 ===" && \
curl -s http://127.0.0.1:8000/api/subscription/products | python3 -m json.tool | head -50
```

---

**请执行上述命令，初始化数据库！** 🚀













