#!/usr/bin/env python3
"""
Preset Manager - Speichern/Laden von Kalibrierungs-Presets
"""

import json
import os
from pathlib import Path

class PresetManager:
    """Verwaltet Kalibrierungs-Presets"""

    def __init__(self, preset_dir=None):
        if preset_dir is None:
            # Default: presets/ im Projektverzeichnis
            base_dir = Path(__file__).parent.parent.parent
            self.preset_dir = base_dir / "presets"
        else:
            self.preset_dir = Path(preset_dir)

        # Create presets directory if it doesn't exist
        self.preset_dir.mkdir(exist_ok=True)

        # Create only stock preset
        self.create_stock_preset()

    def create_stock_preset(self):
        """Create stock preset (no calibration)"""
        stock_preset = {
            "name": "Stock",
            "description": "No calibration",
            "gas": {"deadzone": 0.0, "min": 0.0, "max": 100.0, "curve": "linear", "invert": False},
            "brake": {"deadzone": 0.0, "min": 0.0, "max": 100.0, "curve": "linear", "invert": False},
            "clutch": {"deadzone": 0.0, "min": 0.0, "max": 100.0, "curve": "linear", "invert": False}
        }
        self.save_preset("stock", stock_preset, overwrite=False)


    def save_preset(self, filename, preset_data, overwrite=True):
        """
        Speichert ein Preset

        Args:
            filename: Dateiname (ohne .json)
            preset_data: Dict mit Preset-Daten
            overwrite: Überschreiben falls existiert
        """
        filepath = self.preset_dir / f"{filename}.json"

        if not overwrite and filepath.exists():
            return False

        try:
            with open(filepath, 'w') as f:
                json.dump(preset_data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving preset: {e}")
            return False

    def load_preset(self, filename):
        """
        Lädt ein Preset

        Args:
            filename: Dateiname (ohne .json)

        Returns:
            Preset-Dict oder None
        """
        filepath = self.preset_dir / f"{filename}.json"

        if not filepath.exists():
            return None

        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading preset: {e}")
            return None

    def list_presets(self):
        """Listet alle verfügbaren Presets"""
        presets = []

        for filepath in self.preset_dir.glob("*.json"):
            try:
                with open(filepath, 'r') as f:
                    data = json.load(f)
                    presets.append({
                        'filename': filepath.stem,
                        'name': data.get('name', filepath.stem),
                        'description': data.get('description', '')
                    })
            except:
                pass

        return presets

    def delete_preset(self, filename):
        """Löscht ein Preset"""
        filepath = self.preset_dir / f"{filename}.json"

        try:
            if filepath.exists():
                filepath.unlink()
                return True
        except Exception as e:
            print(f"Error deleting preset: {e}")

        return False

    def apply_preset_to_calibrator(self, preset_data, calibrator):
        """Wendet ein Preset auf einen Calibrator an"""
        for pedal in ['gas', 'brake', 'clutch']:
            if pedal in preset_data:
                pedal_settings = preset_data[pedal]
                for setting_name, value in pedal_settings.items():
                    calibrator.set_pedal_setting(pedal, setting_name, value)

    def get_preset_from_calibrator(self, calibrator, name="Custom", description=""):
        """Erstellt ein Preset-Dict aus einem Calibrator"""
        preset = {
            "name": name,
            "description": description,
            "gas": calibrator.get_pedal_settings('gas'),
            "brake": calibrator.get_pedal_settings('brake'),
            "clutch": calibrator.get_pedal_settings('clutch')
        }
        return preset
