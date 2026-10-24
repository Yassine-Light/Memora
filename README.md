# MemoryAnchor

MemoryAnchor is a memory and scheduling assistant for patients and caregivers.
The repository is organized into audio, AI, core domain, and interface layers.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python main.py
```

`GEMINI_API_KEY` is optional for starting the local scaffold and required only
when using the Gemma integration. Do not commit `.env` or real patient data.

## Layout

- `data/`: local persistence (`database.json` is a development seed).
- `src/audio/`: speech-to-text and text-to-speech boundaries.
- `src/ai/`: Gemma client and context-aware prompts.
- `src/core/`: domain models, scheduling, and orchestration.
- `src/interfaces/`: patient and supervisor UI entry points.
- `main.py`: backend startup entry point.

## Gemma usage

Set `GEMINI_API_KEY` in `.env` and configure `GEMINI_MODEL` for the available
Gemma model in your deployment. Verify consent, privacy, retention, and access
controls before using real patient information.
