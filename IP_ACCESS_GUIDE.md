# IP 地址访问配置指南

本文档说明如何配置图床以支持通过 IP 地址 + 端口访问，而不需要域名和 SSL 证书。

## 📋 目录

- [快速开始](#快速开始)
- [详细配置](#详细配置)
- [配置选项对比](#配置选项对比)
- [常见问题](#常见问题)

---

## 快速开始

如果你想通过 IP 地址（如 `http://192.168.1.100:8080`）访问图床，请按照以下步骤操作：

### 1. 配置环境变量

创建或编辑 `.env` 文件：

```bash
# 复制示例文件
cp .env.example .env

# 编辑 .env 文件
nano .env
```

**关键配置**：

```bash
# 添加你的服务器 IP 地址到 ALLOWED_HOSTS
ALLOWED_HOSTS=192.168.1.100,localhost,127.0.0.1

# 禁用 HTTPS 强制重定向（对于 IP 访问必须设置）
FORCE_HTTPS=False

# 其他设置保持默认即可
DEBUG=False
REQUIRE_AUTH=True
```

### 2. 使用正确的 Nginx 配置

项目提供了两个 Nginx 配置文件：

- **`nginx/conf.d/default.conf`** - 用于 IP 访问（HTTP）✅ 推荐用于 IP 部署
- **`nginx/conf.d/default-http-ip.conf`** - 同样用于 IP 访问的备用配置
- **`nginx/conf.d/default-https-template.conf`** - 用于域名访问（HTTPS）

**确保在 Docker Compose 中使用正确的配置**（默认已正确）：

```yaml
# docker-compose.yml 中的 nginx 服务
nginx:
  volumes:
    - ./nginx/conf.d:/etc/nginx/conf.d:ro
```

### 3. 启动服务

```bash
# 使用 Docker Compose 启动
docker-compose up -d

# 或使用管理脚本
./manage.sh start
```

### 4. 访问图床

通过你的 IP 地址和端口访问：

```
http://192.168.1.100:8080/        # 上传界面
http://192.168.1.100:8080/gallery/ # 图片库
http://192.168.1.100:8080/admin/   # 管理后台
```

---

## 详细配置

### 环境变量详解

#### ALLOWED_HOSTS

**说明**：Django 允许访问的主机名列表，用逗号分隔。

**IP 访问配置**：

```bash
# 单个 IP
ALLOWED_HOSTS=192.168.1.100,localhost,127.0.0.1

# 多个 IP（例如内网和外网 IP）
ALLOWED_HOSTS=192.168.1.100,10.0.0.50,localhost,127.0.0.1

# 使用通配符（不推荐用于生产环境）
ALLOWED_HOSTS=*
```

**注意事项**：
- 必须包含所有可能用于访问的 IP 地址
- 不需要包含端口号（Django 会自动处理）
- `localhost` 和 `127.0.0.1` 用于本地测试

#### FORCE_HTTPS

**说明**：控制是否强制使用 HTTPS。

**IP 访问配置**：

```bash
# 对于 IP 访问，必须设置为 False
FORCE_HTTPS=False
```

**为什么必须设置为 False？**

1. IP 地址无法获得有效的 SSL 证书
2. Let's Encrypt 等证书颁发机构只为域名颁发证书
3. 如果设置为 `True`，Django 会将所有 HTTP 请求重定向到 HTTPS，导致无法访问

#### DEBUG

**说明**：开发模式开关。

```bash
# 生产环境（推荐）
DEBUG=False

# 开发环境（仅用于测试，会显示详细错误信息）
DEBUG=True
```

**安全提示**：生产环境中必须设置 `DEBUG=False`！

#### REQUIRE_AUTH

**说明**：是否需要 API Token 认证才能上传图片。

```bash
# 需要认证（推荐）
REQUIRE_AUTH=True

# 允许匿名上传（不推荐）
REQUIRE_AUTH=False
```

### Nginx 配置详解

#### default.conf vs default-https-template.conf

| 特性 | default.conf | default-https-template.conf |
|------|--------------|----------------------------|
| 协议 | HTTP (80) | HTTPS (443) + HTTP redirect |
| server_name | `_` (匹配所有) | 特定域名 (如 `tc.bluse.me`) |
| SSL 证书 | 不需要 | 需要 |
| 适用场景 | IP 访问 | 域名访问 |

#### default.conf 关键配置

```nginx
server {
    listen 80;
    server_name _;  # 匹配任意域名或 IP

    # 最大上传文件大小
    client_max_body_size 20M;

    # 代理到 Django 应用
    location / {
        proxy_pass http://django;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

**`server_name _` 的作用**：

- `_` 是 Nginx 的特殊语法，表示"匹配所有主机名"
- 支持任意 IP 地址访问
- 支持任意域名访问（如果你有多个域名指向同一服务器）

### Docker Compose 端口映射

编辑 `docker-compose.yml` 更改端口：

```yaml
services:
  nginx:
    ports:
      - "8080:80"  # 将容器的 80 端口映射到主机的 8080 端口
      # - "443:443"  # HTTPS 端口（IP 访问时不需要）
```

**常见端口选择**：

- `80:80` - 使用标准 HTTP 端口（需要 root 权限或防火墙配置）
- `8080:80` - 使用非特权端口 8080
- `3000:80` - 使用端口 3000
- 任意其他端口（1024-65535）

---

## 配置选项对比

### 场景 1：IP 地址 + HTTP（无 SSL）

**适用场景**：内网部署、开发环境、临时使用

```bash
# .env 配置
ALLOWED_HOSTS=192.168.1.100,localhost,127.0.0.1
FORCE_HTTPS=False
DEBUG=False
```

**Nginx 配置**：使用 `default.conf`

**访问方式**：`http://192.168.1.100:8080`

**优点**：
- ✅ 配置简单
- ✅ 不需要域名
- ✅ 不需要 SSL 证书
- ✅ 适合内网环境

**缺点**：
- ❌ 数据未加密（不安全）
- ❌ 不适合公网暴露

### 场景 2：域名 + HTTPS（有 SSL）

**适用场景**：生产环境、公网访问、需要安全性

```bash
# .env 配置
ALLOWED_HOSTS=tc.bluse.me,localhost,127.0.0.1
FORCE_HTTPS=True
DEBUG=False
```

**Nginx 配置**：使用 `default-https-template.conf`（需修改域名）

**访问方式**：`https://tc.bluse.me`

**优点**：
- ✅ 数据加密传输
- ✅ 适合公网访问
- ✅ SEO 友好
- ✅ 浏览器信任

**缺点**：
- ❌ 需要域名
- ❌ 需要 SSL 证书
- ❌ 配置复杂

### 场景 3：混合模式（同时支持 IP 和域名）

**适用场景**：灵活部署、多种访问方式

```bash
# .env 配置
ALLOWED_HOSTS=192.168.1.100,tc.bluse.me,localhost,127.0.0.1
FORCE_HTTPS=False  # 或根据主要访问方式设置
DEBUG=False
```

**优点**：
- ✅ 最灵活
- ✅ 可同时通过 IP 和域名访问

**缺点**：
- ❌ 可能存在安全策略冲突

---

## 常见问题

### Q1: 无法通过 IP 访问，显示 "Invalid HTTP_HOST header"

**原因**：IP 地址未添加到 `ALLOWED_HOSTS`。

**解决方法**：

```bash
# 编辑 .env 文件
ALLOWED_HOSTS=你的IP地址,localhost,127.0.0.1

# 重启服务
docker-compose restart
```

### Q2: 访问时自动跳转到 HTTPS，导致无法访问

**原因**：`FORCE_HTTPS=True` 导致强制 HTTPS 重定向。

**解决方法**：

```bash
# 编辑 .env 文件
FORCE_HTTPS=False

# 重启服务
docker-compose restart
```

### Q3: 图片上传成功，但返回的 URL 不正确

**原因**：这通常不会发生，因为项目使用 `get_full_url()` 动态生成 URL。

**检查方法**：

```python
# 在 imagehost/views.py 中的 get_full_url 函数
def get_full_url(request, path):
    scheme = 'https' if request.is_secure() else 'http'
    host = request.get_host()  # 自动获取 IP:端口
    return f"{scheme}://{host}{path}"
```

### Q4: 需要同时支持 HTTP 和 HTTPS 吗?

**答案**：不建议同时使用。选择其中一种：

- **仅 HTTP**（IP 访问）：`FORCE_HTTPS=False`，使用 `default.conf`
- **仅 HTTPS**（域名访问）：`FORCE_HTTPS=True`，使用 `default-https-template.conf`

### Q5: 能否在公网使用 IP + HTTP？

**答案**：技术上可以，但**强烈不推荐**！

**原因**：
- 数据未加密，容易被窃听
- API Token 可能被截获
- 上传的图片可能被篡改

**建议**：公网访问请使用域名 + HTTPS。

### Q6: 如何更改访问端口？

**方法 1：修改 Docker Compose**

```yaml
# docker-compose.yml
services:
  nginx:
    ports:
      - "8888:80"  # 更改为你想要的端口
```

**方法 2：使用主机网络模式**

```yaml
services:
  nginx:
    network_mode: "host"
```

### Q7: CSRF 验证失败怎么办？

**原因**：新版本已修复 CSRF 配置以支持 IP 访问。

**检查配置**：

```python
# image_bed/settings.py 中的 CSRF 配置
CSRF_TRUSTED_ORIGINS = []
for host in ALLOWED_HOSTS:
    if host not in ['localhost', '127.0.0.1']:
        CSRF_TRUSTED_ORIGINS.append(f'http://{host}')
        CSRF_TRUSTED_ORIGINS.append(f'https://{host}')
```

**确保**：你的 IP 地址已添加到 `ALLOWED_HOSTS`。

---

## 配置验证清单

使用以下清单验证你的配置：

### IP 访问配置清单

- [ ] `.env` 文件中 `ALLOWED_HOSTS` 包含你的 IP 地址
- [ ] `.env` 文件中 `FORCE_HTTPS=False`
- [ ] Docker Compose 使用 `default.conf` 或 `default-http-ip.conf`
- [ ] 服务已重启（`docker-compose restart`）
- [ ] 防火墙允许访问端口（如 8080）
- [ ] 可以通过 `http://IP:端口/` 访问上传界面

### 域名访问配置清单

- [ ] DNS 记录已指向服务器
- [ ] `.env` 文件中 `ALLOWED_HOSTS` 包含域名
- [ ] `.env` 文件中 `FORCE_HTTPS=True`
- [ ] 已修改 `default-https-template.conf` 中的域名
- [ ] 已获取 SSL 证书（Let's Encrypt）
- [ ] Nginx 配置已切换到 HTTPS 模板
- [ ] 可以通过 `https://域名/` 访问上传界面

---

## 完整配置示例

### 示例 1：内网 IP 访问

**环境**：公司内网，IP: `192.168.10.50`，端口: `8080`

```bash
# .env 文件
SECRET_KEY=your-secret-key-change-this
API_TOKEN=your-api-token
DEBUG=False
ALLOWED_HOSTS=192.168.10.50,localhost,127.0.0.1
REQUIRE_AUTH=True
FORCE_HTTPS=False
MEDIA_ROOT=/data/images
MAX_UPLOAD_SIZE=10485760
```

```yaml
# docker-compose.yml (端口配置)
services:
  nginx:
    ports:
      - "8080:80"
```

**访问方式**：`http://192.168.10.50:8080`

### 示例 2：外网域名访问

**环境**：公网域名，`tc.bluse.me`

```bash
# .env 文件
SECRET_KEY=your-secret-key-change-this
API_TOKEN=your-api-token
DEBUG=False
ALLOWED_HOSTS=tc.bluse.me,localhost,127.0.0.1
REQUIRE_AUTH=True
FORCE_HTTPS=True
MEDIA_ROOT=/data/images
MAX_UPLOAD_SIZE=10485760
```

**Nginx 配置**：使用 `default-https-template.conf`（修改域名）

**访问方式**：`https://tc.bluse.me`

---

## 安全建议

### 针对 IP 访问（HTTP）

1. **仅在内网使用**：避免直接暴露到公网
2. **启用认证**：`REQUIRE_AUTH=True`
3. **使用防火墙**：限制访问来源 IP
4. **定期更新 Token**：在 Admin 后台定期轮换 Token
5. **监控访问日志**：检查异常访问

### 针对域名访问（HTTPS）

1. **强制 HTTPS**：`FORCE_HTTPS=True`
2. **使用强密钥**：`SECRET_KEY` 至少 50 个字符
3. **启用 HSTS**：已在 Nginx 配置中包含
4. **定期更新证书**：配置 Certbot 自动续期
5. **启用访问日志**：监控异常请求

---

## 技术细节

### 动态 URL 生成机制

项目使用 `get_full_url()` 函数动态生成图片 URL：

```python
# imagehost/views.py
def get_full_url(request, path):
    """Generate full URL from request and path"""
    scheme = 'https' if request.is_secure() else 'http'
    host = request.get_host()  # 包括端口，例如 "192.168.1.100:8080"
    return f"{scheme}://{host}{path}"
```

**特点**：
- 自动检测协议（HTTP/HTTPS）
- 自动获取主机名和端口
- 无需硬编码域名或 IP
- 支持反向代理环境

### CSRF 保护机制

新版本的 CSRF 配置同时支持 HTTP 和 HTTPS：

```python
# image_bed/settings.py
CSRF_TRUSTED_ORIGINS = []
for host in ALLOWED_HOSTS:
    if host not in ['localhost', '127.0.0.1']:
        CSRF_TRUSTED_ORIGINS.append(f'http://{host}')
        CSRF_TRUSTED_ORIGINS.append(f'https://{host}')
```

这确保了无论使用 HTTP 还是 HTTPS，CSRF 验证都能正常工作。

---

## 总结

通过以上配置，你的图床现在可以灵活地支持：

1. ✅ **IP + 端口访问**（HTTP）- 适合内网和开发环境
2. ✅ **域名访问**（HTTPS）- 适合生产环境和公网访问
3. ✅ **混合模式** - 根据需要同时支持多种访问方式

**核心要点**：

- 使用 IP 访问时，必须设置 `FORCE_HTTPS=False`
- 所有访问的 IP/域名都必须添加到 `ALLOWED_HOSTS`
- Nginx 配置 `server_name _` 支持任意主机名
- 项目代码已支持动态 URL 生成，无需修改代码

如有问题，请检查：
1. `.env` 配置
2. Nginx 配置文件
3. Docker Compose 端口映射
4. 防火墙和网络设置
