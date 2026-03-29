from __future__ import annotations

import importlib
from dataclasses import dataclass
from typing import Any, Optional

import requests

from assistant.config import DEFAULT_MODEL, get_api_key
from assistant.logging_utils import log_ai_error


@dataclass
class ModelCallError(Exception):
    """Structured model error for easier logging."""

    message: str
    model: str

    def __str__(self) -> str:
        return f"{self.message} (model={self.model})"


class GeminiClient:
    """Direct Gemini SDK client kept for compatibility."""

    def __init__(self, api_key: str, model_name: str) -> None:
        try:
            genai = importlib.import_module("google.generativeai")
        except ImportError as exc:
            raise ModelCallError("google-generativeai is not installed", model_name) from exc

        configure_fn: Any = getattr(genai, "configure")
        model_cls: Any = getattr(genai, "GenerativeModel")
        configure_fn(api_key=api_key)
        self._model: Any = model_cls(model_name)
        self.model_name = model_name

    def generate(self, prompt: str, temperature: float, max_output_tokens: int) -> str:
        generation_config = {
            "temperature": temperature,
            "max_output_tokens": max_output_tokens,
        }
        response = self._model.generate_content(prompt, generation_config=generation_config)
        return str(getattr(response, "text", "") or "").strip()


class LiteLLMClient:
    """
    Provider-agnostic model client.
    Works with Hugging Face (free token), Gemini, OpenAI, etc via LiteLLM.
    """

    def __init__(self, model: str = DEFAULT_MODEL) -> None:
        self.model = model
        self.hf_api_base = "https://api-inference.huggingface.co/models"

    def _build_kwargs(self, temperature: float, max_output_tokens: int) -> dict[str, Any]:
        kwargs: dict[str, Any] = {
            "model": self.model,
            "temperature": temperature,
            "max_tokens": max_output_tokens,
        }

        # Route free-first Hugging Face auth when model is HF.
        if self.model.startswith("huggingface/"):
            hf_key = get_api_key("hf")
            if hf_key:
                kwargs["api_key"] = hf_key
        elif self.model.startswith("gemini/"):
            gemini_key = get_api_key("gemini")
            if gemini_key:
                kwargs["api_key"] = gemini_key
        elif self.model.startswith("openai/"):
            openai_key = get_api_key("openai")
            if openai_key:
                kwargs["api_key"] = openai_key

        return kwargs

    def _hf_model_id(self) -> str:
        if self.model.startswith("huggingface/"):
            return self.model.split("/", 1)[1]
        return self.model

    def _generate_hf_inference(self, prompt: str, temperature: float, max_output_tokens: int) -> str:
        """
        Hugging Face fallback path that can work even without a paid key.
        Useful when LiteLLM/provider routing is unavailable.
        """
        model_id = self._hf_model_id()
        url = f"{self.hf_api_base}/{model_id}"
        headers = {"Content-Type": "application/json"}
        hf_token = get_api_key("hf")
        if hf_token:
            headers["Authorization"] = f"Bearer {hf_token}"

        payload = {
            "inputs": prompt,
            "parameters": {
                "temperature": temperature,
                "max_new_tokens": max_output_tokens,
                "return_full_text": False,
            },
        }
        response = requests.post(url, json=payload, headers=headers, timeout=35)
        response.raise_for_status()
        body = response.json()

        if isinstance(body, list) and body and isinstance(body[0], dict):
            generated = body[0].get("generated_text", "")
            return str(generated or "").strip()
        if isinstance(body, dict):
            if "generated_text" in body:
                return str(body.get("generated_text", "")).strip()
            # Some endpoints return { "error": "..."}
            if body.get("error"):
                raise ModelCallError(str(body.get("error")), self.model)
        return ""

    def generate(self, prompt: str, temperature: float = 0.2, max_output_tokens: int = 800) -> str:
        try:
            from litellm import completion
        except ImportError as exc:
            if self.model.startswith("huggingface/"):
                try:
                    return self._generate_hf_inference(prompt, temperature, max_output_tokens)
                except Exception as hf_exc:
                    raise ModelCallError(str(hf_exc), self.model) from hf_exc
            error_msg = str(exc)
            try:
                summary_client = LiteLLMClient("huggingface/HuggingFaceTB/SmolLM2-1.7B-Instruct")
                summary = summary_client.generate(f"Brief LLM error summary for devs: {error_msg[:400]}", temperature=0.1, max_output_tokens=120)
                log_ai_error(exc, {"ai_summary": summary, "model": self.model, "type": "litellm_import"})
            except Exception:
                log_ai_error(exc, {"ai_summary": "Summary failed", "model": self.model, "type": "litellm_import"})
            raise ModelCallError("litellm is not installed", self.model) from exc

        kwargs = self._build_kwargs(temperature=temperature, max_output_tokens=max_output_tokens)
        try:
            response_any: Any = completion(messages=[{"role": "user", "content": prompt}], **kwargs)
        except Exception as exc:
            if self.model.startswith("huggingface/"):
                try:
                    return self._generate_hf_inference(prompt, temperature, max_output_tokens)
                except Exception as hf_exc:
                    raise ModelCallError(str(hf_exc), self.model) from hf_exc
            error_msg = str(exc)
            try:
                summary_client = LiteLLMClient("huggingface/HuggingFaceTB/SmolLM2-1.7B-Instruct")
                summary = summary_client.generate(f"Brief LLM error summary for devs: {error_msg[:400]}", temperature=0.1, max_output_tokens=120)
                log_ai_error(exc, {"ai_summary": summary, "model": self.model, "type": "completion_call"})
            except Exception:
                log_ai_error(exc, {"ai_summary": "Summary failed", "model": self.model, "type": "completion_call"})
            raise ModelCallError(str(exc), self.model) from exc

        message = response_any.choices[0].message
        content = getattr(message, "content", "")
        return str(content or "").strip()


def create_gemini_client(api_key: Optional[str], model_name: str) -> Optional[GeminiClient]:
    if not api_key:
        return None
    return GeminiClient(api_key=api_key, model_name=model_name)
