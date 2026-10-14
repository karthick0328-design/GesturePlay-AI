import time
from collections import deque

class FPSCounter:
    def __init__(self, maxlen=30):
        self.frame_times = deque(maxlen=maxlen)
        self.start_time = None
        
    def start_frame(self):
        """Called at the beginning of frame processing."""
        self.start_time = time.time()
        
    def end_frame(self):
        """Called at the end of frame processing."""
        if self.start_time is not None:
            end_time = time.time()
            self.frame_times.append(end_time - self.start_time)
            
    def get_fps(self):
        """Returns the current average FPS."""
        if len(self.frame_times) == 0:
            return 0.0
        avg_time = sum(self.frame_times) / len(self.frame_times)
        if avg_time == 0:
            return 0.0
        return 1.0 / avg_time
        
    def get_latency_ms(self):
        """Returns the current average frame processing latency in milliseconds."""
        if len(self.frame_times) == 0:
            return 0.0
        avg_time = sum(self.frame_times) / len(self.frame_times)
        return avg_time * 1000.0
