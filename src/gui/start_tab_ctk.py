#!/usr/bin/env python3
"""
Start Tab - CustomTkinter Version
Modern Dashboard mit Pedal Enhancer
"""

import customtkinter as ctk
from tkinter import messagebox
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from device.pedal_enhancer import PedalEnhancer

class StartTab:
    def __init__(self, parent, scanner, calibrator, main_window=None):
        self.parent = parent
        self.scanner = scanner
        self.calibrator = calibrator
        self.main_window = main_window
        self.is_running = False
        self.is_monitoring = False
        self.enhancer = None
        self.monitor_thread = None
        self.pedal_displays = {}

        self.setup_ui()

    def setup_ui(self):
        """Setup modern dashboard"""
        # Connected Devices Card (direkt ohne Welcome)
        devices_card = ctk.CTkFrame(self.parent, corner_radius=10)
        devices_card.pack(fill="x", padx=20, pady=(15, 10))

        ctk.CTkLabel(
            devices_card,
            text="📡 Devices",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w", padx=15, pady=(10, 5))

        # Pedals status
        pedal_frame = ctk.CTkFrame(devices_card, fg_color="transparent")
        pedal_frame.pack(fill="x", padx=20, pady=10)

        ctk.CTkLabel(
            pedal_frame,
            text="🦶 Pedals:",
            font=ctk.CTkFont(size=13, weight="bold"),
            width=100,
            anchor="w"
        ).pack(side="left")

        self.pedal_status = ctk.CTkLabel(
            pedal_frame,
            text="❌ Not detected",
            font=ctk.CTkFont(size=12),
            text_color=("#ff4444", "#cc0000")
        )
        self.pedal_status.pack(side="left", padx=10)

        self.update_device_labels()

        # Enhancer Control
        enhancer_card = ctk.CTkFrame(self.parent, corner_radius=10)
        enhancer_card.pack(fill="x", padx=20, pady=10)

        ctk.CTkLabel(
            enhancer_card,
            text="🔧 Enhancer",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w", padx=15, pady=(10, 5))

        # Status + Toggle Button in one row
        control_frame = ctk.CTkFrame(enhancer_card, fg_color="transparent")
        control_frame.pack(fill="x", padx=15, pady=(5, 10))

        self.status_indicator = ctk.CTkLabel(
            control_frame,
            text="⏹️ Stopped",
            font=ctk.CTkFont(size=11),
            text_color="gray60",
            width=120,
            anchor="w"
        )
        self.status_indicator.pack(side="left", padx=5)

        # TOGGLE BUTTON (Start/Stop in one)
        self.toggle_btn = ctk.CTkButton(
            control_frame,
            text="▶️  START",
            command=self.toggle_enhancer,
            fg_color=("#28a745", "#1e7e34"),
            hover_color=("#218838", "#155724"),
            height=40,
            width=200,
            corner_radius=8,
            font=ctk.CTkFont(size=13, weight="bold")
        )
        self.toggle_btn.pack(side="left", padx=10)

        # Live Monitor Card
        monitor_card = ctk.CTkFrame(self.parent, corner_radius=10)
        monitor_card.pack(fill="both", expand=True, padx=20, pady=10)

        ctk.CTkLabel(
            monitor_card,
            text="📊 Live",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w", padx=15, pady=(10, 5))

        # Create monitor displays for each pedal
        for pedal_name, label, color in [
            ('gas', 'Throttle', ("#28a745", "#1e7e34")),
            ('brake', 'Brake', ("#dc3545", "#c82333")),
            ('clutch', 'Clutch', ("#ffc107", "#ff9800"))
        ]:
            self.create_pedal_monitor(monitor_card, pedal_name, label, color)


    def create_pedal_monitor(self, parent, pedal_name, label, color):
        """Create compact pedal monitor"""
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", padx=15, pady=5)

        # Label (kompakt)
        ctk.CTkLabel(
            frame,
            text=f"{label}:",
            font=ctk.CTkFont(size=11),
            width=60,
            anchor="w"
        ).pack(side="left")

        # Progressbar
        progressbar = ctk.CTkProgressBar(
            frame,
            width=400,
            height=18,
            corner_radius=8,
            progress_color=color
        )
        progressbar.set(0)
        progressbar.pack(side="left", padx=5)

        # Value label
        value_label = ctk.CTkLabel(
            frame,
            text="0%",
            width=50,
            font=ctk.CTkFont(size=11),
            anchor="e"
        )
        value_label.pack(side="left", padx=5)

        self.pedal_displays[pedal_name] = {
            'progressbar': progressbar,
            'label': value_label
        }

    def toggle_enhancer(self):
        """Toggle enhancer on/off"""
        if not self.is_running:
            self.start_enhancer()
        else:
            self.stop_enhancer()

    def update_device_labels(self):
        """Update device status"""
        pedals = self.scanner.get_pedal_device()

        if pedals:
            self.pedal_status.configure(
                text=f"✅ {pedals['name']} (js1)",
                text_color=("#28a745", "#1e7e34")
            )
        else:
            self.pedal_status.configure(
                text="❌ Not detected",
                text_color=("#ff4444", "#cc0000")
            )

    def start_enhancer(self):
        """Start Pedal Enhancer"""
        pedals = self.scanner.get_pedal_device()

        if not pedals:
            messagebox.showerror(
                "Error",
                "No pedals detected!\nPlease connect your pedals and click Rescan."
            )
            return

        # Create enhancer
        self.enhancer = PedalEnhancer(
            pedals_path=pedals['path'],
            name="Enhanced Pedals",
            calibrator=self.calibrator
        )

        # Start
        if self.enhancer.start():
            self.is_running = True
            self.toggle_btn.configure(
                text="⏹️  STOP",
                fg_color=("#dc3545", "#c82333"),
                hover_color=("#bd2130", "#a71d2a")
            )
            self.status_indicator.configure(
                text="✅ Running",
                text_color=("#28a745", "#1e7e34")
            )

            # Start live monitoring automatically
            self.start_live_monitoring()

            # Modern success dialog
            success_dialog = ctk.CTkToplevel(self.parent)
            success_dialog.title("Success!")
            success_dialog.geometry("400x250")
            success_dialog.resizable(False, False)

            ctk.CTkLabel(
                success_dialog,
                text="✅ Enhanced Pedals Created!",
                font=ctk.CTkFont(size=18, weight="bold"),
                text_color=("#28a745", "#1e7e34")
            ).pack(pady=(20, 10))

            ctk.CTkLabel(
                success_dialog,
                text="New device: /dev/input/js2",
                font=ctk.CTkFont(size=12)
            ).pack(pady=5)

            info_frame = ctk.CTkFrame(success_dialog, corner_radius=10, fg_color=("#2b2b2b", "#1a1a1a"))
            info_frame.pack(fill="x", padx=30, pady=15)

            ctk.CTkLabel(
                info_frame,
                text="In your game:\n• Wheelbase: js0\n• Pedals: js2",
                font=ctk.CTkFont(size=12),
                justify="left"
            ).pack(padx=20, pady=15)

            def on_ok():
                success_dialog.destroy()
                # Rescan NACH OK-Klick (zeigt js2 im Header!)
                if self.main_window and hasattr(self.main_window, 'scan_devices'):
                    self.main_window.scan_devices()

            ctk.CTkButton(
                success_dialog,
                text="OK",
                command=on_ok,
                width=120,
                height=35,
                fg_color=("#28a745", "#1e7e34"),
                hover_color=("#218838", "#155724"),
                font=ctk.CTkFont(size=13, weight="bold")
            ).pack(pady=10)
        else:
            messagebox.showerror(
                "Error",
                "Failed to create enhanced pedals!\n\n"
                "Make sure uinput module is loaded:\n"
                "  sudo modprobe uinput\n\n"
                "And permissions are set:\n"
                "  sudo chmod 666 /dev/uinput"
            )

    def stop_enhancer(self):
        """Stop enhancer"""
        if self.enhancer:
            self.enhancer.stop()
            self.enhancer = None

        self.is_running = False
        self.toggle_btn.configure(
            text="▶️  START",
            fg_color=("#28a745", "#1e7e34"),
            hover_color=("#218838", "#155724")
        )
        self.status_indicator.configure(
            text="⏹️ Stopped",
            text_color="gray60"
        )

        # Stop live monitoring
        self.stop_live_monitoring()

        # Rescan nach Stop
        if self.main_window and hasattr(self.main_window, 'scan_devices'):
            self.parent.after(100, self.main_window.scan_devices)

    def start_live_monitoring(self):
        """Start live pedal monitoring"""
        pedal_device = self.scanner.get_pedal_device()
        if not pedal_device:
            return

        self.is_monitoring = True
        import threading
        self.monitor_thread = threading.Thread(
            target=self._monitor_loop,
            args=(pedal_device['path'],),
            daemon=True
        )
        self.monitor_thread.start()

    def stop_live_monitoring(self):
        """Stop live monitoring"""
        self.is_monitoring = False

    def _monitor_loop(self, device_path):
        """Monitor loop for live updates"""
        import struct
        JS_EVENT_FMT = 'IhBB'
        JS_EVENT_SIZE = struct.calcsize(JS_EVENT_FMT)
        JS_EVENT_AXIS = 0x02
        JS_EVENT_INIT = 0x80

        try:
            import os
            fd = os.open(device_path, os.O_RDONLY | os.O_NONBLOCK)

            while self.is_monitoring:
                try:
                    data = os.read(fd, JS_EVENT_SIZE)
                    if len(data) == JS_EVENT_SIZE:
                        timestamp, value, event_type, number = struct.unpack(JS_EVENT_FMT, data)
                        event_type &= ~JS_EVENT_INIT

                        if event_type == JS_EVENT_AXIS:
                            percentage = ((value + 32767) / 65534) * 100
                            pedal_names = {0: 'gas', 1: 'brake', 2: 'clutch'}

                            if number in pedal_names and pedal_names[number] in self.pedal_displays:
                                pedal = pedal_names[number]
                                self.parent.after(0, self._update_monitor, pedal, percentage)
                except BlockingIOError:
                    pass

                import time
                time.sleep(0.001)

            os.close(fd)
        except:
            pass

    def _update_monitor(self, pedal_name, percentage):
        """Update monitor display"""
        if pedal_name in self.pedal_displays:
            self.pedal_displays[pedal_name]['progressbar'].set(percentage / 100.0)
            self.pedal_displays[pedal_name]['label'].configure(text=f"{percentage:.0f}%")
