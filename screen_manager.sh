#!/usr/bin/env bash
# screen_manager.sh - Quản lý backup sessions với screen

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SESSION_PREFIX="vps-backup"
PID_DIR="$SCRIPT_DIR/pids"

# Tạo thư mục PID nếu chưa có
mkdir -p "$PID_DIR"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}  VPS Backup Screen Manager${NC}"
    echo -e "${BLUE}================================${NC}"
}

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_screen() {
    if ! command -v screen &> /dev/null; then
        print_error "Screen is not installed!"
        echo ""
        echo "Install screen:"
        echo "  Rocky/RHEL/CentOS: sudo dnf install screen"
        echo "  Debian/Ubuntu:     sudo apt install screen"
        echo "  macOS:             brew install screen"
        exit 1
    fi
}

list_sessions() {
    print_status "Active backup sessions:"
    echo ""
    
    local sessions=$(screen -ls 2>/dev/null | grep "$SESSION_PREFIX" | awk '{print $1}' || true)
    
    if [[ -z "$sessions" ]]; then
        echo "  No active backup sessions found."
        return
    fi
    
    echo -e "${CYAN}Session Name${NC}            ${CYAN}Status${NC}      ${CYAN}Config${NC}           ${CYAN}Started${NC}"
    echo "--------------------------------------------------------------------------------"
    
    while IFS= read -r session; do
        if [[ -n "$session" ]]; then
            local session_name=$(echo "$session" | cut -d'.' -f2)
            local config_file=""
            local start_time=""
            local pid_file="$PID_DIR/${session_name}.pid"
            
            # Đọc thông tin từ PID file nếu có
            if [[ -f "$pid_file" ]]; then
                config_file=$(grep "CONFIG=" "$pid_file" 2>/dev/null | cut -d'=' -f2 || echo "unknown")
                start_time=$(grep "START_TIME=" "$pid_file" 2>/dev/null | cut -d'=' -f2 || echo "unknown")
            fi
            
            # Check session status
            local status="Running"
            if ! screen -S "$session" -Q select . &>/dev/null; then
                status="Detached"
            fi
            
            printf "%-20s %-10s %-15s %s\n" "$session_name" "$status" "$config_file" "$start_time"
        fi
    done <<< "$sessions"
}

start_backup() {
    local config_file="${1:-config.yaml}"
    local session_name="${2:-backup-$(date +%H%M%S)}"
    local backup_type="${3:-full}"
    
    # Validate config file
    if [[ ! -f "$config_file" ]]; then
        print_error "Config file not found: $config_file"
        return 1
    fi
    
    local full_session_name="${SESSION_PREFIX}-${session_name}"
    
    # Check if session already exists
    if screen -ls | grep -q "$full_session_name"; then
        print_error "Session '$session_name' already exists!"
        return 1
    fi
    
    print_status "Starting backup session: $session_name"
    print_status "Config: $config_file"
    print_status "Type: $backup_type"
    
    # Create PID file with session info
    local pid_file="$PID_DIR/${session_name}.pid"
    cat > "$pid_file" << EOF
SESSION_NAME=$session_name
CONFIG=$config_file
BACKUP_TYPE=$backup_type
START_TIME=$(date '+%Y-%m-%d %H:%M:%S')
PID=$$
EOF
    
    # Determine backup command
    local backup_cmd=""
    case "$backup_type" in
        "full")
            backup_cmd="python3 main.py $config_file"
            ;;
        "full-no-monitor")
            backup_cmd="python3 main.py $config_file --no-bandwidth-monitor"
            ;;
        "test")
            backup_cmd="python3 main.py config_test.yaml"
            ;;
        "monitor-only")
            backup_cmd="python3 monitor_bandwidth.py $config_file monitor 3600 10"
            ;;
        "long-term")
            backup_cmd="python3 main.py $config_file --long-term"
            ;;
        *)
            backup_cmd="python3 main.py $config_file"
            ;;
    esac
    
    # Start screen session
    screen -dmS "$full_session_name" bash -c "
        cd '$SCRIPT_DIR'
        echo '🚀 Backup session started: $session_name'
        echo '📋 Config: $config_file'
        echo '⏰ Started at: \$(date)'
        echo '📊 Type: $backup_type'
        echo '🖥️  Session: $full_session_name'
        echo '================================'
        echo ''
        echo '💡 Tips:'
        echo '  • Use Ctrl+A, then D to detach (not Ctrl+C!)'
        echo '  • Check logs: tail -f logs/backup_*.log'
        echo '  • Monitor: python3 quick_bandwidth.py'
        echo ''
        
        # Set up signal handlers for graceful shutdown
        trap 'echo \"⚠️  Received interrupt signal. Cleaning up...\"; kill -TERM \$backup_pid 2>/dev/null; exit 130' INT TERM
        
        # Run backup with error handling
        echo '🔄 Starting backup process...'
        $backup_cmd &
        backup_pid=\$!
        
        # Wait for backup to complete
        if wait \$backup_pid; then
            echo ''
            echo '✅ Backup completed successfully!'
            echo '⏰ Finished at: \$(date)'
            echo '📊 Check backup_data/ for results'
        else
            exit_code=\$?
            echo ''
            if [ \$exit_code -eq 130 ]; then
                echo '⚠️  Backup was interrupted by user'
            else
                echo '❌ Backup failed with exit code: \$exit_code'
            fi
            echo '⏰ Stopped at: \$(date)'
            echo '📋 Check logs in logs/ directory for details'
        fi
        
        echo ''
        echo '🏁 Session will remain open for review'
        echo 'Press any key to exit this session...'
        read -n 1
    "
    
    # Wait a moment for session to start
    sleep 1
    
    if screen -ls | grep -q "$full_session_name"; then
        print_status "Session '$session_name' started successfully!"
        echo ""
        echo "Commands to manage this session:"
        echo "  Attach:  screen -r $full_session_name"
        echo "  Detach:  Ctrl+A, then D"
        echo "  Kill:    screen -S $full_session_name -X quit"
        echo ""
        echo "Or use this script:"
        echo "  Attach:  $0 attach $session_name"
        echo "  Stop:    $0 stop $session_name"
        echo "  Status:  $0 list"
    else
        print_error "Failed to start session '$session_name'"
        rm -f "$pid_file"
        return 1
    fi
}

attach_session() {
    local session_name="${1:-}"
    
    if [[ -z "$session_name" ]]; then
        print_error "Session name required!"
        echo "Usage: $0 attach <session_name>"
        return 1
    fi
    
    local full_session_name="${SESSION_PREFIX}-${session_name}"
    
    if ! screen -ls | grep -q "$full_session_name"; then
        print_error "Session '$session_name' not found!"
        echo ""
        echo "Available sessions:"
        list_sessions
        return 1
    fi
    
    print_status "Attaching to session: $session_name"
    print_warning "Use Ctrl+A, then D to detach (don't use Ctrl+C!)"
    sleep 2
    
    screen -r "$full_session_name"
}

stop_session() {
    local session_name="${1:-}"
    
    if [[ -z "$session_name" ]]; then
        print_error "Session name required!"
        echo "Usage: $0 stop <session_name>"
        return 1
    fi
    
    local full_session_name="${SESSION_PREFIX}-${session_name}"
    
    if ! screen -ls | grep -q "$full_session_name"; then
        print_error "Session '$session_name' not found!"
        return 1
    fi
    
    print_warning "Stopping session: $session_name"
    read -p "Are you sure? [y/N] " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        screen -S "$full_session_name" -X quit
        rm -f "$PID_DIR/${session_name}.pid"
        print_status "Session '$session_name' stopped."
    else
        print_status "Cancelled."
    fi
}

cleanup_dead_sessions() {
    print_status "Cleaning up dead sessions..."
    
    # Remove PID files for non-existent sessions
    for pid_file in "$PID_DIR"/*.pid; do
        if [[ -f "$pid_file" ]]; then
            local session_name=$(basename "$pid_file" .pid)
            local full_session_name="${SESSION_PREFIX}-${session_name}"
            
            if ! screen -ls | grep -q "$full_session_name"; then
                print_status "Removing dead session info: $session_name"
                rm -f "$pid_file"
            fi
        fi
    done
}

show_help() {
    echo "VPS Backup Screen Manager"
    echo ""
    echo "Usage: $0 <command> [options]"
    echo ""
    echo "Commands:"
    echo "  start <config> [name] [type]  - Start backup in screen session"
    echo "  list                          - List active sessions"
    echo "  attach <name>                 - Attach to session"
    echo "  stop <name>                   - Stop session"
    echo "  cleanup                       - Clean up dead sessions"
    echo "  help                          - Show this help"
    echo ""
    echo "Backup types:"
    echo "  full              - Full backup with monitoring (default)"
    echo "  full-no-monitor   - Full backup without bandwidth monitoring"
    echo "  test              - Test backup (smaller directory)"
    echo "  monitor-only      - Bandwidth monitoring only"
    echo "  long-term         - Optimized for multi-day backups"
    echo ""
    echo "Examples:"
    echo "  $0 start config.yaml                       # Quick start"
    echo "  $0 start config.yaml my-backup full        # Named full backup"
    echo "  $0 start config.yaml long-run long-term    # Long-term backup"
    echo "  $0 start config_test.yaml test-run test    # Test backup"
    echo "  $0 attach my-backup                        # Attach to session"
    echo "  $0 list                                    # Show all sessions"
    echo ""
    echo "Screen commands (when attached):"
    echo "  Ctrl+A, D       - Detach (keep running) ⭐ RECOMMENDED"
    echo "  Ctrl+C          - Interrupt current command"
    echo "  exit            - Exit session"
    echo ""
    echo "Long-term backup tips:"
    echo "  • Use meaningful session names with dates"
    echo "  • Monitor bandwidth to avoid network issues"
    echo "  • Check logs regularly: tail -f logs/backup_*.log"
    echo "  • NEVER use Ctrl+C to exit - use Ctrl+A, D instead"
}

main() {
    check_screen
    
    local command="${1:-help}"
    
    case "$command" in
        "start")
            print_header
            start_backup "${2:-config.yaml}" "${3:-backup-$(date +%H%M%S)}" "${4:-full}"
            ;;
        "list"|"ls")
            print_header
            list_sessions
            ;;
        "attach"|"a")
            attach_session "${2:-}"
            ;;
        "stop"|"kill")
            stop_session "${2:-}"
            ;;
        "cleanup")
            print_header
            cleanup_dead_sessions
            ;;
        "help"|"-h"|"--help")
            show_help
            ;;
        *)
            print_error "Unknown command: $command"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

# Chạy script
main "$@"
