import json
import os
import logging
from .keyboard_controller import KeyboardController

logger = logging.getLogger("GesturePlay.ActionMapper")

class ActionMapper:
    def __init__(self, config_path="app/config/settings.json"):
        self.controller = KeyboardController()
        self.config_path = config_path
        self.mapping = {}
        self.active_profile_name = ""
        self.load_config()

    def load_config(self):
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                    
                self.active_profile_name = config.get("active_profile", "racing")
                profiles = config.get("profiles", {})
                
                if self.active_profile_name in profiles:
                    profile = profiles[self.active_profile_name]
                    self.gestures_map = profile.get("gestures", {})
                    self.keys_map = profile.get("keys", {})
                    logger.info(f"Loaded profile: {self.active_profile_name}")
                else:
                    logger.warning(f"Profile {self.active_profile_name} not found, using empty mapping")
                    self.gestures_map = {}
                    self.keys_map = {}
            else:
                logger.warning(f"Config file not found at {self.config_path}")
        except Exception as e:
            logger.error(f"Failed to load config: {e}")

    def handle_gesture(self, gesture):
        if not gesture or gesture == "NO_HAND":
            self.current_action = "NONE"
            self.controller.release_all()
            return

        self.current_action = self.gestures_map.get(gesture, "NONE")
        target_key = self.keys_map.get(self.current_action)
        
        active_keys = self.controller.get_active_keys()
        
        for key in active_keys:
            if key != target_key:
                self.controller.key_up(key)
                
        if target_key:
            self.controller.key_down(target_key)
            
    def release_all(self):
        self.current_action = "NONE"
        self.controller.release_all()
        
    def get_current_action(self):
        return getattr(self, 'current_action', 'NONE')
        
    def get_current_key(self):
        keys = self.controller.get_active_keys()
        if keys:
            return keys[0].upper()
        return "NONE"

    def cleanup(self):
        self.controller.cleanup()
