# Copyright 2026 Roderick Consulting Inc.
# Licensed under the Apache License, Version 2.0.
"""Transpiler smoke test: vanilla BF Hello World transpiles non-empty.

For the canonical-BF parameter sheet the transpile is the identity
transformation (each token is already its vanilla character), so we
also check the output round-trips through the interpreter.
"""

from __future__ import annotations

import io
from pathlib import Path

from babel.interpreter import run
from babel.loader import load_spec
from babel.transpiler import transpile

EXAMPLES = Path(__file__).resolve().parent.parent / "examples"

HELLO_WORLD_BF = (
    "++++++++[>++++[>++>+++>+++>+<<<<-]>+>+>->>+[<]<-]>>.>---.+++++++.."
    "+++.>>.<-.<.+++.------.--------.>>+.>++."
)


def test_transpile_vanilla_hello_world_smoke() -> None:
    spec = load_spec(EXAMPLES / "brainfuck-vanilla.yaml")
    lowered = transpile(HELLO_WORLD_BF, spec)
    assert lowered  # non-empty
    # Identity-transpile for canonical BF: lowering should run end-to-end.
    out = io.StringIO()
    run(lowered, spec, stdin=io.StringIO(""), stdout=out)
    assert out.getvalue() == "Hello World!\n"
