import pytest
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.control.keyboard_controller import KeyboardController

class MockKeyboardLib:
    def __init__(self):
        self.pressed_keys = set()
        
    def keyDown(self, key):
        self.pressed_keys.add(key)
        
    def keyUp(self, key):
        if key in self.pressed_keys:
            self.pressed_keys.remove(key)
            
    def press(self, key):
        pass

def test_keyboard_controller_state_tracking(monkeypatch):
    import app.control.keyboard_controller as kc
    pressed = []
    
    def mock_send_input(num, ptr, size):
        key = ptr[0].ii.ki.wScan
        flags = ptr[0].ii.ki.dwFlags
        if flags & 0x0002: # release
            pass
        else:
            pressed.append(key)
            
    monkeypatch.setattr(kc, 'SendInput', mock_send_input)
    
    controller = KeyboardController()

    controller.key_down("w")
    assert "w" in controller.active_keys
    
    controller.key_down("w")
    assert len(controller.active_keys) == 1
    
    controller.key_up("w")
    assert "w" not in controller.active_keys

def test_keyboard_controller_release_all(monkeypatch):
    import app.control.keyboard_controller as kc
    monkeypatch.setattr(kc, 'SendInput', lambda a,b,c: None)
    
    controller = KeyboardController()
    
    controller.key_down("w")
    controller.key_down("space")
    assert len(controller.active_keys) == 2
    
    controller.release_all()
    assert len(controller.active_keys) == 0
