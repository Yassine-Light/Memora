"""Text-to-speech service boundary."""

from dataclasses import dataclass


@dataclass
class TextToSpeechService:
    """Provider-neutral text-to-speech service."""

    def synthesize(self, text: str, output_path: str) -> str:
        raise NotImplementedError(
            "Text-to-speech provider is not configured for this deployment."
        )

