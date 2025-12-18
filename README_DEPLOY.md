# 图床系统部署文档

## 项目概述

这是一个基于 Django 的图床系统，支持图片上传、管理、压缩和认证功能。

### 主要特性

- 📤 **多图上传**: 支持拖拽、粘贴、批量上传
- 🔐 **Token 认证**: API Token 认证保护上传接口
- 🗜️ **图片压缩**: 自动压缩图片，节省存储空间
- 📊 **图片管理**: 查看、删除、统计浏览量
- 🎨 **美观界面**: 现代化 UI 设计
- 🔄 **去重机制**: 基于文件哈希自动去重
- 🚀 **高性能**: Nginx + Gunicorn + Docker 部署

---

## 系统要求

- **操作系统**: Debian 12 (或其他 Linux 发行版)
- **Docker**: 20.10+
- **Docker Compose**: 2.0+
- **域名**: tc.bluse.me (已解析到服务器)

---

## 快速开始

### 1. 安装 Docker 和 Docker Compose

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装 Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 安装 Docker Compose
sudo apt install docker-compose-plugin -y

# 将当前用户加入 docker 组
sudo usermod -aG docker $USER

# 重新登录以使组权限生效
```

### 2. 准备项目文件

```bash
# 上传项目到服务器
cd /root
# 假设你已将项目文件上传到 /root/image_bed

cd image_bed
```

### 3. 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑环境变量
nano .env
```

**重要: 请修改以下配置**

```bash
# 生成安全的 SECRET_KEY
SECRET_KEY=$(python3 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')

# 生成 API Token
API_TOKEN=$(python3 -c 'import secrets; print(secrets.token_hex(32))')

# 修改 .env 文件
SECRET_KEY=<生成的SECRET_KEY>
API_TOKEN=<生成的API_TOKEN>
DEBUG=False
ALLOWED_HOSTS=tc.bluse.me,localhost,127.0.0.1
REQUIRE_AUTH=True
```

### 4. 准备数据目录

```bash
# 确保 /data 目录存在并有正确权限
sudo mkdir -p /data
sudo chown -R 1000:1000 /data
sudo chmod 755 /data
```

### 5. 初始配置 (HTTP Only)

首次部署时，先使用 HTTP 配置，稍后再添加 SSL。

```bash
# 备份原始配置
mv nginx/conf.d/default.conf nginx/conf.d/default-https.conf.bak

# 使用 HTTP 配置
cp nginx/conf.d/default-http-only.conf nginx/conf.d/default.conf
```

### 6. 启动服务

```bash
# 构建并启动容器
docker compose up -d --build

# 查看日志
docker compose logs -f

# 等待服务启动完成
```

### 7. 初始化数据库

```bash
# 进入 web 容器
docker compose exec web bash

# 运行数据库迁移
python manage.py migrate

# 创建超级管理员
python manage.py createsuperuser

# 退出容器
exit
```

### 8. 测试访问

访问 `http://tc.bluse.me`，你应该能看到上传页面。

---

## 配置 SSL 证书

### 使用 Certbot 获取 Let's Encrypt 证书

```bash
# 安装 Certbot
sudo apt install certbot -y

# 停止 Nginx (临时)
docker compose stop nginx

# 获取证书
sudo certbot certonly --standalone -d tc.bluse.me --email your-email@example.com --agree-tos

# 证书将保存在 /etc/letsencrypt/live/tc.bluse.me/

# 复制证书到项目目录
sudo mkdir -p certbot/conf
sudo cp -r /etc/letsencrypt/* certbot/conf/
sudo chown -R $USER:$USER certbot/
```

### 启用 HTTPS 配置

```bash
# 使用 HTTPS 配置
rm nginx/conf.d/default.conf
cp nginx/conf.d/default-https.conf.bak nginx/conf.d/default.conf

# 或者直接恢复原始配置
# mv nginx/conf.d/default-https.conf.bak nginx/conf.d/default.conf

# 重启服务
docker compose restart
```

### 自动续期证书

```bash
# 创建续期脚本
cat > /root/renew-cert.sh << 'EOF'
#!/bin/bash
docker compose -f /root/image_bed/docker-compose.yml stop nginx
certbot renew
cp -r /etc/letsencrypt/* /root/image_bed/certbot/conf/
docker compose -f /root/image_bed/docker-compose.yml start nginx
EOF

chmod +x /root/renew-cert.sh

# 添加到 crontab (每月检查一次)
crontab -e
# 添加以下行
0 3 1 * * /root/renew-cert.sh
```

---

## 创建 API Token

有两种方式创建 API Token:

### 方法 1: 通过 Django Admin

1. 访问 `https://tc.bluse.me/admin/`
2. 使用超级管理员账号登录
3. 进入 "Upload tokens" 页面
4. 点击 "Add Upload Token"
5. 输入名称（如 "我的 Token"）
6. 保存后会自动生成 Token
7. 复制 Token 用于上传

### 方法 2: 通过命令行

```bash
docker compose exec web python manage.py shell

# 在 Python Shell 中执行
from imagehost.models import UploadToken
token = UploadToken.objects.create(name="我的Token", token=UploadToken.generate_token())
print(f"Token: {token.token}")
exit()
```

---

## 使用指南

### Web 界面上传

1. 访问 `https://tc.bluse.me`
2. 输入 API Token
3. 拖拽图片、点击上传或直接粘贴图片
4. 复制生成的图片链接

### API 上传

使用 curl 上传图片:

```bash
curl -X POST https://tc.bluse.me/api/upload/ \
  -H "X-API-Token: YOUR_TOKEN" \
  -F "images=@/path/to/image.jpg"
```

使用 Python 上传:

```python
import requests

url = "https://tc.bluse.me/api/upload/"
headers = {"X-API-Token": "YOUR_TOKEN"}
files = {"images": open("image.jpg", "rb")}

response = requests.post(url, headers=headers, files=files)
print(response.json())
```

### 查看图片库

访问 `https://tc.bluse.me/gallery/?token=YOUR_TOKEN`

---

## 维护命令

### 查看日志

```bash
# 查看所有日志
docker compose logs -f

# 查看特定服务日志
docker compose logs -f web
docker compose logs -f nginx
```

### 重启服务

```bash
# 重启所有服务
docker compose restart

# 重启特定服务
docker compose restart web
docker compose restart nginx
```

### 更新代码

```bash
# 拉取最新代码
git pull  # 如果使用 Git

# 重新构建并启动
docker compose up -d --build
```

### 备份数据

```bash
# 备份数据库
docker compose exec web python manage.py dumpdata > backup.json

# 备份图片
sudo tar -czf /root/image_backup_$(date +%Y%m%d).tar.gz /data

# 备份到远程服务器
rsync -avz /data user@backup-server:/backup/images/
```

### 清理磁盘空间

```bash
# 查看磁盘使用
df -h /data

# 清理 Docker 缓存
docker system prune -a

# 查看数据库大小
du -sh image_bed/db.sqlite3
```

---

## 性能优化

### 1. 调整 Gunicorn Workers

编辑 `Dockerfile` 中的 CMD:

```dockerfile
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", ...]
```

推荐 workers 数量 = (CPU 核心数 × 2) + 1

### 2. 启用 Redis 缓存 (可选)

在 `docker-compose.yml` 中添加 Redis:

```yaml
services:
  redis:
    image: redis:alpine
    restart: unless-stopped
```

### 3. 数据库优化

考虑迁移到 PostgreSQL:

```bash
# 安装 PostgreSQL
pip install psycopg2-binary

# 修改 settings.py 中的 DATABASES 配置
```

---

## 安全建议

1. **使用强密码**: SECRET_KEY 和 API_TOKEN 必须足够复杂
2. **定期更新**: 保持 Docker 镜像和系统更新
3. **限制访问**: 使用防火墙限制不必要的端口访问
4. **监控日志**: 定期检查访问日志，发现异常行为
5. **备份数据**: 定期备份数据库和图片文件
6. **HTTPS Only**: 生产环境必须使用 HTTPS
7. **Rate Limiting**: 考虑添加速率限制防止滥用

---

## 故障排查

### 问题 1: 无法访问网站

```bash
# 检查容器状态
docker compose ps

# 检查端口占用
sudo netstat -tlnp | grep :80
sudo netstat -tlnp | grep :443

# 检查 Nginx 日志
docker compose logs nginx
```

### 问题 2: 上传失败

```bash
# 检查 /data 目录权限
ls -la /data

# 查看应用日志
docker compose logs web

# 检查磁盘空间
df -h
```

### 问题 3: 图片无法显示

```bash
# 检查图片文件是否存在
ls -la /data/

# 检查 Nginx 配置
docker compose exec nginx nginx -t

# 查看 Nginx 错误日志
docker compose logs nginx | grep error
```

### 问题 4: SSL 证书错误

```bash
# 检查证书文件
sudo ls -la /etc/letsencrypt/live/tc.bluse.me/

# 测试证书
openssl s_client -connect tc.bluse.me:443

# 续期证书
sudo certbot renew --dry-run
```

---

## 环境变量说明

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| SECRET_KEY | Django 密钥 | 必须修改 |
| DEBUG | 调试模式 | False |
| ALLOWED_HOSTS | 允许的主机 | tc.bluse.me,localhost |
| API_TOKEN | API Token | 必须设置 |
| REQUIRE_AUTH | 是否需要认证 | True |
| MAX_UPLOAD_SIZE | 最大上传大小(字节) | 10485760 (10MB) |
| ENABLE_IMAGE_COMPRESSION | 启用图片压缩 | True |
| COMPRESSION_QUALITY | 压缩质量(1-100) | 85 |
| MAX_IMAGE_DIMENSION | 最大图片尺寸(像素) | 4096 |

---

## 项目结构

```
image_bed/
├── image_bed/           # Django 项目配置
│   ├── settings.py     # 设置文件
│   ├── urls.py         # URL 路由
│   └── wsgi.py         # WSGI 入口
├── imagehost/          # 图床应用
│   ├── models.py       # 数据模型
│   ├── views.py        # 视图函数
│   ├── urls.py         # URL 路由
│   └── admin.py        # 管理后台
├── templates/          # HTML 模板
│   ├── index.html      # 上传页面
│   └── gallery.html    # 图片库页面
├── nginx/              # Nginx 配置
│   ├── nginx.conf      # 主配置
│   └── conf.d/         # 站点配置
├── Dockerfile          # Docker 镜像
├── docker-compose.yml  # Docker Compose 配置
├── requirements.txt    # Python 依赖
├── manage.py          # Django 管理脚本
└── .env               # 环境变量
```

---

## API 文档

### 上传图片

**Endpoint**: `POST /api/upload/`

**Headers**:
```
X-API-Token: YOUR_TOKEN
```

**Body** (multipart/form-data):
```
images: [file1, file2, ...]
```

**Response**:
```json
{
  "results": [
    {
      "filename": "image.jpg",
      "url": "https://tc.bluse.me/i/20250101/abcd1234.jpg",
      "size": 123.45,
      "dimensions": "1920x1080",
      "duplicate": false
    }
  ],
  "errors": []
}
```

### 列出图片

**Endpoint**: `GET /api/images/?page=1&per_page=20`

**Headers**:
```
X-API-Token: YOUR_TOKEN
```

**Response**:
```json
{
  "images": [...],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 100,
    "pages": 5
  }
}
```

### 删除图片

**Endpoint**: `POST /api/images/{id}/delete/`

**Headers**:
```
X-API-Token: YOUR_TOKEN
```

---

## 常见问题

**Q: 如何修改最大上传大小?**

A: 修改 `.env` 文件中的 `MAX_UPLOAD_SIZE` (单位: 字节)，然后重启服务。

**Q: 如何禁用认证?**

A: 在 `.env` 中设置 `REQUIRE_AUTH=False`，但不推荐在生产环境这样做。

**Q: 如何迁移到新服务器?**

A:
1. 备份 `/data` 目录
2. 备份 `db.sqlite3` 数据库
3. 复制 `.env` 配置文件
4. 在新服务器上重新部署
5. 恢复备份的数据

**Q: 如何自定义域名?**

A: 修改 `.env` 中的 `ALLOWED_HOSTS` 和 `nginx/conf.d/default.conf` 中的 `server_name`。

---

## 联系支持

如有问题，请检查:
1. Docker 日志: `docker compose logs`
2. Nginx 日志: `docker compose logs nginx`
3. Django 日志: `docker compose logs web`

---

## 许可证

MIT License
