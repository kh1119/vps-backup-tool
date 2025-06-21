#!/usr/bin/env bash
# backup_with_monitoring.sh - Script tiện ích để chạy backup với monitoring

set -euo pipefail

CONFIG_FILE="${1:-config.yaml}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "🔧 Backup Script with Bandwidth Monitoring"
echo "==========================================="
echo "📋 Config: $CONFIG_FILE"
echo "📁 Working directory: $SCRIPT_DIR"
echo ""

# Kiểm tra config file
if [[ ! -f "$CONFIG_FILE" ]]; then
    echo "❌ Config file not found: $CONFIG_FILE"
    echo "Available configs:"
    ls -la *.yaml 2>/dev/null || echo "  No .yaml files found"
    exit 1
fi

# Menu lựa chọn
echo "Please select an action:"
echo "1) Quick bandwidth check"
echo "2) Start backup with monitoring"
echo "3) Monitor bandwidth only (60s)"
echo "4) Show help"
echo ""
read -p "Enter choice [1-4]: " choice

case $choice in
    1)
        echo "🔍 Running quick bandwidth check..."
        python3 "$SCRIPT_DIR/quick_bandwidth.py" "$CONFIG_FILE"
        ;;
    2)
        echo "🚀 Starting backup with integrated monitoring..."
        echo "Press Ctrl+C to stop"
        echo ""
        python3 "$SCRIPT_DIR/main.py" "$CONFIG_FILE"
        ;;
    3)
        echo "📊 Monitoring bandwidth for 60 seconds..."
        python3 "$SCRIPT_DIR/monitor_bandwidth.py" "$CONFIG_FILE" monitor 60 5
        ;;
    4)
        echo "📖 Help:"
        echo "  $0 [config_file]"
        echo ""
        echo "Available commands:"
        echo "  python3 main.py [config]           - Run backup with monitoring"
        echo "  python3 quick_bandwidth.py [config] - Quick bandwidth check"
        echo "  python3 monitor_bandwidth.py [config] monitor [duration] [interval] - Monitor only"
        echo ""
        echo "Example configs:"
        echo "  config.yaml      - Full backup"
        echo "  config_test.yaml - Test backup (small files)"
        ;;
    *)
        echo "❌ Invalid choice"
        exit 1
        ;;
esac
