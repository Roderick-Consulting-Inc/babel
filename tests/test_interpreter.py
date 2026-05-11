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
