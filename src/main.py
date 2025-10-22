#!/usr/bin/env python3
"""
Linux Pedal Manager
A powerful tool for managing racing pedals on Linux

Features:
- Pedal Enhancer (adds dummy buttons for game compatibility)
- Full Calibration System
- Live Monitoring
- Preset Management
- Universal device support
"""

import customtkinter as ctk
import sys
import os

# Pfad zum src-Verzeichnis hinzufügen
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gui.main_window_ctk import LinuxPedalManagerApp

def main():
    """Main entry point"""
    # Set appearance and color theme
    ctk.set_appearance_mode("dark")  # "dark", "light", "system"
    ctk.set_default_color_theme("blue")  # "blue", "green", "dark-blue"

    # Create modern window
    root = ctk.CTk()
    root.title("PedalC0re by ChuxL_")
    root.geometry("1280x880")
    root.resizable(False, False)  # Fixed size

    app = LinuxPedalManagerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
