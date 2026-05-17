# Changelog

All notable changes to the Babel runtime are recorded here. Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versions follow [Semantic Versioning](https://semver.org/spec/v2.0.0.html). The runtime is pre-1.0; the schema and API may change between minor versions.

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
