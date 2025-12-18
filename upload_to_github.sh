#!/bin/bash

# GitHub 上传脚本
# 用于将项目推送到 GitHub

set -e

echo "================================"
echo "GitHub 上传脚本"
echo "================================"
echo ""

# 检查是否在正确的目录
if [ ! -f "docker-compose.yml" ]; then
    echo "错误: 请在项目根目录运行此脚本"
    exit 1
fi

# 检查 Git 是否初始化
if [ ! -d ".git" ]; then
    echo "错误: Git 仓库未初始化"
    echo "请先运行: git init"
    exit 1
fi

# 检查是否有提交
if ! git rev-parse HEAD &>/dev/null; then
    echo "错误: 没有提交记录"
    echo "请先创建提交"
    exit 1
fi

# 检查远程仓库
REMOTE_URL=$(git remote get-url origin 2>/dev/null || echo "")

if [ -z "$REMOTE_URL" ]; then
    echo "添加远程仓库..."
    echo ""
    echo "请在 GitHub 创建仓库后，输入仓库地址："
    echo "示例: https://github.com/cupid532/image-bed.git"
    read -p "仓库地址: " REPO_URL

    if [ -z "$REPO_URL" ]; then
        echo "错误: 仓库地址不能为空"
        exit 1
    fi

    git remote add origin "$REPO_URL"
    echo "远程仓库已添加: $REPO_URL"
else
    echo "远程仓库: $REMOTE_URL"
fi

echo ""
echo "准备推送到 GitHub..."
echo ""

# 检查是否需要优化 README
if [ -f "README_GITHUB.md" ]; then
    read -p "是否使用 GitHub 优化版 README? (y/N): " USE_GITHUB_README

    if [ "$USE_GITHUB_README" = "y" ] || [ "$USE_GITHUB_README" = "Y" ]; then
        echo "优化 README..."
        mv README.md README_DEPLOY.md
        mv README_GITHUB.md README.md
        git add README.md README_DEPLOY.md
        git commit -m "docs: use GitHub-optimized README" || true
    fi
fi

echo ""
echo "开始推送..."
echo ""

# 推送到 GitHub
if git push -u origin main; then
    echo ""
    echo "================================"
    echo "✅ 推送成功！"
    echo "================================"
    echo ""
    echo "仓库地址: $REMOTE_URL"
    echo ""
    echo "下一步:"
    echo "1. 访问你的仓库查看代码"
    echo "2. 添加仓库描述和标签"
    echo "3. 创建 Release (可选)"
    echo ""
else
    echo ""
    echo "================================"
    echo "❌ 推送失败"
    echo "================================"
    echo ""
    echo "可能的原因:"
    echo "1. 需要认证 - 请使用 Personal Access Token"
    echo "2. 仓库不存在 - 请先在 GitHub 创建仓库"
    echo "3. 分支名称不匹配 - 尝试 'git push -u origin master'"
    echo ""
    echo "获取 Token: https://github.com/settings/tokens"
    echo "详细指引: 查看 GITHUB_UPLOAD_GUIDE.md"
    exit 1
fi
