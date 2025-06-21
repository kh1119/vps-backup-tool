# Screen Session Guide - VPS Backup Tool

## 🖥️ Tại sao sử dụng Screen?

**Screen** cho phép chạy backup trong background, ngay cả khi bạn ngắt kết nối SSH. Điều này rất quan trọng cho:

- ✅ **Backup lớn**: Chạy nhiều giờ hoặc nhiều ngày
- ✅ **Kết nối không ổn định**: WiFi, mobile data có thể bị gián đoạn  
- ✅ **Linh hoạt**: Có thể disconnect và reconnect bất cứ lúc nào
- ✅ **Monitoring**: Theo dõi tiến độ từ xa

## 🚀 Quick Start với Screen

### **1. Start backup trong screen:**
```bash
# Sử dụng menu (khuyến nghị)
./backup_menu.sh

# Hoặc direct command
./auto_backup.sh config.yaml my-backup full
```

### **2. Detach (thoát nhưng giữ backup chạy):**
```
Ctrl+A, sau đó nhấn D
```

### **3. Attach lại (xem lại backup):**
```bash
./screen_manager.sh attach my-backup

# Hoặc direct
screen -r vps-backup-my-backup
```

## 📋 Screen Commands Reference

### **Basic Commands:**
```bash
# List tất cả sessions
./screen_manager.sh list
screen -ls

# Start backup session
./screen_manager.sh start config.yaml session-name full

# Attach to session  
./screen_manager.sh attach session-name
screen -r vps-backup-session-name

# Stop session
./screen_manager.sh stop session-name
screen -S vps-backup-session-name -X quit
```

### **Khi đã attach vào session:**
- **Ctrl+A, D**: Detach (backup tiếp tục chạy)
- **Ctrl+C**: Interrupt command hiện tại
- **exit**: Thoát session hoàn toàn

### **Advanced Screen Commands:**
```bash
# Attach forced (nếu session bị "Attached")
screen -D -r vps-backup-session-name

# Create new window trong session
Ctrl+A, then C

# Switch giữa windows
Ctrl+A, then 0-9

# List windows
Ctrl+A, then "
```

## 🎯 Use Cases

### **📦 Backup Scenarios:**

#### **1. Production Backup (long-running):**
```bash
./backup_menu.sh
# Chọn option 3: Full Production Backup
# Session name: prod-backup-0621
```

#### **2. Test Backup:**
```bash
./screen_manager.sh start config_test.yaml test-session test
```

#### **3. Monitoring Only:**
```bash
./screen_manager.sh start config.yaml monitoring monitor-only
```

### **🌐 Network Scenarios:**

#### **1. Unstable Internet:**
```bash
# Start backup
./auto_backup.sh config.yaml backup-unstable full

# Disconnect SSH safely
Ctrl+A, D

# Reconnect later từ bất kỳ đâu
ssh user@vps
cd /path/to/backup/tool
./screen_manager.sh attach backup-unstable
```

#### **2. Multiple Backups:**
```bash
# Production backup
./screen_manager.sh start config.yaml prod-backup full

# Test backup  
./screen_manager.sh start config_test.yaml test-backup test

# Monitoring
./screen_manager.sh start config.yaml monitor-only monitor-only

# List all
./screen_manager.sh list
```

## 🔧 Troubleshooting

### **❌ "No screen session found"**
```bash
# Check tất cả sessions
screen -ls

# Session có thể có tên khác
./screen_manager.sh list

# Cleanup dead sessions
./screen_manager.sh cleanup
```

### **❌ "There is a screen on..."**
```bash
# Session đã attached ở nơi khác, force attach:
screen -D -r vps-backup-session-name
```

### **❌ Screen không tìm thấy**
```bash
# Install screen
sudo dnf install screen      # Rocky/RHEL/CentOS
sudo apt install screen      # Debian/Ubuntu  
brew install screen          # macOS
```

### **❌ Session bị crash**
```bash
# Cleanup dead sessions
./screen_manager.sh cleanup

# Check logs
ls logs/
cat logs/backup-*.log
```

## 📊 Monitoring trong Screen

### **Real-time monitoring display:**
```
🚀 VPS Backup Tool - Multi-Interface Monitoring
==================================================
🖥️  Running in screen session: 12345.vps-backup-prod
   Detach: Ctrl+A, then D
   Attach: screen -r 12345.vps-backup-prod
==================================================
📋 Config: config.yaml
🖥️  VPS: root@184.164.80.58:1022
📁 Source: /home
💾 Destination: ./backup_data
🧵 Threads: 8
🖥️  Screen Session: 12345.vps-backup-prod
   💡 This backup will continue running even if you disconnect SSH
==================================================

[12:34:56] 📊 Total: ⬇️ 51.0 MB/s | ⬆️ 10.5 MB/s (2/3 active)
         Active interfaces:
           eth0: ⬇️ 50.0 MB/s | ⬆️ 10.0 MB/s
           eth1: ⬇️ 1.0 MB/s | ⬆️ 512.0 KB/s
```

## 🎯 Best Practices

### **🔒 Security:**
1. **SSH Key Authentication**: Luôn sử dụng SSH keys
2. **Screen Permissions**: Session chỉ visible cho user owner
3. **Config Protection**: Sensitive configs không được commit vào git

### **📈 Performance:**
1. **Adequate Resources**: Đảm bảo VPS có đủ CPU/RAM
2. **Network Stability**: Monitor bandwidth để tránh overload
3. **Storage Space**: Check disk space trước khi backup lớn

### **🔧 Management:**
1. **Naming Convention**: Sử dụng tên session rõ ràng (prod-0621, test-morning)
2. **Regular Cleanup**: Cleanup dead sessions định kỳ
3. **Log Monitoring**: Check logs thường xuyên

### **⚡ Workflow Tips:**
1. **Test First**: Luôn test với config_test.yaml trước
2. **Staged Backups**: Backup từng phần với directory nhỏ
3. **Monitor Progress**: Attach session định kỳ để check
4. **Document Sessions**: Ghi chú session names và purposes

## 📱 Quick Reference Card

```bash
# === ESSENTIAL COMMANDS ===

# Start backup menu
./backup_menu.sh

# Quick backup start  
./auto_backup.sh config.yaml

# List sessions
./screen_manager.sh list

# Attach to session
./screen_manager.sh attach session-name

# Detach from session
Ctrl+A, then D

# Stop session
./screen_manager.sh stop session-name

# === EMERGENCY ===

# Force attach
screen -D -r vps-backup-session-name

# Kill all backup sessions
screen -ls | grep vps-backup | cut -d. -f1 | xargs -I {} screen -S {} -X quit

# Cleanup everything
./screen_manager.sh cleanup
```

---

## 🎉 Ready to Go!

Bây giờ bạn có thể chạy backup lớn mà không lo về ngắt kết nối SSH!

```bash
# Start backup menu và tận hưởng
./backup_menu.sh
```

**🎯 Perfect cho backup multi-day với VPS multiple interfaces!** 🚀
