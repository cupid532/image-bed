# 更新日志 (CHANGELOG)

## 版本 2.0 - 通用化改进 (2025-01-XX)

### 主要变更

#### 🎯 通用域名支持
- **移除硬编码域名**: 不再强制使用 `tc.bluse.me`
- **动态 URL 生成**: 图片 URL 基于请求域名自动生成
- **多域名支持**: 通过 `ALLOWED_HOSTS` 配置多个域名
- **Nginx 通配符**: 使用 `server_name _` 匹配任意域名

#### 📁 标准化部署路径
- **集中数据存储**: 所有数据统一在 `/data/image_bed/` 目录
- **子目录结构**:
  - `/data/image_bed/images/` - 图片存储
  - `/data/image_bed/db/` - 数据库
  - `/data/image_bed/certbot/` - SSL 证书
- **灵活源代码位置**: 项目源代码可放置在任意位置

#### ⚙️ 配置改进
- **新增环境变量**: `MEDIA_ROOT` 可配置图片存储路径
- **默认值优化**: `ALLOWED_HOSTS` 默认值改为 `localhost,127.0.0.1`
- **Docker 卷映射**: 优化卷映射结构，更清晰明确

### 具体修改

#### 后端代码 (Python/Django)

**settings.py**
```python
# 旧版
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'tc.bluse.me,localhost,127.0.0.1').split(',')
MEDIA_ROOT = '/data'

# 新版
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')
MEDIA_ROOT = os.getenv('MEDIA_ROOT', '/data/images')
```

**models.py**
```python
# 旧版
@property
def full_url(self):
    return f"https://tc.bluse.me{self.url}"

# 新版
@property
def full_url(self):
    # 动态生成，在 views 中实现
    return self.url
```

**views.py**
```python
# 新增函数
def get_full_url(request, path):
    """根据请求动态生成完整 URL"""
    scheme = 'https' if request.is_secure() else 'http'
    host = request.get_host()
    return f"{scheme}://{host}{path}"

# 使用示例
'url': get_full_url(request, image.url)  # 替代 image.full_url
```

#### 配置文件

**docker-compose.yml**
```yaml
# 旧版
volumes:
  - /data:/data
  - ./db.sqlite3:/app/db.sqlite3

# 新版
volumes:
  - /data/image_bed/images:/data/images
  - /data/image_bed/db:/app/db
```

**.env.example**
```bash
# 旧版
ALLOWED_HOSTS=tc.bluse.me,localhost,127.0.0.1

# 新版
ALLOWED_HOSTS=your-domain.com,localhost,127.0.0.1
MEDIA_ROOT=/data/images
```

#### Nginx 配置

**default.conf**
```nginx
# 旧版
server_name tc.bluse.me;
ssl_certificate /etc/letsencrypt/live/tc.bluse.me/fullchain.pem;
alias /data/;

# 新版
server_name _;  # 匹配任意域名
# ssl_certificate /etc/letsencrypt/live/YOUR_DOMAIN/fullchain.pem;  # 需要配置
alias /data/images/;
```

#### 部署脚本

**deploy.sh**
```bash
# 旧版
mkdir -p /data
chown -R 1000:1000 /data
echo "访问地址: http://tc.bluse.me"

# 新版
mkdir -p /data/image_bed/{images,db,certbot,certbot-www}
chown -R 1000:1000 /data/image_bed
echo "访问地址: http://YOUR_DOMAIN (请替换为你的域名)"
echo "1. 在 .env 文件中设置 ALLOWED_HOSTS 为你的域名"
```

### 向后兼容性

#### ⚠️ 重大变更 (Breaking Changes)

1. **路径变更**
   - 图片存储从 `/data/` 改为 `/data/image_bed/images/`
   - 需要迁移现有图片

2. **URL 生成**
   - API 返回的 URL 不再包含硬编码域名
   - 基于请求动态生成

3. **环境变量**
   - `.env` 文件需要手动设置 `ALLOWED_HOSTS`

#### 迁移步骤

如果从旧版本升级:

1. **备份数据**
   ```bash
   tar -czf backup.tar.gz /data/ db.sqlite3
   ```

2. **创建新目录结构**
   ```bash
   mkdir -p /data/image_bed/{images,db,certbot,certbot-www}
   ```

3. **迁移图片**
   ```bash
   mv /data/* /data/image_bed/images/  # 如果有旧图片
   ```

4. **更新 .env**
   ```bash
   echo "ALLOWED_HOSTS=your-domain.com,localhost" >> .env
   ```

5. **重新部署**
   ```bash
   docker compose down
   docker compose up -d --build
   ```

### 新增文档

- **[CONFIGURATION.md](CONFIGURATION.md)** - 详细的配置说明
- **[CHANGELOG.md](CHANGELOG.md)** - 本文件，记录所有变更

### 已知问题

暂无

### 计划中的功能

- [ ] 支持多种对象存储后端 (S3, OSS, COS)
- [ ] 图片编辑功能 (裁剪、旋转、水印)
- [ ] 用户配额管理
- [ ] API 速率限制
- [ ] 统计分析面板

---

## 版本 1.0 - 初始版本

### 功能

- ✅ 图片上传 (拖拽、粘贴、批量)
- ✅ 图片管理 (查看、删除)
- ✅ Token 认证
- ✅ 自动压缩
- ✅ 去重机制
- ✅ Docker 部署
- ✅ Nginx 反向代理
- ✅ SSL 支持

### 技术栈

- Django 4.2
- Gunicorn
- Nginx
- Docker
- Pillow

---

## 如何查看变更

### 代码对比

```bash
# 查看所有改动的文件
git diff v1.0 v2.0 --name-only

# 查看具体变更
git diff v1.0 v2.0 -- image_bed/settings.py
```

### 测试新功能

```bash
# 测试动态域名
curl http://domain1.example.com/api/upload/ ...
curl http://domain2.example.com/api/upload/ ...

# 验证返回的 URL 是否匹配请求域名
```

---

## 贡献

欢迎提交 Issue 和 Pull Request！

## 许可证

MIT License
