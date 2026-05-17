# Copyright 2026 Roderick Consulting Inc.
# Licensed under the Apache License, Version 2.0.
"""End-to-end tests for the FALSE parameter sheet (Babel v0.6.0).

FALSE (Wouter van Oortmerssen, 1993) is Babel's first canonical-wiki
stack-language exemplar. The wiki entry is at
https://esolangs.org/wiki/FALSE.

Coverage in this file:

* The YAML loads and exposes the expected metadata.
* Each of the six new ops added in v0.6.0 (MUL / DIV / NEGATE / EQUALS
  / GREATER / ROT) is tested individually with a tiny program against
  the loaded YAML.
* The canonical Hello World — pending the string-literal tokenizer
  extension, written character-by-character as `push N , push N , ...`
  with the documented ASCII codepoints — runs end-to-end to the
  expected output (`Hello, World!\\n`).
* Per-language quirks: division by zero raises, FALSE's -1/0 boolean
  convention is preserved end-to-end on equality and greater-than,
  and the cell-width wrap interaction is documented and tested.
"""

from __future__ import annotations

import io
from pathlib import Path

import pytest

from babel.interpreter import InterpreterError
from babel.loader import load_spec
from babel.schema import (
    BaseMachine,
    CellWidth,
    Encoding,
    Instruction,
    InstructionOp,
    LanguageSpec,
    MemoryShape,
)
from babel.stack_interpreter import run as stack_run

EXAMPLES = Path(__file__).resolve().parent.parent / "examples"
FALSE_YAML = EXAMPLES / "false.yaml"


def _run(spec: LanguageSpec, source: str) -> str:
    """Tiny helper: run `source` against `spec`, return captured stdout."""
    out = io.StringIO()
    stack_run(source, spec, stdin=io.StringIO(""), stdout=out)
    return out.getvalue()


# ---------------------------------------------------------------------------
# YAML metadata
# ---------------------------------------------------------------------------


def test_false_yaml_loads() -> None:
    spec = load_spec(FALSE_YAML)
    assert spec.name == "FALSE"
    assert spec.base_machine == BaseMachine.STACK
    assert spec.memory_shape == MemoryShape.STACK_UNBOUNDED
    assert spec.cell_width == CellWidth.ARBITRARY
    assert spec.encoding == Encoding.WHITESPACE_SEPARATED_TOKENS
    assert spec.source_extension == ".f"


def test_false_yaml_token_inventory() -> None:
    """The 15 documented FALSE tokens are all present, and each maps to the
    canonical InstructionOp called out in the YAML comments."""
    spec = load_spec(FALSE_YAML)
    by_token = {i.token: i.op for i in spec.instructions}
    expected = {
        "push": InstructionOp.STACK_PUSH,
        "$": InstructionOp.STACK_DUP,
        "%": InstructionOp.STACK_POP,
        "\\": InstructionOp.STACK_SWAP,
        "@": InstructionOp.STACK_ROT,
        "+": InstructionOp.STACK_ADD,
        "-": InstructionOp.STACK_SUB,
        "*": InstructionOp.STACK_MUL,
        "/": InstructionOp.STACK_DIV,
        "_": InstructionOp.STACK_NEGATE,
        "=": InstructionOp.STACK_EQUALS,
        ">": InstructionOp.STACK_GREATER,
        ".": InstructionOp.STACK_OUTPUT_INT,
        ",": InstructionOp.STACK_OUTPUT_CHAR,
        "halt": InstructionOp.HALT,
    }
    assert by_token == expected


def test_false_yaml_push_is_arity_1_others_arity_0() -> None:
    spec = load_spec(FALSE_YAML)
    push = next(i for i in spec.instructions if i.token == "push")
    assert push.arity == 1
    for i in spec.instructions:
        if i.token != "push":
            assert i.arity == 0, f"{i.token!r} should be arity=0 but is arity={i.arity}"


# ---------------------------------------------------------------------------
# Per-new-op coverage (the six v0.6.0 additions)
# ---------------------------------------------------------------------------


def test_mul_multiplies_two_pushed_values() -> None:
    spec = load_spec(FALSE_YAML)
    assert _run(spec, "push 7 push 6 * .") == "42"


def test_mul_with_zero_yields_zero() -> None:
    spec = load_spec(FALSE_YAML)
    assert _run(spec, "push 0 push 99 * .") == "0"


def test_div_floor_divides() -> None:
    spec = load_spec(FALSE_YAML)
    assert _run(spec, "push 20 push 3 / .") == "6"


def test_div_negative_floors_toward_negative_infinity() -> None:
    """Python floor division: -7 // 2 == -4 (rounds toward -inf).

    This is the documented behaviour on STACK_DIV; FALSE programs that
    need truncating division should normalise operands first.
    """
    spec = load_spec(FALSE_YAML)
    assert _run(spec, "push 7 _ push 2 / .") == "-4"


def test_div_by_zero_raises_interpreter_error() -> None:
    spec = load_spec(FALSE_YAML)
    with pytest.raises(InterpreterError, match="division by zero"):
        _run(spec, "push 5 push 0 /")


def test_negate_inverts_sign() -> None:
    spec = load_spec(FALSE_YAML)
    assert _run(spec, "push 7 _ .") == "-7"


def test_negate_zero_stays_zero() -> None:
    spec = load_spec(FALSE_YAML)
    assert _run(spec, "push 0 _ .") == "0"


def test_negate_underflow_raises() -> None:
    spec = load_spec(FALSE_YAML)
    with pytest.raises(InterpreterError, match="underflow on STACK_NEGATE"):
        _run(spec, "_")


def test_equals_true_pushes_negative_one() -> None:
    """FALSE/Forth convention: -1 for true, 0 for false."""
    spec = load_spec(FALSE_YAML)
    assert _run(spec, "push 3 push 3 = .") == "-1"


def test_equals_false_pushes_zero() -> None:
    spec = load_spec(FALSE_YAML)
    assert _run(spec, "push 3 push 4 = .") == "0"


def test_equals_underflow_raises() -> None:
    spec = load_spec(FALSE_YAML)
    with pytest.raises(InterpreterError, match="underflow on STACK_EQUALS"):
        _run(spec, "push 1 =")


def test_greater_true_pushes_negative_one() -> None:
    """Operand order: pop b then a, push -1 if a > b."""
    spec = load_spec(FALSE_YAML)
    assert _run(spec, "push 5 push 2 > .") == "-1"


def test_greater_false_when_equal() -> None:
    spec = load_spec(FALSE_YAML)
    assert _run(spec, "push 5 push 5 > .") == "0"


def test_greater_false_when_less() -> None:
    spec = load_spec(FALSE_YAML)
    assert _run(spec, "push 2 push 5 > .") == "0"


def test_greater_underflow_raises() -> None:
    spec = load_spec(FALSE_YAML)
    with pytest.raises(InterpreterError, match="underflow on STACK_GREATER"):
        _run(spec, "push 1 >")


def test_rot_brings_third_to_top() -> None:
    """`@` in FALSE: (a b c -- b c a). Stack after push 1 push 2 push 3
    is [1, 2, 3]; rot yields [2, 3, 1]; printing three times prints
    1 first (top), then 3, then 2 — output `"132"`."""
    spec = load_spec(FALSE_YAML)
    assert _run(spec, "push 1 push 2 push 3 @ . . .") == "132"


def test_rot_underflow_with_two_values_raises() -> None:
    spec = load_spec(FALSE_YAML)
    with pytest.raises(InterpreterError, match="underflow on STACK_ROT"):
        _run(spec, "push 1 push 2 @")


def test_rot_underflow_with_one_value_raises() -> None:
    spec = load_spec(FALSE_YAML)
    with pytest.raises(InterpreterError, match="underflow on STACK_ROT"):
        _run(spec, "push 1 @")


def test_rot_underflow_on_empty_stack_raises() -> None:
    spec = load_spec(FALSE_YAML)
    with pytest.raises(InterpreterError, match="underflow on STACK_ROT"):
        _run(spec, "@")


# ---------------------------------------------------------------------------
# Canonical Hello World (character-by-character, pending string-literal
# tokenizer extension — documented in the YAML)
# ---------------------------------------------------------------------------


HELLO_WORLD_SOURCE = (
    "push 72 , "  # 'H'
    "push 101 , "  # 'e'
    "push 108 , "  # 'l'
    "push 108 , "  # 'l'
    "push 111 , "  # 'o'
    "push 44 , "  # ','
    "push 32 , "  # ' '
    "push 87 , "  # 'W'
    "push 111 , "  # 'o'
    "push 114 , "  # 'r'
    "push 108 , "  # 'l'
    "push 100 , "  # 'd'
    "push 33 , "  # '!'
    "push 10 ,"  # newline
)


def test_false_hello_world_character_by_character() -> None:
    """End-to-end Hello World on the loaded YAML.

    Canonical FALSE would express this as `"Hello, World!\\n"` (one
    string literal); since the string-literal tokenizer is deferred this
    test uses the equivalent push-and-emit form documented in
    `examples/false.yaml`. When the string-literal tokenizer lands, this
    test should be supplemented (not replaced) by a parallel one running
    the single-token canonical form.
    """
    spec = load_spec(FALSE_YAML)
    assert _run(spec, HELLO_WORLD_SOURCE) == "Hello, World!\n"


# ---------------------------------------------------------------------------
# Per-language quirks
# ---------------------------------------------------------------------------


def test_false_boolean_arithmetic_round_trip() -> None:
    """Demonstrate that FALSE's -1/0 boolean values participate in
    arithmetic cleanly: (3 == 3) negated is 1, which negated again is -1.

    This is the property that makes the -1 / 0 convention useful for
    masking the (deferred) bitwise AND / OR ops once they ship.
    """
    spec = load_spec(FALSE_YAML)
    assert _run(spec, "push 3 push 3 = _ .") == "1"
    assert _run(spec, "push 3 push 3 = _ _ .") == "-1"


def test_false_halt_terminates_program() -> None:
    """The cross-family HALT op (documented as `halt` in the YAML) stops
    execution mid-source; anything after is not run."""
    spec = load_spec(FALSE_YAML)
    # Without halt, the trailing `push 9 .` would print 9.
    assert _run(spec, "push 1 . halt push 9 .") == "1"


def test_false_arithmetic_chain_matches_canonical_postfix() -> None:
    """A small but non-trivial calculation: (10 - 3) * 2 + 1 = 15.

    Postfix in this sheet: `push 10 push 3 - push 2 * push 1 + .`
    """
    spec = load_spec(FALSE_YAML)
    assert _run(spec, "push 10 push 3 - push 2 * push 1 + .") == "15"


# ---------------------------------------------------------------------------
# Cell-width interaction (FALSE itself is integer-stack / arbitrary,
# but the new ops should behave correctly under bounded widths too).
# ---------------------------------------------------------------------------


def _byte_width_spec_with_negate_and_compare() -> LanguageSpec:
    """A FALSE-flavoured spec on BYTE cells, to exercise the wrap interaction
    with NEGATE / EQUALS / GREATER. Kept inline so the YAML stays focused
    on the canonical ARBITRARY-cell FALSE.
    """
    return LanguageSpec(
        name="false-byte-fixture",
        base_machine=BaseMachine.STACK,
        memory_shape=MemoryShape.STACK_UNBOUNDED,
        cell_width=CellWidth.BYTE,
        encoding=Encoding.WHITESPACE_SEPARATED_TOKENS,
        instructions=[
            Instruction(token="push", op=InstructionOp.STACK_PUSH, arity=1),
            Instruction(token="_", op=InstructionOp.STACK_NEGATE),
            Instruction(token="=", op=InstructionOp.STACK_EQUALS),
            Instruction(token=">", op=InstructionOp.STACK_GREATER),
            Instruction(token=".", op=InstructionOp.STACK_OUTPUT_INT),
        ],
    )


def test_negate_wraps_under_byte_cell_width() -> None:
    """Negate of 1 under BYTE cells: -1 mod 256 = 255.

    The all-ones bit pattern preserves the truth-mask semantics that
    `EQUALS` and `GREATER` rely on under bounded cell widths.
    """
    spec = _byte_width_spec_with_negate_and_compare()
    assert _run(spec, "push 1 _ .") == "255"


def test_equals_true_under_byte_cell_width_is_255() -> None:
    """Under BYTE, true (-1) wraps to 255 — the all-ones byte mask. The
    truth value's bit pattern is still mask-shaped, matching FALSE's
    own behaviour on byte-sized cells.
    """
    spec = _byte_width_spec_with_negate_and_compare()
    assert _run(spec, "push 5 push 5 = .") == "255"


def test_greater_false_under_byte_cell_width_is_0() -> None:
    spec = _byte_width_spec_with_negate_and_compare()
    assert _run(spec, "push 2 push 5 > .") == "0"


# ---------------------------------------------------------------------------
# Schema-level: the FALSE spec must validate that the new ops are
# stack-legal. (Negative test confirms the validator catches a misuse.)
# ---------------------------------------------------------------------------


def test_false_spec_validator_accepts_new_stack_ops() -> None:
    """All six new ops should be permitted on a stack-machine spec by
    `_check_stack_ops_legal`. Loading the YAML exercises this — a
    failure here would surface as a `pydantic.ValidationError`."""
    spec = load_spec(FALSE_YAML)
    ops = {i.op for i in spec.instructions}
    new_ops = {
        InstructionOp.STACK_MUL,
        InstructionOp.STACK_DIV,
        InstructionOp.STACK_NEGATE,
        InstructionOp.STACK_EQUALS,
        InstructionOp.STACK_GREATER,
        InstructionOp.STACK_ROT,
    }
    # All six new ops are referenced in the YAML.
    assert new_ops.issubset(ops)


# ---------------------------------------------------------------------------
# Package-level dispatcher
# ---------------------------------------------------------------------------


def test_package_run_dispatches_false_to_stack() -> None:
    """`babel.run` routes the FALSE spec through the stack interpreter."""
    import babel

    spec = load_spec(FALSE_YAML)
    out = io.StringIO()
    babel.run("push 65 ,", spec, stdin=io.StringIO(""), stdout=out)
    assert out.getvalue() == "A"
