"""
Phase 5: Self-similarity across scale and language.

Tests whether the self-similarity pattern (agreement vs divergence
at different granularity levels) holds uniformly across structurally
distant language pairs, or only across syntactically similar ones.

Produces a language × language similarity matrix.
"""

from __future__ import annotations

import json
import sys
import numpy as np
import pandas as pd
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple
from scipy import stats

# Make sibling modules importable regardless of how this file is invoked
# (e.g. `python -m 2.code.src.self_similarity` from the project root).
_SRC_DIR = Path(__file__).resolve().parent
if str(_SRC_DIR) not in sys.path:
    sys.path.insert(0, str(_SRC_DIR))

from mine_invariants import Invariant, GranularityLevel


@dataclass
class SelfSimilarityProfile:
    language: str
    spec_id: str
    level: GranularityLevel
    agreement_fraction: float  # fraction of implementations sharing the dominant invariant


def compute_self_similarity_profile(
    invariants: List[Invariant],
    n_implementations: int,
    level: GranularityLevel,
    language: str,
    spec_id: str,
) -> SelfSimilarityProfile:
    """
    For a given (spec, language, level) cell, compute the agreement fraction:
    the fraction of implementations sharing the most-common invariant subgraph.
    """
    level_invariants = [i for i in invariants if i.level == level]
    if not level_invariants:
        return SelfSimilarityProfile(language, spec_id, level, 0.0)

    max_support = max(i.support for i in level_invariants)
    return SelfSimilarityProfile(
        language=language,
        spec_id=spec_id,
        level=level,
        agreement_fraction=max_support,
    )


def build_language_similarity_matrix(
    profiles: Dict[str, List[SelfSimilarityProfile]],  # language → profiles
    levels: List[GranularityLevel] = None,
) -> pd.DataFrame:
    """
    Build a language × language matrix where each cell is the KS-test
    statistic between self-similarity distributions.

    Low KS statistic = similar self-similarity patterns.
    """
    if levels is None:
        levels = [GranularityLevel.L4, GranularityLevel.L3, GranularityLevel.L2, GranularityLevel.L1]

    languages = list(profiles.keys())
    n = len(languages)
    matrix = np.zeros((n, n))
    p_matrix = np.ones((n, n))

    for i, lang1 in enumerate(languages):
        for j, lang2 in enumerate(languages):
            if i == j:
                matrix[i, j] = 0.0
                p_matrix[i, j] = 0.0
                continue

            # Collect agreement fractions at matching levels
            lang1_fracs = [p.agreement_fraction for p in profiles[lang1] if p.level in levels]
            lang2_fracs = [p.agreement_fraction for p in profiles[lang2] if p.level in levels]

            if len(lang1_fracs) < 2 or len(lang2_fracs) < 2:
                matrix[i, j] = np.nan
                p_matrix[i, j] = np.nan
                continue

            ks_stat, p_val = stats.ks_2samp(lang1_fracs, lang2_fracs)
            matrix[i, j] = ks_stat
            p_matrix[i, j] = p_val

    df = pd.DataFrame(matrix, index=languages, columns=languages)
    return df


def self_similarity_matrix_to_csv(matrix: pd.DataFrame, output_dir: Path) -> Path:
    """Save the self-similarity matrix as CSV."""
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / "self_similarity_matrix.csv"
    matrix.to_csv(path)
    return path


if __name__ == "__main__":
    # Example: synthetic data to demonstrate the matrix
    levels = [GranularityLevel.L4, GranularityLevel.L3, GranularityLevel.L2]
    profiles = {
        "python": [
            SelfSimilarityProfile("python", "s1", l, np.random.uniform(0.6, 0.9))
            for l in levels for _ in range(5)
        ],
        "typescript": [
            SelfSimilarityProfile("typescript", "s1", l, np.random.uniform(0.6, 0.9))
            for l in levels for _ in range(5)
        ],
        "haskell": [
            SelfSimilarityProfile("haskell", "s1", l, np.random.uniform(0.3, 0.7))
            for l in levels for _ in range(5)
        ],
    }

    matrix = build_language_similarity_matrix(profiles, levels)
    print(matrix.round(3))
    self_similarity_matrix_to_csv(matrix, Path("4.results"))
