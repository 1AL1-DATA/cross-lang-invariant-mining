"""
Phase 0b: Power analysis.

Before deciding sample size N per (spec, language) cell, run a small pilot:
- Positive control spec (binary search), 3 languages (Python, Rust, Haskell), N=10 each
- Estimate variance in the invariant-support statistic
- Compute required N for medium effect size (Cohen's d = 0.5) at alpha = 0.05, power = 0.8
"""

from __future__ import annotations

import json
import math
import sys
import numpy as np
from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple

# Make sibling modules importable regardless of how this file is invoked
# (e.g. `python -m 2.code.src.power_analysis` from the project root).
_SRC_DIR = Path(__file__).resolve().parent
if str(_SRC_DIR) not in sys.path:
    sys.path.insert(0, str(_SRC_DIR))

from parse import ParsedImplementation
from lower import lower_implementation
from mine_invariants import mine_within_language, Invariant, GranularityLevel


# ──────────────────────────────────────────────────────────────────────────────
# Power analysis
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class PowerAnalysisResult:
    pilot_n: int
    pilot_variance: float
    required_n: int
    effect_size: float
    alpha: float
    power: float
    two_tailed: bool

    def to_dict(self) -> dict:
        return {
            "pilot_n": self.pilot_n,
            "pilot_variance": round(self.pilot_variance, 6),
            "required_n": self.required_n,
            "effect_size": self.effect_size,
            "alpha": self.alpha,
            "power": self.power,
            "two_tailed": self.two_tailed,
        }


def compute_required_n(
    variance: float,
    effect_size: float = 0.5,
    alpha: float = 0.05,
    power: float = 0.8,
    two_tailed: bool = True,
) -> int:
    """
    Compute required sample size per group for a two-sample t-test.
    Uses the standard formula.

    effect_size: Cohen's d
    alpha: significance level
    power: 1 - beta
    """
    from scipy import stats

    # Critical z-values
    z_alpha = stats.norm.ppf(1 - alpha / (2 if two_tailed else 1))
    z_beta = stats.norm.ppf(power)

    # Pooled variance assumption: two independent groups of size n each
    # n = 2 * (z_alpha + z_beta)^2 / d^2
    n = 2 * ((z_alpha + z_beta) ** 2) / (effect_size ** 2)
    return math.ceil(n)


def run_pilot(
    pilot_impls: List[ParsedImplementation],
    threshold: int = 70,
) -> float:
    """
    Run the pilot mining on a small batch to estimate variance in
    the invariant-support statistic.

    Returns the estimated variance of the support fraction across specs.
    """
    result = mine_within_language(
        spec_id="pilot",
        language=pilot_impls[0].language if pilot_impls else "python",
        implementations=pilot_impls,
        threshold=threshold,
        levels=[GranularityLevel.L3],
    )

    # Estimate variance in support values
    supports = [inv.support for inv in result.invariants]
    if len(supports) < 2:
        # Fallback: use bootstrap over the batch
        n = len(pilot_impls)
        bootstrap_supports = []
        for _ in range(100):
            sample = np.random.choice(
                [0.0, 1.0], size=n, p=[1 - threshold / 100, threshold / 100]
            )
            bootstrap_supports.append(sample.mean())
        return float(np.var(bootstrap_supports))

    return float(np.var(supports))


def full_power_analysis(
    pilot_data: List[List[ParsedImplementation]],  # per-language pilot batches
    effect_size: float = 0.5,
    alpha: float = 0.05,
    power: float = 0.8,
) -> PowerAnalysisResult:
    """
    Top-level power analysis: takes per-language pilot batches and computes
    the required N per cell.
    """
    # Flatten to estimate pooled variance
    all_impls = [impl for batch in pilot_data for impl in batch]
    variance = run_pilot(all_impls)

    # If variance is 0 (too few invariants), use a conservative estimate
    if variance < 1e-6:
        variance = 0.01  # conservative: assume moderate variance

    required_n = compute_required_n(variance, effect_size, alpha, power)

    return PowerAnalysisResult(
        pilot_n=len(all_impls),
        pilot_variance=variance,
        required_n=required_n,
        effect_size=effect_size,
        alpha=alpha,
        power=power,
        two_tailed=True,
    )


# ──────────────────────────────────────────────────────────────────────────────
# Entry point
# ──────────────────────────────────────────────────────────────────────────────

def main(output_dir: Path = Path("4.results")):
    output_dir.mkdir(parents=True, exist_ok=True)

    # Pilot data should be loaded from 3.data/corpus if already generated
    # For now, document the expected workflow
    result = {
        "note": (
            "Run power_analysis.py after generating the positive-control pilot batch. "
            "This will write the required N to power_analysis.csv. "
            "Until then, this script documents the method."
        ),
        "method": "two-sample t-test, Cohen's d = 0.5, alpha = 0.05, power = 0.8",
        "required_n_placeholder": "TBD — run with real pilot data",
    }

    path = output_dir / "power_analysis.json"
    path.write_text(json.dumps(result, indent=2))
    print(f"Power analysis result: {path}")
    print(json.dumps(result, indent=2))
    return result


if __name__ == "__main__":
    main()
