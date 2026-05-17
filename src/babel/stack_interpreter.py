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
"""Parameter-driven interpreter for the stack-machine family (Babel v0.4.0).

Babel's first non-tape base-machine runtime. The interpreter is generic
across any `LanguageSpec` whose ``base_machine`` is ``stack``; dispatch
is on the canonical ``InstructionOp`` values prefixed ``STACK_*`` defined
in `babel.schema`.

Supported ops:

v0.4.0 core:

* ``STACK_PUSH`` (arity 1) — push an integer literal read from the next
  source atom onto the stack.
* ``STACK_POP`` — drop top of stack.
* ``STACK_DUP`` — duplicate top.
* ``STACK_SWAP`` — swap top two.
* ``STACK_ADD`` — pop two, push their sum.
* ``STACK_SUB`` — pop top (``b``), then second (``a``), push ``a - b``.
* ``STACK_OUTPUT_CHAR`` — pop top, write ``chr(value & 0xff)`` to stdout.
* ``STACK_OUTPUT_INT`` — pop top, write ``str(value)`` to stdout.
* ``HALT`` — stop execution.

v0.6.0 additions (FALSE-driven; see `examples/false.yaml`):

* ``STACK_MUL`` — pop two, push their product.
* ``STACK_DIV`` — pop top (``b``), then second (``a``); push ``a // b``
  (Python floor division). Raises ``InterpreterError`` on ``b == 0``.
* ``STACK_NEGATE`` — pop top, push its arithmetic negation.
* ``STACK_EQUALS`` — pop two; push ``-1`` if equal, ``0`` otherwise
  (FALSE/Forth boolean convention).
* ``STACK_GREATER`` — pop top (``b``), second (``a``); push ``-1`` if
  ``a > b`` else ``0``.
* ``STACK_ROT`` — rotate the third-from-top element to the top:
  ``(a b c -- b c a)``.

Supported memory shapes: ``STACK_UNBOUNDED`` (Python list, grows as
needed) and ``STACK_BOUNDED`` (Python list with a configurable cap;
push beyond the cap raises ``InterpreterError``).

The tokenizer is **arity-aware**: at each step it looks up the next
source atom in the spec's instruction table, and if the matched
``Instruction`` has ``arity > 0`` it consumes the next ``arity`` source
atoms as runtime operands. For ``STACK_PUSH`` the operand is parsed as
an integer (Python ``int()``, which means decimal by default and tolerates
``+`` and ``-`` signs); malformed operands raise ``ParseError`` cleanly.

The cell-width axis is interpreted as **integer wrap behaviour** for
arithmetic, mirroring the tape interpreter's `_wrap_cell`: ``BYTE`` is
mod 256, ``WORD`` is mod 2**32, ``NIBBLE`` is mod 16, ``BIT`` is mod 2,
``ARBITRARY`` is Python ints with no modulus. Character output always
masks to the low byte (parallel to the tape side).
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from typing import IO

from babel.interpreter import InterpreterError, ParseError
from babel.schema import (
    BaseMachine,
    CellWidth,
    Encoding,
    InstructionOp,
    LanguageSpec,
    MemoryShape,
)

# Cell-width modulus for stack arithmetic. ARBITRARY uses None.
# Kept in lockstep with `interpreter._CELL_MODULUS`; if the tape side
# adds a new width, mirror it here so the two execution models stay
# consistent.
_STACK_MODULUS: dict[CellWidth, int | None] = {
    CellWidth.BIT: 2,
    CellWidth.NIBBLE: 16,
    CellWidth.BYTE: 256,
    CellWidth.WORD: 2**32,
    CellWidth.ARBITRARY: None,
}


@dataclass
class _ParsedStackOp:
    """One decoded source instruction.

    ``op`` is the canonical operation; ``operand`` is the parsed runtime
    operand (currently always an integer for ``STACK_PUSH``, ``None``
    otherwise). The shape stays a single-element-operand for now; if a
    later stack op needs multiple operands the dataclass widens to a
    tuple without breaking callers that read ``.operand`` for arity-1
    ops.
    """

    op: InstructionOp
    operand: int | None = None


def _tokenize(source: str, spec: LanguageSpec) -> list[_ParsedStackOp]:
    """Convert source text into a flat list of decoded ``_ParsedStackOp``.

    The stack tokenizer is arity-aware: when the matched ``Instruction``
    has ``arity > 0``, the next ``arity`` source atoms are consumed as
    runtime operands. For the v0.4.0 op set only ``STACK_PUSH`` carries
    a non-zero arity (1, parsed as ``int``); the dispatch below already
    generalises so future ops with arity > 1 (or non-integer operands)
    need only a new branch.

    Encoding is ``WHITESPACE_SEPARATED_TOKENS`` for now. Stack languages
    in the corpus (FALSE, Underload) often use ``ASCII_PUNCTUATION`` —
    adding it here is a follow-up sized to a single elif (literal-detection
    via a numeric-pattern regex), explicitly out of scope for v0.4.0's
    minimal demo.
    """
    if spec.encoding != Encoding.WHITESPACE_SEPARATED_TOKENS:
        raise ParseError(
            "stack interpreter currently only supports "
            f"encoding=whitespace_separated_tokens; got {spec.encoding.value}"
        )

    token_to_instr = {i.token: i for i in spec.instructions}
    atoms = source.split()

    parsed: list[_ParsedStackOp] = []
    i = 0
    while i < len(atoms):
        atom = atoms[i]
        if atom not in token_to_instr:
            raise ParseError(
                f"unknown token {atom!r} at atom index {i}; defined tokens are "
                f"{sorted(token_to_instr)}"
            )
        instr = token_to_instr[atom]
        arity = instr.arity
        op = instr.op

        if arity == 0:
            parsed.append(_ParsedStackOp(op=op, operand=None))
            i += 1
            continue

        # Arity > 0: consume the next `arity` atoms as operands.
        if i + arity >= len(atoms):
            raise ParseError(
                f"token {atom!r} at atom index {i} declares arity={arity} but "
                f"only {len(atoms) - i - 1} operand atom(s) follow"
            )

        # Currently only STACK_PUSH consumes an operand, and it's a single
        # integer. The branch is explicit so future op-and-operand pairings
        # (e.g. a label-resolving jump) get a clear extension point.
        if op == InstructionOp.STACK_PUSH:
            if arity != 1:
                raise ParseError(
                    f"STACK_PUSH must have arity=1; got arity={arity} on token {atom!r}"
                )
            raw = atoms[i + 1]
            try:
                value = int(raw)
            except ValueError as e:
                raise ParseError(
                    f"STACK_PUSH operand at atom index {i + 1} is not a valid integer: "
                    f"{raw!r} (token {atom!r})"
                ) from e
            parsed.append(_ParsedStackOp(op=op, operand=value))
            i += 1 + arity
            continue

        raise ParseError(
            f"stack interpreter does not yet know how to consume operands for op "
            f"{op.value!r} (token {atom!r}, arity={arity})"
        )

    return parsed


def parse(source: str, spec: LanguageSpec) -> list[_ParsedStackOp]:
    """Tokenise. Public for testing and for the dispatcher in ``babel.__init__``."""
    return _tokenize(source, spec)


def _new_stack_bound(spec: LanguageSpec, bounded_size: int) -> int | None:
    """Pick the stack cap. ``STACK_UNBOUNDED`` returns None; ``STACK_BOUNDED`` returns size."""
    if spec.memory_shape == MemoryShape.STACK_UNBOUNDED:
        return None
    if spec.memory_shape == MemoryShape.STACK_BOUNDED:
        return bounded_size
    raise InterpreterError(
        f"stack interpreter cannot construct memory for shape {spec.memory_shape.value}"
    )


def _wrap_value(value: int, modulus: int | None) -> int:
    if modulus is None:
        return value
    return value % modulus


def run(
    source: str,
    spec: LanguageSpec,
    *,
    stdin: IO[str] | None = None,
    stdout: IO[str] | None = None,
    bounded_size: int = 4096,
    max_steps: int | None = None,
) -> None:
    """Execute ``source`` against ``spec`` on the stack machine.

    Parameters mirror the tape interpreter's ``run`` for ergonomic parity:

        source: The program text.
        spec: The validated `LanguageSpec` (must have ``base_machine = stack``).
        stdin: Reserved for future input ops; not consumed by the v0.4.0
            op set. Defaults to ``sys.stdin`` for parity with the tape side.
        stdout: Output stream; defaults to ``sys.stdout``.
        bounded_size: Stack cap when ``memory_shape = stack_bounded``.
        max_steps: Optional safety cap on instruction count.

    Raises:
        InterpreterError on runtime errors (stack underflow, overflow,
        unhandled op).
        ParseError on malformed source (unknown token, malformed operand,
        missing operand atoms).
    """
    if spec.base_machine != BaseMachine.STACK:
        raise InterpreterError(
            f"stack interpreter only supports base_machine=stack; "
            f"got {spec.base_machine.value}"
        )
    _ = stdin if stdin is not None else sys.stdin  # reserved for future input ops
    stdout = stdout if stdout is not None else sys.stdout

    program = parse(source, spec)
    cap = _new_stack_bound(spec, bounded_size)
    modulus = _STACK_MODULUS[spec.cell_width]

    stack: list[int] = []

    def _push(value: int) -> None:
        if cap is not None and len(stack) >= cap:
            raise InterpreterError(
                f"stack overflow: depth {len(stack)} would exceed bound {cap}"
            )
        stack.append(_wrap_value(value, modulus))

    def _pop(op_name: str) -> int:
        if not stack:
            raise InterpreterError(f"stack underflow on {op_name}: stack is empty")
        return stack.pop()

    pc = 0
    steps = 0
    while pc < len(program):
        if max_steps is not None and steps >= max_steps:
            raise InterpreterError(f"max_steps={max_steps} exceeded")
        steps += 1
        item = program[pc]
        op = item.op

        if op == InstructionOp.STACK_PUSH:
            assert item.operand is not None  # tokenizer guarantees this
            _push(item.operand)

        elif op == InstructionOp.STACK_POP:
            _pop("STACK_POP")

        elif op == InstructionOp.STACK_DUP:
            if not stack:
                raise InterpreterError("stack underflow on STACK_DUP: stack is empty")
            _push(stack[-1])

        elif op == InstructionOp.STACK_SWAP:
            if len(stack) < 2:
                raise InterpreterError(
                    f"stack underflow on STACK_SWAP: need 2 elements, have {len(stack)}"
                )
            stack[-1], stack[-2] = stack[-2], stack[-1]

        elif op == InstructionOp.STACK_ADD:
            b = _pop("STACK_ADD")
            a = _pop("STACK_ADD")
            _push(a + b)

        elif op == InstructionOp.STACK_SUB:
            b = _pop("STACK_SUB")
            a = _pop("STACK_SUB")
            _push(a - b)

        elif op == InstructionOp.STACK_MUL:
            b = _pop("STACK_MUL")
            a = _pop("STACK_MUL")
            _push(a * b)

        elif op == InstructionOp.STACK_DIV:
            # FALSE-style divide: pop b then a, push a // b. Division by zero
            # is a runtime error (not a silent zero) so source-level bugs
            # surface clearly. Floor division is used for parity with FALSE's
            # integer-stack semantics (Python's `//` on negative operands
            # rounds toward -inf; FALSE programs that rely on a specific
            # truncation discipline should normalise operands first).
            b = _pop("STACK_DIV")
            a = _pop("STACK_DIV")
            if b == 0:
                raise InterpreterError("STACK_DIV: division by zero")
            _push(a // b)

        elif op == InstructionOp.STACK_NEGATE:
            value = _pop("STACK_NEGATE")
            _push(-value)

        elif op == InstructionOp.STACK_EQUALS:
            # FALSE/Forth boolean convention: -1 for true, 0 for false.
            # Under non-ARBITRARY cell widths the -1 wraps to the all-ones
            # bit pattern (255 for BYTE, 2**32-1 for WORD) — intentional,
            # matches how Forth-family languages use the truth value as a
            # bitmask for the (not-yet-implemented) AND / OR ops.
            b = _pop("STACK_EQUALS")
            a = _pop("STACK_EQUALS")
            _push(-1 if a == b else 0)

        elif op == InstructionOp.STACK_GREATER:
            # Same boolean convention as STACK_EQUALS. Comparison uses the
            # values as they sit on the stack (post-wrap if any).
            b = _pop("STACK_GREATER")
            a = _pop("STACK_GREATER")
            _push(-1 if a > b else 0)

        elif op == InstructionOp.STACK_ROT:
            # (a b c -- b c a). Standard Forth/FALSE `@`. Underflow surfaces
            # as a clear runtime error rather than IndexError on `pop`.
            if len(stack) < 3:
                raise InterpreterError(
                    f"stack underflow on STACK_ROT: need 3 elements, have {len(stack)}"
                )
            c = stack.pop()
            b = stack.pop()
            a = stack.pop()
            # Rotation values bypass the cell-width wrap (no arithmetic
            # changes their magnitude) — append directly to avoid double-
            # wrapping values that were already wrapped on push.
            stack.append(b)
            stack.append(c)
            stack.append(a)

        elif op == InstructionOp.STACK_OUTPUT_CHAR:
            value = _pop("STACK_OUTPUT_CHAR")
            stdout.write(chr(value & 0xFF))
            if hasattr(stdout, "flush"):
                stdout.flush()

        elif op == InstructionOp.STACK_OUTPUT_INT:
            value = _pop("STACK_OUTPUT_INT")
            stdout.write(str(value))
            if hasattr(stdout, "flush"):
                stdout.flush()

        elif op == InstructionOp.HALT:
            return

        else:
            raise InterpreterError(
                f"stack interpreter has no dispatch for op {op.value!r}; "
                "this should have been rejected at schema validation time"
            )

        pc += 1
