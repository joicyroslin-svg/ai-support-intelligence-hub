from __future__ import annotations

from typing import Any, Dict, List

from assistant.config import DEFAULT_MODEL
from assistant.service import analyze_teardown


def teardown_tool(tool_name: str, focus: str = "overview", model: str = DEFAULT_MODEL) -> Dict[str, Any]:
    """Compatibility wrapper around service teardown."""
    return analyze_teardown(tool_name=tool_name, focus=focus, model=model)


def batch_teardown(tools: List[str], focus: str = "overview", model: str = DEFAULT_MODEL) -> List[Dict[str, Any]]:
    return [teardown_tool(tool_name=tool, focus=focus, model=model) for tool in tools]
