import cv2
import sys
import os

# Add parent dir to path so we can import modules properly if run directly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.utils.logger import get_logger
from app.utils.fps_counter import FPSCounter
from app.camera.camera_manager import CameraManager
from app.vision.hand_tracker import HandTracker
from app.vision.landmark_processor import LandmarkProcessor
from app.vision.gesture_detector import GestureDetector
from app.control.action_mapper import ActionMapper
from app.ui.dashboard import Dashboard
from app.calibration.calibrator import Calibrator
from app.ui.settings_window import SettingsWindow

from app.utils.history_tracker import HistoryTracker

def main():
    logger = get_logger()
    logger.info("Starting GesturePlay AI...")
    
    # Initialize components
    mapper = ActionMapper()
    camera = CameraManager(camera_index=0) # Index can be loaded from config
    tracker = HandTracker()
    processor = LandmarkProcessor()
    
    # Load persisted calibration
    try:
        import json, os
        if os.path.exists("app/config/settings.json"):
            with open("app/config/settings.json", "r") as f:
                config = json.load(f)
            saved_scale = config.get("reference_hand_size")
            if saved_scale:
                processor.reference_hand_size = saved_scale
                logger.info(f"Loaded persisted calibration scale: {saved_scale:.4f}")
    except Exception as e:
        logger.error(f"Failed to load calibration data: {e}")
        
    detector = GestureDetector(stable_frames=4)
    ui = Dashboard()
    calibrator = Calibrator()
    fps = FPSCounter()
    history = HistoryTracker(max_size=5)
    last_history_gesture = "NO_HAND"
    
    if not camera.start():
        logger.error("Failed to start camera. Exiting.")
        return
        
    # Make window resizable and set a small default size so it doesn't block the screen
    cv2.namedWindow("GesturePlay AI", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("GesturePlay AI", 480, 360)
        
    try:
        while True:
            fps.start_frame()
            
            ret, frame = camera.read_frame()
            if not ret:
                logger.warning("Failed to grab frame.")
                break
                
            # Computer Vision Pipeline
            results = tracker.process_frame(frame)
            
            features = None
            hand_detected = False
            confidence = 0
            
            if results.multi_hand_landmarks:
                hand_detected = True
                # We only process the first hand for now
                hand_landmarks = results.multi_hand_landmarks[0]
                
                # Draw landmarks on the frame
                frame = tracker.draw_landmarks(frame, results)
                
                # Process landmarks into features
                features = processor.process(hand_landmarks)
                confidence = features.get("confidence", 0) * 100
                
            # Handle Calibration
            calib_progress = -1.0
            if calibrator.is_calibrating:
                calib_progress = calibrator.process(features, processor)
                
            # Gesture Detection & Mapping
            gesture = detector.detect(features)
            
            # Action Mapping
            if not calibrator.is_calibrating:
                mapper.handle_gesture(gesture)
                mapper.controller.update() # Pulse held keys for game engines
                
            current_action = mapper.get_current_action()
            current_key = mapper.get_current_key()
            if gesture != last_history_gesture:
                if gesture != "NO_HAND" and gesture != "UNKNOWN":
                    history.add_event(gesture.replace("_", " "), current_action)
                last_history_gesture = gesture
                
            # UI Updates
            fps.end_frame()
            stats = {
                "hand_detected": hand_detected,
                "gesture": gesture.replace("_", " "),
                "action": current_action.upper() if current_action else "NONE",
                "active_key": current_key,
                "confidence": confidence,
                "fps": fps.get_fps(),
                "latency": fps.get_latency_ms(),
                "profile": mapper.active_profile_name.upper(),
                "calib_progress": calib_progress,
                "history": history.get_recent_events()
            }
            frame = ui.draw(frame, stats)
            
            # Display
            cv2.imshow("GesturePlay AI", frame)
            
            # Input Handling
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                logger.info("Quit requested by user.")
                break
            elif key == ord('c'):
                calibrator.start()
            elif key == ord('s'):
                logger.info("Opening Settings Window...")
                mapper.release_all()
                # Run tkinter blocking main loop. Camera processing will pause.
                # When window closes, callback reloads ActionMapper config.
                SettingsWindow(on_close_callback=mapper.load_config).run()
                
    except Exception as e:
        logger.exception(f"An unexpected error occurred: {e}")
        
    finally:
        # Safety Cleanup
        logger.info("Shutting down safely...")
        mapper.cleanup()
        tracker.cleanup()
        camera.stop()
        cv2.destroyAllWindows()
        logger.info("Shutdown complete.")

if __name__ == "__main__":
    main()
