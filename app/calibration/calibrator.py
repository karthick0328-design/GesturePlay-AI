import logging

logger = logging.getLogger("GesturePlay.Calibrator")

class Calibrator:
    def __init__(self, frames_needed=30):
        self.frames_needed = frames_needed
        self.is_calibrating = False
        self.calibration_data = []
        self.calibration_done = False
        
    def start(self):
        self.is_calibrating = True
        self.calibration_data = []
        self.calibration_done = False
        logger.info("Calibration started. Keep your hand visible...")
        
    def process(self, features, landmark_processor):
        """
        Processes features during calibration mode.
        Returns calibration progress (0.0 to 1.0)
        """
        if not self.is_calibrating:
            return 0.0
            
        if features is None:
            # Skip frames without a hand
            return len(self.calibration_data) / self.frames_needed
            
        self.calibration_data.append(features["hand_scale"])
        
        if len(self.calibration_data) >= self.frames_needed:
            self._finish(landmark_processor)
            
        return len(self.calibration_data) / self.frames_needed
            
    def _finish(self, landmark_processor):
        self.is_calibrating = False
        self.calibration_done = True
        avg_scale = sum(self.calibration_data) / len(self.calibration_data)
        landmark_processor.reference_hand_size = avg_scale
        logger.info(f"Calibration complete. Base hand scale set to: {avg_scale:.4f}")
        
        # Save to settings.json
        try:
            import json, os
            config_path = "app/config/settings.json"
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    config = json.load(f)
                config["reference_hand_size"] = avg_scale
                
                temp_path = config_path + ".tmp"
                with open(temp_path, 'w') as f:
                    json.dump(config, f, indent=2)
                os.replace(temp_path, config_path)
        except Exception as e:
            logger.error(f"Failed to save calibration data: {e}")
