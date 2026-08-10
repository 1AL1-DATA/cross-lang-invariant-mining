"""Unit tests for mismatch.py"""
import pytest
import numpy as np
from mismatch import (
    MismatchType, FailureCategory, MismatchRecord,
    build_contingency_tables, analyze_mismatch, test_factorial_structure,
)


def test_classify_omission_heuristic():
    """Omission: generated is a strict subset of reference."""
    from mismatch import classify_mismatch
    ref = "a b c d e f"
    gen = "a b c"  # subset
    result = classify_mismatch(gen, ref, "top-down")
    assert result == MismatchType.OMISSION


def test_classify_drift_heuristic():
    """Drift: generated has different tokens but not a strict subset."""
    from mismatch import classify_mismatch
    ref = "a b c"
    gen = "x y z"
    result = classify_mismatch(gen, ref, "top-down")
    assert result == MismatchType.DRIFT


def test_build_contingency_table():
    records = [
        MismatchRecord("s1", "python", MismatchType.OMISSION, FailureCategory.FUNCTIONAL, "top-down"),
        MismatchRecord("s1", "python", MismatchType.OMISSION, FailureCategory.FUNCTIONAL, "top-down"),
        MismatchRecord("s1", "python", MismatchType.DRIFT, FailureCategory.STYLISTIC, "top-down"),
    ]
    tables = build_contingency_tables(records)
    key = ("s1", "python")
    assert key in tables
    assert tables[key][0, 0] == 2  # omission, functional
    assert tables[key][1, 1] == 1  # drift, stylistic


def test_analyze_mismatch_runs():
    records = [
        MismatchRecord("s1", "python", MismatchType.OMISSION, FailureCategory.FUNCTIONAL, "top-down"),
        MismatchRecord("s1", "python", MismatchType.DRIFT, FailureCategory.STYLISTIC, "top-down"),
    ]
    results = analyze_mismatch(records)
    assert len(results) == 1
    assert results[0].cramers_v >= 0.0


def test_factorial_structure():
    records = [
        MismatchRecord("s1", "python", MismatchType.OMISSION, FailureCategory.FUNCTIONAL, "top-down"),
        MismatchRecord("s2", "python", MismatchType.OMISSION, FailureCategory.FUNCTIONAL, "top-down"),
        MismatchRecord("s1", "haskell", MismatchType.DRIFT, FailureCategory.STYLISTIC, "top-down"),
    ]
    import mismatch as mm_module
    result = mm_module.test_factorial_structure(records)
    assert "language_driven_p" in result or "spec_driven_p" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
