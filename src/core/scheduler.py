# src/core/scheduler.py
import time
from datetime import datetime
from typing import List, Callable
from src.core.models import Event

def start_monitoring(events: List[Event], on_event_triggered: Callable[[Event], None]):
    """
    Starts an infinite background loop that checks the time every 30 seconds.
    If the current time matches an Event's time, it triggers the provided callback.
    
    Args:
        events (List[Event]): A list of Event objects to monitor.
        on_event_triggered (Callable): The function to execute when time is up.
    """
    print("🕒 Scheduler is running... (Proactive System Active)")
    
    # We use a set to keep track of events triggered today so they don't 
    # trigger 60 times during the same minute!
    triggered_today = set()

    while True:
        # Get current time in HH:MM format (e.g., "14:30")
        current_time = datetime.now().strftime("%H:%M")
        
        # Reset the tracker at midnight so events can run again tomorrow
        if current_time == "00:00":
            triggered_today.clear()

        for event in events:
            # Check if the time matches AND it hasn't been triggered yet today
            if event.time == current_time and event.time not in triggered_today:
                print(f"\n⏰ [TRIGGER] It is {current_time}! Time for: {event.event_type}")
                
                # Call the orchestrator's function and pass the event to it
                on_event_triggered(event)
                
                # Add to the set so it doesn't trigger again for this specific time
                triggered_today.add(event.time)
        
        # Sleep for 30 seconds before checking the clock again (saves CPU power)
        time.sleep(30)