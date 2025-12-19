# 🚀 快速部署指南 - 版本 2.0

这是一份完整的部署指南，帮助您快速部署升级后的图床系统（包含用户认证和游客模式功能）。

---

## 📋 系统要求

- **操作系统**: Debian 12 / Ubuntu 20.04+ / 其他 Linux 发行版
- **Docker**: 20.10+
- **Docker Compose**: 2.0+
- **域名**（可选）: 如果需要使用域名访问

---

## ⚡ 快速部署（5分钟）

### 步骤 1: 准备服务器

```bash
# SSH 连接到您的 Debian 12 服务器
ssh user@your-server-ip

# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装 Git（如果没有）
sudo apt install git -y
```

### 步骤 2: 下载代码

```bash
# 进入工作目录
cd /home/your-username  # 或其他目录

# 克隆项目
git clone https://github.com/cupid532/image-bed.git
cd image-bed

# 如果使用Token认证
# git clone https://YOUR_TOKEN@github.com/cupid532/image-bed.git
```

### 步骤 3: 配置环境变量

```bash
# 复制配置文件
cp .env.example .env

# 编辑配置
nano .env
```

**重要配置项：**

```bash
# 安全密钥（必须修改！）
SECRET_KEY=your-super-secret-key-change-this-now-$(openssl rand -hex 32)
API_TOKEN=your-api-token-$(openssl rand -hex 16)

# 域名配置（根据实际情况修改）
ALLOWED_HOSTS=your-domain.com,your-server-ip,localhost,127.0.0.1

# 认证设置
REQUIRE_AUTH=False          # API上传不需要Token
ALLOW_GUEST_UPLOAD=True     # 允许游客上传（24小时后删除）

# 域名设置（可选，用于生成链接）
SITE_DOMAIN=your-domain.com              # 主站域名
IMAGE_DOMAIN=img.your-domain.com         # 图片CDN域名（可选）

# HTTPS设置
FORCE_HTTPS=False          # 如果使用IP访问，设为False；使用域名+SSL，设为True

# 存储设置
MEDIA_ROOT=/data/images
MAX_UPLOAD_SIZE=10485760   # 10MB
```

### 步骤 4: 一键部署

```bash
# 给脚本执行权限
chmod +x deploy.sh setup_cron.sh

# 运行部署脚本（会自动安装Docker、创建目录、启动服务）
sudo ./deploy.sh
```

部署脚本会自动：
- ✅ 安装 Docker 和 Docker Compose
- ✅ 创建必要的数据目录
- ✅ 生成安全密钥
- ✅ 构建并启动容器
- ✅ 初始化数据库
- ✅ 收集静态文件

### 步骤 5: 配置定时清理任务

```bash
# 设置自动清理过期图片的定时任务
sudo ./setup_cron.sh
```

这会创建一个每小时运行一次的 cron 任务，自动删除游客上传的过期图片。

### 步骤 6: 验证部署

```bash
# 检查容器状态
docker compose ps

# 应该看到类似输出：
# NAME                COMMAND                  SERVICE   STATUS
# image-bed-web-1     "gunicorn..."           web       Up
# image-bed-nginx-1   "nginx -g 'daemon..."   nginx     Up

# 查看日志
docker compose logs -f

# 按 Ctrl+C 退出日志查看
```

### 步骤 7: 访问网站

打开浏览器访问：
- **使用IP**: `http://your-server-ip`
- **使用域名**: `http://your-domain.com`

您应该能看到登录界面和主页。

---

## 🎉 开始使用

### 作为游客使用

1. 访问首页
2. 直接拖拽/上传图片
3. 复制生成的链接
4. ⚠️ 注意：游客上传的图片24小时后自动删除

### 注册账户（推荐）

1. 点击页面右上角的"注册"按钮
2. 输入邮箱和密码（至少8位，包含字母和数字）
3. 注册后自动登录
4. 上传的图片将**永久保存**

### 使用功能

- **上传图片**: 拖拽、粘贴(Ctrl+V)、点击选择
- **查看图片库**: 点击"图片库"查看所有图片
- **个人中心**: 查看统计信息和上传历史
- **复制链接**: 点击"复制链接"按钮一键复制

---

## 🔧 高级配置

### 配置SSL证书（使用域名）

```bash
# 安装 Certbot
sudo apt install certbot -y

# 获取证书
sudo certbot certonly --standalone -d your-domain.com

# 复制证书到项目目录
sudo mkdir -p /data/image_bed/certbot
sudo cp -r /etc/letsencrypt/* /data/image_bed/certbot/

# 更新 .env 文件
nano .env
# 修改: FORCE_HTTPS=True

# 重启服务
docker compose restart
```

### 配置独立图片域名

如果您想用独立域名或CDN提供图片：

```bash
# 编辑 .env
nano .env

# 添加/修改
SITE_DOMAIN=www.example.com      # 主站域名
IMAGE_DOMAIN=img.example.com     # 图片域名

# 重启服务
docker compose restart
```

然后在DNS中添加CNAME记录：
```
img.example.com  ->  www.example.com
```

### 创建管理员账户

```bash
# 进入容器
docker compose exec web python manage.py createsuperuser

# 按提示输入邮箱和密码

# 访问管理后台
# http://your-domain.com/admin/
```

---

## 📊 监控和维护

### 查看日志

```bash
# 实时查看日志
docker compose logs -f

# 查看特定服务日志
docker compose logs web
docker compose logs nginx

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

### 备份数据

```bash
# 创建备份脚本
cat > /usr/local/bin/backup_imagebed.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR=/backup/image_bed
mkdir -p $BACKUP_DIR
tar -czf $BACKUP_DIR/image_bed_$DATE.tar.gz /data/image_bed
# 保留最近7天的备份
find $BACKUP_DIR -name "image_bed_*.tar.gz" -mtime +7 -delete
echo "Backup completed: image_bed_$DATE.tar.gz"
EOF

# 添加执行权限
chmod +x /usr/local/bin/backup_imagebed.sh

# 添加到crontab（每天凌晨2点备份）
(crontab -l 2>/dev/null; echo "0 2 * * * /usr/local/bin/backup_imagebed.sh >> /var/log/image_bed_backup.log 2>&1") | crontab -
```

### 更新系统

```bash
# 进入项目目录
cd /path/to/image-bed

# 拉取最新代码
git pull

# 重新构建并启动
docker compose down
docker compose build
docker compose up -d

# 运行数据库迁移（如果有）
docker compose exec web python manage.py migrate
```

---

## ⚠️ 故障排查

### 问题 1: 无法访问网站

**检查防火墙：**
```bash
# Debian/Ubuntu
sudo ufw status
sudo ufw allow 80
sudo ufw allow 443

# 或使用 iptables
sudo iptables -L
```

**检查容器状态：**
```bash
docker compose ps
docker compose logs nginx
```

### 问题 2: 上传失败

**检查目录权限：**
```bash
ls -la /data/image_bed/images/
sudo chmod -R 755 /data/image_bed/images/
```

**查看错误日志：**
```bash
docker compose logs web | grep ERROR
```

### 问题 3: 定时清理不工作

**检查cron任务：**
```bash
crontab -l | grep cleanup
```

**手动测试：**
```bash
docker compose exec web python manage.py cleanup_expired_images --dry-run
```

**查看清理日志：**
```bash
tail -f /var/log/image_bed_cleanup.log
```

### 问题 4: 数据库迁移失败

**查看迁移状态：**
```bash
docker compose exec web python manage.py showmigrations
```

**重新运行迁移：**
```bash
docker compose exec web python manage.py migrate --fake-initial
docker compose exec web python manage.py migrate
```

---

## 📝 配置文件示例

### 生产环境配置 (.env)

```bash
# 安全设置
SECRET_KEY=production-secret-key-change-this
API_TOKEN=production-api-token-change-this

# 应用设置
DEBUG=False
ALLOWED_HOSTS=example.com,www.example.com
REQUIRE_AUTH=False
ALLOW_GUEST_UPLOAD=True

# 域名设置
SITE_DOMAIN=www.example.com
IMAGE_DOMAIN=img.example.com

# HTTPS
FORCE_HTTPS=True

# 存储
MEDIA_ROOT=/data/images
MAX_UPLOAD_SIZE=10485760

# 图片处理
ENABLE_IMAGE_COMPRESSION=True
COMPRESSION_QUALITY=85
MAX_IMAGE_DIMENSION=4096
```

### 测试环境配置 (.env)

```bash
# 安全设置
SECRET_KEY=test-secret-key
API_TOKEN=test-api-token

# 应用设置
DEBUG=True  # 开启调试
ALLOWED_HOSTS=192.168.1.100,localhost,127.0.0.1
REQUIRE_AUTH=False
ALLOW_GUEST_UPLOAD=True

# 域名设置（留空使用IP）
SITE_DOMAIN=
IMAGE_DOMAIN=

# HTTPS
FORCE_HTTPS=False  # 测试环境不使用HTTPS

# 存储
MEDIA_ROOT=/data/images
MAX_UPLOAD_SIZE=10485760
```

---

## 🔗 相关文档

- [新功能说明](README_NEW_FEATURES.md) - 了解所有新功能
- [数据库迁移指南](MIGRATION_GUIDE.md) - 从旧版本升级
- [配置说明](CONFIGURATION.md) - 详细配置说明
- [API文档](API_DOCUMENTATION.md) - API使用说明

---

## 💡 使用技巧

### 1. 快速上传快捷键

- 在任何页面按 `Ctrl+V` 粘贴上传截图
- 拖拽文件到上传区域
- 支持批量选择多个文件

### 2. 链接格式

系统生成的图片链接格式：
```
https://your-domain.com/i/20250101/abc123.jpg
                          ^         ^
                          日期      唯一ID
```

### 3. 性能优化

- 使用独立的图片域名（IMAGE_DOMAIN）
- 启用图片压缩（ENABLE_IMAGE_COMPRESSION=True）
- 配置CDN加速图片访问

### 4. 安全建议

- 定期更换 SECRET_KEY 和 API_TOKEN
- 使用强密码策略
- 启用 HTTPS
- 定期备份数据
- 监控系统日志

---

## 📞 获取帮助

遇到问题？

1. **查看日志**: `docker compose logs -f`
2. **查看文档**: 阅读相关文档文件
3. **GitHub Issues**: https://github.com/cupid532/image-bed/issues
4. **检查配置**: 确认 `.env` 文件配置正确

---

## 🎯 下一步

部署成功后，您可以：

1. ✅ 注册一个管理员账户
2. ✅ 测试图片上传功能
3. ✅ 配置域名和SSL证书
4. ✅ 设置定时备份
5. ✅ 邀请其他用户使用

祝您使用愉快！🎉

---

**Made with ❤️ by [cupid532](https://github.com/cupid532)**
