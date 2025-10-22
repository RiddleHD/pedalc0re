#!/usr/bin/env python3
"""
Settings Tab - CustomTkinter Version
Kompaktes 2x2 Grid Layout
"""

import customtkinter as ctk
from tkinter import messagebox
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from config.presets import PresetManager

class SettingsTab:
    def __init__(self, parent, scanner, calibrator):
        self.parent = parent
        self.scanner = scanner
        self.calibrator = calibrator
        self.preset_manager = PresetManager()
        self.pedal_controls = {}
        self.setup_ui()

    def setup_ui(self):
        """Setup compact grid UI"""
        # Top bar (Toggle + Presets)
        top_bar = ctk.CTkFrame(self.parent, corner_radius=10)
        top_bar.pack(fill="x", padx=15, pady=15)

        # Toggle links
        self.enabled_var = ctk.BooleanVar(value=False)
        ctk.CTkSwitch(
            top_bar,
            text="Enable",
            variable=self.enabled_var,
            command=self.toggle_calibration,
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(side="left", padx=15, pady=10)

        # Presets rechts
        presets = self.preset_manager.list_presets()
        preset_names = [p['name'] for p in presets]
        self.preset_name_to_file = {p['name']: p['filename'] for p in presets}

        self.preset_var = ctk.StringVar(value=preset_names[0] if preset_names else "")
        ctk.CTkOptionMenu(
            top_bar,
            variable=self.preset_var,
            values=preset_names,
            width=200,
            height=28,
            font=ctk.CTkFont(size=11)
        ).pack(side="left", padx=5, pady=10)

        ctk.CTkButton(
            top_bar,
            text="Load",
            command=self.load_preset,
            width=60,
            height=28,
            font=ctk.CTkFont(size=11)
        ).pack(side="left", padx=3, pady=10)

        ctk.CTkButton(
            top_bar,
            text="Save",
            command=self.save_preset,
            width=60,
            height=28,
            font=ctk.CTkFont(size=11),
            fg_color=("#28a745", "#1e7e34"),
            hover_color=("#218838", "#155724")
        ).pack(side="left", padx=3, pady=10)

        ctk.CTkButton(
            top_bar,
            text="Delete",
            command=self.delete_preset,
            width=65,
            height=28,
            font=ctk.CTkFont(size=11),
            fg_color=("#dc3545", "#c82333"),
            hover_color=("#bd2130", "#a71d2a")
        ).pack(side="left", padx=3, pady=10)

        # 3x1 Grid - 3 Pedale nebeneinander
        grid = ctk.CTkFrame(self.parent, fg_color="transparent")
        grid.pack(fill="x", expand=False, padx=15, pady=5)

        grid.grid_columnconfigure(0, weight=1, uniform="col")
        grid.grid_columnconfigure(1, weight=1, uniform="col")
        grid.grid_columnconfigure(2, weight=1, uniform="col")

        # Throttle (0)
        self.create_pedal_card(grid, "gas", "Throttle").grid(row=0, column=0, padx=3, pady=3, sticky="nsew")

        # Brake (1)
        self.create_pedal_card(grid, "brake", "Brake").grid(row=0, column=1, padx=3, pady=3, sticky="nsew")

        # Clutch (2)
        self.create_pedal_card(grid, "clutch", "Clutch").grid(row=0, column=2, padx=3, pady=3, sticky="nsew")

        # Reset button (unten)
        reset_frame = ctk.CTkFrame(self.parent, fg_color="transparent")
        reset_frame.pack(pady=10)

        ctk.CTkButton(
            reset_frame,
            text="↺ Reset All",
            command=self.reset_all,
            fg_color=("#dc3545", "#c82333"),
            hover_color=("#bd2130", "#a71d2a"),
            width=200,
            height=35,
            corner_radius=8,
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack()

    def create_pedal_card(self, parent, pedal_name, label):
        """Create compact pedal card"""
        card = ctk.CTkFrame(parent, corner_radius=10)
        self.pedal_controls[pedal_name] = {}

        # Header
        ctk.CTkLabel(
            card,
            text=f"🦶 {label}",
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(anchor="w", padx=10, pady=(8, 5))

        # Deadzone
        dz = ctk.CTkFrame(card, fg_color="transparent")
        dz.pack(fill="x", padx=10, pady=3)

        ctk.CTkLabel(dz, text="DZ:", width=30, anchor="w", font=ctk.CTkFont(size=10)).pack(side="left")
        dz_slider = ctk.CTkSlider(dz, from_=0, to=20, number_of_steps=200, command=lambda v: self.update_deadzone(pedal_name, v), width=160)
        dz_slider.set(0)
        dz_slider.pack(side="left", padx=2)
        dz_label = ctk.CTkLabel(dz, text="0%", width=35, font=ctk.CTkFont(size=10))
        dz_label.pack(side="left")

        self.pedal_controls[pedal_name]['deadzone_slider'] = dz_slider
        self.pedal_controls[pedal_name]['deadzone_label'] = dz_label

        # Min
        min_f = ctk.CTkFrame(card, fg_color="transparent")
        min_f.pack(fill="x", padx=10, pady=3)

        ctk.CTkLabel(min_f, text="Min:", width=30, anchor="w", font=ctk.CTkFont(size=10)).pack(side="left")
        min_slider = ctk.CTkSlider(min_f, from_=0, to=100, number_of_steps=100, command=lambda v: self.update_min(pedal_name, v), width=160)
        min_slider.set(0)
        min_slider.pack(side="left", padx=2)
        min_label = ctk.CTkLabel(min_f, text="0%", width=35, font=ctk.CTkFont(size=10))
        min_label.pack(side="left")

        self.pedal_controls[pedal_name]['min_slider'] = min_slider
        self.pedal_controls[pedal_name]['min_label'] = min_label

        # Max
        max_f = ctk.CTkFrame(card, fg_color="transparent")
        max_f.pack(fill="x", padx=10, pady=3)

        ctk.CTkLabel(max_f, text="Max:", width=30, anchor="w", font=ctk.CTkFont(size=10)).pack(side="left")
        max_slider = ctk.CTkSlider(max_f, from_=0, to=100, number_of_steps=100, command=lambda v: self.update_max(pedal_name, v), width=160)
        max_slider.set(100)
        max_slider.pack(side="left", padx=2)
        max_label = ctk.CTkLabel(max_f, text="100%", width=35, font=ctk.CTkFont(size=10))
        max_label.pack(side="left")

        self.pedal_controls[pedal_name]['max_slider'] = max_slider
        self.pedal_controls[pedal_name]['max_label'] = max_label

        # Curve (linksbündig wie Slider)
        curve_var = ctk.StringVar(value="Linear")
        self.pedal_controls[pedal_name]['curve_var'] = curve_var

        curve_buttons = ctk.CTkSegmentedButton(
            card,
            values=["Linear", "Exponential", "Logarithmic"],
            command=lambda v: self.update_curve(pedal_name, v.lower()),
            height=24,
            font=ctk.CTkFont(size=10)
        )
        curve_buttons.pack(anchor="w", padx=40, pady=5)

        # Invert (linksbündig)
        invert_var = ctk.BooleanVar(value=False)
        self.pedal_controls[pedal_name]['invert_var'] = invert_var

        ctk.CTkCheckBox(
            card,
            text="Invert",
            variable=invert_var,
            command=lambda: self.update_invert(pedal_name, invert_var.get()),
            font=ctk.CTkFont(size=10),
            checkbox_width=16,
            checkbox_height=16
        ).pack(anchor="w", padx=40, pady=(3, 8))

        return card

    def toggle_calibration(self):
        """Toggle calibration"""
        self.calibrator.enabled = self.enabled_var.get()

    def update_deadzone(self, pedal_name, value):
        """Update deadzone"""
        value = float(value)
        self.calibrator.set_pedal_setting(pedal_name, 'deadzone', value)
        self.pedal_controls[pedal_name]['deadzone_label'].configure(text=f"{value:.1f}%")

    def update_min(self, pedal_name, value):
        """Update min"""
        value = float(value)
        self.calibrator.set_pedal_setting(pedal_name, 'min', value)
        self.pedal_controls[pedal_name]['min_label'].configure(text=f"{value:.0f}%")

    def update_max(self, pedal_name, value):
        """Update max"""
        value = float(value)
        self.calibrator.set_pedal_setting(pedal_name, 'max', value)
        self.pedal_controls[pedal_name]['max_label'].configure(text=f"{value:.0f}%")

    def update_curve(self, pedal_name, curve_type):
        """Update curve"""
        self.calibrator.set_pedal_setting(pedal_name, 'curve', curve_type)

    def update_invert(self, pedal_name, inverted):
        """Update invert"""
        self.calibrator.set_pedal_setting(pedal_name, 'invert', inverted)

    def load_preset(self):
        """Load preset"""
        preset_name = self.preset_var.get()
        if not preset_name or preset_name not in self.preset_name_to_file:
            return

        filename = self.preset_name_to_file[preset_name]
        preset_data = self.preset_manager.load_preset(filename)

        if preset_data:
            self.preset_manager.apply_preset_to_calibrator(preset_data, self.calibrator)
            self.update_all_ui_from_settings()
            messagebox.showinfo("Success", f"Preset '{preset_name}' loaded!")

    def save_preset(self):
        """Save preset"""
        dialog = ctk.CTkInputDialog(text="Preset name:", title="Save")
        name = dialog.get_input()

        if name:
            filename = name.lower().replace(' ', '_')
            preset_data = self.preset_manager.get_preset_from_calibrator(self.calibrator, name=name, description=f"Custom - {name}")

            if self.preset_manager.save_preset(filename, preset_data, overwrite=True):
                messagebox.showinfo("Success", f"Saved!")
            else:
                messagebox.showerror("Error", "Failed!")

    def delete_preset(self):
        """Delete selected preset"""
        preset_name = self.preset_var.get()
        if not preset_name or preset_name not in self.preset_name_to_file:
            return

        filename = self.preset_name_to_file[preset_name]

        # Confirm deletion
        if messagebox.askyesno("Delete Preset", f"Delete preset '{preset_name}'?"):
            if self.preset_manager.delete_preset(filename):
                # Refresh preset list
                presets = self.preset_manager.list_presets()
                preset_names = [p['name'] for p in presets]
                self.preset_name_to_file = {p['name']: p['filename'] for p in presets}
                self.preset_dropdown.configure(values=preset_names)
                if preset_names:
                    self.preset_var.set(preset_names[0])
                messagebox.showinfo("Deleted", f"Preset '{preset_name}' deleted!")
            else:
                messagebox.showerror("Error", "Failed to delete preset!")

    def reset_all(self):
        """Reset all"""
        self.calibrator.reset_all()
        self.update_all_ui_from_settings()
        messagebox.showinfo("Reset", "Reset to default!")

    def update_all_ui_from_settings(self):
        """Update all UI"""
        for pedal in ['gas', 'brake', 'clutch']:
            if pedal in self.pedal_controls:
                settings = self.calibrator.get_pedal_settings(pedal)
                controls = self.pedal_controls[pedal]

                controls['deadzone_slider'].set(settings['deadzone'])
                controls['deadzone_label'].configure(text=f"{settings['deadzone']:.1f}%")

                controls['min_slider'].set(settings['min'])
                controls['min_label'].configure(text=f"{settings['min']:.0f}%")

                controls['max_slider'].set(settings['max'])
                controls['max_label'].configure(text=f"{settings['max']:.0f}%")

                controls['invert_var'].set(settings['invert'])
