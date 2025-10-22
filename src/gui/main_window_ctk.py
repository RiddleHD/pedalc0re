#!/usr/bin/env python3
"""
Main Window - CustomTkinter Version
Ultra-modern GUI wie Discord/Spotify
"""

import customtkinter as ctk
from tkinter import messagebox
import sys
import os

# Import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from device.scanner import DeviceScanner
from device.calibration import PedalCalibrator
from gui.start_tab_ctk import StartTab
from gui.settings_tab_ctk import SettingsTab

class LinuxPedalManagerApp:
    def __init__(self, root):
        self.root = root

        # Device scanner
        self.scanner = DeviceScanner()

        # Shared calibrator for all tabs
        self.calibrator = PedalCalibrator()

        # Setup UI
        self.setup_ui()

        # Initial scan
        self.scan_devices()

    def setup_ui(self):
        """Setup the main UI"""
        # Main container with padding
        main_container = ctk.CTkFrame(self.root, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=0, pady=0)

        # Header
        header_frame = ctk.CTkFrame(main_container, fg_color=("#2b2b2b", "#1a1a1a"), corner_radius=0)
        header_frame.pack(fill="x", padx=0, pady=0)

        # Title with icon
        title_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        title_frame.pack(side="left", padx=20, pady=15)

        title_label = ctk.CTkLabel(
            title_frame,
            text="🎮 PedalC0re",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack()

        subtitle_label = ctk.CTkLabel(
            title_frame,
            text="by ChuxL_",
            font=ctk.CTkFont(size=11),
            text_color="gray60"
        )
        subtitle_label.pack()

        # Refresh button (modern style)
        refresh_btn = ctk.CTkButton(
            header_frame,
            text="🔄 Rescan Devices",
            command=self.scan_devices,
            fg_color="transparent",
            border_width=2,
            border_color=("#3b8ed0", "#1f6aa5"),
            width=140,
            height=35,
            corner_radius=8,
            font=ctk.CTkFont(size=12)
        )
        refresh_btn.pack(side="right", padx=20, pady=15)

        # Device info section (cards)
        self.device_section = ctk.CTkFrame(main_container, fg_color="transparent")
        self.device_section.pack(fill="x", padx=20, pady=10)

        # Tabview for different sections
        self.tabview = ctk.CTkTabview(main_container, corner_radius=15)
        self.tabview.pack(fill="both", expand=True, padx=20, pady=10)

        # Create tabs (NUR 2 - Monitor ist jetzt auf Start Page!)
        self.tabview.add("🏠 Start")
        self.tabview.add("⚙️ Settings")

        # Initialize tab content (pass self to start_tab for rescan)
        self.start_tab = StartTab(self.tabview.tab("🏠 Start"), self.scanner, self.calibrator, main_window=self)
        self.settings_tab = SettingsTab(self.tabview.tab("⚙️ Settings"), self.scanner, self.calibrator)

        # Status bar
        status_frame = ctk.CTkFrame(main_container, fg_color=("#2b2b2b", "#1a1a1a"), corner_radius=0, height=40)
        status_frame.pack(fill="x", side="bottom", padx=0, pady=0)
        status_frame.pack_propagate(False)

        self.status_label = ctk.CTkLabel(
            status_frame,
            text="Ready",
            font=ctk.CTkFont(size=11),
            anchor="w"
        )
        self.status_label.pack(side="left", padx=20, pady=10)

    def scan_devices(self):
        """Scan for devices"""
        self.scanner.scan()
        self.update_device_display()

        # Update all tabs
        if hasattr(self.start_tab, 'update_device_labels'):
            self.start_tab.update_device_labels()

        self.status_label.configure(text=f"✅ Found: {len(self.scanner.devices)} devices")

    def update_device_display(self):
        """Update device display in header"""
        # Clear old widgets
        for widget in self.device_section.winfo_children():
            widget.destroy()

        if not self.scanner.devices:
            no_device_label = ctk.CTkLabel(
                self.device_section,
                text="❌ No devices found - Click Rescan",
                font=ctk.CTkFont(size=12),
                text_color=("#ff4444", "#cc0000")
            )
            no_device_label.pack(pady=10)
            return

        # Create device cards
        devices_container = ctk.CTkFrame(self.device_section, fg_color="transparent")
        devices_container.pack(fill="x")

        for device in self.scanner.devices:
            self.create_device_card(devices_container, device)

    def create_device_card(self, parent, device):
        """Create a modern device card"""
        # Determine colors based on device type
        if "wheelbase" in device['type'].lower():
            icon = "🎮"
            border_color = ("#3b8ed0", "#1f6aa5")  # Blue
        else:
            icon = "🦶"
            border_color = ("#28a745", "#1e7e34")  # Green

        card = ctk.CTkFrame(
            parent,
            border_width=2,
            border_color=border_color,
            corner_radius=12,
            fg_color=("#2b2b2b", "#1e1e1e")
        )
        card.pack(side="left", padx=10, pady=10, fill="both", expand=True)

        # Icon
        icon_label = ctk.CTkLabel(
            card,
            text=icon,
            font=ctk.CTkFont(size=32)
        )
        icon_label.pack(side="left", padx=15, pady=10)

        # Info
        info_frame = ctk.CTkFrame(card, fg_color="transparent")
        info_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        name_label = ctk.CTkLabel(
            info_frame,
            text=device['name'],
            font=ctk.CTkFont(size=13, weight="bold"),
            anchor="w"
        )
        name_label.pack(anchor="w")

        type_label = ctk.CTkLabel(
            info_frame,
            text=device['type'],
            font=ctk.CTkFont(size=11),
            text_color="gray70",
            anchor="w"
        )
        type_label.pack(anchor="w", pady=2)

        path_label = ctk.CTkLabel(
            info_frame,
            text=device['path'],
            font=ctk.CTkFont(size=10),
            text_color="gray50",
            anchor="w"
        )
        path_label.pack(anchor="w")
