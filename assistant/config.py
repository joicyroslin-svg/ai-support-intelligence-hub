from __future__ import annotations

import os
import shutil
from pathlib import Path
from typing import Dict, Iterable


_ENV_LOADED = False
ROOT_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = ROOT_DIR / ".env"
ENV_EXAMPLE_PATH = ROOT_DIR / ".env.example"


def ensure_env_file() -> None:
    """Create .env from .env.example when .env is missing."""
    if ENV_PATH.exists() or not ENV_EXAMPLE_PATH.exists():
        return
    shutil.copy2(ENV_EXAMPLE_PATH, ENV_PATH)


def load_dotenv() -> None:
    """Load .env into process environment once."""
    global _ENV_LOADED
    if _ENV_LOADED:
        return

    ensure_env_file()
    if not ENV_PATH.exists():
        _ENV_LOADED = True
        return

    for raw_line in ENV_PATH.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[len("export ") :].strip()
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key:
            os.environ[key] = value

    _ENV_LOADED = True


def env(name: str, default: str = "") -> str:
    """Small helper for typed environment reads."""
    load_dotenv()
    return os.getenv(name, default)


DEFAULT_MODEL = env("DEFAULT_MODEL", "huggingface/HuggingFaceTB/SmolLM2-1.7B-Instruct")


def get_api_key(provider: str = "") -> str | None:
    """Return provider key when present."""
    normalized = provider.strip().lower()
    if normalized in {"huggingface", "hf"}:
        return env("HF_TOKEN") or env("HUGGINGFACEHUB_API_TOKEN") or None
    if normalized in {"gemini", "google"}:
        return env("GEMINI_API_KEY") or env("GOOGLE_API_KEY") or None
    if normalized in {"openai", "chatgpt"}:
        return env("OPENAI_API_KEY") or None
    if normalized:
        key_name = f"{normalized.upper().replace('-', '_')}_API_KEY"
        return env(key_name) or None
    return env("API_KEY") or None


def get_available_models() -> list[str]:
    """
    Multi-LLM model list.
    Uses AVAILABLE_MODELS when provided, otherwise safe defaults.
    """
    configured = env("AVAILABLE_MODELS")
    if configured:
        return [model.strip() for model in configured.split(",") if model.strip()]
    return [
        "huggingface/HuggingFaceTB/SmolLM2-1.7B-Instruct",
        "huggingface/mistralai/Mistral-7B-Instruct-v0.3",
        "gemini/gemini-1.5-flash",
        "openai/gpt-4o-mini",
    ]


def validate_keys(required: Iterable[str] | None = None) -> Dict[str, bool]:
    """Return key availability map for UI and diagnostics."""
    load_dotenv()
    required_keys = list(required) if required is not None else [
        "HF_TOKEN",
        "GEMINI_API_KEY",
        "GOOGLE_API_KEY",
        "OPENAI_API_KEY",
    ]
    return {name: bool(env(name)) for name in required_keys}


def get_tool_keys() -> Dict[str, str | None]:
    """Tool key availability used by agent dashboard."""
    return {
        "openai": get_api_key("openai"),
        "gemini": get_api_key("gemini"),
        "notion": get_api_key("notion"),
        "figma": get_api_key("figma"),
        "framer": get_api_key("framer"),
        "lovable": get_api_key("lovable"),
    }


# Load once on module import.
load_dotenv()

