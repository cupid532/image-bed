# 图床系统 - 快速开始

一个功能完整的图床系统，专为 tc.bluse.me 设计。

## 特性

✅ **拖拽上传** - 支持拖拽文件到页面上传
✅ **粘贴上传** - 直接 Ctrl+V 粘贴截图上传
✅ **批量上传** - 一次上传多张图片
✅ **Token 认证** - API Token 保护上传接口
✅ **自动压缩** - 自动压缩图片节省空间
✅ **去重机制** - 基于哈希值自动去重
✅ **图片管理** - 查看、删除、统计浏览量
✅ **美观界面** - 现代化 UI 设计
✅ **Docker 部署** - 一键部署，开箱即用

## 一键部署

在你的 Debian 12 服务器上执行:

```bash
# 1. 上传项目文件到服务器
scp -r image_bed root@your-server:/root/

# 2. SSH 登录服务器
ssh root@your-server

# 3. 进入项目目录
cd /root/image_bed

# 4. 运行部署脚本
chmod +x deploy.sh
./deploy.sh
```

部署脚本会自动:
- 安装 Docker 和 Docker Compose
- 配置环境变量和生成安全密钥
- 创建数据目录 /data
- 启动所有服务
- 运行数据库迁移

## 手动部署

如果你想手动部署，请按照以下步骤:

### 1. 环境准备

```bash
# 安装 Docker
curl -fsSL https://get.docker.com | sh

# 安装 Docker Compose
apt install docker-compose-plugin -y
```

### 2. 配置环境变量

```bash
cp .env.example .env
nano .env  # 编辑配置文件

# 必须修改:
# - SECRET_KEY: Django 密钥
# - API_TOKEN: 上传 Token
```

### 3. 准备数据目录

```bash
mkdir -p /data
chmod 755 /data
```

### 4. 启动服务

```bash
# 首次部署使用 HTTP 配置
cp nginx/conf.d/default-http-only.conf nginx/conf.d/default.conf

# 启动
docker compose up -d --build

# 初始化数据库
docker compose exec web python manage.py migrate

# 创建管理员
docker compose exec web python manage.py createsuperuser
```

### 5. 访问测试

访问 `http://tc.bluse.me`，输入你的 API Token 即可开始上传。

## 配置 SSL (推荐)

```bash
# 1. 安装 Certbot
apt install certbot -y

# 2. 获取证书
certbot certonly --standalone -d tc.bluse.me

# 3. 复制证书
mkdir -p certbot/conf
cp -r /etc/letsencrypt/* certbot/conf/

# 4. 启用 HTTPS 配置
rm nginx/conf.d/default.conf
mv nginx/conf.d/default-https.conf.bak nginx/conf.d/default.conf

# 5. 重启服务
docker compose restart
```

## 使用方法

### Web 界面上传

1. 访问 `https://tc.bluse.me`
2. 输入 API Token
3. 拖拽图片 / 点击上传 / 粘贴图片
4. 复制生成的链接

### API 上传

```bash
curl -X POST https://tc.bluse.me/api/upload/ \
  -H "X-API-Token: YOUR_TOKEN" \
  -F "images=@image.jpg"
```

### 查看图片库

访问 `https://tc.bluse.me/gallery/?token=YOUR_TOKEN`

### 管理后台

访问 `https://tc.bluse.me/admin/` 使用超级管理员账号登录。

## 常用命令

```bash
# 查看日志
docker compose logs -f

# 重启服务
docker compose restart

# 停止服务
docker compose down

# 备份数据
tar -czf backup.tar.gz /data db.sqlite3

# 创建 API Token
docker compose exec web python manage.py shell
>>> from imagehost.models import UploadToken
>>> token = UploadToken.objects.create(name="My Token", token=UploadToken.generate_token())
>>> print(token.token)
```

## 目录结构

```
image_bed/
├── image_bed/          # Django 项目配置
├── imagehost/          # 图床应用
├── templates/          # HTML 模板
├── nginx/              # Nginx 配置
├── Dockerfile          # Docker 镜像
├── docker-compose.yml  # Docker Compose
├── requirements.txt    # Python 依赖
├── deploy.sh          # 一键部署脚本
└── README.md          # 详细文档
```

## 技术栈

- **后端**: Django 4.2 + Gunicorn
- **前端**: 原生 HTML/CSS/JavaScript
- **Web 服务器**: Nginx
- **容器化**: Docker + Docker Compose
- **图片处理**: Pillow
- **数据库**: SQLite (可迁移到 PostgreSQL)

## 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| SECRET_KEY | Django 密钥 | 必须修改 |
| API_TOKEN | 上传 Token | 必须设置 |
| DEBUG | 调试模式 | False |
| REQUIRE_AUTH | 需要认证 | True |
| MAX_UPLOAD_SIZE | 最大上传(字节) | 10MB |
| COMPRESSION_QUALITY | 压缩质量 | 85 |

## 安全建议

1. ✅ 使用强密码 (SECRET_KEY, API_TOKEN)
2. ✅ 启用 HTTPS
3. ✅ 定期备份数据
4. ✅ 更新 Docker 镜像
5. ✅ 监控访问日志
6. ✅ 限制 Token 访问

## 故障排查

**无法访问?**
```bash
docker compose ps              # 检查容器状态
docker compose logs nginx      # 查看 Nginx 日志
docker compose logs web        # 查看应用日志
```

**上传失败?**
```bash
ls -la /data                   # 检查目录权限
df -h                          # 检查磁盘空间
docker compose logs web        # 查看错误日志
```

**图片不显示?**
```bash
ls -la /data/                  # 检查文件是否存在
docker compose exec nginx nginx -t  # 检查 Nginx 配置
```

## 文档

完整文档请查看 [README.md](README.md)

## 许可证

MIT License

---

**需要帮助?** 查看日志: `docker compose logs -f`
