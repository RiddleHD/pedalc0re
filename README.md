# 🎮 PedalC0re
**by ChuxL_**

> The ultimate solution for racing pedal detection issues on Linux

A modern, powerful tool that makes racing games (ACC, iRacing, RaceRoom, etc.) detect your separate pedal devices on Linux/Proton.

---

## 🚀 Features

- **🔧 Pedal Enhancer** - Adds dummy buttons to pedal devices for game compatibility
- **⚙️ Full Calibration** - Deadzone, Min/Max range, Response curves
- **📊 Live Monitor** - Real-time pedal input visualization
- **💾 Preset System** - Save and load calibration profiles
- **🎨 Modern UI** - CustomTkinter dark theme interface
- **🌐 Universal** - Works with any racing pedals

---

## ⚡ Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/RiddleHD/pedalc0re
cd pedalc0re

# 2. Install dependencies
pip3 install --user -r requirements.txt

# 3. Run the app
cd src
python3 main.py
```

**In the app:**
1. Click **START** → Creates enhanced pedals (js2)
2. In your game: Select **js2** for pedals
3. Done! 🏁

---

## 🎯 The Problem

Racing games on Linux/Proton often **ignore separate pedal devices** because they lack buttons. Only devices with buttons or Force Feedback are recognized as "gaming controllers".

**Example:**
- ✅ Wheelbase (js0) - Has FF + Buttons → **Detected**
- ❌ Pedals (js1) - Only axes, no buttons → **Ignored**

---

## 💡 The Solution

**PedalC0re** creates an "enhanced" version of your pedals:
- Reads from **js1** (original pedals)
- Creates **js2** (enhanced pedals with 4 dummy buttons)
- Games see **both devices** separately!

**Result:**
- Wheelbase: js0 (unchanged)
- Pedals: js2 (enhanced, with buttons)
- **Both detected by ACC, iRacing, RaceRoom, etc.!**

---

## 🎮 Tested Hardware

### ✅ Confirmed Working
- **Simsonn Plus X** - 3-axis pedals
- **Moza R5/R9/R12/R16/R21** - Wheelbase

### 🤔 Should Work (Untested)
- Thrustmaster T3PA pedals
- Fanatec CSL Pedals (when used separately)
- Any 2-3 axis pedal device without buttons

**Tested your hardware?** Open an issue and let us know!

---

## ⚙️ Advanced Features

### Calibration
- **Deadzone** - Ignore first X% of travel
- **Min/Max Range** - Adjust usable range
- **Response Curves:**
  - Linear (default)
  - Exponential (less sensitive at start)
  - Logarithmic (more sensitive at start)
- **Invert** - Reverse axis direction

### Presets
Save different configurations for different games!

---

## 🛠️ Setup for Assetto Corsa Competizione

**Steam Launch Options:**
```
SDL_JOYSTICK_DEVICE=/dev/input/js2 %command%
```

**In ACC:**
1. Options → Controls
2. Wheelbase: Select **js0** (your original wheelbase)
3. Pedals: Select **js2** (Enhanced Pedals)
4. Bind axes:
   - Throttle → Axis 0
   - Brake → Axis 1
   - Clutch → Axis 2

**Proton Version:** Works best with **Proton-CachyOS** or **Proton Experimental**

---

## 📦 Installation

### Prerequisites
- Python 3.9+
- tkinter (usually pre-installed)

### Quick Install
```bash
git clone https://github.com/RiddleHD/pedalc0re
cd pedalc0re
pip3 install --user -r requirements.txt
```

### Setup udev Rules (Required!)
```bash
# uinput access
echo 'KERNEL=="uinput", MODE="0660", GROUP="input", TAG+="uaccess"' | sudo tee /etc/udev/rules.d/99-uinput.rules

# Add user to input group
sudo usermod -a -G input $USER

# Reload udev
sudo udevadm control --reload-rules
sudo udevadm trigger

# Load uinput module
sudo modprobe uinput
```

**Then log out and log back in!**

---

## 🐛 Troubleshooting

### "Permission denied for /dev/uinput"
```bash
sudo chmod 666 /dev/uinput  # Quick fix
# OR log out/in after setup
```

### "Pedals not detected"
1. Check: `ls -la /dev/input/js*`
2. Click **Rescan** in app
3. Verify pedals have no buttons: `cat /proc/bus/input/devices | grep -A 10 "YOUR_PEDAL_NAME"`

### "Enhanced device (js2) not created"
```bash
sudo modprobe uinput
ls -la /dev/uinput
```

---

## 📸 Screenshots

_Coming soon!_

---

## 🙏 Credits

- **Created by:** ChuxL_
- **Inspired by:** Boxflat (Moza manager)
- **Built for:** Linux sim-racing community
- **Technology:** Python, CustomTkinter, python-evdev

---

## 📝 License

MIT License - See [LICENSE](LICENSE) file

---

## 🤝 Contributing

Found a bug? Want to add support for your pedals?

1. Open an [Issue](https://github.com/RiddleHD/pedalc0re/issues)
2. Submit a Pull Request
3. Share your setup!

---

## ⭐ Support

If PedalC0re helped you race on Linux, give it a star! ⭐

---

**Made with ❤️ for Linux sim-racers by ChuxL_**
