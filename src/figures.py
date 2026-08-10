"""
Phase 8: Figure generation.

Generates the 8 standard figures for the research project.
Run with: python -m 2.code.src.figures
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap

# ──────────────────────────────────────────────────────────────────────────────
# Paths
# ──────────────────────────────────────────────────────────────────────────────

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
RESULTS_DIR = PROJECT_ROOT / "4.results"
DATA_DIR = PROJECT_ROOT / "3.data"
FIGURES_DIR = PROJECT_ROOT / "5.figures"
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────

def load_json(name: str) -> dict:
    path = RESULTS_DIR / name
    if path.exists():
        return json.loads(path.read_text())
    return {}


def load_csv(name: str, **kwargs) -> pd.DataFrame:
    path = RESULTS_DIR / name
    if path.exists():
        return pd.read_csv(path, **kwargs)
    return pd.DataFrame()


COLORBLIND_PALETTE = [
    "#0173b2", "#de8f05", "#029e73", "#cc78bc", "#ca9161", "#949494",
    "#ece133", "#56b4e9", "#d55e00", "#0072b2",
]


def base_style(ax):
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", alpha=0.3, linestyle="--")
    ax.set_axisbelow(True)


# ──────────────────────────────────────────────────────────────────────────────
# Figures

def fig_h1_replication():
    """
    Figure 1: H1 Replication — Jaccard overlap between primary and replication batches.
    Bar chart, one bar per (spec, threshold) cell.
    """
    df = load_csv("h1_replication.csv")
    if df.empty:
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.text(0.5, 0.5, "No H1 replication data yet.\nRun Phase 4 with primary + replication batches.",
                ha="center", va="center", transform=ax.transAxes, fontsize=14)
        ax.axis("off")
        plt.tight_layout()
        plt.savefig(FIGURES_DIR / "h1_replication.png", dpi=300, bbox_inches="tight")
        return

    fig, ax = plt.subplots(figsize=(12, 6))
    thresholds = sorted(df["threshold"].unique())
    x = np.arange(len(df))
    width = 0.25

    for i, t in enumerate(thresholds):
        subset = df[df["threshold"] == t]
        bars = ax.bar(x + i * width, subset["jaccard"], width,
                      color=COLORBLIND_PALETTE[i % len(COLORBLIND_PALETTE)],
                      label=f"T{int(t)}")
        # Add threshold line
        ax.axhline(y=0.30, color="gray", linestyle="--", alpha=0.7, label="H1 threshold (0.30)")

    ax.set_xlabel("Spec × Language cell")
    ax.set_ylabel("Jaccard overlap")
    ax.set_title("H1: Within-language invariant replication\n(primary vs replication batch)")
    ax.set_xticks(x + width)
    ax.set_xticklabels(df["spec_id"], rotation=45, ha="right", fontsize=8)
    ax.legend()
    base_style(ax)
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "h1_replication.png", dpi=300, bbox_inches="tight")
    plt.close()
    print(f"  → h1_replication.png")


def fig_h2_transfer_heatmap():
    """
    Figure 2: H2 Transfer fraction heatmap — spec × language.
    """
    df = load_csv("h2_transfer.csv")
    if df.empty:
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.text(0.5, 0.5, "No H2 transfer data yet.\nRun Phase 4 cross-language mining.",
                ha="center", va="center", transform=ax.transAxes, fontsize=14)
        ax.axis("off")
        plt.tight_layout()
        plt.savefig(FIGURES_DIR / "h2_transfer_heatmap.png", dpi=300, bbox_inches="tight")
        return

    pivot = df.pivot_table(values="transfer_fraction", index="spec_id", columns="language", aggfunc="mean")
    fig, ax = plt.subplots(figsize=(12, max(4, len(pivot) * 0.5)))

    cmap = LinearSegmentedColormap.from_list("rwg", ["#d73027", "#fee08b", "#1a9850"])
    im = ax.imshow(pivot.values, cmap=cmap, vmin=0, vmax=1, aspect="auto")

    ax.set_xticks(range(len(pivot.columns)))
    ax.set_xticklabels(pivot.columns, rotation=45, ha="right")
    ax.set_yticks(range(len(pivot.index)))
    ax.set_yticklabels(pivot.index, fontsize=9)
    ax.set_title("H2: Cross-language transfer fraction by spec × language\n(fraction of within-language invariants with cross-language counterpart)")

    plt.colorbar(im, ax=ax, label="Transfer fraction")
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "h2_transfer_heatmap.png", dpi=300, bbox_inches="tight")
    plt.close()
    print(f"  → h2_transfer_heatmap.png")


def fig_h3_mismatch_matrix():
    """
    Figure 3: H3 Mismatch matrix — omission vs drift × functional vs stylistic.
    Grouped bar chart per language.
    """
    data = load_json("h3_mismatch.json")
    if not data or "per_cell_results" not in data:
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.text(0.5, 0.5, "No H3 mismatch data yet.\nRun Phase 6.",
                ha="center", va="center", transform=ax.transAxes, fontsize=14)
        ax.axis("off")
        plt.tight_layout()
        plt.savefig(FIGURES_DIR / "h3_mismatch_matrix.png", dpi=300, bbox_inches="tight")
        return

    results = data["per_cell_results"]
    languages = sorted(set(r["language"] for r in results))
    categories = ["omission_functional", "omission_stylistic", "drift_functional", "drift_stylistic"]

    fig, ax = plt.subplots(figsize=(12, 6))
    x = np.arange(len(languages))
    width = 0.2

    colors = ["#0173b2", "#56b4e9", "#de8f05", "#fee08b"]
    for i, cat in enumerate(categories):
        values = []
        for lang in languages:
            cell = next((r for r in results if r["language"] == lang), {})
            values.append(cell.get(cat, 0))
        ax.bar(x + i * width, values, width, label=cat.replace("_", " ").title(),
               color=colors[i])

    ax.set_xlabel("Language")
    ax.set_ylabel("Count")
    ax.set_title("H3: Mismatch type × failure category by language")
    ax.set_xticks(x + 1.5 * width)
    ax.set_xticklabels(languages)
    ax.legend(loc="upper right")
    base_style(ax)
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "h3_mismatch_matrix.png", dpi=300, bbox_inches="tight")
    plt.close()
    print(f"  → h3_mismatch_matrix.png")


def fig_self_similarity_matrix():
    """
    Figure 4: Self-similarity KS-statistic matrix (language × language).
    Low values = similar self-similarity patterns.
    """
    df = load_csv("self_similarity_matrix.csv", index_col=0)
    if df.empty:
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.text(0.5, 0.5, "No self-similarity data yet.\nRun Phase 5.",
                ha="center", va="center", transform=ax.transAxes, fontsize=14)
        ax.axis("off")
        plt.tight_layout()
        plt.savefig(FIGURES_DIR / "self_similarity_matrix.png", dpi=300, bbox_inches="tight")
        return

    fig, ax = plt.subplots(figsize=(8, 6))
    cmap = LinearSegmentedColormap.from_list("bwr", ["#2166ac", "#f7f7f7", "#b2182b"])
    im = ax.imshow(df.values.astype(float), cmap=cmap, vmin=0, vmax=1, aspect="auto")

    ax.set_xticks(range(len(df.columns)))
    ax.set_xticklabels(df.columns, rotation=45, ha="right")
    ax.set_yticks(range(len(df.index)))
    ax.set_yticklabels(df.index)

    # Annotate cells
    for i in range(len(df.index)):
        for j in range(len(df.columns)):
            val = df.values[i, j]
            if not np.isnan(val):
                ax.text(j, i, f"{val:.2f}", ha="center", va="center",
                        fontsize=10, color="black" if 0.2 < val < 0.8 else "white")

    ax.set_title("Self-similarity pattern concordance (KS statistic)\nLower = more similar patterns")
    plt.colorbar(im, ax=ax, label="KS statistic")
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "self_similarity_matrix.png", dpi=300, bbox_inches="tight")
    plt.close()
    print(f"  → self_similarity_matrix.png")


def fig_failure_rates():
    """
    Figure 5: Failure rates per (spec, language) cell.
    Heatmap.
    """
    data = load_json("phase3_stats.json")
    if not data:
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.text(0.5, 0.5, "No failure rate data yet.\nRun Phase 2 first.",
                ha="center", va="center", transform=ax.transAxes, fontsize=14)
        ax.axis("off")
        plt.tight_layout()
        plt.savefig(FIGURES_DIR / "failure_rates.png", dpi=300, bbox_inches="tight")
        return

    # Build from generation batches (they live under 3.data, not 4.results)
    batches = (
        list(RESULTS_DIR.glob("**/*_batch.json")) +
        list(DATA_DIR.glob("**/*_batch.json"))
    )
    if not batches:
        return

    records = []
    for b in batches:
        d = json.loads(b.read_text())
        records.append({
            "spec_id": d["spec_id"],
            "language": d["language"],
            "failure_rate": d.get("failure_rate", 0.0),
        })

    df = pd.DataFrame(records)
    if df.empty:
        return

    pivot = df.pivot_table(values="failure_rate", index="spec_id", columns="language", aggfunc="mean")
    fig, ax = plt.subplots(figsize=(12, max(4, len(pivot) * 0.5)))
    cmap = LinearSegmentedColormap.from_list("rwg", ["#1a9850", "#fee08b", "#d73027"])
    im = ax.imshow(pivot.values, cmap=cmap, vmin=0, vmax=1, aspect="auto")

    ax.set_xticks(range(len(pivot.columns)))
    ax.set_xticklabels(pivot.columns, rotation=45, ha="right")
    ax.set_yticks(range(len(pivot.index)))
    ax.set_yticklabels(pivot.index, fontsize=9)
    ax.set_title("Failure rate by spec × language cell\n(darker red = higher failure)")

    plt.colorbar(im, ax=ax, label="Failure rate")
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "failure_rates.png", dpi=300, bbox_inches="tight")
    plt.close()
    print(f"  → failure_rates.png")


def fig_positive_control():
    """
    Figure 6: Positive control — binary search invariant support by language.
    """
    mining_dir = RESULTS_DIR / "mining"
    if not mining_dir.exists():
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.text(0.5, 0.5, "No positive control data yet.\nRun Phase 4.",
                ha="center", va="center", transform=ax.transAxes, fontsize=14)
        ax.axis("off")
        plt.tight_layout()
        plt.savefig(FIGURES_DIR / "positive_control.png", dpi=300, bbox_inches="tight")
        return

    # Find binary search results
    bs_files = list(mining_dir.glob("mining_t1-ac2-001_*_crosslang_*.json"))
    if not bs_files:
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.text(0.5, 0.5, "Binary search results not found.\nRun Phase 4 with t1-ac2-001.",
                ha="center", va="center", transform=ax.transAxes, fontsize=14)
        ax.axis("off")
        plt.tight_layout()
        plt.savefig(FIGURES_DIR / "positive_control.png", dpi=300, bbox_inches="tight")
        return

    fig, ax = plt.subplots(figsize=(10, 5))
    thresholds = ["T60", "T70", "T80"]
    for i, thresh in enumerate([60, 70, 80]):
        data = load_json(f"mining_t1-ac2-001_crosslang_t{thresh}.json")
        if not data:
            continue
        langs = {}
        for inv in data.get("invariants", []):
            for lang in inv.get("languages", []):
                langs.setdefault(lang, []).append(inv["support"])
        langs_means = {lang: max(supports) for lang, supports in langs.items()}

        ax.bar([x + i * 0.25 for x in range(len(langs_means))],
               list(langs_means.values()),
               0.25, label=thresholds[i], color=COLORBLIND_PALETTE[i])

    ax.set_xlabel("Language")
    ax.set_ylabel("Max invariant support")
    ax.set_title("Positive control: Binary search invariant support\n(by language, per threshold)")
    ax.set_xticks(range(len(langs_means)))
    ax.set_xticklabels(list(langs_means.keys()))
    ax.axhline(y=0.80, color="gray", linestyle="--", alpha=0.7, label="Expected T80 ≥ 0.80")
    ax.legend()
    base_style(ax)
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "positive_control.png", dpi=300, bbox_inches="tight")
    plt.close()
    print(f"  → positive_control.png")


def fig_negative_control():
    """
    Figure 7: Negative control — shuffled-spec transfer fraction.
    Bar chart comparing real vs shuffled.
    """
    neg_data = load_json("mining/negative_control.json")
    if not neg_data:
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.text(0.5, 0.5, "No negative control data yet.\nRun Phase 4.",
                ha="center", va="center", transform=ax.transAxes, fontsize=14)
        ax.axis("off")
        plt.tight_layout()
        plt.savefig(FIGURES_DIR / "negative_control.png", dpi=300, bbox_inches="tight")
        return

    real_max = neg_data.get("max_support", 0)
    passes = neg_data.get("passes_negative_control", False)

    fig, ax = plt.subplots(figsize=(6, 5))
    bars = ax.bar(["Shuffled\n(negative control)"], [real_max],
                  color="#d55e00" if not passes else "#029e73")
    ax.axhline(y=0.10, color="gray", linestyle="--", alpha=0.7, label="Threshold (0.10)")
    ax.set_ylabel("Max transfer fraction")
    ax.set_title("Negative control\n(shuffled specs, should be ≤ 0.10)")
    ax.set_ylim(0, 1)
    ax.legend()

    status = "PASS ✓" if passes else "FAIL ✗"
    ax.text(0, real_max + 0.05, status, ha="center", fontsize=14,
            color="#029e73" if passes else "#d55e00", fontweight="bold")
    base_style(ax)
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "negative_control.png", dpi=300, bbox_inches="tight")
    plt.close()
    print(f"  → negative_control.png")


def fig_headline_summary():
    """
    Figure 8: Headline summary — study results at a glance.
    """
    study_results = load_json("study_results.json")
    if not study_results:
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.text(0.5, 0.5, "No study results yet.\nRun the full pipeline.",
                ha="center", va="center", transform=ax.transAxes, fontsize=14)
        ax.axis("off")
        plt.tight_layout()
        plt.savefig(FIGURES_DIR / "headline_summary.png", dpi=300, bbox_inches="tight")
        return

    hypotheses = [r["hypothesis"] for r in study_results]
    points = [r["point_estimate"] for r in study_results]
    ci_lo = [r["ci_95"][0] for r in study_results]
    ci_hi = [r["ci_95"][1] for r in study_results]
    colors = ["#029e73" if r["significant"] else "#d55e00" for r in study_results]

    fig, ax = plt.subplots(figsize=(10, 6))
    y = range(len(hypotheses))
    ax.barh(list(y), points, color=colors, alpha=0.7)
    for i, (lo, hi) in enumerate(zip(ci_lo, ci_hi)):
        ax.plot([lo, hi], [i, i], color="black", linewidth=2)
        ax.plot([lo, lo], [i - 0.1, i + 0.1], color="black", linewidth=2)
        ax.plot([hi, hi], [i - 0.1, i + 0.1], color="black", linewidth=2)

    ax.set_yticks(list(y))
    ax.set_yticklabels(hypotheses)
    ax.set_xlabel("Effect size (point estimate ± 95% CI)")
    ax.set_title("Cross-Language Invariant Mining — Study Results\n" +
                 "(green = significant, red = not significant)")
    ax.axvline(x=0, color="gray", linestyle="--", alpha=0.5)
    base_style(ax)
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "headline_summary.png", dpi=300, bbox_inches="tight")
    plt.close()
    print(f"  → headline_summary.png")


# ──────────────────────────────────────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────────────────────────────────────

def main():
    print("Generating figures...")
    fig_h1_replication()
    fig_h2_transfer_heatmap()
    fig_h3_mismatch_matrix()
    fig_self_similarity_matrix()
    fig_failure_rates()
    fig_positive_control()
    fig_negative_control()
    fig_headline_summary()
    print(f"\nAll figures saved to {FIGURES_DIR}/")


if __name__ == "__main__":
    main()
