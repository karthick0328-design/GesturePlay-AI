from collections import deque
from datetime import datetime

class HistoryTracker:
    def __init__(self, max_size=5):
        self.events = deque(maxlen=max_size)
        
    def add_event(self, gesture, action):
        """Records a timestamped gesture and its mapped action."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.events.append({"time": timestamp, "gesture": gesture, "action": action})
        
    def get_recent_events(self):
        """Returns the list of recent events."""
        return list(self.events)
