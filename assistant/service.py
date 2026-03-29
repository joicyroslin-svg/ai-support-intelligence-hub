from __future__ import annotations

import json
from typing import Any, Dict, List, Optional, Tuple

from assistant.heuristics import (
    classify_category,
    classify_priority,
    classify_sentiment,
    extract_summary,
    parse_priority_response,
    redact_pii,
    suggest_tags,
)
from assistant.llm import LiteLLMClient
from assistant.logging_utils import log_ai_error
from assistant.prompts import (
    build_agent_prompt,
    build_priority_prompt,
    build_reply_prompt,
    build_teardown_prompt,
)
from assistant.rag import rag
from assistant.tools import get_tool_client


def _default_followups(category: str) -> List[str]:
    if category == "Billing":
        return [
            "Which invoice or order number is affected?",
            "What date did the charge occur?",
        ]
    if category == "Bug/Crash":
        return [
            "What exact steps lead to the issue?",
            "Can you share the error screenshot or message text?",
        ]
    return [
        "Can you share the steps you took before the issue appeared?",
        "Is this happening consistently or intermittently?",
    ]


def _default_internal_notes(category: str, priority: str) -> str:
    return f"Route to {category} queue. Priority set to {priority}. Check recent incidents."


def _fallback_reply() -> str:
    return (
        "Thanks for reaching out. We are reviewing this and will share next steps shortly. "
        "If you can share additional details, we can resolve this faster."
    )


def _fallback_result(
    ticket: str,
    include_followups: bool,
    include_internal_notes: bool,
    include_tags: bool,
) -> Dict[str, Any]:
    summary = extract_summary(ticket)
    priority, priority_reason = classify_priority(ticket)
    category = classify_category(ticket)
    sentiment = classify_sentiment(ticket)
    result: Dict[str, Any] = {
        "summary": summary,
        "priority": priority,
        "priority_reason": priority_reason,
        "category": category,
        "sentiment": sentiment,
        "reply": _fallback_reply(),
        "follow_up_questions": [],
        "internal_notes": "",
        "tags": [],
    }
    if include_followups:
        result["follow_up_questions"] = _default_followups(category)
    if include_internal_notes:
        result["internal_notes"] = _default_internal_notes(category, priority)
    if include_tags:
        result["tags"] = suggest_tags(priority, category)
    return result


def _client_generate(client: Any, prompt: str, temperature: float, max_output_tokens: int) -> str:
    """Call generate() for clients using either max_output_tokens or max_tokens."""
    try:
        text = client.generate(
            prompt=prompt,
            temperature=temperature,
            max_output_tokens=max_output_tokens,
        )
    except TypeError:
        text = client.generate(
            prompt=prompt,
            temperature=temperature,
            max_tokens=max_output_tokens,
        )
    return str(text or "")


def analyze_ticket(
    ticket: str,
    client: Optional[Any],
    tone: str,
    language: str,
    include_followups: bool,
    include_internal_notes: bool,
    include_tags: bool,
    temperature: float,
    max_output_tokens: int,
    redact: bool,
) -> Tuple[Dict[str, Any], Dict[str, int], Optional[str]]:
    if redact:
        ticket, redaction_counts = redact_pii(ticket)
    else:
        redaction_counts = {"emails": 0, "phones": 0, "cards": 0}

    if not client:
        return (
            _fallback_result(ticket, include_followups, include_internal_notes, include_tags),
            redaction_counts,
            None,
        )

    try:
        priority_prompt = build_priority_prompt(ticket)
        priority_raw = _client_generate(
            client=client,
            prompt=priority_prompt,
            temperature=temperature,
            max_output_tokens=min(256, max_output_tokens),
        )
        priority, priority_reason = parse_priority_response(priority_raw, ticket)

        reply_prompt = build_reply_prompt(ticket, tone, language)
        reply_raw = _client_generate(
            client=client,
            prompt=reply_prompt,
            temperature=temperature,
            max_output_tokens=max_output_tokens,
        )

        category = classify_category(ticket)
        result: Dict[str, Any] = {
            "summary": extract_summary(ticket),
            "priority": priority,
            "priority_reason": priority_reason,
            "category": category,
            "sentiment": classify_sentiment(ticket),
            "reply": reply_raw.strip() or _fallback_reply(),
            "follow_up_questions": _default_followups(category) if include_followups else [],
            "internal_notes": _default_internal_notes(category, priority) if include_internal_notes else "",
            "tags": suggest_tags(priority, category) if include_tags else [],
        }

        raw_output = (
            "Priority response:\n"
            + (priority_raw or "")
            + "\n\nReply response:\n"
            + (reply_raw or "")
        )
        return result, redaction_counts, raw_output

    except Exception as exc:
        log_ai_error(
            exc,
            context={
                "operation": "analyze_ticket",
                "ticket_preview": ticket[:140],
                "temperature": temperature,
                "max_output_tokens": max_output_tokens,
            },
        )
        return (
            _fallback_result(ticket, include_followups, include_internal_notes, include_tags),
            redaction_counts,
            None,
        )


def analyze_teardown(tool_name: str, focus: str = "overview", model: str = "huggingface/HuggingFaceTB/SmolLM2-1.7B-Instruct") -> Dict[str, Any]:
    tool_client = get_tool_client(tool_name)
    tool_info = tool_client.query(f"Describe your {focus} capabilities.") if tool_client else "No API access."
    prompt = build_teardown_prompt(tool_name, focus, tool_info)
    llm = LiteLLMClient(model=model)

    try:
        raw = llm.generate(prompt=prompt, temperature=0.2, max_output_tokens=900)
        try:
            parsed = json.loads(raw)
        except Exception:
            parsed = {"raw": raw}
        return {"tool": tool_name, "focus": focus, "tool_info": tool_info, "insights": parsed}
    except Exception as exc:
        event = log_ai_error(
            exc,
            context={"operation": "analyze_teardown", "tool": tool_name, "focus": focus, "model": model},
        )
        return {"tool": tool_name, "focus": focus, "tool_info": tool_info, "error": event.summary}


def find_similar(ticket: str, n: int = 5) -> List[Dict[str, Any]]:
    """Find semantically similar tickets using RAG."""
    try:
        from assistant.rag import rag
        similars = rag.query_similar(ticket, n_results=n)
        return similars
    except Exception:
        return []


def bulk_analyze_tickets(
    df: list[dict], model: str = "gemini/gemini-1.5-flash-exp"
) -> list[dict]:
    """Bulk analyze ticket rows and add analysis fields."""

    client = LiteLLMClient(model)
    results: list[dict] = []

    for idx, row in enumerate(df):
        ticket = ""
        try:
            ticket = str(row.get("ticket_text") or row.get("ticket") or "").strip()
            if not ticket:
                results.append({"ticket_id": idx, "ticket": ticket, "error": "No ticket text"})
                continue

            analysis, _, _ = analyze_ticket(
                ticket=ticket,
                client=client,
                tone="professional",
                language="English",
                include_followups=False,
                include_internal_notes=False,
                include_tags=False,
                temperature=0.1,
                max_output_tokens=400,
                redact=True,
            )
            analysis["ticket"] = ticket
            analysis["ticket_id"] = idx
            results.append(analysis)
        except Exception as exc:
            log_ai_error(
                exc,
                context={
                    "operation": "bulk_analyze_tickets",
                    "ticket_id": idx,
                    "ticket_preview": ticket[:140],
                    "model": model,
                },
            )
            results.append({"ticket_id": idx, "ticket": ticket, "error": str(exc)})

    return results


def build_agent_service(
    tools: List[str],
    goal: str,
    model: str = "huggingface/HuggingFaceTB/SmolLM2-1.7B-Instruct",
) -> Dict[str, Any]:
    llm = LiteLLMClient(model=model)
    teardown_rows = [analyze_teardown(tool_name=t, focus="agent", model=model) for t in tools]
    teardown_text = json.dumps(teardown_rows, indent=2)
    prompt = build_agent_prompt(teardown_text, goal)

    try:
        raw = llm.generate(prompt=prompt, temperature=0.1, max_output_tokens=1200)
        try:
            parsed = json.loads(raw)
            config: Dict[str, Any]
            if isinstance(parsed, dict):
                config = parsed
            else:
                config = {"raw_config": raw}
        except Exception:
            config = {"raw_config": raw}
        config["teardowns"] = tools
        config["user_goal"] = goal
        rag.add_ticket(f"Agent build request: {goal}", config)
        return config
    except Exception as exc:
        event = log_ai_error(
            exc,
            context={"operation": "build_agent_service", "model": model, "tools": tools, "goal": goal[:180]},
        )
        return {
            "agent_name": "fallback-agent",
            "tools": tools,
            "system_prompt": "You are a support assistant focused on clear, safe, and helpful responses.",
            "user_goal": goal,
            "error": event.summary,
        }
