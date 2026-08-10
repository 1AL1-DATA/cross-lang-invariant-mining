"""
Phase 6: Bidirectional hierarchy & mismatch typing.

Tests whether top-down/bottom-up mismatch type (omission vs. drift)
predicts failure category, and whether mismatch type is spec-driven,
language-driven, or an interaction.
"""

from __future__ import annotations

import json
import sys
import numpy as np
import pandas as pd
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from collections import defaultdict

# Make sibling modules importable regardless of how this file is invoked
# (e.g. `python -m 2.code.src.mismatch` from the project root).
_SRC_DIR = Path(__file__).resolve().parent
if str(_SRC_DIR) not in sys.path:
    sys.path.insert(0, str(_SRC_DIR))

from evaluate import cramers_v
from scipy import stats


class MismatchType(str, Enum):
    OMISSION = "omission"    # required component missing from generated code
    DRIFT = "drift"           # component present but structurally different


class FailureCategory(str, Enum):
    FUNCTIONAL = "functional"  # test suite fails (wrong output)
    STYLISTIC = "stylistic"   # tests pass but mismatch flagged


@dataclass
class MismatchRecord:
    spec_id: str
    language: str
    mismatch_type: MismatchType
    failure_category: FailureCategory
    direction: str  # "top-down" or "bottom-up"


@dataclass
class MismatchAnalysisResult:
    spec_id: str
    language: str
    contingency_table: dict  # {omission: {functional: n, stylistic: n}, drift: {...}}
    cramers_v: float
    p_value: float
    fisher_exact_p: float


def classify_mismatch(
    generated_code: str,
    reference_code: str,
    direction: str,
) -> MismatchType:
    """
    Classify a mismatch as omission or drift.

    - OMISSION: required structural component missing from generated code
    - DRIFT: component present but structurally different from reference

    Heuristic: compare the set of AST node types.
    If generated is a strict subset of reference → omission.
    If generated has same node types but different structure → drift.
    """
    # Simple heuristic: check token coverage
    gen_tokens = set(generated_code.split())
    ref_tokens = set(reference_code.split())

    gen_ratio = len(gen_tokens & ref_tokens) / max(len(gen_tokens), 1)
    ref_ratio = len(gen_tokens & ref_tokens) / max(len(ref_tokens), 1)

    if ref_ratio < 0.7 and gen_ratio > ref_ratio:
        return MismatchType.OMISSION
    return MismatchType.DRIFT


def build_contingency_tables(
    records: List[MismatchRecord],
) -> Dict[Tuple[str, str], np.ndarray]:
    """
    Build contingency tables per (spec, language) cell.

    Returns: {(spec_id, language): np.ndarray([[omission_functional, omission_stylistic],
                                               [drift_functional, drift_stylistic]])}
    """
    tables: Dict[Tuple[str, str], Dict[str, Dict[str, int]]] = defaultdict(
        lambda: {
            MismatchType.OMISSION: {FailureCategory.FUNCTIONAL: 0, FailureCategory.STYLISTIC: 0},
            MismatchType.DRIFT: {FailureCategory.FUNCTIONAL: 0, FailureCategory.STYLISTIC: 0},
        }
    )

    for rec in records:
        tables[(rec.spec_id, rec.language)][rec.mismatch_type][rec.failure_category] += 1

    result = {}
    for key, counts in tables.items():
        arr = np.array([
            [counts[MismatchType.OMISSION][FailureCategory.FUNCTIONAL],
             counts[MismatchType.OMISSION][FailureCategory.STYLISTIC]],
            [counts[MismatchType.DRIFT][FailureCategory.FUNCTIONAL],
             counts[MismatchType.DRIFT][FailureCategory.STYLISTIC]],
        ], dtype=int)
        result[key] = arr

    return result


def analyze_mismatch(
    records: List[MismatchRecord],
) -> List[MismatchAnalysisResult]:
    """
    Run the full mismatch analysis: per-cell Fisher's exact test + Cramér's V.
    """
    contingency_tables = build_contingency_tables(records)
    results = []

    for (spec_id, language), table in contingency_tables.items():
        try:
            odds_r, fisher_p = stats.fisher_exact(table)
        except Exception:
            fisher_p = 1.0

        v = cramers_v(table)

        try:
            chi2, p_val, dof, _ = stats.chi2_contingency(table)
        except Exception:
            p_val = 1.0

        results.append(MismatchAnalysisResult(
            spec_id=spec_id,
            language=language,
            contingency_table={
                "omission_functional": int(table[0, 0]),
                "omission_stylistic": int(table[0, 1]),
                "drift_functional": int(table[1, 0]),
                "drift_stylistic": int(table[1, 1]),
            },
            cramers_v=v,
            p_value=p_val,
            fisher_exact_p=fisher_p,
        ))

    return results


def test_factorial_structure(
    records: List[MismatchRecord],
) -> Dict:
    """
    Test whether mismatch type is spec-driven, language-driven, or an interaction.
    Uses a simple chi-square test of independence on the mismatch × driver table.
    """
    # Build: mismatch_type × (spec vs language as driver)
    # Simplified: count per mismatch_type per language
    lang_mismatch: Dict[str, Dict[MismatchType, int]] = defaultdict(
        lambda: {MismatchType.OMISSION: 0, MismatchType.DRIFT: 0}
    )
    spec_mismatch: Dict[str, Dict[MismatchType, int]] = defaultdict(
        lambda: {MismatchType.OMISSION: 0, MismatchType.DRIFT: 0}
    )

    for rec in records:
        lang_mismatch[rec.language][rec.mismatch_type] += 1
        spec_mismatch[rec.spec_id][rec.mismatch_type] += 1

    # Language-driven test
    lang_table = np.array([
        [lang_mismatch[lang].get(MismatchType.OMISSION, 0),
         lang_mismatch[lang].get(MismatchType.DRIFT, 0)]
        for lang in lang_mismatch
    ], dtype=int)

    # Spec-driven test
    spec_table = np.array([
        [spec_mismatch[spec].get(MismatchType.OMISSION, 0),
         spec_mismatch[spec].get(MismatchType.DRIFT, 0)]
        for spec in spec_mismatch
    ], dtype=int)

    results = {}
    if lang_table.size > 0:
        try:
            chi2_lang, p_lang, _, _ = stats.chi2_contingency(lang_table)
            results["language_driven_p"] = float(p_lang)
            results["language_driven_chi2"] = float(chi2_lang)
        except Exception:
            results["language_driven_p"] = 1.0

    if spec_table.size > 0:
        try:
            chi2_spec, p_spec, _, _ = stats.chi2_contingency(spec_table)
            results["spec_driven_p"] = float(p_spec)
            results["spec_driven_chi2"] = float(chi2_spec)
        except Exception:
            results["spec_driven_p"] = 1.0

    return results


def save_mismatch_results(
    results: List[MismatchAnalysisResult],
    factorial: Dict,
    output_dir: Path,
) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / "h3_mismatch.json"
    path.write_text(json.dumps({
        "per_cell_results": [r.__dict__ for r in results],
        "factorial_analysis": factorial,
    }, indent=2))
    return path


if __name__ == "__main__":
    # Smoke test with synthetic data
    records = [
        MismatchRecord("t1-ac2-001", "python", MismatchType.OMISSION, FailureCategory.FUNCTIONAL, "top-down"),
        MismatchRecord("t1-ac2-001", "python", MismatchType.OMISSION, FailureCategory.FUNCTIONAL, "bottom-up"),
        MismatchRecord("t1-ac2-001", "haskell", MismatchType.DRIFT, FailureCategory.STYLISTIC, "top-down"),
    ]
    results = analyze_mismatch(records)
    factorial = test_factorial_structure(records)
    print(f"Per-cell results: {len(results)}")
    print(f"Factorial: {factorial}")
