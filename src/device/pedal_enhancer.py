#!/usr/bin/env python3
"""
Pedal Enhancer - Fügt Dummy-Buttons zu Pedalen hinzu
Transformiert js1 (Simsonn Pedale) → js2 (Enhanced Pedals mit Buttons)
"""

import struct
import threading
import time
import os
from evdev import UInput, AbsInfo, ecodes as e

# Joystick event format
JS_EVENT_FMT = 'IhBB'
JS_EVENT_SIZE = struct.calcsize(JS_EVENT_FMT)
JS_EVENT_BUTTON = 0x01
JS_EVENT_AXIS = 0x02
JS_EVENT_INIT = 0x80


class PedalEnhancer:
    """
    Liest Simsonn Pedale (js1) und erstellt Enhanced Version (js2) mit Dummy-Buttons
    """

    def __init__(self, pedals_path, name="Simsonn Enhanced Pedals", calibrator=None):
        self.pedals_path = pedals_path
        self.device_name = name
        self.uinput = None
        self.is_running = False
        self.reader_thread = None
        self.calibrator = calibrator

    def create_device(self):
        """Erstellt das Enhanced Pedal Device mit Buttons"""
        try:
            # Define capabilities
            cap = {
                # 4 Dummy-Buttons (werden nie gedrückt, aber ACC sieht sie!)
                e.EV_KEY: [e.BTN_JOYSTICK + i for i in range(4)],
                # 3 Achsen für Gas, Bremse, Kupplung
                e.EV_ABS: [
                    (e.ABS_X, AbsInfo(0, -32767, 32767, 0, 0, 0)),   # Gas
                    (e.ABS_Y, AbsInfo(0, -32767, 32767, 0, 0, 0)),   # Bremse
                    (e.ABS_Z, AbsInfo(0, -32767, 32767, 0, 0, 0)),   # Kupplung
                ]
            }

            # Create UInput device
            self.uinput = UInput(
                events=cap,
                name=self.device_name,
                vendor=0xDDFD,   # Simsonn Vendor ID
                product=0x6012,  # Neue Product ID (damit es anders als Original ist)
                version=2,
                bustype=e.BUS_USB
            )

            return True

        except Exception as ex:
            return False

    def write_event(self, event_type, code, value):
        """Schreibt ein Event auf das Enhanced Device"""
        if not self.uinput:
            return

        try:
            self.uinput.write(event_type, code, value)
            self.uinput.syn()
        except Exception as ex:
            pass

    def start(self):
        """Startet den Enhancer"""
        if self.is_running:
            return False

        if not self.create_device():
            return False

        self.is_running = True
        self.reader_thread = threading.Thread(target=self._reader_loop, daemon=True)
        self.reader_thread.start()

        return True

    def stop(self):
        """Stoppt den Enhancer"""
        self.is_running = False

        if self.reader_thread:
            self.reader_thread.join(timeout=2)

        if self.uinput:
            try:
                self.uinput.close()
            except:
                pass
            self.uinput = None

    def _reader_loop(self):
        """Liest Events von Pedalen und schreibt sie enhanced"""
        try:
            pedals_fd = os.open(self.pedals_path, os.O_RDONLY | os.O_NONBLOCK)

            # Axis mapping: Input Achse → Output Achse
            axis_map = {
                0: e.ABS_X,   # Gas
                1: e.ABS_Y,   # Bremse
                2: e.ABS_Z,   # Kupplung
            }

            while self.is_running:
                # Read from pedals
                try:
                    data = os.read(pedals_fd, JS_EVENT_SIZE)
                    if len(data) == JS_EVENT_SIZE:
                        self._process_pedal_event(data, axis_map)
                except BlockingIOError:
                    pass

                time.sleep(0.001)

            os.close(pedals_fd)

        except Exception as ex:
            self.is_running = False

    def _process_pedal_event(self, data, axis_map):
        """Verarbeitet Pedal Events"""
        timestamp, value, event_type, number = struct.unpack(JS_EVENT_FMT, data)
        event_type &= ~JS_EVENT_INIT

        if event_type == JS_EVENT_AXIS:
            if number in axis_map:
                output_axis = axis_map[number]

                # Apply calibration if available and enabled
                if self.calibrator and self.calibrator.enabled:
                    pedal_names = {0: 'gas', 1: 'brake', 2: 'clutch'}
                    if number in pedal_names:
                        value = self.calibrator.calibrate_value(value, pedal_names[number])

                self.write_event(e.EV_ABS, output_axis, value)
