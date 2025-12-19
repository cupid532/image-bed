# 🎉 新功能说明

## 版本 2.0 更新内容

本次更新为图床系统添加了完整的用户认证功能和游客模式，让您的图床更加灵活和强大！

---

## ✨ 主要新功能

### 1. 用户认证系统

#### 📧 邮箱注册/登录
- 使用邮箱地址注册账号
- 密码强度验证（至少8位，包含字母和数字）
- 记住我功能（可选2周免登录）
- 现代化的登录/注册界面

#### 👤 个人中心
- 查看上传历史
- 统计信息：总图片数、总浏览量、存储空间
- 快速访问最近上传的图片

#### 🔒 图片永久保存
- 注册用户上传的图片永久保存
- 不受时间限制
- 可随时管理自己的图片

### 2. 游客模式

#### ⏰ 24小时临时存储
- 无需注册即可上传图片
- 游客上传的图片保留24小时
- 到期自动删除，节省存储空间

#### 🎯 使用场景
- 临时分享图片
- 测试图床功能
- 不想注册的用户

#### 💡 智能提示
- 首页明显提示游客模式限制
- 鼓励用户注册以获得永久存储

### 3. 自动清理机制

#### 🤖 定时任务
- 使用 Django Management Command
- 通过 Linux Cron 定时执行
- 每小时自动检查并删除过期图片

#### 📊 清理日志
- 详细记录清理过程
- 统计删除的文件和记录数
- 便于监控和排查问题

#### 🛡️ 安全性
- 仅清理游客上传的过期图片
- 注册用户的图片永不删除
- 包含错误处理机制

### 4. 域名配置优化

#### 🌐 主站域名 (SITE_DOMAIN)
- 配置网站主域名
- 用于生成页面链接
- 支持 HTTPS

#### 📷 图片CDN域名 (IMAGE_DOMAIN)
- 可选配置独立的图片域名
- 实现图片资源分离
- 提升加载速度
- 未配置时使用主站域名

#### ⚙️ 简化配置
- 所有配置在 `.env` 文件中
- 无需修改代码
- 支持动态切换

### 5. UI/UX 改进

#### 🎨 现代化界面
- 渐变背景设计
- 流畅的动画效果
- 响应式布局
- 移动端友好

#### 🧭 导航栏
- 显示登录状态
- 快速访问各功能
- 用户头像和邮箱显示

#### 📱 用户体验优化
- 更好的错误提示
- 加载动画
- 一键复制链接
- 实时上传进度

---

## 🚀 快速开始

### 新部署（推荐）

```bash
# 1. 克隆/更新代码
git clone https://github.com/cupid532/image-bed.git
cd image-bed

# 2. 配置环境变量
cp .env.example .env
nano .env  # 编辑配置

# 重要配置项：
# ALLOWED_HOSTS=your-domain.com
# ALLOW_GUEST_UPLOAD=True  # 启用游客模式
# SITE_DOMAIN=your-domain.com  # 可选
# IMAGE_DOMAIN=img.your-domain.com  # 可选

# 3. 一键部署
chmod +x deploy.sh setup_cron.sh
sudo ./deploy.sh

# 4. 配置定时清理任务
sudo ./setup_cron.sh

# 5. 访问网站
# http://your-domain.com
```

### 从旧版本升级

请查看 [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md) 获取详细的升级步骤。

---

## 📋 功能对比

| 功能 | 游客模式 | 注册用户 |
|------|---------|---------|
| 上传图片 | ✅ | ✅ |
| 图片保存时间 | 24小时 | 永久 |
| 查看上传历史 | ❌ | ✅ |
| 浏览统计 | ❌ | ✅ |
| 个人中心 | ❌ | ✅ |
| 批量管理 | ❌ | ✅ |
| 存储配额 | 无限制 | 无限制 |

---

## ⚙️ 配置选项

### .env 文件新增配置

```bash
# 认证设置
REQUIRE_AUTH=False           # API上传是否需要Token（建议False）
ALLOW_GUEST_UPLOAD=True      # 是否允许游客上传

# 域名设置
SITE_DOMAIN=                 # 主站域名（可选）
IMAGE_DOMAIN=                # 图片CDN域名（可选）
```

### 建议配置

#### 场景一：个人使用
```bash
ALLOW_GUEST_UPLOAD=False     # 禁用游客模式
REQUIRE_AUTH=False           # 不需要Token
```

#### 场景二：团队共享
```bash
ALLOW_GUEST_UPLOAD=True      # 允许游客试用
REQUIRE_AUTH=False           # 不需要Token（用户系统已足够）
```

#### 场景三：公开服务
```bash
ALLOW_GUEST_UPLOAD=True      # 允许游客上传
REQUIRE_AUTH=False           # 不需要Token
# 建议添加验证码或频率限制（未来版本）
```

---

## 🔧 管理命令

### 清理过期图片

```bash
# 查看会删除哪些图片（不实际删除）
docker compose exec web python manage.py cleanup_expired_images --dry-run

# 手动执行清理
docker compose exec web python manage.py cleanup_expired_images

# 查看清理日志
tail -f /var/log/image_bed_cleanup.log
```

### 用户管理

```bash
# 创建超级管理员
docker compose exec web python manage.py createsuperuser

# 访问管理后台
# http://your-domain.com/admin/
```

---

## 📊 API 变更

### 上传接口

**新增功能：**
- 自动检测用户登录状态
- 游客上传自动设置24小时过期
- 返回结果中包含是否为临时图片的提示

**请求示例：**

```bash
# 游客上传（无需token，24小时后删除）
curl -X POST https://your-domain.com/api/upload/ \
  -F "images=@image.jpg"

# 注册用户上传（通过Cookie自动认证，永久保存）
curl -X POST https://your-domain.com/api/upload/ \
  -H "Cookie: sessionid=xxx" \
  -F "images=@image.jpg"
```

**响应示例：**

```json
{
  "results": [
    {
      "filename": "image.jpg",
      "url": "https://your-domain.com/i/20250101/abc123.jpg",
      "size": 123.45,
      "dimensions": "1920x1080",
      "duplicate": false
    }
  ]
}
```

---

## 🛠️ 故障排查

### 游客上传的图片没有被删除

1. 检查cron任务是否正常运行：
   ```bash
   crontab -l | grep cleanup
   ```

2. 手动运行清理命令：
   ```bash
   docker compose exec web python manage.py cleanup_expired_images
   ```

3. 查看日志：
   ```bash
   tail -f /var/log/image_bed_cleanup.log
   ```

### 用户注册后无法登录

1. 检查数据库：
   ```bash
   docker compose exec web python manage.py shell
   ```
   ```python
   from django.contrib.auth.models import User
   User.objects.all()
   ```

2. 清除浏览器Cookie后重试

3. 检查ALLOWED_HOSTS配置是否正确

### 图片URL域名不正确

1. 检查 `.env` 配置：
   ```bash
   SITE_DOMAIN=your-domain.com
   IMAGE_DOMAIN=img.your-domain.com
   ```

2. 重启服务：
   ```bash
   docker compose restart
   ```

---

## 🔒 安全建议

1. **使用HTTPS**
   ```bash
   FORCE_HTTPS=True
   ```

2. **强密码策略**
   - 系统已内置密码验证
   - 至少8位，包含字母和数字

3. **定期备份**
   ```bash
   # 备份脚本示例
   #!/bin/bash
   DATE=$(date +%Y%m%d)
   tar -czf /backup/image_bed_$DATE.tar.gz /data/image_bed
   ```

4. **监控日志**
   ```bash
   # 定期检查异常
   docker compose logs web | grep ERROR
   ```

---

## 📈 性能优化

1. **使用独立图片域名**
   - 配置 `IMAGE_DOMAIN`
   - 启用CDN加速
   - 减少主站负载

2. **清理频率调整**
   ```bash
   # 每6小时运行一次（减少I/O）
   0 */6 * * * ...cleanup_expired_images...
   ```

3. **数据库优化**
   ```bash
   # 定期清理数据库
   docker compose exec web python manage.py clearsessions
   ```

---

## 🎯 未来计划

- [ ] 邮箱验证
- [ ] 找回密码功能
- [ ] 用户上传配额管理
- [ ] 图片标签和分类
- [ ] 批量操作
- [ ] API密钥管理
- [ ] 访问统计图表
- [ ] 防刷机制（验证码/频率限制）
- [ ] 多语言支持
- [ ] 主题切换

---

## 📞 技术支持

- **GitHub Issues**: https://github.com/cupid532/image-bed/issues
- **文档**:
  - [部署指南](README_DEPLOY.md)
  - [迁移指南](MIGRATION_GUIDE.md)
  - [配置说明](CONFIGURATION.md)
- **更新日志**: [CHANGELOG.md](CHANGELOG.md)

---

## 🙏 致谢

感谢所有使用本项目的用户，您的反馈让这个项目变得更好！

如果觉得有用，请给个 ⭐️ Star 支持一下！

---

**Made with ❤️ by [cupid532](https://github.com/cupid532)**
