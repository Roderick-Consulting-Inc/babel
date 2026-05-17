# Copyright 2026 Roderick Consulting Inc.
# Licensed under the Apache License, Version 2.0.
"""End-to-end test for the BaguaFuck parameter sheet.

BaguaFuck uses the eight Bagua trigrams of the I Ching (乾 / 兑 / 离 / 震 /
巽 / 坎 / 艮 / 坤) as single-character tokens. The reference source format
writes them as adjacent codepoints with no separator, mirroring canonical
BF's punctuation-stream syntax. Babel's `ascii_punctuation` tokenizer
iterates the source character-by-character (Unicode codepoint-aware), so
non-ASCII single-character tokens work natively without any tokenizer
changes.
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

# Per the BaguaFuck wiki page (https://esolangs.org/wiki/BaguaFuck).
_BAGUA_TOKEN: dict[str, str] = {
    ">": "乾",
    "<": "兑",
    "+": "离",
    "-": "震",
    ".": "巽",
    ",": "坎",
    "[": "艮",
    "]": "坤",
}


def _to_bagua(bf: str) -> str:
    """Translate a vanilla BF source to a BaguaFuck source (no separators)."""
    return "".join(_BAGUA_TOKEN[c] for c in bf if c in _BAGUA_TOKEN)


def test_baguafuck_yaml_loads() -> None:
    spec = load_spec(EXAMPLES / "baguafuck.yaml")
    assert spec.name == "BaguaFuck"
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
    # All tokens are exactly one Unicode codepoint.
    assert all(len(i.token) == 1 for i in spec.instructions)
    # All tokens are non-ASCII (Bagua trigrams live in the U+2630..U+2637 block).
    assert all(ord(i.token) > 127 for i in spec.instructions)


def test_baguafuck_hello_world() -> None:
    spec = load_spec(EXAMPLES / "baguafuck.yaml")
    program = _to_bagua(HELLO_WORLD_BF)
    out = io.StringIO()
    run(program, spec, stdin=io.StringIO(""), stdout=out)
    assert out.getvalue() == EXPECTED


def test_baguafuck_non_trigram_chars_are_comments() -> None:
    """ASCII_PUNCTUATION skips unknown chars silently (canonical BF comment behaviour)."""
    spec = load_spec(EXAMPLES / "baguafuck.yaml")
    # Print 'A' (65): 离*65 then 巽. Sprinkle ASCII letters as comments.
    program = "comment text " + ("离" * 65) + " more text " + "巽" + " trailing"
    out = io.StringIO()
    run(program, spec, stdin=io.StringIO(""), stdout=out)
    assert out.getvalue() == "A"
