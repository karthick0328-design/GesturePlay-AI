import math
import numpy as np

class LandmarkProcessor:
    """
    Processes raw MediaPipe normalized landmarks into actionable geometric features.
    Indices (MediaPipe Standard):
    0: Wrist
    1-4: Thumb
    5-8: Index
    9-12: Middle
    13-16: Ring
    17-20: Pinky
    """
    
    def __init__(self):
        # Base scale to normalize distances, updated via calibration
        self.reference_hand_size = 1.0 

    def get_distance(self, p1, p2):
        """Calculates Euclidean distance between two landmarks (normalized coords)."""
        return math.hypot(p1.x - p2.x, p1.y - p2.y)

    def analyze_fingers(self, landmarks):
        """
        Determines which fingers are extended based on distances from the wrist.
        Alternatively, compares y-coordinates if the hand is upright, but 
        distance-based is more robust to rotation.
        """
        wrist = landmarks[0]
        
        # Thumb is special, we check if it's extended away from the palm (using x/y relative to MCP)
        # For a more robust thumb check, compare thumb tip to pinky mcp distance vs thumb ip to pinky mcp
        thumb_tip = landmarks[4]
        thumb_ip = landmarks[3]
        pinky_mcp = landmarks[17]
        thumb_extended = self.get_distance(thumb_tip, pinky_mcp) > self.get_distance(thumb_ip, pinky_mcp)

        # Other fingers: tip (8, 12, 16, 20) vs pip (6, 10, 14, 18) distance from wrist
        index_extended = self.get_distance(landmarks[8], wrist) > self.get_distance(landmarks[6], wrist)
        middle_extended = self.get_distance(landmarks[12], wrist) > self.get_distance(landmarks[10], wrist)
        ring_extended = self.get_distance(landmarks[16], wrist) > self.get_distance(landmarks[14], wrist)
        pinky_extended = self.get_distance(landmarks[20], wrist) > self.get_distance(landmarks[18], wrist)

        return {
            "thumb": thumb_extended,
            "index": index_extended,
            "middle": middle_extended,
            "ring": ring_extended,
            "pinky": pinky_extended
        }

    def calculate_hand_orientation(self, landmarks):
        """
        Estimates if the hand is tilted left or right based on the wrist and middle finger MCP.
        """
        wrist = landmarks[0]
        middle_mcp = landmarks[9]
        
        dx = middle_mcp.x - wrist.x
        dy = middle_mcp.y - wrist.y
        
        # Angle in degrees
        angle = math.degrees(math.atan2(dy, dx))
        
        # -90 is pointing straight up.
        # -60 to 60 is pointing right
        # 120 to 180, or -180 to -120 is pointing left
        
        orientation = "CENTER"
        if -60 <= angle <= 60:
            orientation = "RIGHT"
        elif angle >= 120 or angle <= -120:
            orientation = "LEFT"
            
        return orientation, angle

    def process(self, hand_landmarks):
        """Main processing function returning a dictionary of features."""
        landmarks = hand_landmarks.landmark
        
        # Calculate bounding box (normalized)
        x_coords = [lm.x for lm in landmarks]
        y_coords = [lm.y for lm in landmarks]
        bbox = {
            "x_min": min(x_coords), "x_max": max(x_coords),
            "y_min": min(y_coords), "y_max": max(y_coords)
        }
        
        # Hand scale estimation (wrist to middle finger mcp)
        hand_scale = self.get_distance(landmarks[0], landmarks[9])
        
        fingers = self.analyze_fingers(landmarks)
        orientation, angle = self.calculate_hand_orientation(landmarks)
        
        # Calculate confidence metric based on visibility if available, else standard 1.0
        confidence = 0.95 # Placeholder for rule-based structural confidence
        
        return {
            "fingers": fingers,
            "orientation": orientation,
            "angle": angle,
            "hand_scale": hand_scale,
            "bbox": bbox,
            "confidence": confidence
        }
