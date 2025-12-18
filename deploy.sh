#!/bin/bash

# 图床系统快速部署脚本
# 用于 Debian 12 系统

set -e

echo "================================"
echo "图床系统快速部署脚本"
echo "================================"
echo ""

# 检查是否为 root 用户
if [ "$EUID" -ne 0 ]; then
    echo "请使用 root 用户或 sudo 运行此脚本"
    exit 1
fi

# 1. 安装 Docker
echo "[1/8] 安装 Docker..."
if ! command -v docker &> /dev/null; then
    apt update
    apt install -y curl
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm get-docker.sh
    echo "Docker 安装完成"
else
    echo "Docker 已安装，跳过"
fi

# 2. 安装 Docker Compose
echo "[2/8] 安装 Docker Compose..."
if ! command -v docker compose &> /dev/null; then
    apt install -y docker-compose-plugin
    echo "Docker Compose 安装完成"
else
    echo "Docker Compose 已安装，跳过"
fi

# 3. 安装 Python3 (用于生成密钥)
echo "[3/8] 安装 Python3..."
apt install -y python3 python3-pip

# 4. 创建数据目录
echo "[4/8] 创建数据目录..."
mkdir -p /data/image_bed/{images,db,certbot,certbot-www}
chmod -R 755 /data/image_bed
echo "数据目录创建完成: /data/image_bed/"

# 5. 配置环境变量
echo "[5/8] 配置环境变量..."
if [ ! -f .env ]; then
    cp .env.example .env

    # 生成 SECRET_KEY
    SECRET_KEY=$(python3 -c "import secrets; print(''.join(secrets.choice('abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)') for i in range(50)))")

    # 生成 API_TOKEN
    API_TOKEN=$(python3 -c "import secrets; print(secrets.token_hex(32))")

    # 更新 .env 文件
    sed -i "s/your-super-secret-key-here-please-change-this/$SECRET_KEY/" .env
    sed -i "s/your-api-token-here/$API_TOKEN/" .env

    echo "环境变量配置完成"
    echo ""
    echo "重要: 你的 API Token 是:"
    echo "======================================"
    echo "$API_TOKEN"
    echo "======================================"
    echo "请妥善保管此 Token，上传图片时需要使用"
    echo ""
else
    echo ".env 文件已存在，跳过"
fi

# 6. 配置 Nginx (HTTP Only for initial setup)
echo "[6/8] 配置 Nginx (HTTP Only)..."
if [ ! -f nginx/conf.d/default.conf ]; then
    if [ -f nginx/conf.d/default-http-only.conf ]; then
        cp nginx/conf.d/default-http-only.conf nginx/conf.d/default.conf
        echo "Nginx 配置完成 (HTTP Only)"
    fi
fi

# 7. 设置文件权限
echo "[7/8] 设置文件权限..."
chmod +x manage.py
chown -R 1000:1000 /data/image_bed

# 8. 启动服务
echo "[8/8] 启动服务..."
docker compose up -d --build

echo ""
echo "================================"
echo "等待服务启动..."
echo "================================"
sleep 10

# 运行数据库迁移
echo "运行数据库迁移..."
docker compose exec -T web python manage.py migrate --noinput

echo ""
echo "================================"
echo "部署完成！"
echo "================================"
echo ""
echo "访问地址: http://YOUR_DOMAIN (请替换为你的域名)"
echo ""
echo "你的 API Token:"
if [ -f .env ]; then
    grep "^API_TOKEN=" .env | cut -d'=' -f2
fi
echo ""
echo "下一步:"
echo "1. 在 .env 文件中设置 ALLOWED_HOSTS 为你的域名"
echo "2. 访问 http://YOUR_DOMAIN 测试上传功能"
echo "3. 按照 README.md 配置 SSL 证书（可选）"
echo "4. 创建管理员账号: docker compose exec web python manage.py createsuperuser"
echo "5. 查看日志: docker compose logs -f"
echo ""
echo "详细文档请查看: README.md"
