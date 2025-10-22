#!/usr/bin/env python3
"""
Virtual Device Creator V3 - Verwendet python-evdev Library
Die einfachste und zuverlässigste Methode!
"""

import struct
import threading
import time
from evdev import UInput, AbsInfo, ecodes as e
from device.calibration import PedalCalibrator

# Joystick event format
JS_EVENT_FMT = 'IhBB'
JS_EVENT_SIZE = struct.calcsize(JS_EVENT_FMT)
JS_EVENT_BUTTON = 0x01
JS_EVENT_AXIS = 0x02
JS_EVENT_INIT = 0x80


class VirtualRacingDevice:
    """Erstellt ein virtuelles Racing-Device mit python-evdev"""

    def __init__(self, wheelbase_path, pedals_path, name="Simsonn Virtual Racing", calibrator=None):
        self.wheelbase_path = wheelbase_path
        self.pedals_path = pedals_path
        self.device_name = name
        self.uinput = None
        self.is_running = False
        self.reader_thread = None
        self.calibrator = calibrator if calibrator else PedalCalibrator()

        # Axis mapping
        # ABS Codes werden numerisch sortiert: ABS_X(0), ABS_Y(1), ABS_Z(2), ABS_RX(3), ABS_RY(4), ABS_RZ(5)
        # Daher: ABS_X=js0, ABS_Y=js1, ABS_Z=js2, ABS_RX=js3
        self.wheelbase_axis_map = {0: e.ABS_X}   # Wheelbase Achse 0 (Steering) -> ABS_X -> js0
        self.pedal_axis_map = {
            0: e.ABS_Y,   # Pedal Achse 0 (Gas) -> ABS_Y -> js1
            1: e.ABS_Z,   # Pedal Achse 1 (Bremse) -> ABS_Z -> js2
            2: e.ABS_RX,  # Pedal Achse 2 (Kupplung) -> ABS_RX -> js3
        }

    def create_device(self):
        """Erstellt das virtuelle uinput Device"""
        try:
            # Define capabilities
            cap = {
                e.EV_KEY: [e.BTN_JOYSTICK + i for i in range(16)],
                e.EV_ABS: [
                    (e.ABS_X, AbsInfo(0, -32767, 32767, 0, 0, 0)),   # js Achse 0: Steering
                    (e.ABS_Y, AbsInfo(0, -32767, 32767, 0, 0, 0)),   # js Achse 1: Gas
                    (e.ABS_Z, AbsInfo(0, -32767, 32767, 0, 0, 0)),   # js Achse 2: Brake
                    (e.ABS_RX, AbsInfo(0, -32767, 32767, 0, 0, 0)),  # js Achse 3: Clutch
                ]
            }

            # Create UInput device
            self.uinput = UInput(
                events=cap,
                name=self.device_name,
                vendor=0xDDFD,   # Simsonn Vendor ID
                product=0x6011,  # Simsonn Product ID
                version=1,
                bustype=e.BUS_USB
            )

            # Device created successfully

            return True

        except Exception as ex:
            # Silent fail
            return False

    def write_event(self, event_type, code, value):
        """Schreibt ein Event auf das virtuelle Device"""
        if not self.uinput:
            return

        try:
            self.uinput.write(event_type, code, value)
            self.uinput.syn()
        except Exception as ex:
            pass  # Silent

    def start(self):
        """Startet das Event-Merging"""
        if self.is_running:
            return False

        if not self.create_device():
            return False

        self.is_running = True
        self.reader_thread = threading.Thread(target=self._reader_loop, daemon=True)
        self.reader_thread.start()

        return True

    def stop(self):
        """Stoppt das Virtual Device"""
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
        """Liest Events von beiden Devices und merged sie"""
        import os

        try:
            wheelbase_fd = os.open(self.wheelbase_path, os.O_RDONLY | os.O_NONBLOCK)
            pedals_fd = os.open(self.pedals_path, os.O_RDONLY | os.O_NONBLOCK)

            while self.is_running:
                # Read from wheelbase
                try:
                    data = os.read(wheelbase_fd, JS_EVENT_SIZE)
                    if len(data) == JS_EVENT_SIZE:
                        self._process_wheelbase_event(data)
                except BlockingIOError:
                    pass

                # Read from pedals
                try:
                    data = os.read(pedals_fd, JS_EVENT_SIZE)
                    if len(data) == JS_EVENT_SIZE:
                        self._process_pedal_event(data)
                except BlockingIOError:
                    pass

                time.sleep(0.001)

            os.close(wheelbase_fd)
            os.close(pedals_fd)

        except Exception as ex:
            # Silent error handling
            self.is_running = False

    def _process_wheelbase_event(self, data):
        """Verarbeitet Wheelbase Events"""
        timestamp, value, event_type, number = struct.unpack(JS_EVENT_FMT, data)
        event_type &= ~JS_EVENT_INIT

        if event_type == JS_EVENT_AXIS:
            if number in self.wheelbase_axis_map:
                virtual_axis = self.wheelbase_axis_map[number]
                self.write_event(e.EV_ABS, virtual_axis, value)

        elif event_type == JS_EVENT_BUTTON:
            self.write_event(e.EV_KEY, e.BTN_JOYSTICK + number, value)

    def _process_pedal_event(self, data):
        """Verarbeitet Pedal Events"""
        timestamp, value, event_type, number = struct.unpack(JS_EVENT_FMT, data)
        event_type &= ~JS_EVENT_INIT

        if event_type == JS_EVENT_AXIS:
            if number in self.pedal_axis_map:
                virtual_axis = self.pedal_axis_map[number]

                # Apply calibration if enabled
                pedal_names = {0: 'gas', 1: 'brake', 2: 'clutch'}
                if number in pedal_names and self.calibrator.enabled:
                    value = self.calibrator.calibrate_value(value, pedal_names[number])

                self.write_event(e.EV_ABS, virtual_axis, value)
