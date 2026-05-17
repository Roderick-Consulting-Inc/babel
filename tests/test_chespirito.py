# Copyright 2026 Roderick Consulting Inc.
# Licensed under the Apache License, Version 2.0.
"""End-to-end test for the Chespirito parameter sheet.

Chespirito is a Brainfuck derivative whose surface tokens are Spanish words
from the Mexican comedian Chespirito's vocabulary. Single-atom whitespace-
separated tokens (the simpler tokenizer fast path); 9 ops total (canonical
8 + `chiripiolca` mapped to `random`).
"""

from __future__ import annotations

import io
import random
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

_CHESPIRITO_TOKEN: dict[str, str] = {
    "+": "chilindrina",
    "-": "chiquitolina",
    ">": "chompiras",
    "<": "chaparron",
    "[": "chipote",
    "]": "chillon",
    ".": "chanfle",
    ",": "chapulin",
}


def _to_chespirito(bf: str) -> str:
    """Translate a vanilla BF source to a whitespace-separated Chespirito source."""
    return " ".join(_CHESPIRITO_TOKEN[c] for c in bf if c in _CHESPIRITO_TOKEN)


def test_chespirito_yaml_loads() -> None:
    spec = load_spec(EXAMPLES / "brainfuck-chespirito.yaml")
    assert spec.name == "Chespirito"
    assert spec.base_machine == BaseMachine.BRAINFUCK_TAPE
    assert spec.encoding == Encoding.WHITESPACE_SEPARATED_TOKENS
    ops = {i.op for i in spec.instructions}
    # 8 canonical BF ops + RANDOM (for chiripiolca).
    expected_ops = {
        InstructionOp.PTR_RIGHT,
        InstructionOp.PTR_LEFT,
        InstructionOp.INCREMENT,
        InstructionOp.DECREMENT,
        InstructionOp.OUTPUT,
        InstructionOp.INPUT,
        InstructionOp.LOOP_START,
        InstructionOp.LOOP_END,
        InstructionOp.RANDOM,
    }
    assert ops == expected_ops
    # All tokens are single atoms (no whitespace).
    assert all(" " not in i.token for i in spec.instructions)


def test_chespirito_hello_world() -> None:
    spec = load_spec(EXAMPLES / "brainfuck-chespirito.yaml")
    program = _to_chespirito(HELLO_WORLD_BF)
    out = io.StringIO()
    run(program, spec, stdin=io.StringIO(""), stdout=out)
    assert out.getvalue() == EXPECTED


def test_chespirito_chiripiolca_is_random() -> None:
    """`chiripiolca` sets the current cell to a random byte (per Babel's `random` op)."""
    spec = load_spec(EXAMPLES / "brainfuck-chespirito.yaml")
    rng = random.Random(42)  # seeded for determinism
    out = io.StringIO()
    # chiripiolca (random) then chanfle (output) — should emit one byte.
    run("chiripiolca chanfle", spec, stdin=io.StringIO(""), stdout=out, rng=rng)
    assert len(out.getvalue()) == 1


def test_chespirito_unknown_token_raises() -> None:
    """A non-Chespirito word raises ParseError with a clear message."""
    spec = load_spec(EXAMPLES / "brainfuck-chespirito.yaml")
    out = io.StringIO()
    try:
        run("chilindrina banana chanfle", spec, stdin=io.StringIO(""), stdout=out)
    except Exception as e:
        assert "banana" in str(e)
    else:
        raise AssertionError("expected ParseError on stray word, got none")
