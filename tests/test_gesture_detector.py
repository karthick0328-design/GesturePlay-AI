import pytest
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.vision.gesture_detector import GestureDetector

def create_mock_features(ext_fingers, orientation="CENTER"):
    fingers = {
        "thumb": "thumb" in ext_fingers,
        "index": "index" in ext_fingers,
        "middle": "middle" in ext_fingers,
        "ring": "ring" in ext_fingers,
        "pinky": "pinky" in ext_fingers
    }
    return {
        "fingers": fingers,
        "orientation": orientation,
        "angle": -90,
        "hand_scale": 1.0,
        "confidence": 1.0
    }

def test_gesture_detector_fist():
    detector = GestureDetector(stable_frames=2)
    features = create_mock_features([])
    
    # Frame 1: Not stable yet
    assert detector.detect(features) == "NO_HAND"
    
    # Frame 2: Stable
    assert detector.detect(features) == "FIST"

def test_gesture_detector_open_palm():
    detector = GestureDetector(stable_frames=2)
    features = create_mock_features(["thumb", "index", "middle", "ring", "pinky"])
    
    detector.detect(features)
    assert detector.detect(features) == "OPEN_PALM"

def test_gesture_detector_two_fingers():
    detector = GestureDetector(stable_frames=2)
    features = create_mock_features(["index", "middle"])
    
    detector.detect(features)
    assert detector.detect(features) == "TWO_FINGERS"

def test_gesture_detector_orientation():
    detector = GestureDetector(stable_frames=1)
    features = create_mock_features(["index", "middle"], orientation="LEFT")
    assert detector.detect(features) == "PALM_LEFT"
    
    features = create_mock_features(["index", "middle"], orientation="RIGHT")
    assert detector.detect(features) == "PALM_RIGHT"

def test_gesture_detector_no_hand():
    detector = GestureDetector(stable_frames=1)
    # Give it some hand first
    features = create_mock_features([])
    assert detector.detect(features) == "FIST"
    
    # Hand lost
    assert detector.detect(None) == "NO_HAND"

def test_gesture_stabilization():
    detector = GestureDetector(stable_frames=3)
    palm = create_mock_features(["thumb", "index", "middle", "ring", "pinky"])
    fist = create_mock_features([])
    
    assert detector.detect(palm) == "NO_HAND"
    assert detector.detect(palm) == "NO_HAND"
    assert detector.detect(palm) == "OPEN_PALM"
    
    # Flickering
    assert detector.detect(fist) == "OPEN_PALM"
    assert detector.detect(palm) == "OPEN_PALM"
    assert detector.detect(fist) == "OPEN_PALM"
    
    # Stable fist
    assert detector.detect(fist) == "OPEN_PALM"
    assert detector.detect(fist) == "FIST"
