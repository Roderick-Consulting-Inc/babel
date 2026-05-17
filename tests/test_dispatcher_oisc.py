# Copyright 2026 Roderick Consulting Inc.
# Licensed under the Apache License, Version 2.0.
"""Test that the v0.4.2 package-level dispatcher routes OISC specs correctly."""

from __future__ import annotations

import io
from pathlib import Path

import babel
from babel.loader import load_spec

EXAMPLES = Path(__file__).resolve().parent.parent / "examples"


def test_dispatcher_routes_oisc_to_oisc_interpreter() -> None:
    """`babel.run` on an OISC spec should execute via the OISC interpreter.

    Uses the canonical `subleq.yaml` and a tiny program that halts immediately
    (the c-operand of the first SUBLEQ is -1, so the interpreter terminates
    after the first step). If the dispatcher routed to the wrong runtime —
    say, the BF-tape interpreter — the spec validation alone would raise
    `InterpreterError("interpreter currently only supports base_machine=
    brainfuck_tape; got oisc")` before the program runs. Successful execution
    is therefore evidence the dispatcher is wired correctly.
    """
    spec = load_spec(EXAMPLES / "subleq.yaml")
    out = io.StringIO()
    # Halt-immediately program: any triple with c < 0 halts after one step.
    babel.run("0 0 -1", spec, stdin=io.StringIO(""), stdout=out)
    # No output expected; the test passes if no exception was raised.
    assert out.getvalue() == ""
