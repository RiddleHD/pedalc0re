#!/bin/bash
# PedalC0re Launcher - Shows errors if crash

cd "/var/home/pierrel/Downloads/SEC TOOL/simsonn-manager-py/src"
python3 main.py

# If app crashes, show error
if [ $? -ne 0 ]; then
    echo ""
    echo "App crashed! Press Enter to close..."
    read
fi
