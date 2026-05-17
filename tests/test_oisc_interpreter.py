# Copyright 2026 Roderick Consulting Inc.
# Licensed under the Apache License, Version 2.0.
"""Tests for the Subleq OISC interpreter (v0.4.1).

Covers the Babel Subleq dialect — semantics, halt convention, I/O port,
parse errors, and the canonical ``examples/subleq.yaml`` parameter sheet.
See the module docstring in ``src/babel/oisc_interpreter.py`` for the
dialect specification.
"""

from __future__ import annotations

import io
from pathlib import Path

import pytest

from babel.loader import load_spec
from babel.oisc_interpreter import (
    OISCInterpreterError,
    ParseError,
    parse,
    run,
)
from babel.schema import (
    BaseMachine,
    Encoding,
    Instruction,
    InstructionOp,
    LanguageSpec,
    MemoryShape,
)

EXAMPLES = Path(__file__).resolve().parent.parent / "examples"


def _oisc_spec() -> LanguageSpec:
    """Minimal in-memory OISC spec for tests that don't need the YAML."""
    return LanguageSpec(
        name="subleq-test",
        base_machine=BaseMachine.OISC,
        memory_shape=MemoryShape.TAPE_1D_UNBOUNDED,
        encoding=Encoding.WHITESPACE_SEPARATED_TOKENS,
        instructions=[
            Instruction(
                token="subleq",
                op=InstructionOp.SUBLEQ,
                arity=3,
                description="SUBLEQ a b c.",
            ),
        ],
    )


# ---------------------------------------------------------------------------
# Empty program
# ---------------------------------------------------------------------------


def test_empty_program_runs_clean() -> None:
    """A source of zero atoms is the do-nothing program."""
    spec = _oisc_spec()
    out = io.StringIO()
    run("", spec, stdin=io.StringIO(""), stdout=out)
    assert out.getvalue() == ""


def test_whitespace_only_program_runs_clean() -> None:
    """Whitespace-only source is also zero atoms — runs clean."""
    spec = _oisc_spec()
    out = io.StringIO()
    run("   \n\t  \n  ", spec, stdin=io.StringIO(""), stdout=out)
    assert out.getvalue() == ""


# ---------------------------------------------------------------------------
# Halt convention — c < 0 stops cleanly
# ---------------------------------------------------------------------------


def test_negative_c_halts_after_one_step() -> None:
    """`0 0 -1` halts after one SUBLEQ step (subtract 0 from 0, halt)."""
    spec = _oisc_spec()
    out = io.StringIO()
    run("0 0 -1", spec, stdin=io.StringIO(""), stdout=out, max_steps=10)
    assert out.getvalue() == ""


def test_pc_runs_off_end_halts_cleanly() -> None:
    """When the c-jump isn't taken and pc advances past the end, halt."""
    spec = _oisc_spec()
    out = io.StringIO()
    # mem[0]=5, mem[1]=10. subleq a=0 b=1 c=99.
    # new_b = 10 - 5 = 5 (> 0), so c-jump NOT taken. pc advances by 3 to 3,
    # which is >= len(memory) = 3 → halt.
    # Memory layout: index 0=5, 1=10, 2=99 (c). After step: mem[1] = 5.
    run("5 10 99", spec, stdin=io.StringIO(""), stdout=out, max_steps=10)
    assert out.getvalue() == ""


# ---------------------------------------------------------------------------
# Decrement-and-halt: a small canonical Subleq program
# ---------------------------------------------------------------------------


def test_decrement_and_halt() -> None:
    """A program that decrements a cell three times then halts.

    Memory layout (12 atoms = 4 triples):
      index 0..2:  9 10 -1     # subleq mem[9]=1 from mem[10]=3 → mem[10]=2. c=-1 if mem[10]≤0.
      But that halts on the first step if mem[10]-1 ≤ 0... we want 3 decrements.

    Cleaner: use a counter at index 9 starting at 3, "one" cell at index 10 = 1.
      For each decrement: subleq one, counter, EXIT_IF_DONE.

    Layout:
      0..2:   10 9 -1   # mem[9] -= mem[10]; if mem[9] <= 0 halt (c = -1)
      3..5:   10 9 -1   # same
      6..8:   10 9 -1   # same
      9:      3         # counter (will be decremented to 0)
      10:     1         # the "one" constant
      11:     0         # padding to keep atom count a multiple of 3

    After step 1: mem[9] = 3 - 1 = 2; new_b > 0; pc → 3.
    After step 2: mem[9] = 2 - 1 = 1; new_b > 0; pc → 6.
    After step 3: mem[9] = 1 - 1 = 0; new_b <= 0; c = -1 → halt.
    """
    spec = _oisc_spec()
    source = "10 9 -1   10 9 -1   10 9 -1   3 1 0"
    out = io.StringIO()
    run(source, spec, stdin=io.StringIO(""), stdout=out, max_steps=20)
    assert out.getvalue() == ""


# ---------------------------------------------------------------------------
# I/O: output a known character
# ---------------------------------------------------------------------------


def test_output_emits_character() -> None:
    """The 'print A' canonical example: emits 'A' and halts."""
    spec = _oisc_spec()
    # See examples/subleq.yaml for the explanation.
    source = "6 -1 3   0 0 -1   65 0 0"
    out = io.StringIO()
    run(source, spec, stdin=io.StringIO(""), stdout=out, max_steps=10)
    assert out.getvalue() == "A"


def test_output_emits_multiple_characters() -> None:
    """Two OUTPUT steps emit 'AB' then halt."""
    spec = _oisc_spec()
    # 4 triples = 12 atoms total.
    #   0..2:  9 -1 3      # print mem[9] = 'A' (65); jump to triple 1
    #   3..5:  10 -1 6     # print mem[10] = 'B' (66); jump to triple 2
    #   6..8:  0 0 -1      # halt
    #   9..11: 65 66 0     # data: 'A', 'B', padding
    source = "9 -1 3   10 -1 6   0 0 -1   65 66 0"
    out = io.StringIO()
    run(source, spec, stdin=io.StringIO(""), stdout=out, max_steps=10)
    assert out.getvalue() == "AB"


def test_input_reads_character_into_memory() -> None:
    """INPUT step reads one byte from stdin into mem[b]."""
    spec = _oisc_spec()
    # 3 triples = 9 atoms.
    #   0..2:  -1 6 3      # INPUT: read stdin byte into mem[6]
    #   3..5:  6 -1 -1     # OUTPUT mem[6]; halt
    #   6..8:  0 0 0       # data slot at 6; padding
    source = "-1 6 3   6 -1 -1   0 0 0"
    out = io.StringIO()
    run(source, spec, stdin=io.StringIO("Z"), stdout=out, max_steps=10)
    assert out.getvalue() == "Z"


# ---------------------------------------------------------------------------
# Parse errors
# ---------------------------------------------------------------------------


def test_non_multiple_of_three_atoms_raises_parse_error() -> None:
    """Subleq requires atom count divisible by 3."""
    spec = _oisc_spec()
    with pytest.raises(ParseError, match="multiple of 3"):
        run("1 2 3 4", spec, stdin=io.StringIO(""), stdout=io.StringIO())


def test_non_integer_atom_raises_parse_error() -> None:
    """Non-integer atoms in a Subleq source are a parse error."""
    spec = _oisc_spec()
    with pytest.raises(ParseError, match="non-integer atom"):
        run("1 foo 3", spec, stdin=io.StringIO(""), stdout=io.StringIO())


def test_parse_returns_int_list() -> None:
    """parse() round-trips signed-int atoms into a flat list."""
    spec = _oisc_spec()
    program = parse("1 -2 3   0 0 -1", spec)
    assert program.memory == [1, -2, 3, 0, 0, -1]


# ---------------------------------------------------------------------------
# Step cap (infinite-loop safety)
# ---------------------------------------------------------------------------


def test_max_steps_caps_runaway_program() -> None:
    """An infinite-loop program is killed by max_steps."""
    spec = _oisc_spec()
    # subleq 0 0 0: subtract mem[0]=0 from mem[0]=0, result 0, jump to 0.
    # Infinite loop.
    with pytest.raises(OISCInterpreterError, match="max_steps"):
        run("0 0 0", spec, stdin=io.StringIO(""), stdout=io.StringIO(), max_steps=5)


# ---------------------------------------------------------------------------
# Spec / runtime guards
# ---------------------------------------------------------------------------


def test_non_oisc_spec_rejected() -> None:
    """run() refuses a non-OISC spec."""
    bf_spec = LanguageSpec(
        name="not-oisc",
        base_machine=BaseMachine.BRAINFUCK_TAPE,
        memory_shape=MemoryShape.TAPE_1D_UNBOUNDED,
        encoding=Encoding.ASCII_PUNCTUATION,
        instructions=[
            Instruction(token=">", op=InstructionOp.PTR_RIGHT),
            Instruction(token="<", op=InstructionOp.PTR_LEFT),
            Instruction(token="+", op=InstructionOp.INCREMENT),
        ],
    )
    with pytest.raises(OISCInterpreterError, match="base_machine=oisc"):
        run("0 0 -1", bf_spec, stdin=io.StringIO(""), stdout=io.StringIO())


def test_oisc_spec_with_non_subleq_op_rejected_at_runtime() -> None:
    """The schema's OISC validator only checks arity; the runtime checks op identity.

    A legacy spec wiring a placeholder op (e.g., JUMP_UNCONDITIONAL) +
    arity=3 will validate at schema time (per v0.3.3 affordance) but
    raise at runtime.
    """
    spec = LanguageSpec(
        name="legacy-oisc",
        base_machine=BaseMachine.OISC,
        memory_shape=MemoryShape.TAPE_1D_UNBOUNDED,
        encoding=Encoding.WHITESPACE_SEPARATED_TOKENS,
        instructions=[
            Instruction(
                token="subleq",
                op=InstructionOp.JUMP_UNCONDITIONAL,  # placeholder, not SUBLEQ
                arity=3,
            ),
        ],
    )
    with pytest.raises(OISCInterpreterError, match="op=subleq"):
        run("0 0 -1", spec, stdin=io.StringIO(""), stdout=io.StringIO())


def test_oisc_spec_rejects_non_arity_3_at_schema_time() -> None:
    """Schema-level: OISC spec must have arity=3 on every instruction."""
    from pydantic import ValidationError

    with pytest.raises(ValidationError, match="arity=3"):
        LanguageSpec(
            name="bad-oisc",
            base_machine=BaseMachine.OISC,
            memory_shape=MemoryShape.TAPE_1D_UNBOUNDED,
            encoding=Encoding.WHITESPACE_SEPARATED_TOKENS,
            instructions=[
                Instruction(token="subleq", op=InstructionOp.SUBLEQ, arity=2),
            ],
        )


# ---------------------------------------------------------------------------
# End-to-end via the canonical examples/subleq.yaml
# ---------------------------------------------------------------------------


def test_subleq_yaml_loads() -> None:
    """examples/subleq.yaml is a valid LanguageSpec."""
    spec = load_spec(EXAMPLES / "subleq.yaml")
    assert spec.base_machine == BaseMachine.OISC
    assert spec.memory_shape == MemoryShape.TAPE_1D_UNBOUNDED
    assert len(spec.instructions) == 1
    assert spec.instructions[0].op == InstructionOp.SUBLEQ
    assert spec.instructions[0].arity == 3


def test_subleq_yaml_halt_example() -> None:
    """The 'Halt immediately' example from subleq.yaml runs to empty output."""
    spec = load_spec(EXAMPLES / "subleq.yaml")
    halt_example = next(e for e in spec.examples if e.title == "Halt immediately")
    out = io.StringIO()
    run(halt_example.source, spec, stdin=io.StringIO(""), stdout=out, max_steps=10)
    assert out.getvalue() == (halt_example.expected_output or "")


def test_subleq_yaml_print_a_example() -> None:
    """The 'Print A' example from subleq.yaml emits 'A'."""
    spec = load_spec(EXAMPLES / "subleq.yaml")
    a_example = next(e for e in spec.examples if e.title.startswith("Print 'A'"))
    out = io.StringIO()
    run(a_example.source, spec, stdin=io.StringIO(""), stdout=out, max_steps=10)
    assert out.getvalue() == a_example.expected_output
