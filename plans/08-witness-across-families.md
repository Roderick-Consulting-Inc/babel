---
title: "What a debugger across eight esolanguages taught us"
subtitle: "Witness Mode, the spec/implementation iceberg, and the contract that emerged"
author: "Ramon Rodriguez (RCI)"
date: "2026-05-18"
---

# What a debugger across eight esolanguages taught us

## I. The first surprise

We were building a step debugger for Brainfuck. The first family, the simplest, the one with eight ASCII tokens and an unambiguous tape. The runtime trace hook fired once per op; the snapshot carried the current cell, the pointer, the just-emitted byte. The frontend listened for snapshots, advanced a highlight token by token in the source pane, animated the tape in a memory map. Everything worked.

Then we wired in the second family — Stack — and the highlight worked. We wired in OISC (Subleq), and the highlight pointed at the wrong cell after the second step. We wired in Inflexión, our Spanish-grammar AST-eval language, and the memory map kept showing the state *before* the last statement ran — the actual final write was invisible. We wired in INTERCAL — our hand-built tribute to the 1972 Woods and Lyon original — and the source highlight silently skipped any line with non-canonical whitespace. By the time we'd wired in seven families, we had a dozen distinct bugs in the debugger, and a dawning sense that we were not, actually, building one debugger over and over. We were building eight, and they were silently disagreeing with each other in ways the language specs had not equipped us to predict.

This installment is what we learned from that. It is mostly a story about *implementation residue* — the requirements that show up only when you build the second tool on top of a language and that turn out, by then, to be load-bearing forever. We think the lesson generalises beyond esolanguages, but esolanguages are where it bit us, so esolanguages are how we tell it.

## II. The natural experiment

The Babel Playground (`babel.roderickc.com`) hosts as of this writing eight language families: twelve Brainfuck-tape dialects, two stack languages (a minimal pedagogical one and Wouter van Oortmerssen's FALSE), Subleq as the OISC representative, Befunge-93 for the 2D-grid family, Inflexión for the Spanish-grammar family, INTERCAL for the Woods-Lyon 1972 lineage, FRACTRAN for Conway's 1987 fraction-as-instructions register machine, and most recently Whitespace for the "only space, tab, and linefeed are meaningful" lineage. Twenty-something total languages across eight family-shapes.

We did not set out to do an experiment in cross-family debugger architecture. We set out to add Witness Mode — a step debugger with a source-pane highlight, a per-step state pane, and a persistent memory map — to a playground that already had seven of those families. The "experiment" is the one we conducted accidentally by trying to write generic UI code on top of seven interpreters that had only the loosest agreement about what an interpreter *exposes*.

We mention this because we believe the cross-family observation is the part that's transferable. Anyone who builds a step debugger for a *single* esolanguage will end up with an interpreter that exposes whatever happens to make the debugger work. They will not necessarily notice that the choice — *when in the dispatch loop should the trace hook fire?*, *what should it mean for "the program counter" to be at position N?* — was a choice at all. We noticed because we made *eight* of them and discovered, sometimes painfully, that they were not all the same choice.

## III. The first cleavage: snapshot timing

We will name the architectural decision that produced the most bugs: *when in the dispatch loop does the trace hook fire?*

Two answers naturally arise:

- **After.** The interpreter runs an op, *then* fires the hook. The snapshot carries the post-op state — "what the just-executed op did." This is the natural choice for a machine-style interpreter whose dispatch loop is `while pc valid: execute op[pc]; advance pc`. The post-execution state is right there when the loop body finishes.

- **Before.** The interpreter fires the hook, *then* dispatches the statement. The snapshot carries the pre-statement state — "what's about to happen." This is the natural choice for an AST-eval interpreter whose dispatch loop is `for stmt in program.statements: execute(stmt)`. The hook fires at the top of the loop body, before the statement runs.

Both are reasonable. We have five families in the first camp (Brainfuck, Stack, OISC, Befunge, FRACTRAN) and three in the second (Inflexión, INTERCAL, and — almost — Whitespace, which we made after-snapshot deliberately, having learned by then to ask).

The bugs came from the asymmetry. Specifically, in a *before*-snapshot family, the LAST statement's effects are never observed. The hook fires before it runs; nothing fires after. A program ending in `Hacé que la x esté en 99.` would show `x == 0` in the memory map forever, because the snapshot that *would* have shown `x == 99` doesn't exist.

The naive fix is to also fire the hook after each statement (the "pair" or "before-and-after" pattern). We didn't do this, partly because it doubles snapshot volume and partly because there's a cheaper fix that loses less: have the runtime append one synthetic snapshot after the dispatch loop completes, carrying the post-program state. We call it `ProgramEnd` in Inflexión and `PROGRAM_END` in INTERCAL. It has a sentinel value in its `kind` / `op` field so any client can recognise it, and its `pc` / `top_stmt_idx` is past-the-end so source-pane highlighters drop the cursor cleanly.

But the timing cleavage produced *three more* bugs we hadn't anticipated, each a quiet off-by-one in some downstream UI logic:

- The "just-changed" row-flash in the memory map computes its set of recently-changed bindings from `trace[stepIdx-1].delta` — correct for after-snapshot families, off-by-one for before-snapshot families. The flash fires one step late.
- The "last-modified-step" map populated during delta replay assumes the delta in `snap[i]` represents a change at step `i+1` (after-snapshot convention). For before-snapshot families it's actually `i`. Click-to-jump-to-last-change lands at the wrong step.
- The view-the-current-state lookup uses `trace[stepIdx]` for before-snapshot families (post-statement state is in the *next* snapshot's "pre" data) but `trace[stepIdx-1]` for after-snapshot families. Wiring this generically requires the renderer to know which kind of family it's looking at.

We caught all four eventually. The pattern is clear in retrospect: snapshot timing is a *language* design decision in disguise. The dispatch-loop authors thought they were picking how to write a `for` loop. They were actually picking the trace contract that every external tool will inherit forever.

## IV. The second cleavage: position is not a token

The second category of bug came from a different unspoken assumption: that a snapshot's `pc` field is an index into the source-token array. For most families this is true. For OISC, it isn't.

OISC's program counter is a *memory address*. Each SUBLEQ instruction occupies three memory cells, so `pc` advances by 3 per instruction. The source-token array — the user-visible "this is op 0, this is op 1, this is op 2" — indexes by op number, not by memory address. The first op is at `pc=0`, the second at `pc=3`, the third at `pc=6`. The frontend's "highlight `spans[pc]`" worked accidentally for the first op (because `0/3 == 0`) and then drifted: the second op was at `pc=3`, but `spans[3]` was the fourth triple (the program's data cells), not the second instruction. By the third op, `pc=6` was off the end of the spans array and no highlight rendered at all.

This is a small bug — three lines in the frontend to divide by three when the family is OISC — but the cause is general. A `pc` field on a snapshot is *not* automatically an index into anything in particular. It's an index into whatever the runtime's notion of "current position" is. In a stride-1 family, that happens to align with source-token index. In a stride-k family, it doesn't. In a 2D-grid family (Befunge), there is no linear `pc` at all; the position is `(row, col)`. In a coordinate-free family like INTERCAL (where `pc` is the statement index in a list, with no source-text granularity finer than statement) the `pc` happens to map back to source by way of a separate `source_line_num` field.

We could have predicted all this from the language specs. Subleq's "an instruction is three integers" implies `pc` stride 3. Befunge's "the IP moves on a 2D grid" implies coordinates. INTERCAL's "one statement per source line" implies statement-index addressing. The specs do not *name* the implication — they leave the implementation to derive it. Multiple sibling tools deriving it independently will pick the same answer if they're disciplined, and silently divergent answers otherwise.

## V. The third cleavage: the source pane is part of the language

The third category — the costliest to debug — comes from natural-language esolanguages.

Inflexión is a Spanish-grammar esolang. Its program text is real Spanish, structured to expose the design's grammar-as-semantics mapping. Statements end with `.`. To highlight the current statement in the source pane, our first design simply walked the source text in the frontend, splitting at each `.` to find sentence boundaries.

The bug surfaced the day a user ran `precios.infl` — a four-statement program whose second statement is `El descuento es 0.10.`. The decimal point in `0.10` is *also* a `.`. The frontend, having no concept of float literals, treated it as a sentence terminator and split the program into five "sentences" instead of four. From the second statement onward, every snapshot's "current statement" highlighted the wrong line.

INTERCAL hit a closely related bug. The INTERCAL parser normalises whitespace when it stores the source line: tokens get joined with single spaces. The user's source might have `(1000)  PLEASE DO READ OUT .1` — two spaces between the label and the keyword — and the parser would record `(1000) PLEASE DO READ OUT .1` as the canonical text. The frontend matched by string equality (after `.trim()`); the user's line had two spaces, the parser's record had one; no match; no highlight. The bug shipped, ran, produced silently-wrong UI behaviour for one of our own bundled examples, and was caught only because we audited.

The two bugs share a structural cause: *the frontend was being asked to re-tokenise the source*. The runtime had the right tokenisation — it had to, to parse the program — but didn't expose it to the trace. The frontend re-derived sentence boundaries from source text and got them wrong in two different ways for two different families.

We fixed each bug locally (special-case the `.` in float literals; collapse all whitespace runs before comparing). Both fixes worked. Both fixes were also fragile, since they encoded the runtime's tokenisation rules as a *second* implementation in JavaScript. Any future change to either runtime's lexer would silently drift from the frontend's copy.

The actual fix arrived weeks later as v2.0 of our witness protocol. We added a `line: int` field to each token in both Inflexión and INTERCAL lexers, propagated it through the parser to the AST, and exposed `source_line_num: int` on each trace snapshot. The frontend's source pane became a fifteen-line function: split the source into lines, highlight the one at `source_line_num - 1`. The float-literal bug became structurally impossible. So did the whitespace-normalisation bug. The seventy lines of frontend tokenisation-cum-text-matching went into the dustbin.

The lesson, restated: a debugger's source pane is part of the language's contract. Either the runtime exposes positions, or every UI re-derives them. We tried the second for a year and learned why the first is better.

## VI. The contract becomes load-bearing

By the time we'd worked through these three cleavages (and a fourth — display duplication in the Befunge memory map — and a fifth — the deploy gotcha where our CI/CD pulled the playground repo but not sibling runtimes — but those are smaller stories), the trace contract had grown teeth.

Snapshots had to carry `op` and `output_len` always. Machine-style families had to carry per-op fields like `cell_after` (BF), `mem_b_after` (OISC), `stack_after` (Stack and Befunge). AST-eval families had to carry `top_stmt_idx` and now `source_line_num`. Before-snapshot families had to fire a terminal `ProgramEnd` sentinel. The streaming SSE variant had to emit `meta`, then `memory_init`, then `step*`, then exactly one of `done` or `error`. The backend had a per-family delta computer (`_bf_delta`, `_oisc_delta`, `_inflexion_delta`, `_intercal_delta`, `_fractran_delta`, `_whitespace_delta`). The frontend had per-family renderers in five places.

None of this is what we set out to build. We set out to add a step debugger. We ended up with a *protocol* — a versioned contract that any new language family has to honour to plug in. As of this writing it has eight implementations across four sibling runtimes (Babel, Inflexión, Intercal, Whitespace) and an API surface in the playground that, taken together, comprises something we now have to maintain *as a public interface*. The cost of breaking it is the cost of breaking eight clients at once.

We wrote it down. The protocol document — a flat eleven-section markdown file with a twenty-one-step checklist for adding the ninth family — is now the first thing a new contributor reads, before they look at any existing family's code. We wish we'd written it the day after we wired up the third family. We wrote it the day after we wired up the seventh.

## VII. The eighth-family test

A few days after we wrote the protocol, we tested it. Whitespace seemed like the right ninth family to add: 2003, hand-buildable in a few hundred lines, a different machine model (stack + heap + subroutines + bounded labels) from anything we already had, and a famously hostile surface syntax — only spaces, tabs, and linefeeds are meaningful, with letters in comments stripped as noise.

The protocol's §10 checklist worked. The runtime exposed `trace_hook` per the specified API; the backend dispatch needed two new lines; the frontend renderers needed a new branch for the `whitespace` family identifier; the sample-catalog regression tests added four cases; the deploy unit needed a new env var. Total integration time was roughly the protocol's predicted "machine-style family, low-to-medium friction" budget.

One thing did surface: Whitespace instructions are *variable-length*. A single instruction can be three to fifteen bytes of source. We hadn't anticipated a family whose instructions span ranges rather than positions. The fix was small — add a `span: [start, end]` field to the snapshot, treat it as a new "Token-by-range" source-mapping convention, document it as the protocol's seventh sub-convention, bump the protocol to v1.1. The eighth family didn't reverse-engineer the contract from five sibling implementations; it picked one new addition cleanly and the addition went into the spec. That, we think, is what a working protocol *looks* like.

What we didn't hit: any of the previously-cataloged bug shapes. No snapshot-timing off-by-one, no PC-stride mismatch, no source-text re-tokenisation. The Whitespace runtime fires the hook after each op, carries full state inline in every snapshot, and provides explicit source spans. Each of those choices was made consciously, with knowledge of what each option costs downstream. We made them in fifteen minutes apiece. The first seven families had made them implicitly, sometimes years apart, with no way to consult the choices the others had landed on.

This, we think, is the real value proposition of a written protocol for a multi-tool project. Not that it prevents bugs in the protocol itself (it doesn't; we'll find more). It prevents *redundant* bug discovery — every contributor relearning the same off-by-one through their own bruises.

## VIII. The implementation iceberg

The pattern across all the above is, we think, more general than esolanguages and more general than debuggers. We'll name it directly.

A language specification — and most specifications — describes a *user-facing surface*. What programs mean, what compiles, what runs. The implementation requires far more: how to recover from parse errors, what error messages to emit, what evaluation-order tie-breakers to use, when in the dispatch loop the world is consistent enough to be snapshotted, how to map a runtime cursor back to a source position. The spec is the visible tip; the implementation iceberg is much larger. And — this is the part that bit us repeatedly — *which part of the iceberg you discover is determined by what you try to do with the language*. Write a parser, and you discover the tokeniser-disambiguation iceberg. Write a compiler, and you discover the calling-convention iceberg. Write a debugger, and you discover the observability iceberg.

Each external tool — and a debugger is just one such tool — adds requirements that the language spec was silent about and that, once met by some implementation, become *load-bearing* commitments that any future client of that tool must honour. The protocol document we now maintain is, in effect, a list of all the choices that we made while building Witness Mode and that we are now stuck with. Most of those choices look obvious in retrospect. None of them were named in any of the four runtimes' original specs.

We do not think this is a flaw in those specs. Inflexión's §3 declares six grammar-semantic mappings; we don't fault it for not also declaring when an observer of execution should be told about state changes. INTERCAL-72's manual specifies the politeness rule with mathematical precision; we don't fault it for not also specifying what `source_line` should look like for a statement with two consecutive spaces. The point is structural: every language has these unanswered questions, and every external tool answers some of them. The question, for any project that expects to outlive its first tool, is *where do those answers get written down*.

Our experience says: in the spec, on the day the spec is written, if you can. Failing that, in a protocol document, before the third sibling tool is built. Failing that, in retrospect, as ours did, when the bugs have already shipped and the fixes have already accumulated. We have done all three. The first is the cheapest by an order of magnitude.

## IX. What an esolanguage *is*, slightly reframed

We will close by suggesting that this work has gently shifted our internal view of what an esoteric programming language *is*, at least for tool-building purposes.

We came to this project with a definition that emphasised the user-facing surface: the syntax, the semantics, the conceptual move that makes the language interesting. Brainfuck's eight tokens, INTERCAL's PLEASE-rule, FRACTRAN's fractions-as-instructions, Inflexión's *ser*/*estar* split. The interesting part of the language was, in this framing, what the user *sees*.

After a year of building tools, we now believe the language is at least as much its *natively-observable shape*: what an external observer can see while the language runs. Brainfuck's tape-and-pointer model is observable in a way that lends itself naturally to per-cell visualisation. FRACTRAN's "N gets multiplied by one fraction per step" is observable as a single-integer trajectory. INTERCAL's COME FROM is observable only because the dispatch loop has a moment between statements where the hijack can be reported. Inflexión's grammar mappings are observable per statement, not per token, because the dispatch loop is statement-grained. Each of those is a design choice, even when it doesn't feel like one — and the choice becomes visible the moment you try to *observe* the running program from outside.

We do not think this re-frames the user-facing design. Inflexión is still about Spanish grammar as semantic substrate. INTERCAL is still about hostility-as-virtue. Whitespace is still about textually-invisible programs. What this work has clarified is that *the choice of natural step granularity*, *when the observer is notified*, *what an external "current position" means*, are part of the language's deep structure, not surface ornamentation. They were always there. The debugger is just the first tool that asked.

For the next installment in this series — we owe one to the operational-semantics paper on Inflexión, and one to a sibling on the Babel methodology after a year's worth of implementation has accumulated — we will try to bring this back. We suspect the right framing is something like *every language is a contract between a programmer and an observer*, where the observer is the runtime, debugger, profiler, compiler, repl, or future tool, and the contract is everything the program text doesn't say but every implementation has to answer.

That contract, in our experience, fills more pages than the user-facing surface. We just rarely write it down.

---

*Sibling artefacts referenced in this essay:*

- [Babel Playground repository](https://github.com/Roderick-Consulting-Inc/babel-playground) — the playground, `babel.roderickc.com`, and the source for the witness protocol docs.
- `babel-playground/plans/witness-mode-pitfalls.md` — the technical bug catalog that drove this essay.
- `babel-playground/plans/witness-protocol-v1.md` — the protocol document referred to throughout (v1.2 as of 2026-05-18).
- [Inflexión repository](https://github.com/Roderick-Consulting-Inc/inflexion) — the Spanish-grammar esolang's runtime.
- [Intercal repository](https://github.com/Roderick-Consulting-Inc/intercal) — the MVP-INTERCAL hand-built runtime.
- [Whitespace repository](https://github.com/Roderick-Consulting-Inc/whitespace) — the eighth-family integration that validated witness protocol v1.
