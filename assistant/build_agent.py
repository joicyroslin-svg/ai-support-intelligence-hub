from __future__ import annotations

from typing import Any, Dict, List

from assistant.config import DEFAULT_MODEL
from assistant.service import build_agent_service


def build_agent_from_teardowns(
    tools: List[str],
    user_goal: str,
    model: str = DEFAULT_MODEL,
) -> Dict[str, Any]:
    """Compatibility wrapper for previous module users."""
    return build_agent_service(tools=tools, goal=user_goal, model=model)
