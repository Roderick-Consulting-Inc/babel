# Copyright 2026 Roderick Consulting Inc.
# Licensed under the Apache License, Version 2.0.
"""Schema tests for v0.3.3's Instruction.arity field (operand-slot extension).

The arity field reserves the schema's ability to describe operand-bearing
instructions for the OISC and register families. The interpreter doesn't
consume the field yet (BF-tape ops have arity=0 by definition; non-tape
runtimes that need arity arrive with the stack-machine extension). These
tests verify the schema accepts, validates, and constrains the field
correctly so downstream parameter-sheet authors can already use it.
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from babel.schema import (
    BaseMachine,
    Encoding,
    Instruction,
    InstructionOp,
    LanguageSpec,
    MemoryShape,
)


def _bf_spec(extra_instructions: list[Instruction] | None = None) -> LanguageSpec:
    base = [
        Instruction(token=">", op=InstructionOp.PTR_RIGHT),
        Instruction(token="<", op=InstructionOp.PTR_LEFT),
        Instruction(token="+", op=InstructionOp.INCREMENT),
        Instruction(token="-", op=InstructionOp.DECREMENT),
        Instruction(token=".", op=InstructionOp.OUTPUT),
        Instruction(token=",", op=InstructionOp.INPUT),
        Instruction(token="[", op=InstructionOp.LOOP_START),
        Instruction(token="]", op=InstructionOp.LOOP_END),
    ]
    return LanguageSpec(
        name="bf-test",
        base_machine=BaseMachine.BRAINFUCK_TAPE,
        memory_shape=MemoryShape.TAPE_1D_UNBOUNDED,
        encoding=Encoding.ASCII_PUNCTUATION,
        instructions=base + (extra_instructions or []),
    )


# ---------------------------------------------------------------------------
# Default arity is 0 and unchanged behaviour
# ---------------------------------------------------------------------------


def test_instruction_default_arity_is_zero() -> None:
    """Constructing an Instruction without arity sets it to 0 (backward-compatible)."""
    instr = Instruction(token="+", op=InstructionOp.INCREMENT)
    assert instr.arity == 0


def test_existing_bf_spec_unchanged() -> None:
    """A canonical BF spec built without arity still validates and runs."""
    spec = _bf_spec()
    assert all(i.arity == 0 for i in spec.instructions)


# ---------------------------------------------------------------------------
# Arity validation: non-negative integer
# ---------------------------------------------------------------------------


def test_negative_arity_rejected() -> None:
    with pytest.raises(ValidationError, match="greater than or equal to 0"):
        Instruction(token="x", op=InstructionOp.INCREMENT, arity=-1)


def test_explicit_zero_arity_accepted() -> None:
    instr = Instruction(token="+", op=InstructionOp.INCREMENT, arity=0)
    assert instr.arity == 0


# ---------------------------------------------------------------------------
# Tape spec rejects non-zero arity
# ---------------------------------------------------------------------------


def test_tape_spec_rejects_nonzero_arity() -> None:
    """BF-tape interpreter has no operand-consumption; tape specs must keep arity=0."""
    with pytest.raises(ValidationError, match="arity=0 on every instruction"):
        _bf_spec(
            extra_instructions=[
                Instruction(token="j", op=InstructionOp.JUMP_UNCONDITIONAL, arity=1),
            ]
        )


# ---------------------------------------------------------------------------
# Non-tape spec accepts arity > 0 (OISC Subleq-shaped example)
# ---------------------------------------------------------------------------


def test_oisc_subleq_shaped_spec_validates() -> None:
    """A Subleq-style spec (single op, arity 3 for the a/b/c triple) validates.

    Babel can't interpret OISC yet — the stack/OISC runtime extension lands
    later — but the *schema* needs to accept Subleq-shaped instructions
    today so parameter-sheet authors can write them.
    """
    spec = LanguageSpec(
        name="subleq-test",
        base_machine=BaseMachine.OISC,
        memory_shape=MemoryShape.TAPE_1D_UNBOUNDED,
        encoding=Encoding.WHITESPACE_SEPARATED_TOKENS,
        instructions=[
            # Subleq has one implicit instruction; in Babel's model we name it
            # with a placeholder token. The arity=3 means each occurrence of
            # the token consumes 3 source atoms as runtime operands.
            Instruction(
                token="subleq",
                op=InstructionOp.JUMP_UNCONDITIONAL,  # placeholder op until OISC ops land
                arity=3,
                description="SUBLEQ a b c: subtract b from a, store, jump to c if result ≤ 0.",
            ),
        ],
    )
    assert spec.instructions[0].arity == 3


def test_minsky_register_shaped_spec_validates() -> None:
    """A Minsky-style register-machine spec (INC R, DEC R label) validates."""
    spec = LanguageSpec(
        name="minsky-test",
        base_machine=BaseMachine.REGISTER,
        memory_shape=MemoryShape.NAMED_VARIABLES,
        encoding=Encoding.WHITESPACE_SEPARATED_TOKENS,
        instructions=[
            Instruction(
                token="INC",
                op=InstructionOp.INCREMENT,
                arity=1,
                description="INC R: increment register R.",
            ),
            Instruction(
                token="DEC",
                op=InstructionOp.DECREMENT,
                arity=2,
                description="DEC R label: decrement register R; if R was zero, jump to label.",
            ),
            Instruction(
                token="HALT",
                op=InstructionOp.HALT,
                arity=0,
                description="HALT: stop execution.",
            ),
        ],
    )
    arities = {i.token: i.arity for i in spec.instructions}
    assert arities == {"INC": 1, "DEC": 2, "HALT": 0}
