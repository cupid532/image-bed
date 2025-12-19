#!/bin/bash
# 修复部署脚本

echo "=== 服务器上执行以下命令 ==="
cat << 'REMOTE_COMMANDS'
cd ~/image-bed

# 1. 清理旧容器和镜像
docker compose down
docker system prune -f

# 2. 确保 .env 配置正确
cat > .env << 'ENVEOF'
SECRET_KEY=django-insecure-change-this-key-$(openssl rand -hex 32)
DEBUG=False
ALLOWED_HOSTS=23.147.204.72,tc.090798.xyz,localhost,127.0.0.1
REQUIRE_AUTH=True
FORCE_HTTPS=False
MEDIA_ROOT=/data/images
MAX_UPLOAD_SIZE=10485760
ENABLE_IMAGE_COMPRESSION=True
COMPRESSION_QUALITY=85
MAX_IMAGE_DIMENSION=4096
ENVEOF

# 3. 重新构建（不使用缓存）
docker compose build --no-cache

# 4. 启动容器
docker compose up -d

# 5. 等待启动
sleep 5

# 6. 运行迁移
docker exec image_bed python manage.py migrate

# 7. 收集静态文件
docker exec image_bed python manage.py collectstatic --noinput

# 8. 检查状态
docker ps | grep image_bed
docker logs image_bed --tail 20

echo ""
echo "=== 部署完成！现在访问 http://23.147.204.72:8000/admin/ 测试 ==="
REMOTE_COMMANDS
