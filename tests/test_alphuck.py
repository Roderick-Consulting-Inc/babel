# Copyright 2026 Roderick Consulting Inc.
# Licensed under the Apache License, Version 2.0.
"""End-to-end test for the Alphuck parameter sheet.

Alphuck is a trivial Brainfuck substitution into eight single lowercase ASCII
letters (a / c / e / i / j / o / p / s). Same encoding shape as canonical BF
(single-character punctuation stream), just with letters instead of
punctuation glyphs. Exercises the `ascii_punctuation` tokenizer with
alphabetic single-char tokens.
"""

from __future__ import annotations

import io
from pathlib import Path

from babel.interpreter import run
from babel.loader import load_spec
from babel.schema import BaseMachine, Encoding, InstructionOp

EXAMPLES = Path(__file__).resolve().parent.parent / "examples"

HELLO_WORLD_BF = (
    "++++++++[>++++[>++>+++>+++>+<<<<-]>+>+>->>+[<]<-]>>.>---.+++++++.."
    "+++.>>.<-.<.+++.------.--------.>>+.>++."
)
EXPECTED = "Hello World!\n"

# Per the Alphuck wiki page (https://esolangs.org/wiki/Alphuck).
_ALPH_TOKEN: dict[str, str] = {
    ">": "a",
    "<": "c",
    "+": "e",
    "-": "i",
    ".": "j",
    ",": "o",
    "[": "p",
    "]": "s",
}


def _to_alph(bf: str) -> str:
    """Translate a vanilla BF source to an Alphuck source (no separators)."""
    return "".join(_ALPH_TOKEN[c] for c in bf if c in _ALPH_TOKEN)


def test_alphuck_yaml_loads() -> None:
    spec = load_spec(EXAMPLES / "alphuck.yaml")
    assert spec.name == "Alphuck"
    assert spec.base_machine == BaseMachine.BRAINFUCK_TAPE
    assert spec.encoding == Encoding.ASCII_PUNCTUATION
    ops = {i.op for i in spec.instructions}
    assert ops == {
        InstructionOp.PTR_RIGHT,
        InstructionOp.PTR_LEFT,
        InstructionOp.INCREMENT,
        InstructionOp.DECREMENT,
        InstructionOp.OUTPUT,
        InstructionOp.INPUT,
        InstructionOp.LOOP_START,
        InstructionOp.LOOP_END,
    }
    # All tokens are single lowercase ASCII letters.
    for instr in spec.instructions:
        assert len(instr.token) == 1
        assert instr.token.islower() and instr.token.isascii()


def test_alphuck_hello_world() -> None:
    spec = load_spec(EXAMPLES / "alphuck.yaml")
    program = _to_alph(HELLO_WORLD_BF)
    out = io.StringIO()
    run(program, spec, stdin=io.StringIO(""), stdout=out)
    assert out.getvalue() == EXPECTED


def test_alphuck_non_instruction_chars_are_comments() -> None:
    """ASCII_PUNCTUATION skips unknown chars silently — letters like 'b','d' are comments."""
    spec = load_spec(EXAMPLES / "alphuck.yaml")
    # Print 'A' (65): e*65 then j. Sprinkle non-instruction letters as comments.
    program = "bdfghk " + ("e" * 65) + " lmnq " + "j" + " rtuv"
    out = io.StringIO()
    run(program, spec, stdin=io.StringIO(""), stdout=out)
    assert out.getvalue() == "A"


def test_alphuck_uppercase_is_not_recognized() -> None:
    """Only lowercase letters are instructions; uppercase variants are comments."""
    spec = load_spec(EXAMPLES / "alphuck.yaml")
    # ALL CAPS — no instructions execute, no output produced.
    program = "EEEEJ"
    out = io.StringIO()
    run(program, spec, stdin=io.StringIO(""), stdout=out)
    assert out.getvalue() == ""
