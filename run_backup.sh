#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="."
LOG_DIR="logs"

# timestamp
TS=$(date +"%F_%H%M%S")
mkdir -p "$LOG_DIR/$TS"

# Run backup
python3 "$SCRIPT_DIR/main.py" | tee "$LOG_DIR/$TS/backup_run.log"
