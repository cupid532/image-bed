# 图床系统 (Image Hosting System)

<div align="center">

一个功能完整的自托管图床系统，基于 Django 构建。

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-4.2-green.svg)](https://www.djangoproject.com/)
[![Docker](https://img.shields.io/badge/Docker-ready-blue.svg)](https://www.docker.com/)

[功能特性](#功能特性) • [快速开始](#快速开始) • [配置说明](#配置说明) • [文档](#文档) • [许可证](#许可证)

</div>

---

## 功能特性

### 核心功能

- 📤 **多种上传方式**
  - 拖拽上传
  - 粘贴上传 (Ctrl+V)
  - 批量上传
  - API 上传

- 🔐 **安全认证**
  - Token 认证保护
  - 多 Token 管理
  - 使用统计

- 🗜️ **图片优化**
  - 自动压缩
  - 尺寸限制
  - 智能去重 (基于 SHA256)

- 📊 **图片管理**
  - Web 图片库
  - 浏览量统计
  - 一键删除
  - 分页浏览

- 🎨 **现代化界面**
  - 响应式设计
  - 实时上传进度
  - 一键复制链接

### 技术特性

- ✅ 支持任意域名
- ✅ 多域名配置
- ✅ HTTP/HTTPS 自动适配
- ✅ Docker 一键部署
- ✅ Nginx 高性能服务
- ✅ 完整的 API 接口

---

## 快速开始

### 环境要求

- Docker 20.10+
- Docker Compose 2.0+
- 域名 (可选，可使用 IP)

### 一键部署

```bash
# 1. 克隆项目
git clone https://github.com/cupid532/image-bed.git
cd image-bed

# 2. 配置域名
cp .env.example .env
nano .env  # 修改 ALLOWED_HOSTS 为你的域名

# 3. 一键部署
chmod +x deploy.sh
sudo ./deploy.sh
```

部署脚本会自动：
- 安装 Docker 和 Docker Compose
- 生成安全的密钥和 Token
- 创建必要的目录
- 启动所有服务
- 初始化数据库

### 访问系统

部署完成后，访问 `http://your-domain.com` 即可使用。

---

## 配置说明

### 基础配置

编辑 `.env` 文件：

```bash
# 必须修改
SECRET_KEY=your-secret-key          # Django 密钥
API_TOKEN=your-api-token            # 上传 Token
ALLOWED_HOSTS=your-domain.com,localhost

# 可选配置
MAX_UPLOAD_SIZE=10485760            # 最大上传大小 (10MB)
ENABLE_IMAGE_COMPRESSION=True       # 启用压缩
COMPRESSION_QUALITY=85              # 压缩质量
MAX_IMAGE_DIMENSION=4096            # 最大尺寸
```

### 目录结构

```
/data/image_bed/
├── images/              # 图片存储
├── db/                  # 数据库
├── certbot/             # SSL 证书
└── certbot-www/         # Let's Encrypt 验证
```

### SSL 证书 (可选)

```bash
# 安装 Certbot
sudo apt install certbot -y

# 获取证书
sudo certbot certonly --standalone -d your-domain.com

# 复制证书
sudo mkdir -p /data/image_bed/certbot
sudo cp -r /etc/letsencrypt/* /data/image_bed/certbot/
```

更多配置说明请查看 [CONFIGURATION.md](CONFIGURATION.md)

---

## 使用示例

### Web 界面

1. 访问首页
2. 输入 API Token
3. 拖拽/粘贴/选择图片上传
4. 复制生成的链接

### API 调用

```bash
# 上传图片
curl -X POST https://your-domain.com/api/upload/ \
  -H "X-API-Token: YOUR_TOKEN" \
  -F "images=@image.jpg"

# 响应示例
{
  "results": [
    {
      "filename": "image.jpg",
      "url": "https://your-domain.com/i/20250101/abc123.jpg",
      "size": 123.45,
      "dimensions": "1920x1080"
    }
  ]
}
```

### Python SDK

```python
import requests

url = "https://your-domain.com/api/upload/"
headers = {"X-API-Token": "YOUR_TOKEN"}
files = {"images": open("image.jpg", "rb")}

response = requests.post(url, headers=headers, files=files)
print(response.json())
```

---

## 管理命令

```bash
# 查看日志
docker compose logs -f

# 重启服务
docker compose restart

# 创建管理员
docker compose exec web python manage.py createsuperuser

# 生成 Token
docker compose exec web python manage.py shell
>>> from imagehost.models import UploadToken
>>> token = UploadToken.objects.create(name="My Token", token=UploadToken.generate_token())
>>> print(token.token)

# 备份数据
tar -czf backup.tar.gz /data/image_bed
```

---

## 文档

- 📖 [完整文档](README.md) - 详细的使用和部署文档
- ⚙️ [配置指南](CONFIGURATION.md) - 高级配置说明
- 🚀 [快速开始](QUICKSTART.md) - 快速上手指南
- 📝 [更新日志](CHANGELOG.md) - 版本变更记录
- ✅ [部署检查清单](CHECKLIST.md) - 部署验证

---

## 技术栈

- **后端**: Django 4.2, Gunicorn
- **前端**: 原生 HTML/CSS/JavaScript
- **Web 服务器**: Nginx (Alpine)
- **容器化**: Docker, Docker Compose
- **图片处理**: Pillow
- **数据库**: SQLite (可迁移到 PostgreSQL)

---

## 项目结构

```
image-bed/
├── image_bed/          # Django 项目配置
├── imagehost/          # 图床应用
├── templates/          # HTML 模板
├── nginx/              # Nginx 配置
├── static/             # 静态文件
├── Dockerfile          # Docker 镜像
├── docker-compose.yml  # Docker Compose 配置
├── requirements.txt    # Python 依赖
├── deploy.sh           # 一键部署脚本
├── manage.sh           # 管理工具脚本
└── docs/               # 文档
```

---

## 常见问题

### 无法访问网站？

```bash
# 检查容器状态
docker compose ps

# 查看日志
docker compose logs nginx
docker compose logs web
```

### 上传失败？

```bash
# 检查目录权限
ls -la /data/image_bed/images/

# 检查磁盘空间
df -h /data
```

### 域名配置？

确保：
1. DNS 解析到服务器 IP
2. `.env` 中 `ALLOWED_HOSTS` 包含你的域名
3. 防火墙开放 80 和 443 端口

更多问题请查看 [完整文档](README.md)

---

## 贡献

欢迎提交 Issue 和 Pull Request！

1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

---

## 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

---

## 致谢

- Django 框架
- Pillow 图片处理库
- Docker 容器技术
- Nginx Web 服务器

---

## 联系方式

- GitHub: [@cupid532](https://github.com/cupid532)
- Issue: [提交问题](https://github.com/cupid532/image-bed/issues)

---

<div align="center">

**如果这个项目对你有帮助，请给个 ⭐️ Star 支持一下！**

Made with ❤️ by [cupid532](https://github.com/cupid532)

</div>
