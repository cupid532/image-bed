# 图床完整部署指南

本文档提供从零开始部署图床的完整步骤。

## 📋 前提条件

- 一台 Linux 服务器（Ubuntu/Debian/CentOS）
- 已安装 Docker 和 Docker Compose
- 服务器 IP: `23.147.204.72`（示例）
- 域名: `tc.090798.xyz`（可选）

---

## 🚀 完整部署步骤

### 步骤 1：SSH 连接到服务器

```bash
ssh root@23.147.204.72
```

### 步骤 2：克隆项目

```bash
# 克隆最新代码
git clone https://github.com/cupid532/image-bed.git
cd image-bed
```

### 步骤 3：配置环境变量

```bash
# 复制配置文件模板
cp .env.example .env

# 编辑配置
nano .env
```

**重要配置项**（修改为你的实际值）：

```bash
# 安全密钥（生成新的）
SECRET_KEY=你的随机密钥

# API Token（可留空，后续在后台创建）
API_TOKEN=

# 应用设置
DEBUG=False
ALLOWED_HOSTS=23.147.204.72,tc.090798.xyz,localhost,127.0.0.1
REQUIRE_AUTH=True

# HTTPS 设置（IP 访问时设为 False）
FORCE_HTTPS=False

# 存储设置
MEDIA_ROOT=/data/images

# 上传设置
MAX_UPLOAD_SIZE=10485760
ENABLE_IMAGE_COMPRESSION=True
COMPRESSION_QUALITY=85
MAX_IMAGE_DIMENSION=4096
```

**生成 SECRET_KEY**（可选）：

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(50))"
```

保存并退出：`Ctrl+O` → `Enter` → `Ctrl+X`

### 步骤 4：构建并启动容器

```bash
# 使用 docker-compose 启动
docker-compose up -d

# 或使用新版 docker compose
docker compose up -d

# 查看容器状态
docker ps | grep image_bed
```

### 步骤 5：初始化数据库

```bash
# 运行数据库迁移
docker exec -it image_bed python manage.py migrate

# 收集静态文件
docker exec -it image_bed python manage.py collectstatic --noinput
```

### 步骤 6：创建超级管理员

```bash
docker exec -it image_bed python manage.py createsuperuser

# 按提示输入：
# Username: admin（或你的用户名）
# Email: your@email.com（可随意填）
# Password: 输入密码（不显示）
# Password (again): 再次确认密码
```

### 步骤 7：验证部署

```bash
# 测试访问
curl -I http://localhost:8000/

# 应返回 200 OK
```

### 步骤 8：访问图床

在浏览器中访问：

- **主页（上传界面）**: `http://23.147.204.72:8000/`
- **图片库**: `http://23.147.204.72:8000/gallery/`
- **后台管理**: `http://23.147.204.72:8000/admin/`

---

## 🔑 获取 API Token

### 1. 登录后台

访问：`http://23.147.204.72:8000/admin/`

使用刚才创建的管理员账号登录。

### 2. 创建 Token

1. 在后台找到 **"Upload tokens"** 或 **"上传令牌"**
2. 点击 **"增加"** 或 **"Add Upload Token"**
3. 填写：
   - **Name**: 给 Token 起个名字（如 "我的电脑"）
   - **Is active**: 勾选 ✓（激活）
4. 点击 **"保存"**
5. **复制生成的 Token**（64 位字符串）

### 3. 使用 Token 上传

#### 方式 1：网页上传

1. 访问：`http://23.147.204.72:8000/`
2. 在 **"API Token"** 框粘贴你的 Token
3. 选择图片并上传

#### 方式 2：API 上传

```bash
curl -X POST http://23.147.204.72:8000/api/upload/ \
  -H "X-API-Token: 你的Token" \
  -F "image=@/path/to/image.jpg"
```

#### 方式 3：使用 PicGo

配置：
- **URL**: `http://23.147.204.72:8000/api/upload/`
- **请求头**: `X-API-Token: 你的Token`
- **Body 字段**: `image`

---

## 🌐 配置域名访问（可选）

如果你有 Caddy 反向代理：

### 编辑 Caddyfile

```bash
nano /etc/caddy/Caddyfile
```

添加：

```caddy
tc.090798.xyz {
    reverse_proxy localhost:8000
}
```

### 重启 Caddy

```bash
# 如果 Caddy 在 Docker 中
docker restart caddy

# 如果是系统服务
sudo systemctl reload caddy
```

### 更新 .env 配置

```bash
nano ~/image-bed/.env

# 确保 ALLOWED_HOSTS 包含域名
ALLOWED_HOSTS=tc.090798.xyz,23.147.204.72,localhost,127.0.0.1

# 重启图床容器
docker restart image_bed
```

现在可以通过 `https://tc.090798.xyz` 访问！Caddy 会自动申请 SSL 证书。

---

## 🔄 更新部署

当 GitHub 有新版本时：

```bash
cd ~/image-bed

# 停止容器
docker-compose down

# 拉取最新代码
git pull origin main

# 重新构建镜像（如果有依赖更新）
docker-compose build

# 启动容器
docker-compose up -d

# 运行数据库迁移（如果有）
docker exec -it image_bed python manage.py migrate

# 收集静态文件
docker exec -it image_bed python manage.py collectstatic --noinput

# 验证
docker logs image_bed --tail 20
```

---

## 🔧 常见问题

### 1. "Bad Request (400)" 错误

**原因**：IP 地址不在 `ALLOWED_HOSTS` 中。

**解决**：

```bash
nano ~/image-bed/.env
# 确保 ALLOWED_HOSTS 包含你的 IP
ALLOWED_HOSTS=23.147.204.72,localhost,127.0.0.1

# 重启容器
docker-compose down
docker-compose up -d
```

### 2. "Server Error (500)" 错误

**原因**：数据库未初始化或静态文件未收集。

**解决**：

```bash
docker exec -it image_bed python manage.py migrate
docker exec -it image_bed python manage.py collectstatic --noinput
docker restart image_bed
```

### 3. 无法访问后台

**原因**：未创建超级管理员。

**解决**：

```bash
docker exec -it image_bed python manage.py createsuperuser
```

### 4. 容器无法启动

**查看日志**：

```bash
docker logs image_bed --tail 50
```

**检查配置**：

```bash
cat ~/image-bed/.env
```

### 5. 图片无法上传

**检查 Token**：确保在后台创建了 Token 并且是激活状态。

**检查权限**：

```bash
sudo chown -R 1000:1000 /data/images
```

---

## 📊 维护操作

### 查看日志

```bash
# 实时查看日志
docker logs -f image_bed

# 查看最后 50 行
docker logs image_bed --tail 50
```

### 备份数据

```bash
# 备份图片
sudo tar -czf images_backup_$(date +%Y%m%d).tar.gz /data/images

# 备份数据库
docker cp image_bed:/app/db.sqlite3 ./db_backup_$(date +%Y%m%d).sqlite3
```

### 清理旧图片

在后台管理界面手动删除，或使用 API：

```bash
curl -X DELETE http://23.147.204.72:8000/api/images/图片ID/delete/ \
  -H "X-API-Token: 你的Token"
```

### 查看存储空间

```bash
du -sh /data/images
```

---

## 🔒 安全建议

1. **修改默认密钥**
   - 生成强随机的 `SECRET_KEY`
   - 不要使用默认值

2. **启用认证**
   - 保持 `REQUIRE_AUTH=True`
   - 不要公开你的 Token

3. **使用 HTTPS**
   - 公网访问时配置域名和 SSL
   - 使用 Caddy 自动管理证书

4. **限制访问**
   - 使用防火墙限制来源 IP（可选）
   - 定期更换 Token

5. **定期备份**
   - 备份图片和数据库
   - 保存配置文件

6. **监控日志**
   - 定期检查异常访问
   - 关注错误日志

---

## 📈 性能优化

### 1. 调整上传限制

编辑 `.env`：

```bash
MAX_UPLOAD_SIZE=20971520  # 20MB
MAX_IMAGE_DIMENSION=8192   # 8K 分辨率
COMPRESSION_QUALITY=90     # 更高质量
```

### 2. 增加 Worker 数量

编辑 `docker-compose.yml`：

```yaml
services:
  web:
    command: gunicorn --bind 0.0.0.0:8000 --workers 8 image_bed.wsgi:application
```

### 3. 使用 Redis 缓存（高级）

可考虑添加 Redis 服务提升性能。

---

## 🎨 自定义配置

### Simpleui 主题

编辑 `image_bed/settings.py` 中的 `SIMPLEUI_DEFAULT_THEME`：

可选主题：
- `admin.lte.css` （默认，推荐）
- `layui.css`
- `ant.design.css`
- `element.css`
- `simpleui.css`

### 修改菜单

编辑 `SIMPLEUI_CONFIG` 配置自定义菜单结构。

---

## 📚 API 文档

### 上传图片

```bash
POST /api/upload/

Headers:
  X-API-Token: your-token

Body (multipart/form-data):
  image: 图片文件
```

**响应**：

```json
{
  "url": "http://23.147.204.72:8000/i/2024/12/19/abc123.jpg",
  "filename": "abc123.jpg",
  "size": 123456,
  "format": "JPEG"
}
```

### 列出图片

```bash
GET /api/images/?token=your-token

或

GET /api/images/
Headers:
  X-API-Token: your-token
```

### 删除图片

```bash
DELETE /api/images/{id}/delete/?token=your-token
```

---

## 🆘 获取帮助

- **GitHub Issues**: https://github.com/cupid532/image-bed/issues
- **文档目录**:
  - [IP 访问指南](IP_ACCESS_GUIDE.md)
  - [更新说明](IP_UPDATE_NOTES.md)
  - [卸载指南](UNINSTALL_GUIDE.md)
  - [快速开始](QUICKSTART.md)

---

## ✅ 部署检查清单

部署完成后，使用此清单验证：

- [ ] Docker 容器正常运行（`docker ps | grep image_bed`）
- [ ] 可以访问主页 `http://IP:8000/`
- [ ] 可以访问后台 `http://IP:8000/admin/`
- [ ] 已创建超级管理员账号
- [ ] 已创建至少一个 API Token
- [ ] 测试图片上传功能
- [ ] 测试图片访问和浏览
- [ ] （可选）域名访问配置完成
- [ ] （可选）SSL 证书已申请
- [ ] 已备份 `.env` 配置文件

---

## 🎉 恭喜！

你的图床已经部署成功！现在可以：

1. 通过网页上传图片
2. 使用 API 集成到其他应用
3. 配置 PicGo 等工具
4. 在 Markdown 中使用图片链接

享受你的私有图床服务！🚀
