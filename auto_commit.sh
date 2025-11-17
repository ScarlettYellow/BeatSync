#!/bin/bash
# 自动提交脚本
# 检测重要文件改动并自动提交

set -e

# 配置
AUTO_COMMIT_ENABLED=true
AUTO_PUSH_ENABLED=false  # 默认不自动推送，避免意外推送

# 检查Git仓库
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo "❌ 错误: 当前目录不是Git仓库"
    exit 1
fi

# 检查是否有改动
if git diff --quiet && git diff --cached --quiet; then
    echo "ℹ️  没有检测到改动"
    exit 0
fi

echo "=========================================="
echo "自动提交检测"
echo "=========================================="
echo ""

# 获取改动的文件
CHANGED_FILES=$(git diff --name-only)
STAGED_FILES=$(git diff --cached --name-only)
ALL_CHANGED="$CHANGED_FILES $STAGED_FILES"

# 检测改动类型
CORE_FILES_CHANGED=false
DOCS_CHANGED=false
TEST_CHANGED=false
UTILS_CHANGED=false

for file in $ALL_CHANGED; do
    case "$file" in
        beatsync_fine_cut_modular.py|beatsync_badcase_fix_trim_v2.py|beatsync_parallel_processor.py)
            CORE_FILES_CHANGED=true
            ;;
        beatsync_utils.py)
            UTILS_CHANGED=true
            ;;
        *.md|README.md|PROJECT_*.md|*_GUIDE.md)
            DOCS_CHANGED=true
            ;;
        test_*.py|*_test.py|regression_test.py)
            TEST_CHANGED=true
            ;;
    esac
done

# 生成提交信息
COMMIT_TYPE=""
COMMIT_MSG=""

if [ "$CORE_FILES_CHANGED" = true ]; then
    COMMIT_TYPE="feat"
    COMMIT_MSG="核心功能改动"
elif [ "$UTILS_CHANGED" = true ]; then
    COMMIT_TYPE="refactor"
    COMMIT_MSG="工具模块更新"
elif [ "$DOCS_CHANGED" = true ]; then
    COMMIT_TYPE="docs"
    COMMIT_MSG="文档更新"
elif [ "$TEST_CHANGED" = true ]; then
    COMMIT_TYPE="test"
    COMMIT_MSG="测试相关改动"
else
    COMMIT_TYPE="chore"
    COMMIT_MSG="其他改动"
fi

# 显示改动摘要
echo "检测到的改动："
if [ "$CORE_FILES_CHANGED" = true ]; then
    echo "  ✅ 核心程序文件"
fi
if [ "$UTILS_CHANGED" = true ]; then
    echo "  ✅ 工具模块"
fi
if [ "$DOCS_CHANGED" = true ]; then
    echo "  ✅ 文档文件"
fi
if [ "$TEST_CHANGED" = true ]; then
    echo "  ✅ 测试文件"
fi

echo ""
echo "改动的文件："
git status --short | head -10
if [ $(git status --short | wc -l) -gt 10 ]; then
    echo "  ... 还有更多文件"
fi

echo ""
read -p "是否自动提交？(y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "已取消"
    exit 0
fi

# 添加所有改动
echo ""
echo "添加改动..."
git add .

# 生成详细提交信息
TIMESTAMP=$(date "+%Y-%m-%d %H:%M:%S")
DETAIL_MSG="自动提交于 $TIMESTAMP

改动文件：
$(git diff --cached --name-only | sed 's/^/  - /')

改动类型：
$(if [ "$CORE_FILES_CHANGED" = true ]; then echo "  - 核心程序"; fi)
$(if [ "$UTILS_CHANGED" = true ]; then echo "  - 工具模块"; fi)
$(if [ "$DOCS_CHANGED" = true ]; then echo "  - 文档"; fi)
$(if [ "$TEST_CHANGED" = true ]; then echo "  - 测试"; fi)"

# 创建提交
echo ""
echo "创建提交..."
git commit -m "$COMMIT_TYPE: $COMMIT_MSG" -m "$DETAIL_MSG"

echo ""
echo "✅ 提交完成！"
echo ""

# 显示提交信息
git log -1 --pretty=format:"提交ID: %h%n日期: %ad%n%n%s%n%n%b" --date=format:"%Y-%m-%d %H:%M:%S"

# 询问是否推送
if [ "$AUTO_PUSH_ENABLED" != "true" ]; then
    echo ""
    read -p "是否推送到远程仓库？(y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo ""
        echo "推送到远程仓库..."
        if git push; then
            echo "✅ 推送成功"
        else
            echo "⚠️  推送失败，请手动推送：git push"
        fi
    fi
fi

echo ""
echo "=========================================="
echo "完成！"
echo "=========================================="

