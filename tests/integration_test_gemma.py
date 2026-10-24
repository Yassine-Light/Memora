"""End-to-end smoke test for the AI and core MemoryAnchor pipeline.

This test verifies:

* configuration and the optional local ``.env`` file;
* ``data/database.json`` loading into ``Patient`` and ``Event`` models;
* scheduler event delivery;
* orchestrator prompt construction;
* Gemma response generation when ``GEMINI_API_KEY`` is configured.

Run from the repository root with:

    .venv/bin/python -m tests.integration_test_gemma
"""

from __future__ import annotations

from dataclasses import replace
import importlib
import os
from pathlib import Path
import sys
import time
from unittest.mock import patch


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))


def load_local_env() -> None:
    """Load simple KEY=VALUE entries from the repository's optional .env file."""
    env_path = REPOSITORY_ROOT / ".env"
    if not env_path.is_file():
        return

    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip("\"'"))


load_local_env()

from src import config
from src.core import orchestrator, scheduler
from src.core.models import Event


def generate_test_response(prompt: str) -> str:
    """Generate a live response, or a deterministic offline response."""
    if not config.settings.gemini_api_key:
        return "Othman, please take your medicine with some water."

    try:
        genai = importlib.import_module("google.genai")
    except ImportError as exc:
        raise RuntimeError(
            "Install the current Gemini SDK with: "
            ".venv/bin/python -m pip install google-genai"
        ) from exc

    client = genai.Client(api_key=config.settings.gemini_api_key)
    last_error: Exception | None = None
    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model=config.resolve_model_name(config.settings.gemini_model),
                contents=prompt,
            )
            text = response.text or ""
            if not text.strip():
                raise RuntimeError("Gemma returned an empty response.")
            return text.strip()
        except Exception as exc:
            last_error = exc
            error_text = str(exc)
            if not any(code in error_text for code in ("500", "503", "UNAVAILABLE")):
                raise
            if attempt < 2:
                time.sleep(2**attempt)

    raise RuntimeError("Gemma request failed after retries.") from last_error


class _FixedClock:
    """Make the infinite scheduler perform one deterministic check."""

    @classmethod
    def now(cls):
        from datetime import datetime

        return datetime.now()


class _StopAfterOneSleep:
    """Stop only the scheduler loop without patching global ``time.sleep``."""

    @staticmethod
    def sleep(_seconds: int) -> None:
        raise StopIteration


def run_integration_test() -> int:
    print("Starting MemoryAnchor AI/core integration test...\n")

    settings = config.settings
    if not settings.database_path.is_file():
        print(f"FAILED: database file not found: {settings.database_path}")
        return 1

    patient, events = orchestrator.load_data(str(settings.database_path))
    if not events:
        print("FAILED: database contains no events.")
        return 1
    print(f"PASS: loaded {patient.name} and {len(events)} scheduled events.")

    triggered: list[Event] = []
    responses: list[str] = []

    def handle_event(event: Event) -> None:
        triggered.append(event)
        with patch.object(
            orchestrator,
            "generate_empathetic_message",
            side_effect=lambda prompt: responses.append(
                generate_test_response(prompt)
            )
            or responses[-1],
        ):
            orchestrator.handle_triggered_event(event, patient)

    event_to_run = replace(events[0], time=_FixedClock.now().strftime("%H:%M"))
    try:
        with patch.object(scheduler, "datetime", _FixedClock):
            with patch.object(scheduler, "time", _StopAfterOneSleep):
                scheduler.start_monitoring([event_to_run], handle_event)
    except StopIteration:
        # The patched sleep stops the scheduler after its first polling cycle.
        pass
    except RuntimeError as exc:
        print(f"FAILED: AI/core pipeline could not produce a response: {exc}")
        return 1

    if triggered != [event_to_run]:
        print("FAILED: scheduler did not trigger the expected event.")
        return 1
    if not responses or not responses[0].strip():
        print("FAILED: orchestrator did not produce an AI response.")
        return 1

    print("PASS: scheduler triggered the event and orchestrator produced a response.")
    if settings.gemini_api_key:
        print("\nGemma response:")
        print(responses[0])
        print("\nPASS: live Gemma integration completed.")
    else:
        print("PASS: offline integration completed (GEMINI_API_KEY is not configured).")
    return 0


if __name__ == "__main__":
    raise SystemExit(run_integration_test())
