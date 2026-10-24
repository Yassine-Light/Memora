⚓ MemoryAnchor (Memora)
Zero-Friction, Proactive Memory Care for Alzheimer's Patients.

💡 The Problem
For patients with Alzheimer's and dementia, standard voice assistants fail. Why? Because they require the patient to remember to ask for help. A patient suffering from memory loss will not remember to press a microphone button or say a wake word to check their medication schedule.

🚀 Our Solution: The "Zero-UI" Approach
MemoryAnchor flips the standard AI paradigm. It is a 100% proactive, empathetic voice companion. The system does not wait for prompts. It monitors the patient's daily schedule and autonomously wakes up to deliver warm, highly contextual, and personalized voice reminders in "White Arabic" (a simplified, warm formal Arabic optimized for Text-to-Speech clarity and cultural resonance).

✨ Key Features (The Wow Factor)
⏱️ Proactive Event Scheduler: An independent background engine that triggers events exactly on time. No user interaction required.

🧠 Empathetic AI (Powered by Google Gemma/Gemini): Dynamically generates warm, comforting prompts based on the patient's profile (age, hobbies, family context) rather than sounding like a robotic alarm.

🗣️ "White Arabic" Optimization: Carefully engineered prompts ensure the AI outputs text that current TTS engines can pronounce flawlessly without robotic dialect errors.

🛡️ Bulletproof Fallback System: Built for the real world. If the API fails or Wi-Fi drops, the system instantly falls back to hardcoded, comforting Arabic messages.

🏗️ Technical Architecture
We built MemoryAnchor using a clean, modular, MVP-focused architecture (Single Responsibility Principle):

core/: The heartbeat. Contains data models (pydantic/dataclasses), the JSON database loader, and the independent scheduler.py time-monitor.

ai/: The brain. Houses the prompt_engine.py (context injection) and gemma_client.py (API connectivity and error handling).

orchestrator.py: The Maestro. Links the heartbeat to the brain, piping the AI's response to the audio output system.

🛠️ Tech Stack
Language: Python 3.12

AI / LLM: Google Generative AI API (Gemma / Gemini Flash for sub-second latency)

Data: Local JSON (for rapid MVP deployment without database latency)

Testing: unittest (Full suite of domain and integration tests passed)

🚦 How to Run Locally
Clone & Setup Environment:

git clone https://github.com/your-username/MemoryAnchor.git
cd MemoryAnchor
python3 -m venv venv
source venv/bin/activate

Install Dependencies:

pip install -r requirements.txt

Configure API Key: Create a .env file in the root directory:

GEMINI_API_KEY=your_google_api_key_here
GEMINI_MODEL=gemini-1.5-flash-8b  # Optimized for real-time TTS demo

Run the Orchestrator:

python main.py

The system will load the patient profile and begin monitoring the clock to trigger proactive care.

🏆 Hackathon Track Focus
This project was built with a focus on Originality and Usefulness. By removing the need for patient interaction, we provide a genuinely viable tool for senior care facilities and families.

Built with ❤️ for the Hackathon.