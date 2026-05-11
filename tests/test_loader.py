# Copyright 2026 Roderick Consulting Inc.
# Licensed under the Apache License, Version 2.0.
"""Loader smoke tests: both shipped YAMLs validate against the schema."""

from __future__ import annotations

from pathlib import Path

from babel.loader import load_spec
from babel.schema import BaseMachine, Encoding, InstructionOp, LanguageSpec

EXAMPLES = Path(__file__).resolve().parent.parent / "examples"


def test_vanilla_yaml_loads() -> None:
    spec = load_spec(EXAMPLES / "brainfuck-vanilla.yaml")
    assert isinstance(spec, LanguageSpec)
    assert spec.base_machine == BaseMachine.BRAINFUCK_TAPE
    assert spec.encoding == Encoding.ASCII_PUNCTUATION
    ops = {i.op for i in spec.instructions}
    # All eight canonical BF ops present.
    assert InstructionOp.PTR_RIGHT in ops
    assert InstructionOp.LOOP_END in ops
    assert len(spec.instructions) == 8


def test_rioplatense_yaml_loads() -> None:
    spec = load_spec(EXAMPLES / "brainfuck-rioplatense.yaml")
    assert isinstance(spec, LanguageSpec)
    assert spec.base_machine == BaseMachine.BRAINFUCK_TAPE
    assert spec.encoding == Encoding.WHITESPACE_SEPARATED_TOKENS
    tokens = {i.token for i in spec.instructions}
    # A few of the Spanish surface tokens.
    assert "che" in tokens
    assert "ito" in tokens  # the HALVE addition
    # Includes the HALVE addition on top of the canonical eight.
    ops = {i.op for i in spec.instructions}
    assert InstructionOp.HALVE in ops
    assert len(spec.instructions) == 9
