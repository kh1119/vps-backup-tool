# VPS Backup Tool với Bandwidth Monitoring

Tool backup dữ liệu từ VPS với tính năng monitor băng thông real-time.

## Tính năng

- ✅ Backup parallel với rsync
- ✅ Monitor băng thông real-time trong quá trình backup
- ✅ Hiển thị download/upload speed
- ✅ Cảnh báo khi băng thông cao
- ✅ Retry tự động cho chunks bị lỗi
- ✅ Logging chi tiết
- ✅ Script setup tự động
- ✅ Multiple config templates

## Quick Start

```bash
# Clone repository
git clone https://github.com/your-username/vps-backup-tool.git
cd vps-backup-tool

# Auto setup (tạo config từ templates)
./setup.sh

# Edit config với thông tin VPS của bạn
nano config.yaml
nano config_test.yaml  # Cho testing

# Test connection
python3 quick_bandwidth.py

# Start backup with monitoring
./backup_with_monitoring.sh
```

## Cài đặt thủ công

```bash
# Cài đặt dependencies
pip3 install -r requirements.txt

# Cấp quyền thực thi
chmod +x *.sh

# Tạo config từ templates
cp config.yaml.template config.yaml
cp config_test.yaml.template config_test.yaml

# Edit với thông tin VPS của bạn
nano config.yaml
```

## Cấu hình

Chỉnh sửa `config.yaml`:

```yaml
# SSH & đường dẫn
ssh_user: root
ssh_host: your_vps_ip
ssh_port: 22
ssh_key: /path/to/your/ssh/key

# Thư mục
remote_root: /home
local_root: ./backup_data

# Performance
threads: 8
bwlimit: 0  # KB/s limit (0 = unlimited)

# Bandwidth monitoring
enable_bandwidth_monitoring: true
monitoring_interval: 10  # giây
```

## Sử dụng

### 1. Script tương tác (Khuyến nghị)

```bash
./backup_with_monitoring.sh [config_file]
```

Menu sẽ hiện ra:
1. Quick bandwidth check - Kiểm tra băng thông nhanh
2. Start backup with monitoring - Bắt đầu backup với monitoring
3. Monitor bandwidth only - Chỉ monitor băng thông 
4. Show help - Hiển thị trợ giúp

### 2. Chạy trực tiếp

```bash
# Backup với monitoring tích hợp
python3 main.py [config_file]

# Kiểm tra băng thông nhanh
python3 quick_bandwidth.py [config_file]

# Monitor băng thông liên tục
python3 monitor_bandwidth.py [config_file] monitor [duration] [interval]
```

### 3. Shell script truyền thống

```bash
./run_backup.sh  # Sử dụng config.yaml mặc định
```

## Output mẫu

```
🔍 Bandwidth monitoring started for 192.168.1.100 (interval: 10s)
🚀 Starting backup with 8 threads...
📂 Remote: root@192.168.1.100:/home
📁 Local: ./backup_data
================================================================================
[17:34:27] 📡 eth0: ⬇️ 45.2 MB/s | ⬆️ 2.1 MB/s
[17:34:37] 📡 eth0: ⬇️ 52.8 MB/s | ⬆️ 1.8 MB/s
Chunk 1: ✅ OK
Chunk 2: ✅ OK
[17:34:47] 📡 eth0: ⬇️ 48.9 MB/s | ⬆️ 2.3 MB/s
Chunk 3: ✅ OK
================================================================================
✅ Backup complete! 8/8 chunks successful
📊 Current bandwidth: ⬇️ 25.4 MB/s | ⬆️ 1.2 MB/s
💡 Consider running final mirror rsync if desired.

📊 Max bandwidth observed: ⬇️ 52.8 MB/s | ⬆️ 2.3 MB/s
```

## Cảnh báo băng thông

Script sẽ tự động cảnh báo khi:
- Download > 50 MB/s: `⚠️ HIGH DOWNLOAD TRAFFIC!`
- Upload > 10 MB/s: `⚠️ HIGH UPLOAD TRAFFIC!`

## Security

⚠️ **QUAN TRỌNG**: File `config.yaml` chứa thông tin nhạy cảm và đã được thêm vào `.gitignore`

- SSH keys không được commit vào repository
- File config thật không được push lên Git
- Sử dụng `config.yaml.template` làm mẫu
- Kiểm tra `.gitignore` trước khi commit

## Files Structure

```
├── main.py                      # Script backup chính với monitoring
├── monitor_bandwidth.py         # Tool monitor standalone  
├── quick_bandwidth.py          # Kiểm tra băng thông nhanh
├── backup_with_monitoring.sh   # Script tương tác
├── run_backup.sh              # Script backup truyền thống
├── setup.sh                   # Auto setup script
├── config.yaml.template       # Template cấu hình chính
├── config_test.yaml.template  # Template cấu hình test
├── requirements.txt          # Python dependencies
├── README.md                # Tài liệu này
├── LICENSE                  # MIT License
├── CHANGELOG.md            # Lịch sử thay đổi
└── .gitignore              # Git ignore rules
```

**⚠️ Files không có trong repo (được tạo từ templates):**
```
├── config.yaml             # Config thật (tạo từ template)
├── config_test.yaml       # Config test thật (tạo từ template)
├── backup_data/           # Dữ liệu backup
├── logs/                  # Log files
└── tmp/                   # Temporary files
```

## Troubleshooting

1. **Lỗi SSH**: Kiểm tra ssh_key, ssh_host, ssh_port
2. **Lỗi rsync**: Kiểm tra rsync_opts trong config
3. **Monitoring không hoạt động**: Đặt `enable_bandwidth_monitoring: false`
4. **Slow performance**: Giảm `threads` hoặc tăng `bwlimit`

## Tips

- Sử dụng `config_test.yaml` để test trước khi backup full
- Monitor băng thông trước khi backup để biết baseline
- Backup trong giờ thấp điểm để tránh ảnh hưởng người dùng
- Kiểm tra disk space trước khi backup lớn
# vps-backup-tool
