# Copyright 2026 Roderick Consulting Inc.
# Licensed under the Apache License, Version 2.0.
"""Schema tests for v0.2.0 changes: relaxed BF-tape completeness, new ops, new encodings.

The strict pre-v0.2.0 rule was "a brainfuck_tape language must define all 8
canonical ops". The relaxed rule (per research-notes/interpreter-candidates-2026-05-17.md)
is: pointer mobility + cell modification + balanced loops. I/O optional.
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from babel.schema import (
    BaseMachine,
    Encoding,
    Instruction,
    InstructionOp,
    LanguageSpec,
    MemoryShape,
)


def _spec(ops: list[tuple[str, InstructionOp]], **overrides) -> LanguageSpec:
    """Build a minimal LanguageSpec from (token, op) pairs."""
    return LanguageSpec(
        name=overrides.pop("name", "test-lang"),
        base_machine=overrides.pop("base_machine", BaseMachine.BRAINFUCK_TAPE),
        memory_shape=overrides.pop("memory_shape", MemoryShape.TAPE_1D_UNBOUNDED),
        encoding=overrides.pop("encoding", Encoding.ASCII_PUNCTUATION),
        instructions=[Instruction(token=t, op=o) for t, o in ops],
        **overrides,
    )


# ---------------------------------------------------------------------------
# Relaxed completeness: legitimate subsets now validate
# ---------------------------------------------------------------------------


def test_boolfuck_style_subset_validates() -> None:
    """Boolfuck-style: no DECREMENT (+ toggles), 7 ops total. Should validate."""
    spec = _spec(
        [
            ("+", InstructionOp.INCREMENT),  # toggle
            ("<", InstructionOp.PTR_LEFT),
            (">", InstructionOp.PTR_RIGHT),
            (";", InstructionOp.OUTPUT),
            (",", InstructionOp.INPUT),
            ("[", InstructionOp.LOOP_START),
            ("]", InstructionOp.LOOP_END),
        ]
    )
    assert {i.op for i in spec.instructions} == {
        InstructionOp.INCREMENT,
        InstructionOp.PTR_LEFT,
        InstructionOp.PTR_RIGHT,
        InstructionOp.OUTPUT,
        InstructionOp.INPUT,
        InstructionOp.LOOP_START,
        InstructionOp.LOOP_END,
    }


def test_smallfuck_style_subset_validates() -> None:
    """Smallfuck-style: 5 ops, no I/O at all. Should validate."""
    spec = _spec(
        [
            ("*", InstructionOp.INCREMENT),  # toggle
            ("<", InstructionOp.PTR_LEFT),
            (">", InstructionOp.PTR_RIGHT),
            ("[", InstructionOp.LOOP_START),
            ("]", InstructionOp.LOOP_END),
        ]
    )
    assert InstructionOp.OUTPUT not in {i.op for i in spec.instructions}
    assert InstructionOp.INPUT not in {i.op for i in spec.instructions}


def test_canonical_eight_still_validates() -> None:
    """The full canonical 8-op set still works (backward compatibility)."""
    spec = _spec(
        [
            (">", InstructionOp.PTR_RIGHT),
            ("<", InstructionOp.PTR_LEFT),
            ("+", InstructionOp.INCREMENT),
            ("-", InstructionOp.DECREMENT),
            (".", InstructionOp.OUTPUT),
            (",", InstructionOp.INPUT),
            ("[", InstructionOp.LOOP_START),
            ("]", InstructionOp.LOOP_END),
        ]
    )
    assert len(spec.instructions) == 8


# ---------------------------------------------------------------------------
# Minimum bar: rejections for under-specified languages
# ---------------------------------------------------------------------------


def test_no_mobility_op_rejected() -> None:
    """A spec without PTR_LEFT or PTR_RIGHT must fail (can't reach other cells)."""
    with pytest.raises(ValidationError, match="pointer-moving op"):
        _spec(
            [
                ("+", InstructionOp.INCREMENT),
                ("-", InstructionOp.DECREMENT),
                ("[", InstructionOp.LOOP_START),
                ("]", InstructionOp.LOOP_END),
            ]
        )


def test_no_cell_modifying_op_rejected() -> None:
    """A spec without any cell-modifying op must fail (program would be a no-op)."""
    with pytest.raises(ValidationError, match="cell-modifying op"):
        _spec(
            [
                (">", InstructionOp.PTR_RIGHT),
                ("<", InstructionOp.PTR_LEFT),
                ("[", InstructionOp.LOOP_START),
                ("]", InstructionOp.LOOP_END),
            ]
        )


def test_unbalanced_loops_rejected() -> None:
    """LOOP_START without LOOP_END must fail (parser would fail on bracket-matching)."""
    with pytest.raises(ValidationError, match="LOOP_START and LOOP_END"):
        _spec(
            [
                (">", InstructionOp.PTR_RIGHT),
                ("+", InstructionOp.INCREMENT),
                ("[", InstructionOp.LOOP_START),
            ]
        )


def test_loops_optional_when_neither_present() -> None:
    """If both LOOP_START and LOOP_END are absent, the spec validates (linear program)."""
    spec = _spec(
        [
            (">", InstructionOp.PTR_RIGHT),
            ("+", InstructionOp.INCREMENT),
            (".", InstructionOp.OUTPUT),
        ]
    )
    assert InstructionOp.LOOP_START not in {i.op for i in spec.instructions}


# ---------------------------------------------------------------------------
# New v0.2.0 ops are legal on a tape machine
# ---------------------------------------------------------------------------


def test_halt_op_legal_on_tape() -> None:
    """HALT is in the tape-legal set; specs may include it."""
    spec = _spec(
        [
            (">", InstructionOp.PTR_RIGHT),
            ("<", InstructionOp.PTR_LEFT),
            ("+", InstructionOp.INCREMENT),
            ("-", InstructionOp.DECREMENT),
            (".", InstructionOp.OUTPUT),
            (",", InstructionOp.INPUT),
            ("[", InstructionOp.LOOP_START),
            ("]", InstructionOp.LOOP_END),
            ("h", InstructionOp.HALT),
        ]
    )
    assert InstructionOp.HALT in {i.op for i in spec.instructions}


def test_break_loop_and_jump_unconditional_legal_on_tape() -> None:
    """BREAK_LOOP and JUMP_UNCONDITIONAL are schema-legal (interpreter raises until implemented)."""
    spec = _spec(
        [
            (">", InstructionOp.PTR_RIGHT),
            ("<", InstructionOp.PTR_LEFT),
            ("+", InstructionOp.INCREMENT),
            ("-", InstructionOp.DECREMENT),
            ("[", InstructionOp.LOOP_START),
            ("]", InstructionOp.LOOP_END),
            ("b", InstructionOp.BREAK_LOOP),
            ("j", InstructionOp.JUMP_UNCONDITIONAL),
        ]
    )
    ops = {i.op for i in spec.instructions}
    assert InstructionOp.BREAK_LOOP in ops
    assert InstructionOp.JUMP_UNCONDITIONAL in ops


# ---------------------------------------------------------------------------
# New v0.2.0 encodings are schema-legal
# ---------------------------------------------------------------------------


def test_variable_length_binary_encoding_validates() -> None:
    """Spoon-style variable-length-binary encoding validates."""
    spec = _spec(
        [
            ("010", InstructionOp.PTR_RIGHT),
            ("011", InstructionOp.PTR_LEFT),
            ("1", InstructionOp.INCREMENT),
            ("000", InstructionOp.DECREMENT),
            ("00101", InstructionOp.OUTPUT),
            ("00100", InstructionOp.INPUT),
            ("00110", InstructionOp.LOOP_START),
            ("00111", InstructionOp.LOOP_END),
        ],
        encoding=Encoding.VARIABLE_LENGTH_BINARY,
    )
    assert spec.encoding == Encoding.VARIABLE_LENGTH_BINARY


def test_word_length_dispatch_encoding_validates() -> None:
    """Wordfuck-style word-length-dispatch encoding validates."""
    spec = _spec(
        [
            ("a", InstructionOp.INCREMENT),
            ("ab", InstructionOp.DECREMENT),
            ("abc", InstructionOp.PTR_RIGHT),
            ("abcd", InstructionOp.PTR_LEFT),
            ("abcde", InstructionOp.OUTPUT),
            ("abcdef", InstructionOp.INPUT),
            ("abcdefg", InstructionOp.LOOP_START),
            ("abcdefgh", InstructionOp.LOOP_END),
        ],
        encoding=Encoding.WORD_LENGTH_DISPATCH,
    )
    assert spec.encoding == Encoding.WORD_LENGTH_DISPATCH
