# 图床项目卸载指南

本文档说明如何完全卸载已部署的图床项目。

## 📋 当前运行状态

根据你的服务器状态：
```
CONTAINER ID   IMAGE            COMMAND                  CREATED         STATUS       PORTS                    NAMES
0a38243e7147   image-bed-web    "gunicorn --bind 0.0…"   3 minutes ago   Up 3 minutes 0.0.0.0:8000->8000/tcp   image_bed
```

---

## 🗑️ 完全卸载步骤

### 方法 1：完全清理（推荐）

这会删除所有容器、镜像、数据和项目文件。

```bash
# SSH 连接到服务器后执行

# 1. 进入项目目录（根据你的实际路径）
cd ~/image-bed  # 或者你部署的实际路径

# 2. 停止并删除容器
docker-compose down

# 3. 删除容器（如果 docker-compose 不可用）
docker stop image_bed
docker rm image_bed

# 4. 删除镜像
docker rmi image-bed-web
docker rmi image-bed-nginx  # 如果有 nginx 容器

# 5. 删除数据卷（可选，会删除所有上传的图片）
sudo rm -rf /data/image_bed

# 6. 删除项目文件
cd ~
rm -rf image-bed

# 7. 清理未使用的 Docker 资源
docker system prune -a
```

---

### 方法 2：仅停止服务（保留数据）

如果你想保留上传的图片和数据库，只停止服务：

```bash
# 1. 停止容器
docker stop image_bed

# 2. 删除容器（但保留镜像和数据）
docker rm image_bed
```

**保留的内容**：
- ✅ 上传的图片（在 `/data/image_bed/images/`）
- ✅ 数据库文件（在 `/data/image_bed/db/`）
- ✅ Docker 镜像（可以快速重新启动）

---

### 方法 3：使用管理脚本（如果可用）

如果你使用了项目的 `manage.sh` 脚本：

```bash
cd ~/image-bed
./manage.sh stop    # 停止服务
./manage.sh clean   # 清理容器
```

---

## 📁 需要清理的目录和文件

根据你的部署方式，可能需要清理以下位置：

### 服务器上的项目文件
```bash
# 常见的部署位置
~/image-bed/
/opt/image-bed/
/var/www/image-bed/
/root/image-bed/
```

### 数据目录
```bash
# 图片和数据库存储位置
/data/image_bed/images/     # 上传的图片
/data/image_bed/db/         # SQLite 数据库
/data/image_bed/certbot/    # SSL 证书（如果使用）
```

### Docker 相关
```bash
# 容器
docker ps -a | grep image_bed

# 镜像
docker images | grep image-bed

# 卷
docker volume ls | grep image_bed
```

---

## 🔍 验证卸载是否完成

执行以下命令检查是否已完全卸载：

```bash
# 1. 检查运行的容器
docker ps | grep image

# 2. 检查所有容器（包括停止的）
docker ps -a | grep image

# 3. 检查镜像
docker images | grep image-bed

# 4. 检查数据目录
ls -la /data/image_bed

# 5. 检查项目目录
ls -la ~/image-bed

# 6. 检查端口占用
netstat -tulpn | grep 8000
# 或
ss -tulpn | grep 8000
```

**如果所有命令都没有输出，说明卸载成功！**

---

## ⚠️ 注意事项

### 备份重要数据

在执行完全卸载之前，请确保备份：

1. **上传的图片**：
```bash
# 备份到本地
scp -r root@your-server:/data/image_bed/images/ ./backup/

# 或压缩后下载
ssh root@your-server "tar -czf /tmp/images_backup.tar.gz /data/image_bed/images"
scp root@your-server:/tmp/images_backup.tar.gz ./
```

2. **数据库**：
```bash
# 备份数据库文件
scp root@your-server:/data/image_bed/db/db.sqlite3 ./backup/
```

3. **配置文件**：
```bash
# 备份 .env 配置
scp root@your-server:~/image-bed/.env ./backup/
```

### 数据无法恢复

一旦执行以下命令，数据将**无法恢复**：
```bash
sudo rm -rf /data/image_bed  # ⚠️ 危险操作！
```

---

## 🔄 重新部署

如果你想使用更新后的版本重新部署：

### 步骤 1：卸载旧版本

```bash
# 停止并删除旧容器
docker stop image_bed
docker rm image_bed

# 删除旧镜像
docker rmi image-bed-web

# 删除旧项目文件（保留数据）
cd ~
rm -rf image-bed
```

### 步骤 2：部署新版本

```bash
# 1. 克隆最新代码
git clone https://github.com/cupid532/image-bed.git
cd image-bed

# 2. 配置环境变量
cp .env.example .env
nano .env

# 重要配置：
# ALLOWED_HOSTS=你的IP或域名,localhost,127.0.0.1
# FORCE_HTTPS=False  # 如果使用 IP 访问

# 3. 启动服务
docker-compose up -d

# 或使用管理脚本
./manage.sh start
```

### 步骤 3：恢复数据（如果需要）

```bash
# 恢复图片
sudo cp -r ./backup/images/* /data/image_bed/images/

# 恢复数据库
sudo cp ./backup/db.sqlite3 /data/image_bed/db/

# 修改权限
sudo chown -R 1000:1000 /data/image_bed
```

---

## 📝 快速命令参考

### 仅停止服务
```bash
docker stop image_bed
```

### 停止并删除容器
```bash
docker stop image_bed && docker rm image_bed
```

### 完全清理（保留数据）
```bash
docker stop image_bed
docker rm image_bed
docker rmi image-bed-web
rm -rf ~/image-bed
```

### 完全清理（包括数据）⚠️
```bash
docker stop image_bed
docker rm image_bed
docker rmi image-bed-web
sudo rm -rf /data/image_bed
rm -rf ~/image-bed
```

---

## 🛠️ 故障排查

### 容器无法停止

```bash
# 强制停止
docker kill image_bed

# 强制删除
docker rm -f image_bed
```

### 镜像无法删除

```bash
# 检查是否有其他容器使用该镜像
docker ps -a | grep image-bed

# 强制删除镜像
docker rmi -f image-bed-web
```

### 数据目录无法删除

```bash
# 检查是否有进程占用
lsof /data/image_bed

# 使用 sudo 删除
sudo rm -rf /data/image_bed

# 如果提示权限不足，检查文件权限
ls -la /data/
```

### 端口仍被占用

```bash
# 查找占用端口的进程
lsof -i :8000
# 或
netstat -tulpn | grep 8000

# 终止进程
kill -9 <PID>
```

---

## 📞 需要帮助？

如果遇到卸载问题，可以：

1. 检查 Docker 日志：
```bash
docker logs image_bed
```

2. 检查系统日志：
```bash
journalctl -u docker -f
```

3. 查看 GitHub Issues：
https://github.com/cupid532/image-bed/issues

---

## 总结

**最简单的卸载方式（根据你当前的情况）**：

```bash
# SSH 到服务器后执行
docker stop image_bed
docker rm image_bed
docker rmi image-bed-web
rm -rf ~/image-bed  # 或你的实际路径

# 如果要删除数据（可选）
sudo rm -rf /data/image_bed
```

**如果想保留数据重新部署**：

```bash
# 只删除容器和代码
docker stop image_bed && docker rm image_bed
rm -rf ~/image-bed

# 重新克隆最新代码
git clone https://github.com/cupid532/image-bed.git
cd image-bed

# 配置并启动
cp .env.example .env
nano .env  # 配置 ALLOWED_HOSTS 和 FORCE_HTTPS
docker-compose up -d
```

数据会自动使用 `/data/image_bed` 中的旧数据！
