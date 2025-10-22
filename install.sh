#!/bin/bash
# PedalC0re - Installation Script
# by ChuxL_

set -e

echo "🎮 PedalC0re - Installation"
echo "by ChuxL_"
echo "====================================="
echo ""

# Check if running as root
if [ "$EUID" -eq 0 ]; then
   echo "❌ Please do NOT run as root!"
   echo "   Run: ./install.sh (without sudo)"
   exit 1
fi

# Check Python
echo "🔍 Checking Python..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found!"
    echo "   Install: sudo dnf install python3  (Fedora/Bazzite)"
    echo "   Or: sudo apt install python3  (Ubuntu/Debian)"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | awk '{print $2}')
echo "✅ Python $PYTHON_VERSION found"

# Install dependencies
echo ""
echo "🔍 Installing dependencies..."
pip3 install --user -r requirements.txt 2>&1 | grep -E "Successfully installed|Requirement already satisfied|evdev|customtkinter" || true
echo "✅ Dependencies installed"

# Install udev rules
echo ""
echo "🔧 Installing udev rules..."

# Moza/Boxflat rule
echo 'SUBSYSTEM=="tty", KERNEL=="ttyACM*", ATTRS{idVendor}=="346e", ACTION=="add", MODE="0666", TAG+="uaccess"' | sudo tee /etc/udev/rules.d/99-boxflat.rules > /dev/null

# uinput rule
echo 'KERNEL=="uinput", MODE="0660", GROUP="input", TAG+="uaccess"' | sudo tee /etc/udev/rules.d/99-uinput.rules > /dev/null

echo "✅ udev rules installed"

# Add user to input group
echo ""
echo "👤 Adding user to input group..."
sudo usermod -a -G input $USER
echo "✅ User added to input group"

# Reload udev
echo ""
echo "🔄 Reloading udev..."
sudo udevadm control --reload-rules
sudo udevadm trigger
echo "✅ udev reloaded"

# Load uinput module
echo ""
echo "🔧 Loading uinput kernel module..."
sudo modprobe uinput
echo "✅ uinput loaded"

# Create desktop entry (optional)
echo ""
read -p "📱 Create desktop launcher? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    DESKTOP_FILE="$HOME/.local/share/applications/pedalc0re.desktop"
    INSTALL_DIR="$(cd "$(dirname "$0")" && pwd)"

    cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Name=PedalC0re
Comment=Racing pedal enhancer for Linux by ChuxL_
Exec=python3 $INSTALL_DIR/src/main.py
Icon=applications-games
Terminal=false
Type=Application
Categories=Game;Utility;
EOF

    chmod +x "$DESKTOP_FILE"
    echo "✅ Desktop launcher created"
fi

echo ""
echo "======================================"
echo "🎉 PedalC0re Installation Complete!"
echo "======================================"
echo ""
echo "⚠️  IMPORTANT: Log out and log back in"
echo "   (or reboot) for group changes to take effect!"
echo ""
echo "🚀 To start PedalC0re:"
echo "   cd $(pwd)/src"
echo "   python3 main.py"
echo ""
echo "Or find 'PedalC0re' in your applications menu."
echo ""
echo "Happy racing! 🏁"
echo "- ChuxL_"
