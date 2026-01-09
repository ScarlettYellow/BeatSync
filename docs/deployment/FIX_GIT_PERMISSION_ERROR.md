# 修复 Git 权限错误

## 问题描述

执行 `git pull` 时出现错误：
```
error: cannot open .git/FETCH_HEAD: Permission denied
```

## 原因

`.git` 目录的所有者是 `root`，但当前用户是 `ubuntu`，导致无法写入 Git 元数据。

## 解决方案

### 方案一：修复 Git 目录权限（推荐）

```bash
# 1. 切换到项目目录
cd /opt/beatsync

# 2. 修复 .git 目录权限
sudo chown -R ubuntu:ubuntu /opt/beatsync/.git

# 3. 再次尝试拉取
git pull origin main

# 4. 如果成功，重启服务
sudo systemctl restart beatsync
```

### 方案二：使用 sudo 执行 Git 命令

```bash
# 1. 切换到项目目录
cd /opt/beatsync

# 2. 使用 sudo 拉取（注意：这会将文件所有者改为 root）
sudo git pull origin main

# 3. 修复文件所有者（如果需要）
sudo chown -R ubuntu:ubuntu /opt/beatsync

# 4. 重启服务
sudo systemctl restart beatsync
```

### 方案三：先处理本地更改，再拉取

如果本地有未提交的更改，需要先处理：

```bash
# 1. 切换到项目目录
cd /opt/beatsync

# 2. 查看当前状态
git status

# 3. 如果有已暂存的更改，先提交或撤销
# 选项 A：提交本地更改
git commit -m "本地更改：更新 main.py"

# 选项 B：撤销已暂存的更改（如果不需要保留）
git reset HEAD web_service/backend/main.py
git checkout -- web_service/backend/main.py

# 4. 修复权限
sudo chown -R ubuntu:ubuntu /opt/beatsync/.git

# 5. 拉取最新代码
git pull origin main

# 6. 如果有冲突，解决冲突后重启服务
sudo systemctl restart beatsync
```

## 完整修复命令（一键执行）

```bash
cd /opt/beatsync && \
sudo chown -R ubuntu:ubuntu /opt/beatsync/.git && \
git reset HEAD web_service/backend/main.py 2>/dev/null || true && \
git checkout -- web_service/backend/main.py 2>/dev/null || true && \
git pull origin main && \
sudo systemctl restart beatsync && \
echo "✅ 修复完成！"
```

## 验证修复

```bash
# 1. 检查 Git 状态
cd /opt/beatsync
git status

# 2. 验证代码已更新
grep -n "用户认证端点（移到条件块外" web_service/backend/main.py

# 3. 测试端点
curl -X POST https://beatsync.site/api/auth/register \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "device_id=test_device_123"
```

## 预防措施

为了避免将来出现权限问题，建议：

```bash
# 设置项目目录的所有者为 ubuntu
sudo chown -R ubuntu:ubuntu /opt/beatsync

# 或者，如果服务以 root 运行，保持 root 所有者
# 但使用 sudo 执行所有 Git 命令
```



