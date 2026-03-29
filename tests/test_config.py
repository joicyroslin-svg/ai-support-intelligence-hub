from __future__ import annotations

from assistant.config import get_available_models, validate_keys


def test_get_available_models_from_env(monkeypatch) -> None:
    monkeypatch.setenv("AVAILABLE_MODELS", "huggingface/a, openai/b")
    models = get_available_models()
    assert models == ["huggingface/a", "openai/b"]


def test_validate_keys(monkeypatch) -> None:
    monkeypatch.setenv("HF_TOKEN", "test-token")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    status = validate_keys(required=["HF_TOKEN", "OPENAI_API_KEY"])

    assert status["HF_TOKEN"] is True
    assert status["OPENAI_API_KEY"] is False
