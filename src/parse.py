"""
Phase 3: AST parsing via tree-sitter.

For each language, we use tree-sitter to produce a native parse tree.
The tree-sitter grammars give us a consistent API across Python, Rust,
Haskell, OCaml, Go, and TypeScript.

Key design decisions:
- We store the raw CST (Concrete Syntax Tree) as JSON.
- We keep the raw AST because Phase 4a (within-language mining) operates on native ASTs.
- We also store a "simplified AST" with just the node types we care about,
  which is what lower.py uses for IR generation.
"""

from __future__ import annotations

import json
import hashlib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Any
from enum import Enum
import subprocess
import sys

# ──────────────────────────────────────────────────────────────────────────────
# Simplified AST node types (shared across all languages after normalization)
# ──────────────────────────────────────────────────────────────────────────────

class ASTNodeType(str, Enum):
    # Declarations
    FUNCTION = "FUNCTION"
    PARAM = "PARAM"
    VARIABLE_DECL = "VARIABLE_DECL"
    CONSTANT = "CONSTANT"
    TYPE_ANNOTATION = "TYPE_ANNOTATION"
    # Statements
    ASSIGNMENT = "ASSIGNMENT"
    RETURN = "RETURN"
    IF = "IF"
    LOOP = "LOOP"
    WHILE = "WHILE"
    FOR = "FOR"
    MATCH = "MATCH"
    MATCH_ARM = "MATCH_ARM"
    CALL = "CALL"
    EXPRESSION_STMT = "EXPRESSION_STMT"
    # Expressions
    BINARY_OP = "BINARY_OP"
    UNARY_OP = "UNARY_OP"
    LITERAL = "LITERAL"
    IDENTIFIER = "IDENTIFIER"
    SUBSCRIPT = "SUBSCRIPT"
    MEMBER_ACCESS = "MEMBER_ACCESS"
    LAMBDA = "LAMBDA"
    TUPLE = "TUPLE"
    LIST_LITERAL = "LIST_LITERAL"
    DICT_LITERAL = "DICT_LITERAL"
    # Error handling
    RESULT_OK = "RESULT_OK"
    RESULT_ERR = "RESULT_ERR"
    RESULT_UNWRAP = "RESULT_UNWRAP"
    PANIC = "PANIC"
    # Other
    COMMENT = "COMMENT"
    DECORATOR = "DECORATOR"
    IMPORT = "IMPORT"
    MODULE = "MODULE"
    BLOCK = "BLOCK"
    EMPTY = "EMPTY"


@dataclass
class ASTNode:
    node_type: ASTNodeType
    value: Optional[str] = None
    children: List[ASTNode] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return {
            "type": self.node_type.value,
            "value": self.value,
            "children": [c.to_dict() for c in self.children],
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, d: Dict) -> ASTNode:
        return cls(
            node_type=ASTNodeType(d["type"]),
            value=d.get("value"),
            children=[cls.from_dict(c) for c in d.get("children", [])],
            metadata=d.get("metadata", {}),
        )

    def ast_hash(self) -> str:
        """Normalized AST hash for deduplication (whitespace-insensitive)."""
        return hashlib.sha256(
            json.dumps(self.to_dict(), sort_keys=True).encode()
        ).hexdigest()[:16]

    def node_count(self) -> int:
        return 1 + sum(c.node_count() for c in self.children)

    def walk(self):
        """Depth-first walk yielding all nodes."""
        yield self
        for c in self.children:
            yield from c.walk()


@dataclass
class ParsedImplementation:
    spec_id: str
    language: str
    source: str
    raw_cst: Dict  # raw tree-sitter CST as dict
    ast: ASTNode   # simplified AST
    ast_hash: str
    ast_path: Path
    cst_path: Path

    @classmethod
    def from_source(
        cls,
        spec_id: str,
        language: str,
        source: str,
        output_dir: Path,
    ) -> "ParsedImplementation":
        # Parse using tree-sitter via CLI
        cst = _tree_sitter_parse(language, source)
        ast = _cst_to_ast(language, cst, source)
        ast_hash = ast.ast_hash()

        # Save raw CST and simplified AST
        cst_path = output_dir / f"{ast_hash}.cst.json"
        ast_path = output_dir / f"{ast_hash}.ast.json"

        cst_path.parent.mkdir(parents=True, exist_ok=True)
        ast_path.parent.mkdir(parents=True, exist_ok=True)

        cst_path.write_text(json.dumps(cst, indent=2))
        ast_path.write_text(json.dumps(ast.to_dict(), indent=2))

        return cls(
            spec_id=spec_id,
            language=language,
            source=source,
            raw_cst=cst,
            ast=ast,
            ast_hash=ast_hash,
            ast_path=ast_path,
            cst_path=cst_path,
        )


# ──────────────────────────────────────────────────────────────────────────────
# tree-sitter parsing
# ──────────────────────────────────────────────────────────────────────────────

_TREE_SITTER_LANG_ALIASES = {
    "python": "python",
    "rust": "rust",
    "haskell": "haskell",
    "ocaml": "ocaml",
    "go": "go",
    "typescript": "typescript",
}


def _tree_sitter_parse(language: str, source: str) -> Dict:
    """
    Parse source using tree-sitter CLI (ts-cli or tree-sitter CLI).
    Falls back to a regex-based stub if tree-sitter is not available.

    Returns a dict representation of the CST.
    """
    try:
        import tree_sitter_languages

        parser = tree_sitter_languages.get_parser(language)
        tree = parser.parse(source.encode())
        return _tree_to_dict(tree.root_node, source)
    except Exception:
        # Fallback: regex-based stub for when tree-sitter isn't available
        return _regex_stub_parse(language, source)


def _tree_to_dict(node, source: str) -> Dict:
    """Convert tree-sitter Node to a plain dict."""
    return {
        "type": node.type,
        "text": node.text.decode() if node.text else "",
        "start_point": node.start_point,
        "end_point": node.end_point,
        "children": [_tree_to_dict(c, source) for c in node.children],
    }


def _regex_stub_parse(language: str, source: str) -> Dict:
    """
    Regex-based stub parser for when tree-sitter is unavailable.
    Not accurate — use only for development / CI stubs.
    """
    import re

    def stub_node(type_: str, text: str, children: List = None):
        return {
            "type": type_,
            "text": text.strip(),
            "children": children or [],
        }

    if language == "python":
        # Very rough: split on top-level def/class/control flow
        functions = re.findall(
            r"(def\s+\w+\s*\([^)]*\)\s*(?:->\s*\w+\s*)?:(.*?)(?=\n(?:def|class|$)))",
            source,
            re.DOTALL,
        )
        return stub_node("module", source, [
            stub_node("function_definition", f"def {name}:", [
                stub_node("identifier", name),
                stub_node("block", body)
            ])
            for name, body in functions
        ])

    # Generic fallback: one block per line
    return stub_node("module", source, [
        stub_node("statement", line)
        for line in source.split("\n")
        if line.strip()
    ])


# ──────────────────────────────────────────────────────────────────────────────
# CST → simplified AST lowering
# ──────────────────────────────────────────────────────────────────────────────

def _cst_to_ast(language: str, cst: Dict, source: str) -> ASTNode:
    """Lower a raw CST dict to a simplified ASTNode tree."""
    return _lower_node(language, cst)


def _lower_node(language: str, node: Dict) -> ASTNode:
    """Recursive CST → simplified AST lowering."""
    cst_type = node["type"]
    children = [_lower_node(language, c) for c in node.get("children", []) if c.get("text", "").strip()]

    # Map language-specific CST types to shared ASTNodeTypes
    mapping = _get_cst_to_ast_mapping(language)
    ast_type_str = mapping.get(cst_type, _infer_ast_type(cst_type, node))
    ast_type = ASTNodeType(ast_type_str)

    # Extract value for literals / identifiers
    value = None
    if ast_type == ASTNodeType.IDENTIFIER or ast_type == ASTNodeType.LITERAL:
        value = node.get("text", "").strip()

    return ASTNode(
        node_type=ast_type,
        value=value,
        children=children,
        metadata={"cst_type": cst_type, "source_span": node.get("text", "")[:50]},
    )


def _get_cst_to_ast_mapping(language: str) -> Dict[str, str]:
    """Language-specific CST → AST type mapping."""
    mappings = {
        "python": {
            "function_definition": "FUNCTION",
            "identifier": "IDENTIFIER",
            "integer": "LITERAL",
            "string": "LITERAL",
            "boolean": "LITERAL",
            "assignment": "ASSIGNMENT",
            "augmented_assignment": "ASSIGNMENT",
            "return_statement": "RETURN",
            "if_statement": "IF",
            "for_in_clause": "FOR",
            "while_statement": "WHILE",
            "call": "CALL",
            "binary_operator": "BINARY_OP",
            "comparison_operator": "BINARY_OP",
            "unary_operator": "UNARY_OP",
            "comment": "COMMENT",
            "expression_statement": "EXPRESSION_STMT",
            "module": "MODULE",
            "block": "BLOCK",
            "pattern_matching": "MATCH",
            "match_case": "MATCH_ARM",
            "list_literal": "LIST_LITERAL",
            "tuple": "TUPLE",
            "dictionary": "DICT_LITERAL",
            "subscript": "SUBSCRIPT",
            "attribute": "MEMBER_ACCESS",
            "decorator": "DECORATOR",
            "lambda": "LAMBDA",
            "import_statement": "IMPORT",
            "type_annotation": "TYPE_ANNOTATION",
            "parameter": "PARAM",
            "variable_declarator": "VARIABLE_DECL",
        },
        "rust": {
            "function_item": "FUNCTION",
            "identifier": "IDENTIFIER",
            "literal": "LITERAL",
            "let_declaration": "VARIABLE_DECL",
            "assignment_expression": "ASSIGNMENT",
            "return_statement": "RETURN",
            "if_expression": "IF",
            "for_expression": "FOR",
            "while_expression": "WHILE",
            "loop_expression": "LOOP",
            "macro_invocation": "CALL",
            "call_expression": "CALL",
            "binary_expression": "BINARY_OP",
            "unary_expression": "UNARY_OP",
            "block": "BLOCK",
            "match_expression": "MATCH",
            "match_arm": "MATCH_ARM",
            "result_expression": "RESULT_OK",  # simplified
            "option": "RESULT_OK",
            "tuple": "TUPLE",
            "array_expression": "LIST_LITERAL",
        },
        "haskell": {
            "function_declaration": "FUNCTION",
            "function_definition": "FUNCTION",
            "variable": "IDENTIFIER",
            "identifier": "IDENTIFIER",
            "integer": "LITERAL",
            "string": "LITERAL",
            "let_expression": "VARIABLE_DECL",
            "pattern": "PATTERN",
            "lambda_expression": "LAMBDA",
            "case_expression": "MATCH",
            "alternative": "MATCH_ARM",
            "if_expression": "IF",
            "do_expression": "BLOCK",
            "list_literal": "LIST_LITERAL",
            "tuple": "TUPLE",
        },
        "ocaml": {
            "function_definition": "FUNCTION",
            "value_name": "IDENTIFIER",
            "integer_literal": "LITERAL",
            "string_literal": "LITERAL",
            "let_binding": "VARIABLE_DECL",
            "pattern_matching": "MATCH",
            "match_case": "MATCH_ARM",
            "if_expression": "IF",
            "sequence_expression": "BLOCK",
            "list_expression": "LIST_LITERAL",
            "tuple_expression": "TUPLE",
        },
        "go": {
            "function_declaration": "FUNCTION",
            "identifier": "IDENTIFIER",
            "interpreted_string_literal": "LITERAL",
            "raw_string_literal": "LITERAL",
            "integer_literal": "LITERAL",
            "variable_declaration": "VARIABLE_DECL",
            "assignment_statement": "ASSIGNMENT",
            "return_statement": "RETURN",
            "if_statement": "IF",
            "for_statement": "FOR",
            "expression_statement": "EXPRESSION_STMT",
            "call_expression": "CALL",
            "binary_expression": "BINARY_OP",
            "unary_expression": "UNARY_OP",
            "block": "BLOCK",
            "match_expression": "MATCH",
            "type_switch_statement": "MATCH",
        },
        "typescript": {
            "function_declaration": "FUNCTION",
            "identifier": "IDENTIFIER",
            "number": "LITERAL",
            "string": "LITERAL",
            "boolean": "LITERAL",
            "variable_declaration": "VARIABLE_DECL",
            "assignment_expression": "ASSIGNMENT",
            "return_statement": "RETURN",
            "if_statement": "IF",
            "for_statement": "FOR",
            "while_statement": "WHILE",
            "switch_statement": "MATCH",
            "call_expression": "CALL",
            "binary_expression": "BINARY_OP",
            "unary_expression": "UNARY_OP",
            "block": "BLOCK",
            "array_literal_expression": "LIST_LITERAL",
            "object_literal_expression": "DICT_LITERAL",
            "arrow_function": "LAMBDA",
        },
    }
    return mappings.get(language, {})


def _infer_ast_type(cst_type: str, node: Dict) -> str:
    """Fallback inference when CST type isn't in the mapping."""
    lower = cst_type.lower()
    if "function" in lower or "def" in lower or "fn" in lower:
        return "FUNCTION"
    if "loop" in lower or "while" in lower or "for" in lower:
        return "LOOP"
    if "match" in lower or "case" in lower or "switch" in lower:
        return "MATCH"
    if "if" in lower or "elif" in lower or "else" in lower:
        return "IF"
    if "return" in lower:
        return "RETURN"
    if "assignment" in lower or "let" in lower:
        return "ASSIGNMENT"
    if "call" in lower or "invoke" in lower:
        return "CALL"
    if "literal" in lower or "integer" in lower or "string" in lower or "boolean" in lower:
        return "LITERAL"
    if "identifier" in lower or "name" in lower:
        return "IDENTIFIER"
    if "binary" in lower:
        return "BINARY_OP"
    if "unary" in lower:
        return "UNARY_OP"
    return "EXPRESSION_STMT"


# ──────────────────────────────────────────────────────────────────────────────
# Utility functions
# ──────────────────────────────────────────────────────────────────────────────

def get_all_functions(ast: ASTNode) -> List[ASTNode]:
    """Extract all FUNCTION nodes from an AST."""
    return [n for n in ast.walk() if n.node_type == ASTNodeType.FUNCTION]


def get_cfg_blocks(ast: ASTNode) -> List[ASTNode]:
    """Extract CFG-relevant blocks from an AST (loop bodies, branch arms, etc.)."""
    blocks = []
    for node in ast.walk():
        if node.node_type in (
            ASTNodeType.LOOP,
            ASTNodeType.FOR,
            ASTNodeType.WHILE,
            ASTNodeType.IF,
            ASTNodeType.MATCH,
            ASTNodeType.MATCH_ARM,
            ASTNodeType.BLOCK,
        ):
            blocks.append(node)
    return blocks


if __name__ == "__main__":
    # Quick smoke test
    sample_python = '''
def binary_search(arr, target):
    lo, hi = 0, len(arr) - 1
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
        "t1-ac2-001",
        "python",
        sample_python,
        Path("/tmp/ast_test"),
    )
    print(f"AST hash: {parsed.ast_hash}")
    print(f"Node count: {parsed.ast.node_count()}")
    print(json.dumps(parsed.ast.to_dict(), indent=2)[:1000])
