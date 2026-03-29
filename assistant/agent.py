from __future__ import annotations

import json
from typing import Any, Dict, List

from assistant.config import DEFAULT_MODEL
from assistant.llm import LiteLLMClient
from assistant.rag import rag
from assistant.service import analyze_ticket


def rag_tool(query: str) -> str:
    """Return short summaries from similar historical tickets."""
    try:
        similar = rag.query_similar(query, 3)
    except Exception:
        similar = []
    if not similar:
        return "No past tickets found."

    rows: List[str] = []
    for item in similar:
        ticket = str(item.get("ticket", ""))
        analysis = item.get("analysis", {})
        if not isinstance(analysis, dict):
            analysis = {}
        priority = str(analysis.get("priority", "N/A"))
        rows.append(f"- {ticket[:90]} | priority={priority}")
    return "\n".join(rows)


def heuristic_tool(ticket: str) -> str:
    result, _, _ = analyze_ticket(
        ticket=ticket,
        client=None,
        tone="professional",
        language="English",
        include_followups=False,
        include_internal_notes=False,
        include_tags=True,
        temperature=0.2,
        max_output_tokens=500,
        redact=True,
    )
    return json.dumps(result)


def run_agent(query: str, model: str = DEFAULT_MODEL) -> Dict[str, Any]:
    """
    Minimal orchestrator retained for backward compatibility.
    Uses the same free-first LLM client as the Streamlit app.
    """

    llm = LiteLLMClient(model=model)
    prompt = (
        "You are a support engineering copilot. "
        "Give concise action items for this request:\n\n"
        f"{query}"
    )

    try:
        answer = llm.generate(
            prompt=prompt,
            temperature=0.2,
            max_output_tokens=400,
        )
    except Exception:
        fallback = (
            "I could not reach the configured model right now. "
            "Please retry, or use the ticket analysis tab for a heuristic fallback."
        )
        return {
            "model": model,
            "response": fallback,
            "tool_calls": [],
            "error": "llm_unavailable",
        }

    return {
        "model": model,
        "response": str(answer or "").strip() or "No response generated.",
        "tool_calls": [],
    }


MODELS = [
    DEFAULT_MODEL,
    "huggingface/mistralai/Mistral-7B-Instruct-v0.3",
    "gemini/gemini-1.5-flash",
]
