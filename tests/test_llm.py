from __future__ import annotations

import sys
import types
from typing import Any

import requests

from assistant.llm import LiteLLMClient


class _Message:
    def __init__(self, content: str) -> None:
        self.content = content


class _Choice:
    def __init__(self, content: str) -> None:
        self.message = _Message(content)


class _Response:
    def __init__(self, content: str) -> None:
        self.choices = [_Choice(content)]


def test_generate_with_litellm(monkeypatch: Any) -> None:
    fake_module = types.SimpleNamespace(
        completion=lambda messages, **kwargs: _Response("ok-from-litellm")
    )
    monkeypatch.setitem(sys.modules, "litellm", fake_module)

    client = LiteLLMClient(model="huggingface/test-model")
    text = client.generate("hello")

    assert text == "ok-from-litellm"


def test_generate_uses_hf_fallback_when_litellm_fails(monkeypatch: Any) -> None:
    fake_module = types.SimpleNamespace(
        completion=lambda messages, **kwargs: (_ for _ in ()).throw(RuntimeError("boom"))
    )
    monkeypatch.setitem(sys.modules, "litellm", fake_module)

    client = LiteLLMClient(model="huggingface/test-model")
    monkeypatch.setattr(client, "_generate_hf_inference", lambda *args, **kwargs: "ok-from-hf")

    text = client.generate("hello")
    assert text == "ok-from-hf"


def test_hf_inference_parser(monkeypatch: Any) -> None:
    class FakeResponse:
        def raise_for_status(self) -> None:
            return None

        def json(self) -> Any:
            return [{"generated_text": "hello from hf"}]

    monkeypatch.setattr(requests, "post", lambda *args, **kwargs: FakeResponse())

    client = LiteLLMClient(model="huggingface/HuggingFaceTB/SmolLM2-1.7B-Instruct")
    text = client._generate_hf_inference("hi", 0.2, 30)

    assert text == "hello from hf"
