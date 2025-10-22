#!/usr/bin/env python3
"""
Pedal Calibration Engine
Transformiert rohe Pedal-Werte mit Deadzone, Kurven, Range, Invert
"""

import math

class PedalCalibrator:
    """
    Kalibriert Pedal-Werte
    """

    CURVE_LINEAR = "linear"
    CURVE_EXPONENTIAL = "exponential"
    CURVE_LOGARITHMIC = "logarithmic"

    def __init__(self):
        # Calibration settings per pedal (Gas, Brake, Clutch)
        self.settings = {
            'gas': {
                'deadzone': 0.0,      # 0-20%
                'min': 0.0,           # 0-100%
                'max': 100.0,         # 0-100%
                'curve': self.CURVE_LINEAR,
                'invert': False
            },
            'brake': {
                'deadzone': 0.0,
                'min': 0.0,
                'max': 100.0,
                'curve': self.CURVE_LINEAR,
                'invert': False
            },
            'clutch': {
                'deadzone': 0.0,
                'min': 0.0,
                'max': 100.0,
                'curve': self.CURVE_LINEAR,
                'invert': False
            }
        }

        self.enabled = False

    def calibrate_value(self, value, pedal_name):
        """
        Kalibriert einen einzelnen Pedal-Wert

        Args:
            value: Raw joystick value (-32767 bis 32767)
            pedal_name: 'gas', 'brake', oder 'clutch'

        Returns:
            Kalibrierter Wert (-32767 bis 32767)
        """
        if not self.enabled or pedal_name not in self.settings:
            return value

        settings = self.settings[pedal_name]

        # 1. Convert to percentage (0-100)
        percentage = self._raw_to_percentage(value)

        # 2. Apply invert
        if settings['invert']:
            percentage = 100.0 - percentage

        # 3. Apply min/max range
        percentage = self._apply_range(percentage, settings['min'], settings['max'])

        # 4. Apply deadzone
        percentage = self._apply_deadzone(percentage, settings['deadzone'])

        # 5. Apply curve
        percentage = self._apply_curve(percentage, settings['curve'])

        # 6. Convert back to raw value
        return self._percentage_to_raw(percentage)

    def _raw_to_percentage(self, value):
        """Konvertiert -32767 bis 32767 zu 0-100%"""
        return ((value + 32767) / 65534) * 100.0

    def _percentage_to_raw(self, percentage):
        """Konvertiert 0-100% zu -32767 bis 32767"""
        return int((percentage / 100.0) * 65534 - 32767)

    def _apply_deadzone(self, percentage, deadzone):
        """
        Wendet Deadzone an

        Args:
            percentage: Input 0-100%
            deadzone: Deadzone in % (0-20)

        Returns:
            Output 0-100% mit Deadzone
        """
        if percentage < deadzone:
            return 0.0

        # Reskalieren: deadzone-100 wird zu 0-100
        return ((percentage - deadzone) / (100.0 - deadzone)) * 100.0

    def _apply_range(self, percentage, min_val, max_val):
        """
        Wendet Min/Max Range an

        Args:
            percentage: Input 0-100%
            min_val: Minimum Wert 0-100%
            max_val: Maximum Wert 0-100%

        Returns:
            Reskalierter Wert 0-100%
        """
        if min_val >= max_val:
            return percentage

        # Skaliere percentage vom Bereich min-max auf 0-100
        if percentage < min_val:
            return 0.0
        if percentage > max_val:
            return 100.0

        return ((percentage - min_val) / (max_val - min_val)) * 100.0

    def _apply_curve(self, percentage, curve_type):
        """
        Wendet Response-Kurve an

        Args:
            percentage: Input 0-100%
            curve_type: 'linear', 'exponential', oder 'logarithmic'

        Returns:
            Transformierter Wert 0-100%
        """
        # Normalisieren zu 0.0-1.0
        normalized = percentage / 100.0

        if curve_type == self.CURVE_EXPONENTIAL:
            # Exponentiell: Weniger empfindlich am Anfang, mehr am Ende
            result = normalized ** 2
        elif curve_type == self.CURVE_LOGARITHMIC:
            # Logarithmisch: Mehr empfindlich am Anfang, weniger am Ende
            if normalized <= 0:
                result = 0
            else:
                # log curve: sqrt gibt guten Effekt
                result = math.sqrt(normalized)
        else:
            # Linear (default)
            result = normalized

        # Zurück zu 0-100%
        return result * 100.0

    def set_pedal_setting(self, pedal_name, setting_name, value):
        """Setzt eine Einstellung für ein Pedal"""
        if pedal_name in self.settings and setting_name in self.settings[pedal_name]:
            self.settings[pedal_name][setting_name] = value

    def get_pedal_settings(self, pedal_name):
        """Gibt alle Einstellungen für ein Pedal zurück"""
        return self.settings.get(pedal_name, {})

    def reset_pedal(self, pedal_name):
        """Setzt Pedal auf Standardwerte zurück"""
        if pedal_name in self.settings:
            self.settings[pedal_name] = {
                'deadzone': 0.0,
                'min': 0.0,
                'max': 100.0,
                'curve': self.CURVE_LINEAR,
                'invert': False
            }

    def reset_all(self):
        """Setzt alle Pedale zurück"""
        for pedal in ['gas', 'brake', 'clutch']:
            self.reset_pedal(pedal)
