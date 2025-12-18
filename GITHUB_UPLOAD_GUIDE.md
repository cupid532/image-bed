# GitHub 上传指引

## ✅ 本地准备已完成

你的项目已经准备好上传到 GitHub！

**已完成的步骤：**
- ✅ Git 仓库已初始化
- ✅ 所有文件已添加
- ✅ 首次提交已创建
- ✅ LICENSE 文件已创建
- ✅ README 文件已优化

---

## 📝 第一步：在 GitHub 创建仓库

### 方法 1: 使用网页创建（推荐）

1. **访问 GitHub**
   - 打开浏览器，访问 https://github.com

2. **登录账号**
   - 使用你的账号 `cupid532` 登录

3. **创建新仓库**
   - 点击右上角的 `+` 号
   - 选择 `New repository`

4. **填写仓库信息**
   ```
   Repository name: image-bed
   Description: 一个功能完整的自托管图床系统 / A full-featured self-hosted image hosting system
   Public: ✓ (选择公开)

   ⚠️ 重要：不要勾选以下选项
   ❌ Add a README file
   ❌ Add .gitignore
   ❌ Choose a license

   (因为我们本地已经有这些文件了)
   ```

5. **点击 Create repository**

### 方法 2: 使用 GitHub CLI（如果已安装）

```bash
gh repo create image-bed --public --description "一个功能完整的自托管图床系统"
```

---

## 🚀 第二步：推送代码到 GitHub

仓库创建后，GitHub 会显示一些命令。**不要使用那些命令**，使用下面的命令：

### 推送到 GitHub

```bash
cd /Users/bluse/Desktop/bluse_code/image_bed

# 添加远程仓库
git remote add origin https://github.com/cupid532/image-bed.git

# 推送代码（第一次推送）
git push -u origin main
```

### 如果提示需要认证

**使用 Personal Access Token（推荐）:**

1. **生成 Token**
   - 访问 https://github.com/settings/tokens
   - 点击 `Generate new token` → `Generate new token (classic)`
   - Note: 填写 `image-bed upload`
   - Expiration: 选择 `No expiration` 或自定义
   - 勾选权限: `repo` (完整的仓库权限)
   - 点击 `Generate token`
   - **立即复制 Token（只显示一次）**

2. **使用 Token 推送**
   ```bash
   # 推送时，用户名输入: cupid532
   # 密码输入: 你刚才复制的 Token
   git push -u origin main
   ```

3. **保存凭证（可选）**
   ```bash
   # 让 Git 记住凭证，下次不用再输入
   git config --global credential.helper store
   ```

**或者使用 SSH（如果已配置）:**

```bash
# 改用 SSH 地址
git remote set-url origin git@github.com:cupid532/image-bed.git
git push -u origin main
```

---

## ✅ 第三步：验证上传成功

1. **访问仓库页面**
   ```
   https://github.com/cupid532/image-bed
   ```

2. **检查内容**
   - 应该能看到所有文件
   - README 显示正常
   - 36 个文件已提交

3. **设置 README**
   - 如果 README_GITHUB.md 显示更好，可以重命名：
   ```bash
   mv README.md README_DEPLOY.md
   mv README_GITHUB.md README.md
   git add .
   git commit -m "docs: use GitHub-optimized README"
   git push
   ```

---

## 🎨 第四步：优化仓库（可选）

### 添加 Topics（标签）

1. 访问你的仓库页面
2. 点击右侧的 ⚙️ Settings
3. 在 Topics 输入框添加标签：
   ```
   django, image-hosting, docker, nginx, python, self-hosted,
   image-upload, file-hosting, image-bed
   ```

### 添加项目描述

在仓库首页，点击 About 旁边的 ⚙️，添加：
- **Description**: `一个功能完整的自托管图床系统 / A full-featured self-hosted image hosting system`
- **Website**: 你的演示网站（如果有）
- **Topics**: （同上）

### 创建 Release（可选）

```bash
# 创建标签
git tag -a v1.0.0 -m "First stable release"
git push origin v1.0.0
```

然后在 GitHub 页面：
1. 点击 `Releases`
2. 点击 `Create a new release`
3. 选择标签 `v1.0.0`
4. 填写发布说明

---

## 📋 完整命令清单

如果需要重新执行，这是完整的命令：

```bash
# 1. 进入项目目录
cd /Users/bluse/Desktop/bluse_code/image_bed

# 2. 添加远程仓库（只需执行一次）
git remote add origin https://github.com/cupid532/image-bed.git

# 3. 推送代码
git push -u origin main

# 4. 后续推送（修改代码后）
git add .
git commit -m "your commit message"
git push
```

---

## 🔧 常见问题

### 问题 1: 推送失败 - "remote origin already exists"

```bash
# 删除现有的 origin
git remote remove origin

# 重新添加
git remote add origin https://github.com/cupid532/image-bed.git
```

### 问题 2: 认证失败

使用 Personal Access Token:
1. 访问 https://github.com/settings/tokens
2. 生成新的 Token
3. 推送时用 Token 作为密码

### 问题 3: 推送被拒绝 - "updates were rejected"

```bash
# 强制推送（仅在确定本地代码正确时使用）
git push -u origin main --force
```

### 问题 4: 想修改提交信息

```bash
# 修改最后一次提交
git commit --amend -m "new commit message"
git push --force
```

---

## 📚 后续操作

### 更新代码

```bash
# 1. 修改代码
# 2. 查看修改
git status
git diff

# 3. 添加修改
git add .

# 4. 提交
git commit -m "feat: add new feature"

# 5. 推送
git push
```

### 查看历史

```bash
# 查看提交历史
git log --oneline

# 查看远程仓库
git remote -v
```

### 分支操作

```bash
# 创建新分支
git checkout -b feature/new-feature

# 推送分支
git push -u origin feature/new-feature
```

---

## 🎯 快速命令（复制粘贴即可使用）

### 首次推送

```bash
cd /Users/bluse/Desktop/bluse_code/image_bed && \
git remote add origin https://github.com/cupid532/image-bed.git && \
git push -u origin main
```

### 优化 README（可选）

```bash
cd /Users/bluse/Desktop/bluse_code/image_bed && \
mv README.md README_DEPLOY.md && \
mv README_GITHUB.md README.md && \
git add . && \
git commit -m "docs: use GitHub-optimized README" && \
git push
```

---

## ✅ 检查清单

推送完成后，确认：

- [ ] 访问 https://github.com/cupid532/image-bed 能看到仓库
- [ ] README 显示正常
- [ ] 所有文件都已上传（36 个文件）
- [ ] LICENSE 文件存在
- [ ] .gitignore 工作正常（.env 等敏感文件未上传）
- [ ] 提交历史清晰
- [ ] 仓库描述和标签已设置

---

## 🌟 分享你的项目

仓库创建后，你可以：

1. **分享链接**
   ```
   https://github.com/cupid532/image-bed
   ```

2. **添加 Badge**
   在 README 中已包含各种 Badge

3. **提交到 Awesome 列表**
   - awesome-selfhosted
   - awesome-django

4. **社交媒体分享**
   - Twitter
   - Reddit (r/selfhosted, r/django)
   - V2EX
   - 知乎

---

## 📞 需要帮助？

如果遇到问题：

1. 查看 Git 状态: `git status`
2. 查看远程仓库: `git remote -v`
3. 查看提交历史: `git log --oneline`

---

**准备好了吗？执行上面的命令开始推送吧！** 🚀
