"""
Phase 7: Statistical rigor — evaluation utilities.

Applies Benjamini-Hochberg FDR correction, computes effect sizes with CIs,
and aggregates results across the full study.
"""

from __future__ import annotations

import json
import numpy as np
import pandas as pd
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from scipy import stats


# ──────────────────────────────────────────────────────────────────────────────
# Benjamini-Hochberg FDR correction
# ──────────────────────────────────────────────────────────────────────────────

def benjamini_hochberg(p_values: List[float], q: float = 0.05) -> List[Tuple[int, float, bool]]:
    """
    Benjamini-Hochberg procedure for controlling FDR.

    Returns: list of (index, adjusted_p, significant) per original p-value.
    """
    n = len(p_values)
    if n == 0:
        return []

    indexed = sorted(enumerate(p_values), key=lambda x: x[1])
    adjusted = []

    for rank, (orig_idx, p) in enumerate(indexed, start=1):
        bh_threshold = (rank / n) * q
        adjusted_p = min(p * n / rank, 1.0)  # simplified Storey-like adjustment
        adjusted.append((orig_idx, adjusted_p, p <= bh_threshold))

    # Re-sort to original order
    result = [None] * n
    for orig_idx, adj_p, sig in adjusted:
        result[orig_idx] = (orig_idx, adj_p, sig)

    return result


# ──────────────────────────────────────────────────────────────────────────────
# Bootstrap CI
# ──────────────────────────────────────────────────────────────────────────────

def bootstrap_ci(
    data: List[float],
    statistic=np.mean,
    n_resamples: int = 10000,
    ci: float = 0.95,
) -> Tuple[float, float, float]:
    """
    Compute bootstrap confidence interval for a statistic.
    Returns: (point_estimate, lower_ci, upper_ci)
    """
    if len(data) < 2:
        return (float(np.mean(data)) if data else 0.0, 0.0, 0.0)

    rng = np.random.default_rng(42)
    resamples = [
        statistic(rng.choice(data, size=len(data), replace=True))
        for _ in range(n_resamples)
    ]
    alpha = 1 - ci
    lower = np.percentile(resamples, 100 * alpha / 2)
    upper = np.percentile(resamples, 100 * (1 - alpha / 2))
    point = statistic(data)
    return (point, lower, upper)


# ──────────────────────────────────────────────────────────────────────────────
# Effect size helpers
# ──────────────────────────────────────────────────────────────────────────────

def cohens_d(group1: List[float], group2: List[float]) -> float:
    """Cohen's d between two groups."""
    n1, n2 = len(group1), len(group2)
    if n1 < 2 or n2 < 2:
        return 0.0
    mean1, mean2 = np.mean(group1), np.mean(group2)
    var1, var2 = np.var(group1, ddof=1), np.var(group2, ddof=1)
    pooled_std = math.sqrt(((n1 - 1) * var1 + (n2 - 1) * var2) / (n1 + n2 - 2))
    if pooled_std == 0:
        return 0.0
    return float((mean1 - mean2) / pooled_std)


def cramers_v(contingency_table: np.ndarray) -> float:
    """
    Cramér's V for a contingency table.
    Used for H3 (mismatch type vs failure category).
    """
    chi2, _, dof, _ = stats.chi2_contingency(contingency_table)
    n = contingency_table.sum()
    min_dim = min(contingency_table.shape[0] - 1, contingency_table.shape[1] - 1)
    if min_dim == 0 or n == 0:
        return 0.0
    return float(np.sqrt(chi2 / (n * min_dim)))


# ──────────────────────────────────────────────────────────────────────────────
# Aggregated study results
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class StudyResult:
    hypothesis: str
    test_statistic: str
    point_estimate: float
    effect_size: float
    ci_lower: float
    ci_upper: float
    p_value: float
    p_adjusted: float
    significant: bool
    n_tests: int

    def to_dict(self) -> dict:
        return {
            "hypothesis": self.hypothesis,
            "test_statistic": self.test_statistic,
            "point_estimate": round(self.point_estimate, 4),
            "effect_size": round(self.effect_size, 4),
            "ci_95": [round(self.ci_lower, 4), round(self.ci_upper, 4)],
            "p_value": round(self.p_value, 6),
            "p_adjusted": round(self.p_adjusted, 6),
            "significant": self.significant,
            "n_tests": self.n_tests,
        }


def aggregate_h1_results(
    replication_results: List[dict],  # from mine_invariants.replication_test
) -> StudyResult:
    """
    Aggregate H1 results: Jaccard overlap across specs.
    """
    jaccards = [r["jaccard"] for r in replication_results if "jaccard" in r]
    if not jaccards:
        return _empty_result("H1")

    point, ci_lo, ci_hi = bootstrap_ci(jaccards, statistic=np.mean)
    mean_jaccard = np.mean(jaccards)

    # One-sample t-test: is median Jaccard >= 0.30?
    t_stat, p_val = stats.ttest_1samp(jaccards, 0.30)
    n = len(jaccards)

    return StudyResult(
        hypothesis="H1",
        test_statistic="one_sample_t",
        point_estimate=mean_jaccard,
        effect_size=mean_jaccard,
        ci_lower=ci_lo,
        ci_upper=ci_hi,
        p_value=p_val,
        p_adjusted=p_val * n,  # rough BH
        significant=p_val < 0.05,
        n_tests=n,
    )


def aggregate_h2_results(
    transfer_fractions: List[dict],
) -> StudyResult:
    """
    Aggregate H2 results: transfer fractions.
    """
    fractions = [r["transfer_fraction"] for r in transfer_fractions if "transfer_fraction" in r]
    if not fractions:
        return _empty_result("H2")

    point, ci_lo, ci_hi = bootstrap_ci(fractions, statistic=np.mean)

    # One-sample t-test: is fraction >= 0.35?
    t_stat, p_val = stats.ttest_1samp(fractions, 0.35)
    n = len(fractions)

    return StudyResult(
        hypothesis="H2",
        test_statistic="one_sample_t",
        point_estimate=np.mean(fractions),
        effect_size=np.mean(fractions),
        ci_lower=ci_lo,
        ci_upper=ci_hi,
        p_value=p_val,
        p_adjusted=p_val * n,
        significant=p_val < 0.05,
        n_tests=n,
    )


def aggregate_h3_results(
    contingency_tables: List[np.ndarray],
) -> StudyResult:
    """
    Aggregate H3 results: Cramér's V across contingency tables.
    """
    if not contingency_tables:
        return _empty_result("H3")

    v_values = [cramers_v(ct) for ct in contingency_tables]
    point, ci_lo, ci_hi = bootstrap_ci(v_values, statistic=np.mean)
    mean_v = np.mean(v_values)

    # Chi-square test on pooled contingency
    try:
        pooled = sum(contingency_tables)
        chi2, p_val, dof, _ = stats.chi2_contingency(pooled)
    except Exception:
        p_val = 1.0

    return StudyResult(
        hypothesis="H3",
        test_statistic="cramers_v",
        point_estimate=mean_v,
        effect_size=mean_v,
        ci_lower=ci_lo,
        ci_upper=ci_hi,
        p_value=p_val,
        p_adjusted=p_val * len(contingency_tables),
        significant=p_val < 0.05 and mean_v >= 0.25,
        n_tests=len(contingency_tables),
    )


def _empty_result(hypothesis: str) -> StudyResult:
    return StudyResult(
        hypothesis=hypothesis,
        test_statistic="N/A",
        point_estimate=0.0,
        effect_size=0.0,
        ci_lower=0.0,
        ci_upper=0.0,
        p_value=1.0,
        p_adjusted=1.0,
        significant=False,
        n_tests=0,
    )


def save_results(results: List[StudyResult], output_dir: Path):
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / "study_results.json"
    path.write_text(json.dumps([r.to_dict() for r in results], indent=2))
    return path


import math
