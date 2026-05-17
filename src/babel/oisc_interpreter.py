# Copyright 2026 Roderick Consulting Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Subleq OISC interpreter for the Babel runtime.

OISC ("One Instruction Set Computer") is the canonical extreme of
instruction-set minimalism: a single instruction does everything.
Babel's first OISC dialect is **Subleq** ("SUbtract and Branch if Less
than or EQual to zero"). See https://esolangs.org/wiki/Subleq.

This module is the runtime counterpart to the schema-level OISC support
added in v0.3.3 (``Instruction.arity``) and v0.4.1 (``InstructionOp.SUBLEQ``,
``BaseMachine.OISC``).

Babel Subleq dialect (v0.4.1)
=============================

**Program format.** The source is a whitespace-separated sequence of
signed integers. Atom count must be a multiple of 3; each consecutive
triple is one ``SUBLEQ a b c`` instruction. Comments are not supported in
v0.4.1 (the parameter sheet's encoding declares plain
``whitespace_separated_tokens``).

**Memory.** The program *is* the memory (the canonical Subleq model is
self-modifying). Memory is a list of arbitrary-precision Python ints
(``CellWidth.ARBITRARY``) — Subleq's correctness arguments depend on
unbounded ints. Out-of-range reads and writes auto-extend the memory with
zeros when the spec's memory shape is ``TAPE_1D_UNBOUNDED``; for
``TAPE_1D_BOUNDED`` they raise ``InterpreterError``.

**Program counter.** PC starts at 0 and points to the *first atom of the
current instruction*, so the natural advance is ``pc += 3``. On a taken
jump, the PC is set to ``c`` directly — ``c`` is therefore the absolute
memory index of the next instruction's first atom, not an "instruction
index". (Subleq variants in the wild use both conventions; Babel picks
the absolute-memory-index convention because it matches the original
Mavaddat & Parhami 1988 formulation and makes self-modifying programs
the most natural to write.) A jump target that is not a multiple of 3
still executes — the loop re-reads ``(a, b, c)`` from the new PC.

**Halt.** Two conditions halt the interpreter cleanly:

* ``c < 0`` after the SUBLEQ semantics fire. This is the standard
  Subleq halt convention.
* PC advances past the end of memory after a non-jumping step.

**I/O.** Babel Subleq treats address ``-1`` as the I/O port, with the
"operand-position" disambiguation that is the most common Subleq
tutorial convention:

* When ``a == -1`` (the source operand is the I/O port), one byte is
  read from stdin and stored at ``mem[b]``. The subtract is skipped.
  On EOF the cell is left unchanged.
* When ``b == -1`` (the destination operand is the I/O port), the low
  byte of ``mem[a]`` is emitted as a character to stdout. The subtract
  is skipped (there is no memory cell at -1 to update).
* When both ``a == -1`` and ``b == -1``: input takes precedence (read
  one byte from stdin and discard it).

After an I/O step the jump still happens normally: if ``c < 0`` we halt;
otherwise the I/O step is treated as if it produced a non-positive
``new_b`` (= 0), so the jump to ``c`` is taken. Treating I/O as
"effectively zero result" matches the convention that an I/O instruction
unconditionally jumps to its branch target — the standard idiom is
``subleq -1, A, NEXT`` (read into A and fall through) or
``subleq A, -1, NEXT`` (print A and fall through) with NEXT pointing at
the next instruction.

Any other negative address (``a < -1`` or ``b < -1``) raises
``OISCInterpreterError``.

**Reference.** See `Subleq <https://esolangs.org/wiki/Subleq>`__ and
`OISC <https://esolangs.org/wiki/OISC>`__ on the esolangs wiki.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from typing import IO

from babel.schema import (
    BaseMachine,
    InstructionOp,
    LanguageSpec,
    MemoryShape,
)


class OISCInterpreterError(RuntimeError):
    """Raised when OISC interpretation fails for a runtime reason."""


class ParseError(OISCInterpreterError):
    """Raised when the source can't be parsed against the spec."""


# The reserved magic address for I/O in Babel Subleq.
IO_PORT: int = -1


@dataclass
class _ParsedProgram:
    """Internal representation of a parsed Subleq source program.

    For Subleq the program *is* the memory: the parser just hands back
    the integer sequence. We keep this as a dataclass for symmetry with
    the BF-tape interpreter (which has the same wrapper).
    """

    memory: list[int]


def parse(source: str, spec: LanguageSpec) -> _ParsedProgram:
    """Tokenise the source into a flat list of signed integers.

    Whitespace-separated; every atom must be a base-10 signed integer.
    Atom count must be divisible by 3 (the SUBLEQ arity).

    Raises:
        ParseError: on non-integer atoms or non-multiple-of-3 atom count.
    """
    # The spec is consulted only to ensure we're being called against an
    # OISC sheet — the dispatch is on the canonical SUBLEQ op, but the
    # parser itself just reads integers. We accept the spec arg for
    # signature parity with the BF-tape interpreter and for future
    # tokenizer hooks (themed digit substitutions, etc.).
    if spec.base_machine != BaseMachine.OISC:
        raise OISCInterpreterError(
            f"oisc interpreter only supports base_machine=oisc; "
            f"got {spec.base_machine.value}"
        )
    atoms = source.split()
    if len(atoms) % 3 != 0:
        raise ParseError(
            f"subleq source atom count must be a multiple of 3 "
            f"(one SUBLEQ instruction = 3 atoms); got {len(atoms)} atoms"
        )
    memory: list[int] = []
    for i, atom in enumerate(atoms):
        try:
            memory.append(int(atom))
        except ValueError as e:
            raise ParseError(
                f"non-integer atom at index {i}: {atom!r}; "
                "subleq sources are whitespace-separated signed integers"
            ) from e
    return _ParsedProgram(memory=memory)


def _read_cell(
    memory: list[int],
    addr: int,
    *,
    shape: MemoryShape,
) -> int:
    """Read memory[addr] (no I/O; non-I/O addresses only). Auto-extends on UNBOUNDED."""
    if addr < 0:
        raise OISCInterpreterError(
            f"read from invalid negative address {addr} "
            f"(the only legal negative address is the I/O port {IO_PORT}, "
            "which is handled at the operand-position level — see the module docstring)"
        )
    if addr >= len(memory):
        if shape == MemoryShape.TAPE_1D_UNBOUNDED:
            # Auto-extend with zeros; the canonical Subleq model assumes
            # an unbounded zero-initialised memory beyond the program.
            return 0
        raise OISCInterpreterError(
            f"read past end of bounded memory: addr={addr}, size={len(memory)}"
        )
    return memory[addr]


def _write_cell(
    memory: list[int],
    addr: int,
    value: int,
    *,
    shape: MemoryShape,
) -> None:
    """Write value to memory[addr] (no I/O; non-I/O addresses only)."""
    if addr < 0:
        raise OISCInterpreterError(
            f"write to invalid negative address {addr} "
            f"(the only legal negative address is the I/O port {IO_PORT}, "
            "which is handled at the operand-position level — see the module docstring)"
        )
    if addr >= len(memory):
        if shape == MemoryShape.TAPE_1D_UNBOUNDED:
            # Extend with zeros up to addr inclusive.
            memory.extend([0] * (addr - len(memory) + 1))
        else:
            raise OISCInterpreterError(
                f"write past end of bounded memory: addr={addr}, size={len(memory)}"
            )
    memory[addr] = value


def _check_op_is_subleq(spec: LanguageSpec) -> None:
    """Runtime guard: every instruction on the OISC spec must be SUBLEQ.

    The schema-level OISC validator (``_check_oisc_shape``) enforces only
    arity=3 — the SUBLEQ op identity wasn't part of the schema in v0.3.3
    (when the placeholder op was JUMP_UNCONDITIONAL) so we accept legacy
    placeholder specs at schema time and reject them here at runtime.
    A clean OISC parameter sheet (like ``examples/subleq.yaml``) uses
    ``op: subleq`` and passes this check trivially.
    """
    non_subleq = [(i.token, i.op.value) for i in spec.instructions if i.op != InstructionOp.SUBLEQ]
    if non_subleq:
        raise OISCInterpreterError(
            "oisc interpreter only dispatches on op=subleq; "
            f"spec wires non-subleq ops on: {non_subleq}"
        )


def run(
    source: str,
    spec: LanguageSpec,
    *,
    stdin: IO[str] | None = None,
    stdout: IO[str] | None = None,
    max_steps: int = 100_000,
) -> None:
    """Execute a Subleq ``source`` against ``spec``.

    Parameters:
        source: The program text — whitespace-separated signed integers.
        spec: The validated `LanguageSpec` with ``base_machine=oisc``.
        stdin: Stream for input (defaults to ``sys.stdin``).
        stdout: Stream for output (defaults to ``sys.stdout``).
        max_steps: Safety cap on the number of executed instructions.
            Subleq programs are easy to write into infinite loops; the
            cap (default 100k) protects test runs and CLI sessions.

    Raises:
        ParseError: on malformed source.
        OISCInterpreterError: on runtime errors (illegal address, step
            cap exceeded, spec wired to a non-SUBLEQ op).
    """
    if spec.base_machine != BaseMachine.OISC:
        raise OISCInterpreterError(
            f"oisc interpreter only supports base_machine=oisc; "
            f"got {spec.base_machine.value}"
        )
    _check_op_is_subleq(spec)

    stdin = stdin if stdin is not None else sys.stdin
    stdout = stdout if stdout is not None else sys.stdout

    program = parse(source, spec)
    memory = program.memory
    shape = spec.memory_shape

    # Empty program: nothing to do. The schema requires at least one
    # Instruction, but a source of length 0 atoms is still legal and is
    # the "do nothing" program.
    if not memory:
        return

    pc = 0
    steps = 0
    while pc < len(memory):
        if steps >= max_steps:
            raise OISCInterpreterError(
                f"max_steps={max_steps} exceeded; subleq program may be in an infinite loop"
            )
        steps += 1

        # Read the (a, b, c) triple. If pc + 3 > len(memory) we have a
        # ragged tail — should not happen because parse() rejects
        # non-multiple-of-3 atom counts, but a jump to (len(memory) - 1)
        # or (len(memory) - 2) could land us in this position. Treat
        # as a halt (PC ran off the end mid-instruction).
        if pc + 3 > len(memory):
            return
        a = memory[pc]
        b = memory[pc + 1]
        c = memory[pc + 2]

        # SUBLEQ semantics (Babel dialect):
        # I/O takes operand-position precedence over the subtract:
        #   a == -1: read one stdin byte into mem[b]; skip subtract.
        #   b == -1: emit low byte of mem[a]; skip subtract.
        # I/O steps treat new_b as 0 (so the c-jump is taken if c >= 0).
        # Halt: c < 0 ends the program cleanly.
        if a == IO_PORT and b == IO_PORT:
            # Read one byte from stdin and discard.
            stdin.read(1)
            new_b = 0
        elif a == IO_PORT:
            # INPUT: read one byte from stdin into mem[b]. On EOF leave
            # mem[b] unchanged (getchar() returning -1 is one convention;
            # leave-unchanged is friendlier for terminating short input
            # streams without polluting memory).
            ch = stdin.read(1)
            if ch != "":
                _write_cell(memory, b, ord(ch) & 0xFF, shape=shape)
            new_b = 0
        elif b == IO_PORT:
            # OUTPUT: emit low byte of mem[a] as a character.
            a_val = _read_cell(memory, a, shape=shape)
            stdout.write(chr(a_val & 0xFF))
            if hasattr(stdout, "flush"):
                stdout.flush()
            new_b = 0
        else:
            # Standard subtract-and-store.
            a_val = _read_cell(memory, a, shape=shape)
            b_val = _read_cell(memory, b, shape=shape)
            new_b = b_val - a_val
            _write_cell(memory, b, new_b, shape=shape)

        if c < 0:
            # Halt convention: c < 0 stops the machine cleanly.
            return
        if new_b <= 0:
            pc = c
        else:
            pc += 3
