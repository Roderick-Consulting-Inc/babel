# Copyright 2026 Roderick Consulting Inc.
# Licensed under the Apache License, Version 2.0.
"""End-to-end tests for the Spoon parameter sheet (Babel v0.6.0).

Spoon is the canonical exemplar of the `variable_length_binary` encoding:
a Brainfuck derivative whose instructions are Huffman-style prefix-free
bit-strings. The source is a stream of `0` and `1` characters; any
other character is treated as a comment (silently skipped).
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

# Mapping from canonical BF chars to Spoon bit-strings. Matches the
# parameter sheet `examples/spoon.yaml`.
_SPOON_TOKEN: dict[str, str] = {
    "+": "1",
    "-": "000",
    ">": "010",
    "<": "011",
    ",": "00100",
    ".": "00101",
    "[": "00110",
    "]": "00111",
}


def _to_spoon(bf: str) -> str:
    """Translate a vanilla BF source to a Spoon bit-stream (no separators)."""
    return "".join(_SPOON_TOKEN[c] for c in bf if c in _SPOON_TOKEN)


def test_spoon_yaml_loads() -> None:
    spec = load_spec(EXAMPLES / "spoon.yaml")
    assert spec.name == "Spoon"
    assert spec.base_machine == BaseMachine.BRAINFUCK_TAPE
    assert spec.encoding == Encoding.VARIABLE_LENGTH_BINARY
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
    # Every token is a bit-string (only `0` and `1` characters).
    assert all(set(i.token) <= {"0", "1"} for i in spec.instructions)


def test_spoon_tiny_program_two_increments_and_output() -> None:
    """`1 1 00101` → INCREMENT, INCREMENT, OUTPUT → emits '\\x02'.

    Whitespace between codes is ignored (it's not 0/1 so the tokenizer
    treats it as a comment character).
    """
    spec = load_spec(EXAMPLES / "spoon.yaml")
    out = io.StringIO()
    run("1 1 00101", spec, stdin=io.StringIO(""), stdout=out)
    assert out.getvalue() == "\x02"


def test_spoon_non_bit_characters_are_comments() -> None:
    """Any character that is not `0` or `1` is silently skipped."""
    spec = load_spec(EXAMPLES / "spoon.yaml")
    out = io.StringIO()
    # Decorative formatting with newlines, tabs, ASCII letters.
    src = "increment:\n1\nincrement again:\t1\nemit:\n00101"
    # But "increment" / "emit" contain neither `0` nor `1` so they're fully
    # transparent — the bit-stream is the same `1 1 00101`.
    run(src, spec, stdin=io.StringIO(""), stdout=out)
    assert out.getvalue() == "\x02"


def test_spoon_trailing_bits_raise_parse_error() -> None:
    """A buffer that ends without matching any code raises ParseError."""
    spec = load_spec(EXAMPLES / "spoon.yaml")
    with pytest.raises(ParseError, match="trailing bits"):
        # `001` is the prefix of `00100`/`00101`/`00110`/`00111` but is not
        # itself a defined code; if the source ends with `001` we have
        # incomplete code.
        run("1 001", spec, stdin=io.StringIO(""), stdout=io.StringIO())


def test_spoon_arity_rejected_at_tokenize_time() -> None:
    """Arity > 0 on a variable_length_binary spec raises ParseError.

    Bit-strings have no defined operand-position semantics; even though
    the schema lets a sheet declare arity > 0 on any op, the tokenizer
    refuses to interpret it.
    """
    spec = LanguageSpec(
        name="spoon-arity",
        base_machine=BaseMachine.BRAINFUCK_TAPE,
        memory_shape=MemoryShape.TAPE_1D_UNBOUNDED,
        encoding=Encoding.VARIABLE_LENGTH_BINARY,
        instructions=[
            Instruction(token="010", op=InstructionOp.PTR_RIGHT),
            Instruction(token="011", op=InstructionOp.PTR_LEFT),
            Instruction(token="1", op=InstructionOp.INCREMENT),
            Instruction(token="000", op=InstructionOp.DECREMENT),
            # Arity-1 jump op with a bit-string code — disallowed.
            Instruction(token="00100", op=InstructionOp.JUMP_UNCONDITIONAL, arity=1),
        ],
    )
    with pytest.raises(ParseError, match="variable_length_binary"):
        run("1", spec, stdin=io.StringIO(""), stdout=io.StringIO())


def test_spoon_hello_world() -> None:
    """Canonical BF Hello World transliterated to Spoon outputs `Hello World!\\n`."""
    spec = load_spec(EXAMPLES / "spoon.yaml")
    program = _to_spoon(HELLO_WORLD_BF)
    # Sanity: the bit-stream should be pure 0s and 1s.
    assert set(program) <= {"0", "1"}
    out = io.StringIO()
    run(program, spec, stdin=io.StringIO(""), stdout=out)
    assert out.getvalue() == EXPECTED


def test_spoon_yaml_examples_run() -> None:
    """Every example program in the YAML produces its declared expected_output."""
    spec = load_spec(EXAMPLES / "spoon.yaml")
    for ex in spec.examples:
        out = io.StringIO()
        run(ex.source, spec, stdin=io.StringIO(""), stdout=out, max_steps=200_000)
        assert out.getvalue() == ex.expected_output, (
            f"example {ex.title!r}: got {out.getvalue()!r}, "
            f"expected {ex.expected_output!r}"
        )
