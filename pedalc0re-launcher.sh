#!/bin/bash
# PedalC0re Launcher - Shows errors if crash

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/src"
python3 main.py

# If app crashes, show error
if [ $? -ne 0 ]; then
    echo ""
    echo "App crashed! Press Enter to close..."
    read
fi
