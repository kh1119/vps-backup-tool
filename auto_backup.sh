#!/usr/bin/env bash
# auto_backup.sh - Tự động khởi tạo backup với screen session

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="${1:-config.yaml}"
SESSION_NAME="${2:-auto-backup-$(date +%m%d-%H%M)}"
BACKUP_TYPE="${3:-full}"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🚀 Auto Backup Launcher${NC}"
echo "======================"
echo ""
echo "📋 Config: $CONFIG_FILE"
echo "🏷️  Session: $SESSION_NAME"
echo "📊 Type: $BACKUP_TYPE"
echo ""

# Validate config
if [[ ! -f "$CONFIG_FILE" ]]; then
    echo "❌ Config file not found: $CONFIG_FILE"
    exit 1
fi

# Check if screen is available
if ! command -v screen &> /dev/null; then
    echo "❌ Screen not installed!"
    echo ""
    echo "Install screen:"
    echo "  Rocky/RHEL/CentOS: sudo dnf install screen"
    echo "  Debian/Ubuntu:     sudo apt install screen"
    echo "  macOS:             brew install screen"
    exit 1
fi

# Start backup
echo -e "${YELLOW}Starting backup in screen session...${NC}"
"$SCRIPT_DIR/screen_manager.sh" start "$CONFIG_FILE" "$SESSION_NAME" "$BACKUP_TYPE"

echo ""
echo -e "${GREEN}✅ Backup started successfully!${NC}"
echo ""
echo "🔧 Management commands:"
echo "  📱 Attach:  ./screen_manager.sh attach $SESSION_NAME"
echo "  ⏹️  Stop:    ./screen_manager.sh stop $SESSION_NAME"
echo "  📋 List:    ./screen_manager.sh list"
echo ""
echo "🖥️  Direct screen commands:"
echo "  screen -r vps-backup-$SESSION_NAME    # Attach"
echo "  screen -ls                            # List all sessions"
echo ""
echo "⚠️  Remember: Use Ctrl+A, then D to detach (not Ctrl+C!)"
