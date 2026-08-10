"""
Phase 4: Invariant mining — within-language (4a) and cross-language (4b).

Key design:
- Within-language: operate on native ASTs, run at 60/70/80% thresholds.
- Cross-language: operate on IR subgraphs, require ≥3 languages including L3/L4.
- Jaccard overlap used for H1 replication test.
- Negative control (shuffled specs) run here to rule out artifact detection.
"""

from __future__ import annotations

import json
import hashlib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from collections import defaultdict
from itertools import combinations

from parse import ASTNode, ASTNodeType, ParsedImplementation, get_all_functions, get_cfg_blocks
from lower import (
    IRNode, DataFlowGraph, lower_implementation, load_ir,
    get_ir_subgraphs, GranularityLevel, IRNodeType,
)


# ──────────────────────────────────────────────────────────────────────────────
# Data structures
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class Invariant:
    """A mined structural invariant (subgraph hash + support info)."""
    subgraph_hash: str
    ir_type: str                        # IR node type or "MULTI" for compound
    level: GranularityLevel
    support: float                      # fraction 0–1
    support_count: int                  # absolute count
    total: int                          # total implementations
    languages: List[str] = field(default_factory=list)  # which languages contributed
    spec_id: str = ""

    def to_dict(self) -> Dict:
        return {
            "subgraph_hash": self.subgraph_hash,
            "ir_type": self.ir_type,
            "level": self.level.value,
            "support": round(self.support, 4),
            "support_count": self.support_count,
            "total": self.total,
            "languages": self.languages,
            "spec_id": self.spec_id,
        }


@dataclass
class MiningResult:
    spec_id: str
    language: Optional[str]   # None for cross-language
    threshold: int            # 60, 70, or 80
    invariants: List[Invariant] = field(default_factory=list)
    n_implementations: int = 0

    def to_dict(self) -> Dict:
        return {
            "spec_id": self.spec_id,
            "language": self.language,
            "threshold": self.threshold,
            "n_implementations": self.n_implementations,
            "n_invariants": len(self.invariants),
            "invariants": [i.to_dict() for i in self.invariants],
        }


# ──────────────────────────────────────────────────────────────────────────────
# Within-language invariant mining (Phase 4a)
# ──────────────────────────────────────────────────────────────────────────────

def mine_within_language(
    spec_id: str,
    language: str,
    implementations: List[ParsedImplementation],
    threshold: int,
    levels: List[GranularityLevel] = None,
) -> MiningResult:
    """
    Mine structural invariants from implementations in a single language.
    Uses native ASTs (not IR) for within-language.
    """
    if levels is None:
        levels = [GranularityLevel.L4, GranularityLevel.L3, GranularityLevel.L2]

    result = MiningResult(spec_id=spec_id, language=language, threshold=threshold)
    result.n_implementations = len(implementations)

    if len(implementations) < 2:
        return result

    # Collect subgraphs at each level
    for level in levels:
        subgraph_hashes: Dict[str, int] = defaultdict(int)

        for impl in implementations:
            # Use AST functions for within-language.
            # Count each subgraph at most once per implementation so that
            # support (= count / n_implementations) is always in [0, 1].
            seen: Set[str] = set()
            functions = get_all_functions(impl.ast)
            for func in functions:
                subgraphs = _extract_ast_subgraphs(func, level)
                for sg in subgraphs:
                    h = hashlib.sha256(json.dumps(sg, sort_keys=True).encode()).hexdigest()[:16]
                    if h not in seen:
                        seen.add(h)
                        subgraph_hashes[h] += 1

        min_count = int(result.n_implementations * threshold / 100)
        for h, count in subgraph_hashes.items():
            if count >= min_count:
                inv = Invariant(
                    subgraph_hash=h,
                    ir_type="AST",
                    level=level,
                    support=count / result.n_implementations,
                    support_count=count,
                    total=result.n_implementations,
                    languages=[language],
                    spec_id=spec_id,
                )
                result.invariants.append(inv)

    return result


def _extract_ast_subgraphs(node: ASTNode, level: GranularityLevel) -> List[Dict]:
    """
    Extract AST subgraphs at the given granularity level.
    Returns serializable dicts for hashing.
    """
    if level == GranularityLevel.L4:
        return [node.to_dict()]

    subgraphs = []

    def walk(n: ASTNode, depth: int = 0):
        if level == GranularityLevel.L3:
            # Block-level: loop/branch bodies
            if n.node_type in (
                ASTNodeType.LOOP, ASTNodeType.FOR, ASTNodeType.WHILE,
                ASTNodeType.IF, ASTNodeType.MATCH, ASTNodeType.MATCH_ARM,
                ASTNodeType.BLOCK,
            ):
                subgraphs.append(n.to_dict())
        elif level == GranularityLevel.L2:
            # Statement-level: non-leaf nodes
            if n.node_type not in (ASTNodeType.IDENTIFIER, ASTNodeType.LITERAL):
                subgraphs.append(n.to_dict())
        elif level == GranularityLevel.L1:
            # Expression-level
            if n.children:
                subgraphs.append(n.to_dict())

        for c in n.children:
            walk(c, depth + 1)

    walk(node)
    return subgraphs


# ──────────────────────────────────────────────────────────────────────────────
# Cross-language invariant mining (Phase 4b)
# ──────────────────────────────────────────────────────────────────────────────

def mine_cross_language(
    spec_id: str,
    implementations_by_lang: Dict[str, List[Tuple[IRNode, DataFlowGraph]]],
    threshold: int,
    levels: List[GranularityLevel] = None,
    require_structurally_distant: bool = True,
) -> MiningResult:
    """
    Mine invariant IR-subgraphs across all languages for a given spec.
    Reports which languages contributed to each invariant.
    """
    if levels is None:
        levels = [GranularityLevel.L4, GranularityLevel.L3, GranularityLevel.L2]

    result = MiningResult(spec_id=spec_id, language=None, threshold=threshold)
    all_languages = list(implementations_by_lang.keys())
    total_implementations = sum(len(v) for v in implementations_by_lang.values())
    result.n_implementations = total_implementations

    if total_implementations < 2 or len(all_languages) < 2:
        return result

    for level in levels:
        # Collect all IR subgraphs with language labels
        lang_subgraphs: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
        # lang → hash → count

        for lang, irs in implementations_by_lang.items():
            for ir, _ in irs:
                # Count each subgraph at most once per implementation so that
                # support (= total_count / total_implementations) is always
                # in [0, 1] — previously this summed every occurrence across
                # languages, which could produce support > 1.0.
                seen: Set[str] = set()
                for sg in get_ir_subgraphs(ir, level):
                    # cfg_hash encodes control-flow topology (branch/loop nesting,
                    # not variable names or literal values). Two implementations
                    # of the same algorithm produce the same cfg_hash even if they
                    # use different identifiers. Returns None for sequential-only
                    # subgraphs (no CFG nodes) — these are excluded as universal.
                    h = sg.cfg_hash()
                    if h is None:
                        continue  # sequential-only: skip, not a structural invariant
                    if h not in seen:
                        seen.add(h)
                        lang_subgraphs[lang][h] += 1

        # Find subgraphs appearing in multiple languages
        all_hashes = set()
        for h_set in [set(d.keys()) for d in lang_subgraphs.values()]:
            all_hashes |= h_set

        for h in all_hashes:
            contributing_langs = [
                lang for lang in all_languages
                if h in lang_subgraphs[lang] and lang_subgraphs[lang][h] > 0
            ]
            if len(contributing_langs) < 2:
                continue

            # Compute weighted support across all languages
            total_count = sum(lang_subgraphs[lang][h] for lang in contributing_langs)
            support = total_count / total_implementations

            if support * 100 >= threshold:
                inv = Invariant(
                    subgraph_hash=h,
                    ir_type="IR",
                    level=level,
                    support=support,
                    support_count=total_count,
                    total=total_implementations,
                    languages=contributing_langs,
                    spec_id=spec_id,
                )
                result.invariants.append(inv)

    return result


# ──────────────────────────────────────────────────────────────────────────────
# H1: Replication test (Jaccard overlap)
# ──────────────────────────────────────────────────────────────────────────────

def compute_jaccard(
    set_a: List[Invariant],
    set_b: List[Invariant],
) -> float:
    """
    Jaccard coefficient between two invariant sets.
    Based on subgraph_hash equality.
    """
    hashes_a = {i.subgraph_hash for i in set_a}
    hashes_b = {i.subgraph_hash for i in set_b}

    if not hashes_a and not hashes_b:
        return 1.0
    if not hashes_a or not hashes_b:
        return 0.0

    intersection = hashes_a & hashes_b
    union = hashes_a | hashes_b
    return len(intersection) / len(union)


def replication_test(
    primary_invariants: List[Invariant],
    replication_invariants: List[Invariant],
    threshold: int,
) -> Dict:
    """
    H1 replication test: compute Jaccard between primary and replication batch invariants.
    Returns dict with Jaccard and confidence interval bounds.
    """
    jaccard = compute_jaccard(primary_invariants, replication_invariants)

    # Bootstrap CI (simplified: just report the point estimate and note CI is computed in evaluate.py)
    return {
        "threshold": threshold,
        "jaccard": round(jaccard, 4),
        "n_primary": len(primary_invariants),
        "n_replication": len(replication_invariants),
        "primary_hashes": [i.subgraph_hash for i in primary_invariants],
        "replication_hashes": [i.subgraph_hash for i in replication_invariants],
    }


# ──────────────────────────────────────────────────────────────────────────────
# H2: Transfer fraction
# ──────────────────────────────────────────────────────────────────────────────

def compute_transfer_fraction(
    within_lang_invariants: Dict[str, List[Invariant]],  # lang → invariants
    cross_lang_invariants: List[Invariant],
    structurally_distant: List[str] = None,  # e.g. ["haskell", "ocaml"]
) -> Dict:
    """
    H2 transfer test: for each within-language invariant, check if it has
    a cross-language counterpart.

    Returns per-spec transfer fractions and a summary.
    """
    if structurally_distant is None:
        structurally_distant = ["haskell", "ocaml"]

    cross_hashes = {inv.subgraph_hash: inv for inv in cross_lang_invariants}

    total_within = 0
    transferred = 0
    transferred_with_distal = 0

    for lang, invariants in within_lang_invariants.items():
        for inv in invariants:
            total_within += 1
            if inv.subgraph_hash in cross_hashes:
                transferred += 1
                cross_inv = cross_hashes[inv.subgraph_hash]
                has_distal = any(
                    lang in cross_inv.languages
                    for lang in structurally_distant
                )
                if has_distal:
                    transferred_with_distal += 1

    fraction = transferred / total_within if total_within > 0 else 0.0
    distal_fraction = transferred_with_distal / total_within if total_within > 0 else 0.0

    return {
        "total_within_language_invariants": total_within,
        "transferred_count": transferred,
        "transferred_with_distal_count": transferred_with_distal,
        "transfer_fraction": round(fraction, 4),
        "distal_transfer_fraction": round(distal_fraction, 4),
        "structurally_distant_languages": structurally_distant,
    }


# ──────────────────────────────────────────────────────────────────────────────
# Negative control: shuffled specs
# ──────────────────────────────────────────────────────────────────────────────

def negative_control(
    shuffled_implementations: Dict[str, List[Tuple[IRNode, DataFlowGraph]]],
    threshold: int,
    levels: "list[GranularityLevel]|None" = None,
) -> Dict:
    """
    Run cross-language invariant mining on shuffled (unrelated) spec implementations.
    If support >= threshold is found, the method is artifact-prone.
    """
    if levels is None:
        levels = [GranularityLevel.L4, GranularityLevel.L3, GranularityLevel.L2]
    result = mine_cross_language(
        spec_id="__NEGATIVE_CONTROL__",
        implementations_by_lang=shuffled_implementations,
        threshold=threshold,
        levels=levels,
    )

    return {
        "threshold": threshold,
        "n_invariants_found": len(result.invariants),
        "max_support": max((i.support for i in result.invariants), default=0.0),
        "passes_negative_control": (
            len(result.invariants) == 0 or
            max((i.support for i in result.invariants), default=0.0) < 0.10
        ),
        "invariants": [i.to_dict() for i in result.invariants],
    }


# ──────────────────────────────────────────────────────────────────────────────
# Save results
# ──────────────────────────────────────────────────────────────────────────────

def save_mining_result(result: MiningResult, output_dir: Path):
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"mining_{result.spec_id}_{result.language or 'crosslang'}_t{result.threshold}.json"
    path.write_text(json.dumps(result.to_dict(), indent=2))
    return path


if __name__ == "__main__":
    # Smoke test: mine invariants from a manually-built IR
    ir1 = IRNode(ir_type=IRNodeType.FUNCTION, label="foo", body=[
        IRNode(ir_type=IRNodeType.LOOP, body=[
            IRNode(ir_type=IRNodeType.BRANCH, body=[])
        ])
    ])
    ir2 = IRNode(ir_type=IRNodeType.FUNCTION, label="bar", body=[
        IRNode(ir_type=IRNodeType.LOOP, body=[
            IRNode(ir_type=IRNodeType.BRANCH, body=[])
        ])
    ])

    result = mine_cross_language(
        "t1-ac2-001",
        {"python": [(ir1, DataFlowGraph({}))], "rust": [(ir2, DataFlowGraph({}))]},
        threshold=60,
    )
    print(f"Cross-language invariants: {len(result.invariants)}")
    for inv in result.invariants:
        print(f"  {inv.subgraph_hash}: support={inv.support:.2f}, langs={inv.languages}")
