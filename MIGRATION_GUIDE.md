# 数据库迁移指南

本项目在现有版本基础上进行了重大更新，添加了用户认证和游客模式功能。以下是数据库迁移步骤。

## 新功能

1. **用户认证系统**
   - 邮箱注册/登录
   - 用户个人空间
   - 图片与用户关联

2. **游客模式**
   - 未登录用户可以上传图片
   - 游客上传的图片24小时后自动删除
   - 注册用户的图片永久保存

3. **模型变更**
   - `Image` 模型添加了以下字段：
     - `user`: 外键关联到 User 模型（可空，游客上传为 null）
     - `is_temporary`: 布尔值，标记是否为临时图片
     - `expires_at`: 日期时间，临时图片的过期时间

## 迁移步骤

### 方式一：全新部署（推荐）

如果您是首次部署或可以清空现有数据：

```bash
# 进入项目目录
cd /path/to/image-bed

# 删除现有数据库（如果有）
docker compose down
sudo rm -rf /data/image_bed/db/*

# 删除旧的迁移文件
rm -rf imagehost/migrations/00*.py

# 重新部署
sudo ./deploy.sh

# 系统会自动创建新的数据库结构
```

### 方式二：保留现有数据的迁移

如果您需要保留现有的图片数据：

```bash
# 1. 备份现有数据
sudo tar -czf /backup/image_bed_backup_$(date +%Y%m%d).tar.gz /data/image_bed

# 2. 进入容器
docker compose exec web bash

# 3. 创建迁移文件
python manage.py makemigrations imagehost

# 4. 查看迁移SQL（可选，用于检查）
python manage.py sqlmigrate imagehost 0002

# 5. 应用迁移
python manage.py migrate

# 6. 退出容器
exit

# 7. 重启服务
docker compose restart
```

### 方式三：手动数据库迁移（高级）

如果自动迁移失败，可以手动执行 SQL：

```bash
# 进入容器
docker compose exec web bash

# 打开 SQLite
python manage.py dbshell

# 执行以下 SQL 命令：
```

```sql
-- 添加新字段到 imagehost_image 表
ALTER TABLE imagehost_image ADD COLUMN user_id INTEGER NULL REFERENCES auth_user(id);
ALTER TABLE imagehost_image ADD COLUMN is_temporary BOOLEAN NOT NULL DEFAULT 0;
ALTER TABLE imagehost_image ADD COLUMN expires_at DATETIME NULL;

-- 创建索引
CREATE INDEX imagehost_image_user_id_idx ON imagehost_image (user_id);
CREATE INDEX imagehost_image_expires_at_idx ON imagehost_image (expires_at);

-- 退出
.quit
```

```bash
# 退出容器
exit

# 重启服务
docker compose restart
```

## 迁移后验证

1. **检查数据库结构**
   ```bash
   docker compose exec web python manage.py showmigrations
   ```

2. **测试上传功能**
   - 访问网站首页
   - 以游客身份上传一张图片
   - 验证图片可以正常访问

3. **测试用户注册**
   - 访问 `/register/` 注册新账户
   - 登录后上传图片
   - 访问个人中心查看上传的图片

4. **测试自动清理（可选）**
   ```bash
   # 手动运行清理命令（dry-run模式）
   docker compose exec web python manage.py cleanup_expired_images --dry-run
   ```

## 配置定时任务

为了让游客图片能够自动删除，需要配置 cron 任务：

```bash
# 运行配置脚本
sudo ./setup_cron.sh
```

或手动配置：

```bash
# 编辑 crontab
crontab -e

# 添加以下行（每小时运行一次清理任务）
0 * * * * cd /path/to/image-bed && docker compose exec -T web python manage.py cleanup_expired_images >> /var/log/image_bed_cleanup.log 2>&1
```

## 常见问题

### Q1: 迁移时出现 "no such table" 错误

**A:** 这通常是因为迁移顺序问题。解决方法：

```bash
docker compose exec web python manage.py migrate --fake-initial
docker compose exec web python manage.py migrate
```

### Q2: 现有图片没有关联用户怎么办？

**A:** 现有图片的 `user` 字段为 `NULL`，这是正常的。它们会被视为历史数据，不受游客模式影响，不会自动删除。

### Q3: 如何批量设置现有图片的所有者？

**A:** 如果需要，可以在 Django shell 中批量更新：

```bash
docker compose exec web python manage.py shell
```

```python
from django.contrib.auth.models import User
from imagehost.models import Image

# 创建一个默认管理员用户（如果不存在）
admin_user, created = User.objects.get_or_create(
    username='admin@example.com',
    email='admin@example.com'
)
if created:
    admin_user.set_password('change-this-password')
    admin_user.save()

# 将所有未关联的图片分配给管理员
Image.objects.filter(user__isnull=True).update(user=admin_user)

print("Done!")
```

### Q4: 如何临时禁用游客模式？

**A:** 编辑 `.env` 文件：

```bash
# 禁用游客上传
ALLOW_GUEST_UPLOAD=False

# 重启服务
docker compose restart
```

## 回滚方案

如果迁移后出现问题，可以回滚到之前的版本：

```bash
# 1. 停止服务
docker compose down

# 2. 恢复备份
sudo tar -xzf /backup/image_bed_backup_YYYYMMDD.tar.gz -C /

# 3. 还原代码
git checkout <previous-commit-hash>

# 4. 重新启动
docker compose up -d
```

## 技术支持

如遇到问题，请查看日志：

```bash
# 查看应用日志
docker compose logs web

# 查看 Nginx 日志
docker compose logs nginx

# 查看清理任务日志
tail -f /var/log/image_bed_cleanup.log
```

或在 GitHub 提交 Issue：https://github.com/cupid532/image-bed/issues
