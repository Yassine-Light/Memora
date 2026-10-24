# src/core/models.py
from dataclasses import dataclass
from typing import List

@dataclass
class Event:
    """Model representing scheduled tasks or events"""
    time: str             # Example: "14:00" or "08:30"
    event_type: str       # Event type: "food", "medicine", "date"
    description: str      # Details: "Taking blood pressure medication", "Doctor's appointment"

@dataclass
class Patient:
    """Model representing patient data (personal context)"""
    name: str
    age: int
    situation: str        # Marital/social status (Example: married to Khadija)
    profession: str       # Previous profession (Example: retired math teacher)
    family: List[str]     # Closest 5 people (Example: ["Ahmed (son)", "Sarah (daughter)"])
    hobby: str            # Hobby for building rapport (Example: gardening, listening to Andalusi music)