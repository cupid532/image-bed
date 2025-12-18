# 图床系统 - 配置说明

## 核心改进

本项目已优化为通用图床系统，支持任意域名和标准化的部署路径。

### 主要变更

1. **通用域名支持**
   - 移除硬编码域名 `tc.bluse.me`
   - 所有 URL 动态生成，基于请求域名
   - Nginx 配置使用通配符 `server_name _`
   - 支持任意域名访问

2. **标准化部署路径**
   - 项目部署位置: `/data/image_bed/`
   - 图片存储: `/data/image_bed/images/`
   - 数据库: `/data/image_bed/db/`
   - SSL 证书: `/data/image_bed/certbot/`
   - 所有数据集中在 `/data` 目录

3. **灵活配置**
   - 通过 `.env` 文件配置域名
   - 支持多域名配置
   - 自动适应 HTTP/HTTPS

---

## 快速配置指南

### 1. 设置你的域名

编辑 `.env` 文件:

```bash
# 将 your-domain.com 替换为你的实际域名
ALLOWED_HOSTS=your-domain.com,www.your-domain.com,localhost,127.0.0.1
```

例如:
```bash
ALLOWED_HOSTS=tc.bluse.me,localhost,127.0.0.1
ALLOWED_HOSTS=img.example.com,localhost,127.0.0.1
ALLOWED_HOSTS=pics.mysite.net,localhost,127.0.0.1
```

### 2. 目录结构

部署后的目录结构:

```
/data/image_bed/
├── images/              # 上传的图片文件
│   ├── 20250101/
│   ├── 20250102/
│   └── ...
├── db/                  # 数据库文件
│   └── db.sqlite3
├── certbot/             # SSL 证书
│   └── live/
│       └── your-domain.com/
└── certbot-www/         # Let's Encrypt 验证文件
```

### 3. 部署位置

可以在任意位置部署项目源代码，例如:

```bash
/root/image_bed/         # 默认推荐
/opt/image_bed/          # 也可以
/home/user/image_bed/    # 也可以
```

数据始终存储在 `/data/image_bed/`，与源代码位置无关。

---

## 配置文件说明

### .env 文件

```bash
# 安全密钥 (必须修改)
SECRET_KEY=your-secret-key
API_TOKEN=your-api-token

# 应用配置
DEBUG=False
ALLOWED_HOSTS=your-domain.com,localhost
REQUIRE_AUTH=True

# 存储配置 (默认无需修改)
MEDIA_ROOT=/data/images

# 上传配置
MAX_UPLOAD_SIZE=10485760       # 10MB
ENABLE_IMAGE_COMPRESSION=True
COMPRESSION_QUALITY=85
MAX_IMAGE_DIMENSION=4096
```

### docker-compose.yml

数据卷映射:
```yaml
volumes:
  - /data/image_bed/images:/data/images    # 图片存储
  - /data/image_bed/db:/app/db             # 数据库
  - /data/image_bed/certbot:/etc/letsencrypt  # SSL 证书
```

---

## 多域名支持

### 配置多个域名

在 `.env` 中添加所有需要的域名:

```bash
ALLOWED_HOSTS=img1.example.com,img2.example.com,pics.mysite.com,localhost
```

### DNS 配置

确保所有域名都解析到服务器 IP:

```
A    img1.example.com    -> 你的服务器IP
A    img2.example.com    -> 你的服务器IP
A    pics.mysite.com     -> 你的服务器IP
```

### SSL 证书 (多域名)

为每个域名获取证书:

```bash
# 方法 1: 为每个域名单独获取
certbot certonly --standalone -d img1.example.com
certbot certonly --standalone -d img2.example.com

# 方法 2: 一次性为多个域名获取
certbot certonly --standalone -d img1.example.com -d img2.example.com
```

---

## URL 生成机制

### 自动 URL 生成

图片 URL 会根据访问域名自动生成:

- 访问 `http://img1.example.com` → 返回 `http://img1.example.com/i/xxx.jpg`
- 访问 `https://img2.example.com` → 返回 `https://img2.example.com/i/xxx.jpg`
- 自动检测 HTTP/HTTPS

### API 响应示例

```json
{
  "results": [
    {
      "filename": "test.jpg",
      "url": "https://your-domain.com/i/20250101/abc123.jpg",
      "size": 123.45,
      "dimensions": "1920x1080"
    }
  ]
}
```

URL 中的域名会自动匹配请求的域名。

---

## 迁移指南

### 从旧版本迁移

如果你之前使用了硬编码域名的版本:

1. **备份数据**
   ```bash
   tar -czf backup.tar.gz /data db.sqlite3
   ```

2. **更新配置**
   ```bash
   cd image_bed
   git pull  # 或重新下载项目
   ```

3. **更新 .env**
   ```bash
   # 添加你的域名
   echo "ALLOWED_HOSTS=your-domain.com,localhost" >> .env
   ```

4. **移动数据**
   ```bash
   mkdir -p /data/image_bed/images
   mv /data/* /data/image_bed/images/  # 如果有旧图片
   ```

5. **重启服务**
   ```bash
   docker compose down
   docker compose up -d --build
   ```

---

## 常见场景

### 场景 1: 个人博客图床

```bash
# .env
ALLOWED_HOSTS=blog.example.com,localhost
REQUIRE_AUTH=True
API_TOKEN=your-private-token
```

### 场景 2: 团队共享图床

```bash
# .env
ALLOWED_HOSTS=images.company.com,localhost
REQUIRE_AUTH=True
# 为每个成员创建不同的 Token
```

### 场景 3: 公开图床

```bash
# .env
ALLOWED_HOSTS=public-images.example.com,localhost
REQUIRE_AUTH=False  # 允许匿名上传 (不推荐)
```

### 场景 4: CDN 加速

```bash
# .env
ALLOWED_HOSTS=cdn.example.com,origin.example.com,localhost

# 在 CDN 配置中:
# - 回源域名: origin.example.com
# - CDN 域名: cdn.example.com
```

---

## 测试配置

### 验证域名配置

```bash
# 1. 检查 DNS
ping your-domain.com

# 2. 测试 HTTP 访问
curl http://your-domain.com

# 3. 测试 HTTPS 访问
curl https://your-domain.com

# 4. 测试上传
curl -X POST http://your-domain.com/api/upload/ \
  -H "X-API-Token: YOUR_TOKEN" \
  -F "images=@test.jpg"
```

### 验证路径配置

```bash
# 检查目录结构
ls -la /data/image_bed/

# 检查权限
ls -la /data/image_bed/images/

# 检查磁盘使用
du -sh /data/image_bed/*
```

---

## 故障排查

### 域名无法访问

1. 检查 DNS 解析: `ping your-domain.com`
2. 检查 `.env` 中的 `ALLOWED_HOSTS`
3. 检查 Nginx 配置: `docker compose exec nginx nginx -t`
4. 查看日志: `docker compose logs nginx`

### 图片无法上传

1. 检查目录权限: `ls -la /data/image_bed/images/`
2. 检查磁盘空间: `df -h /data`
3. 查看日志: `docker compose logs web`

### URL 返回错误

1. 检查 `MEDIA_ROOT` 配置
2. 检查 Nginx `location /i/` 配置
3. 确认文件确实存在: `ls /data/image_bed/images/`

---

## 高级配置

### 自定义图片路径

修改 `.env`:
```bash
MEDIA_ROOT=/data/image_bed/my-custom-path
```

修改 `docker-compose.yml`:
```yaml
volumes:
  - /data/image_bed/my-custom-path:/data/images
```

### 自定义 URL 前缀

修改 `settings.py`:
```python
MEDIA_URL = '/images/'  # 改为 /images/ 而不是 /i/
```

修改 Nginx 配置:
```nginx
location /images/ {
    alias /data/images/;
    # ...
}
```

---

## 最佳实践

1. **安全性**
   - 始终使用 HTTPS
   - 定期更换 API Token
   - 启用认证 (REQUIRE_AUTH=True)

2. **性能**
   - 启用图片压缩
   - 使用 CDN 加速
   - 定期清理旧图片

3. **备份**
   - 定期备份 `/data/image_bed/`
   - 备份数据库文件
   - 保存 `.env` 配置

4. **监控**
   - 监控磁盘空间
   - 监控访问日志
   - 设置告警

---

## 支持

- 完整文档: [README.md](README.md)
- 快速开始: [QUICKSTART.md](QUICKSTART.md)
- 部署检查: [CHECKLIST.md](CHECKLIST.md)

如有问题，请查看日志:
```bash
docker compose logs -f
```
