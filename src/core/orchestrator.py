# src/core/orchestrator.py
import json
import os
from src.core.models import Patient, Event
from src.ai.prompt_engine import build_proactive_prompt
from src.ai.gemma_client import generate_empathetic_message
from src.core.scheduler import start_monitoring

# Note: We will import the Text-to-Speech (TTS) function programmed by your friend later
# from src.audio.tts_service import speak

def load_data(filepath: str):
    """
    Reads the database.json file and converts it into programmatically safe objects (Models).
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Data file not found at path: {filepath}")
        
    with open(filepath, 'r', encoding='utf-8') as file:
        data = json.load(file)
        
    # Convert dictionaries into Patient and Event objects
    patient = Patient(**data['patient'])
    events = [Event(**event_data) for event_data in data['events']]
    
    return patient, events

def handle_triggered_event(event: Event, patient: Patient):
    """
    The function called by the scheduler when it is time for the event.
    """
    print(f"\n⚙️ [Orchestrator] Started processing event: {event.event_type}...")
    
    # 1. Build the prompt
    prompt = build_proactive_prompt(patient, event)
    
    # 2. Get the empathetic message from the Gemma 4 model
    ai_sentence = generate_empathetic_message(prompt)
    
    print(f"🧠 [Gemma 4]: {ai_sentence}")
    
    # 3. Pass the sentence to the audio system to speak it out loud (to be enabled later)
    print("🔊 [Orchestrator] Sending text to audio player...")
    # speak(ai_sentence)  

def run_system():
    """
    Main entry point for running the backend engine.
    """
    print("🚀 Initializing MemoryAnchor system...")
    
    # Determine the JSON file path (relative to this file)
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    data_path = os.path.join(base_dir, 'data', 'database.json')
    
    try:
        # Load data
        patient, events = load_data(data_path)
        print(f"✅ Patient profile loaded: {patient.name}")
        print(f"✅ Found {len(events)} scheduled tasks.")
        
        # Run the time monitor, telling it to call handle_triggered_event at each scheduled time
        # We use lambda to pass the fixed patient object with each new event
        start_monitoring(events, lambda triggered_event: handle_triggered_event(triggered_event, patient))
        
    except Exception as e:
        print(f"❌ Failed to run the system: {e}")

if __name__ == "__main__":
    run_system()