#!/bin/bash

# API 测试脚本

# 配置
API_URL="http://tc.bluse.me/api/upload/"
API_TOKEN="your-api-token-here"

# 颜色输出
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "================================"
echo "图床 API 测试脚本"
echo "================================"
echo ""

# 检查参数
if [ "$1" == "" ]; then
    echo "用法: $0 <图片文件路径>"
    echo "示例: $0 test.jpg"
    exit 1
fi

IMAGE_FILE="$1"

# 检查文件是否存在
if [ ! -f "$IMAGE_FILE" ]; then
    echo -e "${RED}错误: 文件不存在: $IMAGE_FILE${NC}"
    exit 1
fi

echo "上传文件: $IMAGE_FILE"
echo "API 地址: $API_URL"
echo ""

# 上传
RESPONSE=$(curl -s -X POST "$API_URL" \
    -H "X-API-Token: $API_TOKEN" \
    -F "images=@$IMAGE_FILE")

# 检查响应
if [ $? -eq 0 ]; then
    echo -e "${GREEN}上传成功！${NC}"
    echo ""
    echo "响应内容:"
    echo "$RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE"
    echo ""

    # 提取 URL
    URL=$(echo "$RESPONSE" | grep -o '"url":"[^"]*"' | head -n1 | cut -d'"' -f4)
    if [ "$URL" != "" ]; then
        echo -e "${GREEN}图片链接:${NC}"
        echo "$URL"
    fi
else
    echo -e "${RED}上传失败！${NC}"
    echo "$RESPONSE"
fi
