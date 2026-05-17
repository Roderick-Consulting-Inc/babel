# Copyright 2026 Roderick Consulting Inc.
# Licensed under the Apache License, Version 2.0.
"""End-to-end test for the GERMAN parameter sheet.

GERMAN is a trivial Brainfuck substitution into German vocabulary (all-caps
single-atom tokens: LINKS, RECHTS, ADDITION, SUBTRAKTION, EINGABE, AUSGABE,
SCHLEIFENANFANG, SCHLEIFENENDE). Single-atom whitespace-separated tokens —
exercises the same fast path as Chespirito and Rioplatense.
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

_GERMAN_TOKEN: dict[str, str] = {
    "<": "LINKS",
    ">": "RECHTS",
    "+": "ADDITION",
    "-": "SUBTRAKTION",
    ",": "EINGABE",
    ".": "AUSGABE",
    "[": "SCHLEIFENANFANG",
    "]": "SCHLEIFENENDE",
}


def _to_german(bf: str) -> str:
    """Translate a vanilla BF source to a whitespace-separated GERMAN source."""
    return " ".join(_GERMAN_TOKEN[c] for c in bf if c in _GERMAN_TOKEN)


def test_german_yaml_loads() -> None:
    spec = load_spec(EXAMPLES / "german.yaml")
    assert spec.name == "GERMAN"
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
    # All tokens are single atoms (no whitespace), all uppercase.
    assert all(" " not in i.token for i in spec.instructions)
    assert all(i.token.isupper() for i in spec.instructions)


def test_german_hello_world() -> None:
    spec = load_spec(EXAMPLES / "german.yaml")
    program = _to_german(HELLO_WORLD_BF)
    out = io.StringIO()
    run(program, spec, stdin=io.StringIO(""), stdout=out)
    assert out.getvalue() == EXPECTED


def test_german_unknown_token_raises() -> None:
    """A non-GERMAN word raises ParseError with a clear message."""
    spec = load_spec(EXAMPLES / "german.yaml")
    out = io.StringIO()
    try:
        run("ADDITION KARTOFFEL AUSGABE", spec, stdin=io.StringIO(""), stdout=out)
    except Exception as e:
        assert "KARTOFFEL" in str(e) or "unknown token" in str(e)
    else:
        raise AssertionError("expected ParseError on stray word, got none")


def test_german_case_sensitive() -> None:
    """Lowercase variants are not recognized (the spec is all-caps)."""
    spec = load_spec(EXAMPLES / "german.yaml")
    out = io.StringIO()
    try:
        run("addition", spec, stdin=io.StringIO(""), stdout=out)
    except Exception as e:
        assert "addition" in str(e) or "unknown token" in str(e)
    else:
        raise AssertionError("expected ParseError on lowercase variant, got none")
