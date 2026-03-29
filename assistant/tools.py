from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

from assistant.config import DEFAULT_MODEL
from assistant.llm import LiteLLMClient


@dataclass(frozen=True)
class ToolProfile:
    name: str
    description: str
    default_query: str


TOOL_PROFILES: Dict[str, ToolProfile] = {
    "chatgpt": ToolProfile(
        name="chatgpt",
        description="General-purpose assistant for drafting and reasoning tasks.",
        default_query="List your best use cases for support operations.",
    ),
    "gemini": ToolProfile(
        name="gemini",
        description="Fast multimodal assistant for support automation and knowledge workflows.",
        default_query="Describe strengths and limits for support ticket triage.",
    ),
    "notion-ai": ToolProfile(
        name="notion-ai",
        description="Knowledge-base and workflow assistant for documentation-heavy support teams.",
        default_query="How can this tool improve support documentation quality?",
    ),
    "figma-ai": ToolProfile(
        name="figma-ai",
        description="Design workflow assistant for UI iteration and prototype handoff.",
        default_query="How can support teams use design tooling for issue communication?",
    ),
    "framer": ToolProfile(
        name="framer",
        description="Website builder with strong prototyping and visual iteration capabilities.",
        default_query="Summarize integration ideas for support landing pages.",
    ),
    "lovable": ToolProfile(
        name="lovable",
        description="Rapid product ideation assistant focused on user-facing experiences.",
        default_query="Explain how this tool helps customer support product experiments.",
    ),
}


class ToolClient:
    """
    Lightweight tool facade.

    It does not require each third-party SDK to be installed,
    so the dashboard remains stable in constrained environments.
    """

    def __init__(self, profile: ToolProfile, model: str = DEFAULT_MODEL) -> None:
        self.profile = profile
        self.model = model

    def _fallback(self, prompt: str) -> str:
        safe_prompt = (prompt or self.profile.default_query).strip()
        return (
            f"Tool: {self.profile.name}. "
            f"Description: {self.profile.description} "
            f"Focus request: {safe_prompt[:160]}"
        )

    def query(self, prompt: str = "") -> str:
        request = (prompt or self.profile.default_query).strip()
        model_prompt = (
            f"You are summarizing '{self.profile.name}' for an AI support agent builder.\n"
            f"Tool description: {self.profile.description}\n"
            f"User request: {request}\n"
            "Respond in 4 short bullets: capabilities, best use case, limitation, integration tip."
        )

        try:
            client = LiteLLMClient(model=self.model)
            response = client.generate(
                prompt=model_prompt,
                temperature=0.2,
                max_output_tokens=280,
            )
            return response.strip() or self._fallback(request)
        except Exception:
            return self._fallback(request)


TOOLS: Dict[str, ToolClient] = {
    name: ToolClient(profile=profile) for name, profile in TOOL_PROFILES.items()
}


def get_tool_client(name: str) -> ToolClient:
    key = name.strip().lower()
    if key in TOOLS:
        return TOOLS[key]
    profile = ToolProfile(
        name=key or "custom-tool",
        description="User-defined tool profile.",
        default_query="Share agent integration guidance.",
    )
    return ToolClient(profile=profile)
