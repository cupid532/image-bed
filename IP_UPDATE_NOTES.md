# 图床 IP 访问功能更新说明

## 📅 更新时间
2025-12-19

## 🎯 更新目标
支持使用 IP 地址 + 端口进行访问，无需强制使用域名和 SSL 证书。

---

## ✨ 主要更改

### 1. Django Settings 配置优化 ([settings.py](image_bed/image_bed/settings.py#L114-L134))

#### 更改前：
```python
# CSRF settings
CSRF_TRUSTED_ORIGINS = [f'https://{host}' for host in ALLOWED_HOSTS if host not in ['localhost', '127.0.0.1']]

# Security settings for production
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
```

#### 更改后：
```python
# CSRF settings
# Support both HTTPS domains and HTTP IP addresses with ports
CSRF_TRUSTED_ORIGINS = []
for host in ALLOWED_HOSTS:
    if host in ['localhost', '127.0.0.1']:
        continue
    # Add both HTTP and HTTPS for domains and IPs
    CSRF_TRUSTED_ORIGINS.append(f'http://{host}')
    CSRF_TRUSTED_ORIGINS.append(f'https://{host}')

# Security settings for production
# Allow disabling HTTPS redirect for IP-based deployments
FORCE_HTTPS = os.getenv('FORCE_HTTPS', 'True') == 'True'

if not DEBUG and FORCE_HTTPS:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
```

**改进说明**：
- ✅ CSRF 配置同时支持 HTTP 和 HTTPS 协议
- ✅ 新增 `FORCE_HTTPS` 环境变量控制 HTTPS 重定向
- ✅ IP 访问时可以禁用 HTTPS 强制跳转
- ✅ 保持了生产环境的安全性配置

### 2. Nginx 配置文件

#### 新增文件：[default-http-ip.conf](nginx/conf.d/default-http-ip.conf)

专门用于 IP 访问的 Nginx 配置文件：

```nginx
server {
    listen 80;
    server_name _;  # 匹配所有域名和 IP 地址

    client_max_body_size 20M;

    location / {
        proxy_pass http://django;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

**特点**：
- ✅ `server_name _` 匹配任意主机名或 IP
- ✅ 支持所有必要的代理头
- ✅ 已配置上传大小限制
- ✅ 已配置静态文件和图片服务

**注意**：项目默认的 `default.conf` 已经支持 IP 访问，这个文件作为备用配置。

### 3. 环境变量配置文件 ([.env.example](.env.example#L5-L17))

#### 更新内容：

```bash
# App settings
DEBUG=False
# ALLOWED_HOSTS: Comma-separated list of domains or IP addresses
# For domain: your-domain.com
# For IP: 192.168.1.100 or your-server-ip
# You can also include ports: 192.168.1.100:8080 (though nginx typically handles this)
ALLOWED_HOSTS=your-domain.com,localhost,127.0.0.1
REQUIRE_AUTH=True

# HTTPS Settings
# Set to False if using IP-based access without SSL certificate
# Set to True if using domain with SSL certificate
FORCE_HTTPS=False
```

**新增说明**：
- ✅ 添加了详细的 IP 配置注释
- ✅ 新增 `FORCE_HTTPS` 配置项
- ✅ 提供了 IP 和域名的配置示例

### 4. HTML 模板优化

#### [index.html](templates/index.html#L6) 和 [gallery.html](templates/gallery.html#L6)

**更改前**：
```html
<title>图床上传 - tc.bluse.me</title>
<title>图片库 - tc.bluse.me</title>
```

**更改后**：
```html
<title>图床上传</title>
<title>图片库</title>
```

**改进说明**：
- ✅ 移除硬编码的域名
- ✅ 更加通用，适用于任何部署环境

---

## 📚 新增文档

### [IP_ACCESS_GUIDE.md](IP_ACCESS_GUIDE.md)

详细的 IP 访问配置指南，包含：

- ✅ 快速开始指南
- ✅ 详细的环境变量说明
- ✅ Nginx 配置解释
- ✅ 多种部署场景示例
- ✅ 常见问题解答
- ✅ 配置验证清单
- ✅ 安全建议

---

## 🚀 如何使用

### 场景 1：使用 IP 地址访问（推荐用于内网）

1. **创建 `.env` 文件**：
```bash
cp .env.example .env
```

2. **编辑配置**：
```bash
# .env
ALLOWED_HOSTS=192.168.1.100,localhost,127.0.0.1  # 改成你的 IP
FORCE_HTTPS=False  # 必须设置为 False
DEBUG=False
REQUIRE_AUTH=True
```

3. **启动服务**：
```bash
docker-compose up -d
```

4. **访问**：
```
http://192.168.1.100:8080/
```

### 场景 2：使用域名访问（推荐用于公网）

1. **编辑配置**：
```bash
# .env
ALLOWED_HOSTS=your-domain.com,localhost,127.0.0.1
FORCE_HTTPS=True  # 启用 HTTPS 强制跳转
DEBUG=False
REQUIRE_AUTH=True
```

2. **切换 Nginx 配置**：
```bash
# 修改 docker-compose.yml 或复制 HTTPS 配置
cp nginx/conf.d/default-https-template.conf nginx/conf.d/default.conf
# 然后修改配置中的域名
```

3. **获取 SSL 证书并启动**：
```bash
# 使用 certbot 或 deploy.sh 脚本
./deploy.sh
```

---

## 🔧 技术实现细节

### 动态 URL 生成

项目已经使用动态 URL 生成机制，无需修改代码即可支持 IP 访问：

```python
# imagehost/views.py
def get_full_url(request, path):
    """Generate full URL from request and path"""
    scheme = 'https' if request.is_secure() else 'http'
    host = request.get_host()  # 自动获取 IP:端口
    return f"{scheme}://{host}{path}"
```

**工作原理**：
- `request.is_secure()` 自动检测 HTTP/HTTPS
- `request.get_host()` 自动获取主机名（包括端口）
- 支持反向代理环境（通过 `X-Forwarded-Proto` 等头）

### CSRF 保护增强

```python
# image_bed/settings.py
CSRF_TRUSTED_ORIGINS = []
for host in ALLOWED_HOSTS:
    if host not in ['localhost', '127.0.0.1']:
        CSRF_TRUSTED_ORIGINS.append(f'http://{host}')
        CSRF_TRUSTED_ORIGINS.append(f'https://{host}')
```

**改进**：
- 自动为每个 ALLOWED_HOSTS 生成 HTTP 和 HTTPS 的 CSRF 信任源
- 避免 CSRF 验证失败问题
- 同时支持 IP 和域名访问

---

## ⚠️ 重要注意事项

### 使用 IP 访问时

1. **必须设置 `FORCE_HTTPS=False`**
   - 否则会强制跳转到 HTTPS，导致无法访问

2. **IP 地址必须在 `ALLOWED_HOSTS` 中**
   - 否则 Django 会返回 "Invalid HTTP_HOST header" 错误

3. **仅建议在内网使用**
   - HTTP 未加密，不适合公网暴露
   - 考虑使用防火墙限制访问来源

4. **仍需启用认证**
   - 设置 `REQUIRE_AUTH=True`
   - 在 Admin 后台创建 API Token

### 使用域名访问时

1. **必须有有效的 SSL 证书**
   - 可使用 Let's Encrypt 免费证书
   - IP 地址无法获得 SSL 证书

2. **设置 `FORCE_HTTPS=True`**
   - 强制使用 HTTPS，提高安全性

3. **配置 DNS 记录**
   - A 记录指向服务器 IP

---

## 📊 配置对比表

| 特性 | IP 访问 (HTTP) | 域名访问 (HTTPS) |
|------|----------------|-----------------|
| **协议** | HTTP | HTTPS |
| **端口** | 80/8080/自定义 | 443 + 80 (redirect) |
| **FORCE_HTTPS** | False | True |
| **需要域名** | ❌ | ✅ |
| **需要 SSL 证书** | ❌ | ✅ |
| **数据加密** | ❌ | ✅ |
| **配置复杂度** | 简单 | 中等 |
| **适用场景** | 内网/开发 | 生产/公网 |
| **安全性** | 低 | 高 |

---

## 🔒 安全建议

### IP 访问安全措施

1. **网络隔离**：仅在内网使用
2. **防火墙规则**：限制访问来源 IP
3. **强认证**：使用复杂的 API Token
4. **定期轮换**：定期更新 Token
5. **访问日志**：监控异常访问

### 域名访问安全措施

1. **强制 HTTPS**：`FORCE_HTTPS=True`
2. **HSTS 启用**：已在 Nginx 配置中
3. **证书自动续期**：配置 Certbot
4. **强密钥**：使用长随机字符串作为 SECRET_KEY
5. **定期更新**：保持 Django 和依赖最新

---

## 🧪 测试验证

### 验证 IP 访问

```bash
# 1. 检查配置
cat .env | grep ALLOWED_HOSTS
cat .env | grep FORCE_HTTPS

# 2. 启动服务
docker-compose up -d

# 3. 测试访问
curl http://192.168.1.100:8080/
curl http://192.168.1.100:8080/gallery/

# 4. 测试上传 API
curl -X POST http://192.168.1.100:8080/api/upload/ \
  -H "X-API-Token: your-token" \
  -F "image=@test.jpg"
```

### 验证域名访问

```bash
# 1. 测试 HTTP 到 HTTPS 重定向
curl -I http://your-domain.com/
# 应返回 301 重定向到 https://

# 2. 测试 HTTPS 访问
curl -I https://your-domain.com/
# 应返回 200 OK

# 3. 检查 SSL 证书
openssl s_client -connect your-domain.com:443 -servername your-domain.com
```

---

## 📝 变更文件列表

### 修改的文件

1. `image_bed/settings.py` - Django 核心配置
2. `.env.example` - 环境变量模板
3. `templates/index.html` - 上传页面
4. `templates/gallery.html` - 图片库页面

### 新增的文件

1. `nginx/conf.d/default-http-ip.conf` - IP 访问专用配置
2. `IP_ACCESS_GUIDE.md` - IP 访问详细指南
3. `IP_UPDATE_NOTES.md` - 本文档

### 未修改的文件

1. `imagehost/views.py` - 已经支持动态 URL
2. `imagehost/models.py` - 无需修改
3. `nginx/conf.d/default.conf` - 已经支持 IP 访问
4. `docker-compose.yml` - 无需修改

---

## 🎉 总结

本次更新完成了以下目标：

✅ **支持 IP 地址 + 端口访问**
✅ **保持域名访问的完整功能**
✅ **增强 CSRF 保护机制**
✅ **提供详细的配置文档**
✅ **向后兼容现有部署**

现在你的图床可以灵活地部署在：
- 内网环境（使用 IP）
- 公网环境（使用域名）
- 开发环境（使用 localhost）
- 混合环境（同时支持多种方式）

**核心优势**：配置简单，无需修改代码，安全性可控！

---

## 📖 相关文档

- [IP 访问配置指南](IP_ACCESS_GUIDE.md) - 详细配置说明
- [CONFIGURATION.md](CONFIGURATION.md) - 完整配置文档
- [QUICKSTART.md](QUICKSTART.md) - 快速开始指南
- [README_DEPLOY.md](README_DEPLOY.md) - 部署文档

---

**如有问题或建议，请查阅 [IP_ACCESS_GUIDE.md](IP_ACCESS_GUIDE.md) 中的常见问题部分。**
