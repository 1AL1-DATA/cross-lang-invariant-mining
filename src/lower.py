"""
Phase 3: AST → Intermediate Representation (IR) lowering.

Two IR levels:
1. IR-CFG: Control-Flow Graph — branches, loops/recursion, sequencing
2. IR-Dataflow: Dependency graph — which values depend on which

Both IRs are language-agnostic. The lowering rules are documented
explicitly (see PREREGISTRATION.md §9) so the bias source is visible.

The IR is validated against the positive control (binary search)
before Phase 4 begins.
"""

from __future__ import annotations

import json
import hashlib
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Set, Tuple
from pathlib import Path

from parse import ASTNode, ASTNodeType, ParsedImplementation


# ──────────────────────────────────────────────────────────────────────────────
# IR node types
# ──────────────────────────────────────────────────────────────────────────────

class IRNodeType(str, Enum):
    FUNCTION = "FUNCTION"
    PARAM = "PARAM"
    BRANCH = "BRANCH"           # if/elif/else, match/case, guards
    LOOP = "LOOP"               # for, while, recursion (tail or non-tail)
    SEQUENCE = "SEQUENCE"       # sequential statements
    CALL = "CALL"               # function call
    RETURN = "RETURN"
    ASSIGN = "ASSIGN"           # assignment (mutation or binding)
    EXIT_ERROR = "EXIT_ERROR"   # panic, error return
    RESULT_UNWRAP = "RESULT_UNWRAP"
    LITERAL = "LITERAL"
    IDENTIFIER = "IDENTIFIER"
    SUBSCRIPT = "SUBSCRIPT"
    BINARY_OP = "BINARY_OP"
    UNARY_OP = "UNARY_OP"
    PHI = "PHI"  # merge point in CFG (functional languages)


@dataclass
class IRNode:
    ir_type: IRNodeType
    label: str = ""                     # human-readable label
    params: List["IRNode"] = field(default_factory=list)
    body: List["IRNode"] = field(default_factory=list)
    condition: Optional["IRNode"] = None
    then_branch: Optional["IRNode"] = None
    else_branch: Optional["IRNode"] = None
    loop_body: Optional["IRNode"] = None
    arms: List[Tuple["IRNode", "IRNode"]] = field(default_factory=list)  # (pattern, body)
    value: Optional[str] = None
    metadata: Dict = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return {
            "type": self.ir_type.value,
            "label": self.label,
            "params": [p.to_dict() for p in self.params],
            "body": [b.to_dict() for b in self.body],
            "condition": self.condition.to_dict() if self.condition else None,
            "then_branch": self.then_branch.to_dict() if self.then_branch else None,
            "else_branch": self.else_branch.to_dict() if self.else_branch else None,
            "loop_body": self.loop_body.to_dict() if self.loop_body else None,
            "arms": [(pat.to_dict(), bod.to_dict()) for pat, bod in self.arms],
            "value": self.value,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, d: Dict) -> "IRNode":
        arms = [(cls.from_dict(p), cls.from_dict(b)) for p, b in d.get("arms", [])]
        return cls(
            ir_type=IRNodeType(d["type"]),
            label=d.get("label", ""),
            params=[cls.from_dict(p) for p in d.get("params", [])],
            body=[cls.from_dict(b) for b in d.get("body", [])],
            condition=cls.from_dict(d["condition"]) if d.get("condition") else None,
            then_branch=cls.from_dict(d["then_branch"]) if d.get("then_branch") else None,
            else_branch=cls.from_dict(d["else_branch"]) if d.get("else_branch") else None,
            loop_body=cls.from_dict(d["loop_body"]) if d.get("loop_body") else None,
            arms=arms,
            value=d.get("value"),
            metadata=d.get("metadata", {}),
        )

    def ir_hash(self) -> str:
        """Canonical hash for IR isomorphism checking — includes all node content."""
        return hashlib.sha256(
            json.dumps(self.to_dict(), sort_keys=True).encode()
        ).hexdigest()[:16]

    def cfg_hash(self) -> str:
        """
        CFG-topology-aware hash.

        Encodes only control-flow nodes (BRANCH/LOOP/MATCH) and the path taken
        through them, ignoring SEQUENCE nodes and all variable names/literals.
        Two implementations of the same algorithm produce the same hash even if
        they use different identifiers; implementations of different algorithms
        produce different hashes because their control-flow topology differs.

        Encoding: a list of (direction, node_type) tuples walked depth-first
        through the CFG, where direction encodes how we arrived at each node.
        """
        parts: list = []

        def walk(node: "IRNode", direction: str = "entry") -> None:
            # Encode this node
            if node.ir_type == IRNodeType.BRANCH:
                has_then = node.then_branch is not None
                has_else = node.else_branch is not None
                parts.append((direction, "BRANCH", has_then, has_else))
                if node.then_branch:
                    walk(node.then_branch, "then")
                if node.else_branch:
                    walk(node.else_branch, "else")
            elif node.ir_type == IRNodeType.LOOP:
                parts.append((direction, "LOOP"))
                if node.loop_body:
                    walk(node.loop_body, "loop")
            elif node.arms:  # match expression
                parts.append((direction, "MATCH", len(node.arms)))
                for _, arm_body in node.arms:
                    walk(arm_body, "match")
            else:
                # Sequential or leaf: traverse children but keep direction
                for child in node.body:
                    walk(child, direction)

        for item in self.body:
            walk(item, "entry")

        # If the function has no control-flow nodes at all, return None.
        # Sequential-only code is universal across all implementations and languages
        # (every function has some body statements). Mining it as an invariant
        # produces false positives in the negative control.
        if not parts:
            return None

        encoded = json.dumps(parts, sort_keys=True)
        return hashlib.sha256(encoded.encode()).hexdigest()[:16]

    def node_count(self) -> int:
        return 1 + sum(
            b.node_count() for b in
            self.body + self.params +
            ([self.condition] if self.condition else []) +
            ([self.then_branch] if self.then_branch else []) +
            ([self.else_branch] if self.else_branch else []) +
            ([self.loop_body] if self.loop_body else []) +
            [p for p, b in self.arms] + [b for p, b in self.arms]
        )

    def walk(self):
        yield self
        for n in self.params:
            yield from n.walk()
        for n in self.body:
            yield from n.walk()
        if self.condition:
            yield from self.condition.walk()
        if self.then_branch:
            yield from self.then_branch.walk()
        if self.else_branch:
            yield from self.else_branch.walk()
        if self.loop_body:
            yield from self.loop_body.walk()
        for pat, bod in self.arms:
            yield from pat.walk()
            yield from bod.walk()


# ──────────────────────────────────────────────────────────────────────────────
# Lowering rules
# ──────────────────────────────────────────────────────────────────────────────

def ast_to_ir(ast: ASTNode, language: str) -> IRNode:
    """Main entry point: lower an ASTNode to an IRNode tree."""
    return _lower_ast_node(ast, language)


def _lower_ast_node(node: ASTNode, language: str) -> IRNode:
    """Recursive AST → IR lowering with language-specific rules."""
    # Map AST node types to IR node types (documented in PREREGISTRATION §9)
    mapping = _get_ast_to_ir_mapping(language)
    ir_type_str = mapping.get(node.node_type.value, _infer_ir_type(node))
    ir_type = IRNodeType(ir_type_str)

    # Build IR node
    ir = IRNode(ir_type=ir_type, label=node.value or "", metadata={"ast_type": node.node_type.value})

    if node.node_type == ASTNodeType.FUNCTION:
        ir.label = node.value or "anon"
        body_items = []
        for c in node.children:
            if c.node_type == ASTNodeType.PARAM:
                ir.params.append(_lower_ast_node(c, language))
            elif c.node_type == ASTNodeType.BLOCK:
                body_items.extend(c.children)
            else:
                # TypeScript, Haskell, OCaml, Go, Rust put body items directly
                # under FUNCTION without wrapping them in a BLOCK node.
                body_items.append(c)
        ir.body = [_lower_ast_node(b, language) for b in body_items]

    elif node.node_type == ASTNodeType.IF:
        # Find condition, then_branch, else_branch from children
        ir.condition = _find_condition(node)  # type: ignore[func-returns-ref]
        branches = _extract_if_branches(node, language)
        if len(branches) >= 1:
            ir.then_branch = branches[0]
        if len(branches) >= 2:
            ir.else_branch = branches[1]
        elif len(branches) == 1:
            ir.else_branch = IRNode(ir_type=IRNodeType.SEQUENCE, body=[])

    elif node.node_type == ASTNodeType.FOR or node.node_type == ASTNodeType.WHILE:
        ir.loop_body = IRNode(
            ir_type=IRNodeType.SEQUENCE,
            body=[_lower_ast_node(c, language) for c in node.children],
        )

    elif node.node_type == ASTNodeType.MATCH or node.node_type == ASTNodeType.MATCH_ARM:
        for arm_child in node.children:
            if arm_child.node_type == ASTNodeType.MATCH_ARM:
                # match arm: pattern + body
                arms = _extract_match_arms(node, language)
                ir.arms = [(IRNode(ir_type=IRNodeType.IDENTIFIER, label=a[0]), _lower_ast_node(a[1], language)) for a in arms]
            else:
                ir.body.append(_lower_ast_node(arm_child, language))

    elif node.node_type == ASTNodeType.BLOCK:
        ir.body = [_lower_ast_node(c, language) for c in node.children if c.node_type != ASTNodeType.COMMENT]

    elif node.node_type == ASTNodeType.LITERAL:
        ir.value = node.value

    elif node.node_type == ASTNodeType.IDENTIFIER:
        ir.value = node.value

    elif node.node_type == ASTNodeType.BINARY_OP:
        ir.value = node.value
        ir.body = [_lower_ast_node(c, language) for c in node.children]

    elif node.node_type == ASTNodeType.ASSIGNMENT:
        ir.value = node.value
        ir.body = [_lower_ast_node(c, language) for c in node.children]

    else:
        # Generic: descend
        ir.body = [_lower_ast_node(c, language) for c in node.children if c.node_type != ASTNodeType.COMMENT]

    return ir


def _get_ast_to_ir_mapping(language: str) -> Dict[str, str]:
    """AST → IR type mapping per language."""
    base = {
        "FUNCTION": "FUNCTION",
        "PARAM": "PARAM",
        "RETURN": "RETURN",
        "CALL": "CALL",
        "LITERAL": "LITERAL",
        "IDENTIFIER": "IDENTIFIER",
        "SUBSCRIPT": "SUBSCRIPT",
        "BINARY_OP": "BINARY_OP",
        "UNARY_OP": "UNARY_OP",
        "ASSIGNMENT": "ASSIGN",
        "VARIABLE_DECL": "ASSIGN",
        "IF": "BRANCH",
        "MATCH": "BRANCH",
        "MATCH_ARM": "BRANCH",
        "FOR": "LOOP",
        "WHILE": "LOOP",
        "LOOP": "LOOP",
        "BLOCK": "SEQUENCE",
        "EXPRESSION_STMT": "SEQUENCE",
        "LIST_LITERAL": "LITERAL",
        "TUPLE": "LITERAL",
        "RESULT_OK": "RESULT_UNWRAP",
        "RESULT_ERR": "EXIT_ERROR",
        "PANIC": "EXIT_ERROR",
        "LAMBDA": "FUNCTION",
        "MODULE": "SEQUENCE",
    }
    return base


def _infer_ir_type(node: ASTNode) -> str:
    """Fallback IR type inference."""
    lower = node.node_type.value.lower()
    if "branch" in lower or "match" in lower or "if" in lower:
        return "BRANCH"
    if "loop" in lower or "for" in lower or "while" in lower:
        return "LOOP"
    if "function" in lower:
        return "FUNCTION"
    if "return" in lower:
        return "RETURN"
    if "call" in lower:
        return "CALL"
    if "literal" in lower or "constant" in lower:
        return "LITERAL"
    if "identifier" in lower:
        return "IDENTIFIER"
    if "assign" in lower or "decl" in lower:
        return "ASSIGN"
    return "SEQUENCE"


def _find_condition(node: ASTNode) -> Optional[IRNode]:
    for c in node.children:
        if c.node_type in (ASTNodeType.BINARY_OP, ASTNodeType.IDENTIFIER, ASTNodeType.LITERAL):
            return _lower_ast_node(c, "")
    return None


def _extract_if_branches(node: ASTNode, language: str) -> List[IRNode]:
    branches = []
    current_body: List[ASTNode] = []
    for c in node.children:
        if c.node_type == ASTNodeType.IF or c.node_type == ASTNodeType.MATCH:
            continue  # nested
        if c.node_type == ASTNodeType.BLOCK:
            current_body.extend(c.children)
        else:
            current_body.append(c)
    if current_body:
        branches.append(IRNode(
            ir_type=IRNodeType.SEQUENCE,
            body=[_lower_ast_node(child, language) for child in current_body],
        ))
    return branches


def _extract_match_arms(node: ASTNode, language: str) -> List[Tuple[str, ASTNode]]:
    arms = []
    for c in node.children:
        if c.node_type == ASTNodeType.MATCH_ARM:
            pattern = ""
            body = None
            for grand in c.children:
                if grand.node_type == ASTNodeType.IDENTIFIER or grand.node_type == ASTNodeType.LITERAL:
                    pattern = grand.value or ""
                else:
                    body = grand
            if body and pattern:
                arms.append((pattern, body))
    return arms


# ──────────────────────────────────────────────────────────────────────────────
# Data-flow graph (simplified: def-use pairs)
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class DataFlowGraph:
    """Simplified data-flow graph: def → set of uses."""
    edges: Dict[str, Set[str]]  # variable → set of variables it flows into

    def to_dict(self) -> Dict:
        return {k: list(v) for k, v in self.edges.items()}

    @classmethod
    def from_ir(cls, ir: IRNode) -> "DataFlowGraph":
        edges: Dict[str, Set[str]] = {}
        _collect_def_uses(ir, edges, set())
        return cls(edges=edges)


def _collect_def_uses(ir: IRNode, edges: Dict[str, Set[str]], current_scope: Set[str]) -> Set[str]:
    """Collect def→use edges and return the set of variables in scope."""
    scope = set(current_scope)

    if ir.ir_type == IRNodeType.ASSIGN:
        # First child is the target, rest are the value
        targets = [n for n in ir.body if n.ir_type == IRNodeType.IDENTIFIER]
        uses = [n for n in ir.body if n.ir_type != IRNodeType.IDENTIFIER]
        for target in targets:
            t_name = target.value or "_"
            for use_node in uses:
                for used_name in _extract_names(use_node):
                    if used_name in scope:
                        edges.setdefault(used_name, set()).add(t_name)
        for t in targets:
            scope.add(t.value or "_")

    elif ir.ir_type == IRNodeType.IDENTIFIER:
        scope.add(ir.value or "_")

    # Recurse
    for n in ir.body + ir.params:
        _collect_def_uses(n, edges, scope)
    if ir.condition:
        _collect_def_uses(ir.condition, edges, scope)
    if ir.then_branch:
        _collect_def_uses(ir.then_branch, edges, scope)
    if ir.else_branch:
        _collect_def_uses(ir.else_branch, edges, scope)
    if ir.loop_body:
        _collect_def_uses(ir.loop_body, edges, scope)
    for pat, bod in ir.arms:
        _collect_def_uses(pat, edges, scope)
        _collect_def_uses(bod, edges, scope)

    return scope


def _extract_names(ir: IRNode) -> List[str]:
    """Extract all identifier names from an IR subtree."""
    names = []
    if ir.ir_type == IRNodeType.IDENTIFIER and ir.value:
        names.append(ir.value)
    for n in ir.walk():
        if n.ir_type == IRNodeType.IDENTIFIER and n.value:
            names.append(n.value)
    return names


# ──────────────────────────────────────────────────────────────────────────────
# High-level IR functions
# ──────────────────────────────────────────────────────────────────────────────

def lower_implementation(
    parsed: ParsedImplementation,
    output_dir: Path,
) -> Tuple[IRNode, DataFlowGraph, Path]:
    """
    Lower a ParsedImplementation to IR-CFG + IR-dataflow.
    Returns (ir_cfg, dataflow_graph, output_path).
    """
    ir = ast_to_ir(parsed.ast, parsed.language)
    dfgraph = DataFlowGraph.from_ir(ir)
    ir_hash = ir.ir_hash()

    out_path = output_dir / f"{ir_hash}.ir.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps({
        "ir": ir.to_dict(),
        "dataflow": dfgraph.to_dict(),
        "spec_id": parsed.spec_id,
        "language": parsed.language,
        "ast_hash": parsed.ast_hash,
    }, indent=2))

    return ir, dfgraph, out_path


def load_ir(ir_path: Path) -> Tuple[IRNode, DataFlowGraph, str, str]:
    """Load a saved IR from disk."""
    data = json.loads(ir_path.read_text())
    ir = IRNode.from_dict(data["ir"])
    dfgraph = DataFlowGraph(edges={k: set(v) for k, v in data["dataflow"].items()})
    return ir, dfgraph, data["spec_id"], data["language"]


# ──────────────────────────────────────────────────────────────────────────────
# Granularity-level helpers
# ──────────────────────────────────────────────────────────────────────────────

class GranularityLevel(str, Enum):
    L4 = "L4"  # whole-function CFG
    L3 = "L3"  # block-level (loop bodies, branch arms)
    L2 = "L2"  # statement-level
    L1 = "L1"  # expression-level


def get_ir_subgraphs(ir: IRNode, level: GranularityLevel) -> List[IRNode]:
    """
    Extract IR subgraphs at a given granularity level.
    L4: the whole function
    L3: basic blocks (loop bodies, branch arms, match arms)
    L2: individual nodes
    L1: expression subtrees
    """
    if level == GranularityLevel.L4:
        return [ir]

    subgraphs = []
    if level == GranularityLevel.L3:
        for node in ir.walk():
            if node.ir_type in (IRNodeType.LOOP, IRNodeType.BRANCH):
                subgraphs.append(node)
            elif node.ir_type == IRNodeType.SEQUENCE and node.body:
                subgraphs.append(node)

    elif level == GranularityLevel.L2:
        for node in ir.walk():
            if node.ir_type not in (IRNodeType.IDENTIFIER, IRNodeType.LITERAL):
                subgraphs.append(node)

    elif level == GranularityLevel.L1:
        for node in ir.walk():
            if node.body:
                subgraphs.extend(node.body)

    return subgraphs


if __name__ == "__main__":
    # Quick smoke test with binary search
    from parse import ParsedImplementation
    import tempfile

    sample = '''
def binary_search(arr, target):
    lo = 0
    hi = len(arr) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1
'''
    parsed = ParsedImplementation.from_source(
        "t1-ac2-001", "python", sample, Path("/tmp/ir_test")
    )
    ir, df, _ = lower_implementation(parsed, Path("/tmp/ir_test"))
    print(f"IR hash: {ir.ir_hash()}")
    print(f"IR nodes: {ir.node_count()}")
    print(f"Dataflow edges: {df.edges}")
    print(json.dumps(ir.to_dict(), indent=2)[:1000])
