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
"""Transpile a Babel-spec source program into vanilla Brainfuck.

The transpiler covers the same language family as the interpreter — any
spec whose ``base_machine`` is ``brainfuck_tape``. The output is a
vanilla Brainfuck source string that an external BF interpreter would
accept.

For the canonical-BF parameter sheet the transpile is the identity
transformation (each token is already its vanilla character). For
vocabulary-skin sheets (Spanish keywords, etc.) tokens are mapped back
to their canonical BF characters via the ``op`` field. For sheets with
additions (HALVE, DOUBLE, etc.), each addition is *lowered* to a vanilla
BF idiom that produces the same effect.

The lowering catalogue is small and deliberate: keep it well-tested and
extend it cautiously. Anything not in the catalogue raises a clear
error so a future contributor knows to add the lowering rather than
silently emit a no-op.
"""

from __future__ import annotations

from babel.interpreter import parse
from babel.schema import BaseMachine, InstructionOp, LanguageSpec


class TranspilerError(RuntimeError):
    """Raised when source can't be lowered to vanilla BF."""


# Map each canonical op to its vanilla Brainfuck character (for the eight
# core ops) or to a vanilla-BF idiom that produces the same effect (for
# the additions seen in the corpus).
#
# All idioms assume a 1D unbounded byte tape with wrap-on-overflow
# semantics — the canonical Brainfuck environment. Idioms must leave
# auxiliary cells they touch in their starting state (or at zero) so
# they compose.
_VANILLA_LOWERING: dict[InstructionOp, str] = {
    InstructionOp.PTR_RIGHT: ">",
    InstructionOp.PTR_LEFT: "<",
    InstructionOp.INCREMENT: "+",
    InstructionOp.DECREMENT: "-",
    InstructionOp.OUTPUT: ".",
    InstructionOp.INPUT: ",",
    InstructionOp.LOOP_START: "[",
    InstructionOp.LOOP_END: "]",
    # ZERO: standard BF idiom — zero the current cell.
    InstructionOp.ZERO: "[-]",
    # DOUBLE: x' = 2x. Move x to a temp, then add the temp back twice.
    # Uses the cell to the right as scratch; restores it to 0.
    # Sequence: [->>+<<]>>[-<+<+>>]<< — moves x→t1, then t1→x x times.
    # Simpler: [->+>+<<]>>[-<<+>>]< (uses two scratch cells), or:
    # Conservative one-cell scratch (right neighbour, restored):
    #   >[-]<        ; ensure scratch is zero
    #   [->+<]       ; move x → scratch
    #   >[-<++>]<    ; move scratch back, doubled
    InstructionOp.DOUBLE: ">[-]<[->+<]>[-<++>]<",
    # HALVE: x' = floor(x/2). Implemented via the canonical Brainfuck
    # divmod-by-N algorithm from the esolangs.org wiki [BF Algorithms].
    # Layout used: [x | d | 0 | 0 | 0 | 0] starting at the data pointer,
    # with d = 2 (the divisor we set up). After divmod runs, the cells
    # become [0 | d - x%d | x%d | x/d | 0 | 0]. We then move x/d back
    # into the original cell and clean up the two intermediate scratch
    # values. Cells +1 through +5 must be zero before HALVE runs; the
    # idiom restores them all to zero after. Verified against
    # 0,1,2,3,4,5,10,11,50,100,200,255.
    InstructionOp.HALVE: (
        ">++<"                                      # set divisor cell (p+1) to 2
        "[->-[>+>>]>[+[-<+>]>+>>]<<<<<]"           # canonical divmod
        ">>>[-<<<+>>>]<<<"                          # move quotient (p+3) back to p
        ">[-]>[-]<<"                                # clear p+1 and p+2 scratch leftovers
    ),
    # CLIPBOARD_STORE / CLIPBOARD_RECALL — La Weá-style clipboard. Lowered
    # using a fixed scratch slot far to the right of any reasonable
    # working tape. The lowering is approximate (vanilla BF has no
    # truly-separate register) and is left out of the v0 catalogue;
    # callers needing clipboard semantics should target the interpreter
    # rather than the transpiler. Adding these requires a calling
    # convention for "where the clipboard lives" and is left to a future
    # milestone.
    # RANDOM and DEBUG are not lowerable to deterministic vanilla BF.
}


def transpile(source: str, spec: LanguageSpec) -> str:
    """Transpile ``source`` (in the language defined by ``spec``) to
    vanilla Brainfuck.

    Returns:
        A vanilla BF source string suitable for any conforming BF
        interpreter (canonical 8-instruction, ASCII punctuation).

    Raises:
        TranspilerError if the spec's base machine is not
        ``brainfuck_tape`` or if the source uses an op for which no
        lowering is defined.
    """
    if spec.base_machine != BaseMachine.BRAINFUCK_TAPE:
        raise TranspilerError(
            f"transpiler currently only supports base_machine=brainfuck_tape; "
            f"got {spec.base_machine.value}"
        )
    program = parse(source, spec)
    pieces: list[str] = []
    for op in program.ops:
        if op not in _VANILLA_LOWERING:
            raise TranspilerError(
                f"no vanilla-BF lowering for op {op.value}; the lowering catalogue "
                "in babel/transpiler.py needs to be extended for this op"
            )
        pieces.append(_VANILLA_LOWERING[op])
    return "".join(pieces)


def lowering_catalogue() -> dict[str, str]:
    """Public view of the lowering catalogue, keyed by op name.

    Used by the spec emitter to document which additions are
    transpilable.
    """
    return {op.value: idiom for op, idiom in _VANILLA_LOWERING.items()}
