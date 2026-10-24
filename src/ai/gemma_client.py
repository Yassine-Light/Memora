"""Gemma client boundary.

The provider SDK is intentionally imported only when a request is made so the
application can start in local/offline mode.
"""

from dataclasses import dataclass


@dataclass
class GemmaClient:
    api_key: str
    model: str = "gemma-3-27b-it"

    def generate(self, prompt: str) -> str:
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is required to use the Gemma client.")

        try:
            import google.generativeai as genai
        except ImportError as exc:
            raise RuntimeError(
                "Install requirements.txt to enable the Gemma integration."
            ) from exc

        genai.configure(api_key=self.api_key)
        return genai.GenerativeModel(self.model).generate_content(prompt).text

