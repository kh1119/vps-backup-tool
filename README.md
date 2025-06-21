# VPS Backup Tool với Multi-Interface Bandwidth Monitoring

> **Production-ready backup tool** cho VPS với real-time bandwidth monitoring và hỗ trợ multiple network interfaces.

[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Version](https://img.shields.io/badge/Version-v1.4.0-orange.svg)](CHANGELOG.md)

## 🚀 Tính năng chính

### 💾 **Advanced Backup System**
- **Parallel Backup**: Backup nhiều chunk đồng thời với rsync
- **Chunked Transfer**: Chia nhỏ file list để backup hiệu quả
- **Auto Retry**: Tự động thử lại khi transfer thất bại
- **Progress Tracking**: Theo dõi tiến độ real-time
- **Configurable Options**: Tùy chỉnh rsync options và performance

### 📊 **Multi-Interface Bandwidth Monitoring** ⭐ NEW!
- **Smart Interface Detection**: Tự động phát hiện và monitor tất cả network interfaces
- **Virtual Interface Filtering**: Loại bỏ interfaces ảo (docker, bridge, tunnel)
- **Real-time Monitoring**: Hiển thị bandwidth usage của từng interface
- **Total Bandwidth Calculation**: Tính tổng chính xác từ tất cả interfaces
- **Visual Status Indicators**: 🟢 Active / ⚫ Inactive interfaces
- **High Traffic Warnings**: Cảnh báo khi bandwidth quá cao

### 🛡️ **Security & Configuration**
- **Secure Config Management**: Template system với .gitignore protection
- **SSH Key Authentication**: Hỗ trợ SSH private key
- **No Sensitive Data in Git**: Config files được bảo vệ khỏi git tracking

### 🖥️ **Screen Session Support** ⭐ NEW!
- **Background Processing**: Backup chạy ngầm với screen sessions
- **SSH Disconnect Protection**: Backup tiếp tục khi SSH bị ngắt
- **Session Management**: Tools để quản lý multiple backup sessions
- **Long-term Backup**: Hỗ trợ backup dài ngày không gián đoạn

### 📅 **Long-term Backup** ⭐ NEW!
- **Multi-day Support**: Thiết kế cho backup lớn có thể chạy nhiều ngày
- **Time Estimation**: Ước tính thời gian backup dựa trên data size
- **Resource Monitoring**: Kiểm tra disk space và network capacity
- **Enhanced Resilience**: Xử lý lỗi và recovery tốt hơn cho backup dài hạn

## � Quick Start

### 📦 **1. Cài đặt**
```bash
# Clone repository
git clone https://github.com/kh1119/vps-backup-tool.git
cd vps-backup-tool

# Auto setup - phát hiện OS và cài dependencies
./setup.sh
```

**Alternative setup options:**
```bash
# Rocky Linux / RHEL / CentOS (optimized)
./setup_rocky.sh

# Manual setup (any platform)
pip3 install PyYAML
chmod +x *.sh
cp config.yaml.template config.yaml
cp config_test.yaml.template config_test.yaml
```

### ⚙️ **2. Cấu hình**
```bash
# Edit config với thông tin VPS của bạn
nano config.yaml

# Ví dụ config:
ssh_user: root
ssh_host: 184.164.80.58
ssh_port: 1022
ssh_key: /Users/username/.ssh/vps_key
remote_root: /home
local_root: ./backup_data
threads: 8
enable_bandwidth_monitoring: true
```

### 🔍 **3. Test kết nối**
```bash
# Test SSH connection
./test_ssh.sh config.yaml

# Quick bandwidth check
python3 quick_bandwidth.py config.yaml

# Test multi-interface detection
python3 test_multi_interface.py config.yaml
```

### 🎯 **4. Chạy backup**
```bash
# Interactive menu (recommended)
./backup_menu.sh

# Long-term backup (for multi-day operations)
./long_backup.sh

# Screen-based backup (background processing)
./auto_backup.sh config.yaml my-backup

# Direct backup with monitoring
python3 main.py config.yaml

# Quick demo of screen functionality
./demo_screen.sh
```

## 🖥️ Screen Session Management ⭐ NEW!

Hệ thống backup giờ đây hỗ trợ **screen sessions** cho backup dài hạn:

### **Interactive Menu System:**
```bash
# Main menu with all options
./backup_menu.sh

# Specialized long-term backup menu
./long_backup.sh

# Quick screen demo
./demo_screen.sh
```

### **Screen Session Benefits:**
- ✅ **SSH Disconnect Protection**: Backup tiếp tục khi SSH bị ngắt
- ✅ **Background Processing**: Chạy ngầm, không chiếm terminal
- ✅ **Session Persistence**: Reconnect và tiếp tục theo dõi
- ✅ **Multiple Sessions**: Chạy nhiều backup cùng lúc
- ✅ **Resource Monitoring**: Track bandwidth và system resources

### **Screen Commands:**
```bash
# Session management via our tools
./screen_manager.sh start config.yaml my-backup full
./screen_manager.sh list
./screen_manager.sh attach my-backup
./screen_manager.sh stop my-backup

# Direct screen commands
screen -ls                          # List all sessions
screen -r vps-backup-my-backup     # Attach to session
# Ctrl+A, then D                   # Detach (keep running)
screen -S vps-backup-my-backup -X quit  # Kill session
```

## 📅 Long-term Backup ⭐ NEW!

Chế độ **Long-term Backup** được thiết kế cho backup lớn có thể chạy **nhiều ngày**:

### **Features:**
- 🕐 **Time Estimation**: Ước tính thời gian dựa trên kích thước data
- 💾 **Disk Space Check**: Kiểm tra không gian trống trước khi backup
- 📡 **Network Stability**: Monitor bandwidth để tránh quá tải
- 🔧 **Enhanced Error Handling**: Xử lý lỗi tốt hơn cho backup dài
- 📊 **Progress Tracking**: Theo dõi tiến độ chi tiết

### **Usage:**
```bash
# Launch long-term backup menu
./long_backup.sh

# Features include:
# - Pre-backup system checks
# - Time and space estimation  
# - Optimized screen session settings
# - Enhanced monitoring and alerts
```

### **Best Practices for Long-term Backup:**
```bash
✅ Use meaningful session names with dates
✅ Monitor bandwidth to avoid network issues  
✅ Check disk space regularly
✅ Use screen detach (Ctrl+A, D) never Ctrl+C
✅ Check logs periodically: tail -f logs/backup_*.log
✅ Keep SSH connection alive or use screen sessions
```

## � Multi-Interface Monitoring ⭐ NEW!

Tool giờ đây hỗ trợ **monitoring tất cả network interfaces** trên VPS:

### **Before vs After:**
```bash
# ❌ Trước (v1.0):
[12:34:56] 📊 Total: ⬇️ 50.0 MB/s | ⬆️ 10.0 MB/s

# ✅ Sau (v1.4.0):
[12:34:56] 📊 Total: ⬇️ 51.0 MB/s | ⬆️ 10.5 MB/s (2/3 active)
         Active interfaces:
           eth0: ⬇️ 50.0 MB/s | ⬆️ 10.0 MB/s
           eth1: ⬇️ 1.0 MB/s | ⬆️ 512.0 KB/s
         ⚠️  HIGH DOWNLOAD TRAFFIC!
```

### **Detailed Interface View:**
```bash
📊 Total Bandwidth: ⬇️ 51.0 MB/s | ⬆️ 10.5 MB/s  
🔌 Network Interfaces: 2/3 active

📡 Network Interface Details:
   🟢 eth0: ⬇️ 50.0 MB/s | ⬆️ 10.0 MB/s ⚠️ HIGH DOWNLOAD
            Total: ⬇️ 125.50GB | ⬆️ 89.20GB
   🟢 eth1: ⬇️ 1.0 MB/s | ⬆️ 512.0 KB/s  
            Total: ⬇️ 25.80GB | ⬆️ 12.40GB
   ⚫ wlan0: ⬇️ 0.0 B/s | ⬆️ 0.0 B/s
            Total: ⬇️ 5.20GB | ⬆️ 2.10GB

🏷️  Interface Types: Ethernet: 2, WiFi: 1
```

## 🛠️ Tools Overview

| Tool | Description | Usage |
|------|-------------|-------|
| **backup_menu.sh** | Main interactive menu | `./backup_menu.sh` |
| **long_backup.sh** | Long-term backup specialized menu | `./long_backup.sh` |
| **screen_manager.sh** | Screen session management | `./screen_manager.sh start config.yaml session-name` |
| **auto_backup.sh** | Quick backup launcher with screen | `./auto_backup.sh config.yaml session-name` |
| **demo_screen.sh** | Screen functionality demo | `./demo_screen.sh` |
| **main.py** | Core backup script with integrated monitoring | `python3 main.py config.yaml` |
| **monitor_bandwidth.py** | Standalone bandwidth monitoring | `python3 monitor_bandwidth.py config.yaml monitor 60 5` |
| **quick_bandwidth.py** | Quick bandwidth check | `python3 quick_bandwidth.py config.yaml` |
| **test_ssh.sh** | SSH connection and permission test | `./test_ssh.sh config.yaml` |
| **test_multi_interface.py** | Multi-interface detection test | `python3 test_multi_interface.py config.yaml` |
| **demo_multi_interface.py** | Demo of monitoring improvements | `python3 demo_multi_interface.py` |

## 🏗️ Project Structure

```
vps-backup-tool/
├── 🐍 Core Scripts
│   ├── main.py                     # Main backup script
│   ├── monitor_bandwidth.py        # Standalone monitoring  
│   └── quick_bandwidth.py          # Quick bandwidth check
├── 🔧 Setup & Utilities
│   ├── setup.sh                    # Universal setup script
│   ├── setup_rocky.sh              # Rocky Linux setup
│   ├── backup_with_monitoring.sh   # Interactive menu
│   └── run_backup.sh               # Backup execution script
├── 🧪 Testing Tools
│   ├── test_ssh.sh                 # SSH connection test
│   ├── test_multi_interface.py     # Interface detection test
│   └── demo_multi_interface.py     # Demo script
├── ⚙️ Configuration
│   ├── config.yaml.template        # Production config template
│   ├── config_test.yaml.template   # Test config template
│   ├── config.yaml                 # Your production config (gitignored)
│   └── config_test.yaml            # Your test config (gitignored)
├── 📚 Documentation
│   ├── README.md                   # This file
│   ├── CHANGELOG.md                # Version history
│   ├── GITHUB_SETUP.md             # GitHub setup guide
│   ├── MULTI_INTERFACE_SUMMARY.md  # Multi-interface guide
│   └── LICENSE                     # MIT License
├── 📦 Dependencies
│   ├── requirements.txt            # Python dependencies
│   └── .gitignore                 # Git ignore rules
└── 📁 Generated Directories
    ├── backup_data/                # Local backup storage
    ├── tmp/                        # Temporary files
    └── logs/                       # Log files
```

## 🎯 Use Cases & Scenarios

### **🏢 Production Environments**
- **Multi-Server Backup**: Different configs for multiple VPS
- **Scheduled Backups**: Cron jobs with different monitoring intervals
- **High-Traffic Monitoring**: Real-time bandwidth tracking during peak hours
- **Load Balancer Setups**: Monitor multiple network interfaces on LB servers

### **🧪 Development & Testing**  
- **Container Environments**: Proper filtering of Docker/LXC interfaces
- **CI/CD Integration**: Automated backup testing with `config_test.yaml`
- **Network Debugging**: Interface detection and bandwidth analysis
- **Multi-Interface Testing**: VMs with multiple NICs

### **☁️ Cloud VPS Scenarios**
- **AWS EC2**: Multiple ENIs (Elastic Network Interfaces)
- **DigitalOcean Droplets**: Private networking + public interfaces  
- **Linode VPS**: VLAN + public interfaces
- **Vultr Instances**: Multiple IP addresses and interfaces

### **🌐 Edge & IoT Deployments**
- **Edge Servers**: WiFi + Ethernet failover monitoring
- **IoT Gateways**: Multiple connection types (4G, WiFi, Ethernet)
- **Remote Locations**: Satellite + terrestrial backup connections

## 🔍 Advanced Features

### **🎛️ Monitoring Customization**
```yaml
# Fine-tune monitoring behavior
monitoring_interval: 5              # Check every 5 seconds
enable_bandwidth_monitoring: true   # Enable/disable monitoring
```

### **⚡ Performance Tuning**
```yaml
threads: 8          # Parallel backup threads (CPU cores * 2)
bwlimit: 10000      # Limit to 10MB/s (10000 KB/s)
chunk_size: 1000    # Files per chunk (auto-calculated if not set)
```

### **🔧 Advanced Rsync Options**
```yaml
rsync_opts:
  - --archive                    # Standard backup options
  - --compress                   # Compression during transfer
  - --delete                     # Mirror mode (delete extra files)
  - --progress                   # Show progress
  - --exclude=*.tmp             # Exclude temporary files
  - --exclude=node_modules/     # Exclude node_modules
  - --bandwidth-limit=10M       # Alternative bandwidth limiting
```

### **📊 Custom Monitoring Thresholds**
Tool automatically warns when:
- **Download** > 100 MB/s (total across all interfaces)
- **Upload** > 50 MB/s (total across all interfaces)  
- **Per-interface** > 50 MB/s download or > 10 MB/s upload

## 🐛 Troubleshooting

### **🔑 SSH Issues**
```bash
# Test SSH connection
./test_ssh.sh config.yaml

# Common fixes:
chmod 600 /path/to/ssh/key          # Fix key permissions
ssh-copy-id -i key user@host        # Copy public key to VPS
ssh -i key -p port user@host        # Manual connection test
```

### **🌐 Network Interface Issues**
```bash
# Test interface detection
python3 test_multi_interface.py config.yaml

# Check what interfaces exist on VPS
ssh user@host "ip addr show"
ssh user@host "cat /proc/net/dev"
```

### **📊 Bandwidth Monitoring Issues**
```bash
# Quick bandwidth test
python3 quick_bandwidth.py config.yaml

# Demo with mock data (if SSH fails)
python3 demo_multi_interface.py

# Check VPS network status
ssh user@host "iftop -t -s 10"      # If iftop is installed
```

### **💾 Backup Issues**
```bash
# Test with smaller directory first
python3 main.py config_test.yaml

# Check disk space
df -h ./backup_data                 # Local space
ssh user@host "df -h /"            # Remote space

# Check rsync connectivity
rsync --version                     # Check rsync is installed
```

### **🔧 Permission Issues**
```bash
# Fix script permissions
chmod +x *.sh

# Check SSH key permissions  
ls -la /path/to/ssh/key            # Should be 600

# Check VPS directory permissions
ssh user@host "ls -la /path/to/backup/dir"
```

## 📈 Performance Tips

### **🚀 Speed Optimization**
1. **Increase threads**: `threads: 16` (but don't exceed CPU cores * 4)
2. **Use compression**: Include `--compress` in rsync_opts
3. **Exclude unnecessary files**: Add `--exclude` patterns
4. **Local SSD storage**: Use fast local disk for backup_data
5. **Network optimization**: Check if VPS has multiple interfaces for load balancing

### **💰 Bandwidth Management**
1. **Set bandwidth limits**: `bwlimit: 5000` (5MB/s) for shared hosting
2. **Monitor during off-peak**: Run backups during low-traffic hours
3. **Use monitoring intervals**: `monitoring_interval: 30` for less overhead
4. **Graduated backup**: Start with small directories, scale up

### **🔒 Security Best Practices**
1. **SSH Key Authentication**: Never use password auth for automated backups
2. **Restricted SSH Keys**: Use keys with limited command access if possible  
3. **Config Security**: Never commit real configs to git (templates only)
4. **Network Security**: Use VPN if backing up over public internet
5. **Encryption**: Consider encrypting backup_data locally

## 🤝 Contributing

### **🐛 Bug Reports**
- Use GitHub Issues with detailed error messages
- Include config (with sensitive data removed)
- Provide VPS environment details (OS, network setup)

### **✨ Feature Requests**  
- Describe use case and expected behavior
- Check existing issues for similar requests
- Consider submitting a PR if you can implement it

### **🔧 Development Setup**
```bash
git clone git@github.com:kh1119/vps-backup-tool.git
cd vps-backup-tool
./setup.sh
# Make changes, test thoroughly
git add . && git commit -m "feat: description"
```

## 📋 Requirements

### **System Requirements**
- **Python**: 3.7+ (3.8+ recommended)
- **rsync**: Must be installed on both local and remote systems
- **SSH**: Key-based authentication configured
- **Disk Space**: Adequate space for backup data

### **Supported Platforms**

| Platform | Status | Setup Command |
|----------|--------|---------------|
| **Rocky Linux 8/9** | ✅ Full Support | `./setup_rocky.sh` |
| **RHEL 8/9** | ✅ Full Support | `./setup_rocky.sh` |
| **CentOS 8** | ✅ Full Support | `./setup_rocky.sh` |
| **Ubuntu 20.04+** | ✅ Full Support | `./setup.sh` |
| **Debian 11+** | ✅ Full Support | `./setup.sh` |
| **macOS** | ✅ Full Support | `./setup.sh` |
| **Windows** | ⚠️ WSL Only | `./setup.sh` (in WSL) |

### **VPS Requirements**
- **Linux-based VPS** (any distribution)
- **SSH access** with key authentication
- **rsync installed** on VPS
- **Network interfaces** accessible via `/proc/net/dev`

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🏷️ Version History

- **v1.4.0** (2025-06-21): Multi-Interface Bandwidth Monitoring
- **v1.0.0** (2025-06-21): Initial Release

See [CHANGELOG.md](CHANGELOG.md) for detailed version history.

---

## 🎉 Ready to Start?

```bash
# 1. Clone and setup
git clone https://github.com/kh1119/vps-backup-tool.git
cd vps-backup-tool && ./setup.sh

# 2. Configure  
nano config.yaml

# 3. Test connection
./test_ssh.sh config.yaml

# 4. Start backup!
./backup_with_monitoring.sh
```

**🎯 Perfect for VPS environments with multiple network interfaces!**

---

Made with ❤️ for the VPS backup community. [Star us on GitHub!](https://github.com/kh1119/vps-backup-tool) ⭐
