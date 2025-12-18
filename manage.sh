#!/bin/bash

# 图床系统管理脚本

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 显示菜单
show_menu() {
    echo ""
    echo "================================"
    echo "图床系统管理脚本"
    echo "================================"
    echo "1. 启动服务"
    echo "2. 停止服务"
    echo "3. 重启服务"
    echo "4. 查看状态"
    echo "5. 查看日志"
    echo "6. 生成 API Token"
    echo "7. 创建管理员账号"
    echo "8. 备份数据"
    echo "9. 查看磁盘使用"
    echo "10. 更新服务"
    echo "11. 清理 Docker 缓存"
    echo "12. 配置 SSL 证书"
    echo "0. 退出"
    echo "================================"
}

# 启动服务
start_service() {
    echo -e "${GREEN}正在启动服务...${NC}"
    docker compose up -d
    echo -e "${GREEN}服务已启动${NC}"
}

# 停止服务
stop_service() {
    echo -e "${YELLOW}正在停止服务...${NC}"
    docker compose down
    echo -e "${GREEN}服务已停止${NC}"
}

# 重启服务
restart_service() {
    echo -e "${YELLOW}正在重启服务...${NC}"
    docker compose restart
    echo -e "${GREEN}服务已重启${NC}"
}

# 查看状态
show_status() {
    echo -e "${GREEN}服务状态:${NC}"
    docker compose ps
    echo ""
    echo -e "${GREEN}资源使用:${NC}"
    docker stats --no-stream
}

# 查看日志
show_logs() {
    echo "选择要查看的日志:"
    echo "1. 所有服务"
    echo "2. Web 应用"
    echo "3. Nginx"
    read -p "请选择 [1-3]: " log_choice

    case $log_choice in
        1) docker compose logs -f ;;
        2) docker compose logs -f web ;;
        3) docker compose logs -f nginx ;;
        *) echo -e "${RED}无效选择${NC}" ;;
    esac
}

# 生成 Token
generate_token() {
    echo -e "${GREEN}正在生成 API Token...${NC}"
    read -p "请输入 Token 名称: " token_name

    if [ -z "$token_name" ]; then
        token_name="Token-$(date +%Y%m%d-%H%M%S)"
    fi

    docker compose exec -T web python manage.py shell << EOF
from imagehost.models import UploadToken
token = UploadToken.objects.create(
    name="$token_name",
    token=UploadToken.generate_token()
)
print("\n" + "="*50)
print(f"Token 名称: {token.name}")
print(f"Token 值: {token.token}")
print("="*50 + "\n")
print("请妥善保管此 Token！")
EOF
}

# 创建管理员
create_admin() {
    echo -e "${GREEN}创建管理员账号${NC}"
    docker compose exec web python manage.py createsuperuser
}

# 备份数据
backup_data() {
    echo -e "${GREEN}正在备份数据...${NC}"

    BACKUP_DIR="$SCRIPT_DIR/backups"
    mkdir -p "$BACKUP_DIR"

    BACKUP_FILE="$BACKUP_DIR/backup_$(date +%Y%m%d_%H%M%S).tar.gz"

    # 备份数据库和图片
    tar -czf "$BACKUP_FILE" db.sqlite3 2>/dev/null || true

    # 备份 /data 目录（如果存在）
    if [ -d "/data" ]; then
        echo "备份 /data 目录..."
        sudo tar -czf "$BACKUP_DIR/data_$(date +%Y%m%d_%H%M%S).tar.gz" /data
    fi

    echo -e "${GREEN}备份完成: $BACKUP_FILE${NC}"

    # 显示备份大小
    du -h "$BACKUP_FILE"
}

# 查看磁盘使用
show_disk_usage() {
    echo -e "${GREEN}磁盘使用情况:${NC}"
    echo ""
    echo "系统磁盘:"
    df -h | grep -E "^Filesystem|/$"
    echo ""
    echo "/data 目录:"
    du -sh /data 2>/dev/null || echo "无法访问 /data 目录"
    echo ""
    echo "数据库大小:"
    du -sh db.sqlite3 2>/dev/null || echo "数据库文件不存在"
    echo ""
    echo "Docker 占用:"
    docker system df
}

# 更新服务
update_service() {
    echo -e "${YELLOW}正在更新服务...${NC}"

    # 拉取最新代码（如果使用 Git）
    if [ -d ".git" ]; then
        echo "拉取最新代码..."
        git pull
    fi

    # 重新构建并启动
    echo "重新构建镜像..."
    docker compose build --no-cache

    echo "重启服务..."
    docker compose up -d

    echo -e "${GREEN}更新完成${NC}"
}

# 清理 Docker 缓存
clean_docker() {
    echo -e "${YELLOW}清理 Docker 缓存...${NC}"

    echo "清理前磁盘使用:"
    docker system df
    echo ""

    read -p "确定要清理吗？这将删除未使用的镜像和容器 [y/N]: " confirm

    if [ "$confirm" = "y" ] || [ "$confirm" = "Y" ]; then
        docker system prune -a -f
        echo ""
        echo "清理后磁盘使用:"
        docker system df
        echo -e "${GREEN}清理完成${NC}"
    else
        echo "已取消"
    fi
}

# 配置 SSL
setup_ssl() {
    echo -e "${GREEN}配置 SSL 证书${NC}"
    echo ""
    echo "1. 获取新证书"
    echo "2. 续期现有证书"
    echo "3. 启用 HTTPS 配置"
    read -p "请选择 [1-3]: " ssl_choice

    case $ssl_choice in
        1)
            read -p "请输入域名: " domain
            read -p "请输入邮箱: " email

            echo "停止 Nginx..."
            docker compose stop nginx

            echo "获取证书..."
            sudo certbot certonly --standalone -d "$domain" --email "$email" --agree-tos

            echo "复制证书..."
            sudo mkdir -p certbot/conf
            sudo cp -r /etc/letsencrypt/* certbot/conf/
            sudo chown -R $(id -u):$(id -g) certbot/

            echo "启动 Nginx..."
            docker compose start nginx

            echo -e "${GREEN}证书获取完成${NC}"
            ;;
        2)
            echo "续期证书..."
            docker compose stop nginx
            sudo certbot renew
            sudo cp -r /etc/letsencrypt/* certbot/conf/
            docker compose start nginx
            echo -e "${GREEN}证书续期完成${NC}"
            ;;
        3)
            if [ -f "nginx/conf.d/default-https.conf.bak" ]; then
                echo "启用 HTTPS 配置..."
                rm -f nginx/conf.d/default.conf
                cp nginx/conf.d/default-https.conf.bak nginx/conf.d/default.conf
                docker compose restart nginx
                echo -e "${GREEN}HTTPS 配置已启用${NC}"
            else
                echo -e "${RED}找不到 HTTPS 配置文件${NC}"
            fi
            ;;
        *)
            echo -e "${RED}无效选择${NC}"
            ;;
    esac
}

# 主循环
main() {
    while true; do
        show_menu
        read -p "请选择操作 [0-12]: " choice

        case $choice in
            1) start_service ;;
            2) stop_service ;;
            3) restart_service ;;
            4) show_status ;;
            5) show_logs ;;
            6) generate_token ;;
            7) create_admin ;;
            8) backup_data ;;
            9) show_disk_usage ;;
            10) update_service ;;
            11) clean_docker ;;
            12) setup_ssl ;;
            0)
                echo "退出"
                exit 0
                ;;
            *)
                echo -e "${RED}无效选择，请重试${NC}"
                ;;
        esac

        echo ""
        read -p "按 Enter 继续..."
    done
}

# 运行主程序
main
