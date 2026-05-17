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


def test_break_loop_jumps_to_next_loop_end() -> None:
    """v0.5.2: BREAK_LOOP (La Weá's `pico`) jumps to nearest following LOOP_END.

    Program: `+[b+.]+.`
    Op stream: INCREMENT, LOOP_START, BREAK_LOOP, INCREMENT, OUTPUT, LOOP_END, INCREMENT, OUTPUT
    Runtime trace:
      pc=0 INCREMENT       cell=1
      pc=1 LOOP_START      cell≠0 → enter loop
      pc=2 BREAK_LOOP      jump to next LOOP_END (pc=5); bottom-of-loop pc+=1 → pc=6
      pc=6 INCREMENT       cell=2
      pc=7 OUTPUT          emit '\\x02'
    Expected output: '\\x02' (the in-loop INCREMENT and OUTPUT are skipped).
    """
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
            Instruction(token=".", op=InstructionOp.OUTPUT),
            Instruction(token="[", op=InstructionOp.LOOP_START),
            Instruction(token="]", op=InstructionOp.LOOP_END),
            Instruction(token="b", op=InstructionOp.BREAK_LOOP),
        ],
    )
    out = io.StringIO()
    run("+[b+.]+.", spec, stdin=io.StringIO(""), stdout=out)
    assert out.getvalue() == "\x02"


def test_break_loop_without_loop_end_raises() -> None:
    """BREAK_LOOP with no following LOOP_END surfaces a clear error."""
    spec = LanguageSpec(
        name="break-no-end",
        base_machine=BaseMachine.BRAINFUCK_TAPE,
        memory_shape=MemoryShape.TAPE_1D_UNBOUNDED,
        encoding=Encoding.ASCII_PUNCTUATION,
        instructions=[
            Instruction(token=">", op=InstructionOp.PTR_RIGHT),
            Instruction(token="<", op=InstructionOp.PTR_LEFT),
            Instruction(token="+", op=InstructionOp.INCREMENT),
            Instruction(token="-", op=InstructionOp.DECREMENT),
            Instruction(token="b", op=InstructionOp.BREAK_LOOP),
        ],
    )
    with pytest.raises(InterpreterError, match="no loop_end follows"):
        run("+b", spec, stdin=io.StringIO(""), stdout=io.StringIO())


def test_jump_unconditional_executes_with_arity_one() -> None:
    """v0.5.0: JUMP_UNCONDITIONAL with arity=1 jumps to the operand-specified absolute pc.

    Test program (whitespace-separated; integer operand after `jump`):
        ``+ . jump 0``
    Op stream after parsing: [INCREMENT, OUTPUT, JUMP_UNCONDITIONAL]
    Runtime trace: INCREMENT (cell=1) → OUTPUT (emit '\\x01') → JUMP to pc=0 →
        INCREMENT (cell=2) → OUTPUT (emit '\\x02') → JUMP to pc=0 → …
    Bounded by `max_steps`; expected output begins with '\\x01\\x02\\x03'.
    """
    spec = LanguageSpec(
        name="jump-test",
        base_machine=BaseMachine.BRAINFUCK_TAPE,
        memory_shape=MemoryShape.TAPE_1D_UNBOUNDED,
        encoding=Encoding.WHITESPACE_SEPARATED_TOKENS,
        instructions=[
            Instruction(token=">", op=InstructionOp.PTR_RIGHT),
            Instruction(token="<", op=InstructionOp.PTR_LEFT),
            Instruction(token="+", op=InstructionOp.INCREMENT),
            Instruction(token="-", op=InstructionOp.DECREMENT),
            Instruction(token=".", op=InstructionOp.OUTPUT),
            Instruction(token="jump", op=InstructionOp.JUMP_UNCONDITIONAL, arity=1),
        ],
    )
    out = io.StringIO()
    with pytest.raises(InterpreterError, match="max_steps"):
        # Cap at 9 steps so we see exactly 3 increment+output cycles
        # (3 × (INC + OUTPUT + JUMP) = 9), then the next step trips max.
        run(
            "+ . jump 0",
            spec,
            stdin=io.StringIO(""),
            stdout=out,
            max_steps=9,
        )
    assert out.getvalue() == "\x01\x02\x03"


def test_jump_unconditional_without_arity_raises_clearly() -> None:
    """JUMP_UNCONDITIONAL declared with arity=0 raises a clear runtime error.

    The op needs an operand (the jump target); a parameter sheet that
    declares it with arity=0 is malformed, and the interpreter surfaces
    that explicitly rather than silently mis-jumping.
    """
    spec = LanguageSpec(
        name="jump-no-arity",
        base_machine=BaseMachine.BRAINFUCK_TAPE,
        memory_shape=MemoryShape.TAPE_1D_UNBOUNDED,
        encoding=Encoding.ASCII_PUNCTUATION,
        instructions=[
            Instruction(token=">", op=InstructionOp.PTR_RIGHT),
            Instruction(token="<", op=InstructionOp.PTR_LEFT),
            Instruction(token="+", op=InstructionOp.INCREMENT),
            Instruction(token="-", op=InstructionOp.DECREMENT),
            Instruction(token="j", op=InstructionOp.JUMP_UNCONDITIONAL),  # arity=0 default
        ],
    )
    with pytest.raises(InterpreterError, match="arity=1 on the jump instruction"):
        run("+j", spec, stdin=io.StringIO(""), stdout=io.StringIO())


def test_jump_unconditional_out_of_range_target_raises() -> None:
    """A jump target outside the parsed-op stream raises InterpreterError."""
    spec = LanguageSpec(
        name="jump-oob",
        base_machine=BaseMachine.BRAINFUCK_TAPE,
        memory_shape=MemoryShape.TAPE_1D_UNBOUNDED,
        encoding=Encoding.WHITESPACE_SEPARATED_TOKENS,
        instructions=[
            Instruction(token=">", op=InstructionOp.PTR_RIGHT),
            Instruction(token="<", op=InstructionOp.PTR_LEFT),
            Instruction(token="+", op=InstructionOp.INCREMENT),
            Instruction(token="-", op=InstructionOp.DECREMENT),
            Instruction(token="jump", op=InstructionOp.JUMP_UNCONDITIONAL, arity=1),
        ],
    )
    with pytest.raises(InterpreterError, match="out of range"):
        run("+ jump 99", spec, stdin=io.StringIO(""), stdout=io.StringIO())


def test_arity_with_ascii_punctuation_rejected_at_parse() -> None:
    """ASCII-punctuation encoding has no operand slot; arity > 0 raises ParseError.

    The constraint is at tokenize time, not schema time — a parameter sheet
    can declare arity > 0 on an ascii-punctuation spec (which validates
    fine), and the failure surfaces only when something actually tries to
    parse a source program against it.
    """
    from babel.interpreter import ParseError

    spec = LanguageSpec(
        name="ascii-jump",
        base_machine=BaseMachine.BRAINFUCK_TAPE,
        memory_shape=MemoryShape.TAPE_1D_UNBOUNDED,
        encoding=Encoding.ASCII_PUNCTUATION,
        instructions=[
            Instruction(token=">", op=InstructionOp.PTR_RIGHT),
            Instruction(token="<", op=InstructionOp.PTR_LEFT),
            Instruction(token="+", op=InstructionOp.INCREMENT),
            Instruction(token="-", op=InstructionOp.DECREMENT),
            Instruction(token="j", op=InstructionOp.JUMP_UNCONDITIONAL, arity=1),
        ],
    )
    with pytest.raises(ParseError, match="ascii_punctuation"):
        run("+j", spec, stdin=io.StringIO(""), stdout=io.StringIO())


def test_arity_non_integer_operand_raises_parse_error() -> None:
    """JUMP_UNCONDITIONAL with a non-integer operand surfaces ParseError."""
    from babel.interpreter import ParseError

    spec = LanguageSpec(
        name="jump-bad-operand",
        base_machine=BaseMachine.BRAINFUCK_TAPE,
        memory_shape=MemoryShape.TAPE_1D_UNBOUNDED,
        encoding=Encoding.WHITESPACE_SEPARATED_TOKENS,
        instructions=[
            Instruction(token=">", op=InstructionOp.PTR_RIGHT),
            Instruction(token="<", op=InstructionOp.PTR_LEFT),
            Instruction(token="+", op=InstructionOp.INCREMENT),
            Instruction(token="-", op=InstructionOp.DECREMENT),
            Instruction(token="jump", op=InstructionOp.JUMP_UNCONDITIONAL, arity=1),
        ],
    )
    with pytest.raises(ParseError, match="must be an integer"):
        run("+ jump banana", spec, stdin=io.StringIO(""), stdout=io.StringIO())


def test_arity_missing_operand_raises_parse_error() -> None:
    """JUMP_UNCONDITIONAL at end of source with no operand raises ParseError."""
    from babel.interpreter import ParseError

    spec = LanguageSpec(
        name="jump-no-operand",
        base_machine=BaseMachine.BRAINFUCK_TAPE,
        memory_shape=MemoryShape.TAPE_1D_UNBOUNDED,
        encoding=Encoding.WHITESPACE_SEPARATED_TOKENS,
        instructions=[
            Instruction(token=">", op=InstructionOp.PTR_RIGHT),
            Instruction(token="<", op=InstructionOp.PTR_LEFT),
            Instruction(token="+", op=InstructionOp.INCREMENT),
            Instruction(token="-", op=InstructionOp.DECREMENT),
            Instruction(token="jump", op=InstructionOp.JUMP_UNCONDITIONAL, arity=1),
        ],
    )
    with pytest.raises(ParseError, match="requires an operand"):
        run("+ jump", spec, stdin=io.StringIO(""), stdout=io.StringIO())
