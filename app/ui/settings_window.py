import tkinter as tk
from tkinter import ttk, messagebox
import json
import logging
import os

logger = logging.getLogger("GesturePlay.SettingsUI")

class SettingsWindow:
    def __init__(self, config_path="app/config/settings.json", on_close_callback=None):
        self.config_path = config_path
        self.on_close_callback = on_close_callback
        
        self.config = {}
        self.load_config()
        
        self.root = tk.Tk()
        self.root.title("GesturePlay AI - Settings")
        self.root.geometry("400x500")
        self.root.resizable(False, False)
        
        # Profile Selection
        profile_frame = ttk.LabelFrame(self.root, text="Active Profile")
        profile_frame.pack(padx=10, pady=10, fill="x")
        
        self.profile_var = tk.StringVar(value=self.config.get("active_profile", "racing"))
        profiles = list(self.config.get("profiles", {}).keys())
        
        self.profile_dropdown = ttk.Combobox(profile_frame, textvariable=self.profile_var, values=profiles, state="readonly")
        self.profile_dropdown.pack(padx=10, pady=10, fill="x")
        self.profile_dropdown.bind("<<ComboboxSelected>>", self.on_profile_change)
        
        # Profile Mappings
        self.mapping_frame = ttk.LabelFrame(self.root, text="Profile Mappings (Action -> Key)")
        self.mapping_frame.pack(padx=10, pady=5, fill="both", expand=True)
        
        hint = ttk.Label(self.root, text="Hint: Type 'mouse_left' or 'mouse_right' to click screen pedals.", foreground="gray", font=("Arial", 8))
        hint.pack(pady=2)
        
        self.entry_vars = {}
        self.build_mapping_fields()
            
        # Buttons
        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(pady=10)
        
        ttk.Button(btn_frame, text="Save", command=self.save_settings).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Reset", command=self.reset_settings).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Cancel", command=self.cancel_settings).pack(side="left", padx=5)
        
    def load_config(self):
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    self.config = json.load(f)
            else:
                self.config = {"active_profile": "racing", "profiles": {"racing": {"gestures": {}, "keys": {}}}}
        except Exception as e:
            logger.error(f"Error reading config in UI: {e}")
            
    def build_mapping_fields(self):
        for widget in self.mapping_frame.winfo_children():
            widget.destroy()
            
        self.entry_vars.clear()
        active = self.profile_var.get()
        profile_data = self.config.get("profiles", {}).get(active, {})
        keys_map = profile_data.get("keys", {})
        
        for i, (action, key_val) in enumerate(keys_map.items()):
            ttk.Label(self.mapping_frame, text=action).grid(row=i, column=0, padx=10, pady=5, sticky="w")
            var = tk.StringVar(value=key_val)
            self.entry_vars[action] = var
            ttk.Entry(self.mapping_frame, textvariable=var, width=15).grid(row=i, column=1, padx=10, pady=5, sticky="e")
            
    def on_profile_change(self, event):
        self.build_mapping_fields()
                
    def validate_keys(self):
        for action, var in self.entry_vars.items():
            val = var.get().strip().lower()
            if not val:
                messagebox.showerror("Validation Error", f"Key for {action} cannot be empty.")
                return False
            valid_specials = ["space", "enter", "shift", "ctrl", "alt", "tab", "esc", "up", "down", "left", "right", "mouse_left", "mouse_right"]
            if len(val) > 1 and val not in valid_specials:
                messagebox.showerror("Validation Error", f"'{val}' might be an invalid key name for {action}. Use single characters or valid names like 'space' or 'mouse_right'.")
                return False
        return True

    def save_settings(self):
        if not self.validate_keys():
            return
            
        try:
            active = self.profile_var.get()
            self.config["active_profile"] = active
            
            for action, var in self.entry_vars.items():
                self.config["profiles"][active]["keys"][action] = var.get().strip().lower()
                    
            temp_path = self.config_path + ".tmp"
            with open(temp_path, 'w') as f:
                json.dump(self.config, f, indent=2)
            os.replace(temp_path, self.config_path)
            
            logger.info("Settings saved successfully.")
            self.root.destroy()
            if self.on_close_callback:
                self.on_close_callback()
                
        except Exception as e:
            logger.error(f"Failed to save settings: {e}")
            messagebox.showerror("Save Error", f"Failed to save settings:\n{e}")
            
    def reset_settings(self):
        self.load_config()
        self.profile_var.set(self.config.get("active_profile", "racing"))
        self.build_mapping_fields()

    def cancel_settings(self):
        self.root.destroy()
        if self.on_close_callback:
            self.on_close_callback()

    def run(self):
        self.root.mainloop()
