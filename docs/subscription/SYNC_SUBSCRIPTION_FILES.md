# 同步订阅系统文件到服务器

## 问题

服务器上缺少订阅系统模块文件：
- `subscription_service.py`
- `subscription_db.py`
- `subscription_receipt_verification.py`
- `payment_service.py`

导致 `SUBSCRIPTION_AVAILABLE = False`，端点返回空列表。

## 解决方案

由于 Git 拉取有网络问题，需要手动同步这些文件。

### 方法 1：使用 scp 从本地复制（推荐）

在**本地**执行：

```bash
# 复制订阅系统文件到服务器
scp web_service/backend/subscription_service.py user@your-server:/opt/beatsync/web_service/backend/
scp web_service/backend/subscription_db.py user@your-server:/opt/beatsync/web_service/backend/
scp web_service/backend/subscription_receipt_verification.py user@your-server:/opt/beatsync/web_service/backend/
scp web_service/backend/payment_service.py user@your-server:/opt/beatsync/web_service/backend/
```

### 方法 2：在服务器上直接创建文件

如果无法使用 scp，可以在服务器上直接创建这些文件。由于文件较大，建议使用方法 1。

---

**请使用方法 1（scp）将文件复制到服务器，然后告诉我！** 📁
