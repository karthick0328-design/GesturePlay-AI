import pytest
import sys
import os
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.control.action_mapper import ActionMapper

def create_temp_config(tmp_path):
    config = {
        "active_profile": "test_profile",
        "profiles": {
            "test_profile": {
                "gestures": {
                    "OPEN_PALM": "Action1",
                    "FIST": "Action2"
                },
                "keys": {
                    "Action1": "w",
                    "Action2": "s"
                }
            }
        }
    }
    file_path = tmp_path / "settings.json"
    with open(file_path, "w") as f:
        json.dump(config, f)
    return str(file_path)

def test_action_mapper_loads_config(tmp_path):
    config_path = create_temp_config(tmp_path)
    mapper = ActionMapper(config_path)
    
    assert mapper.active_profile_name == "test_profile"
    assert mapper.gestures_map["OPEN_PALM"] == "Action1"
    assert mapper.keys_map["Action1"] == "w"

def test_action_mapper_handle_gesture(tmp_path):
    config_path = create_temp_config(tmp_path)
    mapper = ActionMapper(config_path)
    
    # Mock the keyboard controller
    class MockKeyboardController:
        def __init__(self):
            self.active_keys = set()
            self.pressed = []
            self.released = []
        def key_down(self, key):
            self.active_keys.add(key)
            self.pressed.append(key)
        def key_up(self, key):
            if key in self.active_keys:
                self.active_keys.remove(key)
                self.released.append(key)
        def get_active_keys(self):
            return list(self.active_keys)
        def release_all(self):
            self.active_keys.clear()
            self.released.append("ALL")
            
    mapper.controller = MockKeyboardController()
    
    # Test valid gesture
    mapper.handle_gesture("OPEN_PALM")
    assert "w" in mapper.controller.pressed
    assert len(mapper.controller.get_active_keys()) == 1
    
    # Test gesture change
    mapper.handle_gesture("FIST")
    assert "w" in mapper.controller.released
    assert "s" in mapper.controller.pressed
    
    # Test NO_HAND
    mapper.handle_gesture("NO_HAND")
    assert "ALL" in mapper.controller.released
    assert len(mapper.controller.get_active_keys()) == 0

def test_action_mapper_custom_profile(tmp_path):
    config = {
        "active_profile": "custom",
        "profiles": {
            "custom": {
                "gestures": {
                    "OPEN_PALM": "UpAction",
                    "FIST": "DownAction"
                },
                "keys": {
                    "UpAction": "up",
                    "DownAction": "down"
                }
            }
        }
    }
    file_path = tmp_path / "settings.json"
    import json
    with open(file_path, "w") as f:
        json.dump(config, f)
        
    mapper = ActionMapper(str(file_path))
    assert mapper.active_profile_name == "custom"
    assert mapper.gestures_map["OPEN_PALM"] == "UpAction"
    assert mapper.keys_map["UpAction"] == "up"
