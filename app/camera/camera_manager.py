import cv2
import logging

logger = logging.getLogger("GesturePlay.Camera")

class CameraManager:
    def __init__(self, camera_index=0, width=640, height=480):
        self.camera_index = camera_index
        self.width = width
        self.height = height
        self.cap = None
        
    def start(self):
        """Initializes the webcam."""
        logger.info(f"Initializing camera {self.camera_index}...")
        self.cap = cv2.VideoCapture(self.camera_index)
        
        if not self.cap.isOpened():
            logger.error(f"Failed to open camera {self.camera_index}")
            return False
            
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        
        # Attempt to set 30 FPS
        self.cap.set(cv2.CAP_PROP_FPS, 30)
        
        actual_width = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        actual_height = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        logger.info(f"Camera initialized at resolution {int(actual_width)}x{int(actual_height)}")
        return True
        
    def read_frame(self):
        """Reads a frame, flips it for mirror effect, and returns it."""
        if self.cap is None or not self.cap.isOpened():
            return False, None
            
        ret, frame = self.cap.read()
        if ret:
            # Mirror the frame so it behaves like a mirror
            frame = cv2.flip(frame, 1)
        return ret, frame
        
    def stop(self):
        """Releases the camera resources."""
        if self.cap is not None:
            self.cap.release()
            self.cap = None
            logger.info("Camera released.")
