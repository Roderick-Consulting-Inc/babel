# Copyright 2026 Roderick Consulting Inc.
# Licensed under the Apache License, Version 2.0.
"""End-to-end interpreter tests: run BF Hello World in both YAMLs."""

from __future__ import annotations

import io
from pathlib import Path

from babel.interpreter import run
from babel.loader import load_spec

EXAMPLES = Path(__file__).resolve().parent.parent / "examples"

# Canonical BF "Hello World!\n" from the esolangs.org wiki.
HELLO_WORLD_BF = (
    "++++++++[>++++[>++>+++>+++>+<<<<-]>+>+>->>+[<]<-]>>.>---.+++++++.."
    "+++.>>.<-.<.+++.------.--------.>>+.>++."
)
EXPECTED = "Hello World!\n"

# Map vanilla-BF chars to their Rioplatense surface tokens (matches the YAML).
_RIO_TOKEN: dict[str, str] = {
    ">": "che",
    "<": "vení",
    "+": "más",
    "-": "menos",
    ".": "decí",
    ",": "escuchá",
    "[": "mientras",
    "]": "ya",
}


def _to_rioplatense(bf: str) -> str:
    """Translate a vanilla BF source to whitespace-separated Rioplatense tokens."""
    return " ".join(_RIO_TOKEN[c] for c in bf if c in _RIO_TOKEN)


def test_vanilla_hello_world() -> None:
    spec = load_spec(EXAMPLES / "brainfuck-vanilla.yaml")
    out = io.StringIO()
    run(HELLO_WORLD_BF, spec, stdin=io.StringIO(""), stdout=out)
    assert out.getvalue() == EXPECTED


def test_rioplatense_hello_world() -> None:
    spec = load_spec(EXAMPLES / "brainfuck-rioplatense.yaml")
    program = _to_rioplatense(HELLO_WORLD_BF)
    out = io.StringIO()
    run(program, spec, stdin=io.StringIO(""), stdout=out)
    assert out.getvalue() == EXPECTED


# ---------------------------------------------------------------------------
# v0.2.0 op handler coverage: HALT (implemented); BREAK_LOOP and
# JUMP_UNCONDITIONAL schema-legal but interpreter raises pending runtime work.
# ---------------------------------------------------------------------------

import pytest

from babel.interpreter import InterpreterError
from babel.schema import (
    BaseMachine,
    Encoding,
    Instruction,
    InstructionOp,
    LanguageSpec,
    MemoryShape,
)


def _halt_spec() -> LanguageSpec:
    """BF canonical + HALT (`h`)."""
    return LanguageSpec(
        name="halt-test",
        base_machine=BaseMachine.BRAINFUCK_TAPE,
        memory_shape=MemoryShape.TAPE_1D_UNBOUNDED,
        encoding=Encoding.ASCII_PUNCTUATION,
        instructions=[
            Instruction(token=">", op=InstructionOp.PTR_RIGHT),
            Instruction(token="<", op=InstructionOp.PTR_LEFT),
            Instruction(token="+", op=InstructionOp.INCREMENT),
            Instruction(token="-", op=InstructionOp.DECREMENT),
            Instruction(token=".", op=InstructionOp.OUTPUT),
            Instruction(token=",", op=InstructionOp.INPUT),
            Instruction(token="[", op=InstructionOp.LOOP_START),
            Instruction(token="]", op=InstructionOp.LOOP_END),
            Instruction(token="h", op=InstructionOp.HALT),
        ],
    )


def test_halt_stops_execution_immediately() -> None:
    """`h` between two output ops emits only the first."""
    spec = _halt_spec()
    out = io.StringIO()
    # +++++ (cell=5) . (emit '\5') h (halt) + . (would emit '\6' but halted)
    run("+++++.h+.", spec, stdin=io.StringIO(""), stdout=out)
    assert out.getvalue() == "\x05"


def test_halt_in_program_without_output_after() -> None:
    """HALT mid-program prevents anything after from running."""
    spec = _halt_spec()
    out = io.StringIO()
    run("+++h+++.", spec, stdin=io.StringIO(""), stdout=out)
    assert out.getvalue() == ""


def test_break_loop_raises_not_yet_implemented() -> None:
    """BREAK_LOOP is schema-legal but interpreter raises (deferred runtime work)."""
    spec = LanguageSpec(
        name="break-test",
        base_machine=BaseMachine.BRAINFUCK_TAPE,
        memory_shape=MemoryShape.TAPE_1D_UNBOUNDED,
        encoding=Encoding.ASCII_PUNCTUATION,
        instructions=[
            Instruction(token=">", op=InstructionOp.PTR_RIGHT),
            Instruction(token="<", op=InstructionOp.PTR_LEFT),
            Instruction(token="+", op=InstructionOp.INCREMENT),
            Instruction(token="-", op=InstructionOp.DECREMENT),
            Instruction(token="[", op=InstructionOp.LOOP_START),
            Instruction(token="]", op=InstructionOp.LOOP_END),
            Instruction(token="b", op=InstructionOp.BREAK_LOOP),
        ],
    )
    with pytest.raises(InterpreterError, match="break_loop"):
        run("+[b]", spec, stdin=io.StringIO(""), stdout=io.StringIO())


def test_jump_unconditional_raises_not_yet_implemented() -> None:
    """JUMP_UNCONDITIONAL is schema-legal but interpreter raises (operand-slot pending)."""
    spec = LanguageSpec(
        name="jump-test",
        base_machine=BaseMachine.BRAINFUCK_TAPE,
        memory_shape=MemoryShape.TAPE_1D_UNBOUNDED,
        encoding=Encoding.ASCII_PUNCTUATION,
        instructions=[
            Instruction(token=">", op=InstructionOp.PTR_RIGHT),
            Instruction(token="<", op=InstructionOp.PTR_LEFT),
            Instruction(token="+", op=InstructionOp.INCREMENT),
            Instruction(token="-", op=InstructionOp.DECREMENT),
            Instruction(token="j", op=InstructionOp.JUMP_UNCONDITIONAL),
        ],
    )
    with pytest.raises(InterpreterError, match="jump_unconditional"):
        run("+j", spec, stdin=io.StringIO(""), stdout=io.StringIO())
