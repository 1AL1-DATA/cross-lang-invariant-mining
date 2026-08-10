"""
Provider-agnostic LLM interface for code generation.

All generation goes through the LLMProvider protocol. Each provider
is a self-contained class that handles its own auth, transport, and
response parsing. Swapping providers requires only a config change —
no code changes.

Usage:
    from providers import load_provider
    from pathlib import Path

    cfg = yaml.safe_load(Path("config/generation.yaml").read_text())
    provider = load_provider(cfg["provider"], cfg["credentials"])

    code = provider.generate(messages=[
        {"role": "system", "content": "You are an expert Rust programmer."},
        {"role": "user",   "content": "Write a function that reverses a string."},
    ], model="gpt-4o-mini", temperature=0.2, max_tokens=2048)
"""

from __future__ import annotations

import os
import json
import subprocess
import tempfile
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Protocol, runtime_checkable

import yaml


# ──────────────────────────────────────────────────────────────────────────────
# Protocol (structural interface)
# ──────────────────────────────────────────────────────────────────────────────

@runtime_checkable
class LLMProvider(Protocol):
    """Structural protocol: any object with a `generate` method satisfies this."""

    def generate(
        self,
        messages: list[dict],
        *,
        model: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> str:
        """Call the LLM and return the text content of the response."""
        ...


# ──────────────────────────────────────────────────────────────────────────────
# OpenAI / OpenAI-compatible (Azure, local LLM gateways, etc.)
# ──────────────────────────────────────────────────────────────────────────────

class OpenAIProvider:
    """
    OpenAI SDK client with OpenAI-compatible base URL support.

    base_url: override for compatible proxies (e.g. local LLM gateway,
              Azure OpenAI endpoint, etc.). If None, uses the official
              OpenAI API.
    """

    def __init__(
        self,
        api_key: str,
        base_url: str | None = None,
        *,
        timeout: int = 120,
    ):
        self.api_key = api_key
        self.base_url = base_url
        self.timeout = timeout
        self._client = None  # lazy

    @property
    def client(self):
        if self._client is None:
            import openai
            kwargs: dict = {"api_key": self.api_key, "timeout": self.timeout}
            if self.base_url:
                kwargs["base_url"] = self.base_url
            self._client = openai.OpenAI(**kwargs)
        return self._client

    def generate(
        self,
        messages: list[dict],
        *,
        model: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> str:
        import openai
        try:
            kwargs: dict = {"model": model}
            if temperature is not None:
                kwargs["temperature"] = temperature
            if max_tokens is not None:
                kwargs["max_tokens"] = max_tokens
            resp = self.client.chat.completions.create(messages=messages, **kwargs)
            return resp.choices[0].message.content or ""
        except openai.APIStatusError as e:
            raise RuntimeError(f"OpenAI API error {e.status_code}: {e.response.text}") from e


# ──────────────────────────────────────────────────────────────────────────────
# Anthropic
# ──────────────────────────────────────────────────────────────────────────────

class AnthropicProvider:
    """
    Anthropic SDK client for Claude models.

    Supports all Anthropic models (claude-opus-4, claude-sonnet-4-7, etc.).
    """

    def __init__(self, api_key: str, *, timeout: int = 120):
        self.api_key = api_key
        self.timeout = timeout
        self._client = None

    @property
    def client(self):
        if self._client is None:
            import anthropic
            self._client = anthropic.Anthropic(
                api_key=self.api_key,
                timeout=self.timeout * 1000,  # Anthropic uses ms
            )
        return self._client

    def generate(
        self,
        messages: list[dict],
        *,
        model: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> str:
        import anthropic
        try:
            # Convert OpenAI-style messages to Anthropic format
            system_parts = []
            anthropic_messages = []
            for msg in messages:
                if msg["role"] == "system":
                    system_parts.append(msg["content"])
                else:
                    anthropic_messages.append({
                        "role": msg["role"],
                        "content": msg["content"],
                    })

            kwargs: dict = {"messages": anthropic_messages}
            if system_parts:
                kwargs["system"] = "\n\n".join(system_parts)
            if model:
                kwargs["model"] = model
            else:
                kwargs["model"] = "claude-sonnet-4-7"
            if temperature is not None:
                kwargs["temperature"] = temperature
            if max_tokens is not None:
                kwargs["max_tokens"] = max_tokens
            else:
                kwargs["max_tokens"] = 4096

            resp = self.client.messages.create(**kwargs)
            return resp.content[0].text
        except anthropic.APIError as e:
            raise RuntimeError(f"Anthropic API error: {e}") from e


# ──────────────────────────────────────────────────────────────────────────────
# Ollama (local)
# ──────────────────────────────────────────────────────────────────────────────

class OllamaProvider:
    """
    Ollama local LLM server.

    base_url: defaults to http://localhost:11434. Supports any Ollama model
              (llama3.3, codellama, qwen2.5-coder, etc.).
    """

    def __init__(self, base_url: str = "http://localhost:11434", *, timeout: int = 300):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._models: list[str] | None = None

    @property
    def models(self) -> list[str]:
        """Cached list of available Ollama models."""
        if self._models is None:
            try:
                import urllib.request
                req = urllib.request.Request(f"{self.base_url}/api/tags")
                with urllib.request.urlopen(req, timeout=10) as r:
                    self._models = [m["name"] for m in json.loads(r.read())["models"]]
            except Exception:
                self._models = []
        return self._models

    def model_alias(self, requested: str | None) -> str:
        """Map a canonical model name to the closest available Ollama model."""
        if requested and requested in self.models:
            return requested
        if self.models:
            return self.models[0]
        return "llama3.3"

    def generate(
        self,
        messages: list[dict],
        *,
        model: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> str:
        import urllib.request, urllib.error

        actual_model = self.model_alias(model)

        # Convert to Ollama chat format
        ollama_messages = []
        for msg in messages:
            if msg["role"] == "system":
                ollama_messages.append({"role": "system", "content": msg["content"]})
            elif msg["role"] == "user":
                ollama_messages.append({"role": "user", "content": msg["content"]})
            elif msg["role"] == "assistant":
                ollama_messages.append({"role": "assistant", "content": msg["content"]})

        payload = {
            "model": actual_model,
            "messages": ollama_messages,
            "stream": False,
        }
        if temperature is not None:
            payload["options"] = {"temperature": temperature}
        if max_tokens is not None:
            payload["options"] = payload.get("options", {})
            payload["options"]["num_predict"] = max_tokens

        req = urllib.request.Request(
            f"{self.base_url}/api/chat",
            data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as r:
                data = json.loads(r.read())
            return data["message"]["content"]
        except urllib.error.HTTPError as e:
            body = e.read().decode()
            raise RuntimeError(f"Ollama HTTP {e.code}: {body}") from e


# ──────────────────────────────────────────────────────────────────────────────
# OpenCode (Zen gateway — used when config.provider == "opencode")
# ──────────────────────────────────────────────────────────────────────────────

class OpenCodeProvider:
    """
    OpenCode Zen gateway — OpenAI-compatible API at https://opencode.ai/zen/go/v1.

    Reads credentials from ~/.local/share/opencode/auth.json by default,
    or from the OPENCODE_API_KEY environment variable.

    base_url: override for self-hosted OpenCode instances.
    """

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str = "https://opencode.ai/zen/go/v1",
        *,
        timeout: int = 120,
    ):
        self.api_key = api_key or self._load_key()
        self.base_url = base_url
        self.timeout = timeout

    @staticmethod
    def _load_key() -> str:
        key_path = os.path.expanduser("~/.local/share/opencode/auth.json")
        try:
            with open(key_path) as f:
                d = json.load(f)
            return d["opencode-go"]["key"]
        except (FileNotFoundError, KeyError) as e:
            raise RuntimeError(
                f"OpenCode API key not found. Set OPENCODE_API_KEY env var or "
                f"populate ~/.local/share/opencode/auth.json → opencode-go.key"
            ) from e

    def generate(
        self,
        messages: list[dict],
        *,
        model: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> str:
        import requests

        actual_model = model or "minimax-m2.5"
        payload: dict = {
            "model": actual_model,
            "messages": messages,
        }
        if temperature is not None:
            payload["temperature"] = temperature
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens

        try:
            resp = requests.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
                timeout=self.timeout,
            )
            resp.raise_for_status()
            data = resp.json()
            content = data["choices"][0]["message"]["content"]
            if content is None:
                raise RuntimeError(f"OpenCode returned content=None. Response: {str(data)[:200]}")
            return content
        except requests.HTTPError as e:
            raise RuntimeError(f"OpenCode HTTP {e.response.status_code}: {e.response.text}") from e


# ──────────────────────────────────────────────────────────────────────────────
# OpenRouter (aggregates many providers behind one API key)
# ──────────────────────────────────────────────────────────────────────────────

class OpenRouterProvider:
    """
    OpenRouter — unified API to 100+ models from different providers.

    api_key: get from https://openrouter.ai
    base_url: https://openrouter.ai/api/v1 (default)
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://openrouter.ai/api/v1",
        *,
        timeout: int = 120,
    ):
        self._delegate = OpenAIProvider(api_key=api_key, base_url=base_url, timeout=timeout)

    def generate(
        self,
        messages: list[dict],
        *,
        model: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> str:
        # OpenRouter requires an explicit model; inject site metadata
        model = model or "anthropic/claude-sonnet-4-7"
        return self._delegate.generate(
            messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
        )


# ──────────────────────────────────────────────────────────────────────────────
# Factory
# ──────────────────────────────────────────────────────────────────────────────

_PROVIDER_CLASSES: dict[str, type] = {
    "openai":     OpenAIProvider,
    "anthropic":  AnthropicProvider,
    "ollama":     OllamaProvider,
    "opencode":   OpenCodeProvider,
    "openrouter": OpenRouterProvider,
}


def load_provider(name: str, credentials: dict) -> LLMProvider:
    """
    Instantiate a provider by name.

    name: one of "openai", "anthropic", "ollama", "opencode", "openrouter"
    credentials: dict with provider-specific keys (see generation.yaml.example)
    """
    if name not in _PROVIDER_CLASSES:
        available = ", ".join(_PROVIDER_CLASSES)
        raise ValueError(f"Unknown provider {name!r}. Available: {available}")

    cls = _PROVIDER_CLASSES[name]

    # Map yaml keys to constructor params
    creds = dict(credentials) if credentials else {}
    kwargs: dict = {}

    if name == "openai":
        kwargs["api_key"] = creds.get("api_key") or os.environ.get("OPENAI_API_KEY", "")
        kwargs["base_url"] = creds.get("base_url") or None

    elif name == "anthropic":
        kwargs["api_key"] = creds.get("api_key") or os.environ.get("ANTHROPIC_API_KEY", "")
        if not kwargs["api_key"]:
            raise RuntimeError("Anthropic provider requires an api_key in credentials, "
                               "or ANTHROPIC_API_KEY env var.")

    elif name == "ollama":
        kwargs["base_url"] = creds.get("base_url", "http://localhost:11434")

    elif name == "opencode":
        kwargs["api_key"] = creds.get("api_key") or os.environ.get("OPENCODE_API_KEY") or None
        kwargs["base_url"] = creds.get("base_url") or "https://opencode.ai/zen/go/v1"

    elif name == "openrouter":
        kwargs["api_key"] = creds.get("api_key") or os.environ.get("OPENROUTER_API_KEY", "")
        kwargs["base_url"] = creds.get("base_url") or "https://openrouter.ai/api/v1"

    return cls(**kwargs)


def load_config(path: str | Path = "config/generation.yaml") -> dict:
    """Load generation config, resolving env-var references."""
    p = Path(path)
    raw = p.read_text()

    # Expand ${ENV_VAR} references. If the var is not set, leave the reference as-is
    # so the loaded config still shows the placeholder.
    import re
    def _expand(m: re.Match) -> str:
        var = m.group(1)
        val = os.environ.get(var, "")
        if not val:
            return m.group(0)  # leave ${UNSET_VAR} in place as a placeholder
        return val

    expanded = re.sub(r'\$\{([^}]+)\}', _expand, raw)
    return yaml.safe_load(expanded)
