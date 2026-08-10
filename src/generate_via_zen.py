#!/usr/bin/env python3
"""
Phase 2 generation via OpenAI-compatible client calling the OpenCode Zen gateway.
Use via: python generate_via_zen.py [spec_id] [language] [impl_idx]

Updates /tmp/opencode_progress.json on each success/failure.
Outputs the generated code file path on success, or error message on failure.
"""
import sys, json, time, os
from pathlib import Path

# ── Config ───────────────────────────────────────────────────────────────────
ZEN_BASE_URL = "https://opencode.ai/zen/go/v1"
ZEN_KEY_PATH = os.path.expanduser("~/.local/share/opencode/auth.json")
PROGRESS_PATH = "/tmp/opencode_progress.json"
OUT_ROOT = Path(__file__).resolve().parent.parent / "results" / "phase2"

# ── Load key ─────────────────────────────────────────────────────────────────
def load_key():
    with open(ZEN_KEY_PATH) as f:
        d = json.load(f)
    return d["opencode-go"]["key"]

# ── Generation ────────────────────────────────────────────────────────────────
PROMPT_VARIANTS = {
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

_EXT = {
    "python": ".py", "rust": ".rs", "haskell": ".hs",
    "ocaml": ".ml", "go": ".go", "typescript": ".ts"
}

def spec_md_from_id(spec_id: str) -> str:
    """Return a markdown description of the spec."""
    import sys
    sys.path.insert(0, str(Path(__file__).parent))
    from specs import CORPUS
    for s in CORPUS:
        if s.id == spec_id:
            inputs = "\n".join(f"- `{i['name']}` ({i['type']}): {i['description']}" for i in s.inputs)
            outputs = "\n".join(f"- `{o['name']}` ({o['type']}): {o['description']}" for o in s.outputs)
            edges = "\n".join(f"- {e}" for e in (s.edge_cases or []))
            return f"""# {s.title}
{s.description}
## Inputs
{inputs}
## Outputs
{outputs}
## Edge Cases
{edges}"""
    raise ValueError(f"Unknown spec: {spec_id}")


def make_test_suite(spec_id: str, language: str) -> str:
    """Return a simple Python test suite as a string for reference."""
    import sys
    sys.path.insert(0, str(Path(__file__).parent))
    from specs import CORPUS
    for s in CORPUS:
        if s.id == spec_id:
            fn = s.title.lower().replace(" ", "_")
            # Generate test calls from corpus examples
            tests = []
            # Simple stub tests
            tests.append(f"    # {s.description}")
            return f"def test_{fn}():\n    # TODO: add test cases\n    pass"
    return "def test_placeholder():\n    pass"


def generate(spec_id: str, language: str, impl_idx: int) -> str:
    import urllib.request, urllib.error

    key = load_key()
    spec_md = spec_md_from_id(spec_id)
    test_suite = make_test_suite(spec_id, language)
    prompt_variant = impl_idx % len(PROMPT_VARIANTS[language])
    prompt_text = PROMPT_VARIANTS[language][prompt_variant]
    temperature = [0.2, 0.5, 0.8][impl_idx % 3]

    system = (
        f"You are an expert {language} programmer. "
        f"Write clean, idiomatic {language} code. "
        f"Only output the code — no explanations, no markdown fences. "
        f"The code must pass the provided test suite. "
        f"IMPORTANT: Output raw code only, no markdown fences, no comments, no explanatory text."
    )

    user = f"""{prompt_text}

## Specification
{spec_md}

## Test Suite
```python
{test_suite}
```

Write only the implementation code, no tests. Output raw code only."""

    # Use requests (avoids Cloudflare 403 that urllib hits from this server)
    import requests

    resp = requests.post(
        f"{ZEN_BASE_URL}/chat/completions",
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
        },
        json={
            "model": "minimax-m2.5",
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "max_tokens": 4096,
            "temperature": temperature,
        },
        timeout=120,
    )
    resp.raise_for_status()
    data = resp.json()
    code = data["choices"][0]["message"]["content"]
    if code is None:
        raise RuntimeError(f"Model returned no content (content=None). Response: {str(data)[:200]}")

    # Strip markdown fences robustly — handles multiple ```, blank lines, stray fences
    code = code.strip()
    if "```" in code:
        # Find the content between the first and last ```
        first_fence = code.index("```")
        # Skip past the opening fence (may have language label)
        after_first = code.index("\n", first_fence) + 1
        last_fence = code.rindex("```")
        code = code[after_first:last_fence].strip()

    return code


def save_progress(spec_id: str, language: str, impl_idx: int, success: bool, path: str = "", error: str = ""):
    path = Path(PROGRESS_PATH)
    if path.exists():
        try:
            prog = json.loads(path.read_text())
        except Exception:
            prog = {}
    else:
        prog = {}

    # Normalize to expected schema
    prog.setdefault("completed", [])
    prog.setdefault("failed", [])

    key = f"{spec_id}|{language}|{impl_idx}"
    if success:
        if key not in prog["completed"]:
            prog["completed"].append(key)
        if key in prog["failed"]:
            prog["failed"].remove(key)
    else:
        if key not in prog["failed"]:
            prog["failed"].append(key)

    path.write_text(json.dumps(prog, indent=2))


def main(spec_id: str, language: str, impl_idx: int):
    impl_idx = int(impl_idx)
    batch_dir = OUT_ROOT / spec_id / language / f"impl_{impl_idx}"
    batch_dir.mkdir(parents=True, exist_ok=True)
    ext = _EXT.get(language, ".txt")
    out_file = batch_dir / f"implementation{ext}"

    try:
        code = generate(spec_id, language, impl_idx)
        out_file.write_text(code)
        save_progress(spec_id, language, impl_idx, success=True, path=str(out_file))
        print(f"OK: {out_file}")
    except Exception as exc:
        save_progress(spec_id, language, impl_idx, success=False, error=str(exc))
        print(f"ERROR: {spec_id}/{language}/impl_{impl_idx}: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print(f"Usage: {sys.argv[0]} <spec_id> <language> <impl_idx>", file=sys.stderr)
        sys.exit(1)
    main(sys.argv[1], sys.argv[2], sys.argv[3])
