# Copyright 2026 Roderick Consulting Inc.
# Licensed under the Apache License, Version 2.0.
"""End-to-end tests for the La Weá parameter sheet (Babel v0.5.1).

La Weá is the Chilean Spanish entry in the Spanish-language BF trio
(Argentine/Mexican/peninsular/Chilean — four registers, one parameter-
sheet schema). Sixteen instructions; 15 of them execute end-to-end after
v0.5.1's 5 new InstructionOps. The 16th (`pico` → BREAK_LOOP) is schema-
legal but runtime-raises pending the BF-tape loop-stack runtime extension.
"""

from __future__ import annotations

import io
from pathlib import Path

import pytest

from babel.interpreter import InterpreterError, run
from babel.loader import load_spec
from babel.schema import BaseMachine, Encoding, InstructionOp

EXAMPLES = Path(__file__).resolve().parent.parent / "examples"

HELLO_WORLD_BF = (
    "++++++++[>++++[>++>+++>+++>+<<<<-]>+>+>->>+[<]<-]>>.>---.+++++++.."
    "+++.>>.<-.<.+++.------.--------.>>+.>++."
)
EXPECTED = "Hello World!\n"

# Token map covers the 8 canonical-BF ops only; the La Weá extras
# (aweonao, maraco, maraca, pico, chúpala, brígido, perkin, mierda) are
# not used by the standard BF Hello World.
_LA_WEA_TOKEN: dict[str, str] = {
    "+": "weón",
    "-": "maricón",
    ">": "puta",
    "<": "chucha",
    ".": "ctm",
    ",": "quéweá",
    "[": "pichula",
    "]": "tula",
}


def _to_la_wea(bf: str) -> str:
    return " ".join(_LA_WEA_TOKEN[c] for c in bf if c in _LA_WEA_TOKEN)


def test_la_wea_yaml_loads() -> None:
    spec = load_spec(EXAMPLES / "brainfuck-la-wea.yaml")
    assert spec.name == "La Weá"
    assert spec.base_machine == BaseMachine.BRAINFUCK_TAPE
    assert spec.encoding == Encoding.WHITESPACE_SEPARATED_TOKENS
    ops = {i.op for i in spec.instructions}
    expected = {
        InstructionOp.PTR_RIGHT,
        InstructionOp.PTR_LEFT,
        InstructionOp.INCREMENT,
        InstructionOp.DECREMENT,
        InstructionOp.OUTPUT,
        InstructionOp.INPUT,
        InstructionOp.LOOP_START,
        InstructionOp.LOOP_END,
        InstructionOp.ZERO,
        InstructionOp.HALT,
        InstructionOp.INCREMENT_BY_2,
        InstructionOp.DECREMENT_BY_2,
        InstructionOp.CLIPBOARD_TOGGLE,
        InstructionOp.OUTPUT_INT,
        InstructionOp.INPUT_INT,
        InstructionOp.BREAK_LOOP,
    }
    assert ops == expected
    assert len(spec.instructions) == 16


def test_la_wea_hello_world() -> None:
    """Canonical BF Hello World transliterated to La Weá's 8 canonical tokens."""
    spec = load_spec(EXAMPLES / "brainfuck-la-wea.yaml")
    program = _to_la_wea(HELLO_WORLD_BF)
    out = io.StringIO()
    run(program, spec, stdin=io.StringIO(""), stdout=out)
    assert out.getvalue() == EXPECTED


def test_la_wea_aweonao_plus_2() -> None:
    """`aweonao` (+2) sets cell to 2 in one op; output as char emits `\\x02`."""
    spec = load_spec(EXAMPLES / "brainfuck-la-wea.yaml")
    out = io.StringIO()
    run("aweonao ctm", spec, stdin=io.StringIO(""), stdout=out)
    assert out.getvalue() == "\x02"


def test_la_wea_maraco_minus_2() -> None:
    """`maraco` (-2) on a byte cell wraps to 254; output as integer emits `254`."""
    spec = load_spec(EXAMPLES / "brainfuck-la-wea.yaml")
    out = io.StringIO()
    run("maraco chúpala", spec, stdin=io.StringIO(""), stdout=out)
    assert out.getvalue() == "254"


def test_la_wea_maraca_zero() -> None:
    """`maraca` zeroes the cell — a non-zero cell becomes 0."""
    spec = load_spec(EXAMPLES / "brainfuck-la-wea.yaml")
    out = io.StringIO()
    # Increment to 5, then zero, then print as integer
    run("weón weón weón weón weón maraca chúpala", spec, stdin=io.StringIO(""), stdout=out)
    assert out.getvalue() == "0"


def test_la_wea_chupala_integer_output() -> None:
    """`chúpala` prints the cell as a decimal integer regardless of IOModel."""
    spec = load_spec(EXAMPLES / "brainfuck-la-wea.yaml")
    out = io.StringIO()
    # Build 42 via 21 × +2
    program = " ".join(["aweonao"] * 21) + " chúpala"
    run(program, spec, stdin=io.StringIO(""), stdout=out)
    assert out.getvalue() == "42"


def test_la_wea_brigido_integer_input() -> None:
    """`brígido` reads a decimal integer from stdin into the current cell."""
    spec = load_spec(EXAMPLES / "brainfuck-la-wea.yaml")
    out = io.StringIO()
    run("brígido chúpala", spec, stdin=io.StringIO("123\n"), stdout=out)
    assert out.getvalue() == "123"


def test_la_wea_perkin_toggle() -> None:
    """`perkin` toggles between copy and paste:
    1) cell=5; perkin → buffer=5, cell=5
    2) maraca → cell=0
    3) perkin → cell=5 (buffer was full, pastes back and clears)
    """
    spec = load_spec(EXAMPLES / "brainfuck-la-wea.yaml")
    out = io.StringIO()
    program = "weón weón weón weón weón perkin maraca perkin chúpala"
    run(program, spec, stdin=io.StringIO(""), stdout=out)
    assert out.getvalue() == "5"


def test_la_wea_mierda_halt() -> None:
    """`mierda` halts immediately; ops after it don't execute."""
    spec = load_spec(EXAMPLES / "brainfuck-la-wea.yaml")
    out = io.StringIO()
    run("weón ctm mierda weón ctm", spec, stdin=io.StringIO(""), stdout=out)
    # First ctm emits \x01, then mierda halts before second ctm
    assert out.getvalue() == "\x01"


def test_la_wea_pico_jumps_out_of_loop() -> None:
    """v0.5.2: `pico` jumps to the position after the nearest following `tula`.

    Program: `weón pichula pico weón ctm tula weón ctm`
    Op stream: INCREMENT, LOOP_START, BREAK_LOOP, INCREMENT, OUTPUT, LOOP_END, INCREMENT, OUTPUT
    Same trace as `test_break_loop_jumps_to_next_loop_end` — the in-loop
    `weón ctm` is skipped; the post-loop `weón ctm` emits '\\x02'.
    """
    spec = load_spec(EXAMPLES / "brainfuck-la-wea.yaml")
    out = io.StringIO()
    run("weón pichula pico weón ctm tula weón ctm", spec, stdin=io.StringIO(""), stdout=out)
    assert out.getvalue() == "\x02"
