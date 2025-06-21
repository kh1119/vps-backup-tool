#!/usr/bin/env bash
# demo_screen.sh - Demo script để test screen functionality

set -euo pipefail

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${BLUE}🎭 Screen Demo for VPS Backup${NC}"
echo "============================="
echo ""

echo -e "${YELLOW}📋 This demo will show you how screen works for long-running backups${NC}"
echo ""

# Check if screen is installed
if ! command -v screen &> /dev/null; then
    echo -e "${RED}❌ Screen not installed!${NC}"
    echo ""
    echo "Install screen first:"
    echo "  Rocky/RHEL/CentOS: sudo dnf install screen"
    echo "  Debian/Ubuntu:     sudo apt install screen"
    echo "  macOS:             brew install screen"
    exit 1
fi

echo -e "${GREEN}✅ Screen is installed${NC}"
echo ""

echo "🎯 What this demo will do:"
echo "  1. Create a screen session running a mock backup"
echo "  2. Show you how to detach and reattach"
echo "  3. Demonstrate long-running process management"
echo ""

read -p "Continue with demo? [y/N] " -n 1 -r
echo

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Demo cancelled."
    exit 0
fi

SESSION_NAME="backup-demo-$(date +%H%M%S)"

echo ""
echo -e "${CYAN}🚀 Starting demo session: $SESSION_NAME${NC}"
echo ""

# Create screen session with demo backup
screen -dmS "$SESSION_NAME" bash -c '
    echo "🎭 VPS Backup Demo Session"
    echo "========================="
    echo ""
    echo "This is a mock backup that will run for 60 seconds"
    echo "to demonstrate how screen sessions work."
    echo ""
    echo "⏰ Started at: $(date)"
    echo ""
    
    for i in {1..60}; do
        echo "📦 Processing file batch $i/60 ($(date +%H:%M:%S))"
        
        # Simulate different backup activities
        case $((i % 4)) in
            0) echo "   📁 Scanning directories..." ;;
            1) echo "   🔄 Syncing files..." ;;
            2) echo "   📊 Checking bandwidth..." ;;
            3) echo "   💾 Updating checksums..." ;;
        esac
        
        sleep 1
    done
    
    echo ""
    echo "✅ Demo backup completed!"
    echo "⏰ Finished at: $(date)"
    echo ""
    echo "In a real backup, this would transfer your VPS data."
    echo ""
    echo "Press any key to exit this demo session..."
    read -n 1
'

# Wait a moment for session to start
sleep 2

if screen -ls | grep -q "$SESSION_NAME"; then
    echo -e "${GREEN}✅ Demo session started successfully!${NC}"
    echo ""
    echo -e "${CYAN}🎮 Demo Instructions:${NC}"
    echo ""
    echo "1️⃣  Attach to the session:"
    echo "   screen -r $SESSION_NAME"
    echo ""
    echo "2️⃣  Watch the mock backup run for a minute"
    echo ""
    echo "3️⃣  Practice detaching (VERY IMPORTANT):"
    echo "   Press: Ctrl+A, then D"
    echo "   (NOT Ctrl+C - that would kill the backup!)"
    echo ""
    echo "4️⃣  Reattach to see it's still running:"
    echo "   screen -r $SESSION_NAME"
    echo ""
    echo "5️⃣  Let it complete or kill the session:"
    echo "   screen -S $SESSION_NAME -X quit"
    echo ""
    
    echo -e "${YELLOW}💡 Key Points for Real Backups:${NC}"
    echo "   • Use meaningful session names with dates"
    echo "   • Always detach with Ctrl+A, D (never Ctrl+C)"
    echo "   • Long backups can run for days safely"
    echo "   • You can disconnect SSH and reconnect later"
    echo "   • Check logs regularly: tail -f logs/backup_*.log"
    echo ""
    
    echo -e "${CYAN}🔧 Session Management Commands:${NC}"
    echo "   List sessions:    screen -ls"
    echo "   Attach:          screen -r $SESSION_NAME"
    echo "   Kill session:    screen -S $SESSION_NAME -X quit"
    echo "   Our tool:        ./screen_manager.sh list"
    echo ""
    
    read -p "Attach to the demo session now? [y/N] " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo ""
        echo -e "${YELLOW}⚠️  Remember: Use Ctrl+A, then D to detach!${NC}"
        sleep 3
        screen -r "$SESSION_NAME"
    else
        echo ""
        echo "Demo session is running in background."
        echo "You can attach later with: screen -r $SESSION_NAME"
    fi
    
else
    echo -e "${RED}❌ Failed to start demo session${NC}"
fi
