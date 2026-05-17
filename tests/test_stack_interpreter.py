# Copyright 2026 Roderick Consulting Inc.
# Licensed under the Apache License, Version 2.0.
"""End-to-end tests for the stack-machine interpreter (Babel v0.4.0).

Covers the new `babel.stack_interpreter` module, the package-level
dispatcher in `babel.run`, and the `examples/minimal-stack.yaml`
parameter sheet that ships with the release.
"""

from __future__ import annotations

import io
from pathlib import Path

import pytest

import babel
from babel.interpreter import InterpreterError, ParseError
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


def _minimal_stack_spec() -> LanguageSpec:
    """Build the same spec the YAML ships, but inline for ops/tokenizer tests.

    Mirrors `examples/minimal-stack.yaml`. Kept as a Python fixture so the
    interpreter tests run even if the YAML grows or is re-themed later.
    """
    return LanguageSpec(
        name="minimal-stack-fixture",
        base_machine=BaseMachine.STACK,
        memory_shape=MemoryShape.STACK_UNBOUNDED,
        cell_width=CellWidth.ARBITRARY,
        encoding=Encoding.WHITESPACE_SEPARATED_TOKENS,
        instructions=[
            Instruction(token="push", op=InstructionOp.STACK_PUSH, arity=1),
            Instruction(token="pop", op=InstructionOp.STACK_POP),
            Instruction(token="dup", op=InstructionOp.STACK_DUP),
            Instruction(token="swap", op=InstructionOp.STACK_SWAP),
            Instruction(token="add", op=InstructionOp.STACK_ADD),
            Instruction(token="sub", op=InstructionOp.STACK_SUB),
            Instruction(token="emit", op=InstructionOp.STACK_OUTPUT_CHAR),
            Instruction(token="print", op=InstructionOp.STACK_OUTPUT_INT),
        ],
    )


# ---------------------------------------------------------------------------
# Basic execution
# ---------------------------------------------------------------------------


def test_empty_program_runs_to_completion() -> None:
    spec = _minimal_stack_spec()
    out = io.StringIO()
    stack_run("", spec, stdin=io.StringIO(""), stdout=out)
    assert out.getvalue() == ""


def test_whitespace_only_program_runs_to_completion() -> None:
    """Whitespace-only source is the same as empty; should not error."""
    spec = _minimal_stack_spec()
    out = io.StringIO()
    stack_run("   \n\t  ", spec, stdin=io.StringIO(""), stdout=out)
    assert out.getvalue() == ""


def test_push_emit_writes_ascii_char() -> None:
    spec = _minimal_stack_spec()
    out = io.StringIO()
    stack_run("push 65 emit", spec, stdin=io.StringIO(""), stdout=out)
    assert out.getvalue() == "A"


def test_add_sums_two_pushed_values() -> None:
    """5 + 3 = 8 = backspace ('\\x08')."""
    spec = _minimal_stack_spec()
    out = io.StringIO()
    stack_run("push 5 push 3 add emit", spec, stdin=io.StringIO(""), stdout=out)
    assert out.getvalue() == "\x08"


def test_dup_then_add_doubles_top() -> None:
    """1 dup add → 2."""
    spec = _minimal_stack_spec()
    out = io.StringIO()
    stack_run("push 1 dup add emit", spec, stdin=io.StringIO(""), stdout=out)
    assert out.getvalue() == "\x02"


def test_sub_uses_second_minus_top() -> None:
    """10 - 3 = 7 (operand order documented on STACK_SUB)."""
    spec = _minimal_stack_spec()
    out = io.StringIO()
    stack_run("push 10 push 3 sub print", spec, stdin=io.StringIO(""), stdout=out)
    assert out.getvalue() == "7"


def test_swap_reorders_top_two() -> None:
    """push 10 push 3 swap sub print → 10 - 3 swapped to 3 - 10 = -7."""
    spec = _minimal_stack_spec()
    out = io.StringIO()
    stack_run(
        "push 10 push 3 swap sub print", spec, stdin=io.StringIO(""), stdout=out
    )
    assert out.getvalue() == "-7"


def test_pop_discards_top() -> None:
    """push 99 push 7 pop print → 99 (the 7 was popped)."""
    spec = _minimal_stack_spec()
    out = io.StringIO()
    stack_run("push 99 push 7 pop print", spec, stdin=io.StringIO(""), stdout=out)
    assert out.getvalue() == "99"


# ---------------------------------------------------------------------------
# Error surfaces
# ---------------------------------------------------------------------------


def test_pop_on_empty_stack_raises_interpreter_error() -> None:
    spec = _minimal_stack_spec()
    out = io.StringIO()
    with pytest.raises(InterpreterError, match="underflow"):
        stack_run("pop", spec, stdin=io.StringIO(""), stdout=out)


def test_emit_on_empty_stack_raises_interpreter_error() -> None:
    spec = _minimal_stack_spec()
    out = io.StringIO()
    with pytest.raises(InterpreterError, match="underflow"):
        stack_run("emit", spec, stdin=io.StringIO(""), stdout=out)


def test_swap_with_one_element_raises_interpreter_error() -> None:
    spec = _minimal_stack_spec()
    out = io.StringIO()
    with pytest.raises(InterpreterError, match="underflow"):
        stack_run("push 1 swap", spec, stdin=io.StringIO(""), stdout=out)


def test_malformed_push_operand_raises_parse_error() -> None:
    """`push hello` — the operand isn't parseable as int."""
    spec = _minimal_stack_spec()
    out = io.StringIO()
    with pytest.raises(ParseError, match="not a valid integer"):
        stack_run("push hello", spec, stdin=io.StringIO(""), stdout=out)


def test_push_missing_operand_raises_parse_error() -> None:
    """`push` at end of source has no operand atom to consume."""
    spec = _minimal_stack_spec()
    out = io.StringIO()
    with pytest.raises(ParseError, match="arity=1"):
        stack_run("push", spec, stdin=io.StringIO(""), stdout=out)


def test_unknown_token_raises_parse_error() -> None:
    spec = _minimal_stack_spec()
    out = io.StringIO()
    with pytest.raises(ParseError, match="unknown token"):
        stack_run("push 1 banana", spec, stdin=io.StringIO(""), stdout=out)


def test_max_steps_caps_execution() -> None:
    spec = _minimal_stack_spec()
    out = io.StringIO()
    with pytest.raises(InterpreterError, match="max_steps"):
        stack_run(
            "push 1 push 1 push 1 push 1 push 1",
            spec,
            stdin=io.StringIO(""),
            stdout=out,
            max_steps=2,
        )


def test_stack_run_rejects_non_stack_spec() -> None:
    """`stack_interpreter.run` must reject a tape spec with a clear error."""
    bf_spec = LanguageSpec(
        name="bf-test",
        base_machine=BaseMachine.BRAINFUCK_TAPE,
        memory_shape=MemoryShape.TAPE_1D_UNBOUNDED,
        encoding=Encoding.ASCII_PUNCTUATION,
        instructions=[
            Instruction(token=">", op=InstructionOp.PTR_RIGHT),
            Instruction(token="<", op=InstructionOp.PTR_LEFT),
            Instruction(token="+", op=InstructionOp.INCREMENT),
            Instruction(token=".", op=InstructionOp.OUTPUT),
        ],
    )
    out = io.StringIO()
    with pytest.raises(InterpreterError, match="base_machine=stack"):
        stack_run("+.", bf_spec, stdin=io.StringIO(""), stdout=out)


# ---------------------------------------------------------------------------
# Bounded stack
# ---------------------------------------------------------------------------


def test_bounded_stack_overflow_raises() -> None:
    spec = LanguageSpec(
        name="bounded-test",
        base_machine=BaseMachine.STACK,
        memory_shape=MemoryShape.STACK_BOUNDED,
        cell_width=CellWidth.ARBITRARY,
        encoding=Encoding.WHITESPACE_SEPARATED_TOKENS,
        instructions=[
            Instruction(token="push", op=InstructionOp.STACK_PUSH, arity=1),
            Instruction(token="print", op=InstructionOp.STACK_OUTPUT_INT),
        ],
    )
    out = io.StringIO()
    with pytest.raises(InterpreterError, match="overflow"):
        stack_run(
            "push 1 push 2 push 3",
            spec,
            stdin=io.StringIO(""),
            stdout=out,
            bounded_size=2,
        )


# ---------------------------------------------------------------------------
# Cell-width wrapping
# ---------------------------------------------------------------------------


def test_byte_cell_width_wraps_on_add() -> None:
    """255 + 2 with BYTE cell width wraps to 1."""
    spec = LanguageSpec(
        name="byte-wrap-test",
        base_machine=BaseMachine.STACK,
        memory_shape=MemoryShape.STACK_UNBOUNDED,
        cell_width=CellWidth.BYTE,
        encoding=Encoding.WHITESPACE_SEPARATED_TOKENS,
        instructions=[
            Instruction(token="push", op=InstructionOp.STACK_PUSH, arity=1),
            Instruction(token="add", op=InstructionOp.STACK_ADD),
            Instruction(token="print", op=InstructionOp.STACK_OUTPUT_INT),
        ],
    )
    out = io.StringIO()
    stack_run("push 255 push 2 add print", spec, stdin=io.StringIO(""), stdout=out)
    assert out.getvalue() == "1"


# ---------------------------------------------------------------------------
# YAML round-trip
# ---------------------------------------------------------------------------


def test_minimal_stack_yaml_loads() -> None:
    spec = load_spec(EXAMPLES / "minimal-stack.yaml")
    assert spec.name == "Minimal Stack"
    assert spec.base_machine == BaseMachine.STACK
    assert spec.memory_shape == MemoryShape.STACK_UNBOUNDED
    assert spec.encoding == Encoding.WHITESPACE_SEPARATED_TOKENS
    push = next(i for i in spec.instructions if i.token == "push")
    assert push.arity == 1
    non_push = [i for i in spec.instructions if i.token != "push"]
    assert all(i.arity == 0 for i in non_push)


def test_minimal_stack_yaml_compute_and_print_end_to_end() -> None:
    """The YAML's `push 10 push 3 sub print` example runs to "7"."""
    spec = load_spec(EXAMPLES / "minimal-stack.yaml")
    out = io.StringIO()
    stack_run("push 10 push 3 sub print", spec, stdin=io.StringIO(""), stdout=out)
    assert out.getvalue() == "7"


# ---------------------------------------------------------------------------
# Package-level dispatcher
# ---------------------------------------------------------------------------


def test_package_run_dispatches_to_stack() -> None:
    """`babel.run` picks the stack interpreter for a stack spec."""
    spec = _minimal_stack_spec()
    out = io.StringIO()
    babel.run("push 65 emit", spec, stdin=io.StringIO(""), stdout=out)
    assert out.getvalue() == "A"


def test_package_run_dispatches_to_tape() -> None:
    """`babel.run` still picks the tape interpreter for a tape spec."""
    spec = load_spec(EXAMPLES / "brainfuck-vanilla.yaml")
    out = io.StringIO()
    babel.run("++++++++[>++++++++<-]>+.", spec, stdin=io.StringIO(""), stdout=out)
    assert out.getvalue() == "A"


# ---------------------------------------------------------------------------
# Schema-level validator: stack specs reject non-stack ops
# ---------------------------------------------------------------------------


def test_stack_spec_rejects_tape_op_at_schema_time() -> None:
    """`_check_stack_ops_legal` catches tape ops in a stack spec."""
    from pydantic import ValidationError

    with pytest.raises(ValidationError, match="don't apply to a stack"):
        LanguageSpec(
            name="bad-stack",
            base_machine=BaseMachine.STACK,
            memory_shape=MemoryShape.STACK_UNBOUNDED,
            encoding=Encoding.WHITESPACE_SEPARATED_TOKENS,
            instructions=[
                Instruction(token="push", op=InstructionOp.STACK_PUSH, arity=1),
                # PTR_RIGHT is a tape op; should be rejected on a stack spec.
                Instruction(token="right", op=InstructionOp.PTR_RIGHT),
            ],
        )
