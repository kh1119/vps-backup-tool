# Tạo GitHub Repository

## Bước 1: Tạo repo trên GitHub.com

1. Đi đến https://github.com/new
2. Repository name: `vps-backup-tool`
3. Description: `VPS Backup Tool with Real-time Bandwidth Monitoring - Parallel rsync backup with monitoring capabilities`
4. Chọn **Public** (hoặc Private nếu muốn)
5. **KHÔNG** check "Add a README file" (vì chúng ta đã có)
6. **KHÔNG** check "Add .gitignore" (vì chúng ta đã có)
7. **KHÔNG** check "Choose a license" (vì chúng ta đã có)
8. Click **Create repository**

## Bước 2: Push code lên GitHub

```bash
# Thêm GitHub remote (thay 'your-username' bằng username GitHub của bạn)
git remote add origin https://github.com/your-username/vps-backup-tool.git

# Push main branch
git push -u origin main

# Push tags
git push --tags
```

## Bước 3: Cập nhật README

Sau khi tạo repo, cập nhật link clone trong README.md:

```bash
git clone https://github.com/your-username/vps-backup-tool.git
```

## Bước 4: Optional - Tạo GitHub Release

1. Đi đến repository trên GitHub
2. Click **Releases** 
3. Click **Create a new release**
4. Tag version: `v1.0.0`
5. Release title: `VPS Backup Tool v1.0.0`
6. Description: Copy nội dung từ CHANGELOG.md
7. Click **Publish release**

## Commands summary:

```bash
# Tạo repo và push
git remote add origin https://github.com/your-username/vps-backup-tool.git
git push -u origin main
git push --tags

# Kiểm tra
git remote -v
git branch -a
git tag
```
