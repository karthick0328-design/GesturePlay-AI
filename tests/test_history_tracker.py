import pytest
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.utils.history_tracker import HistoryTracker

def test_history_tracker_bounds():
    tracker = HistoryTracker(max_size=3)
    
    tracker.add_event("OPEN_PALM", "w")
    tracker.add_event("FIST", "s")
    tracker.add_event("TWO_FINGERS", "space")
    
    events = tracker.get_recent_events()
    assert len(events) == 3
    assert events[0]["gesture"] == "OPEN_PALM"
    
    # Add 4th event, should push out the first
    tracker.add_event("PALM_LEFT", "a")
    events = tracker.get_recent_events()
    assert len(events) == 3
    assert events[0]["gesture"] == "FIST"
    assert events[-1]["gesture"] == "PALM_LEFT"
