# Changelog

All notable changes to the Babel runtime are recorded here. Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versions follow [Semantic Versioning](https://semver.org/spec/v2.0.0.html). The runtime is pre-1.0; the schema and API may change between minor versions.

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
