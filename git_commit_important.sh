#!/bin/bash
# 重要改动存档脚本
# 使用方法: ./git_commit_important.sh "类型: 简短描述" "详细说明..."

if [ $# -lt 1 ]; then
    echo "用法: $0 \"类型: 简短描述\" [\"详细说明...\"]"
    echo ""
    echo "类型前缀："
    echo "  feat:  - 新功能"
    echo "  fix:   - 修复bug"
    echo "  perf:  - 性能优化"
    echo "  refactor: - 代码重构"
    echo "  docs:  - 文档更新"
    echo "  test:  - 测试相关"
    echo ""
    echo "示例:"
    echo "  $0 \"perf: 优化视频处理速度\" \"实现了新的编码策略，速度提升2倍\""
    exit 1
fi

SHORT_MSG="$1"
DETAIL_MSG="${2:-}"

echo "=========================================="
echo "重要改动存档"
echo "=========================================="
echo ""

# 1. 显示当前状态
echo "1. 检查当前状态..."
git status --short
echo ""

# 2. 确认是否继续
read -p "是否继续提交？(y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "已取消"
    exit 1
fi

# 3. 添加所有改动
echo ""
echo "2. 添加所有改动..."
git add .
echo ""

# 4. 创建提交
echo "3. 创建提交..."
if [ -n "$DETAIL_MSG" ]; then
    git commit -m "$SHORT_MSG" -m "$DETAIL_MSG"
else
    git commit -m "$SHORT_MSG"
fi

# 5. 显示提交信息
echo ""
echo "4. 提交完成！"
echo ""
git log -1 --pretty=format:"提交ID: %h%n作者: %an%n日期: %ad%n%n%s%n%n%b" --date=format:"%Y-%m-%d %H:%M:%S"
echo ""

# 6. 询问是否创建标签
read -p "是否创建版本标签？(y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    read -p "请输入版本号（如 v1.4.0）: " VERSION
    if [ -n "$VERSION" ]; then
        read -p "请输入版本说明: " VERSION_MSG
        if [ -n "$VERSION_MSG" ]; then
            git tag -a "$VERSION" -m "$VERSION_MSG"
            echo "标签 $VERSION 已创建"
        else
            git tag -a "$VERSION" -m "$SHORT_MSG"
            echo "标签 $VERSION 已创建（使用提交信息）"
        fi
    fi
fi

echo ""
echo "=========================================="
echo "完成！"
echo "=========================================="

