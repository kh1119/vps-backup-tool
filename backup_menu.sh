#!/usr/bin/env bash
# backup_menu.sh - Interactive menu cho VPS backup với screen support

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

print_logo() {
    echo -e "${BLUE}"
    cat << 'EOF'
    ╔══════════════════════════════════════╗
    ║        VPS Backup Tool v1.4+         ║
    ║     Multi-Interface Monitoring       ║
    ║        + Screen Session Support      ║
    ╚══════════════════════════════════════╝
EOF
    echo -e "${NC}"
}

print_main_menu() {
    echo -e "${CYAN}╔════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║              MAIN MENU             ║${NC}"
    echo -e "${CYAN}╚════════════════════════════════════╝${NC}"
    echo ""
    echo "📦 BACKUP OPTIONS:"
    echo "  1) 🚀 Quick Backup (screen session)"
    echo "  2) 🧪 Test Backup (small directory)"
    echo "  3) 💾 Full Production Backup"
    echo "  4) � Long-term Backup (multi-day)"
    echo "  5) �📊 Bandwidth Monitoring Only"
    echo ""
    echo "🖥️  SESSION MANAGEMENT:"
    echo "  6) 📋 List Active Sessions"
    echo "  7) 🔗 Attach to Session"
    echo "  8) ⏹️  Stop Session"
    echo "  9) 🧹 Cleanup Dead Sessions"
    echo ""
    echo "🔧 SETUP & TESTING:"
    echo " 10) ⚙️  Setup & Configuration"
    echo " 11) 🔍 Test SSH Connection"
    echo " 12) 📡 Test Network Interfaces"
    echo " 13) ⚡ Quick Bandwidth Check"
    echo ""
    echo "📚 INFORMATION:"
    echo " 14) 📖 Show Documentation"
    echo " 15) ❓ Help & Examples"
    echo ""
    echo "  0) 🚪 Exit"
    echo ""
}

check_dependencies() {
    local missing=0
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}❌ Python 3 not found${NC}"
        missing=1
    else
        echo -e "${GREEN}✅ Python 3 installed${NC}"
    fi
    
    # Check screen
    if ! command -v screen &> /dev/null; then
        echo -e "${RED}❌ Screen not found${NC}"
        echo "   Install: sudo dnf install screen  (Rocky/RHEL)"
        echo "           sudo apt install screen  (Debian/Ubuntu)"
        missing=1
    else
        echo -e "${GREEN}✅ Screen installed${NC}"
    fi
    
    # Check rsync
    if ! command -v rsync &> /dev/null; then
        echo -e "${RED}❌ Rsync not found${NC}"
        missing=1
    else
        echo -e "${GREEN}✅ Rsync installed${NC}"
    fi
    
    # Check PyYAML
    if ! python3 -c "import yaml" &> /dev/null; then
        echo -e "${RED}❌ PyYAML not found${NC}"
        echo "   Install: pip3 install PyYAML"
        missing=1
    else
        echo -e "${GREEN}✅ PyYAML installed${NC}"
    fi
    
    return $missing
}

show_configs() {
    echo -e "${YELLOW}Available configurations:${NC}"
    echo ""
    
    for config in config.yaml config_test.yaml; do
        if [[ -f "$config" ]]; then
            echo -e "${GREEN}✅ $config${NC}"
            # Show basic info
            if command -v python3 &> /dev/null && python3 -c "import yaml" &> /dev/null; then
                local host=$(python3 -c "import yaml; print(yaml.safe_load(open('$config'))['ssh_host'])" 2>/dev/null || echo "unknown")
                local user=$(python3 -c "import yaml; print(yaml.safe_load(open('$config'))['ssh_user'])" 2>/dev/null || echo "unknown")
                local port=$(python3 -c "import yaml; print(yaml.safe_load(open('$config'))['ssh_port'])" 2>/dev/null || echo "unknown")
                echo "   📍 ${user}@${host}:${port}"
            fi
        else
            echo -e "${RED}❌ $config (missing)${NC}"
        fi
    done
}

backup_quick() {
    echo -e "${BLUE}🚀 Quick Backup (Screen Session)${NC}"
    echo "================================"
    echo ""
    
    show_configs
    echo ""
    
    # Select config
    echo "Select configuration:"
    echo "1) config.yaml (production)"
    echo "2) config_test.yaml (test)"
    echo "3) Custom config file"
    echo ""
    read -p "Choice [1]: " config_choice
    config_choice=${config_choice:-1}
    
    local config_file=""
    case $config_choice in
        1)
            config_file="config.yaml"
            ;;
        2)
            config_file="config_test.yaml"
            ;;
        3)
            read -p "Enter config file path: " config_file
            ;;
        *)
            config_file="config.yaml"
            ;;
    esac
    
    if [[ ! -f "$config_file" ]]; then
        echo -e "${RED}❌ Config file not found: $config_file${NC}"
        return 1
    fi
    
    # Generate session name
    local session_name="backup-$(date +%m%d-%H%M)"
    read -p "Session name [$session_name]: " input_name
    session_name=${input_name:-$session_name}
    
    echo ""
    echo -e "${YELLOW}Starting backup session...${NC}"
    echo "📋 Config: $config_file"
    echo "🏷️  Session: $session_name"
    echo ""
    
    # Start backup in screen
    ./screen_manager.sh start "$config_file" "$session_name" "full"
    
    echo ""
    echo -e "${GREEN}Backup started in background!${NC}"
    echo ""
    echo "Management commands:"
    echo "  📱 Attach:  ./screen_manager.sh attach $session_name"
    echo "  ⏹️  Stop:    ./screen_manager.sh stop $session_name"
    echo "  📋 List:    ./screen_manager.sh list"
}

backup_test() {
    echo -e "${BLUE}🧪 Test Backup${NC}"
    echo "==============="
    echo ""
    
    if [[ ! -f "config_test.yaml" ]]; then
        echo -e "${RED}❌ config_test.yaml not found!${NC}"
        echo "Run setup first (option 9)"
        return 1
    fi
    
    local session_name="test-$(date +%H%M)"
    echo "Starting test backup in screen session: $session_name"
    echo ""
    
    ./screen_manager.sh start "config_test.yaml" "$session_name" "test"
    
    echo ""
    echo -e "${GREEN}Test backup started!${NC}"
    echo "📱 Attach: ./screen_manager.sh attach $session_name"
}

backup_production() {
    echo -e "${BLUE}💾 Full Production Backup${NC}"
    echo "========================="
    echo ""
    
    if [[ ! -f "config.yaml" ]]; then
        echo -e "${RED}❌ config.yaml not found!${NC}"
        echo "Run setup first (option 9)"
        return 1
    fi
    
    echo -e "${YELLOW}⚠️  This will start a full production backup!${NC}"
    echo "This may take a long time depending on data size."
    echo ""
    read -p "Continue? [y/N] " -n 1 -r
    echo
    
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Cancelled."
        return 0
    fi
    
    local session_name="prod-$(date +%m%d-%H%M)"
    read -p "Session name [$session_name]: " input_name
    session_name=${input_name:-$session_name}
    
    echo ""
    echo "Starting production backup..."
    
    ./screen_manager.sh start "config.yaml" "$session_name" "full"
    
    echo ""
    echo -e "${GREEN}Production backup started!${NC}"
    echo "📱 Attach: ./screen_manager.sh attach $session_name"
}

monitoring_only() {
    echo -e "${BLUE}📊 Bandwidth Monitoring Only${NC}"
    echo "============================="
    echo ""
    
    show_configs
    echo ""
    read -p "Config file [config.yaml]: " config_file
    config_file=${config_file:-config.yaml}
    
    if [[ ! -f "$config_file" ]]; then
        echo -e "${RED}❌ Config file not found: $config_file${NC}"
        return 1
    fi
    
    local session_name="monitor-$(date +%H%M)"
    echo "Starting monitoring session: $session_name"
    echo ""
    
    ./screen_manager.sh start "$config_file" "$session_name" "monitor-only"
    
    echo ""
    echo -e "${GREEN}Monitoring started!${NC}"
    echo "📱 Attach: ./screen_manager.sh attach $session_name"
}

setup_configuration() {
    echo -e "${BLUE}⚙️ Setup & Configuration${NC}"
    echo "========================"
    echo ""
    
    echo "Checking dependencies..."
    if ! check_dependencies; then
        echo ""
        echo -e "${RED}❌ Some dependencies are missing!${NC}"
        echo "Run the setup script first:"
        echo "  ./setup.sh"
        echo ""
        read -p "Press Enter to continue..."
        return 1
    fi
    
    echo ""
    echo "Configuration files:"
    show_configs
    echo ""
    
    echo "Setup options:"
    echo "1) 🔧 Run automatic setup (./setup.sh)"
    echo "2) 📝 Edit config.yaml"
    echo "3) 📝 Edit config_test.yaml"
    echo "4) 📋 Show current config"
    echo "5) 🔄 Create config from template"
    echo ""
    read -p "Choice [1]: " setup_choice
    setup_choice=${setup_choice:-1}
    
    case $setup_choice in
        1)
            echo "Running setup script..."
            ./setup.sh
            ;;
        2)
            ${EDITOR:-nano} config.yaml
            ;;
        3)
            ${EDITOR:-nano} config_test.yaml
            ;;
        4)
            echo ""
            echo "=== config.yaml ==="
            cat config.yaml 2>/dev/null || echo "File not found"
            echo ""
            echo "=== config_test.yaml ==="
            cat config_test.yaml 2>/dev/null || echo "File not found"
            ;;
        5)
            echo "Creating configs from templates..."
            cp config.yaml.template config.yaml 2>/dev/null || echo "Template not found"
            cp config_test.yaml.template config_test.yaml 2>/dev/null || echo "Template not found"
            echo "Done! Edit the files with your VPS details."
            ;;
    esac
}

show_documentation() {
    echo -e "${BLUE}📖 Documentation${NC}"
    echo "================="
    echo ""
    
    echo "Available documentation:"
    echo ""
    echo "📄 README.md - Complete user guide"
    echo "📊 CHANGELOG.md - Version history"
    echo "🔧 GITHUB_SETUP.md - GitHub setup guide"
    echo "🌐 MULTI_INTERFACE_SUMMARY.md - Multi-interface monitoring"
    echo ""
    
    read -p "View README.md? [y/N] " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        if command -v less &> /dev/null; then
            less README.md
        else
            cat README.md
        fi
    fi
}

show_help() {
    echo -e "${BLUE}❓ Help & Examples${NC}"
    echo "=================="
    echo ""
    
    echo "🚀 Quick Start:"
    echo "  1. Run option 10 (Setup) first"
    echo "  2. Edit config.yaml with your VPS details"
    echo "  3. Test with option 11 (SSH test)"
    echo "  4. For small backups: option 1 (Quick Backup)"
    echo "  5. For large backups: option 4 (Long-term Backup)"
    echo ""
    
    echo "📅 Long-term Backup (for multi-day operations):"
    echo "  • Specialized menu for large backups that take days"
    echo "  • Enhanced monitoring and error handling"
    echo "  • Detailed time estimation and disk space checking"
    echo "  • Optimized for resilience and long-running sessions"
    echo ""
    
    echo "📱 Screen Session Commands:"
    echo "  Attach to session:    screen -r vps-backup-<name>"
    echo "  Detach from session:  Ctrl+A, then D"
    echo "  Kill session:         screen -S vps-backup-<name> -X quit"
    echo ""
    
    echo "🔧 Manual Commands:"
    echo "  Direct backup:        python3 main.py config.yaml"
    echo "  Quick bandwidth:      python3 quick_bandwidth.py"
    echo "  Interface test:       python3 test_multi_interface.py"
    echo "  SSH test:            ./test_ssh.sh config.yaml"
    echo ""
    
    echo "📊 Monitoring:"
    echo "  Live monitoring:     python3 monitor_bandwidth.py config.yaml monitor 60 5"
    echo "  Interface demo:      python3 demo_multi_interface.py"
    echo ""
    
    echo "🏗️ Project Structure:"
    echo "  backup_data/         - Local backup storage"
    echo "  logs/               - Log files"
    echo "  tmp/                - Temporary files"
    echo "  pids/               - Screen session info"
}

main_loop() {
    while true; do
        clear
        print_logo
        print_main_menu
        
        read -p "Select option [0]: " choice
        choice=${choice:-0}
        
        echo ""
        
        case $choice in
            1)
                backup_quick
                ;;
            2)
                backup_test
                ;;
            3)
                backup_production
                ;;
            4)
                echo -e "${BLUE}📅 Long-term Backup${NC}"
                echo "Launching specialized long-term backup menu..."
                echo ""
                ./long_backup.sh
                ;;
            5)
                monitoring_only
                ;;
            6)
                ./screen_manager.sh list
                ;;
            7)
                echo "Active sessions:"
                ./screen_manager.sh list
                echo ""
                read -p "Session name to attach: " session_name
                if [[ -n "$session_name" ]]; then
                    ./screen_manager.sh attach "$session_name"
                fi
                ;;
            8)
                echo "Active sessions:"
                ./screen_manager.sh list
                echo ""
                read -p "Session name to stop: " session_name
                if [[ -n "$session_name" ]]; then
                    ./screen_manager.sh stop "$session_name"
                fi
                ;;
            9)
                ./screen_manager.sh cleanup
                ;;
            10)
                setup_configuration
                ;;
            11)
                if [[ -f "test_ssh.sh" ]]; then
                    ./test_ssh.sh config.yaml
                else
                    echo "test_ssh.sh not found"
                fi
                ;;
            12)
                if [[ -f "test_multi_interface.py" ]]; then
                    python3 test_multi_interface.py config.yaml
                else
                    echo "test_multi_interface.py not found"
                fi
                ;;
            13)
                if [[ -f "quick_bandwidth.py" ]]; then
                    python3 quick_bandwidth.py config.yaml
                else
                    echo "quick_bandwidth.py not found"
                fi
                ;;
            14)
                show_documentation
                ;;
            15)
                show_help
                ;;
            0)
                echo -e "${GREEN}👋 Goodbye!${NC}"
                exit 0
                ;;
            *)
                echo -e "${RED}❌ Invalid option: $choice${NC}"
                ;;
        esac
        
        echo ""
        read -p "Press Enter to continue..." -r
    done
}

# Make sure screen_manager.sh is executable
chmod +x screen_manager.sh 2>/dev/null || true

# Start main loop
main_loop
