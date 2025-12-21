#!/bin/bash
# Kill any hanging server processes (supports dynamic ports)

PORT=${1:-5555}  # Use provided port or default to 5555

echo "Checking for processes on port ${PORT}..."

# Find and kill processes using the specified port
PIDS=$(lsof -t -i:${PORT} 2>/dev/null)

if [ -z "$PIDS" ]; then
    echo "✓ No processes found on port ${PORT}"
    exit 0
fi

echo "Found process(es) on port ${PORT}:"
lsof -i:${PORT}

echo ""
echo "Killing processes: $PIDS"
kill -9 $PIDS 2>/dev/null

sleep 1

# Verify they're gone
if lsof -i:${PORT} >/dev/null 2>&1; then
    echo "⚠️  Warning: Some processes may still be running"
    lsof -i:${PORT}
    exit 1
else
    echo "✓ All processes on port ${PORT} have been killed"
    exit 0
fi
