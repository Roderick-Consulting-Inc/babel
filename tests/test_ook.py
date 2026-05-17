# Copyright 2026 Roderick Consulting Inc.
# Licensed under the Apache License, Version 2.0.
"""End-to-end test for the Ook! parameter sheet (Babel v0.3.0).

Ook! is the first Babel parameter sheet that exercises the multi-atom
whitespace-token tokenizer: each instruction is a pair of Ook tokens
(`Ook. Ook?`, `Ook? Ook.`, etc.) rather than a single atom.

The canonical Hello World here is the standard BF Hello World translated
character-by-character into its Ook pair via the published mapping.
"""

from __future__ import annotations

import io
from pathlib import Path

from babel.interpreter import run
from babel.loader import load_spec
from babel.schema import BaseMachine, Encoding, InstructionOp

EXAMPLES = Path(__file__).resolve().parent.parent / "examples"

# Canonical BF "Hello World!\n" from the esolangs.org wiki.
HELLO_WORLD_BF = (
    "++++++++[>++++[>++>+++>+++>+<<<<-]>+>+>->>+[<]<-]>>.>---.+++++++.."
    "+++.>>.<-.<.+++.------.--------.>>+.>++."
)
EXPECTED = "Hello World!\n"

# Per the Ook! wiki page (https://esolangs.org/wiki/Ook!).
_OOK_TOKEN: dict[str, str] = {
    ">": "Ook. Ook?",
    "<": "Ook? Ook.",
    "+": "Ook. Ook.",
    "-": "Ook! Ook!",
    ".": "Ook! Ook.",
    ",": "Ook. Ook!",
    "[": "Ook! Ook?",
    "]": "Ook? Ook!",
}


def _to_ook(bf: str) -> str:
    """Translate a vanilla BF source to a whitespace-separated Ook! source."""
    return " ".join(_OOK_TOKEN[c] for c in bf if c in _OOK_TOKEN)


def test_ook_yaml_loads() -> None:
    spec = load_spec(EXAMPLES / "ook.yaml")
    assert spec.name == "Ook!"
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
    # All tokens are exactly two atoms.
    assert all(len(i.token.split()) == 2 for i in spec.instructions)


def test_ook_hello_world() -> None:
    spec = load_spec(EXAMPLES / "ook.yaml")
    program = _to_ook(HELLO_WORLD_BF)
    out = io.StringIO()
    run(program, spec, stdin=io.StringIO(""), stdout=out)
    assert out.getvalue() == EXPECTED


def test_ook_unknown_token_raises() -> None:
    """A stray non-Ook atom in the middle of the stream surfaces a clear error."""
    spec = load_spec(EXAMPLES / "ook.yaml")
    # Two valid Ook pairs sandwiching a bogus atom.
    program = "Ook. Ook. banana Ook. Ook."
    out = io.StringIO()
    try:
        run(program, spec, stdin=io.StringIO(""), stdout=out)
    except Exception as e:
        assert "banana" in str(e) or "unknown token sequence" in str(e)
    else:
        raise AssertionError("expected ParseError on stray atom, got none")


def test_ook_partial_pair_at_end_raises() -> None:
    """A dangling single Ook atom at the end of the source surfaces an error."""
    spec = load_spec(EXAMPLES / "ook.yaml")
    program = "Ook. Ook. Ook."  # second '+' has only one Ook
    out = io.StringIO()
    try:
        run(program, spec, stdin=io.StringIO(""), stdout=out)
    except Exception as e:
        assert "unknown token sequence" in str(e) or "Ook." in str(e)
    else:
        raise AssertionError("expected ParseError on dangling Ook atom, got none")
