#!/usr/bin/env bash
# long_backup.sh - Khởi động backup cho quá trình dài ngày với các tính năng nâng cao

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

print_banner() {
    echo -e "${CYAN}"
    cat << 'EOF'
╔═══════════════════════════════════════════════════════════╗
║                   🚀 LONG-TERM BACKUP                    ║
║              Multi-Day VPS Backup with Screen            ║
║                     + Monitoring                         ║
╚═══════════════════════════════════════════════════════════╝
EOF
    echo -e "${NC}"
}

print_warning_banner() {
    echo -e "${YELLOW}"
    cat << 'EOF'
⚠️  IMPORTANT NOTES FOR LONG-TERM BACKUP:
════════════════════════════════════════

• This backup may run for DAYS depending on data size
• Use screen session to prevent interruption when SSH disconnects  
• Monitor bandwidth to avoid overwhelming your connection
• Keep your SSH connection alive or use screen detach/attach
• Check logs regularly for any issues

EOF
    echo -e "${NC}"
}

check_prerequisites() {
    echo -e "${BLUE}🔍 Checking prerequisites...${NC}"
    
    local issues=0
    
    # Check screen
    if ! command -v screen &> /dev/null; then
        echo -e "${RED}❌ Screen not installed${NC}"
        echo "   Install: sudo dnf install screen (Rocky/RHEL)"
        echo "           sudo apt install screen (Debian/Ubuntu)" 
        issues=$((issues + 1))
    else
        echo -e "${GREEN}✅ Screen available${NC}"
    fi
    
    # Check rsync
    if ! command -v rsync &> /dev/null; then
        echo -e "${RED}❌ Rsync not installed${NC}"
        issues=$((issues + 1))
    else
        echo -e "${GREEN}✅ Rsync available${NC}"
    fi
    
    # Check Python and PyYAML
    if ! python3 -c "import yaml" &> /dev/null; then
        echo -e "${RED}❌ PyYAML not installed${NC}"
        echo "   Install: pip3 install PyYAML"
        issues=$((issues + 1))
    else
        echo -e "${GREEN}✅ Python3 + PyYAML available${NC}"
    fi
    
    # Check disk space
    local free_gb=$(df . | awk 'NR==2 {printf "%.1f", $4/1024/1024}')
    echo -e "${CYAN}💾 Available disk space: ${free_gb}GB${NC}"
    
    if (( $(echo "$free_gb < 10" | bc -l) )); then
        echo -e "${YELLOW}⚠️  Warning: Low disk space (< 10GB)${NC}"
        echo "   Consider freeing up space before starting large backup"
    fi
    
    # Check network connectivity (if config exists)
    if [[ -f "config.yaml" ]]; then
        echo -e "${BLUE}🌐 Testing SSH connectivity...${NC}"
        if ./test_ssh.sh config.yaml &> /dev/null; then
            echo -e "${GREEN}✅ SSH connection successful${NC}"
        else
            echo -e "${YELLOW}⚠️  SSH connection test failed${NC}"
            echo "   Check config.yaml and SSH keys"
        fi
    fi
    
    return $issues
}

estimate_backup_time() {
    local config_file="${1:-config.yaml}"
    
    if [[ ! -f "$config_file" ]]; then
        echo -e "${YELLOW}⚠️  Config file not found, skipping estimation${NC}"
        return
    fi
    
    echo -e "${BLUE}📊 Estimating backup time...${NC}"
    
    # Try to get remote directory size
    if command -v python3 &> /dev/null && python3 -c "import yaml" &> /dev/null; then
        local ssh_host=$(python3 -c "import yaml; print(yaml.safe_load(open('$config_file'))['ssh_host'])" 2>/dev/null || echo "")
        local ssh_user=$(python3 -c "import yaml; print(yaml.safe_load(open('$config_file'))['ssh_user'])" 2>/dev/null || echo "")
        local ssh_key=$(python3 -c "import yaml; print(yaml.safe_load(open('$config_file'))['ssh_key'])" 2>/dev/null || echo "")
        local remote_root=$(python3 -c "import yaml; print(yaml.safe_load(open('$config_file'))['remote_root'])" 2>/dev/null || echo "")
        
        if [[ -n "$ssh_host" && -n "$ssh_user" && -n "$ssh_key" && -n "$remote_root" ]]; then
            echo "   Source: ${ssh_user}@${ssh_host}:${remote_root}"
            
            # Get directory size
            local size_cmd="du -sb $remote_root 2>/dev/null | cut -f1 || echo 0"
            local size_bytes=$(ssh -i "$ssh_key" -o ConnectTimeout=10 "${ssh_user}@${ssh_host}" "$size_cmd" 2>/dev/null || echo "0")
            
            if [[ "$size_bytes" -gt 0 ]]; then
                local size_gb=$(echo "scale=2; $size_bytes / 1024 / 1024 / 1024" | bc -l)
                echo -e "   📦 Remote directory size: ${size_gb}GB"
                
                # Rough time estimation (assuming 10MB/s average transfer)
                local estimated_seconds=$(echo "scale=0; $size_bytes / 10 / 1024 / 1024" | bc -l)
                local estimated_hours=$(echo "scale=1; $estimated_seconds / 3600" | bc -l)
                
                echo -e "   ⏱️  Estimated time (10MB/s): ${estimated_hours} hours"
                
                if (( $(echo "$estimated_hours > 24" | bc -l) )); then
                    echo -e "${YELLOW}   ⚠️  This backup will take more than 24 hours!${NC}"
                fi
            else
                echo -e "${YELLOW}   ⚠️  Could not determine remote directory size${NC}"
            fi
        fi
    fi
}

configure_long_backup() {
    echo -e "${BLUE}⚙️  Long-term backup configuration${NC}"
    echo ""
    
    # Select config file
    echo "Available configurations:"
    for config in config.yaml config_test.yaml; do
        if [[ -f "$config" ]]; then
            echo -e "  ${GREEN}✅ $config${NC}"
        else
            echo -e "  ${RED}❌ $config (missing)${NC}"
        fi
    done
    echo ""
    
    read -p "Config file [config.yaml]: " config_file
    config_file=${config_file:-config.yaml}
    
    if [[ ! -f "$config_file" ]]; then
        echo -e "${RED}❌ Config file not found: $config_file${NC}"
        return 1
    fi
    
    # Generate session name with date
    local default_session="long-backup-$(date +%m%d)"
    read -p "Session name [$default_session]: " session_name
    session_name=${session_name:-$default_session}
    
    # Backup options
    echo ""
    echo "🎛️  Backup options:"
    echo "1) Full backup with monitoring (recommended)"
    echo "2) Full backup without monitoring"
    echo "3) Monitor bandwidth only"
    echo ""
    read -p "Choice [1]: " backup_option
    backup_option=${backup_option:-1}
    
    local backup_type="full"
    case $backup_option in
        1) backup_type="full" ;;
        2) backup_type="full-no-monitor" ;;
        3) backup_type="monitor-only" ;;
        *) backup_type="full" ;;
    esac
    
    # Summary
    echo ""
    echo -e "${CYAN}📋 Backup Summary:${NC}"
    echo "   Config: $config_file"
    echo "   Session: $session_name"
    echo "   Type: $backup_type"
    echo ""
    
    # Time estimation
    estimate_backup_time "$config_file"
    echo ""
    
    # Final confirmation
    echo -e "${YELLOW}⚠️  This backup may run for DAYS. Continue?${NC}"
    read -p "Start long-term backup? [y/N] " -n 1 -r
    echo
    
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Cancelled."
        return 0
    fi
    
    # Start backup
    echo ""
    echo -e "${GREEN}🚀 Starting long-term backup...${NC}"
    
    ./screen_manager.sh start "$config_file" "$session_name" "$backup_type"
    
    echo ""
    echo -e "${GREEN}✅ Long-term backup started!${NC}"
    echo ""
    echo -e "${CYAN}📱 Management commands:${NC}"
    echo "  Attach:  ./screen_manager.sh attach $session_name"
    echo "  Status:  ./screen_manager.sh list"
    echo "  Stop:    ./screen_manager.sh stop $session_name"
    echo ""
    echo -e "${CYAN}🖥️  Direct screen commands:${NC}"
    echo "  screen -r vps-backup-$session_name    # Attach"
    echo "  screen -ls                            # List sessions"
    echo ""
    echo -e "${YELLOW}💡 Tips for long-term backup:${NC}"
    echo "  • Use Ctrl+A, then D to detach (not Ctrl+C!)"
    echo "  • Check logs regularly: tail -f logs/backup_*.log"
    echo "  • Monitor bandwidth: python3 quick_bandwidth.py"
    echo "  • Keep SSH connection alive or detach and reconnect later"
    echo ""
}

show_active_backups() {
    echo -e "${BLUE}📊 Active Long-term Backups${NC}"
    echo ""
    
    ./screen_manager.sh list
    
    echo ""
    echo -e "${CYAN}📱 Quick Actions:${NC}"
    echo "  a) Attach to a session"
    echo "  s) Stop a session" 
    echo "  r) Restart monitoring"
    echo "  q) Back to main menu"
    echo ""
    
    read -p "Action [q]: " action
    action=${action:-q}
    
    case $action in
        a|A)
            echo ""
            read -p "Session name to attach: " session_name
            if [[ -n "$session_name" ]]; then
                ./screen_manager.sh attach "$session_name"
            fi
            ;;
        s|S)
            echo ""
            read -p "Session name to stop: " session_name
            if [[ -n "$session_name" ]]; then
                ./screen_manager.sh stop "$session_name"
            fi
            ;;
        r|R)
            echo ""
            echo "Starting bandwidth monitor..."
            python3 quick_bandwidth.py config.yaml
            ;;
    esac
}

main_menu() {
    while true; do
        clear
        print_banner
        
        echo -e "${CYAN}╔════════════════════════════════════╗${NC}"
        echo -e "${CYAN}║         LONG-TERM BACKUP           ║${NC}"  
        echo -e "${CYAN}╚════════════════════════════════════╝${NC}"
        echo ""
        echo "🚀 BACKUP OPTIONS:"
        echo "  1) 📦 Start Long-term Backup"
        echo "  2) 📊 View Active Backups"
        echo "  3) 🔧 Quick Setup Check"
        echo ""
        echo "📚 INFORMATION:"
        echo "  4) 📖 Long-term Backup Guide"
        echo "  5) 💡 Tips & Best Practices"
        echo ""
        echo "  0) 🔙 Back to Main Menu"
        echo ""
        
        read -p "Select option [0]: " choice
        choice=${choice:-0}
        
        echo ""
        
        case $choice in
            1)
                print_warning_banner
                if check_prerequisites; then
                    configure_long_backup
                else
                    echo -e "${RED}❌ Please fix issues above before starting backup${NC}"
                fi
                ;;
            2)
                show_active_backups
                ;;
            3)
                check_prerequisites
                ;;
            4)
                show_guide
                ;;
            5)
                show_tips
                ;;
            0)
                echo -e "${GREEN}👋 Returning to main menu...${NC}"
                return 0
                ;;
            *)
                echo -e "${RED}❌ Invalid option: $choice${NC}"
                ;;
        esac
        
        if [[ $choice != 0 ]]; then
            echo ""
            read -p "Press Enter to continue..." -r
        fi
    done
}

show_guide() {
    echo -e "${BLUE}📖 Long-term Backup Guide${NC}"
    echo "=========================="
    echo ""
    cat << 'EOF'
🎯 PURPOSE:
   Long-term backup is designed for large VPS backups that may take
   days to complete. It uses screen sessions to run in background.

🚀 GETTING STARTED:
   1. Run option 3 (Quick Setup Check) first
   2. Make sure you have enough disk space
   3. Test SSH connection works properly
   4. Start backup with option 1

🖥️  SCREEN SESSION BASICS:
   • Screen lets programs run even after SSH disconnects
   • Detach: Ctrl+A, then D (keeps backup running)
   • Attach: screen -r <session-name> (reconnect)
   • List: screen -ls (show all sessions)

⚠️  IMPORTANT TIPS:
   • NEVER use Ctrl+C to exit - use Ctrl+A, D instead
   • Monitor bandwidth to avoid network issues
   • Check logs regularly for errors
   • Keep track of session names for easy reconnection

📊 MONITORING:
   • Bandwidth monitoring runs automatically
   • Check logs: tail -f logs/backup_*.log
   • Quick bandwidth: python3 quick_bandwidth.py
   • Interface stats: python3 demo_multi_interface.py

🔧 TROUBLESHOOTING:
   • If backup stops: check logs for errors
   • If SSH fails: verify keys and config
   • If disk full: free up space and restart
   • If network slow: monitor bandwidth usage

EOF
}

show_tips() {
    echo -e "${BLUE}💡 Tips & Best Practices${NC}"
    echo "========================"
    echo ""
    cat << 'EOF'
🏆 BEST PRACTICES:

📋 BEFORE STARTING:
   ✅ Test SSH connection thoroughly
   ✅ Ensure sufficient disk space (2x source size recommended)
   ✅ Check network stability
   ✅ Set up monitoring

🖥️  DURING BACKUP:
   ✅ Use screen sessions for resilience
   ✅ Monitor bandwidth usage regularly
   ✅ Check logs for errors periodically
   ✅ Avoid stopping backup unnecessarily

📊 MONITORING TIPS:
   ✅ Set bandwidth warnings appropriately
   ✅ Monitor multiple network interfaces
   ✅ Keep an eye on disk space usage
   ✅ Check system load on both sides

🚨 EMERGENCY PROCEDURES:
   ✅ Stop backup: screen_manager.sh stop <session>
   ✅ Emergency stop: screen -S vps-backup-<name> -X quit
   ✅ Check what's running: screen -ls
   ✅ Free disk space: clean old backups first

⚡ PERFORMANCE OPTIMIZATION:
   ✅ Use compression for faster transfer
   ✅ Adjust chunk size for your network
   ✅ Run during off-peak hours
   ✅ Monitor system resources

🔐 SECURITY NOTES:
   ✅ Use SSH keys (no passwords)
   ✅ Keep configs out of git (in .gitignore)
   ✅ Set proper file permissions
   ✅ Use separate test config for testing

EOF
}

# Check if bc is available (for calculations)
if ! command -v bc &> /dev/null; then
    echo "Warning: bc not installed, some calculations may not work"
    echo "Install: sudo dnf install bc (Rocky/RHEL) or sudo apt install bc (Debian/Ubuntu)"
fi

# Run main menu
main_menu
