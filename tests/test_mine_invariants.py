"""Unit tests for mine_invariants.py"""
import pytest
from mine_invariants import (
    Invariant, compute_jaccard, compute_transfer_fraction,
    GranularityLevel,
)


def test_jaccard_identical_sets():
    inv1 = Invariant(
        subgraph_hash="abc123", ir_type="IR", level=GranularityLevel.L3,
        support=0.8, support_count=8, total=10, languages=["python"],
    )
    inv2 = Invariant(
        subgraph_hash="abc123", ir_type="IR", level=GranularityLevel.L3,
        support=0.8, support_count=8, total=10, languages=["python"],
    )
    assert compute_jaccard([inv1], [inv2]) == 1.0


def test_jaccard_disjoint_sets():
    inv1 = Invariant(
        subgraph_hash="abc123", ir_type="IR", level=GranularityLevel.L3,
        support=0.8, support_count=8, total=10, languages=["python"],
    )
    inv2 = Invariant(
        subgraph_hash="def456", ir_type="IR", level=GranularityLevel.L3,
        support=0.8, support_count=8, total=10, languages=["rust"],
    )
    assert compute_jaccard([inv1], [inv2]) == 0.0


def test_jaccard_partial_overlap():
    inv1 = Invariant(
        subgraph_hash="abc123", ir_type="IR", level=GranularityLevel.L3,
        support=0.8, support_count=8, total=10, languages=["python"],
    )
    inv2 = Invariant(
        subgraph_hash="abc123", ir_type="IR", level=GranularityLevel.L3,
        support=0.8, support_count=8, total=10, languages=["python"],
    )
    inv3 = Invariant(
        subgraph_hash="def456", ir_type="IR", level=GranularityLevel.L3,
        support=0.7, support_count=7, total=10, languages=["rust"],
    )
    # set_a={"abc123"}, set_b={"abc123","def456"} -> Jaccard=1/2
    assert compute_jaccard([inv1, inv2], [inv1, inv3]) == pytest.approx(0.5)


def test_jaccard_empty_sets():
    assert compute_jaccard([], []) == 1.0
    assert compute_jaccard([], [Invariant(
        subgraph_hash="abc", ir_type="IR", level=GranularityLevel.L3,
        support=0.8, support_count=8, total=10, languages=["python"],
    )]) == 0.0


def test_transfer_fraction_basic():
    within = {
        "python": [
            Invariant(subgraph_hash="h1", ir_type="IR", level=GranularityLevel.L3,
                      support=0.8, support_count=8, total=10, languages=["python"], spec_id="s1"),
        ],
        "rust": [
            Invariant(subgraph_hash="h1", ir_type="IR", level=GranularityLevel.L3,
                      support=0.7, support_count=7, total=10, languages=["rust"], spec_id="s1"),
        ],
    }
    cross = [
        Invariant(subgraph_hash="h1", ir_type="IR", level=GranularityLevel.L3,
                  support=0.75, support_count=15, total=20,
                  languages=["python", "rust"], spec_id="s1"),
    ]
    result = compute_transfer_fraction(within, cross, structurally_distant=["haskell"])
    assert result["total_within_language_invariants"] == 2
    assert result["transfer_fraction"] > 0


def test_transfer_fraction_zero():
    within = {
        "python": [
            Invariant(subgraph_hash="h1", ir_type="IR", level=GranularityLevel.L3,
                      support=0.8, support_count=8, total=10, languages=["python"], spec_id="s1"),
        ],
    }
    cross = [
        Invariant(subgraph_hash="different_hash", ir_type="IR", level=GranularityLevel.L3,
                  support=0.5, support_count=5, total=10,
                  languages=["rust"], spec_id="s1"),
    ]
    result = compute_transfer_fraction(within, cross)
    assert result["transfer_fraction"] == 0.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
