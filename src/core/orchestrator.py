"""Application service coordinating memory context and AI responses."""

from collections.abc import Iterable

from src.ai.prompt_engine import build_context_prompt


class Orchestrator:
    def __init__(self, ai_client) -> None:
        self.ai_client = ai_client

    def respond(self, message: str, memories: Iterable[str]) -> str:
        prompt = build_context_prompt(message, memories)
        return self.ai_client.generate(prompt)

