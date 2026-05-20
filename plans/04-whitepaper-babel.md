---
title: "Babel: A Methodology for Building Esoteric Programming Languages"
subtitle: "First Installment"
author:
  - Ramon Rodriguez
affiliation: RCI
date: 2026-05-20
abstract: |
  The esoteric-programming-language field has produced a vast corpus and a vague methodology — roughly 1,500 catalogued languages, including ~800 Brainfuck derivatives, each hand-rolled with the same restructuring work repeated. The field has examples but not a generator, variation axes but not a parameter schema, a museum but not a method. This paper proposes Babel: a methodology for the programmatic construction of esoteric programming languages, together with the parameter schema and a working runtime that make the methodology operable. From a chosen parameter set, three outputs follow in lockstep — a runnable interpreter, a transpiler to a chosen base, and a specification page. The methodology is the core contribution; the runtime is its demonstration. A vertical-slice runtime ships with this installment as `babel-runtime` v0.7.0, and a worked end-to-end example — interpreter run, transpile, and generated spec page for a Rioplatense Brainfuck derivative — appears in §7. A companion paper develops one specific instantiation of the design space: a hand-built Spanish-grammar esoteric language. A third installment treats LLM-oriented programming-language design as a parallel field and extends the schema accordingly; the present paper limits itself to the esolang field that motivated the methodology in the first place.
bibliography: ../references.bib
csl: ../csl/chicago-author-date.csl
link-citations: true
---

> *White paper, first installment of the Babel / Inflexión series. Style: Chicago author-date via pandoc + BibTeX. Voice: essayistic for curious minds. Citations are BibTeX keys (`[@key]`) and resolve through `references.bib`.*

## 1. A field that has produced examples but not a method

An esoteric programming language is a programming language designed to test the boundaries of what a programming language can be: usually small, often deliberately impractical, sometimes a joke that turns out to be a research programme on second reading. The community at esolangs.org [@esolangs_wiki] has been cataloguing them for over two decades. The wiki currently lists something on the order of 1,500 entries. Its single largest category is *Brainfuck derivatives* [@esolangs_bf_derivatives], with around eight hundred languages — each one a re-encoding of the same eight-instruction tape machine that Urban Müller distributed in 1993 [@mueller_brainfuck_1993] under a different surface form, a different cell width, a different alphabet, or a different cultural skin.

Read sympathetically, this is a remarkable creative output. Read carefully, it is also a strange artefact. Eight hundred authors took the same starting point and did the same kind of restructuring work, mostly without referring to each other's tools or inheriting each other's scaffolding. The field has produced a corpus but not a methodology. It has discovered the variation axes its languages move along — cell width, tape topology, instruction count, surface vocabulary, cultural theme — without ever consolidating them into a parameter schema that a new author could pick up and use.

The closest analogues elsewhere in computing are the long-running obfuscation contests — the International Obfuscated C Code Contest, running annually since 1984 [@ioccc], and the Obfuscated Perl Contest of the late 1990s [@obfuscated_perl_contest]. Those communities accept programs that are formally correct, executable, and unreadable without dedicated study. They explore the same gap that esoteric languages do — the gap between *what compiles* and *what communicates* — but from inside an existing language. The esolang field plays the same game from outside: it builds new languages that hold the gap open by design. Both communities have learned, in their own ways, what kinds of constraint produce interesting strangeness. Neither has produced a tool that would let the next contributor inherit that learning.

This paper proposes that tool. Babel is a methodology for the programmatic construction of esoteric programming languages, plus the parameter schema and runtime that make the methodology operable. The argument is that making the field's tacit variation axes explicit — and providing a runtime that turns chosen parameter values into a working language — changes the economics of esoteric-language design. It is a lever on the *next* eight hundred attempts, not on the existing eight hundred.

## 2. What an esoteric language is, for the purposes of this paper

The wiki at esolangs.org takes a generous view of what counts as esoteric. The category includes Turing-complete languages, sub-Turing languages, deliberately undecidable jokes, languages that exist as a single program, and languages that are formally identical to existing ones with one or two cosmetic substitutions. For the purposes of this paper, an esoteric programming language is one with at least the following features.

It has an executable semantics — there is a clear answer, in principle, to the question *what does this program do?* This excludes pure performance art and language-as-poetry projects, however adjacent they may be culturally. It has a small surface area — typically a few dozen instructions or fewer, often fewer than ten. This excludes the heavyweight production languages (Java, Python) and the small but architecturally rich ones (Forth, Lua) that aim to be genuinely useful at scale. And it has a deliberate constraint or strangeness — the language was designed to be in some way *interesting* rather than *useful*, where the interest comes from a chosen restriction, addition, or framing that production languages would not adopt.

These criteria admit Brainfuck (eight instructions, deliberate minimalism), Whitespace (only spaces and tabs are syntactic), Befunge (two-dimensional source grid), Shakespeare (English-language plays as syntax), Wenyan (Classical Chinese grammar as syntax) [@huang_wenyan], INTERCAL (deliberately user-hostile error messages), and Piet (program-as-bitmap). They exclude general-purpose languages with eccentric communities (Lisp, Smalltalk), code-golf languages whose goal is shortness rather than constraint (J, K), and pure jokes with no executable semantics.

The criteria are not particularly novel. The community has converged on something like them implicitly. Stating them explicitly matters because the parameter schema in the next section depends on having a definite class of artifact to parameterise. A schema that tries to cover everything — production languages, code-golf languages, executable poetry, and esolangs proper — would be too loose to be useful. Babel parameterises the class of language that meets the three criteria above.

## 3. The variation axes the field has implicitly used

The eight hundred Brainfuck derivatives, taken as a sample, vary along a small number of axes. Reading widely across the corpus suggests the following partition.

**The base machine.** Every esoteric language has an underlying execution model — the abstract machine its programs run on. The corpus uses, in approximate order of frequency: tape machines (Brainfuck and its derivatives), stack machines (FALSE, GolfScript), one-instruction-set machines (Subleq, BitBitJump), two-dimensional grid machines (Befunge, Hexagony), register-and-jump assembly clones, queue machines (Fueue), string-rewriting systems (Thue, Markov-style), and a handful of more exotic machines (combinator calculus, cellular automata as program). The base machine is the largest single design choice; everything else parameterises it.

**Memory shape.** Within a given base machine, the memory has a shape: a one-dimensional unbounded tape, a one-dimensional circular tape, a two-dimensional torus, a stack of fixed depth, an unbounded stack, a queue, a deque, a graph. Brainfuck's standard memory is a one-dimensional unbounded tape of byte-sized cells; Boolfuck uses a tape of bit-sized cells; Brainfuck Extended uses arbitrary-precision integers.

**Cell width.** Closely related but separable: the size of an individual cell. Bit, nibble, byte, word, arbitrary precision. Some languages allow signed values, some unsigned, some only positive.

**Instruction count and set.** A Brainfuck derivative might use the canonical eight instructions, a subset (Boolfuck), a superset (Brainfuck with debug or randomness), or a non-overlapping replacement. The instruction count typically ranges from one (OISC machines) to a few dozen (richer fungeoids). Larger instruction sets are usually re-encodings of small ones rather than truly novel additions.

**Encoding.** Once an instruction set exists, it has to be encoded in source text. The canonical Brainfuck encoding uses ASCII punctuation: `> < + - . , [ ]`. Whitespace encodes its instructions in tab/space/newline triples. Unary encodes its entire program as a single integer expressed in base-1. Binary, base-N, and natural-language-keyword encodings are all options.

**I/O model.** Character at a time is the dominant pattern. Some languages take whole-line input, some take an integer, some take no input and produce no output (the program's effect is its own internal state at termination), some treat the file system as I/O.

**Additions and removals.** Many derivatives are characterised primarily by what they add to or subtract from a base. La Weá adds a clipboard register to Brainfuck's eight instructions. Chespirito adds a randomness instruction. Brainfuck Lite removes the loop instructions. These additions and removals are the design choices that distinguish a derivative from its base; they are also where the most interesting work in the corpus lives.

**Theming.** Orthogonal to all the above is the surface theme — the cultural skin laid over the instruction set. Cooking (Chef), Shakespearean play (Shakespeare), action-movie quotes (ArnoldC), Schwarzenegger catchphrases (ArnoldC), Chilean slang (La Weá), 19th-century literary Chinese (Wenyan). Theming changes how the language reads without necessarily changing how it executes. It is the most visible design choice and often the one a new author chooses first; it is also, on its own, the cheapest contribution one can make to the corpus.

These eight axes — base machine, memory shape, cell width, instruction count and set, encoding, I/O, additions and removals, theming — between them account for most of the variation across the corpus. They are not the only possible axes, and Babel's schema (next section) will need to be open to additions. The third installment in this series [@rodriguez_llm_oriented_2026] takes up an adjacent field — LLM-oriented programming-language design — that surfaces further axes the original eight cannot cleanly express; those extensions are developed there, against that field's design choices, and are not folded into the present paper. The original eight are the foundation; any later extensions sit on top of them.

## 4. Babel's parameter schema

Babel proposes that an esoteric programming language can be specified, for the purposes of generation, as a parameter set across the axes inventoried in §3 plus a small number of *meta-parameters* that describe the language's character rather than its mechanism.

The mechanical parameters follow §3 directly: base machine, memory shape, cell width, instructions (token and operation), encoding, I/O model, additions, removals, theme. A YAML parameter sheet — the format the runtime consumes — collects these into a single document. The instruction set is given as a list of `(token, op)` pairs, where the canonical operation names form a fixed vocabulary the runtime dispatches on (pointer movement, cell modification, loop bracketing, I/O, plus a small set of well-known additions like a clipboard register or a halve primitive). New canonical operations are added to the runtime's vocabulary as the corpus surfaces them; the schema's openness lives there.

The meta-parameters are different in kind. They are knobs on what the resulting language *feels like* to read and write, not knobs on its mechanism. The proposed meta-parameter set:

**Complexity** measures the cognitive cost of writing a non-trivial program. A Subleq machine has high complexity (one instruction, large programs); Brainfuck has medium complexity; a richer fungeoid like Befunge has lower complexity per useful program.

**Abstraction** measures the gap between surface syntax and execution model. Brainfuck is low-abstraction (the instructions correspond directly to operations on the tape); Shakespeare is high-abstraction (a soliloquy assigns a value through letter counts and metaphor); Wenyan is high-abstraction in its surface syntax but lower in its underlying semantics.

**Verbosity** measures bytes per logical operation. Chicken (one token, repetition-encoded) is hyper-verbose; Brainfuck is moderate; J or K (single-byte tokens) are hyper-compact.

**Playfulness** measures the language's self-conscious humour, parody, or theatricality. INTERCAL, Chef, ArnoldC, Fetlang are high-playfulness; Subleq is low.

**Unpredictability** measures the degree to which the same program can produce different results across executions, or the degree to which the language's behaviour deviates from the programmer's reading of the source. Whenever (which executes statements when it feels like it) is high-unpredictability; Malbolge is high in a different way (the instruction effect depends on the address); a deterministic Brainfuck is low.

**Naturalness** measures how closely the language's surface syntax follows a natural-language grammar. The single-value framing first proposed for this axis turned out to be too coarse, as the Wenyan and Inflexión decompositions in §6 demonstrate: under one value, *Mierda* and *Inflexión* both reported as "naturalness involving Spanish" — collapsing a real structural difference (Mierda substitutes vocabulary; Inflexión engages grammar). The parameter resolves into three sub-values:

- *Vocabulary substitution.* The language's keywords are natural-language words but the grammar is otherwise English-keyworded-PL standard. Mierda, La Weá, Chespirito, BIRL, ArnoldC, and Monicelli sit here.
- *Lexical-grammar engagement.* The language uses natural-language morphology or word order in a partial way: a few inflection-driven syntactic rules over otherwise-standard PL grammar. LOLCODE, Shakespeare, and Rockstar approximately sit here; the position is sparsely populated relative to the other two.
- *Deep-grammar engagement.* The language's parser handles the substrate language's actual grammatical constructions: agreement, case, mood, aspect, clitic systems, particles in their literary positions. Wenyan, Perligata, Tampio, and Inflexión [@rodriguez_inflexion_2026] sit here.

A language can sit at any of the three levels independently of its other parameters. The decomposition resolves the *naturalness* coarseness that the original single value carried; the four-value version surfaced in the wider LLM-oriented field [@rodriguez_llm_oriented_2026] adds an anti-human-readable corner that does not apply to the esolang corpus this paper treats.

The meta-parameters are not independent of the mechanical parameters. *Verbosity* is partially a function of encoding and instruction count; *naturalness* is partially a function of theming; *unpredictability* sometimes leaks out of the instruction set (a Brainfuck derivative that adds a randomness primitive picks up nonzero unpredictability without changing any meta-parameter explicitly). The point of including the meta-parameters anyway is that they capture the design intent at a level a new author thinks at. A new author rarely starts with "I want a one-dimensional unbounded tape with byte-sized cells." They start with "I want something playful, high-verbosity, themed around X, primarily readable by humans." The meta-parameters let Babel meet the author at that level and resolve down to the mechanical parameters as a second step.

This two-layer schema is the methodological contribution. The field has had the mechanical axes available implicitly for thirty years; what it has not had is a vocabulary at the level of design intent that can be turned into a working language without each author rebuilding the same scaffold.

The schema is incomplete by design. The *naturalness* axis still risks coarseness within its three values; the *additions* axis is doing implicit work for evaluation strategy, effect model, and toolchain targets in ways future installments will need to break apart. The pattern of revision is the one §6 demonstrates: decompose existing languages against the schema, find the cells where the decomposition is muddy, extend or split the axis. The schema improves through friction with real artifacts rather than through theorising.

## 5. Three output targets, three readers

A parameter set is not a language. To turn a Babel parameter sheet into a usable artifact, the runtime produces three outputs.

The first is **a runnable interpreter** for the generated language. The shipped runtime is implemented in Python and reads source files written in the new language, executing them against the chosen base-machine semantics. The interpreter's role is to make the generated language *real*: a language without a working executor is a specification, not a programming language. The interpreter is also the artifact most useful to students and casual users, who can pick it up and run programs without engaging Babel itself.

The second is **a transpiler** that converts source in the generated language to a chosen target language — typically the language of its base machine (vanilla Brainfuck for Brainfuck-derivative generations) — so that programs written in the new language can be executed via existing toolchains. The transpiler matters for two reasons. It makes generated languages composable with tools already in the ecosystem; and it provides a second execution path that can serve as a sanity check on the interpreter.

The third is **a specification page** in the format of an esolangs.org wiki entry, giving the language's name and version, mechanical and meta-parameter values, instruction reference with surface tokens and canonical operations, additions and removals, and any example programs the parameter sheet carries. The specification is the artifact that joins the discourse: it is what other esolang authors read, what wiki maintainers can index, what reviewers cite, and what later installments of this project can refer back to. A generated language without a specification is a private toy.

Three outputs serve three readers — the user who runs programs, the developer who integrates with existing infrastructure, and the writer who joins the wiki community. None of the three is more important than the others; what matters is that the methodology produces all three from one parameter set, in lockstep, without each author having to reproduce the spec by hand from a working interpreter. §7 shows the three outputs for a concrete example.

## 6. Retrospective decompositions

The methodology can be tested by decomposing existing esoteric languages into their would-be Babel parameters. If the decomposition is clean — if the parameter sheet for an existing language picks out exactly that language and not its neighbours — the schema is doing useful work. If the decomposition is muddy, the schema needs revision. Four worked decompositions, drawn from the Spanish- and Chinese-flavoured corners of the corpus where the *naturalness* axis is most visibly load-bearing.

**Mierda** [@wiki_mierda] is a Brainfuck derivative with Spanish keywords. Its Babel parameter sheet would read: base machine = Brainfuck tape; memory shape = one-dimensional unbounded; cell width = byte; instruction count = 8; instruction set = {`Mas`, `Menos`, `Derecha`, `Izquierda`, `Decir`, `Leer`, `Iniciar Bucle`, `Terminar Bucle`}; encoding = natural-language keyword tokens separated by whitespace; I/O = character; additions = none; removals = none; theme = Spanish vocabulary. Meta-parameters: complexity medium, abstraction low, verbosity medium-high (the natural-language keywords inflate token length), playfulness moderate, unpredictability zero, naturalness *vocabulary substitution*. The decomposition is clean: every cell of the parameter sheet is filled in unambiguously, and the resulting parameter sheet picks out Mierda specifically.

**La Weá** [@wiki_lawea] is a Chilean-Spanish Brainfuck derivative with one significant addition — a clipboard register that stores a single byte separately from the tape. Its parameter sheet matches Mierda's on the mechanical axes except: instruction count = 16; instruction set = sixteen Chilean-slang tokens; additions = clipboard register with two associated instructions (store-to-clipboard, recall-from-clipboard); theme = Chilean dialect. Meta-parameters: similar to Mierda but with higher playfulness (the dialect register carries comic weight) and *vocabulary substitution* naturalness at the dialect end of the scale (Chilean slang is further from "neutral" Spanish vocabulary, which makes it *more* culturally specific even though no grammar is engaged). The decomposition picks La Weá out from Mierda specifically by virtue of the *additions* axis (clipboard register) and the dialect-specific *theme*.

**Wenyan** [@huang_wenyan] is harder and was the case that first surfaced the *naturalness* coarseness now formalised in §4. Its base machine is a procedural / variable-based machine with named variables, conditionals, loops, and functions — closer to a stripped-down ALGOL family than to a tape machine. Memory shape = named-variable model with no fixed shape; cell width = arbitrary-precision integer or string; instruction count = several dozen, organised into syntactic categories (declarations, control flow, arithmetic) rather than primitive operations; encoding = Classical Chinese characters and particles (者, 也, 而) in their literary positions; I/O = whole-line via standard input/output; additions = compilation to JavaScript, Python, and Ruby targets; theme = Classical Chinese literary register. Meta-parameters: complexity moderate, abstraction high, verbosity moderate, playfulness moderate (the language is taken seriously by its community), unpredictability low, naturalness **deep-grammar engagement** (the parser handles real Classical Chinese grammar, not vocabulary substitution).

**Inflexión** [@rodriguez_inflexion_2026] is the case that confirms the deep-grammar level needs to be a level rather than a binary. Its parameter sheet under the old single-value naturalness would have collided with Wenyan; under the three sub-values it picks out the same level but a different substrate language. Base machine = procedural / variable-based with explicit mutability typed through the *ser* / *estar* split; memory shape = named-variable; cell width = arbitrary-precision / typed; instruction count and set = the six grammatical-semantic mappings of §3 in the companion paper, each carrying one Spanish grammatical feature with a programming-semantic role; encoding = Rioplatense Argentine Spanish surface forms with `.infl` file extension; I/O = character (via *decí*, vos imperative); additions = the six mappings as joint feature set; theme = Rioplatense cultural register. Meta-parameters: complexity moderate, abstraction high, verbosity low (morphological packing carries semantic distinctions without expansion), playfulness moderate, unpredictability zero, naturalness **deep-grammar engagement**. The decomposition picks Inflexión out from Wenyan specifically via *substrate language* (Rioplatense Spanish versus Classical Chinese), *additions* (the *ser* / *estar* / mood / aspect / clitic / diminutive feature set), and *encoding* (vos imperatives, enclitic pronouns).

Four decompositions, two of which (Mierda, La Weá) ran cleanly against the original schema, one of which (Wenyan) forced the naturalness coarseness into the open, and one of which (Inflexión) confirmed the three-value naturalness decomposition is the right repair. The methodology is doing what a methodology should do: friction with new languages surfaces gaps; gaps drive schema extensions; the schema improves through use rather than through theorising. The companion paper develops Inflexión in detail [@rodriguez_inflexion_2026]; the wider LLM-oriented PL field, which decomposes against further axes the present schema does not carry, is the subject of the third installment [@rodriguez_llm_oriented_2026].

## 7. A forward example: Brainfuck Rioplatense

A retrospective decomposition tests the schema against an existing language. A forward example tests the runtime against a parameter sheet. Both are necessary; together they close the loop the methodology promises.

Suppose an author wants a small esoteric language with the following design intent. *Themed around the Argentine Rioplatense dialect, with voseo. Brainfuck-derivative base for ease of implementation. Eight instructions, vocabulary-substitution naturalness only (no grammar engagement; that is the companion language's territory). Moderate playfulness. Add one instruction that reflects something distinctive about the dialect: the diminutive suffix as a "halve the current cell" operation.*

The author writes a YAML parameter sheet — the file ships as `examples/brainfuck-rioplatense.yaml` in the runtime distribution:

```yaml
name: "Brainfuck Rioplatense"
version: "0.1.0"
base_machine: brainfuck_tape
memory_shape: 1d_unbounded
cell_width: byte
encoding: whitespace_separated_tokens
io: character
source_extension: ".bfri"
theme: "rioplatense_argentine"

instructions:
  - { token: "che",      op: ptr_right,  description: "Advance the data pointer (Argentine vocative)." }
  - { token: "vení",     op: ptr_left,   description: "Retreat the data pointer (vos imperative)." }
  - { token: "más",      op: increment,  description: "Increment the current cell." }
  - { token: "menos",    op: decrement,  description: "Decrement the current cell." }
  - { token: "decí",     op: output,     description: "Output the current cell as a character (vos imperative)." }
  - { token: "escuchá",  op: input,      description: "Read one character into the current cell (vos imperative)." }
  - { token: "mientras", op: loop_start, description: "Enter loop body if the current cell is nonzero." }
  - { token: "ya",       op: loop_end,   description: "Exit loop or loop back (Rioplatense terminative particle)." }
  - { token: "ito",      op: halve,      description: "Halve the current cell (diminutive suffix)." }

additions: ["halve_via_diminutive_suffix"]
removals:  []

meta:
  complexity:       medium
  abstraction:      low
  verbosity:        verbose
  playfulness:      moderate
  unpredictability: zero
  naturalness:      vocabulary
```

The sheet is short — under fifty lines including comments. The author runs three commands against it. Each command corresponds to one of the three output targets in §5.

**Output 1 — the interpreter.** The canonical "print the letter A" program rewritten in Rioplatense tokens runs end-to-end against the generated interpreter:

```
$ babel run examples/brainfuck-rioplatense.yaml \
    --program "más más más más más más más más mientras che más más más más \
               más más más más vení menos ya che más decí"
A
```

The interpreter reads the whitespace-separated tokens, dispatches each through the YAML's instruction table to the canonical operation, and executes against a one-dimensional unbounded byte tape. The program prints the byte 65 (`'A'`) and halts.

**Output 2 — the transpiler.** The same program transpiles to vanilla Brainfuck:

```
$ babel transpile examples/brainfuck-rioplatense.yaml \
    --program "más más más más más más más más mientras che más más más más \
               más más más más vení menos ya che más decí"
++++++++[>++++++++<-]>+.
```

The transpiler maps each surface token through the same instruction table to the canonical operation, then re-encodes each canonical operation as its vanilla-Brainfuck token. The lowering for the `halve_via_diminutive_suffix` addition is more interesting: a program that uses `ito` (the only mechanical departure from canonical BF) transpiles to vanilla BF's divmod idiom, since vanilla BF has no halve primitive:

```
$ babel transpile examples/brainfuck-rioplatense.yaml \
    --program "[130 'más' tokens] ito decí"
+++…+++>++<[->-[>+>>]>[+[-<+>]>+>>]<<<<<]>>>[-<<<+>>>]<<<>[-]>[-]<<.
```

The lowered program halves 130 to 65 using a six-instruction loop that decrements the source cell twice for every increment of a scratch cell. The author of the Rioplatense parameter sheet never wrote that loop; the runtime emitted it from the canonical `halve` operation. This is the kind of work the methodology saves a new author.

**Output 3 — the specification page.** The spec generator emits a Markdown wiki-style page directly from the parameter sheet:

```
$ babel spec examples/brainfuck-rioplatense.yaml
# Brainfuck Rioplatense — Specification

*Version 0.1.0. Generated by Babel runtime.*

## Overview

Vocabulary-skin Brainfuck derivative themed around the Argentine
Rioplatense dialect with voseo. Adds one diminutive-as-halve instruction
(the only mechanical departure from canonical BF).

## Mechanical parameters

| Parameter         | Value                          |
| ----------------- | ------------------------------ |
| Base machine      | brainfuck_tape                 |
| Memory shape      | 1d_unbounded                   |
| Cell width        | byte                           |
| Encoding          | whitespace_separated_tokens    |
| I/O model         | character                      |
| Theme             | rioplatense_argentine          |
| Source extension  | .bfri                          |

## Instruction set

| Token    | Operation  | Description                                    |
| -------- | ---------- | ---------------------------------------------- |
| che      | ptr_right  | Advance the data pointer (Argentine vocative). |
| vení     | ptr_left   | Retreat the data pointer (vos imperative).     |
| más      | increment  | Increment the current cell.                    |
| menos    | decrement  | Decrement the current cell.                    |
| decí     | output     | Output the current cell as a character.        |
| escuchá  | input      | Read one character into the current cell.      |
| mientras | loop_start | Enter loop body if the current cell is nonzero.|
| ya       | loop_end   | Exit loop or loop back.                        |
| ito      | halve      | Halve the current cell (diminutive suffix).    |

...
```

(The complete spec page continues with the additions list, the meta-parameter table, and the example programs the YAML carries. The full output is included alongside this paper as `generated/brainfuck-rioplatense/specification.md`.)

The three outputs were produced from the one parameter sheet by three CLI commands. No additional authoring was required between the sheet and any of the three artifacts. A new author who wanted to produce this language hand-rolled would spend an evening writing a small interpreter; if they wanted a transpiler and a wiki-style spec page they would spend a second evening. With Babel they fill in a parameter sheet, run three commands, and the three outputs are produced together, in lockstep, without ever drifting out of sync.

The example is deliberately modest. The point is not that *Brainfuck Rioplatense* is interesting on its own — it is a vocabulary-skin Brainfuck derivative with one minor addition, and the existing corpus already contains many such — but that its parameter sheet is short, fillable, and unambiguous, and that the three outputs follow from it mechanically. The interesting design choice (the *halve* primitive, surfaced from the dialect's productive diminutive morphology) is the kind of work the methodology is designed to leave room for: the author chose the addition, and the runtime did the lowering. That is the division of labour the methodology proposes.

## 8. Educational and academic value

The methodology has value for three audiences at three levels of engagement.

For *students*, Babel makes the field's variation axes legible without requiring the student to first build a working interpreter from scratch. A class on programming-language design can walk through the parameter schema as a taxonomy of design choices, with examples drawn from the corpus, and assign a project that is no longer "build an esoteric language" — a vague brief that produces uneven work — but "fill in this parameter sheet, run it through Babel, and write a one-page rationale for your choices." The student learns the same material and produces a comparable artefact, but the focus is on the *choice of parameters*, which is where the design thinking actually lives. The work the student saves on plumbing is reinvested in the work that matters.

For *researchers*, Babel provides a shared vocabulary for talking about what makes one esoteric language different from another. The current literature on esolangs — such as it is — relies on prose comparison and intuition. A parameter schema gives reviewers, citation-writers, and survey-paper authors a more compact way to summarise a language's design. It is the same kind of contribution that the *features* of typological linguistics make to comparative grammar work: not a substitute for careful prose, but a scaffold on which careful prose can be built more efficiently.

For *language designers* working in adjacent territory — not pure esolang authors, but people designing constrained languages, controlled natural languages [@attempto_ace; @nelson_inform7], domain-specific languages with deliberate strangeness, or pedagogical mini-languages — Babel's schema provides a sanity check on which axes have already been varied in the esolang corpus and which combinations are unexplored. A designer who finds their parameter sheet matching an existing esolang exactly is reinventing; one whose sheet does not match anything is exploring.

The field's historical literary precedents — Cheswick's narration of a security incident as a story [@cheswick_berferd_1992], Raymond's edition of the Jargon File [@raymond_jargon] as a vocabulary that does cognitive work, Kidder's portrait of a minicomputer team as a story of human effort [@kidder_soul_1981] — all suggest that technical artefacts are at their most useful when they are accompanied by the *language to talk about them*. Babel is, in part, an attempt to give the esolang field that language.

## 9. What this is not

Three things Babel is explicitly not.

It is not a production-language toolkit. The interpreter and transpiler outputs are intended for use, not for performance. There is no JIT, no optimisation, no profiling support, and no debugger beyond what the generated language's own semantics provide. The argument is not that production-grade tooling is undesirable; it is that production-grade tooling is the *next* problem, and conflating it with the methodology problem would muddy both.

It is not a replacement for hand-craft. Some of the most interesting languages in the corpus — Malbolge, Piet, Velato, Folders, Vigil — depend on creative leaps that no parameter schema can capture. Malbolge's instruction-effect-dependent-on-memory-address mechanism is not a value of any reasonable parameter; it is an idea. Babel is for the languages that *are* parameter-driven (which, per the corpus, is most of them), and it is meant to free up author energy for the ideas that aren't.

It is not finished. This is the first installment. The parameter schema as presented has at least one known limitation (the *additions* axis is doing implicit work for evaluation strategy, effect model, and toolchain targets that future revisions will need to split apart) and presumably others that will surface as the runtime is exercised against further corpus entries. The methodology will improve through use. A first installment that pretended to be complete would be both dishonest about its stage and unhelpful to whatever future author tries to push the work forward.

## 10. What comes next

The companion paper [@rodriguez_inflexion_2026] develops one specific instantiation of the design space Babel proposes to parameterise: a hand-built esoteric language that engages Spanish grammar — number, mood, aspect, *ser* / *estar*, clitic ordering, diminutive morphology — as the source of programming semantics rather than as theme. The companion paper joins a small lineage of inflection-driven non-English natural-language esolangs (Perligata in Latin, the unimplemented Espro in Esperanto, Tampio in Finnish, Wenyan in Classical Chinese) and is the first in that lineage to use a living Romance language [@conway_perligata_2000; @espro_2015; @hauhio_tampio; @huang_wenyan; @wiki_lawea]. That language is not generated by Babel and is not constrained by Babel's parameter schema; the choice to hand-build it was made to keep the language design free of any tooling limits not yet discovered. Once both Babel and the companion language exist as working artefacts, a future installment can ask whether Babel's parameter schema can express the companion language. The answer, whatever it is, will be informative about the schema. The companion language is catalogued on the esolangs.org wiki at <https://esolangs.org/wiki/Inflexión>.

The third installment [@rodriguez_llm_oriented_2026] treats the parallel field of LLM-oriented programming-language design as an adjacent corpus and extends Babel's parameter schema to cover it. That extension does not bear on the esolang material in the present paper; it is developed against the LLM-oriented field's own design choices, in its own paper, where the audience is the one whose work the extensions address.

Further installments of *this* paper will address: refinement of the *naturalness* sub-parameters as the corpus surfaces gradient cases within each of the three values; decomposition of the *additions* axis into the evaluation-strategy, effect-model, and toolchain-target sub-axes the schema currently flattens; and an empirical comparison of hand-rolled and Babel-generated language production effort, sufficient to support or refute the order-of-magnitude claim in §1.

The vertical-slice runtime ships with this installment as `babel-runtime` v0.7.0, a Python package with parameter sheets for vanilla and Rioplatense Brainfuck plus fifteen other example languages drawn from across the corpus (Ook, Alphuck, Baguafuck, German, Pikalang, Spoon, Wordfuck, Mierda, La Weá, Chespirito, FALSE, Befunge, minimal-stack, Subleq, fungeoid). All run end-to-end through the interpreter; all generate spec pages through the spec emitter; the Brainfuck-derivative family additionally transpiles to vanilla BF. A small browser playground at `babel.roderickc.com` exposes the runtime to readers without a local install: pick a parameter sheet (vanilla Brainfuck or Rioplatense Brainfuck), type a program, watch it run.

The series is the unit of work. This first installment is meant to be readable on its own, but its main value is in establishing the methodology and the vocabulary the rest of the series will build on.

## 11. A closing note

Esoteric programming languages are usually read as a joke first. Read again, slowly, they are a research programme on what mainstream programming languages quietly assume — about syntax, about state, about how a program is supposed to communicate with the person reading it. The two readings are not in conflict. The joke is real, and the research programme is real.

The field has carried the research programme for thirty years on the energy of individual practitioners working in parallel, mostly without inheriting each other's tools. That work has produced an enormous corpus and proportionally little methodology. Babel is offered as a methodology — specifically, a methodology that lets the field's tacit variation axes be made explicit, parameterised, and turned into working languages with three outputs in lockstep. The contribution is not a new esoteric language. It is *a technique for making esoteric languages*, of the kind a museum acquires only after it has accumulated enough specimens for the curation to start mattering.

A methodological note worth carrying through future installments: this paper's approach to its own novelty claims has been *honest preparation* — writing down where pushback is expected and looking for the precedents that would falsify the claims before review rather than after. The lineage acknowledged in §10 surfaced through exactly this practice: a pre-publication literature check intended as confirmation found four prior authors whose work shifted the companion paper's framing from *first* to *fifth in a small lineage*. The same discipline applies forward: any author using Babel whose parameter sheet matches an existing entry is reinventing rather than extending, and the schema's value depends on authors being willing to discover that before the wiki community does.

A wider observation, treated more fully in the LinkedIn series accompanying this paper: technical vocabulary in mainstream programming languages is a deliberate register that strips cultural and historical context from the words it borrows — *daemon* loses Hesiod's *daimon*, *cookie* loses the bakery, *fork* loses both cutlery and the road. The strip-down is useful but not free: the weight remains *available* to a careful reader and *invisible* to a casual one. The esoteric-language field has often moved in the opposite direction, letting cultural weight be visible at the cost of portability. Babel's *theming* axis (§3) names this design choice explicitly so it is no longer silently inherited; the companion paper [@rodriguez_inflexion_2026] develops the move further, building a language whose grammar — not only vocabulary — engages cultural specificity.

The next eight hundred attempts can be different from the last eight hundred.

---

## Authorship and contribution

This is the first installment of a planned series on the construction of esoteric programming languages and on the role of culture and language in computing technology. It is authored by Ramon Rodriguez under the auspices of RCI. The series welcomes additional authors and collaborators; correspondence to be directed through RCI publication channels.

The companion paper, *Inflexión: A Spanish-Grammar Esoteric Language* [@rodriguez_inflexion_2026], treats one hand-built instantiation of the design space this paper opens. The third installment, *LLM-Oriented Programming-Language Design: A Methodology* [@rodriguez_llm_oriented_2026], extends the present paper's schema against an adjacent field.

## Acknowledgements

To the esolang community for thirty years of patient corpus-building. To Urban Müller for the eight instructions everything else is a derivative of. To the wiki maintainers at esolangs.org for the catalogue that made the survey possible. To the early readers whose pushback shifted the paper from a single sweeping schema-for-everything to the esolang-focused first installment it is now, with the LLM-oriented work moved to a third installment where it belongs.

## References
