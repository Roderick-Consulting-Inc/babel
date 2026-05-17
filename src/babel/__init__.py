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
"""Babel — a parameter-driven generator for esoteric programming languages.

The package exposes the parameter schema (Pydantic models), a YAML loader,
and three output emitters: an interpreter, a transpiler, and a markdown
specification page.

As of v0.4.2 Babel supports three base-machine runtimes end-to-end: the
original Brainfuck-tape family (``base_machine = brainfuck_tape``), the
stack-machine family (``base_machine = stack``, shipped v0.4.0), and the
OISC Subleq family (``base_machine = oisc``, shipped v0.4.1 — wired into
the dispatcher in v0.4.2). The package-level ``run`` function dispatches
on ``spec.base_machine`` and calls the appropriate per-family interpreter;
the per-family modules (`babel.interpreter` for tape,
`babel.stack_interpreter` for stack, `babel.oisc_interpreter` for OISC)
remain importable and continue to enforce their original single-family
contracts.
"""

from __future__ import annotations

from typing import IO

from babel.schema import (
    BaseMachine,
    CellWidth,
    Encoding,
    InstructionOp,
    IOModel,
    LanguageSpec,
    MemoryShape,
    MetaParameters,
)

__version__ = "0.5.1"


def run(
    source: str,
    spec: LanguageSpec,
    *,
    stdin: IO[str] | None = None,
    stdout: IO[str] | None = None,
    **kwargs: object,
) -> None:
    """Dispatch ``source`` to the appropriate per-family interpreter.

    Picks the right runtime based on ``spec.base_machine``:

    * ``brainfuck_tape`` → :func:`babel.interpreter.run`
    * ``stack`` → :func:`babel.stack_interpreter.run`
    * ``oisc`` → :func:`babel.oisc_interpreter.run`
    * any other value → :class:`babel.interpreter.InterpreterError`

    ``**kwargs`` is forwarded to the underlying runtime so callers can
    still pass family-specific options (e.g. ``bounded_size``,
    ``max_steps``, ``rng`` for tape). Options the target runtime doesn't
    accept will surface a clear ``TypeError`` from the target function
    — that's intentional, the dispatcher is a routing layer not a
    parameter validator.

    Existing code that imports ``babel.interpreter.run`` directly keeps
    working unchanged; that entry point retains its tape-only contract
    (raising for non-tape specs). The dispatcher is the new, more
    permissive entry point for callers that want a single-call API
    across families.
    """
    # Local imports avoid a circular reference at package import time
    # (each interpreter module imports from `babel.schema`, which is
    # already loaded at this point, but they also pull in dataclasses
    # and a small surface area — importing lazily keeps `import babel`
    # cheap for callers that only need the schema models).
    from babel import interpreter as tape_interpreter
    from babel import oisc_interpreter as oisc_runtime
    from babel import stack_interpreter as stack_runtime

    if spec.base_machine == BaseMachine.BRAINFUCK_TAPE:
        return tape_interpreter.run(source, spec, stdin=stdin, stdout=stdout, **kwargs)
    if spec.base_machine == BaseMachine.STACK:
        return stack_runtime.run(source, spec, stdin=stdin, stdout=stdout, **kwargs)
    if spec.base_machine == BaseMachine.OISC:
        return oisc_runtime.run(source, spec, stdin=stdin, stdout=stdout, **kwargs)
    raise tape_interpreter.InterpreterError(
        f"no runtime is implemented for base_machine={spec.base_machine.value}; "
        "supported families are brainfuck_tape, stack, and oisc"
    )


__all__ = [
    "BaseMachine",
    "CellWidth",
    "Encoding",
    "InstructionOp",
    "IOModel",
    "LanguageSpec",
    "MemoryShape",
    "MetaParameters",
    "__version__",
    "run",
]
