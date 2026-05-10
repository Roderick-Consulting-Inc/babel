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
"""Pydantic models for Babel parameter sheets.

The schema follows §3 and §4 of the methodology paper
(`plans/04-whitepaper-babel.md`):

* §3 enumerates eight mechanical axes — base machine, memory shape, cell
  width, instruction set, encoding, I/O, additions/removals, theming.
* §4 introduces a thinner second layer of meta-parameters — complexity,
  abstraction, verbosity, playfulness, unpredictability, naturalness —
  which describe design intent rather than mechanism.

The schema is intentionally open to base machines beyond the
Brainfuck-tape family; the runtime in this vertical slice only knows how
to interpret/transpile the tape family, but the schema validates other
combinations cleanly so the next milestone can extend without a schema
rewrite.

Illegal *combinations* are rejected by validators at the top level of
`LanguageSpec` — for example, a stack-machine base paired with a
tape-shaped memory.
"""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


# ---------------------------------------------------------------------------
# Enums for the mechanical axes
# ---------------------------------------------------------------------------


class BaseMachine(str, Enum):
    """The abstract execution model. §3 of the paper.

    Only ``brainfuck_tape`` is interpreted/transpiled by the current
    runtime; the other values validate but raise a clear error if you ask
    the interpreter or transpiler to handle them.
    """

    BRAINFUCK_TAPE = "brainfuck_tape"
    STACK = "stack"
    OISC = "oisc"
    FUNGEOID_2D = "fungeoid_2d"
    REGISTER = "register"
    QUEUE = "queue"
    STRING_REWRITING = "string_rewriting"


class MemoryShape(str, Enum):
    """The shape memory takes within a base machine."""

    TAPE_1D_UNBOUNDED = "1d_unbounded"
    TAPE_1D_CIRCULAR = "1d_circular"
    TAPE_1D_BOUNDED = "1d_bounded"
    GRID_2D_TORUS = "2d_torus"
    STACK_UNBOUNDED = "stack_unbounded"
    STACK_BOUNDED = "stack_bounded"
    QUEUE = "queue"
    DEQUE = "deque"
    NAMED_VARIABLES = "named_variables"


class CellWidth(str, Enum):
    """The size of an individual cell."""

    BIT = "bit"
    NIBBLE = "nibble"
    BYTE = "byte"  # 8-bit unsigned, the BF default
    WORD = "word"  # 32-bit
    ARBITRARY = "arbitrary"


class Encoding(str, Enum):
    """How instructions are encoded in source text."""

    ASCII_PUNCTUATION = "ascii_punctuation"
    WHITESPACE_SEPARATED_TOKENS = "whitespace_separated_tokens"
    UNARY = "unary"
    BINARY = "binary"
    TWO_DIMENSIONAL_GRID = "two_dimensional_grid"


class IOModel(str, Enum):
    """Input/output model."""

    CHARACTER = "character"
    LINE = "line"
    INTEGER = "integer"
    NONE = "none"


class InstructionOp(str, Enum):
    """The canonical operation an instruction performs.

    These names are runtime-stable: the interpreter dispatches on these,
    and a derivative language is defined (in part) by mapping its surface
    tokens onto this set. The first eight cover canonical Brainfuck;
    further values are the additions seen in the corpus (HALVE for the
    diminutive thought-experiment in 04 §7, CLIPBOARD_STORE/RECALL for
    La Weá, etc.).
    """

    # Canonical Brainfuck tape operations
    PTR_RIGHT = "ptr_right"
    PTR_LEFT = "ptr_left"
    INCREMENT = "increment"
    DECREMENT = "decrement"
    OUTPUT = "output"
    INPUT = "input"
    LOOP_START = "loop_start"
    LOOP_END = "loop_end"

    # Common additions seen in the corpus
    HALVE = "halve"  # Rioplatense diminutive thought-experiment, 04 §7
    DOUBLE = "double"
    ZERO = "zero"
    CLIPBOARD_STORE = "clipboard_store"  # La Weá
    CLIPBOARD_RECALL = "clipboard_recall"  # La Weá
    RANDOM = "random"  # Chespirito
    DEBUG = "debug"


# Operations that are only valid on a Brainfuck-tape base machine.
_TAPE_OPS: frozenset[InstructionOp] = frozenset(
    {
        InstructionOp.PTR_RIGHT,
        InstructionOp.PTR_LEFT,
        InstructionOp.INCREMENT,
        InstructionOp.DECREMENT,
        InstructionOp.OUTPUT,
        InstructionOp.INPUT,
        InstructionOp.LOOP_START,
        InstructionOp.LOOP_END,
        InstructionOp.HALVE,
        InstructionOp.DOUBLE,
        InstructionOp.ZERO,
        InstructionOp.CLIPBOARD_STORE,
        InstructionOp.CLIPBOARD_RECALL,
        InstructionOp.RANDOM,
        InstructionOp.DEBUG,
    }
)

# The eight canonical Brainfuck operations — the minimum a tape language must define.
_CANONICAL_BF_OPS: frozenset[InstructionOp] = frozenset(
    {
        InstructionOp.PTR_RIGHT,
        InstructionOp.PTR_LEFT,
        InstructionOp.INCREMENT,
        InstructionOp.DECREMENT,
        InstructionOp.OUTPUT,
        InstructionOp.INPUT,
        InstructionOp.LOOP_START,
        InstructionOp.LOOP_END,
    }
)


# Memory shapes legal for each base machine.
_LEGAL_MEMORY_FOR_BASE: dict[BaseMachine, set[MemoryShape]] = {
    BaseMachine.BRAINFUCK_TAPE: {
        MemoryShape.TAPE_1D_UNBOUNDED,
        MemoryShape.TAPE_1D_CIRCULAR,
        MemoryShape.TAPE_1D_BOUNDED,
    },
    BaseMachine.STACK: {
        MemoryShape.STACK_UNBOUNDED,
        MemoryShape.STACK_BOUNDED,
    },
    BaseMachine.OISC: {
        MemoryShape.TAPE_1D_UNBOUNDED,
        MemoryShape.TAPE_1D_BOUNDED,
        MemoryShape.NAMED_VARIABLES,
    },
    BaseMachine.FUNGEOID_2D: {
        MemoryShape.GRID_2D_TORUS,
        MemoryShape.STACK_UNBOUNDED,
    },
    BaseMachine.REGISTER: {MemoryShape.NAMED_VARIABLES},
    BaseMachine.QUEUE: {MemoryShape.QUEUE, MemoryShape.DEQUE},
    BaseMachine.STRING_REWRITING: {MemoryShape.NAMED_VARIABLES},
}


# ---------------------------------------------------------------------------
# Sub-models
# ---------------------------------------------------------------------------


class Instruction(BaseModel):
    """One surface token in the language and the operation it triggers.

    ``token`` is the literal string the source code uses; ``op`` is the
    canonical operation the interpreter dispatches on. ``description`` is
    optional human-readable text for the spec page.
    """

    model_config = ConfigDict(frozen=True)

    token: str = Field(..., min_length=1, description="Surface token in the source language.")
    op: InstructionOp = Field(..., description="Canonical operation this token performs.")
    description: str | None = Field(
        default=None, description="Human-readable description for the spec page."
    )


class MetaParameters(BaseModel):
    """The thinner second layer of design-intent parameters (§4).

    All six are optional and validate to bounded ranges; nothing in the
    current runtime *drives* code generation from these values — they
    appear in the generated spec page so the design intent is captured
    alongside the mechanism. A future installment may refine
    ``naturalness`` into sub-parameters (the paper flags it as too
    coarse).
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    complexity: str | None = Field(
        default=None,
        description="Cognitive cost of writing a non-trivial program. low / medium / high.",
    )
    abstraction: str | None = Field(
        default=None,
        description="Gap between surface syntax and execution model. low / medium / high.",
    )
    verbosity: str | None = Field(
        default=None,
        description="Bytes per logical operation. compact / medium / verbose / hyper.",
    )
    playfulness: str | None = Field(
        default=None,
        description="Self-conscious humour or theatricality. low / moderate / high.",
    )
    unpredictability: str | None = Field(
        default=None,
        description="Determinism. zero / low / moderate / high.",
    )
    naturalness: str | None = Field(
        default=None,
        description=(
            "How closely the surface syntax follows a natural-language grammar. "
            "none / vocabulary / lexical_grammar / deep_grammar. (The paper notes "
            "this axis is too coarse and flags it for refinement.)"
        ),
    )

    @field_validator("complexity", "abstraction", "playfulness")
    @classmethod
    def _check_low_med_high(cls, v: str | None) -> str | None:
        if v is None:
            return v
        allowed = {"low", "medium", "high", "moderate"}
        if v not in allowed:
            raise ValueError(f"must be one of {sorted(allowed)}, got {v!r}")
        return v

    @field_validator("verbosity")
    @classmethod
    def _check_verbosity(cls, v: str | None) -> str | None:
        if v is None:
            return v
        allowed = {"compact", "medium", "verbose", "hyper"}
        if v not in allowed:
            raise ValueError(f"must be one of {sorted(allowed)}, got {v!r}")
        return v

    @field_validator("unpredictability")
    @classmethod
    def _check_unpredictability(cls, v: str | None) -> str | None:
        if v is None:
            return v
        allowed = {"zero", "low", "moderate", "high"}
        if v not in allowed:
            raise ValueError(f"must be one of {sorted(allowed)}, got {v!r}")
        return v

    @field_validator("naturalness")
    @classmethod
    def _check_naturalness(cls, v: str | None) -> str | None:
        if v is None:
            return v
        allowed = {"none", "vocabulary", "lexical_grammar", "deep_grammar"}
        if v not in allowed:
            raise ValueError(f"must be one of {sorted(allowed)}, got {v!r}")
        return v


# ---------------------------------------------------------------------------
# Top-level spec
# ---------------------------------------------------------------------------


class LanguageSpec(BaseModel):
    """A complete Babel parameter sheet — the input the runtime consumes.

    Fields map onto §3 of the paper directly, with a ``meta`` block for
    §4. The cross-field validators reject the combinations that don't
    make sense (e.g., ``base_machine = stack`` paired with
    ``memory_shape = 1d_unbounded``).
    """

    model_config = ConfigDict(extra="forbid")

    name: str = Field(..., min_length=1, description="Human-readable language name.")
    version: str = Field(default="0.1.0", description="Specification version.")
    description: str | None = Field(
        default=None, description="One-paragraph summary; appears in the spec page Overview."
    )

    # Mechanical axes (§3)
    base_machine: BaseMachine
    memory_shape: MemoryShape
    cell_width: CellWidth = CellWidth.BYTE
    instructions: list[Instruction] = Field(..., min_length=1)
    encoding: Encoding
    io: IOModel = IOModel.CHARACTER
    additions: list[str] = Field(default_factory=list)
    removals: list[str] = Field(default_factory=list)
    theme: str | None = Field(default=None, description="Cultural/surface theme, if any.")

    # Meta layer (§4) — design intent, not mechanism
    meta: MetaParameters = Field(default_factory=MetaParameters)

    # Optional source-file extension hint for the generated language
    source_extension: str | None = Field(
        default=None,
        description="Conventional file extension for source files in this language (e.g. '.bf').",
    )

    # Examples included in the spec page
    examples: list[ExampleProgram] = Field(default_factory=list)

    @field_validator("instructions")
    @classmethod
    def _instructions_unique(cls, v: list[Instruction]) -> list[Instruction]:
        tokens = [i.token for i in v]
        if len(set(tokens)) != len(tokens):
            duplicates = sorted({t for t in tokens if tokens.count(t) > 1})
            raise ValueError(f"duplicate instruction tokens: {duplicates}")
        ops = [i.op for i in v]
        if len(set(ops)) != len(ops):
            duplicates = sorted({o.value for o in ops if ops.count(o) > 1})
            raise ValueError(f"duplicate instruction ops: {duplicates}")
        return v

    @model_validator(mode="after")
    def _check_machine_memory_pairing(self) -> LanguageSpec:
        legal = _LEGAL_MEMORY_FOR_BASE.get(self.base_machine, set())
        if self.memory_shape not in legal:
            raise ValueError(
                f"illegal combination: base_machine={self.base_machine.value} cannot use "
                f"memory_shape={self.memory_shape.value}; legal shapes for this base are "
                f"{sorted(s.value for s in legal)}"
            )
        return self

    @model_validator(mode="after")
    def _check_brainfuck_tape_completeness(self) -> LanguageSpec:
        """A Brainfuck-tape language must define all eight canonical ops.

        Subsetting (e.g., Boolfuck removing certain ops) is left as a
        future schema extension; for the vertical slice we require the
        full canonical set so the interpreter has well-defined semantics.
        """
        if self.base_machine != BaseMachine.BRAINFUCK_TAPE:
            return self
        defined_ops = {i.op for i in self.instructions}
        missing = _CANONICAL_BF_OPS - defined_ops
        if missing:
            raise ValueError(
                "brainfuck_tape language is missing canonical operations: "
                f"{sorted(o.value for o in missing)}"
            )
        # Any extra ops must still be from the tape-legal set.
        extras = defined_ops - _TAPE_OPS
        if extras:
            raise ValueError(
                "brainfuck_tape language defines operations that don't apply to a tape "
                f"machine: {sorted(o.value for o in extras)}"
            )
        return self

    @model_validator(mode="after")
    def _check_2d_encoding(self) -> LanguageSpec:
        """A 2D fungeoid base must use the 2D-grid encoding."""
        if (
            self.base_machine == BaseMachine.FUNGEOID_2D
            and self.encoding != Encoding.TWO_DIMENSIONAL_GRID
        ):
            raise ValueError(
                f"fungeoid_2d base machine requires encoding=two_dimensional_grid, "
                f"got {self.encoding.value}"
            )
        return self


class ExampleProgram(BaseModel):
    """An example program for the spec page."""

    model_config = ConfigDict(frozen=True)

    title: str = Field(..., min_length=1)
    source: str = Field(..., min_length=1, description="Program source in the generated language.")
    expected_output: str | None = Field(
        default=None, description="Expected output, if known (used in the spec page)."
    )
    description: str | None = None


# Resolve the forward reference declared on LanguageSpec.examples.
LanguageSpec.model_rebuild()
