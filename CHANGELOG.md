# Changelog

All notable changes to the Babel runtime are recorded here. Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versions follow [Semantic Versioning](https://semver.org/spec/v2.0.0.html). The runtime is pre-1.0; the schema and API may change between minor versions.

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
