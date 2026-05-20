# Copyright 2026 Roderick Consulting Inc.
# Licensed under the Apache License, Version 2.0.
"""Tests for the Markdown specification-page generator."""

from __future__ import annotations

from pathlib import Path

import pytest

from babel.loader import load_spec
from babel.schema import LanguageSpec
from babel.spec import render_spec

EXAMPLES = Path(__file__).resolve().parent.parent / "examples"


@pytest.fixture()
def vanilla() -> LanguageSpec:
    return load_spec(EXAMPLES / "brainfuck-vanilla.yaml")


@pytest.fixture()
def rioplatense() -> LanguageSpec:
    return load_spec(EXAMPLES / "brainfuck-rioplatense.yaml")


def test_spec_starts_with_title_and_version(vanilla: LanguageSpec) -> None:
    out = render_spec(vanilla)
    first_line = out.splitlines()[0]
    assert first_line.startswith("# ")
    assert vanilla.name in first_line
    assert f"Version {vanilla.version}" in out


def test_spec_includes_all_mechanical_axes(vanilla: LanguageSpec) -> None:
    out = render_spec(vanilla)
    assert "Base machine" in out
    assert "Memory shape" in out
    assert "Cell width" in out
    assert "Encoding" in out
    assert "I/O model" in out
    assert vanilla.base_machine.value in out
    assert vanilla.encoding.value in out


def test_spec_includes_every_instruction(vanilla: LanguageSpec) -> None:
    out = render_spec(vanilla)
    for inst in vanilla.instructions:
        # Every token must appear, wrapped in backticks.
        assert f"`{inst.token}`" in out
        # Every canonical op name must appear.
        assert inst.op.value in out


def test_spec_renders_additions_and_descriptions(rioplatense: LanguageSpec) -> None:
    out = render_spec(rioplatense)
    # The Rioplatense sheet adds halve_via_diminutive_suffix.
    assert "halve_via_diminutive_suffix" in out
    # Description column is present and populated.
    assert "Advance the data pointer" in out
    # Theme appears in the mechanical section.
    assert "rioplatense_argentine" in out


def test_spec_renders_meta_parameters(rioplatense: LanguageSpec) -> None:
    out = render_spec(rioplatense)
    assert "Meta-parameters" in out
    # The Rioplatense sheet has six meta values set.
    for value in ("medium", "low", "verbose", "moderate", "zero", "vocabulary"):
        assert value in out


def test_spec_renders_example_programs(rioplatense: LanguageSpec) -> None:
    out = render_spec(rioplatense)
    # Both example titles must appear.
    assert "Print the letter A" in out
    assert "Halve and print" in out
    # The fence-info hint comes from the source extension (bfri).
    assert "```bfri" in out
    # Expected output renders as a fenced block.
    assert "Expected output" in out


def test_spec_handles_empty_meta() -> None:
    # Hand-construct a minimal spec that has no meta values set.
    from babel.schema import (
        BaseMachine,
        CellWidth,
        Encoding,
        Instruction,
        InstructionOp,
        IOModel,
        MemoryShape,
        MetaParameters,
    )

    spec = LanguageSpec(
        name="MinimalTest",
        base_machine=BaseMachine.BRAINFUCK_TAPE,
        memory_shape=MemoryShape.TAPE_1D_UNBOUNDED,
        cell_width=CellWidth.BYTE,
        encoding=Encoding.ASCII_PUNCTUATION,
        io=IOModel.CHARACTER,
        instructions=[
            Instruction(token=">", op=InstructionOp.PTR_RIGHT),
            Instruction(token="<", op=InstructionOp.PTR_LEFT),
            Instruction(token="+", op=InstructionOp.INCREMENT),
            Instruction(token="-", op=InstructionOp.DECREMENT),
            Instruction(token=".", op=InstructionOp.OUTPUT),
            Instruction(token=",", op=InstructionOp.INPUT),
            Instruction(token="[", op=InstructionOp.LOOP_START),
            Instruction(token="]", op=InstructionOp.LOOP_END),
        ],
        meta=MetaParameters(),
    )
    out = render_spec(spec)
    assert "No meta-parameters set on this sheet" in out


def test_spec_does_not_render_examples_section_if_none(vanilla: LanguageSpec) -> None:
    # The vanilla BF sheet ships no examples block.
    if not vanilla.examples:
        out = render_spec(vanilla)
        assert "## Example programs" not in out


def test_spec_table_pipes_in_token_are_escaped() -> None:
    """Pipe characters inside a token break Markdown tables unless escaped."""
    from babel.schema import (
        BaseMachine,
        CellWidth,
        Encoding,
        Instruction,
        InstructionOp,
        IOModel,
        MemoryShape,
    )

    # The legal token set for tape ops doesn't forbid `|`; we'd never ship
    # such a sheet, but a paranoid renderer should still escape.
    spec = LanguageSpec(
        name="PipeTest",
        base_machine=BaseMachine.BRAINFUCK_TAPE,
        memory_shape=MemoryShape.TAPE_1D_UNBOUNDED,
        cell_width=CellWidth.BYTE,
        encoding=Encoding.WHITESPACE_SEPARATED_TOKENS,
        io=IOModel.CHARACTER,
        instructions=[
            Instruction(token=">", op=InstructionOp.PTR_RIGHT),
            Instruction(token="<", op=InstructionOp.PTR_LEFT),
            Instruction(token="up|down", op=InstructionOp.INCREMENT),
            Instruction(token="-", op=InstructionOp.DECREMENT),
            Instruction(token=".", op=InstructionOp.OUTPUT),
            Instruction(token=",", op=InstructionOp.INPUT),
            Instruction(token="[", op=InstructionOp.LOOP_START),
            Instruction(token="]", op=InstructionOp.LOOP_END),
        ],
    )
    out = render_spec(spec)
    assert r"up\|down" in out


def test_cli_spec_subcommand(rioplatense: LanguageSpec, capsys) -> None:
    from babel.__main__ import main

    rc = main(["spec", str(EXAMPLES / "brainfuck-rioplatense.yaml")])
    assert rc == 0
    captured = capsys.readouterr()
    assert "# Brainfuck Rioplatense — Specification" in captured.out
    assert "Print the letter A" in captured.out
