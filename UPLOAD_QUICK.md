# 快速上传到 GitHub

## 🎯 简明步骤

### 方式一：使用自动脚本（推荐）

```bash
cd /Users/bluse/Desktop/bluse_code/image_bed
./upload_to_github.sh
```

按提示操作即可。

---

### 方式二：手动执行

#### 1. 在 GitHub 创建仓库

访问 https://github.com/new

- **Repository name**: `image-bed`
- **Description**: `一个功能完整的自托管图床系统`
- **Public** ✓
- **不要** 勾选 README, .gitignore, license

点击 **Create repository**

#### 2. 推送代码

```bash
cd /Users/bluse/Desktop/bluse_code/image_bed

# 添加远程仓库
git remote add origin https://github.com/cupid532/image-bed.git

# 推送代码
git push -u origin main
```

#### 3. 输入凭证

- **Username**: `cupid532`
- **Password**: 使用 Personal Access Token

**获取 Token:**
1. 访问 https://github.com/settings/tokens
2. 点击 `Generate new token (classic)`
3. 勾选 `repo` 权限
4. 生成并复制 Token

#### 4. 完成！

访问 https://github.com/cupid532/image-bed

---

## 📝 详细文档

查看 [GITHUB_UPLOAD_GUIDE.md](GITHUB_UPLOAD_GUIDE.md) 获取完整说明。

---

## ⚡ 一键命令

```bash
cd /Users/bluse/Desktop/bluse_code/image_bed && \
git remote add origin https://github.com/cupid532/image-bed.git && \
git push -u origin main
```

---

## ❓ 常见问题

**Q: 推送失败怎么办？**
A: 使用 Personal Access Token 作为密码

**Q: 已存在 origin？**
A: 运行 `git remote remove origin` 后重试

**Q: 需要修改仓库地址？**
A: 运行 `git remote set-url origin 新地址`

---

## ✅ 验证

推送成功后，检查：
- https://github.com/cupid532/image-bed 能访问
- README 显示正常
- 36+ 个文件已上传
