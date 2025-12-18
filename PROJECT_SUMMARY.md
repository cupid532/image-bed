# 图床系统项目总结

## 项目完成情况

✅ **已完成所有功能**

所有核心功能已实现并经过测试，包括:
1. Django 项目结构搭建
2. 图片上传功能（支持拖拽和粘贴）
3. 图片管理功能（查看、删除）
4. Token 认证系统
5. 图片自动压缩
6. 前端页面（现代化 UI）
7. Docker 部署配置
8. Nginx 反向代理配置
9. 完整部署文档

---

## 项目结构

```
image_bed/
├── image_bed/                    # Django 项目配置
│   ├── __init__.py
│   ├── settings.py              # 核心配置文件
│   ├── urls.py                  # 主路由
│   ├── wsgi.py                  # WSGI 入口
│   └── asgi.py                  # ASGI 入口
│
├── imagehost/                   # 图床应用
│   ├── __init__.py
│   ├── models.py                # 数据模型 (Image, UploadToken)
│   ├── views.py                 # 视图函数 (上传、删除、查看)
│   ├── urls.py                  # 路由配置
│   ├── admin.py                 # 管理后台配置
│   └── apps.py                  # 应用配置
│
├── templates/                   # HTML 模板
│   ├── index.html              # 上传页面（拖拽、粘贴）
│   └── gallery.html            # 图片库页面
│
├── nginx/                      # Nginx 配置
│   ├── nginx.conf              # 主配置
│   └── conf.d/
│       ├── default.conf        # HTTPS 配置
│       └── default-http-only.conf  # HTTP 配置
│
├── static/                     # 静态文件目录
├── Dockerfile                  # Docker 镜像配置
├── docker-compose.yml          # Docker Compose 配置
├── requirements.txt            # Python 依赖
├── manage.py                   # Django 管理脚本
├── .env.example               # 环境变量模板
├── .gitignore                 # Git 忽略配置
├── deploy.sh                  # 一键部署脚本
├── test_upload.sh             # API 测试脚本
├── README.md                  # 完整文档
└── QUICKSTART.md              # 快速开始指南
```

---

## 核心功能说明

### 1. 图片上传

**文件**: `imagehost/views.py` - `upload_image()`

功能:
- 支持单张/多张图片上传
- 文件类型验证 (JPEG, PNG, GIF, WebP)
- 文件大小限制 (默认 10MB)
- 基于 SHA256 的去重机制
- 自动图片压缩（可配置）
- Token 认证保护
- 记录上传 IP 和时间

### 2. 图片管理

**文件**: `imagehost/views.py` - `list_images()`, `delete_image()`

功能:
- 分页查看所有图片
- 显示图片信息（尺寸、大小、浏览量）
- 删除图片（文件+数据库记录）
- Token 认证保护

### 3. 图片服务

**文件**: `imagehost/views.py` - `serve_image()`

功能:
- 直接访问图片 URL
- 自动记录浏览量
- 缓存控制（1年）
- Nginx 直接服务（高性能）

### 4. 认证系统

**文件**: `imagehost/models.py` - `UploadToken`, `imagehost/views.py` - `token_required()`

功能:
- Token 生成和验证
- 支持多个 Token
- 记录使用统计
- 可启用/禁用 Token

### 5. 图片压缩

**文件**: `imagehost/models.py` - `Image.compress_image()`

功能:
- 智能压缩（JPEG 质量 85）
- 自动尺寸限制（默认 4096px）
- RGBA → RGB 转换
- 优化存储空间

---

## 数据库模型

### Image 模型

```python
- id: 主键
- image: 图片文件路径
- original_filename: 原始文件名
- file_size: 文件大小（字节）
- file_hash: SHA256 哈希值（用于去重）
- width: 图片宽度
- height: 图片高度
- mime_type: MIME 类型
- upload_ip: 上传者 IP
- created_at: 上传时间
- view_count: 浏览量
```

### UploadToken 模型

```python
- id: 主键
- token: Token 字符串（64位十六进制）
- name: Token 名称/描述
- is_active: 是否激活
- upload_count: 使用次数
- last_used: 最后使用时间
- created_at: 创建时间
```

---

## API 接口

### 1. 上传图片

```
POST /api/upload/
Headers: X-API-Token: <token>
Body: multipart/form-data
  - images: file[]
```

响应:
```json
{
  "results": [
    {
      "filename": "test.jpg",
      "url": "https://tc.bluse.me/i/20250101/abc123.jpg",
      "size": 123.45,
      "dimensions": "1920x1080",
      "duplicate": false
    }
  ],
  "errors": []
}
```

### 2. 列出图片

```
GET /api/images/?page=1&per_page=20
Headers: X-API-Token: <token>
```

### 3. 删除图片

```
POST /api/images/<id>/delete/
Headers: X-API-Token: <token>
```

### 4. 访问图片

```
GET /i/<path>
无需认证，自动记录浏览量
```

---

## 配置说明

### 环境变量 (.env)

```bash
SECRET_KEY=<Django密钥>
API_TOKEN=<上传Token>
DEBUG=False
ALLOWED_HOSTS=tc.bluse.me,localhost
REQUIRE_AUTH=True
MAX_UPLOAD_SIZE=10485760        # 10MB
ENABLE_IMAGE_COMPRESSION=True
COMPRESSION_QUALITY=85
MAX_IMAGE_DIMENSION=4096
```

### Django 配置 (settings.py)

关键配置:
- `MEDIA_ROOT = '/data'` - 图片存储在 /data 目录
- `MEDIA_URL = '/i/'` - 图片访问路径
- 支持中文语言 (zh-hans)
- 时区设置为上海
- 生产环境安全配置

### Nginx 配置

- 反向代理到 Gunicorn (端口 8000)
- 直接服务静态文件和图片（高性能）
- HTTPS 支持（Let's Encrypt）
- Gzip 压缩
- 缓存控制
- 安全头部

---

## 部署步骤

### 方法 1: 一键部署（推荐）

```bash
# 1. 上传项目到服务器
scp -r image_bed root@your-server:/root/

# 2. 运行部署脚本
cd /root/image_bed
chmod +x deploy.sh
./deploy.sh
```

### 方法 2: 手动部署

```bash
# 1. 安装 Docker
curl -fsSL https://get.docker.com | sh

# 2. 配置环境变量
cp .env.example .env
nano .env  # 修改 SECRET_KEY 和 API_TOKEN

# 3. 创建数据目录
mkdir -p /data
chmod 755 /data

# 4. 配置 Nginx（首次使用 HTTP）
cp nginx/conf.d/default-http-only.conf nginx/conf.d/default.conf

# 5. 启动服务
docker compose up -d --build

# 6. 初始化数据库
docker compose exec web python manage.py migrate

# 7. 创建管理员
docker compose exec web python manage.py createsuperuser
```

### SSL 证书配置

```bash
# 1. 获取证书
apt install certbot -y
docker compose stop nginx
certbot certonly --standalone -d tc.bluse.me

# 2. 复制证书
mkdir -p certbot/conf
cp -r /etc/letsencrypt/* certbot/conf/

# 3. 启用 HTTPS 配置
rm nginx/conf.d/default.conf
mv nginx/conf.d/default-https.conf.bak nginx/conf.d/default.conf

# 4. 重启服务
docker compose restart
```

---

## 使用指南

### Web 界面使用

1. **访问首页**: https://tc.bluse.me
2. **输入 Token**: 在输入框输入 API Token
3. **上传图片**:
   - 拖拽图片到上传区域
   - 点击"选择文件"按钮
   - 按 Ctrl+V 粘贴截图
4. **复制链接**: 点击"复制链接"按钮

### API 使用

**命令行上传**:
```bash
curl -X POST https://tc.bluse.me/api/upload/ \
  -H "X-API-Token: YOUR_TOKEN" \
  -F "images=@test.jpg"
```

**Python 上传**:
```python
import requests

url = "https://tc.bluse.me/api/upload/"
headers = {"X-API-Token": "YOUR_TOKEN"}
files = {"images": open("test.jpg", "rb")}
response = requests.post(url, headers=headers, files=files)
print(response.json())
```

### 管理后台使用

1. 访问 https://tc.bluse.me/admin/
2. 使用超级管理员账号登录
3. 可以管理:
   - 上传的图片
   - API Tokens
   - 用户账号

---

## 常用命令

```bash
# 查看日志
docker compose logs -f

# 查看特定服务日志
docker compose logs -f web
docker compose logs -f nginx

# 重启服务
docker compose restart

# 停止服务
docker compose down

# 进入容器
docker compose exec web bash
docker compose exec nginx sh

# 数据库操作
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
docker compose exec web python manage.py shell

# 创建 Token
docker compose exec web python manage.py shell
>>> from imagehost.models import UploadToken
>>> token = UploadToken.objects.create(name="My Token", token=UploadToken.generate_token())
>>> print(token.token)

# 备份数据
tar -czf backup_$(date +%Y%m%d).tar.gz /data db.sqlite3

# 查看容器状态
docker compose ps

# 查看资源使用
docker stats
```

---

## 性能优化建议

### 1. 数据库优化

- 考虑迁移到 PostgreSQL（更高性能）
- 添加数据库索引（已在模型中配置）
- 定期清理旧数据

### 2. 缓存优化

- 添加 Redis 缓存
- 使用 CDN 加速图片访问
- 启用浏览器缓存（已配置）

### 3. 服务器优化

- 调整 Gunicorn workers 数量
- 增加服务器内存
- 使用 SSD 存储

### 4. Nginx 优化

- 启用 HTTP/2（已配置）
- 配置 Gzip 压缩（已配置）
- 调整 worker_connections

---

## 安全建议

1. ✅ **使用强密码**: SECRET_KEY 和 API_TOKEN 必须复杂
2. ✅ **启用 HTTPS**: 使用 Let's Encrypt 免费证书
3. ✅ **定期更新**: 保持 Docker 镜像和系统更新
4. ✅ **限制访问**: 配置防火墙规则
5. ✅ **监控日志**: 定期检查异常访问
6. ✅ **备份数据**: 定期备份数据库和图片
7. ✅ **Token 管理**: 定期轮换 Token
8. ✅ **文件验证**: 严格验证上传文件类型

---

## 故障排查

### 问题 1: 容器无法启动

```bash
# 检查日志
docker compose logs

# 检查端口占用
netstat -tlnp | grep :80
netstat -tlnp | grep :8000

# 重新构建
docker compose down
docker compose up -d --build
```

### 问题 2: 上传失败

```bash
# 检查数据目录权限
ls -la /data
chown -R 1000:1000 /data

# 检查磁盘空间
df -h

# 查看应用日志
docker compose logs web
```

### 问题 3: 图片无法显示

```bash
# 检查文件是否存在
ls -la /data/

# 检查 Nginx 配置
docker compose exec nginx nginx -t

# 重启 Nginx
docker compose restart nginx
```

### 问题 4: SSL 证书问题

```bash
# 检查证书文件
ls -la certbot/conf/live/tc.bluse.me/

# 测试证书
openssl s_client -connect tc.bluse.me:443

# 续期证书
certbot renew
```

---

## 技术栈详情

- **Python**: 3.11
- **Django**: 4.2
- **Gunicorn**: 21.2
- **Nginx**: Alpine
- **Pillow**: 10.0 (图片处理)
- **Docker**: 最新版
- **操作系统**: Debian 12

---

## 项目特点

1. **易于部署**: 一键部署脚本，5分钟上线
2. **高性能**: Nginx + Gunicorn + Docker 组合
3. **安全可靠**: Token 认证 + HTTPS + 文件验证
4. **用户友好**: 现代化 UI + 拖拽上传 + 粘贴上传
5. **功能完整**: 上传、管理、压缩、统计一应俱全
6. **易于维护**: Docker 容器化，日志完善

---

## 后续扩展建议

1. **用户系统**: 多用户支持，每个用户独立配额
2. **图片水印**: 自动添加水印功能
3. **CDN 集成**: 对接七牛云、阿里云 OSS
4. **批量处理**: 图片批量编辑、压缩
5. **API 限流**: 防止滥用，添加 rate limiting
6. **统计分析**: 上传、访问统计图表
7. **分享功能**: 生成分享链接，设置过期时间
8. **相册功能**: 图片分组管理

---

## 文档索引

- [README.md](README.md) - 完整部署文档
- [QUICKSTART.md](QUICKSTART.md) - 快速开始指南
- [deploy.sh](deploy.sh) - 一键部署脚本
- [test_upload.sh](test_upload.sh) - API 测试脚本

---

## 支持

如遇问题:
1. 查看日志: `docker compose logs -f`
2. 查看文档: `README.md`
3. 检查配置: `.env` 和 `nginx/conf.d/default.conf`

---

**项目完成日期**: 2025年
**适用系统**: Debian 12 / Ubuntu 20.04+ / CentOS 8+
**域名**: tc.bluse.me
**存储目录**: /data
