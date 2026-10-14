import mediapipe as mp
import cv2
import logging

logger = logging.getLogger("GesturePlay.HandTracker")

class HandTracker:
    def __init__(self, max_num_hands=1, min_detection_confidence=0.7, min_tracking_confidence=0.7):
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=max_num_hands,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence
        )
        logger.info("MediaPipe HandTracker initialized.")
        
    def process_frame(self, frame):
        """
        Processes a BGR frame and returns MediaPipe hand landmark results.
        Note: MediaPipe expects RGB images.
        """
        # Convert BGR to RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # To improve performance, optionally mark the image as not writeable to pass by reference.
        frame_rgb.flags.writeable = False
        results = self.hands.process(frame_rgb)
        frame_rgb.flags.writeable = True
        
        return results
        
    def draw_landmarks(self, frame, results):
        """
        Draws hand landmarks on the provided BGR frame.
        """
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                self.mp_drawing.draw_landmarks(
                    frame,
                    hand_landmarks,
                    self.mp_hands.HAND_CONNECTIONS,
                    self.mp_drawing_styles.get_default_hand_landmarks_style(),
                    self.mp_drawing_styles.get_default_hand_connections_style()
                )
        return frame
        
    def cleanup(self):
        self.hands.close()
