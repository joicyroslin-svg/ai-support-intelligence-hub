import re
from typing import Dict, List, Tuple


EMAIL_RE = re.compile(r"\b[\w\.-]+@[\w\.-]+\.\w+\b", re.IGNORECASE)
PHONE_RE = re.compile(r"\b(?:\+?\d{1,3}[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?){1}\d{3}[-.\s]?\d{4}\b")
CARD_RE = re.compile(r"\b(?:\d[ -]*?){13,19}\b")
PRIORITY_RE = re.compile(r"\b(high|medium|low)\b", re.IGNORECASE)


def redact_pii(text: str) -> Tuple[str, Dict[str, int]]:
    """Redact common PII like emails, phone numbers, and card-like numbers."""
    counts = {"emails": 0, "phones": 0, "cards": 0}

    def _sub_email(match: re.Match) -> str:
        counts["emails"] += 1
        return "[REDACTED_EMAIL]"

    def _sub_phone(match: re.Match) -> str:
        counts["phones"] += 1
        return "[REDACTED_PHONE]"

    def _sub_card(match: re.Match) -> str:
        counts["cards"] += 1
        return "[REDACTED_CARD]"

    redacted = EMAIL_RE.sub(_sub_email, text)
    redacted = PHONE_RE.sub(_sub_phone, redacted)
    redacted = CARD_RE.sub(_sub_card, redacted)
    return redacted, counts


def extract_summary(ticket: str, max_words: int = 24) -> str:
    words = ticket.strip().split()
    if not words:
        return ""
    summary_words = words[:max_words]
    summary = " ".join(summary_words).strip()
    if len(words) > max_words:
        summary += "..."
    return summary


def classify_priority(ticket: str) -> Tuple[str, str]:
    text = ticket.lower()
    high_keywords = [
        "urgent",
        "asap",
        "immediately",
        "outage",
        "down",
        "breach",
        "security",
        "data loss",
        "cannot login",
        "can't login",
        "payment failed",
        "refund",
        "charged twice",
        "access denied",
    ]
    medium_keywords = [
        "slow",
        "error",
        "bug",
        "crash",
        "not working",
        "issue",
        "problem",
        "failed",
    ]

    for kw in high_keywords:
        if kw in text:
            return "High", f"Detected urgent keyword: '{kw}'."

    for kw in medium_keywords:
        if kw in text:
            return "Medium", f"Detected service-impact keyword: '{kw}'."

    return "Low", "No urgent or service-impact keywords detected."


def parse_priority_response(text: str, ticket: str) -> Tuple[str, str]:
    """Extract priority from model output; fall back to heuristic classification."""
    if text:
        match = PRIORITY_RE.search(text)
        if match:
            priority = match.group(1).capitalize()
            return priority, text.strip()
    return classify_priority(ticket)


def classify_category(ticket: str) -> str:
    text = ticket.lower()
    if any(kw in text for kw in ["invoice", "billing", "charged", "refund", "payment"]):
        return "Billing"
    if any(kw in text for kw in ["login", "password", "access", "sign in", "2fa"]):
        return "Login/Access"
    if any(kw in text for kw in ["bug", "error", "crash", "stack trace", "exception"]):
        return "Bug/Crash"
    if any(kw in text for kw in ["feature", "request", "enhancement", "add"]):
        return "Feature Request"
    if any(kw in text for kw in ["account", "profile", "email change", "delete account"]):
        return "Account"
    if any(kw in text for kw in ["shipping", "delivery", "tracking", "order"]):
        return "Shipping"
    return "General"


def classify_sentiment(ticket: str) -> str:
    text = ticket.lower()
    if any(kw in text for kw in ["angry", "frustrated", "upset", "unacceptable", "terrible", "disappointed"]):
        return "Negative"
    if any(kw in text for kw in ["love", "great", "thanks", "appreciate", "awesome"]):
        return "Positive"
    return "Neutral"


def suggest_tags(priority: str, category: str) -> List[str]:
    tags = {priority.lower(), category.lower().replace("/", "-")}
    return sorted(tags)
