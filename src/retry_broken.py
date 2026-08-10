#!/usr/bin/env python3.11
"""
Retry all broken quality-check files by re-running generate_via_zen.py.
Run: python3.11 retry_broken.py
"""
import subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SCRIPT = ROOT / "generate_via_zen.py"

# All broken files from quality checks
BROKEN = [
    # QC1: Python syntax errors (3)
    ("t3-ac2-001", "python", 2),
    ("t4-ac4-002", "python", 0),
    ("t4-ac4-002", "python", 2),
    # QC2: Rust no braces/fn (1)
    ("t1-ac4-001", "rust", 0),
    # QC3: TypeScript no export (10)
    ("t1-ac1-001", "typescript", 2),
    ("t1-ac3-001", "typescript", 0),
    ("t1-ac3-001", "typescript", 1),
    ("t1-ac3-001", "typescript", 2),
    ("t3-ac4-002", "typescript", 0),
    ("t3-ac4-002", "typescript", 1),
    ("t3-ac4-002", "typescript", 2),
    ("t4-ac4-001", "typescript", 0),
    ("t4-ac4-001", "typescript", 1),
    ("t4-ac4-001", "typescript", 2),
    # QC5: OCaml too short (3)
    ("t4-ac4-003", "ocaml", 0),
    ("t4-ac4-003", "ocaml", 1),
    ("t4-ac4-003", "ocaml", 2),
    # QC6: Go no package — many files (25)
    ("t1-ac1-001", "go", 0),
    ("t1-ac1-001", "go", 1),
    ("t1-ac2-001", "go", 0),
    ("t1-ac2-001", "go", 1),
    ("t1-ac2-001", "go", 2),
    ("t1-ac3-001", "go", 2),
    ("t1-ac3-002", "go", 0),
    ("t1-ac3-002", "go", 2),
    ("t1-ac4-001", "go", 0),
    ("t1-ac4-001", "go", 2),
    ("t2-ac1-001", "go", 0),
    ("t2-ac2-002", "go", 0),
    ("t2-ac2-002", "go", 1),
    ("t2-ac2-002", "go", 2),
    ("t2-ac3-002", "go", 0),
    ("t2-ac3-002", "go", 1),
    ("t2-ac3-002", "go", 2),
    ("t2-ac4-001", "go", 0),
    ("t3-ac3-001", "go", 0),
    ("t3-ac4-002", "go", 0),
    ("t4-ac1-001", "go", 0),
    ("t4-ac1-001", "go", 1),
    ("t4-ac1-001", "go", 2),
    ("t4-ac4-001", "go", 0),
    ("t4-ac4-001", "go", 1),
    ("t4-ac4-001", "go", 2),
    ("t4-ac4-002", "go", 0),
    ("t4-ac4-002", "go", 1),
    ("t4-ac4-002", "go", 2),
    ("t4-ac4-003", "go", 0),
    ("t4-ac4-003", "go", 1),
    ("t4-ac4-003", "go", 2),
    # QC7: Identical impls (6 — retry the first impl)
    ("t2-ac1-001", "python", 0),
    ("t2-ac1-001", "haskell", 0),
    ("t2-ac1-001", "ocaml", 0),
    ("t2-ac2-002", "python", 0),
    ("t2-ac3-002", "python", 0),
    ("t4-ac4-001", "python", 0),
]

# Deduplicate: if a file appears multiple times, only retry once
seen = set()
unique = []
for spec, lang, impl in BROKEN:
    key = (spec, lang, impl)
    if key not in seen:
        seen.add(key)
        unique.append((spec, lang, impl))

print(f"Retrying {len(unique)} unique broken files...")
print()

results = []
errors = []
for i, (spec, lang, impl) in enumerate(unique):
    task_id = f"{spec}|{lang}|{impl}"
    print(f"[{i+1}/{len(unique)}] {task_id}...", end=" ", flush=True)
    try:
        result = subprocess.run(
            [sys.executable, str(SCRIPT), spec, lang, str(impl)],
            capture_output=True, text=True, timeout=180,
            cwd=str(ROOT),
        )
        if result.returncode == 0 and "OK:" in result.stdout:
            print("OK")
            results.append((spec, lang, impl, "OK"))
        else:
            err = result.stderr or result.stdout
            print(f"FAIL: {err[:100]}")
            errors.append((spec, lang, impl, err[:200]))
    except subprocess.TimeoutExpired:
        print("TIMEOUT")
        errors.append((spec, lang, impl, "TIMEOUT"))
    except Exception as e:
        print(f"ERROR: {e}")
        errors.append((spec, lang, impl, str(e)))

print()
print("=" * 50)
print(f"OK: {len(results)}/{len(unique)}")
print(f"FAIL: {len(errors)}/{len(unique)}")
if errors:
    print("\nFailures:")
    for spec, lang, impl, err in errors:
        print(f"  {spec}/{lang}/impl_{impl}: {err[:150]}")
