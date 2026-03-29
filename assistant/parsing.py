import json
import re
from typing import Any, Dict, Optional


FENCE_RE = re.compile(r"```(?:json)?|```", re.IGNORECASE)


def extract_json(text: str) -> Optional[Dict[str, Any]]:
    """Extract and parse a JSON object from model output."""
    if not text:
        return None
    cleaned = FENCE_RE.sub("", text).strip()
    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start == -1 or end == -1 or end <= start:
        return None
    payload = cleaned[start : end + 1]
    try:
        return json.loads(payload)
    except json.JSONDecodeError:
        return None

