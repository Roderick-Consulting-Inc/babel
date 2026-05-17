# Copyright 2026 Roderick Consulting Inc.
# Licensed under the Apache License, Version 2.0.
"""End-to-end test for the Pikalang parameter sheet.

Pikalang is a Brainfuck derivative whose tokens are Pokémon-syllable words
(pipi / pichu / pi / ka / pikachu / pikapi / pika / chu). The tokens contain
prefix overlaps (`pi` ⊂ `pikapi`, `pika` ⊂ `pikachu`), but the wiki
specifies whitespace-separated source format — so atom-by-atom matching is
unambiguous and Babel's single-atom fast path handles it without longest-
match logic.
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

# Per the Pikalang wiki page (https://esolangs.org/wiki/Pikalang).
_PIKA_TOKEN: dict[str, str] = {
    ">": "pipi",
    "<": "pichu",
    "+": "pi",
    "-": "ka",
    ".": "pikachu",
    ",": "pikapi",
    "[": "pika",
    "]": "chu",
}


def _to_pika(bf: str) -> str:
    """Translate a vanilla BF source to a whitespace-separated Pikalang source."""
    return " ".join(_PIKA_TOKEN[c] for c in bf if c in _PIKA_TOKEN)


def test_pikalang_yaml_loads() -> None:
    spec = load_spec(EXAMPLES / "pikalang.yaml")
    assert spec.name == "Pikalang"
    assert spec.base_machine == BaseMachine.BRAINFUCK_TAPE
    assert spec.encoding == Encoding.WHITESPACE_SEPARATED_TOKENS
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
    # All tokens are single atoms (no internal whitespace).
    assert all(" " not in i.token for i in spec.instructions)


def test_pikalang_hello_world() -> None:
    spec = load_spec(EXAMPLES / "pikalang.yaml")
    program = _to_pika(HELLO_WORLD_BF)
    out = io.StringIO()
    run(program, spec, stdin=io.StringIO(""), stdout=out)
    assert out.getvalue() == EXPECTED


def test_pikalang_prefix_overlap_disambiguated_by_whitespace() -> None:
    """`pika` and `pikachu` are distinct because the source is whitespace-separated.

    Program: ++[->+<].  →  pi pi pika ka pipi pi pichu chu pipi pikachu
    Sets cell 0 to 2, runs a loop that moves +2 to cell 1, then > and output.
    """
    spec = load_spec(EXAMPLES / "pikalang.yaml")
    program = "pi pi pika ka pipi pi pichu chu pipi pikachu"
    out = io.StringIO()
    run(program, spec, stdin=io.StringIO(""), stdout=out)
    assert out.getvalue() == "\x02"


def test_pikalang_unknown_token_raises() -> None:
    """A non-Pikalang word raises ParseError with a clear message."""
    spec = load_spec(EXAMPLES / "pikalang.yaml")
    out = io.StringIO()
    try:
        run("pi charizard pikachu", spec, stdin=io.StringIO(""), stdout=out)
    except Exception as e:
        assert "charizard" in str(e) or "unknown token" in str(e)
    else:
        raise AssertionError("expected ParseError on stray word, got none")
