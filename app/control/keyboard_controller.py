import logging
import pyautogui

logger = logging.getLogger("GesturePlay.Keyboard")

# Configure pyautogui
pyautogui.FAILSAFE = False

class KeyboardController:
    """
    Manages keyboard state using pyautogui, which works well for standard PC games and UWP apps.
    """
    def __init__(self):
        self.active_keys = set()
        logger.info("Initialized KeyboardController using pyautogui")

    def key_down(self, key):
        if not key or key == "NONE":
            return
            
        key = key.lower()
        if key not in self.active_keys:
            try:
                pyautogui.keyDown(key)
                self.active_keys.add(key)
                logger.debug(f"Key down: {key}")
            except Exception as e:
                logger.warning(f"Unsupported key mapped: {key}, Error: {e}")

    def key_up(self, key):
        if not key or key == "NONE":
            return
            
        key = key.lower()
        if key in self.active_keys:
            try:
                pyautogui.keyUp(key)
                self.active_keys.remove(key)
                logger.debug(f"Key up: {key}")
            except Exception as e:
                pass

    def release_all(self):
        for key in list(self.active_keys):
            self.key_up(key)
        if len(self.active_keys) > 0:
            self.active_keys.clear()
        logger.debug("All hardware keys released")

    def get_active_keys(self):
        return list(self.active_keys)
        
    def update(self):
        pass # PyAutoGUI doesn't require manual pulsing for held keys
        
    def cleanup(self):
        self.release_all()
