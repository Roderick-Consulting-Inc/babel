# Changelog

All notable changes to the Babel runtime are recorded here. Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versions follow [Semantic Versioning](https://semver.org/spec/v2.0.0.html). The runtime is pre-1.0; the schema and API may change between minor versions.

## [0.7.0] — 2026-05-17

### Added

- **Witness / tracing hook on every interpreter.** All four `run()` functions (`babel.interpreter`, `babel.stack_interpreter`, `babel.oisc_interpreter`, `babel.fungeoid_interpreter`) gained an optional `trace_hook: Callable[[dict], None] | None = None` keyword argument. When non-None, the hook fires once per executed instruction with a family-specific state snapshot:
  - **BF-tape** → `{step, pc, op, operand, ptr_before, cell_before, ptr_after, cell_after, cells_window, window_offset, emit}`
  - **Stack / FALSE** → `{step, pc, op, operand, stack_before, stack_after, emit}`
  - **OISC (Subleq)** → `{step, pc, op, a, b, c, mem_a_before, mem_b_before, new_b, mem_a_after, mem_b_after, jumped, next_pc, emit}`
  - **Fungeoid (Befunge)** → `{step, row, col, dir, cell, string_mode, op, stack_before, stack_after, next_row, next_col, next_dir, emit}`
- New shared helper `_TeeingWriter` in `babel.interpreter` — a stdout wrapper that records the per-step emit chunk. Used by all four interpreters under witness mode to capture what each instruction wrote. Hooks always receive the `emit` field even for non-output ops (empty string).
- Used by `babel-playground` v0.5.0 to power its Witness Mode UI (per-step trace, scrubbable, per-family state renderer).

### Behaviour notes

- When `trace_hook=None` (the default for all existing callers): zero behavioural change, zero per-step overhead. All 193 existing tests pass unchanged.
- The hook is invoked **after** the op has mutated state, so the snapshot reflects post-step values. For families with `HALT` ops that early-return (stack, fungeoid), the HALT step is also reported before returning.
- Hooks may raise to abort execution — Babel propagates the exception out of `run()`. The playground uses this with a sentinel `_WitnessStepCapReached` to enforce a 10,000-step cap without modifying `max_steps`.

### Fixed

- `examples/brainfuck-rioplatense.yaml` "Halve and print" example: had 2073 `más` tokens (wrapping to 25 mod 256) where the description claimed 260; emitted `\x06` instead of `'A'`. Rewritten to 130 `más` + 1 `ito` + `decí` → `'A'`, matching the description.

## [0.6.2] — 2026-05-17

### Added — Fungeoid 2D base machine + Befunge-93 parameter sheet (third non-tape runtime)

Babel's fourth base-machine runtime end-to-end, after Brainfuck-tape (since v0.1.0), stack (v0.4.0), and OISC (v0.4.1). The fungeoid family is Babel's first **2D** execution model: a rectangular grid of ASCII cells, a directional instruction pointer that wraps toroidally, and a (conventional 1D) data stack. The canonical exemplar shipped in this release is `Befunge-93 <https://esolangs.org/wiki/Befunge>`__ (Pressey, 1993).

(Versioned as v0.6.2 because the v0.6.0 and v0.6.1 slots on this branch were claimed by the FALSE-stack and Spoon/Wordfuck releases respectively; all three releases ship the same day. The MINOR-version family for "new base machine" was previously consumed by stack (v0.4.0) and OISC (v0.4.1); under the pre-1.0 minor-bump-for-new-base convention this would otherwise be a fresh v0.6.0.)

#### Added

- **19 new `InstructionOp` values** in the fungeoid family (all prefixed `FUNGEOID_*` for dispatch isolation from the superficially-overlapping `STACK_*` family):
  - Direction: `FUNGEOID_DIR_RIGHT` / `_LEFT` / `_UP` / `_DOWN` — Befunge `> < ^ v`
  - Stack literal: `FUNGEOID_PUSH_DIGIT` — Befunge `0`..`9`. One canonical op; the digit value is encoded in the *token* itself (the ten cell-character entries on the parameter sheet all share this op, with a narrow carve-out in `LanguageSpec._instructions_unique` to permit the ten-to-one mapping)
  - Arithmetic: `FUNGEOID_STACK_ADD` / `_SUB` / `_MUL` / `_DIV` — Befunge `+ - * /`. Division by zero pushes `0` (Befunge silent-zero convention; FALSE's stack-runtime divide raises, the difference is documented in both module docstrings)
  - Stack manipulation: `FUNGEOID_STACK_DUP` / `_SWAP` / `_POP` — Befunge `: \ $`. Underflow is silent (the Befunge "implicit zero" convention extends to all three: dup of empty pushes 0; swap of <2 elements zero-fills; pop of empty is a no-op)
  - I/O: `FUNGEOID_OUTPUT_INT` (`. ` — note the trailing space, which is part of the spec) / `FUNGEOID_OUTPUT_CHAR` (`,`)
  - Conditionals: `FUNGEOID_IF_HORIZONTAL` / `_VERTICAL` — Befunge `_ |`
  - Control: `FUNGEOID_STRING_MODE_TOGGLE` (`"`) / `FUNGEOID_BRIDGE` (`#`) / `FUNGEOID_NOOP` (space) — and the cross-family `HALT` (`@`) is re-used unchanged
- **`_FUNGEOID_OPS` frozenset** in `schema.py` plus a parallel **`_check_fungeoid_ops_legal`** model-validator on `LanguageSpec` — same shape as the stack-family's `_STACK_OPS` / `_check_stack_ops_legal`: a negative-only rule that rejects ops with no defined semantics on a 2D grid.
- **Narrow carve-out** on `_instructions_unique`: `FUNGEOID_PUSH_DIGIT` is the only op for which multiple `Instruction` entries (sharing the op, differing in token) are legal. Every other op still enforces the per-op uniqueness rule. The dup-token rule is unchanged.
- **`src/babel/fungeoid_interpreter.py`** — a sibling module to `interpreter.py` / `stack_interpreter.py` / `oisc_interpreter.py`. Mirror of the structure: top-level `run(source, spec, *, stdin, stdout, max_steps=100_000)` matching the OISC signature; internal `_Grid`, `_IP`, `_State` dataclasses; `_build_dispatch_table` validates single-character tokens + arity=0 at parse time; the main loop reads one cell, dispatches on the canonical op (or pushes `ord(cell)` if string mode is on), then advances the IP toroidally. The bridge `#` works by calling the IP advance once extra in its handler before the bottom-of-loop advance.
- **`examples/befunge.yaml`** — 29 tokens (4 directions + 10 digits + 4 arithmetic + 3 stack-manip + 2 I/O + 2 conditionals + 1 string-mode + 1 bridge + 1 halt + 1 noop). Theme `befunge`, source_extension `.befunge`. Includes four examples: a `2.@` smoke test, a `54+.@` arithmetic demo, the canonical Hello World `"!dlroW olleH">:#,_@`, and a string-mode character output `"A",@`.
- **Package-level dispatcher wired in `babel/__init__.py`.** `babel.run` now routes `fungeoid_2d` specs to `babel.fungeoid_interpreter.run`; the module docstring is updated to reflect four base-machine runtimes; the per-family `babel.fungeoid_interpreter.run` keeps its single-family contract (rejects non-fungeoid specs).

#### Tests

- 35 new `tests/test_fungeoid_interpreter.py` tests: YAML loads + 29-token inventory + ten-digit op-sharing check; empty source + whitespace-only source both run to completion; tiny `2.@`, `54+.@`, `93-.@`, `67*.@`, `50/.@` (silent-zero) programs; string-mode push/pop ordering; 2D direction reversal via `v`; toroidal wrap-around via `<` heading off the left edge; bridge `#` skipping a cell; dup / swap / pop; the Befunge "implicit zero" convention on each of dup-of-empty / pop-of-empty; halt via `@`; `max_steps` cap on a `>`-only torus loop; unknown-cell error; canonical Hello World end-to-end; the YAML's Hello World example end-to-end; runtime + schema-level guards (non-fungeoid spec rejected, non-2D-grid encoding rejected, stack op on fungeoid spec rejected, multi-char token rejected as ParseError, ten-digit duplicate-op allowed by carve-out, dup ops outside the carve-out still rejected); package-level dispatcher routes correctly for both the smoke test and the Hello World.
- All 158 previously-passing v0.6.1 tests still pass (+35 from this batch → 193 total).

#### Hello World variant

The shipped Hello World is the canonical single-line Befunge-93 idiom: `"!dlroW olleH">:#,_@`. Toggles string mode, pushes the characters of `Hello World!` in reverse (so `H` ends up on top), then enters a print loop: `:` dup the top, `#` bridge over the `,`, `_` horizontal-if sends control LEFT on non-zero. Going left, the IP hits the `,` and prints; continues left to `#` which skips `:` on the way back; the `>` resets direction to RIGHT and the loop repeats. When the implicit zero is finally popped (every character has been emitted), `_` sends control RIGHT and the IP hits `@` to halt. Output: `Hello World!` (no trailing newline; Befunge programs that want one print it explicitly).

#### Deferred from this release

The standard Befunge-93 ops not yet implemented, with the runtime extension each would need (each is a 1–2 PR follow-up, scoped to leave the v0.6.2 dispatch table untouched):

| Op | Token | Blocked on |
| --- | --- | --- |
| put | `p` | Self-modifying grid write (mutable grid + bounds policy) |
| get | `g` | Self-modifying grid read (mirror of `p`) |
| random direction | `?` | Seeded `random.Random` plumbed through the runtime signature (same shape as the BF-tape `RANDOM` op) |
| input integer | `&` | Stdin read + integer parse + push (already-reserved `stdin` parameter is unused by the v0.6.2 op set) |
| input character | `~` | Stdin one-byte read + push of codepoint |

The runtime gap on the biggest of those (`p` / `g`) is the natural next milestone for Befunge-scope work, since several non-trivial Befunge programs depend on the self-modifying property to compute jump tables.

#### Constraint observed

Per the v0.6.2 work-order constraint, `src/babel/interpreter.py`, `src/babel/stack_interpreter.py`, and `src/babel/oisc_interpreter.py` are unchanged in this release. The fungeoid runtime lives in a fourth sibling module that re-uses zero code from the other three; the only cross-module reach is the schema enum / frozenset additions and the dispatcher branch.

## [0.6.1] — 2026-05-17

### Added — `VARIABLE_LENGTH_BINARY` (Spoon) + `WORD_LENGTH_DISPATCH` (Wordfuck) tokenizers

Closes the last two encoding-stub items from the v0.2.0 schema bundle. Both encoding values have been schema-legal since v0.2.0, but the BF-tape tokenizer raised `ParseError("not yet supported")` when asked to actually parse a source against either of them. v0.6.1 wires up the tokenizer for both, with two new parameter sheets that exercise each end-to-end.

(Versioned as v0.6.1 rather than v0.6.0 because the v0.6.0 slot was concurrently claimed by the FALSE-parameter-sheet release immediately below; the intended bump for this tokenizer batch under the pre-1.0 minor-bump-for-new-schema-capability convention is v0.6.0 in isolation. Both releases ship the same day on the same branch.)

#### Added

- **`VARIABLE_LENGTH_BINARY` tokenizer.** Spoon-style Huffman / prefix-free bit-string encoding: source is a stream of `0` and `1` characters; any other character is silently skipped (treated as a comment — whitespace, newlines, prose annotations all pass through transparently). The tokenizer walks the source bit-by-bit, accumulates into a buffer, and emits the moment the buffer matches a defined code. Because the canonical code set is prefix-free by construction, the first match is also the longest match — no lookahead needed. Trailing bits at end-of-source that do not complete any token raise `ParseError`. Arity > 0 is rejected at tokenize time (bit-strings have no defined operand-position semantics).
- **`WORD_LENGTH_DISPATCH` tokenizer.** Wordfuck-style: only the *length* of each whitespace-separated atom matters; the letters chosen are commentary. The parameter sheet's `token` field carries a representative word of each length so the schema's per-token uniqueness check still holds; the tokenizer builds a `{length: op}` map from those representatives and dispatches on `len(atom)` for each source atom. Unknown atom lengths raise `ParseError` with the offending length and the legal length set quoted. Two instructions sharing a token length on one spec raise `ParseError` at tokenize time (the sheet would be ambiguous). Arity > 0 is rejected at tokenize time (operand atoms would also be dispatched by length and become indistinguishable from new instructions).
- **`examples/spoon.yaml`** — the canonical Spoon-style parameter sheet. Eight prefix-free bit-string codes covering the canonical BF op set; theme `huffman`, source_extension `.spoon`. The mapping matches the schema-validation reference in `tests/test_schema_relaxed_completeness.py` (v0.2.0). Includes a tiny `1 1 00101` example and a full transliteration of `++++++++[>++++++++<-]>+.` to print `A`.
- **`examples/wordfuck.yaml`** — the canonical Wordfuck parameter sheet. Eight length-N placeholder tokens (lengths 1..8) covering the canonical BF op set; theme `word_length`, source_extension `.wordfuck`. Includes a tiny `a a abcde` example and a full transliteration of the canonical BF "print A" program.

#### Tests

- 7 new `tests/test_spoon.py` tests: YAML loads + 8-op inventory + bit-string-only-tokens check; tiny `1 1 00101` → `\x02`; non-bit characters are comments; trailing-bits source raises `ParseError`; arity > 0 on a `VARIABLE_LENGTH_BINARY` spec raises `ParseError`; canonical BF Hello World transliterated to Spoon via `_to_spoon()` runs to `"Hello World!\n"`; every YAML example produces its declared `expected_output`.
- 8 new `tests/test_wordfuck.py` tests: YAML loads + 8-op inventory + length-1..8 coverage check; tiny `a a abcde` → `\x02`; unknown-length atom raises `ParseError`; word *content* is irrelevant (different length-1 words dispatch the same); arity > 0 raises `ParseError`; duplicate-length spec raises `ParseError`; canonical BF Hello World transliterated to Wordfuck via `_to_wordfuck()` runs to `"Hello World!\n"`; every YAML example produces its declared `expected_output`.
- All 112 previously-passing v0.5.2 tests still pass (+15 from this tokenizer batch → 127 with the tokenizer slice only; combined with the v0.6.0 FALSE batch the full suite is 158).

#### Schema encoding-stubs remaining

None on the v0.2.0 list for the BF-tape family. The two encoding values v0.2.0 introduced for tokenizer follow-up (`VARIABLE_LENGTH_BINARY`, `WORD_LENGTH_DISPATCH`) both ship runtime today. The earlier `UNARY` and `BINARY` encoding values from v0.1.0 remain schema-legal but have no canonical exemplar in the corpus that motivated dedicated tokenizer work; `TWO_DIMENSIONAL_GRID` is reserved for the fungeoid family (separate Path B).

#### A note on the Spoon spec

The esolangs wiki page for Spoon and the various secondary writeups give slightly different code assignments for the eight canonical ops; several common ones (e.g. `0010` for `]` paired with `00100` for `,`) are not actually prefix-free, which makes greedy left-to-right scanning ambiguous. Babel's sheet picks a mapping that **is** prefix-free, matches the schema-validation reference in `tests/test_schema_relaxed_completeness.py`, and renders the longest-prefix-match property a trivial first-match check. Spec-page authors who want to track a specific Spoon variant should override the eight token strings; the tokenizer accepts any prefix-free code set.

#### Note on the v0.6.0 "Constraint observed" claim

The v0.6.0 FALSE release notes (below) state that `src/babel/interpreter.py` is unchanged in this release; that constraint was true at v0.6.0 commit time but no longer holds at v0.6.1 (this release modifies `_tokenize` to add the two new encoding paths). Both releases ship together on the same branch and should be considered jointly; the FALSE constraint note refers to that release's own diff, not the cumulative branch state.

## [0.6.0] — 2026-05-17

### Added — FALSE parameter sheet (first canonical stack-language exemplar)

Babel's first canonical-wiki stack-language sheet — FALSE
(Wouter van Oortmerssen, 1993; <https://esolangs.org/wiki/FALSE>). The
v0.4.0 stack runtime gets its first real-world exemplar from the corpus,
and the stack op set grows by six ops to cover the integer-stack subset
of the language.

#### Added

- **`examples/false.yaml`** — 15 tokens (the 14 canonical FALSE single-character ops covered by this scope plus the cross-family `halt` convenience). Tokens map one-for-one to canonical FALSE source (`$ % \\ @ + - * / _ = > . ,`); the integer-literal form is the existing `push N` arity-1 pattern pending the ASCII-punctuation tokenizer extension (where bare digit sequences would form literals). String literals, named variables, lambdas / `!` / `?` / `#`, and the bitwise logic ops are deferred — each is documented in the YAML with the runtime extension it would need.
- **6 new `InstructionOp` values** in the stack family, all added to `_STACK_OPS`:
  - `STACK_MUL` — pop two, push product (FALSE `*`)
  - `STACK_DIV` — pop b then a, push a // b; raises `InterpreterError` on b == 0 (FALSE `/`)
  - `STACK_NEGATE` — pop top, push `-value` (FALSE `_`, the signature unary negation op)
  - `STACK_EQUALS` — pop two, push -1 if equal else 0 (FALSE `=`, Forth boolean convention)
  - `STACK_GREATER` — pop b then a, push -1 if a > b else 0 (FALSE `>`)
  - `STACK_ROT` — rotate third-from-top to top: `(a b c -- b c a)` (FALSE `@`)
- **Stack-interpreter handlers** for all six new ops; `STACK_ROT` direct-`append`s to bypass the cell-width wrap (the values are already wrapped on push, no arithmetic produced).
- **Division-by-zero** surfaces as a clear `InterpreterError("STACK_DIV: division by zero")` rather than a silent zero — source-level bugs surface explicitly.

#### Tests

- 31 new `tests/test_false.py` tests: YAML loads + token inventory + arity check; per-op coverage for all six new ops including underflow paths; canonical Hello World character-by-character end-to-end to `"Hello, World!\n"`; FALSE-specific quirks (the -1/0 boolean convention, postfix arithmetic chain, halt mid-source); cell-width interaction with byte cells confirming the all-ones-mask discipline holds for `EQUALS` / `GREATER` / `NEGATE` under wrap; schema-validator acceptance of the six new ops; package-level `babel.run` dispatch.
- All 112 previously-passing v0.5.2 tests still pass (112 → 143 total).

#### Boolean convention rationale

FALSE returns `-1` for true and `0` for false (Forth convention). Under `ARBITRARY` cell width (FALSE's canonical setting) this is preserved literally; under bounded widths the `-1` wraps to the all-ones bit pattern (`255` for BYTE, `2**32-1` for WORD) — intentional, and tested. The all-ones pattern is what makes the truth value useful as a mask for the bitwise AND / OR ops a future release will add to lift the deferred FALSE control-flow primitives.

#### What's deferred (and why)

Each of the following needs runtime or tokenizer machinery beyond the v0.6.0 scope, so this sheet ships without them and the YAML calls out the path:

| FALSE feature | Tokens | Blocked on |
| --- | --- | --- |
| String literal output | `"..."` | String-aware tokenizer + `STACK_OUTPUT_STRING` |
| Named variables | a..z, `:`, `;` | Named-cell store alongside the integer stack |
| Lambdas + control flow | `[ ]`, `!`, `?`, `#` | First-class code values on the stack + call stack |
| Bitwise logic | `&`, `|`, `~` | Held until the mask users (lambdas) land |
| Character input | `^` | Stdin plumbing the stack runtime reserves but doesn't yet consume |

The runtime gap on the bigger of those (lambdas) is the natural next milestone for FALSE-scope work; the smaller items (string literal output, named variables) can ship independently.

#### Constraint observed

Per the v0.6.0 work-order constraint, `src/babel/__init__.py`, `src/babel/interpreter.py`, and `src/babel/oisc_interpreter.py` are unchanged in this release. `__version__` inside `__init__.py` therefore still reads `"0.5.2"` (one minor behind `pyproject.toml`'s `"0.6.0"`); the next release that touches the dispatcher should re-sync the two.

## [0.5.2] — 2026-05-17

### Added — `BREAK_LOOP` runtime (La Weá's `pico` fully working)

Closes the last stub op in the BF-tape interpreter. `BREAK_LOOP` was added to the schema in v0.2.0 but interpreted as a not-yet-implemented stub since then; v0.5.2 implements La Weá's `pico` semantic: at runtime, scan the parsed-op stream forward from the current `pc` for the nearest `LOOP_END`, set `pc` to that position, and let the bottom-of-loop `pc += 1` advance past it. Programs without any `LOOP_END` after the `BREAK_LOOP` surface a clear `InterpreterError`.

The semantic deliberately matches La Weá's wiki ("regardless of current cell value", finds nearest *following* `tula`) — it doesn't track loop nesting at runtime. A future variant of `BREAK_LOOP` with proper innermost-open-loop semantics (Brainlove-style) would need a runtime loop stack and a new op value; this implementation matches La Weá specifically.

#### Changed

- **`test_break_loop_raises_not_yet_implemented` → `test_break_loop_jumps_to_next_loop_end`** — the stub-raising test becomes a real behavioural test.
- **`test_la_wea_pico_raises_not_yet_implemented` → `test_la_wea_pico_jumps_out_of_loop`** — same; La Weá's `pico` now executes end-to-end.

#### Tests

- 1 new `test_break_loop_without_loop_end_raises` covering the error path.
- All 111 previously-passing v0.5.1 tests still pass (111 → 112 total).

#### La Weá op coverage: 16/16

With `BREAK_LOOP` runtime in place, all sixteen La Weá ops execute end-to-end. The Chilean-Spanish BF entry is now fully runnable.

#### Stub ops remaining in the schema

None on the BF-tape side. Encoding-tokenizer stubs remain for `VARIABLE_LENGTH_BINARY` (Spoon) and `WORD_LENGTH_DISPATCH` (Wordfuck); those are tokenizer extensions, not new ops.

## [0.5.1] — 2026-05-17

### Added — La Weá parameter sheet + 5 tape ops to support it

The Chilean Spanish entry in the Spanish-language BF coverage matrix. Completes the four-register set: Argentine (Rioplatense), Mexican (Chespirito), peninsular (Mierda), Chilean (La Weá) — one parameter-sheet schema, four registers.

#### Added

- **5 new `InstructionOp` values** to express La Weá's signature extras (all tape-legal):
  - `INCREMENT_BY_2` — La Weá's `aweonao` (+2 in one op)
  - `DECREMENT_BY_2` — La Weá's `maraco` (-2 in one op)
  - `CLIPBOARD_TOGGLE` — La Weá's `perkin` (stateful: empty → store + mark full; full → recall + clear)
  - `OUTPUT_INT` — La Weá's `chúpala` (emit cell as decimal integer, ignoring spec-wide `IOModel`)
  - `INPUT_INT` — La Weá's `brígido` (read decimal integer into cell, ignoring spec-wide `IOModel`)
- **`_TapeState.clipboard_filled: bool`** — runtime flag backing `CLIPBOARD_TOGGLE`'s stateful semantics. Existing `CLIPBOARD_STORE` / `CLIPBOARD_RECALL` (single-direction ops) are unchanged.
- **Tape interpreter handlers** for all five new ops; cell-width wrap behaviour matches the existing arithmetic ops (BYTE mod 256, etc.).
- **`_TAPE_OPS`** and **`_TAPE_CELL_MODIFY_OPS`** frozensets in `schema.py` updated to include the new ops where appropriate. No new validators.
- **`examples/brainfuck-la-wea.yaml`** — 16 tokens, the full La Weá op set. 15 of 16 execute end-to-end; the 16th (`pico` → `BREAK_LOOP`) is schema-legal but the runtime stub raises `InterpreterError` until the BF-tape loop-stack runtime extension lands (documented in the YAML and tested explicitly).

#### Tests

- 10 new `tests/test_la_wea.py` tests: spec loads with all 16 ops; canonical BF Hello World transliterated to La Weá runs to `Hello World!\n`; per-op tests for `aweonao` (+2), `maraco` (-2 wraps to 254 on byte), `maraca` (zero), `chúpala` (integer output), `brígido` (integer input), `perkin` (toggle copy/paste), `mierda` (halt); `pico` raises the expected runtime stub.
- All 101 previously-passing v0.5.0 tests still pass (101 → 111 total).

#### What still needs runtime work

The only La Weá op without a runtime is `pico` → `BREAK_LOOP`. The op semantics ("jump to position after nearest following `tula`") require a runtime loop-stack rather than operand-consumption; orthogonal to the v0.5.0 operand-aware tokenizer work. La Weá parameter sheets without `pico` are fully runnable today; `pico`-using programs surface a clear runtime error.

## [0.5.0] — 2026-05-17

### Added — BF-tape arity-aware tokenizer + `JUMP_UNCONDITIONAL` runtime

The BF-tape interpreter becomes operand-aware. Closes the last v0.2.0 deferral ("`JUMP_UNCONDITIONAL` needs the deferred operand-slot extension; runtime support is a follow-up") and the v0.3.3 forward-looking note ("Runtime semantics for `JUMP_UNCONDITIONAL` in the BF-tape interpreter").

#### Added

- **Arity-aware BF-tape tokenizer.** `_tokenize` now returns `(ops, operands)` parallel lists; when an `Instruction` declares `arity > 0`, the next source atoms are consumed as runtime operands. The arity-1 operand is parsed as `int()` (matches the stack interpreter's `STACK_PUSH` shape). Constraints surface as `ParseError` at parse time, not as silent corruption: arity > 1 rejected (the BF-tape pattern only needs arity-0 and arity-1 ops); `ascii_punctuation` encoding with arity > 0 rejected (single-character tokens have no operand slot); multi-atom whitespace tokens with arity > 0 rejected (the operand position becomes ambiguous against the next multi-atom token); missing operand at end of source rejected; non-integer operand rejected with the offending token quoted.
- **`InstructionOp.JUMP_UNCONDITIONAL` runtime.** With arity=1, the operand is the absolute `pc` target into the parsed-op stream. Jump targets out of range raise `InterpreterError`. The op is also schema-legal with arity=0 (parameter sheet may declare it), but executing it that way raises a clear runtime error ("must declare arity=1 on the jump instruction") rather than mis-jumping. Programs can now express loops without the BF bracket pair (`[` `]`) — useful for La Weá-style tape derivatives whose original wiki specifies a jump-target instruction.
- **`_ParsedProgram.operands`** — new parallel list alongside `ops`; `None` for arity-0 ops, integer for the v0.5.0 `JUMP_UNCONDITIONAL` arity-1 case. Shape generalises to a tuple per position if a future tape op needs multiple operands.

#### Changed

- **Removed `LanguageSpec._check_tape_arity_is_zero`** validator. The validator was a v0.3.3 safety check that fired before the interpreter knew how to consume operands — now that the tokenizer is arity-aware, the validator's job moves to the tokenizer (which rejects bad combinations at parse time with more actionable error messages). Tape specs are now schema-validating with arity > 0 instructions; whether the runtime can interpret a particular arity-N op is determined when the source is parsed. The parallel updates to the validators on the OISC and stack base machines (which already accept arity > 0) stay unchanged.

#### Tests

- 5 new `tests/test_interpreter.py` tests: `JUMP_UNCONDITIONAL` jumps correctly and produces an output sequence `\x01\x02\x03` from a 3-iteration loop bounded by `max_steps`; raises clearly when declared without arity; raises on out-of-range target; raises `ParseError` on `ascii_punctuation` + arity > 0; raises `ParseError` on non-integer operand; raises `ParseError` on missing operand at end of source.
- 1 updated `tests/test_instruction_arity.py` test: `test_tape_spec_rejects_nonzero_arity` → `test_tape_spec_accepts_nonzero_arity_post_v0_5_0` (mirror of the schema-validator change).
- All 95 previously-passing v0.4.2 tests still pass (95 → 101 total).

#### Operand-slot extension across the family

The v0.2.0 → v0.3.3 → v0.4.0 → v0.4.1 → v0.5.0 arc closes the operand-slot story for all three base machines now in the runtime:

| Family | Operand support | Op that uses it |
| --- | --- | --- |
| `brainfuck_tape` | v0.5.0 (this release) | `JUMP_UNCONDITIONAL` (arity 1) |
| `stack` | v0.4.0 | `STACK_PUSH` (arity 1) |
| `oisc` | v0.4.1 | `SUBLEQ` (arity 3) |

The remaining schema-stub op without a runtime is `BREAK_LOOP` (Brainlove-style "exit innermost enclosing loop") — that one needs a runtime loop-stack rather than operand-consumption, which is a separate piece.

## [0.4.2] — 2026-05-17

### Changed — Package-level dispatcher now routes OISC

`babel.run` (the package-level entry point) now dispatches `base_machine = oisc` specs to `babel.oisc_interpreter.run`, matching the routing for `brainfuck_tape` and `stack`. Closes the v0.4.1 follow-up note ("This release does *not* extend the package-level `babel.run` dispatcher to OISC; v0.4.2 will wire that").

Callers that previously had to use `from babel.oisc_interpreter import run` directly can now use `babel.run(source, spec)` regardless of which of the three base machines the spec uses. The per-family `babel.oisc_interpreter.run` entry point keeps its original single-family contract (still raises on non-OISC specs); both styles are supported.

#### Tests

- 1 new `tests/test_dispatcher_oisc.py` test verifying `babel.run` correctly routes an OISC spec to the OISC interpreter and produces expected output.
- All 95 previously-passing v0.4.1 tests still pass (95 → 96 total).

## [0.4.1] — 2026-05-17

### Added — OISC Subleq interpreter (second non-tape base machine)

The second non-tape base machine, landing on top of v0.4.0's stack runtime. Subleq is the canonical [One Instruction Set Computer](https://esolangs.org/wiki/Subleq) — a single instruction `SUBLEQ a b c` (subtract and branch if less than or equal to zero) is Turing-complete on its own. The interpreter is the "~50 LOC" Path B investment flagged by the [BF-family interpreter-candidates survey](research-notes/interpreter-candidates-2026-05-17.md) for its high narrative density (the "one instruction" headline) and modest implementation cost.

#### Added

- **`src/babel/oisc_interpreter.py`** — new interpreter module, sibling to the BF-tape interpreter. Self-contained parse + run loop; the module docstring documents the Babel Subleq dialect:
  - **Program format**: whitespace-separated signed integers; atom count must be a multiple of 3.
  - **Memory**: the program *is* the memory (self-modifying); arbitrary-precision Python ints; auto-extends on `TAPE_1D_UNBOUNDED`.
  - **PC**: starts at 0; absolute memory index (not instruction index); the c-operand is the post-jump PC directly.
  - **Halt**: `c < 0` after the SUBLEQ step, or PC running past end of memory.
  - **I/O**: address `-1` is the I/O port with operand-position disambiguation — `a == -1` reads one byte from stdin into `mem[b]`; `b == -1` emits the low byte of `mem[a]` to stdout. I/O steps skip the subtract and treat `new_b` as 0 (so the c-jump fires unconditionally).
- **`InstructionOp.SUBLEQ`** — new canonical op for the single Subleq instruction.
- **`LanguageSpec._check_oisc_shape`** — new cross-field validator: every instruction on an OISC spec must have `arity == 3`. Op identity (`SUBLEQ` vs. another op) is enforced at *runtime* by the interpreter, not at schema time, so the v0.3.3 placeholder-op test affordance still validates.
- **`examples/subleq.yaml`** — canonical Subleq parameter sheet; theme `oisc`, source_extension `.sub`, single instruction with `op: subleq` and `arity: 3`. Includes a "Halt immediately" and a "Print 'A'" example, both verified by tests.

This release does *not* extend the package-level `babel.run` dispatcher to OISC; v0.4.2 will wire that. For now, OISC interpretation goes through `from babel.oisc_interpreter import run` directly.

#### Tests

- 18 new `tests/test_oisc_interpreter.py` tests covering: empty / whitespace-only programs, `c < 0` halt, PC-runs-off-end halt, multi-step decrement program, OUTPUT one and two characters, INPUT step, parse errors (non-multiple-of-3, non-integer atom), step cap on infinite loop, non-OISC-spec rejection, runtime rejection of legacy placeholder-op specs, schema-time rejection of non-arity-3 OISC specs, and end-to-end YAML loading + example execution.
- All 77 previously-passing v0.4.0 tests still pass (77 → 95 total).

#### Constraints honoured

- BF-tape interpreter (`src/babel/interpreter.py`) and stack interpreter (`src/babel/stack_interpreter.py`) untouched.
- Existing tests untouched (no import-path updates needed).
- New operand-aware tokenization lives inside `oisc_interpreter.py`; neither the BF-tape tokenizer nor the stack tokenizer is modified.

## [0.4.0] — 2026-05-17

### Added — Stack-machine runtime (first non-tape base machine)

Babel's first Path B investment from the [BF-family interpreter-candidates survey](research-notes/interpreter-candidates-2026-05-17.md): a stack-machine interpreter alongside the existing Brainfuck-tape one. The schema has reserved `BaseMachine.STACK` and the `STACK_UNBOUNDED` / `STACK_BOUNDED` memory shapes since v0.1.0; v0.4.0 lights up the runtime behind them.

#### Added

- **Eight new `InstructionOp` values** for the stack core: `STACK_PUSH` (arity 1; reads the next source atom as an integer literal), `STACK_POP`, `STACK_DUP`, `STACK_SWAP`, `STACK_ADD`, `STACK_SUB`, `STACK_OUTPUT_CHAR`, `STACK_OUTPUT_INT`. `HALT` (already in the enum since v0.2.0) is also recognised by the stack runtime. The set is deliberately minimal — large enough to demonstrate the dispatcher and arity-aware tokenizer, small enough that the dispatch table fits on a screen; concrete stack-language sheets (FALSE, Underload, a Forth subset) will grow it in follow-up releases.
- **`_STACK_OPS` frozenset** in `babel/schema.py`, parallel to `_TAPE_OPS`, plus a new `_check_stack_ops_legal` cross-field validator on `LanguageSpec`. A stack spec that references tape-only ops (e.g. `PTR_RIGHT`, `LOOP_START`) is rejected at schema-validation time with a clear error listing the legal stack ops. Tape spec validation is unchanged.
- **`babel/stack_interpreter.py`** — the stack runtime. Mirrors the structure of `babel/interpreter.py`: a `parse()` helper, a `run()` entry point with the same `stdin`/`stdout`/`max_steps` parameters, and a `_step`-style dispatch loop. The tokenizer is **arity-aware** — at each step it looks up the matched `Instruction` and, if `arity > 0`, consumes the next `arity` source atoms as runtime operands. `STACK_PUSH`'s operand is parsed with `int()`; malformed operands raise the existing `ParseError` (reused from `babel.interpreter` so callers can catch one exception type across both families). Supports both stack memory shapes (`STACK_UNBOUNDED` and `STACK_BOUNDED` with a configurable cap; overflow raises `InterpreterError`) and honours cell-width wrap on arithmetic (`BYTE` mod 256, `WORD` mod 2**32, etc.).
- **Base-machine dispatcher in `babel/__init__.py`** — a new package-level `babel.run(source, spec, ...)` that picks the right runtime based on `spec.base_machine`. The per-family modules keep their original single-family contracts: `babel.interpreter.run` still raises on non-tape specs, and `babel.stack_interpreter.run` raises on non-stack specs. The dispatcher is the new ergonomic entry point for callers that want a single-call API across families. `babel/__main__.py` switches to the dispatcher so `babel run minimal-stack.yaml --program "push 65 emit"` works from the CLI end-to-end.
- **`examples/minimal-stack.yaml`** — Babel's first stack parameter sheet. Explicitly labelled in its description as a synthetic demo (not a canonical wiki esolang) whose purpose is to validate the runtime. Eight whitespace-separated tokens (`push`, `pop`, `dup`, `swap`, `add`, `sub`, `emit`, `print`) covering exactly the v0.4.0 op core. `push` has arity 1; the other seven have arity 0.

#### Tests

- 23 new `tests/test_stack_interpreter.py` tests: empty + whitespace-only programs run to completion; the four spec'd examples from the YAML (`push 65 emit` → `A`, `push 5 push 3 add emit` → `\x08`, `push 1 dup add emit` → `\x02`, `push 10 push 3 sub print` → `7`); `swap`, `pop`, integer output; stack underflow on `pop`/`emit`/`swap` raises `InterpreterError`; malformed/missing `push` operand and unknown tokens raise `ParseError`; `max_steps` honoured; the stack runtime rejects tape specs with a clear error; bounded-stack overflow raises; BYTE-cell-width add wraps; YAML round-trip + end-to-end run; the package-level dispatcher routes correctly for both stack and tape specs; the schema validator rejects tape ops on stack specs.
- All 54 previously-passing tests still pass (54 → 77 total).

### What this unblocks

The dispatcher pattern (`babel.run` routes on `spec.base_machine`; per-family modules keep single-family contracts) is the template for every future Path B family. The next non-tape runtimes — OISC/Subleq first (~50 LOC, the operand-slot is already in place from v0.3.3), then register / queue / fungeoid_2d — slot into the same shape: a new `<family>_interpreter.py` module, a new `_FAMILY_OPS` frozenset + validator pair in `schema.py`, and one new clause in the package dispatcher.

## [0.3.3] — 2026-05-17

### Added — `Instruction.arity` field (operand-slot extension deferred from v0.2.0)

Closes the fourth and last schema gap surfaced by the [BF-family interpreter-candidates survey](research-notes/interpreter-candidates-2026-05-17.md): the `Instruction` model gains an `arity: int = 0` field describing how many additional whitespace-separated source atoms the interpreter should consume *after* this token as runtime operands.

The field is schema-level only — the interpreter doesn't consume operands yet, because Babel's only base-machine runtime today is `brainfuck_tape` and BF-tape ops have arity 0 by definition. The arity field lands here as the foundation for the planned OISC (Subleq) and register-machine extensions, plus stack-machine literal-pushes — all of which need to enumerate per-token operand counts at parameter-sheet authoring time. It also unblocks the deferred runtime semantics for `JUMP_UNCONDITIONAL` (added schema-only in v0.2.0).

#### Added

- **`Instruction.arity: int`** with `default=0`, `ge=0` validation, and human-readable docstring covering the Subleq (`SUBLEQ a b c`, arity 3) and Minsky (`INC R1` arity 1; `DEC R1 label` arity 2) shapes.

#### Changed

- **`LanguageSpec._check_tape_arity_is_zero`** — new cross-field validator that rejects any tape spec setting `arity > 0` on any instruction. The BF-tape interpreter has no operand-consumption machinery; if it processed an operand atom as the next instruction token, behaviour would silently corrupt. Validation at schema time surfaces the misuse immediately. Backward-compatible: every existing tape sheet has implicit `arity=0` everywhere.

#### Tests

- 7 new `tests/test_instruction_arity.py` tests: default arity is 0; existing BF specs unchanged; negative arity rejected; explicit `arity=0` accepted; tape specs reject non-zero arity; OISC-shaped (Subleq, arity 3) and register-shaped (Minsky, mixed arities) specs validate at the schema level even though no runtime exists yet.
- All 54 previously-passing tests still pass (54 → 61 total).

### What still needs runtime work

Arity unblocks parameter-sheet authoring for operand-bearing instructions, but no interpreter consumes arity > 0 yet. Three follow-up runtime pieces are now sequenced (no longer schema-blocked):

1. **Stack-machine interpreter** (Path B from the candidates survey, ~long weekend). With arity in place, stack literal-pushes can be expressed (`PUSH` with arity 1).
2. **OISC interpreter** (~50 LOC). Subleq's `SUBLEQ a b c` is now expressible at the parameter-sheet level; the interpreter just needs to read 3 atoms after the implicit token.
3. **Runtime semantics for `JUMP_UNCONDITIONAL`** in the BF-tape interpreter — currently raises `InterpreterError`. Could now be wired by giving it arity-via-label semantics if a tape derivative wants it (though most don't).

## [0.3.2] — 2026-05-17

### Added — GERMAN + BaguaFuck + Pikalang + Alphuck parameter sheets

Four new parameter sheets ship in this release, no runtime changes. All four were flagged as Path A (no runtime work required) by the [BF-family interpreter-candidates survey](research-notes/interpreter-candidates-2026-05-17.md):

- **`examples/german.yaml`** — GERMAN, a 2014 trivial BF substitution by User:domi382 using all-caps German nouns (*LINKS*, *RECHTS*, *ADDITION*, *SUBTRAKTION*, *EINGABE*, *AUSGABE*, *SCHLEIFENANFANG*, *SCHLEIFENENDE*). Single-atom whitespace-separated tokens. Methodological exemplar of a non-Spanish, non-English natural-language skin — broadens Babel's "naturalness" axis to a third register beyond English (Ook!) and Spanish (Mierda / Chespirito / Rioplatense).
- **`examples/baguafuck.yaml`** — BaguaFuck, whose eight instructions are the Bagua trigrams of the I Ching (乾 / 兑 / 离 / 震 / 巽 / 坎 / 艮 / 坤). Single Unicode-codepoint tokens written adjacently without separators. Uses `ascii_punctuation` encoding — Babel's single-character tokenizer iterates the source by Unicode codepoint, so non-ASCII single-character tokens work natively without any tokenizer changes. Clean Unicode-axis exemplar.
- **`examples/pikalang.yaml`** — Pikalang, eight Pokémon-syllable tokens (*pipi*, *pichu*, *pi*, *ka*, *pikachu*, *pikapi*, *pika*, *chu*). The tokens contain prefix overlaps (`pi` ⊂ `pikapi`, `pika` ⊂ `pikachu`), but because the wiki specifies whitespace-separated source, atom-by-atom matching is unambiguous and Babel's single-atom fast path handles it without longest-match logic.
- **`examples/alphuck.yaml`** — Alphuck, plain letter-for-symbol substitution: eight single lowercase ASCII letters (*a*, *c*, *e*, *i*, *j*, *o*, *p*, *s*) replace the eight BF punctuation glyphs. Same encoding shape as canonical BF; exercises `ascii_punctuation` with alphabetic single-char tokens.

#### Tests

- `tests/test_german.py` — 4 tests including Hello World end-to-end and case-sensitivity check.
- `tests/test_baguafuck.py` — 3 tests including Hello World end-to-end and Unicode codepoint assertions.
- `tests/test_pikalang.py` — 4 tests including Hello World end-to-end and a prefix-overlap disambiguation check.
- `tests/test_alphuck.py` — 4 tests including Hello World end-to-end and comment-skip behaviour.
- All previous tests still pass (39 → 54 total).

## [0.3.1] — 2026-05-17

### Added — Chespirito + Mierda parameter sheets (completes the Spanish-language BF trio)

Two new parameter sheets ship in this release, no runtime changes:

- **`examples/brainfuck-chespirito.yaml`** — Brainfuck derivative whose surface tokens are Spanish words from the vocabulary of Roberto Gómez Bolaños (the Mexican comedian *Chespirito*) — *chilindrina*, *chiquitolina*, *chompiras*, *chaparrón*, *chipote*, *chillón*, *chanfle*, *chapulín*, plus *chiripiolca* mapped to the `random` op. Mexican-Spanish vocabulary; 9 single-atom instructions; uses the v0.1.0 fast path.
- **`examples/brainfuck-mierda.yaml`** — pure peninsular-Spanish vocabulary skin (*Mas*, *Menos*, *Derecha*, *Izquierda*, *Decir*, *Leer*, *Iniciar Bucle*, *Terminar Bucle*). 6 single-atom + 2 two-atom tokens in one sheet; exercises the v0.3.0 multi-atom tokenizer in a mixed configuration the Ook! sheet doesn't. Mierda's only known prior implementation was a fragile Common Lisp interpreter; this sheet revives the language.

Together with `brainfuck-rioplatense.yaml` (Argentine), the trio gives Babel coverage of three Spanish-language registers — Mexican, peninsular, and Rioplatense — from the single parameter-sheet schema.

#### Tests

- `tests/test_chespirito.py` — 4 tests including Hello World end-to-end and `chiripiolca` random behaviour.
- `tests/test_mierda.py` — 4 tests including Hello World end-to-end and a mixed single+multi-atom program.
- All previous tests still pass (24 → 32 total).

## [0.3.0] — 2026-05-17

### Added — Multi-atom whitespace tokens + first new parameter sheet (Ook!)

The tokenizer for `WHITESPACE_SEPARATED_TOKENS` now supports tokens that span multiple whitespace-separated atoms — e.g. Ook!'s two-atom `Ook. Ook?` pair. The path is greedy longest-match: tokens are pre-sorted by atom-length descending, and the source's atom stream is walked consuming the longest matching prefix at each position. Backward-compatible: single-atom tokens (the Rioplatense-BF case and most other vocabulary skins) take the existing fast path; the multi-atom path only kicks in when a token contains internal whitespace.

`examples/ook.yaml` ships as the first parameter sheet that exercises this — David Morgan-Mar's 2001 Ook! Brainfuck derivative, where each canonical instruction maps to a pair of three base tokens (`Ook.`, `Ook?`, `Ook!`). Canonical Ook! Hello World runs end-to-end against the BF Hello World transliterated via the published mapping.

#### Tests

- `tests/test_ook.py` — 4 tests: YAML loads, Hello World runs to `Hello World!\n`, stray non-Ook atoms surface a clear error, dangling single Ook atoms surface a clear error.
- All previous tests still pass (20 → 24 total).

## [0.2.0] — 2026-05-17

### Schema-gap bundle from the 2026-05-17 interpreter-candidates survey

This release closes three of the four schema gaps surfaced by the [BF-family interpreter-candidates survey](research-notes/interpreter-candidates-2026-05-17.md) (the fourth — adding an operand slot to `Instruction` — is structurally larger and is deferred to its own release).

#### Added

- **`InstructionOp` values**: `HALT` (Spoon, La Weá), `BREAK_LOOP` (Brainlove), `JUMP_UNCONDITIONAL` (La Weá). All three are tape-legal. `HALT` is fully implemented in the interpreter; `BREAK_LOOP` and `JUMP_UNCONDITIONAL` are schema-legal for parameter-sheet authoring but the interpreter raises `InterpreterError` with a clear pending-runtime-support message — `BREAK_LOOP` needs runtime loop-stack tracking; `JUMP_UNCONDITIONAL` needs the deferred operand-slot extension.
- **`Encoding` values**: `VARIABLE_LENGTH_BINARY` (Spoon-style Huffman) and `WORD_LENGTH_DISPATCH` (Wordfuck-style). Both validate at the schema level; tokeniser support is deferred (the interpreter raises a clear `ParseError` for now).

#### Changed

- **`_check_brainfuck_tape_completeness` relaxed.** The strict pre-v0.2.0 rule was *a brainfuck_tape language must define all 8 canonical ops*. The new rule is a viable-minimum bar:
  - At least one pointer-moving op (`PTR_RIGHT` or `PTR_LEFT`).
  - At least one cell-modifying op (`INCREMENT`, `DECREMENT`, `ZERO`, `HALVE`, `DOUBLE`, `CLIPBOARD_RECALL`, `RANDOM`, or `INPUT`).
  - `LOOP_START` and `LOOP_END` both present, or both absent.
  - Any defined op must still be in the tape-legal set (unchanged).

  This unblocks Boolfuck-style subsets (no separate `DECREMENT` — `+` toggles the bit) and Smallfuck-style subsets (no I/O at all). Backward-compatible: the full canonical 8-op set still validates.

#### Tests

- 11 new `tests/test_schema_relaxed_completeness.py` tests covering: Boolfuck-style + Smallfuck-style subsets validate; canonical-8 still validates; minimum-bar rejections (no mobility, no cell-mod, unbalanced loops); new ops are tape-legal; new encodings are schema-legal.
- 4 new `tests/test_interpreter.py` tests: `HALT` stops execution; `BREAK_LOOP` and `JUMP_UNCONDITIONAL` raise the expected `InterpreterError`.
- All previously-passing tests still pass (5 existing → 16 total → 20 with the new interpreter tests).

### Deferred to a follow-up release

- **`Instruction.operand` field**. The fourth schema gap from the survey. Foundational for the OISC and register base machines (Subleq's `SUBLEQ a b c`, Minsky's `DEC reg label`) and for register-style BF derivatives (COW, Brainlove). Touches the schema, the loader, and the interpreter trampoline; intentionally separate from this bundle so the changes can be reviewed in isolation.

## [0.1.0] — 2026-05-11

### Added

- Initial vertical-slice runtime for the Brainfuck-tape family: `LanguageSpec` schema, YAML loader, interpreter, transpiler.
- Two shipped parameter sheets: `brainfuck-vanilla.yaml`, `brainfuck-rioplatense.yaml`.
