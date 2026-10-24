"""Speech-to-text service boundary."""

from dataclasses import dataclass


@dataclass
class SpeechToTextService:
    """Provider-neutral speech-to-text service.

    A provider can be injected later without coupling the core orchestrator to it.
    """

    def transcribe(self, audio_path: str) -> str:
        raise NotImplementedError(
            "Speech-to-text provider is not configured for this deployment."
        )

