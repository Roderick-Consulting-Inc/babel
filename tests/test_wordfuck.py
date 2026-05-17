# Copyright 2026 Roderick Consulting Inc.
# Licensed under the Apache License, Version 2.0.
"""End-to-end tests for the Wordfuck parameter sheet (Babel v0.6.0).

Wordfuck is the canonical exemplar of the `word_length_dispatch`
encoding: a Brainfuck derivative whose instruction is selected by the
*length* of each whitespace-separated word. The eight canonical BF ops
map to lengths 1 through 8.
"""

from __future__ import annotations

import io
from pathlib import Path

import pytest

from babel.interpreter import ParseError, run
from babel.loader import load_spec
from babel.schema import (
    BaseMachine,
    Encoding,
    Instruction,
    InstructionOp,
    LanguageSpec,
    MemoryShape,
)

EXAMPLES = Path(__file__).resolve().parent.parent / "examples"

HELLO_WORLD_BF = (
    "++++++++[>++++[>++>+++>+++>+<<<<-]>+>+>->>+[<]<-]>>.>---.+++++++.."
    "+++.>>.<-.<.+++.------.--------.>>+.>++."
)
EXPECTED = "Hello World!\n"

# Canonical mapping: BF char → word length. Matches `examples/wordfuck.yaml`.
_LENGTH_FOR: dict[str, int] = {
    "+": 1,
    "-": 2,
    ">": 3,
    "<": 4,
    ".": 5,
    ",": 6,
    "[": 7,
    "]": 8,
}


def _to_wordfuck(bf: str) -> str:
    """Translate a vanilla BF source to a Wordfuck program.

    Emits length-N placeholder strings (`"a" * N`) for each BF char, so
    `++` becomes `"a a"`, `[>]` becomes `"aaaaaaa aaa aaaaaaaa"`, etc.
    """
    return " ".join("a" * _LENGTH_FOR[c] for c in bf if c in _LENGTH_FOR)


def test_wordfuck_yaml_loads() -> None:
    spec = load_spec(EXAMPLES / "wordfuck.yaml")
    assert spec.name == "Wordfuck"
    assert spec.base_machine == BaseMachine.BRAINFUCK_TAPE
    assert spec.encoding == Encoding.WORD_LENGTH_DISPATCH
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
    # Token lengths cover exactly 1..8 (the canonical Wordfuck mapping).
    lengths = sorted(len(i.token) for i in spec.instructions)
    assert lengths == [1, 2, 3, 4, 5, 6, 7, 8]


def test_wordfuck_tiny_program_two_increments_and_output() -> None:
    """`"a a abcde"` → lengths 1, 1, 5 → INCREMENT, INCREMENT, OUTPUT → '\\x02'."""
    spec = load_spec(EXAMPLES / "wordfuck.yaml")
    out = io.StringIO()
    run("a a abcde", spec, stdin=io.StringIO(""), stdout=out)
    assert out.getvalue() == "\x02"


def test_wordfuck_unknown_length_raises_parse_error() -> None:
    """An atom whose length isn't in the dispatch table raises ParseError.

    The Wordfuck sheet defines lengths 1..8; a 9-letter word has no
    mapping.
    """
    spec = load_spec(EXAMPLES / "wordfuck.yaml")
    with pytest.raises(ParseError, match="length 9"):
        run("a abcdefghi", spec, stdin=io.StringIO(""), stdout=io.StringIO())


def test_wordfuck_word_content_is_irrelevant() -> None:
    """Different words of the same length dispatch to the same op."""
    spec = load_spec(EXAMPLES / "wordfuck.yaml")
    out = io.StringIO()
    # All length-1 words → 65 increments → cell=65 → output 'A'
    src = " ".join(["x"] * 65) + " hello"
    run(src, spec, stdin=io.StringIO(""), stdout=out)
    assert out.getvalue() == "A"


def test_wordfuck_arity_rejected_at_tokenize_time() -> None:
    """Arity > 0 on a word_length_dispatch spec raises ParseError.

    Operand atoms would also be dispatched by length and become
    indistinguishable from instructions; the tokenizer refuses to
    interpret such a spec.
    """
    spec = LanguageSpec(
        name="wordfuck-arity",
        base_machine=BaseMachine.BRAINFUCK_TAPE,
        memory_shape=MemoryShape.TAPE_1D_UNBOUNDED,
        encoding=Encoding.WORD_LENGTH_DISPATCH,
        instructions=[
            Instruction(token="a", op=InstructionOp.INCREMENT),
            Instruction(token="ab", op=InstructionOp.DECREMENT),
            Instruction(token="abc", op=InstructionOp.PTR_RIGHT),
            Instruction(token="abcd", op=InstructionOp.PTR_LEFT),
            # arity=1 jump op — disallowed under word_length_dispatch.
            Instruction(token="abcde", op=InstructionOp.JUMP_UNCONDITIONAL, arity=1),
        ],
    )
    with pytest.raises(ParseError, match="word_length_dispatch"):
        run("a", spec, stdin=io.StringIO(""), stdout=io.StringIO())


def test_wordfuck_duplicate_length_rejected_at_tokenize_time() -> None:
    """Two instructions sharing a token length make the spec ambiguous.

    The tokenizer surfaces this at parse time rather than silently
    picking one.
    """
    spec = LanguageSpec(
        name="wordfuck-dup-length",
        base_machine=BaseMachine.BRAINFUCK_TAPE,
        memory_shape=MemoryShape.TAPE_1D_UNBOUNDED,
        encoding=Encoding.WORD_LENGTH_DISPATCH,
        instructions=[
            Instruction(token="a", op=InstructionOp.INCREMENT),
            # Same length-1 mapped to a different op — sheet is ambiguous.
            Instruction(token="b", op=InstructionOp.PTR_RIGHT),
            Instruction(token="cc", op=InstructionOp.PTR_LEFT),
        ],
    )
    with pytest.raises(ParseError, match="same token length"):
        run("a", spec, stdin=io.StringIO(""), stdout=io.StringIO())


def test_wordfuck_hello_world() -> None:
    """Canonical BF Hello World transliterated to Wordfuck outputs `Hello World!\\n`."""
    spec = load_spec(EXAMPLES / "wordfuck.yaml")
    program = _to_wordfuck(HELLO_WORLD_BF)
    out = io.StringIO()
    run(program, spec, stdin=io.StringIO(""), stdout=out)
    assert out.getvalue() == EXPECTED


def test_wordfuck_yaml_examples_run() -> None:
    """Every example program in the YAML produces its declared expected_output."""
    spec = load_spec(EXAMPLES / "wordfuck.yaml")
    for ex in spec.examples:
        out = io.StringIO()
        run(ex.source, spec, stdin=io.StringIO(""), stdout=out, max_steps=200_000)
        assert out.getvalue() == ex.expected_output, (
            f"example {ex.title!r}: got {out.getvalue()!r}, "
            f"expected {ex.expected_output!r}"
        )
