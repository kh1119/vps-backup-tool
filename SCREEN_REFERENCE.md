# Screen Quick Reference cho VPS Backup

## 🎯 Screen Commands Cơ bản

### **Tạo session mới:**
```bash
screen -S tên-session          # Tạo session với tên
screen -dmS tên-session cmd    # Tạo session và chạy command ngay
```

### **Quản lý sessions:**
```bash
screen -ls                     # Liệt kê tất cả sessions
screen -r tên-session         # Attach vào session
screen -d tên-session         # Detach session từ xa
screen -S tên-session -X quit # Kill session
```

### **Trong session (phím tắt):**
```bash
Ctrl+A, D      # Detach (thoát nhưng giữ session chạy) ⭐ QUAN TRỌNG
Ctrl+A, K      # Kill session
Ctrl+A, ?      # Help menu
Ctrl+A, C      # Tạo window mới
Ctrl+A, N      # Next window
Ctrl+A, P      # Previous window
```

## 🚀 VPS Backup với Screen

### **Sử dụng tools của chúng ta:**
```bash
# Menu chính với screen support
./backup_menu.sh

# Long-term backup (khuyến nghị cho backup lớn)
./long_backup.sh

# Quick start với auto session
./auto_backup.sh config.yaml my-backup-$(date +%m%d)

# Manual session management
./screen_manager.sh start config.yaml session-name full
./screen_manager.sh list
./screen_manager.sh attach session-name
./screen_manager.sh stop session-name
```

### **Demo và testing:**
```bash
# Demo screen functionality
./demo_screen.sh

# Test SSH trước khi backup
./test_ssh.sh config.yaml
```

## ⚠️ QUAN TRỌNG - Những điều TUYỆT ĐỐI tránh

### **❌ ĐỪNG BAO GIỜ:**
```bash
Ctrl+C         # ❌ Sẽ kill backup process!
Ctrl+Z         # ❌ Sẽ suspend backup!
kill -9        # ❌ Force kill có thể corrupt data!
close terminal # ❌ Nếu không dùng screen
```

### **✅ LUÔN LUÔN:**
```bash
Ctrl+A, D      # ✅ Detach an toàn
screen -r      # ✅ Reattach khi cần
./screen_manager.sh stop  # ✅ Stop an toàn qua tool
```

## 📅 Long-term Backup Best Practices

### **Đặt tên session có ý nghĩa:**
```bash
backup-prod-1225     # Backup production ngày 25/12
backup-home-weekend  # Backup home folder cuối tuần  
backup-db-monthly    # Monthly database backup
test-backup-small    # Test backup với data nhỏ
```

### **Monitor và maintenance:**
```bash
# Check sessions định kỳ
screen -ls

# Check log files
tail -f logs/backup_*.log

# Check bandwidth
python3 quick_bandwidth.py config.yaml

# Check disk space
df -h
```

### **Troubleshooting:**
```bash
# Session bị đứng/không response
screen -S session-name -X quit

# Quá nhiều dead sessions
./screen_manager.sh cleanup

# Check process đang chạy
ps aux | grep python
ps aux | grep rsync

# Kill emergency (chỉ khi thật sự cần thiết)
pkill -f "python3 main.py"
```

## 🔧 Advanced Screen Usage

### **Session sharing (multiple users):**
```bash
screen -S shared-backup        # User 1 tạo session
screen -x shared-backup        # User 2 attach cùng session
```

### **Logging screen output:**
```bash
screen -L -S backup-session    # Enable logging
# Log sẽ được lưu vào screenlog.0
```

### **Custom screen config (.screenrc):**
```bash
# ~/.screenrc
startup_message off           # Tắt startup message
defscrollback 10000          # Increase scroll buffer
hardstatus alwayslastline    # Status bar
hardstatus string '%{= kG}%-Lw%{= kW}%50> %n%f* %t%{= kG}%+Lw%< %{= kG}%-=%D %m/%d %{...'
```

## 💡 Tips cho Backup dài ngày

### **Chuẩn bị trước backup:**
```bash
# Check disk space
df -h

# Test SSH connection
./test_ssh.sh config.yaml

# Estimate backup time
./long_backup.sh  # Có time estimation

# Setup bandwidth monitoring
python3 monitor_bandwidth.py config.yaml monitor 3600 10 &
```

### **Trong quá trình backup:**
```bash
# Check progress (từ session khác)
tail -f logs/backup_*.log

# Monitor bandwidth
python3 quick_bandwidth.py config.yaml

# Check system load
top
htop
```

### **Sau backup:**
```bash
# Verify backup integrity
du -sh backup_data/
find backup_data/ -name "*.log" -exec tail {} \;

# Cleanup old sessions
./screen_manager.sh cleanup

# Archive logs if needed
tar -czf backup_logs_$(date +%Y%m%d).tar.gz logs/
```

## 🆘 Emergency Procedures

### **Backup bị stuck:**
```bash
# 1. Attach vào session
screen -r session-name

# 2. Kiểm tra có process đang chạy
ps aux | grep rsync

# 3. Nếu cần stop:
# Trong session: Ctrl+C (chỉ khi thật sự cần)
# Hoặc: ./screen_manager.sh stop session-name
```

### **SSH connection bị mất:**
```bash
# 1. Reconnect SSH
ssh user@host

# 2. Check sessions còn chạy
screen -ls

# 3. Reattach
screen -r session-name

# 4. Check backup vẫn đang chạy
ps aux | grep python
```

### **Disk đầy:**
```bash
# 1. Check disk usage
df -h

# 2. Stop backup an toàn
./screen_manager.sh stop session-name

# 3. Clear space
rm -rf backup_data/old_backups/
rm -rf logs/old_logs/

# 4. Restart backup
./backup_menu.sh
```

---

📚 **Xem thêm:** 
- README.md - Complete user guide
- SCREEN_GUIDE.md - Detailed screen session guide
- long_backup.sh --help - Long-term backup options
