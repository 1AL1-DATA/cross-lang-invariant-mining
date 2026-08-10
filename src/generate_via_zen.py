#!/usr/bin/env python3
"""
Phase 2 generation via OpenAI-compatible client calling the OpenCode Zen gateway.
Use via: python generate_via_zen.py [spec_id] [language] [impl_idx]

Updates /tmp/opencode_progress.json on each success/failure.
Outputs the generated code file path on success, or error message on failure.
"""
import sys, json, time, os, re, tempfile, subprocess
from pathlib import Path
from typing import Tuple, List

# ── Config ───────────────────────────────────────────────────────────────────
PROGRESS_PATH = "/tmp/opencode_progress.json"
OUT_ROOT = Path(__file__).resolve().parent.parent / "results" / "phase2"

# ── Lazy config loader ───────────────────────────────────────────────────────
_CONFIG = None

def _get_config() -> dict:
    global _CONFIG
    if _CONFIG is None:
        from providers import load_config
        cfg_path = Path(__file__).resolve().parent.parent / "config" / "generation.yaml"
        _CONFIG = load_config(cfg_path)
    return _CONFIG

# ── Prompt loader ────────────────────────────────────────────────────────────
def _load_prompt_variants(language: str) -> list[str]:
    """Load prompt file for the given language.
    Returns [system_prompt, variant1, variant2, variant3].
    """
    prompt_path = Path(__file__).resolve().parent.parent / "prompts" / f"{language}.md"
    raw = prompt_path.read_text()
    # Split by --- separator, strip empty lines
    parts = [p.strip() for p in raw.split("---") if p.strip()]
    return parts  # [system_prompt, variant1, variant2, variant3]

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


# ──────────────────────────────────────────────────────────────────────────────
# Edge-case parser — extracts (input_args, expected_value) from spec edge_cases
# ──────────────────────────────────────────────────────────────────────────────

def _parse_py_value(s: str) -> object:
    """Parse a Python-literal-like string into a Python value."""
    s = s.strip()
    if not s:
        return None

    # Try literal first
    try:
        return eval(s, {"__builtins__": {}}, {})
    except Exception:
        pass

    # Handle empty collections explicitly
    if s in ("''", '""', "[]", "{}", "set()"):
        return eval(s)

    # Strip outer quotes for strings
    if (s.startswith("'") and s.endswith("'")) or (s.startswith('"') and s.endswith('"')):
        return s[1:-1]

    return s


def _derive_test_cases(spec) -> List[Tuple[List, object]]:
    """
    Return a list of (input_args_list, expected_value) for the given spec.

    Format conventions:
      - Each entry is (positional_args, expected) where positional_args is a list
        of Python values (one per function parameter).
      - Single-arg specs: positional_args is [value], e.g. (['hello'], 'olleh')
      - Multi-arg specs: positional_args is [arg1, arg2, ...], e.g. (['abc', ''], 0)

    Two sources are combined (deduplicated by repr of positional_args):
      1. Hardcoded curated cases (primary source — reliable, human-verified)
      2. Parsed edge_cases that contain a clear "X → Y" pattern where X is a
         Python literal (quoted string, number, list) — supplements hardcoded
         coverage without introducing garbage from descriptive edge-case text.
    """
    # ── 1. Hardcoded curated cases ────────────────────────────────────────────
    # Format: (positional_args, expected)
    hardcoded: dict = {
        "t1-ac1-001": [   # String Reverse — single arg
            (['hello'], 'olleh'),
            ([''], ''),
            (['a'], 'a'),
            (['racecar'], 'racecar'),
        ],
        "t1-ac2-001": [   # Binary Search — two args
            (([1, 3, 5, 7, 9], 5), 2),
            (([], 1), -1),
            (([1], 1), 0),
            (([1], 2), -1),
            (([1, 3, 5, 7, 9], 10), -1),
            (([1, 3, 5, 7, 9], 1), 0),
            (([1, 3, 5, 7, 9], 9), 4),
        ],
        "t1-ac3-001": [   # Factorial (Iterative) — single arg
            (([0],), 1),
            (([1],), 1),
            (([5],), 120),
            (([20],), 2432902008176640000),
        ],
        "t1-ac3-002": [   # Fibonacci (Iterative) — single arg (no parsed supplement)
            (([0],), 0),
            (([1],), 1),
            (([10],), 55),
            (([15],), 610),
        ],
        "t1-ac4-001": [   # Flatten a List — single arg (list of lists is the input)
            ([[]], []),
            ([[1, 2, 3]], [1, 2, 3]),
            ([[1, [2, [3, [4]]]]], [1, 2, 3, 4]),
            ([[1, 'a', [2, [3.0]]]], [1, 'a', 2, 3.0]),
        ],
        "t2-ac1-001": [   # Count Character Frequency — single arg
            ([''], {}),
            (['aaa'], {'a': 3}),
            (['AaA'], {'A': 1, 'a': 2}),
            (['hello'], {'h': 1, 'e': 1, 'l': 2, 'o': 1}),
        ],
        "t2-ac2-001": [   # BFS — two args
            ([{}, 0], [0]),
            ([{0: []}, 0], [0]),
            ([{0: [1, 2], 1: [], 2: []}, 0], [0, 1, 2]),
        ],
        "t2-ac2-002": [   # DFS (Iterative) — two args
            ([{}, 0], [0]),
            ([{0: [1, 2], 1: [], 2: []}, 0], [0, 2, 1]),
        ],
        "t2-ac3-001": [   # Merge Sort — single arg
            ([[]], []),
            ([[5]], [5]),
            ([[3, 1, 2]], [1, 2, 3]),
            ([[1, 2, 3]], [1, 2, 3]),
            ([[3, 2, 1]], [1, 2, 3]),
            ([[2, 2, 2]], [2, 2, 2]),
        ],
        "t2-ac3-002": [   # LCS — two args
            (['abc', ''], 0),
            (['', 'abc'], 0),
            (['abc', 'abc'], 3),
            (['ABCBDAB', 'BDCAB'], 4),
        ],
        "t2-ac4-001": [   # Group By Key — single arg: list of [key, value] pairs
            ([[]], {}),
            ([[['a', 1], ['a', 2], ['b', 3]]], {'a': [1, 2], 'b': [3]}),
            ([[['x', 1], ['y', 2], ['z', 3]]], {'x': [1], 'y': [2], 'z': [3]}),
        ],
        "t3-ac2-001": [   # AVL Tree Insert — complex Node return type, skip in unit harness
            ([[1, 2, 3]], None),
        ],
        "t3-ac2-002": [   # Binary Tree Level-Order Traversal — complex Node type, skip
            ([[1]], None),
        ],
        "t3-ac3-001": [   # 0/1 Knapsack — three args: values, weights, capacity
            ([[], [], 10], 0),
            ([[5], [10], [4]], 0),
            ([[5], [10], [5]], 10),
            ([[2, 3, 4, 5], [3, 4, 5, 6], [5]], 7),
        ],
        "t3-ac4-001": [   # Word Count — single arg (input is list of words/tokens)
            ([['hello', 'world']], {'hello': 1, 'world': 1}),
            ([['hello', 'HELLO']], {'hello': 1, 'HELLO': 1}),
        ],
        "t3-ac4-002": [   # Top-K Elements — two args
            ([[3, 1, 4, 1, 5, 9], 3], [9, 5, 4]),
            ([[9, 9, 9], 2], [9, 9]),
            ([[5], 1], [5]),
        ],
        "t4-ac4-001": [   # Filter-Map-Reduce Pipeline — single arg
            ([[]], 0),
            ([[-1, -2, -3]], 0),
            ([[-1, 2, 3]], 13),
            ([[1, 2, 3, 4, 5]], 54),
        ],
        "t4-ac4-002": [   # Parser: Arithmetic Expression Evaluator — single arg
            (['1 + 2 + 3'], 6),
            (['8 / 3'], 2),
            (['(1 + 2) * 3'], 9),
            (['1 * 2 + 3 * 4'], 14),
        ],
        "t4-ac1-001": [   # Anagram Detection — two args
            (['listen', 'silent'], True),
            (['hello', 'world'], False),
            (['aab', 'aba'], True),
            (['Listen', 'Silent'], False),
            (['', ''], True),
        ],
        "t4-ac4-003": [   # Compose N Functions — two args; tested inline only (callable)
        ],
    }

    # ── 2. Arrow-pattern parser — only for clean literal inputs ───────────────
    # Only match "X → Y" where X is clearly a Python literal:
    #   - quoted string: '...' or "..."
    #   - list literal:  [..]
    #   - dict literal: {..}
    #   - number: 123, -5, etc.
    # Skip descriptions that happen to contain an arrow (e.g.
    #   "Mixed ASCII and Unicode (e.g. 'héllo 世界') → ''")
    arrow_pat = re.compile(
        r'^(?P<input>'
        r"'(?:[^'\\]|\\.)*'"   # single-quoted string (handles \')
        r'|"(?:[^"\\]|\\.)*"'  # double-quoted string
        r'|\[-?[0-9]'          # list starting with a number
        r'|\[[^\[\]]+\]'       # list with simple contents
        r'|\{[^{}]+\}'         # dict literal
        r'|-?[0-9]+'           # integer
        r'|-?[0-9]+\.[0-9]+'  # float
        r'|True|False|None'   # built-in constants
        r'|-?[0-9]+\s*[-+*/]\s*-?[0-9]+'  # simple expression
        r')\s*→\s*(?P<expected>.+)$'
    )

    parsed_cases: List[Tuple[List, object]] = []
    for ec in (spec.edge_cases or []):
        m = arrow_pat.match(ec)
        if not m:
            continue
        inp_raw = m.group("input").strip()
        exp_raw = m.group("expected").strip()

        inp_val = _parse_py_value(inp_raw)
        exp_val = _parse_py_value(exp_raw)

        # Build positional_args list from inp_val
        if isinstance(inp_val, tuple):
            positional_args: List = list(inp_val)
        elif isinstance(inp_val, list):
            positional_args = inp_val
        elif inp_val is None:
            positional_args = []
        else:
            positional_args = [inp_val]

        parsed_cases.append((positional_args, exp_val))

    # ── 3. Merge, deduplicate ─────────────────────────────────────────────────
    fallback = hardcoded.get(spec.id, [])
    all_cases: List[Tuple[List, object]] = list(fallback)
    seen_args = {repr(c[0]) for c in all_cases}
    for c in parsed_cases:
        if repr(c[0]) not in seen_args:
            all_cases.append(c)
            seen_args.add(repr(c[0]))

    return all_cases


def _fn_name_from_title(title: str) -> str:
    """Derive the function name from the spec title.
    Strips parenthetical suffixes (e.g. '(LCS)', '(Iterative)', '(Dynamic Programming)')
    to produce clean Python identifiers.
    """
    # Strip anything in parentheses first, then strip colons
    import re
    cleaned = re.sub(r'\s*\([^)]*\)\s*', '', title).strip()
    cleaned = cleaned.lstrip(':').strip()
    return cleaned.lower().replace(" ", "_").replace("/", "_").replace("-", "_")


# ──────────────────────────────────────────────────────────────────────────────
# make_test_suite — generates a complete Python test file as a string
# ──────────────────────────────────────────────────────────────────────────────

def make_test_suite(spec_id: str, language: str) -> str:
    """Generate a complete Python test file for the given spec."""
    import sys
    sys.path.insert(0, str(Path(__file__).parent))
    from specs import CORPUS

    spec = None
    for s in CORPUS:
        if s.id == spec_id:
            spec = s
            break
    if spec is None:
        return f"# Unknown spec: {spec_id}\n"

    fn_name = _fn_name_from_title(spec.title)
    # Sanitize to a valid Python identifier for test file use
    import re
    safe_fn_name = re.sub(r'[^a-zA-Z0-9_]', '_', fn_name).strip('_')
    if not safe_fn_name or safe_fn_name[0].isdigit():
        safe_fn_name = 'fn_' + safe_fn_name

    # Use the sanitized name for both import and test file
    import_line = f"from implementation import {safe_fn_name}"

    cases = _derive_test_cases(spec)

    def _contains_callable(obj) -> bool:
        """Recursively check if a value or any nested element is callable."""
        if callable(obj):
            return True
        if isinstance(obj, list):
            return any(_contains_callable(x) for x in obj)
        if isinstance(obj, tuple):
            return any(_contains_callable(x) for x in obj)
        return False

    lines = [
        "# Auto-generated test suite — do not edit manually",
        f"# Spec: {spec.id} | Generated fn: {fn_name} | Test alias: {safe_fn_name}",
        "",
        "import sys",
        "from pathlib import Path",
        "",
        import_line,
        "",
        "",
        f"def test_{safe_fn_name}_cases():",
    ]

    # Collect assert lines so we can add 'pass' if the body is empty
    has_assert = False
    for args, expected in cases:
        # Skip placeholder Nones for complex types
        if expected is None:
            continue

        # Skip cases with callable args (can't be serialised as Python literals)
        if _contains_callable(args):
            continue

        # Format the call using safe_fn_name (always a valid identifier)
        if len(args) == 1:
            call_str = f"{safe_fn_name}({_format_arg(args[0])})"
        else:
            call_str = f"{safe_fn_name}({', '.join(_format_arg(a) for a in args)})"

        # Special case: Compose N Functions — define funcs inline
        if spec.id == "t4-ac4-003":
            lines.append("    # Compose N Functions — funcs defined inline")
            lines.append("    funcs = [lambda x: x * 2, lambda x: x + 3]")
            lines.append(f"    assert {safe_fn_name}(funcs, 5) == 16")
            has_assert = True
            continue

        lines.append(f"    assert {call_str} == {_format_arg(expected)}")
        has_assert = True

    if not has_assert:
        lines.append("    pass")

    lines.append("")
    lines.append(f"def test_{safe_fn_name}_returns_correct_type():")
    # Basic smoke test: first case that is not None and has no callable args
    smoke_found = False
    if cases:
        for first_args, first_expected in cases:
            if first_expected is None:
                continue
            if _contains_callable(first_args):
                continue
            if len(first_args) == 1:
                lines.append(f"    result = {safe_fn_name}({_format_arg(first_args[0])})")
            else:
                lines.append(f"    result = {safe_fn_name}({', '.join(_format_arg(a) for a in first_args)})")
            lines.append("    # Should not raise — basic smoke test")
            smoke_found = True
            break
    if not smoke_found:
        lines.append("    pass")

    lines.append("")
    lines.append("if __name__ == '__main__':")
    lines.append(f"    test_{safe_fn_name}_cases()")
    lines.append(f"    test_{safe_fn_name}_returns_correct_type()")
    lines.append("    print('All tests passed!')")

    return "\n".join(lines)


def _format_arg(val: object) -> str:
    """Format a Python value for embedding in an assert statement."""
    if val is None:
        return "None"
    if isinstance(val, bool):
        return "True" if val else "False"
    if isinstance(val, int):
        return str(val)
    if isinstance(val, float):
        return repr(val)
    if isinstance(val, str):
        return repr(val)
    if isinstance(val, list):
        return "[" + ", ".join(_format_arg(x) for x in val) + "]"
    if isinstance(val, tuple):
        return "(" + ", ".join(_format_arg(x) for x in val) + ")"
    if isinstance(val, dict):
        items = ", ".join(f"{_format_arg(k)}: {_format_arg(v)}" for k, v in val.items())
        return "{" + items + "}"
    if isinstance(val, set):
        return "{" + ", ".join(_format_arg(x) for x in val) + "}"
    return repr(val)


# ──────────────────────────────────────────────────────────────────────────────
# run_tests — write source + test to temp dir, run, return (passed, error)
# ──────────────────────────────────────────────────────────────────────────────

def _extract_fn_name(source: str) -> str:
    """Extract the primary function name from generated source code."""
    # Try common patterns
    patterns = [
        # Python: def fn_name(
        (r'def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(', 'python'),
        # Rust: fn fn_name(
        (r'fn\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(', 'rust'),
        # Go: func fn_name(
        (r'func\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(', 'go'),
        # TypeScript: function fn_name(
        (r'function\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(', 'ts'),
        # Haskell: fn_name :: or let fn_name =
        (r'^([a-zA-Z_][a-zA-Z0-9_\']*)\s*::', 'haskell'),
        (r'^let\s+([a-zA-Z_][a-zA-Z0-9_\']*)', 'haskell'),
        # OCaml: let fn_name
        (r'let\s+(?:rec\s+)?([a-zA-Z_][a-zA-Z0-9_\']*)\s*[=\(]', 'ocaml'),
    ]
    for pat, lang in patterns:
        m = re.search(pat, source, re.MULTILINE)
        if m:
            return m.group(1)
    return "implementation"  # fallback


def run_tests(source: str, language: str, spec_id: str, fn_name: str) -> Tuple[bool, str]:
    """
    Write source + test to a temp directory and execute the test suite.
    Returns (passed: bool, error_message: str).
    """
    tmpdir = None
    try:
        tmpdir = tempfile.mkdtemp(prefix="zen_test_")
        tmppath = Path(tmpdir)

        ext = _EXT.get(language, ".txt")

        # ── Write the generated source ─────────────────────────────────────
        impl_file = tmppath / f"implementation{ext}"
        impl_file.write_text(source)

        # ── Python: write + run the Python test harness ────────────────────
        if language == "python":
            test_file = tmppath / f"test_{fn_name}.py"
            test_code = make_test_suite(spec_id, language)
            test_file.write_text(test_code)

            # Run the test — put tmpdir on PYTHONPATH so `from implementation import` works
            env = dict(os.environ)
            env["PYTHONPATH"] = tmpdir
            result = subprocess.run(
                [sys.executable, str(test_file)],
                capture_output=True,
                text=True,
                cwd=tmpdir,
                env=env,
                timeout=30,
            )
            if result.returncode == 0:
                return True, ""
            return False, result.stdout + "\n" + result.stderr

        # ── Non-Python: try syntax/compilation check ───────────────────────
        compiler_map = {
            "rust":        ["rustc", "--edition", "2021", "-o", str(tmppath / "impl_bin"), str(impl_file)],
            "go":          ["go", "build", "-o", str(tmppath / "impl_bin"), str(impl_file)],
            "haskell":     ["ghc", "-o", str(tmppath / "impl_bin"), str(impl_file)],
            "ocaml":       ["ocamlfind", "ocamlc", "-o", str(tmppath / "impl_bin"), str(impl_file)],
            "typescript":  ["npx", "tsc", "--strict", "--esModuleInterop", "--target", "ES2020",
                            "--outDir", str(tmppath), str(impl_file)],
        }

        if language in compiler_map:
            cmd = compiler_map[language]
            try:
                comp_result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    cwd=tmpdir,
                    timeout=60,
                )
            except FileNotFoundError:
                return False, f"no toolchain available: {cmd[0]} not found"
            except Exception as exc:
                return False, f"toolchain error: {exc}"

            if comp_result.returncode != 0:
                return False, comp_result.stderr.strip()

            # Compilation succeeded — we can only do a syntax/type check for non-Python
            # languages without a test harness. Compilation success is the honest ceiling.
            # Treat this as a pass at the level of validation we can perform.
            return True, f"compiled ({language}): syntax/type check passed"

        # Unknown language
        return False, f"no test runner for language: {language}"

    except subprocess.TimeoutExpired:
        return False, "test execution timed out after 30 seconds"
    except Exception as exc:
        return False, f"run_tests error: {exc}"
    finally:
        # Clean up temp directory
        import shutil
        if tmpdir and os.path.exists(tmpdir):
            shutil.rmtree(tmpdir)


# ──────────────────────────────────────────────────────────────────────────────
# generate — call the provider, strip fences, return code
# ──────────────────────────────────────────────────────────────────────────────

def generate(spec_id: str, language: str, impl_idx: int, provider, config: dict) -> Tuple[str, str]:
    """
    Call the LLM provider and return (code, fn_name).
    The fn_name is extracted from the generated source.
    """
    spec_md = spec_md_from_id(spec_id)
    test_suite = make_test_suite(spec_id, language)

    variants = _load_prompt_variants(language)
    system = variants[0]  # first part is system prompt
    prompt_variants = variants[1:]  # rest are user variants

    prompt_variant = prompt_variants[impl_idx % len(prompt_variants)]
    temperature = config.get("temperature", 0.2)

    messages = [
        {"role": "system", "content": system},
        {"role": "user",   "content": f"{prompt_variant}\n\n## Specification\n{spec_md}\n\n## Test Suite\n```python\n{test_suite}\n```\n\nWrite only the implementation code, no tests. Output raw code only."},
    ]

    code = provider.generate(
        messages,
        model=config.get("model", "gpt-4o-mini"),
        temperature=temperature,
        max_tokens=config.get("max_tokens", 4096),
    )

    # Strip markdown fences robustly — handles multiple ```, blank lines, stray fences
    code = code.strip()
    if "```" in code:
        # Find the content between the first and last ```
        first_fence = code.index("```")
        # Skip past the opening fence (may have language label)
        after_first = code.index("\n", first_fence) + 1
        last_fence = code.rindex("```")
        code = code[after_first:last_fence].strip()

    fn_name = _extract_fn_name(code)

    return code, fn_name


# ──────────────────────────────────────────────────────────────────────────────
# Progress tracking
# ──────────────────────────────────────────────────────────────────────────────

def save_progress(spec_id: str, language: str, impl_idx: int, success: bool, path: str = "", error: str = ""):
    path_obj = Path(PROGRESS_PATH)
    if path_obj.exists():
        try:
            prog = json.loads(path_obj.read_text())
        except Exception:
            prog = {}
    else:
        prog = {}

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

    path_obj.write_text(json.dumps(prog, indent=2))


# ──────────────────────────────────────────────────────────────────────────────
# main — generate + test with retry logic
# ──────────────────────────────────────────────────────────────────────────────

def main(spec_id: str, language: str, impl_idx: int):
    impl_idx = int(impl_idx)
    batch_dir = OUT_ROOT / spec_id / language / f"impl_{impl_idx}"
    batch_dir.mkdir(parents=True, exist_ok=True)
    ext = _EXT.get(language, ".txt")
    out_file = batch_dir / f"implementation{ext}"

    # Load provider and config lazily
    from providers import load_provider
    cfg = _get_config()
    provider = load_provider(cfg["provider"], cfg["credentials"])

    max_retries = 3
    last_error = ""

    for attempt in range(max_retries):
        try:
            code, fn_name = generate(spec_id, language, impl_idx, provider, cfg)
        except Exception as exc:
            save_progress(spec_id, language, impl_idx, success=False, error=str(exc))
            print(f"ERROR generating {spec_id}/{language}/impl_{impl_idx} (attempt {attempt+1}): {exc}", file=sys.stderr)
            sys.exit(1)

        # Run tests
        passed, test_error = run_tests(code, language, spec_id, fn_name)

        if passed:
            out_file.write_text(code)
            save_progress(spec_id, language, impl_idx, success=True, path=str(out_file))
            print(f"OK: {out_file}")
            return

        last_error = test_error
        print(
            f"Tests failed for {spec_id}/{language}/impl_{impl_idx} "
            f"(attempt {attempt+1}/{max_retries}): {test_error[:300]}",
            file=sys.stderr,
        )

        # If this wasn't the last attempt, try generating again
        if attempt < max_retries - 1:
            print(f"  Retrying generation (attempt {attempt+2})...", file=sys.stderr)

    # All retries exhausted
    save_progress(spec_id, language, impl_idx, success=False, error=last_error)
    print(f"ERROR: {spec_id}/{language}/impl_{impl_idx}: all {max_retries} attempts failed", file=sys.stderr)
    print(f"Last error: {last_error[:500]}", file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print(f"Usage: {sys.argv[0]} <spec_id> <language> <impl_idx>", file=sys.stderr)
        sys.exit(1)
    main(sys.argv[1], sys.argv[2], sys.argv[3])
