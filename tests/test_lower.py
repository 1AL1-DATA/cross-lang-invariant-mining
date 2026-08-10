"""Unit tests for lower.py"""
import pytest
from lower import (
    IRNode, IRNodeType, ast_to_ir, lower_implementation,
    DataFlowGraph, GranularityLevel, get_ir_subgraphs,
)
from parse import ASTNode, ASTNodeType, ParsedImplementation


def test_ir_hash_deterministic():
    ir1 = IRNode(ir_type=IRNodeType.FUNCTION, label="foo", body=[])
    ir2 = IRNode(ir_type=IRNodeType.FUNCTION, label="foo", body=[])
    assert ir1.ir_hash() == ir2.ir_hash()


def test_ir_hash_different():
    ir1 = IRNode(ir_type=IRNodeType.FUNCTION, label="foo", body=[])
    ir2 = IRNode(ir_type=IRNodeType.FUNCTION, label="bar", body=[])
    assert ir1.ir_hash() != ir2.ir_hash()


def test_ir_node_count():
    ir = IRNode(ir_type=IRNodeType.SEQUENCE, body=[
        IRNode(ir_type=IRNodeType.LITERAL, value="1"),
        IRNode(ir_type=IRNodeType.LITERAL, value="2"),
    ])
    assert ir.node_count() == 3  # 1 root + 2 children


def test_get_ir_subgraphs_l4():
    ir = IRNode(ir_type=IRNodeType.FUNCTION, body=[
        IRNode(ir_type=IRNodeType.LITERAL, value="x"),
    ])
    subs = get_ir_subgraphs(ir, GranularityLevel.L4)
    assert len(subs) == 1
    assert subs[0] == ir


def test_get_ir_subgraphs_l3():
    ir = IRNode(ir_type=IRNodeType.FUNCTION, body=[
        IRNode(ir_type=IRNodeType.LOOP, body=[
            IRNode(ir_type=IRNodeType.BRANCH, body=[])
        ])
    ])
    subs = get_ir_subgraphs(ir, GranularityLevel.L3)
    types = {s.ir_type for s in subs}
    assert IRNodeType.LOOP in types


def test_dataflow_graph():
    ir = IRNode(
        ir_type=IRNodeType.FUNCTION,
        body=[
            IRNode(ir_type=IRNodeType.ASSIGN, value="x",
                   body=[
                       IRNode(ir_type=IRNodeType.LITERAL, value="1"),
                   ]),
        ]
    )
    df = DataFlowGraph.from_ir(ir)
    assert isinstance(df, DataFlowGraph)


def test_ir_serialization_roundtrip():
    ir = IRNode(ir_type=IRNodeType.FUNCTION, label="test", body=[
        IRNode(ir_type=IRNodeType.ASSIGN, value="y",
               body=[IRNode(ir_type=IRNodeType.LITERAL, value="42")]),
    ])
    import json
    serialized = json.dumps(ir.to_dict(), sort_keys=True)
    restored = IRNode.from_dict(json.loads(serialized))
    assert restored.ir_type == ir.ir_type
    assert restored.label == ir.label
    assert restored.ir_hash() == ir.ir_hash()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
