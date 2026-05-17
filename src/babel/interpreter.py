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
"""Parameter-driven interpreter for the Brainfuck-tape family.

The interpreter is generic across any `LanguageSpec` whose
``base_machine`` is ``brainfuck_tape``. The surface tokens come from the
spec; the dispatch is on the canonical ``InstructionOp`` values defined
in `babel.schema`.

For canonical Brainfuck (single-character ASCII punctuation tokens) the
parser walks the source character-by-character; for token-based
encodings (Spanish-keyword skins, etc.) it whitespace-tokenises first
and then walks the token stream. Both cases collapse to the same
internal representation: a list of ``(op, optional_jump_target)`` pairs.

Cell-width support: BIT (mod 2), NIBBLE (mod 16), BYTE (mod 256), WORD
(mod 2**32), ARBITRARY (Python int, no modulus). Memory shape support:
TAPE_1D_UNBOUNDED (auto-grows on the right; left-of-zero raises),
TAPE_1D_CIRCULAR (wraps), TAPE_1D_BOUNDED (default size 30000, raises
on out-of-bounds — Müller's original choice).
"""

from __future__ import annotations

import random
import sys
from dataclasses import dataclass, field
from typing import IO

from babel.schema import (
    BaseMachine,
    CellWidth,
    Encoding,
    InstructionOp,
    IOModel,
    LanguageSpec,
    MemoryShape,
)


class InterpreterError(RuntimeError):
    """Raised when interpretation fails for a runtime reason."""


class ParseError(InterpreterError):
    """Raised when the source can't be parsed against the spec."""


# Cell-width modulus. ARBITRARY uses None (no modulus, Python int).
_CELL_MODULUS: dict[CellWidth, int | None] = {
    CellWidth.BIT: 2,
    CellWidth.NIBBLE: 16,
    CellWidth.BYTE: 256,
    CellWidth.WORD: 2**32,
    CellWidth.ARBITRARY: None,
}


@dataclass
class _ParsedProgram:
    """Internal representation of a parsed source program."""

    ops: list[InstructionOp]
    # For each LOOP_START at index i, jump_table[i] is the matching LOOP_END index, and vice versa.
    jump_table: dict[int, int] = field(default_factory=dict)


def _tokenize(source: str, spec: LanguageSpec) -> list[InstructionOp]:
    """Convert source text into a flat list of canonical ops.

    The two encodings the vertical slice supports:

    * ``ASCII_PUNCTUATION``: tokens are single characters (Müller BF). We
      walk the source character-by-character; characters that are not in
      the instruction table are silently treated as comments — this
      matches the canonical BF convention (and is essential for
      preserving readability of common BF programs that include comments).
    * ``WHITESPACE_SEPARATED_TOKENS``: tokens are whitespace-separated
      strings. Unknown tokens raise ``ParseError`` because in a vocabulary
      skin a typo is almost always a real bug, not a comment.
    """
    token_to_op = {i.token: i.op for i in spec.instructions}

    if spec.encoding == Encoding.ASCII_PUNCTUATION:
        ops: list[InstructionOp] = []
        for ch in source:
            if ch in token_to_op:
                ops.append(token_to_op[ch])
            # else: treat as comment, skip silently
        return ops

    if spec.encoding == Encoding.WHITESPACE_SEPARATED_TOKENS:
        ops = []
        for raw in source.split():
            if raw not in token_to_op:
                raise ParseError(
                    f"unknown token {raw!r}; defined tokens are "
                    f"{sorted(token_to_op)}"
                )
            ops.append(token_to_op[raw])
        return ops

    raise ParseError(
        f"interpreter does not yet support encoding={spec.encoding.value}; "
        "supported encodings are ascii_punctuation and whitespace_separated_tokens"
    )


def _build_jump_table(ops: list[InstructionOp]) -> dict[int, int]:
    """Pre-compute a bracket-matching jump table for [ and ]."""
    stack: list[int] = []
    table: dict[int, int] = {}
    for i, op in enumerate(ops):
        if op == InstructionOp.LOOP_START:
            stack.append(i)
        elif op == InstructionOp.LOOP_END:
            if not stack:
                raise ParseError(f"unmatched loop_end at op index {i}")
            start = stack.pop()
            table[start] = i
            table[i] = start
    if stack:
        raise ParseError(f"unmatched loop_start at op indices {stack}")
    return table


def parse(source: str, spec: LanguageSpec) -> _ParsedProgram:
    """Tokenise + bracket-match. Public for testing and reuse."""
    ops = _tokenize(source, spec)
    table = _build_jump_table(ops)
    return _ParsedProgram(ops=ops, jump_table=table)


@dataclass
class _TapeState:
    """The mutable execution state of a tape machine."""

    cells: list[int]
    ptr: int
    clipboard: int = 0  # only used when CLIPBOARD_* ops are present


def _new_tape(spec: LanguageSpec, bounded_size: int = 30000) -> _TapeState:
    if spec.memory_shape == MemoryShape.TAPE_1D_UNBOUNDED:
        return _TapeState(cells=[0], ptr=0)
    if spec.memory_shape == MemoryShape.TAPE_1D_CIRCULAR:
        return _TapeState(cells=[0] * bounded_size, ptr=0)
    if spec.memory_shape == MemoryShape.TAPE_1D_BOUNDED:
        return _TapeState(cells=[0] * bounded_size, ptr=0)
    raise InterpreterError(
        f"interpreter cannot construct memory for shape {spec.memory_shape.value}"
    )


def _wrap_cell(value: int, modulus: int | None) -> int:
    if modulus is None:
        return value
    return value % modulus


def run(
    source: str,
    spec: LanguageSpec,
    *,
    stdin: IO[str] | None = None,
    stdout: IO[str] | None = None,
    bounded_size: int = 30000,
    max_steps: int | None = None,
    rng: random.Random | None = None,
) -> None:
    """Execute ``source`` against ``spec``.

    Parameters:
        source: The program text in the language defined by ``spec``.
        spec: The validated `LanguageSpec`.
        stdin: Stream for input (defaults to ``sys.stdin``).
        stdout: Stream for output (defaults to ``sys.stdout``).
        bounded_size: Tape length for bounded/circular shapes.
        max_steps: Optional safety cap on instruction count (for tests).
        rng: Optional seeded RNG for the RANDOM op (defaults to
            ``random.Random()`` non-deterministic).

    Raises:
        InterpreterError on runtime errors; ParseError on malformed
        source.
    """
    if spec.base_machine != BaseMachine.BRAINFUCK_TAPE:
        raise InterpreterError(
            f"interpreter currently only supports base_machine=brainfuck_tape; "
            f"got {spec.base_machine.value}"
        )
    stdin = stdin if stdin is not None else sys.stdin
    stdout = stdout if stdout is not None else sys.stdout
    rng = rng if rng is not None else random.Random()

    program = parse(source, spec)
    state = _new_tape(spec, bounded_size=bounded_size)
    modulus = _CELL_MODULUS[spec.cell_width]
    shape = spec.memory_shape
    io_model = spec.io
    ops = program.ops
    jt = program.jump_table

    pc = 0
    steps = 0
    while pc < len(ops):
        if max_steps is not None and steps >= max_steps:
            raise InterpreterError(f"max_steps={max_steps} exceeded")
        steps += 1
        op = ops[pc]

        if op == InstructionOp.PTR_RIGHT:
            state.ptr += 1
            if shape == MemoryShape.TAPE_1D_UNBOUNDED:
                if state.ptr >= len(state.cells):
                    state.cells.append(0)
            elif shape == MemoryShape.TAPE_1D_CIRCULAR:
                state.ptr %= len(state.cells)
            elif shape == MemoryShape.TAPE_1D_BOUNDED:
                if state.ptr >= len(state.cells):
                    raise InterpreterError(
                        f"tape pointer ran past right edge ({state.ptr} >= {len(state.cells)})"
                    )

        elif op == InstructionOp.PTR_LEFT:
            state.ptr -= 1
            if shape == MemoryShape.TAPE_1D_UNBOUNDED:
                if state.ptr < 0:
                    raise InterpreterError("tape pointer ran past left edge")
            elif shape == MemoryShape.TAPE_1D_CIRCULAR:
                state.ptr %= len(state.cells)
            elif shape == MemoryShape.TAPE_1D_BOUNDED:
                if state.ptr < 0:
                    raise InterpreterError("tape pointer ran past left edge")

        elif op == InstructionOp.INCREMENT:
            state.cells[state.ptr] = _wrap_cell(state.cells[state.ptr] + 1, modulus)

        elif op == InstructionOp.DECREMENT:
            state.cells[state.ptr] = _wrap_cell(state.cells[state.ptr] - 1, modulus)

        elif op == InstructionOp.OUTPUT:
            value = state.cells[state.ptr]
            if io_model == IOModel.CHARACTER:
                # BYTE/NIBBLE/BIT all map cleanly to chr() of value & 0xff for output.
                # ARBITRARY/WORD: clamp to the low byte for character output.
                stdout.write(chr(value & 0xFF))
                stdout.flush() if hasattr(stdout, "flush") else None
            elif io_model == IOModel.INTEGER:
                stdout.write(str(value))
            elif io_model == IOModel.NONE:
                pass  # silent
            elif io_model == IOModel.LINE:
                stdout.write(chr(value & 0xFF))
            else:
                raise InterpreterError(f"unsupported io model {io_model.value}")

        elif op == InstructionOp.INPUT:
            if io_model == IOModel.NONE:
                state.cells[state.ptr] = 0
            elif io_model in (IOModel.CHARACTER, IOModel.LINE):
                ch = stdin.read(1)
                if ch == "":  # EOF: leave cell unchanged (BF convention)
                    pass
                else:
                    state.cells[state.ptr] = _wrap_cell(ord(ch), modulus)
            elif io_model == IOModel.INTEGER:
                line = stdin.readline().strip()
                if line == "":
                    pass
                else:
                    try:
                        state.cells[state.ptr] = _wrap_cell(int(line), modulus)
                    except ValueError as e:
                        raise InterpreterError(f"input was not an integer: {line!r}") from e
            else:
                raise InterpreterError(f"unsupported io model {io_model.value}")

        elif op == InstructionOp.LOOP_START:
            if state.cells[state.ptr] == 0:
                pc = jt[pc]  # jump past matching ]

        elif op == InstructionOp.LOOP_END:
            if state.cells[state.ptr] != 0:
                pc = jt[pc]  # jump back to matching [

        elif op == InstructionOp.HALVE:
            # 04 §7 thought-experiment: diminutive-as-halve. Floor division.
            state.cells[state.ptr] = _wrap_cell(state.cells[state.ptr] // 2, modulus)

        elif op == InstructionOp.DOUBLE:
            state.cells[state.ptr] = _wrap_cell(state.cells[state.ptr] * 2, modulus)

        elif op == InstructionOp.ZERO:
            state.cells[state.ptr] = 0

        elif op == InstructionOp.CLIPBOARD_STORE:
            state.clipboard = state.cells[state.ptr]

        elif op == InstructionOp.CLIPBOARD_RECALL:
            state.cells[state.ptr] = state.clipboard

        elif op == InstructionOp.RANDOM:
            if modulus is None:
                # ARBITRARY: pick a small random value
                state.cells[state.ptr] = rng.randint(0, 255)
            else:
                state.cells[state.ptr] = rng.randint(0, modulus - 1)

        elif op == InstructionOp.DEBUG:
            sys.stderr.write(
                f"[debug pc={pc} ptr={state.ptr} cell={state.cells[state.ptr]} "
                f"tape={state.cells[:max(state.ptr + 4, 8)]}]\n"
            )

        elif op == InstructionOp.HALT:
            # Explicit program termination. Used by Spoon, La Weá.
            return

        elif op == InstructionOp.BREAK_LOOP:
            # Exit innermost enclosing loop (Brainlove-style). Needs
            # runtime loop-stack tracking that the current parser doesn't
            # build; deferred until that lands.
            raise InterpreterError(
                "break_loop op is not yet implemented in the interpreter "
                "(schema accepts it for parameter-sheet authoring; runtime "
                "support is a follow-up)"
            )

        elif op == InstructionOp.JUMP_UNCONDITIONAL:
            # Unconditional jump to a target. Needs the Instruction
            # operand slot, which is a separate schema extension.
            raise InterpreterError(
                "jump_unconditional op is not yet implemented in the interpreter "
                "(needs the Instruction operand-slot extension; deferred)"
            )

        else:
            raise InterpreterError(f"unhandled op {op.value}")

        pc += 1
