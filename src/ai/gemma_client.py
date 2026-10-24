import importlib
import time

from src.config import resolve_model_name, settings


def generate_empathetic_message(prompt: str) -> str:
    if not settings.gemini_api_key:
        raise RuntimeError("GEMINI_API_KEY is required to generate a message.")

    try:
        genai = importlib.import_module("google.genai")
        client = genai.Client(api_key=settings.gemini_api_key)
        last_error: Exception | None = None
        for attempt in range(3):
            try:
                response = client.models.generate_content(
                    model=resolve_model_name(settings.gemini_model),
                    contents=prompt,
                )
                text = response.text or ""
                if not text.strip():
                    raise RuntimeError("Gemma returned an empty response.")
                return text.strip()
            except Exception as exc:
                last_error = exc
                if not any(
                    code in str(exc) for code in ("500", "503", "UNAVAILABLE")
                ):
                    raise
                if attempt < 2:
                    time.sleep(2**attempt)
        raise RuntimeError("Gemma request failed after retries.") from last_error
    except ImportError as exc:
        raise RuntimeError(
            "Install the Gemini SDK with: python -m pip install -r requirements.txt"
        ) from exc
    except Exception as exc:
        raise RuntimeError("Gemma API request failed.") from exc