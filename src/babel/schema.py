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
    # v0.2.0 additions surfaced by the 2026-05-17 interpreter-candidates survey.
    VARIABLE_LENGTH_BINARY = "variable_length_binary"  # Huffman-style; e.g. Spoon
    WORD_LENGTH_DISPATCH = "word_length_dispatch"  # Word-length selects op; e.g. Wordfuck


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

    # v0.2.0 additions surfaced by the 2026-05-17 interpreter-candidates survey.
    # See research-notes/interpreter-candidates-2026-05-17.md (§ "Schema gaps").
    HALT = "halt"  # Explicit program termination (Spoon, La Weá)
    BREAK_LOOP = "break_loop"  # Exit innermost enclosing loop (Brainlove); interpreter NotImplementedError pending runtime support
    JUMP_UNCONDITIONAL = "jump_unconditional"  # Absolute-pc unconditional jump (arity=1); runtime landed in v0.5.0

    # v0.5.1 additions for La Weá and adjacent BF derivatives. Five small
    # tape-family ops that surfaced as gaps when writing the La Weá sheet:
    # the +2/-2 variants `aweonao`/`maraco`, the toggle-buffer op `perkin`,
    # and the integer-mode I/O pair `chúpala`/`brígido`.
    INCREMENT_BY_2 = "increment_by_2"  # cell += 2 (La Weá's `aweonao`)
    DECREMENT_BY_2 = "decrement_by_2"  # cell -= 2 (La Weá's `maraco`)
    CLIPBOARD_TOGGLE = "clipboard_toggle"  # Stateful: if buffer empty store + mark full; if full recall + clear (La Weá's `perkin`)
    OUTPUT_INT = "output_int"  # Emit cell as decimal integer, regardless of IOModel (La Weá's `chúpala`)
    INPUT_INT = "input_int"  # Read decimal integer from stdin, regardless of IOModel (La Weá's `brígido`)

    # v0.4.0 — stack-machine ops (Path B; first non-tape base machine).
    # See research-notes/interpreter-candidates-2026-05-17.md (§ "Stack-machine
    # family"). A deliberately minimal set covering literal push, pop, dup,
    # swap, add/sub, and the two character/integer output flavours. Designed
    # to be extended (mul/div/mod, rot/over/pick, comparisons, conditional
    # branches) in follow-up sheets as concrete stack-language exemplars
    # (FALSE, Underload, Forth subset) land.
    STACK_PUSH = "stack_push"  # Push the operand (arity=1) onto the stack.
    STACK_POP = "stack_pop"  # Drop the top of stack.
    STACK_DUP = "stack_dup"  # Duplicate the top of stack.
    STACK_SWAP = "stack_swap"  # Swap the top two elements.
    STACK_ADD = "stack_add"  # Pop two, push their sum.
    STACK_SUB = "stack_sub"  # Pop top (b) then second (a); push a - b.
    STACK_OUTPUT_CHAR = "stack_output_char"  # Pop top; output as ASCII char.
    STACK_OUTPUT_INT = "stack_output_int"  # Pop top; output as decimal integer.

    # v0.6.0 additions — six stack ops surfaced by the first canonical-wiki
    # stack-language exemplar (FALSE). See `examples/false.yaml` and
    # `research-notes/interpreter-candidates-2026-05-17.md` (§ "Stack-machine
    # family"). FALSE-driven choices:
    #   * STACK_MUL / STACK_DIV are pop-two / push-result; STACK_DIV raises
    #     a clear runtime error on divide-by-zero (no silent zero).
    #   * STACK_NEGATE is FALSE's signature `_` op, kept as a unary primitive
    #     rather than synthesised from `0 swap -` (matches the wiki op set
    #     one-for-one and reads better in the spec page).
    #   * STACK_EQUALS / STACK_GREATER follow FALSE's boolean convention:
    #     push -1 for true, 0 for false (Forth-style; the same bit pattern
    #     also works as a mask for the deferred AND/OR ops).
    #   * STACK_ROT is the standard Forth/FALSE `@` op — bring the third
    #     element to the top: (a b c -- b c a).
    STACK_MUL = "stack_mul"  # Pop two, push their product.
    STACK_DIV = "stack_div"  # Pop top (b) then second (a); push a // b; b==0 raises.
    STACK_NEGATE = "stack_negate"  # Pop top, push its arithmetic negation (FALSE `_`).
    STACK_EQUALS = "stack_equals"  # Pop two; push -1 if equal else 0 (FALSE convention).
    STACK_GREATER = "stack_greater"  # Pop top (b), second (a); push -1 if a > b else 0.
    STACK_ROT = "stack_rot"  # Rotate third-from-top to top: (a b c -- b c a).

    # v0.4.1 addition — OISC (One Instruction Set Computer) base machine.
    # See research-notes/interpreter-candidates-2026-05-17.md Path B
    # ("~50 LOC" runner-up) and src/babel/oisc_interpreter.py.
    SUBLEQ = "subleq"  # SUBLEQ a b c — mem[b] -= mem[a]; if mem[b] <= 0 jump to c.


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
        InstructionOp.HALT,
        InstructionOp.BREAK_LOOP,
        InstructionOp.JUMP_UNCONDITIONAL,
        InstructionOp.INCREMENT_BY_2,
        InstructionOp.DECREMENT_BY_2,
        InstructionOp.CLIPBOARD_TOGGLE,
        InstructionOp.OUTPUT_INT,
        InstructionOp.INPUT_INT,
    }
)

# Ops that move the tape pointer. A tape language must have at least one.
_TAPE_MOBILITY_OPS: frozenset[InstructionOp] = frozenset(
    {InstructionOp.PTR_RIGHT, InstructionOp.PTR_LEFT}
)

# Ops that modify the cell under the pointer. A tape language must have at least one.
_TAPE_CELL_MODIFY_OPS: frozenset[InstructionOp] = frozenset(
    {
        InstructionOp.INCREMENT,
        InstructionOp.DECREMENT,
        InstructionOp.ZERO,
        InstructionOp.HALVE,
        InstructionOp.DOUBLE,
        InstructionOp.CLIPBOARD_RECALL,
        InstructionOp.CLIPBOARD_TOGGLE,
        InstructionOp.RANDOM,
        InstructionOp.INPUT,  # INPUT replaces the cell, counts as a modifier
        InstructionOp.INPUT_INT,
        InstructionOp.INCREMENT_BY_2,
        InstructionOp.DECREMENT_BY_2,
    }
)

# Operations that are only valid on a stack base machine. v0.4.0 ships a
# deliberately minimal core — push/pop/dup/swap, add/sub, and two output
# flavours — large enough to demonstrate the dispatcher and the arity-
# aware tokenizer, small enough that the dispatch table fits on a screen.
# Follow-up sheets (FALSE, Underload, Forth subset) will likely grow this
# set; the discipline is the same as `_TAPE_OPS` — every op enumerated
# here must have a clause in `stack_interpreter._step`.
_STACK_OPS: frozenset[InstructionOp] = frozenset(
    {
        InstructionOp.STACK_PUSH,
        InstructionOp.STACK_POP,
        InstructionOp.STACK_DUP,
        InstructionOp.STACK_SWAP,
        InstructionOp.STACK_ADD,
        InstructionOp.STACK_SUB,
        InstructionOp.STACK_OUTPUT_CHAR,
        InstructionOp.STACK_OUTPUT_INT,
        # v0.6.0 additions — FALSE-driven arithmetic, comparison, and stack
        # rearrangement primitives. The discipline matches the rest of this
        # set: every op enumerated here must have a clause in
        # `stack_interpreter._step` (or, equivalently, in the dispatch chain
        # of `stack_interpreter.run`).
        InstructionOp.STACK_MUL,
        InstructionOp.STACK_DIV,
        InstructionOp.STACK_NEGATE,
        InstructionOp.STACK_EQUALS,
        InstructionOp.STACK_GREATER,
        InstructionOp.STACK_ROT,
        # Cross-family ops legal on a stack machine too.
        InstructionOp.HALT,
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

    ``arity`` (v0.3.3 — the *operand-slot extension* deferred from v0.2.0)
    is the number of additional whitespace-separated source atoms the
    interpreter should consume *after* this token as runtime operands.
    Default 0 covers every Brainfuck-tape op. Non-zero values describe
    languages like Subleq (single op, arity=3 for `SUBLEQ a b c` triples)
    and Minsky counter-machines (arity=1 for `INC R1`, arity=2 for
    `DEC R1 label`). The interpreter is responsible for parsing the
    consumed atoms; the schema only validates that arity is non-negative
    and that tape specs leave it at 0 (the BF-tape interpreter has no
    operand-consumption machinery).
    """

    model_config = ConfigDict(frozen=True)

    token: str = Field(..., min_length=1, description="Surface token in the source language.")
    op: InstructionOp = Field(..., description="Canonical operation this token performs.")
    arity: int = Field(
        default=0,
        ge=0,
        description=(
            "Number of additional source atoms consumed after this token as "
            "runtime operands. Default 0 for tape ops; non-zero for OISC, "
            "register, and other operand-bearing families."
        ),
    )
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
        """A Brainfuck-tape language must have a viable minimum op set.

        v0.2.0 relaxes the prior all-eight-canonical-ops requirement so
        subsetting languages like Boolfuck (no separate DECREMENT — `+`
        toggles the bit) and Smallfuck (no I/O at all) validate. The
        new minimum bar is:

        * At least one pointer-moving op (PTR_RIGHT or PTR_LEFT).
        * At least one cell-modifying op (INCREMENT, DECREMENT, ZERO,
          HALVE, DOUBLE, CLIPBOARD_RECALL, RANDOM, or INPUT).
        * LOOP_START and LOOP_END both present, or both absent
          (the parser's bracket matching depends on this).
        * Any defined op must still be in the tape-legal set.

        I/O is no longer required (Smallfuck has none).
        """
        if self.base_machine != BaseMachine.BRAINFUCK_TAPE:
            return self
        defined_ops = {i.op for i in self.instructions}

        # Extras must still be from the tape-legal set.
        extras = defined_ops - _TAPE_OPS
        if extras:
            raise ValueError(
                "brainfuck_tape language defines operations that don't apply to a tape "
                f"machine: {sorted(o.value for o in extras)}"
            )

        # Mobility: at least one pointer-moving op.
        if not (defined_ops & _TAPE_MOBILITY_OPS):
            raise ValueError(
                "brainfuck_tape language must define at least one pointer-moving op "
                f"({sorted(o.value for o in _TAPE_MOBILITY_OPS)})"
            )

        # Cell modification: at least one cell-modifying op.
        if not (defined_ops & _TAPE_CELL_MODIFY_OPS):
            raise ValueError(
                "brainfuck_tape language must define at least one cell-modifying op "
                f"({sorted(o.value for o in _TAPE_CELL_MODIFY_OPS)})"
            )

        # Balanced loops: both or neither.
        has_start = InstructionOp.LOOP_START in defined_ops
        has_end = InstructionOp.LOOP_END in defined_ops
        if has_start != has_end:
            raise ValueError(
                "brainfuck_tape language must define both LOOP_START and LOOP_END, "
                f"or neither; got LOOP_START={has_start}, LOOP_END={has_end}"
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

    @model_validator(mode="after")
    def _check_oisc_shape(self) -> LanguageSpec:
        """OISC base machines must have SUBLEQ-shaped (arity=3) instructions.

        Babel's OISC dialect (see ``babel.oisc_interpreter`` module docstring)
        is Subleq: one canonical operation with three operands ``a b c``.
        At the schema level we enforce the *arity* part of that shape:
        every instruction on an OISC spec must declare ``arity == 3``.

        The *op identity* (``InstructionOp.SUBLEQ`` vs. another op) is not
        checked here — the v0.3.3 ``test_oisc_subleq_shaped_spec_validates``
        test deliberately seeded a spec with a placeholder op + arity=3
        before the SUBLEQ op existed, and we keep that schema affordance.
        The runtime check (in ``babel.oisc_interpreter``) raises a clear
        error if an OISC spec wires up an op other than ``SUBLEQ``.

        A spec is free to expose more than one *surface token* for the
        Subleq operation (e.g., a token alias for theming) — each token
        still consumes three operand atoms.

        Non-OISC specs are not checked here; only the OISC base is
        constrained, matching the "one instruction set" semantics.
        """
        if self.base_machine != BaseMachine.OISC:
            return self
        bad_arity = [(i.token, i.arity) for i in self.instructions if i.arity != 3]
        if bad_arity:
            raise ValueError(
                "oisc language must have arity=3 on every instruction "
                "(SUBLEQ a b c consumes three operand atoms); "
                f"got non-3 arity on: {bad_arity}"
            )
        return self

    # v0.5.0 — the prior `_check_tape_arity_is_zero` validator was removed
    # when the BF-tape interpreter became arity-aware. Tape ops with arity > 0
    # are now legal (currently only `JUMP_UNCONDITIONAL` uses it, with an
    # integer operand interpreted as the absolute pc target). The tokenizer
    # enforces format constraints (arity > 0 requires whitespace_separated_tokens
    # encoding with single-atom tokens; ascii_punctuation and multi-atom tokens
    # raise ParseError at tokenize time).

    @model_validator(mode="after")
    def _check_stack_ops_legal(self) -> LanguageSpec:
        """A stack-machine language must reference only stack-legal ops.

        Parallel to `_check_brainfuck_tape_completeness` but deliberately
        lighter-weight: there is no canonical-minimum stack op set the way
        there is for Brainfuck (a stack language can be just `PUSH` + one
        output op and still be a valid pedagogical example, as the
        accompanying `examples/minimal-stack.yaml` demonstrates by going
        a little further). The rule we *do* enforce is the negative one:
        a stack spec cannot reference ops that have no defined semantics
        on a stack (e.g. tape pointer movement, BF loop brackets). The
        stack interpreter's dispatch table is the source of truth — see
        ``_STACK_OPS`` above.
        """
        if self.base_machine != BaseMachine.STACK:
            return self
        defined_ops = {i.op for i in self.instructions}
        illegal = defined_ops - _STACK_OPS
        if illegal:
            raise ValueError(
                "stack language defines operations that don't apply to a stack "
                f"machine: {sorted(o.value for o in illegal)}; legal stack ops are "
                f"{sorted(o.value for o in _STACK_OPS)}"
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
