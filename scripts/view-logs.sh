#!/bin/bash
# View logs from the compiled app

set -e

LOG_DIR="$HOME/Library/Logs/BrowserAutomation"

echo "========================================"
echo "Browser Automation App Logs"
echo "========================================"
echo ""
echo "Log directory: $LOG_DIR"
echo ""

if [ ! -d "$LOG_DIR" ]; then
    echo "Log directory does not exist yet."
    echo "The app will create it on first run."
    exit 0
fi

# Find the most recent log file
LATEST_LOG=$(find "$LOG_DIR" -name "*.log" -type f -print0 | xargs -0 ls -t | head -1)

if [ -z "$LATEST_LOG" ]; then
    echo "No log files found."
    echo ""
    echo "Available files:"
    ls -lh "$LOG_DIR"
    exit 0
fi

echo "Latest log file: $LATEST_LOG"
echo "Last modified: $(stat -f "%Sm" -t "%Y-%m-%d %H:%M:%S" "$LATEST_LOG")"
echo ""
echo "========================================"
echo ""

# Check if user wants to tail or cat
if [ "$1" == "--follow" ] || [ "$1" == "-f" ]; then
    echo "Following log file (Ctrl+C to stop)..."
    echo ""
    tail -f "$LATEST_LOG"
else
    cat "$LATEST_LOG"
    echo ""
    echo "========================================"
    echo ""
    echo "To follow logs in real-time, run:"
    echo "  $0 --follow"
    echo ""
    echo "To open log directory in Finder:"
    echo "  open \"$LOG_DIR\""
fi
