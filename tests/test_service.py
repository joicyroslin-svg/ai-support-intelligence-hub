from __future__ import annotations

from typing import Any

import assistant.service as service


class FakeClient:
    def generate(self, prompt: str, temperature: float, max_output_tokens: int) -> str:
        text = prompt.lower()
        if "classify priority" in text:
            return "High: customer cannot login and service is blocked"
        return "Thanks for reaching out. We are on it and will update you shortly."


def test_analyze_ticket_with_client() -> None:
    result, redaction, raw = service.analyze_ticket(
        ticket="Customer cannot login and is blocked from checkout.",
        client=FakeClient(),
        tone="professional",
        language="English",
        include_followups=True,
        include_internal_notes=True,
        include_tags=True,
        temperature=0.2,
        max_output_tokens=500,
        redact=True,
    )

    assert result["priority"] in {"High", "Medium", "Low"}
    assert result["reply"]
    assert isinstance(redaction, dict)
    assert raw is not None


def test_analyze_ticket_without_client_uses_fallback() -> None:
    result, redaction, raw = service.analyze_ticket(
        ticket="Simple request about account settings.",
        client=None,
        tone="professional",
        language="English",
        include_followups=False,
        include_internal_notes=False,
        include_tags=False,
        temperature=0.2,
        max_output_tokens=500,
        redact=False,
    )

    assert result["reply"]
    assert raw is None
    assert redaction == {"emails": 0, "phones": 0, "cards": 0}


def test_build_agent_service_success(monkeypatch: Any) -> None:
    monkeypatch.setattr(
        service,
        "analyze_teardown",
        lambda tool_name, focus="overview", model="": {
            "tool": tool_name,
            "focus": focus,
            "insights": {"ok": True},
        },
    )

    def fake_generate(self: Any, prompt: str, temperature: float = 0.2, max_output_tokens: int = 800) -> str:
        return '{"agent_name":"support-pro","tools":[],"system_prompt":"Assist users clearly.","ui_recommendations":"Use clear sections","user_flow":["intake","analyze","reply"]}'

    monkeypatch.setattr(service.LiteLLMClient, "generate", fake_generate)

    config = service.build_agent_service(
        tools=["chatgpt", "gemini"],
        goal="Create support copilot",
        model="huggingface/HuggingFaceTB/SmolLM2-1.7B-Instruct",
    )

    assert config["agent_name"] == "support-pro"
    assert config["user_goal"] == "Create support copilot"


def test_build_agent_service_fallback_on_error(monkeypatch: Any) -> None:
    def boom(self: Any, prompt: str, temperature: float = 0.2, max_output_tokens: int = 800) -> str:
        raise RuntimeError("provider unavailable")

    monkeypatch.setattr(service.LiteLLMClient, "generate", boom)

    config = service.build_agent_service(
        tools=["chatgpt"],
        goal="Create support copilot",
        model="huggingface/HuggingFaceTB/SmolLM2-1.7B-Instruct",
    )

    assert config["agent_name"] == "fallback-agent"
    assert "error" in config
