#!/bin/bash
# 图床系统完全卸载脚本

set -e

echo "=========================================="
echo "   图床系统卸载工具"
echo "=========================================="
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 确认卸载
echo -e "${YELLOW}警告：此操作将完全删除图床系统和所有数据！${NC}"
echo -e "${YELLOW}包括：${NC}"
echo "  - Docker容器和镜像"
echo "  - 所有上传的图片"
echo "  - 数据库文件"
echo "  - 定时清理任务"
echo ""
read -p "确认要继续吗？(输入 YES 继续): " CONFIRM

if [ "$CONFIRM" != "YES" ]; then
    echo "已取消卸载"
    exit 0
fi

echo ""
echo "开始卸载..."
echo ""

# 1. 停止并删除Docker容器
echo "1️⃣  停止并删除Docker容器..."
if [ -f "docker-compose.yml" ]; then
    docker compose down -v 2>/dev/null || true
    echo -e "${GREEN}✓ Docker容器已停止并删除${NC}"
else
    # 如果没有docker-compose.yml，手动停止容器
    docker stop image_bed image_bed_nginx 2>/dev/null || true
    docker rm image_bed image_bed_nginx 2>/dev/null || true
    echo -e "${GREEN}✓ Docker容器已手动停止并删除${NC}"
fi

# 2. 删除Docker镜像
echo ""
echo "2️⃣  删除Docker镜像..."
docker rmi image-bed-web image-bed-nginx nginx:alpine 2>/dev/null || true
echo -e "${GREEN}✓ Docker镜像已删除${NC}"

# 3. 删除Docker网络
echo ""
echo "3️⃣  删除Docker网络..."
docker network rm image_bed_network 2>/dev/null || true
echo -e "${GREEN}✓ Docker网络已删除${NC}"

# 4. 删除数据目录
echo ""
echo "4️⃣  删除数据目录..."
read -p "是否删除 /data/image_bed 目录？(y/N): " DELETE_DATA
if [[ "$DELETE_DATA" =~ ^[Yy]$ ]]; then
    sudo rm -rf /data/image_bed
    echo -e "${GREEN}✓ 数据目录已删除${NC}"
else
    echo -e "${YELLOW}⚠ 数据目录已保留在 /data/image_bed${NC}"
    echo -e "${YELLOW}  如需手动删除：sudo rm -rf /data/image_bed${NC}"
fi

# 5. 删除cron任务
echo ""
echo "5️⃣  删除定时清理任务..."
CRON_FILE="/tmp/imagebed_cron_backup"
crontab -l > "$CRON_FILE" 2>/dev/null || touch "$CRON_FILE"

if grep -q "cleanup_expired_images" "$CRON_FILE"; then
    grep -v "cleanup_expired_images" "$CRON_FILE" > "${CRON_FILE}.tmp" || true
    crontab "${CRON_FILE}.tmp" 2>/dev/null || true
    rm -f "${CRON_FILE}.tmp"
    echo -e "${GREEN}✓ 定时清理任务已删除${NC}"
else
    echo -e "${YELLOW}⚠ 未找到定时清理任务${NC}"
fi
rm -f "$CRON_FILE"

# 6. 删除项目目录（可选）
echo ""
echo "6️⃣  删除项目代码..."
CURRENT_DIR=$(pwd)
if [[ "$CURRENT_DIR" == *"image-bed"* ]] || [[ "$CURRENT_DIR" == *"image_bed"* ]]; then
    echo -e "${YELLOW}当前位于项目目录：$CURRENT_DIR${NC}"
    read -p "是否删除项目代码目录？(y/N): " DELETE_CODE
    if [[ "$DELETE_CODE" =~ ^[Yy]$ ]]; then
        cd ..
        rm -rf "$CURRENT_DIR"
        echo -e "${GREEN}✓ 项目代码已删除${NC}"
    else
        echo -e "${YELLOW}⚠ 项目代码已保留${NC}"
    fi
else
    echo -e "${YELLOW}⚠ 未在项目目录中，跳过代码删除${NC}"
fi

# 7. 清理日志文件
echo ""
echo "7️⃣  清理日志文件..."
sudo rm -f /var/log/image_bed_cleanup.log
sudo rm -f /var/log/image_bed_backup.log
echo -e "${GREEN}✓ 日志文件已清理${NC}"

# 8. 清理Docker系统（可选）
echo ""
read -p "是否清理Docker未使用的资源？(y/N): " CLEAN_DOCKER
if [[ "$CLEAN_DOCKER" =~ ^[Yy]$ ]]; then
    docker system prune -f
    echo -e "${GREEN}✓ Docker未使用资源已清理${NC}"
fi

echo ""
echo "=========================================="
echo -e "${GREEN}✅ 卸载完成！${NC}"
echo "=========================================="
echo ""
echo "已删除："
echo "  ✓ Docker容器和镜像"
echo "  ✓ Docker网络"
echo "  ✓ 定时清理任务"
echo "  ✓ 日志文件"
echo ""
if [[ "$DELETE_DATA" =~ ^[Yy]$ ]]; then
    echo "  ✓ 数据目录 /data/image_bed"
else
    echo -e "  ${YELLOW}⚠ 数据目录已保留：/data/image_bed${NC}"
fi
echo ""
echo "如需重新安装，请访问："
echo "https://github.com/cupid532/image-bed"
echo ""
