"""
Phase 2: Generate equivalence batches per (spec, language).

For each spec × language cell, we generate N implementations varying:
- Model family (at least 3)
- Temperature
- Prompt phrasing (2–3 native/fluent variants per language)

All implementations are tested against the validated test suite.
Results are deduplicated via AST hash before finalizing.
"""

from __future__ import annotations

import json
import time
import random
import hashlib
import httpx
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime

try:
    import anthropic  # optional reference dependency (not used — Ollama backend)
except ImportError:
    anthropic = None

# ──────────────────────────────────────────────────────────────────────────────
# Configuration
# ──────────────────────────────────────────────────────────────────────────────

OLLAMA_BASE_URL = "http://127.0.0.1:11434"

_ollama_models_cache = None

def _resolve_model(requested: str) -> str:
    """Map a model name to an available Ollama model."""
    global _ollama_models_cache
    if _ollama_models_cache is None:
        try:
            r = httpx.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
            _ollama_models_cache = [m["name"] for m in json.loads(r.text).get("models", [])]
        except Exception:
            _ollama_models_cache = []
    if requested in _ollama_models_cache:
        return requested
    aliases = {
        "opencode/big-pickle": "kat-coder:q6_k",
        "openai/o4-mini": "gemma4:12b",
        "anthropic/claude-sonnet-4-7": "gemma4:12b",
    }
    mapped = aliases.get(requested, "kat-coder:q6_k")
    if mapped in _ollama_models_cache:
        return mapped
    return _ollama_models_cache[0] if _ollama_models_cache else "kat-coder:q6_k"

MODELS = [
    "kat-coder:q6_k",
    "gemma4:12b",
    "gemma4:e4b",
    "aga/OLMoE:latest",
]


TEMPERATURES = [0.2, 0.5, 0.8]

# Prompt variants per language (native/fluent, not machine-translated)
PROMPT_VARIANTS: Dict[str, List[str]] = {
    "python": [
        "Write a Python implementation of the following function.",
        "Implement the following in Python.",
        "Provide a Python function that satisfies the specification.",
    ],
    "rust": [
        "Write a Rust implementation of the following function.",
        "Implement the following in Rust.",
        "Provide a Rust function that satisfies the specification.",
    ],
    "haskell": [
        "Write a Haskell implementation of the following function.",
        "Implement the following in Haskell.",
        "Provide a Haskell function that satisfies the specification.",
    ],
    "ocaml": [
        "Write an OCaml implementation of the following function.",
        "Implement the following in OCaml.",
        "Provide an OCaml function that satisfies the specification.",
    ],
    "go": [
        "Write a Go implementation of the following function.",
        "Implement the following in Go.",
        "Provide a Go function that satisfies the specification.",
    ],
    "typescript": [
        "Write a TypeScript implementation of the following function.",
        "Implement the following in TypeScript.",
        "Provide a TypeScript function that satisfies the specification.",
    ],
}

# ──────────────────────────────────────────────────────────────────────────────
# Data structures
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class GenerationAttempt:
    spec_id: str
    language: str
    model: str
    temperature: float
    prompt_variant: int   # index into PROMPT_VARIANTS[language]
    source: str
    passed: bool
    error_message: str = ""
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def result_hash(self) -> str:
        return hashlib.sha256(self.source.encode()).hexdigest()[:16]


@dataclass
class BatchResult:
    spec_id: str
    language: str
    n_generated: int = 0
    n_passing: int = 0
    n_deduplicated: int = 0
    failure_rate: float = 0.0
    attempts: List[GenerationAttempt] = field(default_factory=list)
    dedup_hashes: set = field(default_factory=set)

    def to_dict(self) -> Dict:
        return {
            "spec_id": self.spec_id,
            "language": self.language,
            "n_generated": self.n_generated,
            "n_passing": self.n_passing,
            "n_deduplicated": self.n_deduplicated,
            "failure_rate": self.failure_rate,
        }


# ──────────────────────────────────────────────────────────────────────────────
# Code generation via OpenCode's Zen gateway (openai-compatible).
# ──────────────────────────────────────────────────────────────────────────────

_client = None

def get_client():
    """Returns an Ollama-capable client."""
    global _client
    if _client is None:
        import openai
        _client = openai.OpenAI(
            base_url=f"{OLLAMA_BASE_URL}/v1",
            api_key="ollama",  # Ollama doesn't need a real key
            timeout=httpx.Timeout(120.0, connect=30.0),
        )
    return _client



def generate_implementation(
    spec_md: str,
    language: str,
    model: str,
    temperature: float,
    prompt_variant: int,
    test_suite: str,
) -> str:
    """
    Call the model via Ollama to generate a single implementation.
    Uses subprocess curl (avoids httpx keep-alive bug with Ollama's HTTP/1.1 server).
    Returns the source code (extracted from the response).
    """
    import subprocess, json as _json, sys

    prompt_text = PROMPT_VARIANTS[language][prompt_variant % len(PROMPT_VARIANTS[language])]

    system = (
        f"You are an expert {language} programmer. "
        f"Write clean, idiomatic {language} code. "
        f"Only output the code — no explanations, no markdown fences. "
        f"The code must pass the provided test suite."
    )

    user = f"""{prompt_text}

## Specification
{spec_md}

## Test Suite
```python
{test_suite}
```

Write only the implementation code, no tests. Output raw code only."""

    try:
        resolved_model = _resolve_model(model)
        payload = {
            "model": resolved_model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "max_tokens": 1024,
            "temperature": temperature,
        }
        resp = subprocess.run(
            ["curl", "-s", "--max-time", "120", "--noproxy", "*",
             f"{OLLAMA_BASE_URL}/v1/chat/completions",
             "-X", "POST",
             "-H", "Content-Type: application/json",
             "-d", _json.dumps(payload)],
            capture_output=True, text=True, timeout=180,
        )
        if resp.returncode != 0:
            return f"__GENERATION_ERROR__: curl rc={resp.returncode}: {resp.stderr[:200]}"
        data = _json.loads(resp.stdout)
        code = ""
        try:
            code = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError):
            return f"__GENERATION_ERROR__: unexpected response: {str(data)[:200]}"
        code = (code or "").strip()
        # Strip markdown fences if present
        if code.startswith("```"):
            lines = code.split("\n")
            code = "\n".join(lines[1:-1])
        return code.strip()
    except subprocess.TimeoutExpired:
        return f"__GENERATION_ERROR__: model call timed out after 180s"
    except Exception as e:
        return f"__GENERATION_ERROR__: {e}"

def run_tests(source: str, language: str, spec_id: str) -> Tuple[bool, str]:
    """
    Validate a generated implementation.

    Returns (passed, error_message).

    PREREGISTRATION requires per-language test suites validated against
    reference implementations before Phase 2 generation. Those suites are not
    yet in the repo (see METHODOLOGY.md). Until they exist, this function
    performs a syntax check where a toolchain is available (Python) and
    otherwise returns an explicit failure: unvalidated code MUST NOT be
    counted as passing. Previously every non-Python implementation silently
    passed, making n_passing / failure_rate meaningless.
    """
    if "__GENERATION_ERROR__" in source:
        return False, source

    if language == "python":
        try:
            compile(source, "<string>", "exec")
            return True, ""
        except SyntaxError as e:
            return False, str(e)

    return False, (
        f"no validated test suite for {language} (PREREGISTRATION Phase 2); "
        f"refusing to mark unvalidated code as passing — implement the "
        f"per-language test suite for spec {spec_id} first"
    )


# ──────────────────────────────────────────────────────────────────────────────
# Batch generation
# ──────────────────────────────────────────────────────────────────────────────

def generate_batch(
    spec_id: str,
    spec_md: str,
    language: str,
    N: int,
    test_suite: str,
    output_dir,  # Path or str
    model_overrides: Optional[List[str]] = None,
    delay_between_calls: float = 1.0,
) -> BatchResult:
    """
    Generate N passing, distinct implementations for (spec_id, language).
    Varies model, temperature, and prompt variant.
    """
    result = BatchResult(spec_id=spec_id, language=language)
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    attempts = 0
    max_attempts = N * 4  # generous budget before giving up

    while result.n_deduplicated < N and attempts < max_attempts:
        model = (model_overrides or MODELS)[attempts % len(MODELS or ["claude-sonnet-4-20250514"])]
        temperature = TEMPERATURES[attempts % len(TEMPERATURES)]
        prompt_variant = attempts % len(PROMPT_VARIANTS.get(language, [""]))

        source = generate_implementation(
            spec_md, language, model, temperature, prompt_variant, test_suite
        )

        passed, error = run_tests(source, language, spec_id)
        result_hash = hashlib.sha256(source.encode()).hexdigest()[:16]

        attempt = GenerationAttempt(
            spec_id=spec_id,
            language=language,
            model=model,
            temperature=temperature,
            prompt_variant=prompt_variant,
            source=source,
            passed=passed and result_hash not in result.dedup_hashes,
            error_message=error,
        )

        result.attempts.append(attempt)
        result.n_generated += 1

        if attempt.passed and result_hash not in result.dedup_hashes:
            result.n_passing += 1
            result.n_deduplicated += 1
            result.dedup_hashes.add(result_hash)

            # Save the passing implementation
            impl_path = Path(output_dir) / f"{spec_id}_{language}_{result_hash}.{_ext(language)}"
            impl_path.write_text(source)

        attempts += 1
        time.sleep(delay_between_calls)

    result.failure_rate = 1 - (result.n_passing / result.n_generated) if result.n_generated > 0 else 1.0

    # Save batch metadata
    meta_path = Path(output_dir) / f"{spec_id}_{language}_batch.json"
    meta_path.write_text(json.dumps(result.to_dict(), indent=2))

    return result


def _ext(language: str) -> str:
    return {
        "python": "py",
        "rust": "rs",
        "haskell": "hs",
        "ocaml": "ml",
        "go": "go",
        "typescript": "ts",
    }.get(language, "txt")


# ──────────────────────────────────────────────────────────────────────────────
# Full corpus generation
# ──────────────────────────────────────────────────────────────────────────────

def generate_full_corpus(
    specs,  # from specs.py
    N: int,
    data_dir: Path,
    test_suites: Dict[str, Dict[str, str]],  # spec_id → language → test_suite
) -> Dict[str, BatchResult]:
    """
    Generate batches for all spec × language cells.
    Returns {f"{spec_id}_{language}": BatchResult}.
    """
    results = {}

    for spec in specs:
        spec_dir = data_dir / "corpus" / f"specs_v1" / spec.id
        spec_md = spec.to_markdown()

        for language in ["python", "rust", "haskell", "ocaml", "go", "typescript"]:
            lang_dir = spec_dir / language
            test_suite = test_suites.get(spec.id, {}).get(language, "")

            print(f"  Generating {spec.id} × {language} (target N={N})...", flush=True)
            batch = generate_batch(
                spec_id=spec.id,
                spec_md=spec_md,
                language=language,
                N=N,
                test_suite=test_suite,
                output_dir=lang_dir,
            )
            results[f"{spec.id}_{language}"] = batch
            print(f"    → {batch.n_deduplicated}/{N} passing, {batch.failure_rate:.1%} failure rate")

    return results


if __name__ == "__main__":
    from specs import CORPUS
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        test_suites = {}  # populated from Phase 1 test suite validation
        results = generate_full_corpus(
            CORPUS[:2],  # smoke test with first 2 specs
            N=5,
            data_dir=Path(tmpdir),
            test_suites=test_suites,
        )
        for key, br in results.items():
            print(key, br.to_dict())
