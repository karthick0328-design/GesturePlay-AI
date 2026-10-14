import cv2

class Dashboard:
    def __init__(self):
        # Colors (BGR)
        self.bg_color = (30, 30, 30)
        self.text_color = (255, 255, 255)
        self.accent_color = (0, 200, 100)
        self.alert_color = (50, 50, 255)
        
    def draw(self, frame, stats):
        """
        Draws the dashboard overlay on the frame.
        stats: dict containing fps, latency, gesture, action, confidence, profile
        """
        # Create a semi-transparent sidebar
        h, w, _ = frame.shape
        sidebar_w = max(250, int(w * 0.3))
        
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (sidebar_w, h), self.bg_color, -1)
        
        # Alpha blend the sidebar
        alpha = 0.8
        cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)
        
        # Draw Title
        cv2.putText(frame, "GESTUREPLAY AI", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, self.accent_color, 2)
        cv2.line(frame, (20, 55), (sidebar_w - 20, 55), self.accent_color, 1)
        
        # State display
        # Hand status
        hand_status = "DETECTED" if stats.get("hand_detected") else "NOT DETECTED"
        hand_color = self.accent_color if hand_status == "DETECTED" else (0, 0, 255)
        self._draw_row(frame, "Hand:", hand_status, 20, 70, hand_color)
        
        # Action overlay
        self._draw_row(frame, "Gesture:", stats.get("gesture", "UNKNOWN"), 20, 110)
        self._draw_row(frame, "Confidence:", f"{stats.get('confidence', 0.0):.0%}", 20, 140)
        self._draw_row(frame, "Action:", stats.get("action", "NONE"), 20, 170)
        self._draw_row(frame, "Active Key:", stats.get("active_key", "NONE"), 20, 200)
        
        # Perf overlay
        y_offset = 240
        self._draw_row(frame, "FPS:", f"{stats.get('fps', 0):.1f}", 20, y_offset)
        y_offset += 30
        
        self._draw_row(frame, "Latency:", f"~{stats.get('latency', 0):.1f} ms", 20, y_offset)
        y_offset += 30
        
        self._draw_row(frame, "Profile:", stats.get("profile", "UNKNOWN"), 20, y_offset)
        
        # Legend & Controls
        y_offset = h - 60
        cv2.putText(frame, "Controls:", (20, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.5, self.text_color, 1)
        cv2.putText(frame, "[Q] Quit  [C] Calibrate  [S] Settings", (20, y_offset + 25), cv2.FONT_HERSHEY_SIMPLEX, 0.5, self.text_color, 1)
        
        # Gesture History
        history = stats.get("history", [])
        if history:
            hist_y = h - 140
            cv2.putText(frame, "GESTURE HISTORY:", (sidebar_w + 20, hist_y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, self.text_color, 1)
            hist_y += 25
            for event in history:
                text = f"{event['time']}  {event['gesture']} -> {event['action']}"
                cv2.putText(frame, text, (sidebar_w + 20, hist_y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, self.accent_color, 1)
                hist_y += 20

        # Calibration overlay
        calib_progress = stats.get("calib_progress", -1)
        if calib_progress >= 0:
            cv2.putText(frame, f"CALIBRATING: {int(calib_progress * 100)}%", (sidebar_w + 50, 50), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1.0, self.alert_color, 2)
                        
        return frame

    def _draw_row(self, frame, label, value, x, y, val_color=None):
        if val_color is None:
            val_color = self.text_color
        cv2.putText(frame, label, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, self.text_color, 1)
        cv2.putText(frame, value, (x + 120, y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, val_color, 2)
