"""
Phase 1: Spec corpus definition.

Every spec has a unique ID, title, complexity tier (T1–T4),
algorithm class (AC1–AC4), and a formal semantic contract
with input/output examples and edge cases.

The corpus is versioned (specs_v1, specs_v2, ...) to ensure
reproducibility of the generation phase.
"""

from dataclasses import dataclass, field
from typing import List, Dict
from pathlib import Path

# ──────────────────────────────────────────────────────────────────────────────
# Spec metadata
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class Spec:
    id: str
    title: str
    description: str
    tier: str          # T1, T2, T3, T4
    algo_class: str    # AC1, AC2, AC3, AC4
    inputs: List[Dict]
    outputs: List[Dict]
    edge_cases: List[str]
    complexity_note: str = ""

    def to_markdown(self) -> str:
        """Render the spec as a markdown document for prompt injection."""
        return f"""## {self.id}: {self.title}

**Tier:** {self.tier} | **Algorithm Class:** {self.algo_class}

### Description
{self.description}

{self.complexity_note}

### Formal Contract

#### Inputs
{chr(10).join(f"- {inp}" for inp in self.inputs)}

#### Outputs
{chr(10).join(f"- {out}" for out in self.outputs)}

### Edge Cases
{chr(10).join(f"- {ec}" for ec in self.edge_cases)}

### Test Cases
(Generated per-language in Phase 1; tests must be semantically equivalent across all languages)
"""


# ──────────────────────────────────────────────────────────────────────────────
# Corpus — 20 specs, stratified across tiers and algorithm classes
# ──────────────────────────────────────────────────────────────────────────────

CORPUS: List[Spec] = [
    # ── T1 (5 specs) ──────────────────────────────────────────────────────
    Spec(
        id="t1-ac1-001",
        title="String Reverse",
        description="Reverse a string. For multi-byte characters (e.g. UTF-8), reverse codepoints, not bytes.",
        tier="T1", algo_class="AC1",
        inputs=[
            {"name": "s", "type": "string", "description": "input string"},
        ],
        outputs=[
            {"name": "result", "type": "string", "description": "reversed string"},
        ],
        edge_cases=[
            "Empty string → ''",
            "Single character → same character",
            "ASCII only",
            "Mixed ASCII and Unicode (e.g. 'héllo 世界')",
        ],
    ),
    Spec(
        id="t1-ac2-001",
        title="Binary Search",
        description="Given a sorted integer array and a target, return the index of the target, or -1 if not found.",
        tier="T1", algo_class="AC2",
        inputs=[
            {"name": "arr", "type": "list[int]", "description": "sorted integer array, ascending"},
            {"name": "target", "type": "int", "description": "value to search for"},
        ],
        outputs=[
            {"name": "result", "type": "int", "description": "index of target in arr, or -1"},
        ],
        edge_cases=[
            "Empty array → -1",
            "Single element, match → 0",
            "Single element, no match → -1",
            "Target not in array",
            "Target at first position",
            "Target at last position",
        ],
    ),
    Spec(
        id="t1-ac3-001",
        title="Factorial (Iterative)",
        description="Compute n! iteratively (n ≥ 0, n ≤ 20 to avoid overflow).",
        tier="T1", algo_class="AC3",
        inputs=[
            {"name": "n", "type": "int", "description": "non-negative integer, 0 ≤ n ≤ 20"},
        ],
        outputs=[
            {"name": "result", "type": "int", "description": "n factorial"},
        ],
        edge_cases=[
            "n = 0 → 1",
            "n = 1 → 1",
            "n = 20 → 2432902008176640000",
            "n < 0 → error/panic",
            "n > 20 → error/panic",
        ],
    ),
    Spec(
        id="t1-ac3-002",
        title="Fibonacci (Iterative)",
        description="Return the nth Fibonacci number (F(0)=0, F(1)=1, F(n)=F(n-1)+F(n-2)). Use iterative approach.",
        tier="T1", algo_class="AC3",
        inputs=[
            {"name": "n", "type": "int", "description": "non-negative integer, 0 ≤ n ≤ 45"},
        ],
        outputs=[
            {"name": "result", "type": "int", "description": "nth Fibonacci number"},
        ],
        edge_cases=[
            "n = 0 → 0",
            "n = 1 → 1",
            "n = 10 → 55",
        ],
    ),
    Spec(
        id="t1-ac4-001",
        title="Flatten a List",
        description="Given a list that may contain nested lists (arbitrary depth), return a flat list of all elements.",
        tier="T1", algo_class="AC4",
        inputs=[
            {"name": "lst", "type": "list", "description": "list possibly containing nested lists"},
        ],
        outputs=[
            {"name": "result", "type": "list", "description": "flattened list"},
        ],
        edge_cases=[
            "Empty list → []",
            "Already flat list → same list",
            "Deeply nested: [1, [2, [3, [4]]]] → [1, 2, 3, 4]",
            "Mixed types: [1, 'a', [2, [3.0]]] → [1, 'a', 2, 3.0]",
        ],
    ),

    # ── T2 (6 specs) ──────────────────────────────────────────────────────
    Spec(
        id="t2-ac1-001",
        title="Count Character Frequency",
        description="Count occurrences of each character in a string. Return as a map from character to count.",
        tier="T2", algo_class="AC1",
        inputs=[
            {"name": "s", "type": "string", "description": "input string"},
        ],
        outputs=[
            {"name": "counts", "type": "dict[str, int]", "description": "character → frequency map"},
        ],
        edge_cases=[
            "Empty string → {}",
            "All same character → {c: n}",
            "Mixed case: 'AaA' → treat as case-sensitive",
        ],
    ),
    Spec(
        id="t2-ac2-001",
        title="Breadth-First Search (BFS)",
        description="Given a graph (adjacency list) and a start node, return all reachable nodes in BFS order.",
        tier="T2", algo_class="AC2",
        inputs=[
            {"name": "graph", "type": "dict[int, list[int]]", "description": "adjacency list, node IDs are integers"},
            {"name": "start", "type": "int", "description": "starting node ID"},
        ],
        outputs=[
            {"name": "visited_order", "type": "list[int]", "description": "nodes visited in BFS order"},
        ],
        edge_cases=[
            "Empty graph (no edges) → [start]",
            "Single node, no edges → [start]",
            "Disconnected graph → only reachable nodes",
            "Cyclic graph → visited once per node",
        ],
    ),
    Spec(
        id="t2-ac2-002",
        title="Depth-First Search (DFS, Iterative)",
        description="Given a graph (adjacency list) and a start node, return all reachable nodes in DFS order (iterative, explicit stack).",
        tier="T2", algo_class="AC2",
        inputs=[
            {"name": "graph", "type": "dict[int, list[int]]", "description": "adjacency list"},
            {"name": "start", "type": "int", "description": "starting node ID"},
        ],
        outputs=[
            {"name": "visited_order", "type": "list[int]", "description": "nodes visited in DFS order"},
        ],
        edge_cases=[
            "Empty graph → [start]",
            "Cyclic graph → visited once per node",
        ],
    ),
    Spec(
        id="t2-ac3-001",
        title="Merge Sort",
        description="Sort a list of integers using merge sort. Return the sorted list.",
        tier="T2", algo_class="AC3",
        inputs=[
            {"name": "lst", "type": "list[int]", "description": "unsorted list of integers"},
        ],
        outputs=[
            {"name": "result", "type": "list[int]", "description": "sorted list, ascending"},
        ],
        edge_cases=[
            "Empty list → []",
            "Single element → [x]",
            "Already sorted → same list",
            "Reverse sorted → sorted",
            "All equal elements → same list",
        ],
    ),
    Spec(
        id="t2-ac3-002",
        title="Longest Common Subsequence (LCS)",
        description="Return the length of the longest common subsequence of two strings.",
        tier="T2", algo_class="AC3",
        inputs=[
            {"name": "s1", "type": "string", "description": "first string"},
            {"name": "s2", "type": "string", "description": "second string"},
        ],
        outputs=[
            {"name": "result", "type": "int", "description": "length of LCS"},
        ],
        edge_cases=[
            "Empty s1 or s2 → 0",
            "No common subsequence → 0",
            "Identical strings → len(s)",
            "'ABCBDAB', 'BDCAB' → 4 (BCAB or BDCB)",
        ],
    ),
    Spec(
        id="t2-ac4-001",
        title="Group By Key",
        description="Given a list of (key, value) tuples, group values by key. Return a dict mapping each key to the list of its values.",
        tier="T2", algo_class="AC4",
        inputs=[
            {"name": "pairs", "type": "list[tuple[str, int]]", "description": "list of (key, value) pairs"},
        ],
        outputs=[
            {"name": "result", "type": "dict[str, list[int]]", "description": "key → list of values"},
        ],
        edge_cases=[
            "Empty list → {}",
            "All keys same → single key with all values",
            "All keys distinct → each key has one value",
        ],
    ),

    # ── T3 (5 specs) ──────────────────────────────────────────────────────
    Spec(
        id="t3-ac2-001",
        title="AVL Tree Insert",
        description="Insert a key into an AVL tree. Return the (potentially rebalanced) tree root. Support search after insert.",
        tier="T3", algo_class="AC2",
        inputs=[
            {"name": "keys", "type": "list[int]", "description": "list of keys to insert in order"},
        ],
        outputs=[
            {"name": "root", "type": "Node", "description": "root of the AVL tree"},
            {"name": "heights", "type": "list[int]", "description": "in-order heights of nodes"},
        ],
        edge_cases=[
            "Insert into empty tree",
            "Insert already-existing key",
            "Single rotation (LL, RR)",
            "Double rotation (LR, RL)",
            "Insert in sorted order (worst case for naive BST)",
        ],
    ),
    Spec(
        id="t3-ac2-002",
        title="Binary Tree Level-Order Traversal",
        description="Given a binary tree root, return node values level by level (BFS, each level as a list).",
        tier="T3", algo_class="AC2",
        inputs=[
            {"name": "root", "type": "Node", "description": "root of binary tree (or None)"},
        ],
        outputs=[
            {"name": "result", "type": "list[list[int]]", "description": "levels of the tree"},
        ],
        edge_cases=[
            "Empty tree → []",
            "Single node → [[val]]",
            "Skewed tree (all left or all right)",
            "Complete binary tree",
        ],
    ),
    Spec(
        id="t3-ac3-001",
        title="0/1 Knapsack (Dynamic Programming)",
        description="Given n items with weights and values, and a capacity, return the maximum total value achievable.",
        tier="T3", algo_class="AC3",
        inputs=[
            {"name": "weights", "type": "list[int]", "description": "weights of n items"},
            {"name": "values", "type": "list[int]", "description": "values of n items"},
            {"name": "capacity", "type": "int", "description": "knapsack capacity"},
        ],
        outputs=[
            {"name": "max_value", "type": "int", "description": "maximum achievable value"},
        ],
        edge_cases=[
            "Empty items → 0",
            "Item too heavy alone → skip",
            "All items fit → sum of all values",
        ],
    ),
    Spec(
        id="t3-ac4-001",
        title="Word Count (Map-Reduce Style)",
        description="Given a list of strings, count word frequencies using a map-then-reduce pattern. Case-insensitive.",
        tier="T3", algo_class="AC4",
        inputs=[
            {"name": "lines", "type": "list[str]", "description": "list of input lines"},
        ],
        outputs=[
            {"name": "word_counts", "type": "dict[str, int]", "description": "word → total count"},
        ],
        edge_cases=[
            "Empty input → {}",
            "Punctuation: 'hello,' and 'hello' are different words",
            "Numbers as words: '123' counted as '123'",
        ],
    ),
    Spec(
        id="t3-ac4-002",
        title="Top-K Elements",
        description="Given a list of numbers and an integer k, return the k largest elements in descending order.",
        tier="T3", algo_class="AC4",
        inputs=[
            {"name": "lst", "type": "list[int]", "description": "input list"},
            {"name": "k", "type": "int", "description": "number of top elements to return, 0 < k ≤ len(lst)"},
        ],
        outputs=[
            {"name": "result", "type": "list[int]", "description": "k largest elements, descending"},
        ],
        edge_cases=[
            "k = 1 → [max(lst)]",
            "k = len(lst) → sorted descending",
            "All elements equal → all elements",
        ],
    ),

    # ── T4 (4 specs) ──────────────────────────────────────────────────────
    Spec(
        id="t4-ac4-001",
        title="Filter-Map-Reduce Pipeline",
        description="Given a list of integers, (1) filter to keep only positive numbers, (2) square each, (3) sum the results.",
        tier="T4", algo_class="AC4",
        inputs=[
            {"name": "lst", "type": "list[int]", "description": "input list"},
        ],
        outputs=[
            {"name": "result", "type": "int", "description": "sum of squares of positive numbers"},
        ],
        edge_cases=[
            "Empty list → 0",
            "All negative → 0",
            "Mix of positive, negative, zero",
            "All positive",
        ],
    ),
    Spec(
        id="t4-ac4-002",
        title="Parser: Arithmetic Expression Evaluator",
        description="Evaluate a simple arithmetic expression with +, -, *, / and integer precedence (multiply before add). Support parentheses. No unary minus.",
        tier="T4", algo_class="AC4",
        inputs=[
            {"name": "expr", "type": "string", "description": "arithmetic expression, e.g. '2 + 3 * 4'"},
        ],
        outputs=[
            {"name": "result", "type": "int", "description": "integer result"},
        ],
        edge_cases=[
            "'1 + 2 + 3' → 6",
            "'8 / 3' → integer division, 2",
            "'(1 + 2) * 3' → 9",
            "'1 * 2 + 3 * 4' → 14",
        ],
    ),
    Spec(
        id="t4-ac1-001",
        title="Anagram Detection",
        description="Given two strings, return True if they are anagrams of each other (same characters, same counts).",
        tier="T4", algo_class="AC1",
        inputs=[
            {"name": "s1", "type": "string", "description": "first string"},
            {"name": "s2", "type": "string", "description": "second string"},
        ],
        outputs=[
            {"name": "result", "type": "bool", "description": "True if anagrams, False otherwise"},
        ],
        edge_cases=[
            "'listen', 'silent' → True",
            "'hello', 'world' → False",
            "'aab', 'aba' → True",
            "Case sensitivity: 'Listen', 'Silent' → False (strict)",
            "Empty strings → True",
        ],
    ),
    Spec(
        id="t4-ac4-003",
        title="Compose N Functions",
        description="Given a list of unary functions [f1, f2, ..., fn] and a value x, return f_n(...f_2(f_1(x))...). Apply in left-to-right order.",
        tier="T4", algo_class="AC4",
        inputs=[
            {"name": "funcs", "type": "list[callable]", "description": "list of unary functions (Python), closures or lambdas"},
            {"name": "x", "type": "int", "description": "initial value"},
        ],
        outputs=[
            {"name": "result", "type": "int", "description": "composition result"},
        ],
        edge_cases=[
            "Empty function list → x",
            "Single function → f(x)",
            "Identity functions",
        ],
    ),
]


def get_spec_by_id(spec_id: str) -> Spec:
    for spec in CORPUS:
        if spec.id == spec_id:
            return spec
    raise ValueError(f"Unknown spec ID: {spec_id}")


def specs_by_tier(tier: str) -> List[Spec]:
    return [s for s in CORPUS if s.tier == tier]


def specs_by_algo_class(ac: str) -> List[Spec]:
    return [s for s in CORPUS if s.algo_class == ac]


# ──────────────────────────────────────────────────────────────────────────────
# Corpus version info
# ──────────────────────────────────────────────────────────────────────────────

CORPUS_VERSION = "v1"
CORPUS_TIMESTAMP = "2026-08-08"

# Language list (ordered as in PREREGISTRATION.md)
LANGUAGES = ["python", "rust", "haskell", "ocaml", "go", "typescript"]


if __name__ == "__main__":
    print(f"Corpus: {CORPUS_VERSION} — {len(CORPUS)} specs")
    for tier in ["T1", "T2", "T3", "T4"]:
        specs = specs_by_tier(tier)
        print(f"  {tier}: {len(specs)} specs")
        for s in specs:
            print(f"    {s.id}: {s.title}")
