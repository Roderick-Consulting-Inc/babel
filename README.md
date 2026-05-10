# Babel

A methodology for the programmatic construction of esoteric programming languages, plus the parameter schema and runtime that turn methodology into working artifacts.

The esoteric-language field has produced a vast corpus and a vague methodology. The wiki at [esolangs.org](https://esolangs.org) catalogues something on the order of 1,500 named languages, with roughly 800 Brainfuck derivatives in the largest single category — every one of them hand-rolled, every author repeating the same restructuring work. The field has produced examples but not a generator; variation axes but not a parameter schema; a museum but not a method.

Babel proposes the method.

A Babel parameter sheet specifies an esoteric programming language across two layers — the *mechanical parameters* the field has implicitly varied for thirty years (base machine, memory shape, cell width, instruction set, encoding, I/O model, additions and removals, theming) and a small set of *meta-parameters* that name design intent at the level a new author thinks at (complexity, abstraction, verbosity, playfulness, unpredictability, naturalness). The runtime turns a parameter sheet into three outputs in lockstep: a runnable interpreter, a transpiler to a chosen base language, and a specification page in the style of an esolangs.org wiki entry.

The contribution is not a new esoteric language. It is *a technique for making esoteric languages* that the field has lacked for thirty years, made operable.

## Where to start reading

This repository is in its planning phase. The intellectual work — motivation, prior art, position, methodology — is laid out in a sequence of foundation documents and white papers in [`plans/`](plans/), to be read roughly in order:

| | Document | What it covers |
|---|---|---|
| 00 | [README for the planning track](plans/00-README.md) | Index and reading order |
| 01 | [Motivation](plans/01-motivation.md) | Why we are doing this |
| 02 | [Inspiration](plans/02-inspiration.md) | Prior art, precedents, the esolang corpus, and the literary-technical tradition the project draws on |
| 03 | [Position](plans/03-position.md) | What we solve and what we don't |
| 04 | [White paper: Babel](plans/04-whitepaper-babel.md) | The methodology paper itself, first installment |
| 05 | [White paper: Inflexión](../Inflexion/plans/05-whitepaper-inflexion.md) | The companion language paper (lives in the sibling [Inflexion repository](../Inflexion/)) |
| 06 | [Anticipated objections](plans/06-objections.md) | Pushback we expect from each constituency, with current best replies |

A reader new to the project should start with [`01-motivation.md`](plans/01-motivation.md) for the framing and read through `04` for the substantive contribution. The companion language paper in the sibling [`/data/rci/Inflexion/`](../Inflexion/) repository develops one specific instantiation of the design space Babel opens.

## What this is and is not

Babel is a *methodology* paper and an *implementation* in active development. It is not, yet, a finished tool. The runtime is being built in Python (parameter sheets in YAML; schema definition through Pydantic; full triple of outputs — interpreter, transpiler, spec emitter). When the runtime stabilises, the worked examples in `04` §7 will be replaced with real generated artefacts; until then they are honest thought experiments.

Babel is not a production-language toolkit. It is not a replacement for hand-craft (some esoteric languages — Malbolge, Piet, Folders — depend on creative leaps no parameter schema can capture). It is a lever on the *next* eight hundred attempts, not on the existing eight hundred.

## Citation infrastructure

White papers use Chicago author-date through pandoc and BibTeX. The shared bibliography lives at [`references.bib`](references.bib); the citation-style file lives at [`csl/chicago-author-date.csl`](csl/) (fetched from the [CSL styles repository](https://github.com/citation-style-language/styles) at first render). The canonical citation URL is the `roderickc.com/babel` page; the project does not currently use arXiv (no DOI). If a DOI becomes useful later, [Zenodo](https://zenodo.org) integrates with GitHub releases and assigns one without an endorser. Render with:

```bash
pandoc plans/04-whitepaper-babel.md \
  --citeproc \
  --bibliography=references.bib \
  --csl=csl/chicago-author-date.csl \
  -o 04-whitepaper-babel.pdf
```

## Licensing

Different artifacts under different licenses, all permissive and attribution-required:

- **Code** (the runtime, when it lands; everything in `src/` and `tests/`): [Apache License 2.0](LICENSE). Permissive + explicit patent grant.
- **Documents** (everything in `plans/`, `publications/`, this README, `CLAUDE.md`): [Creative Commons Attribution 4.0 International (CC-BY 4.0)](LICENSE-DOCS). Reusable with attribution; arXiv-compatible.
- **Bibliography** (`references.bib`): [CC0 1.0 Universal](https://creativecommons.org/publicdomain/zero/1.0/) public-domain dedication. Bibliographic facts are facts.

Attribution form for the docs: *"Rodriguez, Ramon (RCI), Babel: A Methodology for Building Esoteric Programming Languages, [year], CC-BY 4.0."* Citation conventions vary by venue; the underlying licence is what matters.

## Authorship and contribution

Authored by Ramon Rodriguez under the auspices of RCI. Additional authors and collaborators welcome — the project is open to extension on every front (additional parameter axes, alternative implementation languages, dialect-specific instantiations of the companion language). Correspondence through RCI publication channels.

## Series

Babel is one half of an ongoing two-part series. The other half is [Inflexión](../Inflexion/), a hand-built Spanish-grammar esoteric language that occupies one specific instantiation of the design space Babel opens. The two artefacts inform each other but do not depend on each other; either can be read on its own.
