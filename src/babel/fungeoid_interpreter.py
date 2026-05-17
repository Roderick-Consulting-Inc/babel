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
"""Befunge-93 fungeoid interpreter for the Babel runtime (v0.6.0).

The third Path B base-machine runtime after stack (v0.4.0) and OISC
(v0.4.1). Babel's first 2D execution model.

Fungeoid 2D base machine
=========================

The canonical exemplar is `Befunge-93 <https://esolangs.org/wiki/Befunge>`__.
A fungeoid program is a rectangular grid of ASCII cells, each holding
one instruction character. A directional **instruction pointer** (IP)
starts at ``(0, 0)`` heading right; each step looks up the character at
the IP, dispatches it, and then advances the IP one cell in the current
direction (with toroidal wrap at the grid edges).

The data model is a (separate, conventional) **stack** of integers.
Befunge is a hybrid: 2D control flow + 1D stack data.

Babel's Befunge-93 subset (v0.6.0)
==================================

A focused minimum-viable subset; deferred ops are listed at the bottom
of this docstring.

**Direction (4 ops)**
    ``>`` ``<`` ``^`` ``v`` — set IP direction to right / left / up / down.

**Stack literals (1 op, 10 surface tokens)**
    ``0``–``9`` — push the digit's integer value onto the stack. Each
    digit is a separate ``Instruction`` entry on the parameter sheet,
    all sharing the canonical op ``FUNGEOID_PUSH_DIGIT`` (the schema's
    per-op-uniqueness rule carves this op out — see
    ``LanguageSpec._instructions_unique``). The digit value is encoded
    in the ``Instruction.token`` itself.

**Stack arithmetic & manipulation (7 ops)**
    ``+`` add, ``-`` subtract (pop ``b`` then ``a``, push ``a - b``),
    ``*`` multiply, ``/`` integer divide (pop ``b`` then ``a``; push
    ``a // b``; if ``b == 0`` push ``0`` — Befunge's silent-zero
    convention; the upstream wiki specifies "ask the user" but the
    silent-zero is what every real-world interpreter does), ``:`` dup
    (dup of empty stack pushes ``0``), ``\\`` swap (swap of fewer
    than two elements zero-fills), ``$`` pop (pop of empty stack is a
    no-op).

**I/O (2 ops)**
    ``.`` pop and print as a decimal integer followed by a single
    trailing space (the canonical Befunge-93 ``.`` semantic — every
    real-world interpreter emits the trailing space, and stripping it
    breaks the test corpus). ``,`` pop and print the low byte as an
    ASCII character.

**Conditionals (2 ops)**
    ``_`` horizontal if — pop; if ``0`` head right, else head left.
    ``|`` vertical if — pop; if ``0`` head down, else head up.

**String mode (1 op)**
    ``"`` toggle string mode. While string mode is on, *every* cell
    encountered pushes ``ord(cell_char)`` onto the stack instead of
    dispatching as an op — except another ``"``, which toggles the
    mode back off. The dispatch is therefore: read cell; if string
    mode and the cell is ``"`` toggle off; if string mode push
    ``ord(cell)``; else look up the cell as an op and dispatch.

**Control (3 ops)**
    ``#`` bridge — after dispatch, advance the IP one *extra* cell
    (i.e. skip the next cell). ``@`` halt — end the program cleanly
    (wired via the cross-family ``HALT`` op). Whitespace cells: a
    single space (``" "``) is a no-op; the IP just advances normally.

**Grid layout**
    The source is split on ``\\n`` into rows; each row is padded with
    trailing spaces to the width of the longest row, making the grid
    rectangular. Befunge-93 traditionally uses 80x25, but Babel infers
    dimensions from the source — programs do not have to declare a
    grid size. The IP wraps at all four edges (toroidal: stepping off
    the right edge re-enters at column 0 of the same row, etc.).

    An empty source (zero non-whitespace cells) is a no-op program: the
    interpreter returns immediately without executing any cell.

**Halt**
    Three conditions stop the interpreter:

    * The IP lands on a cell that dispatches to ``HALT`` (Befunge's
      ``@``).
    * ``max_steps`` is exceeded — raises ``FungeoidInterpreterError``.
    * The grid is degenerate (zero cells) — returns immediately.

    Befunge-93 is *not* guaranteed to halt; a torus + IP makes infinite
    loops trivial to write accidentally. The ``max_steps`` cap (default
    100_000, matching the OISC runtime) protects test runs from runaway
    programs.

**Cell width**
    The stack stores Python ints — Befunge-93 is defined for 32-bit
    signed values but in practice the test corpus uses small magnitudes.
    Babel defers cell-width arithmetic wrapping to the consumer: the
    parameter sheet's ``cell_width`` field is recorded in the spec for
    documentation but does not modulus arithmetic results (the analogous
    ``_STACK_MODULUS`` table in ``stack_interpreter`` is not used here
    because Befunge programs rely on wide ranges for ASCII codepoint
    arithmetic). Character output always masks to the low byte.

**Deferred from v0.6.0**
    * ``p`` (put) and ``g`` (get) — self-modifying grid access. Befunge
      programs *can* read or write cells at arbitrary ``(x, y)`` at
      runtime; these ops are part of the standard but have subtle corner
      cases (out-of-bounds writes auto-extend the grid in some dialects)
      and are not needed for the Hello World / arithmetic / string-mode
      tests that ship with v0.6.0.
    * ``?`` — random direction. Trivial to add (one ``rng.choice`` call)
      but introduces non-determinism into the test corpus; deferred for
      a follow-up.
    * ``&`` and ``~`` — read integer / read character from stdin.
      Symmetric to ``.`` / ``,``; deferred for a follow-up.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from enum import Enum
from typing import IO

from babel.schema import (
    BaseMachine,
    Encoding,
    InstructionOp,
    LanguageSpec,
)


class FungeoidInterpreterError(RuntimeError):
    """Raised when fungeoid interpretation fails for a runtime reason."""


class ParseError(FungeoidInterpreterError):
    """Raised when the source can't be parsed against the spec."""


class _Direction(Enum):
    """The four cardinal directions the IP can travel."""

    RIGHT = (1, 0)
    LEFT = (-1, 0)
    UP = (0, -1)
    DOWN = (0, 1)


# Map fungeoid direction ops onto runtime directions.
_OP_TO_DIRECTION: dict[InstructionOp, _Direction] = {
    InstructionOp.FUNGEOID_DIR_RIGHT: _Direction.RIGHT,
    InstructionOp.FUNGEOID_DIR_LEFT: _Direction.LEFT,
    InstructionOp.FUNGEOID_DIR_UP: _Direction.UP,
    InstructionOp.FUNGEOID_DIR_DOWN: _Direction.DOWN,
}


@dataclass
class _Grid:
    """The rectangular 2D source grid (rows of characters, all same width)."""

    rows: list[str]
    width: int
    height: int

    @classmethod
    def from_source(cls, source: str) -> _Grid:
        """Parse ``source`` into a rectangular grid.

        Lines are split on ``\\n``. The grid's width is the longest line's
        length; shorter lines are right-padded with spaces (which dispatch
        to ``FUNGEOID_NOOP``).

        A source with zero lines or a single empty line produces a
        degenerate 0x0 grid; ``run()`` returns immediately for that case.
        """
        if not source:
            return cls(rows=[], width=0, height=0)
        # Splitting on `\n` preserves trailing empty strings if the source
        # ends in newlines; we strip those for the grid-shape purpose
        # (visually-trailing blank rows don't add executable cells).
        raw_rows = source.split("\n")
        # Drop trailing empty rows only — interior empty rows are kept
        # (they become all-space rows in the padded grid).
        while raw_rows and raw_rows[-1] == "":
            raw_rows.pop()
        if not raw_rows:
            return cls(rows=[], width=0, height=0)
        width = max(len(row) for row in raw_rows)
        if width == 0:
            return cls(rows=[], width=0, height=0)
        padded = [row.ljust(width) for row in raw_rows]
        return cls(rows=padded, width=width, height=len(padded))

    def cell(self, x: int, y: int) -> str:
        """Return the character at ``(x, y)``. Bounds are caller responsibility."""
        return self.rows[y][x]


@dataclass
class _IP:
    """The instruction pointer's position and direction."""

    x: int = 0
    y: int = 0
    direction: _Direction = _Direction.RIGHT

    def advance(self, grid: _Grid) -> None:
        """Step one cell in the current direction; wrap toroidally."""
        dx, dy = self.direction.value
        self.x = (self.x + dx) % grid.width
        self.y = (self.y + dy) % grid.height


@dataclass
class _State:
    """The mutable execution state."""

    grid: _Grid
    ip: _IP = field(default_factory=_IP)
    stack: list[int] = field(default_factory=list)
    string_mode: bool = False


def _build_dispatch_table(spec: LanguageSpec) -> dict[str, InstructionOp]:
    """Build a `{cell_char: op}` lookup from the parameter sheet's instructions.

    Befunge's surface encoding is one ASCII character per cell, so every
    spec ``Instruction.token`` must be a single character. The ten
    ``FUNGEOID_PUSH_DIGIT`` entries each carry a distinct digit token —
    the dispatch table preserves the per-character mapping; the op
    handler reads back the cell character to recover the digit value
    (``int(cell)``).

    Raises:
        ParseError: if any token is not a single character.
    """
    table: dict[str, InstructionOp] = {}
    for instr in spec.instructions:
        if len(instr.token) != 1:
            raise ParseError(
                f"fungeoid interpreter requires single-character tokens "
                f"(every cell holds one ASCII char); got token {instr.token!r} "
                f"(length {len(instr.token)}) for op {instr.op.value!r}"
            )
        if instr.arity != 0:
            raise ParseError(
                f"fungeoid interpreter does not support arity > 0 "
                f"(every grid cell is one atom; there is no operand slot); "
                f"got arity={instr.arity} for op {instr.op.value!r}"
            )
        # Duplicate-token validation already lives in
        # `LanguageSpec._instructions_unique`; if we get here, tokens are
        # unique.
        table[instr.token] = instr.op
    return table


def _pop(stack: list[int]) -> int:
    """Befunge pop: empty stack returns 0 (the canonical convention)."""
    if not stack:
        return 0
    return stack.pop()


def run(
    source: str,
    spec: LanguageSpec,
    *,
    stdin: IO[str] | None = None,
    stdout: IO[str] | None = None,
    max_steps: int = 100_000,
) -> None:
    """Execute Befunge-93 ``source`` against ``spec``.

    Parameters:
        source: The program text. Lines are split on ``\\n``; the grid
            is padded with spaces to the longest line's width.
        spec: The validated `LanguageSpec` with ``base_machine=fungeoid_2d``.
        stdin: Reserved for future input ops (``&``, ``~``); not consumed
            by the v0.6.0 op set. Defaults to ``sys.stdin`` for parity
            with the other interpreters.
        stdout: Stream for output (defaults to ``sys.stdout``).
        max_steps: Safety cap on the number of executed cells. Befunge
            is easy to write into infinite loops (the IP wraps); the cap
            (default 100k, matching the OISC runtime) protects test runs
            and CLI sessions from runaway programs.

    Raises:
        ParseError: on malformed spec (multi-character tokens, arity > 0).
        FungeoidInterpreterError: on runtime errors (max_steps exceeded,
            unhandled op, encoding mismatch, base-machine mismatch).
    """
    if spec.base_machine != BaseMachine.FUNGEOID_2D:
        raise FungeoidInterpreterError(
            f"fungeoid interpreter only supports base_machine=fungeoid_2d; "
            f"got {spec.base_machine.value}"
        )
    if spec.encoding != Encoding.TWO_DIMENSIONAL_GRID:
        # The schema's `_check_2d_encoding` already enforces this, but
        # surface a clear runtime error if a spec slips past validation
        # (e.g. constructed in-memory with model_construct).
        raise FungeoidInterpreterError(
            f"fungeoid interpreter requires encoding=two_dimensional_grid; "
            f"got {spec.encoding.value}"
        )

    _ = stdin if stdin is not None else sys.stdin  # reserved for future input ops
    stdout = stdout if stdout is not None else sys.stdout

    dispatch = _build_dispatch_table(spec)
    grid = _Grid.from_source(source)

    # Empty / whitespace-only source: nothing to execute. Return cleanly.
    if grid.width == 0 or grid.height == 0:
        return

    state = _State(grid=grid)

    steps = 0
    while True:
        if steps >= max_steps:
            raise FungeoidInterpreterError(
                f"max_steps={max_steps} exceeded; "
                "fungeoid program may be in an infinite loop"
            )
        steps += 1

        cell = state.grid.cell(state.ip.x, state.ip.y)

        # String mode short-circuit: every cell pushes its codepoint
        # except `"` which toggles back to op mode. The lookup against
        # the dispatch table is bypassed entirely while string mode is
        # on — Befunge programs frequently include arbitrary characters
        # inside string literals that have no defined op semantics.
        if state.string_mode:
            if cell == '"' and dispatch.get(cell) == InstructionOp.FUNGEOID_STRING_MODE_TOGGLE:
                state.string_mode = False
            else:
                state.stack.append(ord(cell))
            state.ip.advance(state.grid)
            continue

        # Op-mode dispatch.
        op = dispatch.get(cell)
        if op is None:
            # Befunge tradition: unknown characters are NOT comments; they
            # would be undefined behaviour. Babel surfaces them as a clear
            # error so that drift between the parameter sheet and source
            # is caught immediately. (If a sheet wants comment-friendly
            # cells, it can map them to FUNGEOID_NOOP.)
            raise FungeoidInterpreterError(
                f"unknown cell character {cell!r} at ({state.ip.x}, {state.ip.y}); "
                f"defined cells are {sorted(dispatch)}"
            )

        # --- Dispatch ---

        if op == InstructionOp.FUNGEOID_NOOP:
            pass  # advance only

        elif op == InstructionOp.FUNGEOID_PUSH_DIGIT:
            # The digit value is the cell character itself.
            state.stack.append(int(cell))

        elif op == InstructionOp.FUNGEOID_DIR_RIGHT:
            state.ip.direction = _Direction.RIGHT
        elif op == InstructionOp.FUNGEOID_DIR_LEFT:
            state.ip.direction = _Direction.LEFT
        elif op == InstructionOp.FUNGEOID_DIR_UP:
            state.ip.direction = _Direction.UP
        elif op == InstructionOp.FUNGEOID_DIR_DOWN:
            state.ip.direction = _Direction.DOWN

        elif op == InstructionOp.FUNGEOID_STACK_ADD:
            b = _pop(state.stack)
            a = _pop(state.stack)
            state.stack.append(a + b)
        elif op == InstructionOp.FUNGEOID_STACK_SUB:
            b = _pop(state.stack)
            a = _pop(state.stack)
            state.stack.append(a - b)
        elif op == InstructionOp.FUNGEOID_STACK_MUL:
            b = _pop(state.stack)
            a = _pop(state.stack)
            state.stack.append(a * b)
        elif op == InstructionOp.FUNGEOID_STACK_DIV:
            b = _pop(state.stack)
            a = _pop(state.stack)
            # Befunge silent-zero convention: divide-by-zero pushes 0
            # rather than raising. The upstream wiki says "ask the user"
            # but no real interpreter implements that.
            state.stack.append(0 if b == 0 else a // b)

        elif op == InstructionOp.FUNGEOID_STACK_DUP:
            # Dup of empty stack pushes 0 (Befunge convention: the
            # "implicit zero" rule extends to dup).
            top = state.stack[-1] if state.stack else 0
            state.stack.append(top)
        elif op == InstructionOp.FUNGEOID_STACK_SWAP:
            # Swap of <2 elements: the missing values are treated as 0.
            b = _pop(state.stack)
            a = _pop(state.stack)
            state.stack.append(b)
            state.stack.append(a)
        elif op == InstructionOp.FUNGEOID_STACK_POP:
            # `$` of an empty stack is a no-op (Befunge convention; the
            # implicit zero pops invisibly).
            if state.stack:
                state.stack.pop()

        elif op == InstructionOp.FUNGEOID_OUTPUT_INT:
            # Befunge `.` emits the integer followed by a single space.
            # The trailing space is part of the spec; stripping it
            # breaks the test corpus.
            value = _pop(state.stack)
            stdout.write(f"{value} ")
            if hasattr(stdout, "flush"):
                stdout.flush()
        elif op == InstructionOp.FUNGEOID_OUTPUT_CHAR:
            value = _pop(state.stack)
            stdout.write(chr(value & 0xFF))
            if hasattr(stdout, "flush"):
                stdout.flush()

        elif op == InstructionOp.FUNGEOID_IF_HORIZONTAL:
            # `_`: pop; if 0 head right, else head left.
            value = _pop(state.stack)
            state.ip.direction = _Direction.RIGHT if value == 0 else _Direction.LEFT
        elif op == InstructionOp.FUNGEOID_IF_VERTICAL:
            # `|`: pop; if 0 head down, else head up.
            value = _pop(state.stack)
            state.ip.direction = _Direction.DOWN if value == 0 else _Direction.UP

        elif op == InstructionOp.FUNGEOID_STRING_MODE_TOGGLE:
            # Turn ON: the string-mode branch above handles toggling OFF.
            state.string_mode = True

        elif op == InstructionOp.FUNGEOID_BRIDGE:
            # `#`: advance one extra cell (skip the next one). The
            # bottom-of-loop advance then runs as normal, for a total of
            # two cells advanced after this dispatch.
            state.ip.advance(state.grid)

        elif op == InstructionOp.HALT:
            return

        else:
            raise FungeoidInterpreterError(
                f"fungeoid interpreter has no dispatch for op {op.value!r}; "
                "this should have been rejected at schema validation time"
            )

        state.ip.advance(state.grid)
