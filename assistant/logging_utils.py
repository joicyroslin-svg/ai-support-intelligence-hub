from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional


LOG_DIR = Path("logs")
LOG_FILE = LOG_DIR / "ai_errors.jsonl"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def summarize_error(error: Exception, context: Optional[Dict[str, Any]] = None) -> str:
    """Short human-friendly error summary for UI/logging."""
    raw = str(error).strip() or error.__class__.__name__
    lowered = raw.lower()
    if "rate limit" in lowered or "429" in lowered:
        reason = "Rate limit from AI provider."
    elif "api key" in lowered or "auth" in lowered or "401" in lowered or "403" in lowered:
        reason = "Authentication issue with AI provider."
    elif "timeout" in lowered:
        reason = "AI request timed out."
    elif "network" in lowered or "connection" in lowered:
        reason = "Network/connectivity issue."
    else:
        reason = "General AI call failure."

    if context and context.get("model"):
        return f"{reason} Model={context['model']} | Details={raw[:220]}"
    return f"{reason} Details={raw[:220]}"


@dataclass
class ErrorEvent:
    timestamp: str
    summary: str
    error_type: str
    details: str
    context: Dict[str, Any]

    def to_json(self) -> str:
        return json.dumps(
            {
                "timestamp": self.timestamp,
                "summary": self.summary,
                "error_type": self.error_type,
                "details": self.details,
                "context": self.context,
            },
            ensure_ascii=True,
        )


def log_ai_error(error: Exception, context: Optional[Dict[str, Any]] = None) -> ErrorEvent:
    """Persist AI error with summary and structured context."""
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    event = ErrorEvent(
        timestamp=_now_iso(),
        summary=summarize_error(error, context=context),
        error_type=error.__class__.__name__,
        details=str(error),
        context=context or {},
    )
    with LOG_FILE.open("a", encoding="utf-8") as handle:
        handle.write(event.to_json() + "\n")
    return event

