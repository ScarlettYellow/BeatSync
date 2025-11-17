# 自动化Git版本管理指南

## 一、自动化机制说明

### 1.1 已实现的自动化功能

1. **Pre-commit Hook** (`.git/hooks/pre-commit`)
   - 自动检测核心文件改动
   - 提示用户检查提交信息
   - 不阻止提交，仅提供提醒

2. **Post-commit Hook** (`.git/hooks/post-commit`)
   - 可选：自动推送到远程仓库
   - 自动推送新标签
   - 可通过配置启用/禁用

3. **自动提交脚本** (`auto_commit.sh`)
   - 自动检测文件改动类型
   - 智能生成提交信息
   - 交互式确认后提交

### 1.2 自动化时机

**自动触发**：
- Pre-commit: 每次 `git commit` 前
- Post-commit: 每次 `git commit` 后（如果启用）

**手动触发**：
- `./auto_commit.sh` - 检测改动并自动提交

## 二、使用方法

### 2.1 快速自动提交（推荐）

```bash
# 方式1：使用完整命令
./auto_commit.sh

# 方式2：使用快捷方式（如果已创建）
./ac
```

**流程**：
1. 自动检测改动类型（核心文件/文档/测试等）
2. 显示改动摘要
3. 询问是否提交
4. 自动生成提交信息
5. 创建提交
6. 询问是否推送（如果未启用自动推送）

### 2.2 手动提交（重要改动）

```bash
# 使用重要改动存档脚本
./git_commit_important.sh "类型: 描述" "详细说明..."
```

### 2.3 配置自动推送

```bash
# 启用自动推送（每次提交后自动推送到GitHub）
git config beatsync.auto-push true

# 禁用自动推送（需要手动推送）
git config beatsync.auto-push false

# 查看当前配置
git config --get beatsync.auto-push
```

## 三、自动化工作流

### 3.1 日常开发流程

```bash
# 1. 修改代码
# ... 编辑文件 ...

# 2. 自动提交
./ac

# 3. 如果启用了自动推送，代码会自动推送到GitHub
# 如果未启用，手动推送：
git push
```

### 3.2 重要改动流程

```bash
# 1. 修改代码
# ... 编辑文件 ...

# 2. 使用重要改动脚本（更详细的提交信息）
./git_commit_important.sh "feat: 新功能" "实现了XXX功能..."

# 3. 如果启用了自动推送，会自动推送
# 如果未启用，手动推送：
git push
```

## 四、自动化检测规则

### 4.1 改动类型识别

**核心程序**：
- `beatsync_fine_cut_modular.py`
- `beatsync_badcase_fix_trim_v2.py`
- `beatsync_parallel_processor.py`

**工具模块**：
- `beatsync_utils.py`

**文档**：
- `*.md` 文件
- `README.md`
- `PROJECT_*.md`
- `*_GUIDE.md`

**测试**：
- `test_*.py`
- `*_test.py`
- `regression_test.py`

### 4.2 提交类型映射

- 核心程序改动 → `feat: 核心功能改动`
- 工具模块改动 → `refactor: 工具模块更新`
- 文档改动 → `docs: 文档更新`
- 测试改动 → `test: 测试相关改动`
- 其他改动 → `chore: 其他改动`

## 五、配置选项

### 5.1 自动推送配置

```bash
# 启用（推荐用于重要项目）
git config beatsync.auto-push true

# 禁用（默认，更安全）
git config beatsync.auto-push false
```

**建议**：
- **启用自动推送**：如果希望每次提交后自动备份到GitHub
- **禁用自动推送**：如果希望手动控制推送时机（更安全）

### 5.2 自定义Hooks

如果需要自定义hooks行为，编辑：
- `.git/hooks/pre-commit` - 提交前检查
- `.git/hooks/post-commit` - 提交后操作

## 六、最佳实践

### 6.1 何时使用自动提交

✅ **适合使用自动提交**：
- 日常小改动
- 文档更新
- 代码格式调整
- 测试用例添加

⚠️ **建议手动提交**：
- 重要功能改动
- 性能优化
- 异常处理增强
- 需要详细说明的改动

### 6.2 提交频率

- **重要功能完成时**：立即提交（手动或自动）
- **测试通过后**：提交稳定版本
- **每日工作结束**：提交当日改动

### 6.3 推送策略

- **启用自动推送**：适合单人开发，希望自动备份
- **禁用自动推送**：适合需要审查或多人协作

## 七、故障排除

### 7.1 Hooks不执行

```bash
# 检查hooks权限
ls -la .git/hooks/

# 重新设置权限
chmod +x .git/hooks/pre-commit
chmod +x .git/hooks/post-commit
```

### 7.2 自动推送失败

```bash
# 检查远程仓库配置
git remote -v

# 检查SSH连接
ssh -T git@github.com

# 手动推送
git push
```

### 7.3 自动提交脚本不工作

```bash
# 检查脚本权限
ls -la auto_commit.sh

# 重新设置权限
chmod +x auto_commit.sh

# 检查Git仓库
git status
```

## 八、当前配置状态

运行以下命令查看当前配置：

```bash
# 查看自动推送配置
git config --get beatsync.auto-push

# 查看远程仓库
git remote -v

# 查看hooks状态
ls -la .git/hooks/ | grep -E "pre-commit|post-commit"
```

## 九、快速参考

```bash
# 自动提交
./ac 或 ./auto_commit.sh

# 重要改动提交
./git_commit_important.sh "类型: 描述"

# 手动推送
git push

# 配置自动推送
git config beatsync.auto-push true   # 启用
git config beatsync.auto-push false  # 禁用

# 查看配置
git config --get beatsync.auto-push
```

## 十、总结

✅ **已实现**：
- Pre-commit检查（提醒）
- Post-commit自动推送（可选）
- 自动提交脚本（智能检测）

✅ **优势**：
- 减少手动操作
- 自动生成提交信息
- 可选自动推送

⚠️ **注意**：
- 自动推送默认禁用（更安全）
- 重要改动建议手动提交
- 提交前检查改动内容

