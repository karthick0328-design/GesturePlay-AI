from collections import deque
import logging

logger = logging.getLogger("GesturePlay.GestureDetector")

class GestureDetector:
    def __init__(self, stable_frames=4):
        self.stable_frames = stable_frames
        self.history = deque(maxlen=stable_frames)
        self.current_stable_gesture = "NO_HAND"
        
    def _classify_raw_gesture(self, features):
        """
        Applies rules to classify the gesture based on landmark features.
        """
        fingers = features["fingers"]
        ext_count = sum([fingers["thumb"], fingers["index"], fingers["middle"], fingers["ring"], fingers["pinky"]])
        
        # Check orientation first
        orientation = features["orientation"]
        if orientation == "LEFT":
            return "PALM_LEFT"
        elif orientation == "RIGHT":
            return "PALM_RIGHT"
            
        # Check fingers
        if ext_count == 0 or (ext_count == 1 and fingers["thumb"]):
            # Sometimes thumb is hard to detect as folded
            return "FIST"
            
        if ext_count == 5 or (ext_count == 4 and not fingers["thumb"]):
            return "OPEN_PALM"
            
        if fingers["index"] and fingers["middle"] and not fingers["ring"] and not fingers["pinky"]:
            return "TWO_FINGERS"
            
        if fingers["index"] and not fingers["middle"] and not fingers["ring"] and not fingers["pinky"]:
            return "ONE_FINGER"
            
        return "UNKNOWN"
        
    def detect(self, features):
        """
        Returns the stable gesture.
        """
        if features is None:
            raw_gesture = "NO_HAND"
        else:
            raw_gesture = self._classify_raw_gesture(features)
            
        self.history.append(raw_gesture)
        
        # If the history is full and all recent frames have the same gesture
        if len(self.history) == self.stable_frames:
            if all(g == raw_gesture for g in self.history):
                if self.current_stable_gesture != raw_gesture:
                    logger.info(f"Gesture changed: {raw_gesture}")
                    self.current_stable_gesture = raw_gesture
                    
        return self.current_stable_gesture
