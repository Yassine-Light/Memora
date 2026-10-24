"""Prompt construction for memory-aware conversations."""

from collections.abc import Iterable


def build_context_prompt(user_message: str, memories: Iterable[str]) -> str:
    context = "\n".join(f"- {memory}" for memory in memories) or "- No saved memories."
    return (
        "You are MemoryAnchor, a calm and respectful memory assistant.\n"
        "Use the following patient context only when it is relevant:\n"
        f"{context}\n\n"
        f"User message: {user_message}"
    )

