# 🚀 完整部署指南

## 系统信息
- **服务器**: Debian 12
- **端口**: 7773 (Web服务), 80/443 (Nginx)
- **GitHub**: https://github.com/cupid532/image-bed

---

## 📋 第一步：卸载旧版本（如果有）

如果您之前安装过图床系统，请先卸载：

```bash
# 方案A：使用卸载脚本（推荐）
cd /path/to/old/image-bed
chmod +x uninstall.sh
sudo ./uninstall.sh

# 方案B：手动卸载
# 1. 停止并删除容器
docker stop image_bed image_bed_nginx 2>/dev/null || true
docker rm image_bed image_bed_nginx 2>/dev/null || true

# 2. 删除镜像
docker rmi image-bed-web nginx:alpine 2>/dev/null || true

# 3. 删除网络
docker network rm image_bed_network 2>/dev/null || true

# 4. 备份数据（重要！）
sudo tar -czf ~/image_bed_backup_$(date +%Y%m%d).tar.gz /data/image_bed

# 5. 删除数据目录（可选，建议先备份）
sudo rm -rf /data/image_bed

# 6. 清理cron任务
crontab -e
# 删除包含 cleanup_expired_images 的行

# 7. 清理日志
sudo rm -f /var/log/image_bed_*.log
```

---

## 📦 第二步：安装新版本

### 1. SSH连接到服务器

```bash
ssh user@your-server-ip
```

### 2. 克隆项目

```bash
# 进入工作目录
cd ~

# 克隆项目
git clone https://github.com/cupid532/image-bed.git
cd image-bed

# 查看最新版本
git log --oneline -5
```

### 3. 配置环境变量

```bash
# 复制配置文件
cp .env.example .env

# 编辑配置
nano .env
```

**重要配置项：**

```bash
# ============================================
# 安全设置（必须修改！）
# ============================================
SECRET_KEY=$(openssl rand -hex 32)
API_TOKEN=$(openssl rand -hex 16)

# ============================================
# 域名配置
# ============================================
# 如果使用域名：
ALLOWED_HOSTS=your-domain.com,www.your-domain.com,localhost,127.0.0.1

# 如果使用IP：
ALLOWED_HOSTS=your-server-ip,localhost,127.0.0.1

# ============================================
# 认证设置
# ============================================
REQUIRE_AUTH=False              # 使用用户系统，不需要API Token
ALLOW_GUEST_UPLOAD=True         # 允许游客上传（24小时后删除）

# ============================================
# 域名设置（可选）
# ============================================
SITE_DOMAIN=your-domain.com              # 主站域名
IMAGE_DOMAIN=img.your-domain.com         # 图片CDN域名（可选）

# 如果使用IP，留空：
SITE_DOMAIN=
IMAGE_DOMAIN=

# ============================================
# HTTPS设置
# ============================================
FORCE_HTTPS=False               # 如果使用IP，设为False
                                # 如果使用域名+SSL，设为True

# ============================================
# 存储设置
# ============================================
MEDIA_ROOT=/data/images
MAX_UPLOAD_SIZE=10485760        # 10MB

# ============================================
# 图片处理
# ============================================
ENABLE_IMAGE_COMPRESSION=True
COMPRESSION_QUALITY=85
MAX_IMAGE_DIMENSION=4096
```

### 4. 运行部署脚本

```bash
# 添加执行权限
chmod +x deploy.sh setup_cron.sh uninstall.sh

# 运行部署脚本
sudo ./deploy.sh
```

部署脚本会自动：
- ✅ 安装 Docker 和 Docker Compose（如果需要）
- ✅ 创建数据目录 `/data/image_bed`
- ✅ 构建Docker镜像
- ✅ 启动容器
- ✅ 初始化数据库
- ✅ 收集静态文件

### 5. 配置定时清理任务

```bash
# 设置自动清理过期图片的定时任务
sudo ./setup_cron.sh
```

### 6. 验证部署

```bash
# 检查容器状态
docker compose ps

# 应该看到：
# NAME                COMMAND              SERVICE   STATUS
# image_bed           "gunicorn..."       web       Up
# image_bed_nginx     "nginx..."          nginx     Up

# 查看日志
docker compose logs -f

# 按 Ctrl+C 退出

# 测试端口
curl http://localhost
```

### 7. 配置防火墙

```bash
# Debian/Ubuntu
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw reload

# 或者 iptables
sudo iptables -A INPUT -p tcp --dport 80 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 443 -j ACCEPT
sudo iptables-save
```

---

## 🌐 第三步：访问和测试

### 访问网站

打开浏览器，访问：
- **使用IP**: `http://your-server-ip`
- **使用域名**: `http://your-domain.com`

### 功能测试清单

- [ ] 首页正常加载
- [ ] 游客模式提示显示
- [ ] 以游客身份上传图片成功
- [ ] 复制链接并访问图片
- [ ] 点击"注册"，注册新账户
- [ ] 登录成功后上传图片
- [ ] 访问个人中心，查看统计
- [ ] 测试退出登录
- [ ] 查看图片库

---

## 🔧 第四步：高级配置（可选）

### 配置SSL证书（使用域名）

```bash
# 1. 安装Certbot
sudo apt update
sudo apt install certbot -y

# 2. 停止nginx（临时）
docker compose stop nginx

# 3. 获取证书
sudo certbot certonly --standalone -d your-domain.com -d www.your-domain.com

# 4. 复制证书
sudo mkdir -p /data/image_bed/certbot
sudo cp -r /etc/letsencrypt/* /data/image_bed/certbot/

# 5. 修改nginx配置（如果需要）
# 编辑 nginx/conf.d/default.conf，添加SSL配置

# 6. 更新.env
nano .env
# 修改：FORCE_HTTPS=True

# 7. 重启服务
docker compose up -d

# 8. 测试HTTPS
curl https://your-domain.com
```

### 配置独立图片域名

```bash
# 1. 在DNS添加记录
# img.your-domain.com -> your-server-ip

# 2. 修改.env
nano .env
# 添加：
# SITE_DOMAIN=www.your-domain.com
# IMAGE_DOMAIN=img.your-domain.com

# 3. 重启服务
docker compose restart

# 4. 测试
# 上传图片后，URL应该使用 img.your-domain.com
```

### 创建管理员账户

```bash
# 进入容器
docker compose exec web python manage.py createsuperuser

# 按提示输入：
# Email: admin@example.com
# Password: (输入密码)
# Password (again): (再次输入)

# 访问管理后台
# http://your-domain.com/admin/
```

---

## 📊 管理和维护

### 查看日志

```bash
# 实时查看所有日志
docker compose logs -f

# 查看web服务日志
docker compose logs -f web

# 查看nginx日志
docker compose logs -f nginx

# 查看清理任务日志
tail -f /var/log/image_bed_cleanup.log
```

### 手动清理过期图片

```bash
# 查看会删除什么（不实际删除）
docker compose exec web python manage.py cleanup_expired_images --dry-run

# 实际执行清理
docker compose exec web python manage.py cleanup_expired_images
```

### 重启服务

```bash
# 重启所有服务
docker compose restart

# 重启特定服务
docker compose restart web
docker compose restart nginx

# 完全停止并重新启动
docker compose down
docker compose up -d
```

### 更新系统

```bash
# 1. 备份数据
sudo tar -czf ~/image_bed_backup_$(date +%Y%m%d).tar.gz /data/image_bed

# 2. 拉取最新代码
cd ~/image-bed
git pull origin main

# 3. 重新构建
docker compose down
docker compose build
docker compose up -d

# 4. 运行数据库迁移
docker compose exec web python manage.py migrate

# 5. 收集静态文件
docker compose exec web python manage.py collectstatic --noinput
```

### 备份数据

```bash
# 创建备份脚本（已在安装时创建）
cat /usr/local/bin/backup_imagebed.sh

# 手动备份
sudo /usr/local/bin/backup_imagebed.sh

# 查看备份
ls -lh /backup/image_bed/

# 恢复备份
sudo tar -xzf /backup/image_bed/image_bed_YYYYMMDD_HHMMSS.tar.gz -C /
docker compose restart
```

---

## 🐛 故障排查

### 无法访问网站

```bash
# 1. 检查容器状态
docker compose ps

# 2. 检查端口
sudo netstat -tulpn | grep -E '80|443|7773'

# 3. 检查防火墙
sudo ufw status

# 4. 查看nginx日志
docker compose logs nginx | tail -50

# 5. 测试nginx配置
docker compose exec nginx nginx -t
```

### 上传失败

```bash
# 1. 检查目录权限
ls -la /data/image_bed/images/
sudo chmod -R 755 /data/image_bed/images/

# 2. 检查磁盘空间
df -h /data

# 3. 查看web日志
docker compose logs web | grep ERROR

# 4. 检查环境变量
docker compose exec web env | grep MEDIA
```

### 数据库错误

```bash
# 1. 检查数据库文件
ls -la /data/image_bed/db/

# 2. 运行迁移
docker compose exec web python manage.py migrate

# 3. 检查数据库
docker compose exec web python manage.py dbshell
# 输入：.tables
# 输入：.quit
```

### 定时清理不工作

```bash
# 1. 检查cron任务
crontab -l | grep cleanup

# 2. 手动运行测试
docker compose exec web python manage.py cleanup_expired_images --dry-run

# 3. 查看日志
tail -f /var/log/image_bed_cleanup.log

# 4. 重新配置
sudo ./setup_cron.sh
```

---

## 📞 获取帮助

- **GitHub Issues**: https://github.com/cupid532/image-bed/issues
- **文档**:
  - [新功能说明](README_NEW_FEATURES.md)
  - [迁移指南](MIGRATION_GUIDE.md)
  - [快速部署](QUICKSTART_V2.md)

---

## ⚙️ 常用命令速查

```bash
# 启动服务
docker compose up -d

# 停止服务
docker compose down

# 重启服务
docker compose restart

# 查看日志
docker compose logs -f

# 进入容器
docker compose exec web bash

# 查看容器状态
docker compose ps

# 更新代码
git pull origin main && docker compose restart

# 备份数据
sudo tar -czf ~/backup.tar.gz /data/image_bed

# 清理过期图片
docker compose exec web python manage.py cleanup_expired_images
```

---

**部署完成后，请访问网站测试所有功能！** 🎉
