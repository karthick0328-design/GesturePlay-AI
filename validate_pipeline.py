import sys
import os
import time

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app.vision.landmark_processor import LandmarkProcessor
from app.vision.gesture_detector import GestureDetector
from app.control.action_mapper import ActionMapper

class MockLandmark:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class MockHandLandmarks:
    def __init__(self, coords):
        self.landmark = [MockLandmark(x, y) for x, y in coords]

def create_hand_coords(fingers_ext, orientation="CENTER"):
    # Base coords (wrist at 0.5, 0.9)
    coords = [(0.5, 0.9)] * 21
    
    # Orientation modifier
    # Default is pointing UP (wrist at 0.9, MCPs around 0.5)
    # LEFT means pointing LEFT (wrist at 0.9, MCPs at left)
    ox, oy = 0.5, 0.5
    if orientation == "LEFT":
        ox, oy = 0.1, 0.9 # Leftwards
    elif orientation == "RIGHT":
        ox, oy = 0.9, 0.9 # Rightwards
        
    # Wrist
    coords[0] = (0.5, 0.9)
    
    # Thumb (4 is tip, 3 is IP, 17 is Pinky MCP)
    coords[17] = (0.7, 0.6) # Pinky MCP
    coords[3] = (0.3, 0.6)  # Thumb IP
    if "thumb" in fingers_ext:
        coords[4] = (0.1, 0.5) # Thumb Tip extended far from Pinky MCP
    else:
        coords[4] = (0.4, 0.6) # Thumb Tip close to Pinky MCP

    # Index (8 is tip, 6 is PIP)
    coords[6] = (ox - 0.1, oy)
    if "index" in fingers_ext:
        coords[8] = (ox - 0.1, oy - 0.2) # Tip further from wrist than PIP
    else:
        coords[8] = (ox - 0.1, oy + 0.1) # Tip closer to wrist
        
    # Middle (12 is tip, 10 is PIP)
    coords[9] = (ox, oy) # Middle MCP
    coords[10] = (ox, oy)
    if "middle" in fingers_ext:
        coords[12] = (ox, oy - 0.2)
    else:
        coords[12] = (ox, oy + 0.1)

    # Ring (16 is tip, 14 is PIP)
    coords[14] = (ox + 0.1, oy)
    if "ring" in fingers_ext:
        coords[16] = (ox + 0.1, oy - 0.2)
    else:
        coords[16] = (ox + 0.1, oy + 0.1)

    # Pinky (20 is tip, 18 is PIP)
    coords[18] = (ox + 0.2, oy)
    if "pinky" in fingers_ext:
        coords[20] = (ox + 0.2, oy - 0.2)
    else:
        coords[20] = (ox + 0.2, oy + 0.1)

    return MockHandLandmarks(coords)

def run_validation():
    processor = LandmarkProcessor()
    detector = GestureDetector(stable_frames=3)
    mapper = ActionMapper()
    
    gestures = [
        ("OPEN_PALM", ["thumb", "index", "middle", "ring", "pinky"], "CENTER"),
        ("FIST", [], "CENTER"),
        ("TWO_FINGERS", ["index", "middle"], "CENTER"),
        ("PALM_LEFT", ["thumb", "index", "middle", "ring", "pinky"], "LEFT"),
        ("PALM_RIGHT", ["thumb", "index", "middle", "ring", "pinky"], "RIGHT"),
        ("ONE_FINGER", ["index"], "CENTER"),
        ("NO_HAND", None, None)
    ]
    
    print("=== GESTURE VALIDATION ===")
    for expected, fingers, orient in gestures:
        # Feed 4 frames to ensure stability
        gesture_result = None
        for _ in range(4):
            if expected == "NO_HAND":
                gesture_result = detector.detect(None)
                mapper.handle_gesture(gesture_result)
            else:
                lms = create_hand_coords(fingers, orient)
                features = processor.process(lms)
                gesture_result = detector.detect(features)
                mapper.handle_gesture(gesture_result)
                
        active_keys = mapper.controller.get_active_keys()
        key_str = active_keys[0] if active_keys else "NONE"
        action = mapper.mapping.get(gesture_result, "NONE")
        if gesture_result == "NO_HAND":
            action = "NONE"
            
        print(f"Expected: {expected:<15} | Detected: {gesture_result:<15} | Action: {action:<10} | Key: {key_str}")

if __name__ == "__main__":
    run_validation()
