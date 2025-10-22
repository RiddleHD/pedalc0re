#!/usr/bin/env python3
"""
Device Scanner - scannt nach Input-Geräten
"""

import os
import struct
from pathlib import Path

class DeviceScanner:
    def __init__(self):
        self.devices = []
        self.pedal_device = None
        self.wheelbase_device = None

    def scan(self):
        """Scanne /dev/input nach Joystick-Geräten"""
        self.devices = []
        input_dir = Path("/dev/input")

        if not input_dir.exists():
            return

        # Scanne nach js* und event* Geräten
        for device_path in sorted(input_dir.glob("js*")):
            try:
                device_info = self._get_device_info(device_path)
                if device_info:
                    self.devices.append(device_info)

                    # Identifiziere Pedale (universell)
                    if "Pedals" in device_info['type']:
                        self.pedal_device = device_info

                    # Identifiziere Wheelbase (universell)
                    if "Wheelbase" in device_info['type'] or "Force Feedback" in device_info['type']:
                        self.wheelbase_device = device_info

            except Exception as e:
                print(f"Error scanning {device_path}: {e}")

    def _get_device_info(self, device_path):
        """Hole Geräte-Informationen"""
        try:
            # Versuche Device-Name aus /proc/bus/input/devices zu lesen
            name = self._get_device_name_from_proc(device_path)

            if not name:
                name = device_path.name

            # Bestimme Device-Typ
            device_type = self._determine_device_type(name)

            return {
                'path': str(device_path),
                'name': name,
                'type': device_type
            }

        except Exception as e:
            print(f"Error getting device info: {e}")
            return None

    def _get_device_name_from_proc(self, device_path):
        """Lese Device-Name aus /proc/bus/input/devices"""
        try:
            with open("/proc/bus/input/devices", "r") as f:
                content = f.read()

            # Finde den Handler, der zu unserem js* Device passt
            handler_name = device_path.name
            for block in content.split("\n\n"):
                if f"js{handler_name[2:]}" in block:  # z.B. js1
                    for line in block.split("\n"):
                        if line.startswith("N: Name="):
                            name = line.split('Name=')[1].strip().strip('"')
                            return name

        except Exception as e:
            print(f"Error reading /proc/bus/input/devices: {e}")

        return None

    def _determine_device_type(self, name):
        """Bestimme Device-Typ anhand des Namens"""
        name_upper = name.upper()

        # Check for known pedal brands
        pedal_keywords = ["SIMSONN", "PEDAL", "THRUSTMASTER", "FANATEC CSL", "HEUSINKVELD"]
        for keyword in pedal_keywords:
            if keyword in name_upper:
                return "Pedals"

        # Check for known wheelbase brands
        if "MOZA" in name_upper:
            if "BASE" in name_upper or any(f"R{i}" in name_upper for i in range(1, 25)):
                return "Force Feedback Wheelbase"
            return "Wheelbase"

        wheelbase_keywords = ["WHEEL", "BASE", "LOGITECH G", "THRUSTMASTER T"]
        for keyword in wheelbase_keywords:
            if keyword in name_upper:
                return "Wheelbase"

        return "Input Device"

    def get_pedal_device(self):
        """Gibt das erkannte Pedal Device zurück (universell)"""
        return self.pedal_device

    def get_simsonn_device(self):
        """Alias for backward compatibility"""
        return self.get_pedal_device()

    def get_wheelbase_device(self):
        """Gibt das Wheelbase Device zurück"""
        return self.wheelbase_device
