# VPS Backup Tool v2.0

Công cụ backup VPS với monitoring băng thông và hỗ trợ screen session cho long-running backups.

## ✨ Tính năng

### 🔧 Tự động kiểm tra và cài đặt
- ✅ Kiểm tra Python version (≥3.6)
- ✅ Kiểm tra và cài đặt các gói hệ thống cần thiết (rsync, ssh, screen)
- ✅ Tự động cài đặt Python packages
- ✅ Kiểm tra cấu hình và kết nối SSH
- ✅ Kiểm tra đường dẫn nguồn và đích

### 📦 Các loại backup
- **Quick Backup**: Backup nhanh để test, chạy trong screen session
- **Full Backup**: Backup đầy đủ cho production
- **Long-term Backup**: Backup dài hạn (nhiều ngày) với screen session
- **Bandwidth Monitoring Only**: Chỉ monitor băng thông

### 🖥️ Quản lý Screen Session
- 📋 Liệt kê các session đang chạy
- 🔗 Attach vào session
- ⏹️ Dừng session
- 🧹 Cleanup các session đã chết

### 📊 Monitoring băng thông
- Real-time monitoring tất cả network interfaces
- Hiển thị bandwidth download/upload
- Phát hiện interface chính đang active
- Cảnh báo traffic cao

## 🚀 Cài đặt và Sử dụng

### 1. Khởi động ứng dụng

```bash
python app.py
```

File `app.py` sẽ tự động:
- Kiểm tra Python version
- Kiểm tra và cài đặt các gói hệ thống cần thiết
- Cài đặt Python packages
- Tạo file cấu hình từ template (nếu chưa có)
- Kiểm tra kết nối SSH
- Khởi động giao diện menu

### 2. Cấu hình

Lần đầu chạy, file `configs/config.yaml` sẽ được tạo từ template. Chỉnh sửa các thông số:

```yaml
# SSH Connection
ssh_user: root
ssh_host: YOUR_VPS_IP
ssh_port: 22
ssh_key: ~/.ssh/id_rsa

# Backup Paths
remote_root: /home
local_root: ./backup_data

# Performance
threads: 8
bwlimit: 0  # KB/s (0 = unlimited)
```

### 3. Menu chính

```
📦 BACKUP OPTIONS:
  1) 🚀 Quick Backup (với screen session)
  2) 💾 Full Backup (production)
  3) 🕐 Long-term Backup (multi-day)
  4) 📊 Bandwidth Monitoring Only

🖥️ SESSION MANAGEMENT:
  5) 📋 List Active Sessions
  6) 🔗 Attach to Session
  7) ⏹️ Stop Session
  8) 🧹 Cleanup Dead Sessions

🔧 SETUP & TESTING:
  9) ⚙️ Show Configuration
 10) 🔍 Test SSH Connection
 11) 📡 Test Network Interfaces
 12) 🖥️ System Information
 13) 📋 View Remote Backup Logs
 14) 🔍 Debug Remote Backup Status
```

## 📁 Cấu trúc dự án

```
backup/
├── app.py                          # File khởi động chính
├── configs/
│   ├── config.yaml.template        # Template cấu hình
│   └── config.yaml                 # Cấu hình thực tế
├── src/
│   ├── core/                       # Core functionality
│   │   ├── config.py               # Quản lý cấu hình
│   │   ├── ssh.py                  # SSH connection & network monitoring
│   │   ├── backup.py               # Backup engine
│   │   └── backup_runner.py        # Backup runner cho screen sessions
│   ├── utils/                      # Utilities
│   │   ├── screen.py               # Screen session management
│   │   └── formatting.py           # Format output & UI helpers
│   └── ui/
│       └── main_menu.py            # Main menu interface
├── scripts/                        # Utility scripts
├── backup_data/                    # Local backup destination
├── tmp/                           # Temporary files
└── logs/                          # Log files
```

## 🔧 Yêu cầu hệ thống

### Python
- Python 3.6 trở lên
- Packages: PyYAML, rich (tự động cài đặt)

### System Commands
- `rsync` - Sync files
- `ssh` - SSH connection  
- `screen` - Session management

### Hệ điều hành hỗ trợ
- ✅ Linux (Ubuntu, CentOS, RHEL, etc.)
- ✅ macOS
- ⚠️ Windows (hạn chế, cần WSL)

### Cài đặt tự động cho:
- **macOS**: Homebrew
- **Ubuntu/Debian**: apt
- **CentOS/RHEL**: yum/dnf

## 🛠️ Sử dụng nâng cao

### 1. Backup với Screen Session

Long-running backups tự động chạy trong screen session:

```bash
# Backup sẽ chạy trong screen session
# Có thể detach và reattach sau
screen -r backup_longterm_1
```

### 2. Monitoring băng thông

```bash
# Chỉ chạy monitoring
python app.py
# Chọn option 4) Bandwidth Monitoring Only
```

### 3. Kiểm tra kết nối

```bash
# Test SSH connection
python app.py
# Chọn option 10) Test SSH Connection

# Test network interfaces
python app.py  
# Chọn option 11) Test Network Interfaces
```

### 4. Quản lý Sessions

```bash
# List sessions
screen -ls

# Attach to session
screen -r backup_full_1

# Detach from session
# Trong session: Ctrl+A then D
```

## 📊 Output Examples

### Bandwidth Monitoring
```
[14:23:45] 📊 Total: ⬇️ 45.2 MB/s | ⬆️ 12.1 MB/s (2/4 active)
         Active interfaces:
           eth0: ⬇️ 42.1 MB/s | ⬆️ 11.8 MB/s
           eth1: ⬇️ 3.1 MB/s | ⬆️ 0.3 MB/s
```

### Backup Progress
```
🚀 Starting full backup...
📂 Remote: root@192.168.1.100:/home
📁 Local: ./backup_data
🧵 Threads: 8
═══════════════════════════════════════

📋 Building file list from remote server...
🔀 Creating file chunks for parallel processing...
🔄 Starting rsync with 8 chunks...

Chunk 1: ✅ OK
Chunk 2: ✅ OK
Chunk 3: ❌ FAILED
...

✅ Backup completed successfully!
📊 Results: 7/8 chunks successful
⏱️ Duration: 2h 34m 12s
```

## 🚨 Xử lý lỗi

### SSH Connection Issues
```bash
# Kiểm tra SSH key
ls -la ~/.ssh/
chmod 600 ~/.ssh/id_rsa

# Test manual SSH
ssh -i ~/.ssh/id_rsa user@host
```

### Permission Issues
```bash
# Fix permissions
chmod +x app.py
sudo chown -R $USER:$USER ./backup_data
```

### Screen Session Issues
```bash
# List all sessions
screen -ls

# Kill dead sessions
screen -wipe

# Kill specific session
screen -S session_name -X quit
```

## 💡 Tips & Best Practices

1. **Long backups**: Luôn sử dụng screen session cho backup dài
2. **Bandwidth limit**: Đặt `bwlimit` để tránh làm chậm mạng
3. **Threads**: Điều chỉnh số threads dựa trên CPU và network
4. **Monitoring**: Theo dõi bandwidth để tối ưu hiệu suất
5. **Logs**: Kiểm tra log files trong thư mục `logs/`

## 🔄 Migration từ version cũ

Nếu bạn đang sử dụng version cũ:

1. Backup data và config cũ
2. Chạy `python app.py` để setup version mới
3. Copy settings từ config cũ sang `configs/config.yaml`
4. Test connection trước khi chạy backup

## 📞 Hỗ trợ

- Kiểm tra logs trong thư mục `logs/`
- Chạy system check: Option 12 trong menu
- Test từng component: SSH, Network interfaces
- GitHub Issues: [Link to repository]

## 📜 License

MIT License - See LICENSE file for details.

## 🔍 Debugging & Monitoring trên VPS

### Xem log backup từ xa
Khi chạy backup trên VPS, bạn có thể xem log từ máy local:

1. **Từ menu chính**: Chọn option `13) 📋 View Remote Backup Logs`
2. **Script nhanh**:
   ```bash
   ./view_remote_logs.sh
   # hoặc với config file khác
   ./view_remote_logs.sh configs/production.yaml
   ```

### Debug trạng thái backup từ xa
Để kiểm tra toàn diện trạng thái backup trên VPS:

1. **Từ menu chính**: Chọn option `14) 🔍 Debug Remote Backup Status`
2. **Script nhanh**:
   ```bash
   ./debug_remote_backup.sh
   ```

### Debug script sẽ kiểm tra:
- ✅ System info (OS, uptime, load, memory, disk)
- ✅ Screen sessions đang chạy
- ✅ Python/rsync processes
- ✅ Backup directory status
- ✅ Log files và errors
- ✅ Network interfaces
- ✅ Top processes (CPU/Memory)
- ✅ Chunk files status
- ✅ Screen session output capture

### Khi Long-term backup bị dừng sớm:
1. Chạy `./debug_remote_backup.sh` để kiểm tra:
   - Memory usage (có thể bị out of memory)
   - Disk space (có thể đầy ổ cứng)
   - Screen session còn sống không
   - Có process backup nào đang chạy không
   - Log file có error gì không

2. Xem log chi tiết:
   ```bash
   ./view_remote_logs.sh
   ```

3. Nếu cần, attach vào screen session:
   ```bash
   ssh user@vps
   screen -ls  # xem sessions
   screen -r session_name  # attach vào session
   ```
