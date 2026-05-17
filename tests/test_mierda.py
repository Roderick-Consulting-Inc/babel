# Copyright 2026 Roderick Consulting Inc.
# Licensed under the Apache License, Version 2.0.
"""End-to-end test for the Mierda parameter sheet.

Mierda is a trivial Brainfuck substitution into Spanish vocabulary. Notable
because the sheet mixes single-atom tokens (Mas, Menos, Derecha, Izquierda,
Decir, Leer) with two-atom tokens (Iniciar Bucle, Terminar Bucle), exercising
the multi-atom tokenizer in a mixed configuration the Ook! sheet doesn't.
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

_MIERDA_TOKEN: dict[str, str] = {
    "+": "Mas",
    "-": "Menos",
    ">": "Derecha",
    "<": "Izquierda",
    ".": "Decir",
    ",": "Leer",
    "[": "Iniciar Bucle",
    "]": "Terminar Bucle",
}


def _to_mierda(bf: str) -> str:
    """Translate a vanilla BF source to a whitespace-separated Mierda source."""
    return " ".join(_MIERDA_TOKEN[c] for c in bf if c in _MIERDA_TOKEN)


def test_mierda_yaml_loads() -> None:
    spec = load_spec(EXAMPLES / "brainfuck-mierda.yaml")
    assert spec.name == "Mierda"
    assert spec.base_machine == BaseMachine.BRAINFUCK_TAPE
    assert spec.encoding == Encoding.WHITESPACE_SEPARATED_TOKENS
    ops = {i.op for i in spec.instructions}
    # All 8 canonical BF ops, no extras.
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
    # 6 single-atom + 2 two-atom tokens — exercises the multi-atom path.
    single_atom = [i for i in spec.instructions if " " not in i.token]
    multi_atom = [i for i in spec.instructions if " " in i.token]
    assert len(single_atom) == 6
    assert len(multi_atom) == 2


def test_mierda_hello_world() -> None:
    spec = load_spec(EXAMPLES / "brainfuck-mierda.yaml")
    program = _to_mierda(HELLO_WORLD_BF)
    out = io.StringIO()
    run(program, spec, stdin=io.StringIO(""), stdout=out)
    assert out.getvalue() == EXPECTED


def test_mierda_mixed_atom_count_in_one_program() -> None:
    """A program that uses both single-atom and multi-atom tokens parses correctly."""
    spec = load_spec(EXAMPLES / "brainfuck-mierda.yaml")
    # ++[->+<]. — set cell 0 to 2, then add to cell 1, then move and output cell 1.
    # = "Mas Mas Iniciar Bucle Menos Derecha Mas Izquierda Terminar Bucle Derecha Decir"
    program = "Mas Mas Iniciar Bucle Menos Derecha Mas Izquierda Terminar Bucle Derecha Decir"
    out = io.StringIO()
    run(program, spec, stdin=io.StringIO(""), stdout=out)
    assert out.getvalue() == "\x02"


def test_mierda_unknown_token_raises() -> None:
    """A non-Mierda atom mid-stream surfaces a clear error."""
    spec = load_spec(EXAMPLES / "brainfuck-mierda.yaml")
    out = io.StringIO()
    try:
        run("Mas plátano Decir", spec, stdin=io.StringIO(""), stdout=out)
    except Exception as e:
        assert "plátano" in str(e) or "unknown token sequence" in str(e)
    else:
        raise AssertionError("expected ParseError on stray atom, got none")
