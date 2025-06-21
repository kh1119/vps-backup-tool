#!/bin/bash
# Simple startup script for VPS Backup Tool

echo "🚀 Starting VPS Backup Tool v2.0..."
echo "=================================="

# Check if Python 3 is available
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo "❌ Python not found! Please install Python 3.6 or higher."
    exit 1
fi

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Change to script directory
cd "$SCRIPT_DIR"

# Run the application
echo "Starting application with $PYTHON_CMD..."
exec "$PYTHON_CMD" app.py "$@"
