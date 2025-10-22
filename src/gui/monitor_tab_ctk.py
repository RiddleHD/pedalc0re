#!/usr/bin/env python3
"""
Monitor Tab - CustomTkinter Version
Live pedal monitoring mit modernen Progressbars
"""

import customtkinter as ctk
from tkinter import messagebox
import struct
import threading
import time
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Joystick event format
JS_EVENT_FMT = 'IhBB'
JS_EVENT_SIZE = struct.calcsize(JS_EVENT_FMT)
JS_EVENT_AXIS = 0x02
JS_EVENT_INIT = 0x80

class MonitorTab:
    def __init__(self, parent, scanner):
        self.parent = parent
        self.scanner = scanner
        self.is_monitoring = False
        self.monitor_thread = None

        self.setup_ui()

    def setup_ui(self):
        """Setup modern monitor UI"""
        # Title
        ctk.CTkLabel(
            self.parent,
            text="📊 Live Monitor",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=(20, 5))

        ctk.CTkLabel(
            self.parent,
            text="Real-time visualization of your pedal inputs",
            font=ctk.CTkFont(size=12),
            text_color="gray70"
        ).pack(pady=(0, 20))

        # Control buttons
        btn_frame = ctk.CTkFrame(self.parent, fg_color="transparent")
        btn_frame.pack(pady=15)

        self.start_btn = ctk.CTkButton(
            btn_frame,
            text="▶️  Start Monitoring",
            command=self.start_monitoring,
            fg_color=("#28a745", "#1e7e34"),
            hover_color=("#218838", "#155724"),
            width=180,
            height=40,
            corner_radius=10,
            font=ctk.CTkFont(size=13, weight="bold")
        )
        self.start_btn.pack(side="left", padx=10)

        self.stop_btn = ctk.CTkButton(
            btn_frame,
            text="⏹️  Stop",
            command=self.stop_monitoring,
            fg_color=("#dc3545", "#c82333"),
            hover_color=("#bd2130", "#a71d2a"),
            width=120,
            height=40,
            corner_radius=10,
            font=ctk.CTkFont(size=13),
            state="disabled"
        )
        self.stop_btn.pack(side="left", padx=10)

        # Pedal displays
        displays_frame = ctk.CTkFrame(self.parent, corner_radius=15)
        displays_frame.pack(fill="both", expand=True, padx=30, pady=20)

        self.pedal_displays = {}

        for pedal_name, pedal_label, color in [
            ('gas', 'Gas Pedal', ("#28a745", "#1e7e34")),
            ('brake', 'Brake Pedal', ("#dc3545", "#c82333")),
            ('clutch', 'Clutch Pedal', ("#ffc107", "#ff9800"))
        ]:
            self.create_pedal_display(displays_frame, pedal_name, pedal_label, color)

    def create_pedal_display(self, parent, pedal_name, label, color):
        """Create modern pedal display"""
        frame = ctk.CTkFrame(parent, corner_radius=12)
        frame.pack(fill="x", padx=20, pady=15)

        # Label
        ctk.CTkLabel(
            frame,
            text=label,
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w", padx=20, pady=(15, 10))

        # Progress bar
        bar_frame = ctk.CTkFrame(frame, fg_color="transparent")
        bar_frame.pack(fill="x", padx=20, pady=(0, 15))

        progressbar = ctk.CTkProgressBar(
            bar_frame,
            width=600,
            height=25,
            corner_radius=10,
            progress_color=color
        )
        progressbar.set(0)
        progressbar.pack(side="left", padx=5)

        # Value label
        value_label = ctk.CTkLabel(
            bar_frame,
            text="0.0%",
            width=70,
            font=ctk.CTkFont(size=13, weight="bold")
        )
        value_label.pack(side="left", padx=10)

        self.pedal_displays[pedal_name] = {
            'progressbar': progressbar,
            'label': value_label
        }

    def start_monitoring(self):
        """Start monitoring"""
        pedal_device = self.scanner.get_pedal_device()

        if not pedal_device:
            messagebox.showerror(
                "Error",
                "No pedals detected!\nPlease connect pedals and rescan."
            )
            return

        self.is_monitoring = True
        self.start_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")

        # Start monitoring thread
        self.monitor_thread = threading.Thread(
            target=self._monitor_loop,
            args=(pedal_device['path'],),
            daemon=True
        )
        self.monitor_thread.start()

    def stop_monitoring(self):
        """Stop monitoring"""
        self.is_monitoring = False
        self.start_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")

    def _monitor_loop(self, device_path):
        """Monitor loop"""
        try:
            with open(device_path, 'rb') as jsdev:
                while self.is_monitoring:
                    event_data = jsdev.read(JS_EVENT_SIZE)
                    if not event_data:
                        break

                    timestamp, value, event_type, number = struct.unpack(
                        JS_EVENT_FMT,
                        event_data
                    )

                    event_type &= ~JS_EVENT_INIT

                    if event_type == JS_EVENT_AXIS:
                        percentage = ((value + 32767) / 65534) * 100

                        pedal_names = {0: 'gas', 1: 'brake', 2: 'clutch'}
                        if number in pedal_names:
                            pedal = pedal_names[number]
                            self.parent.after(
                                0,
                                self._update_display,
                                pedal,
                                percentage
                            )

        except Exception as e:
            self.parent.after(
                0,
                lambda: messagebox.showerror("Error", f"Monitor error: {e}")
            )
            self.parent.after(0, self.stop_monitoring)

    def _update_display(self, pedal_name, percentage):
        """Update pedal display"""
        if pedal_name in self.pedal_displays:
            display = self.pedal_displays[pedal_name]
            display['progressbar'].set(percentage / 100.0)
            display['label'].configure(text=f"{percentage:.1f}%")
