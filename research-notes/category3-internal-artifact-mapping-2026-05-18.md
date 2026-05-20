# Category 3: Internal-artifact citation audit

Drafted 2026-05-18 to close the loop on the three `@unpublished`
"internal Rodriguez research artifacts" cited in `04-whitepaper-babel.md`
and `07-whitepaper-llm-oriented-pl.md`.

## The problem

Three citation keys in `references.bib` describe internal research
artifacts that do not exist as files in this repository:

- `empirical_step1_extended_2026` — *"Installment 07 Empirical Step 1
  (Extended): Four-Way Verbosity Stratification"*
- `babel_schema_audit_2026` — *"Babel Parameter-Schema Audit Against the
  2024-2026 LLM-Oriented PL Field"*
- `empirical_e4_e7_e9_2026` — *"Installment 07 Schema-Extension Data
  Gathering: E4, E7, E9"*

These citations are load-bearing. They support specific empirical claims
in 04 and 07 (the four-way stratification numbers, the E1–E10 schema
extensions, the "set-valued E4" finding, the "n/a — deterministic by
design" E7 finding, the "decoder-contract" E9 finding). Until 2026-05-18
the bib treated them as internal artifacts pending write-up.

## What the artifacts actually are

The artifacts **do exist**, but as published research notes in the
companion website repository — not in the Babel repo. The substance
matches one-to-one for two of the three:

| Bib key | Published research note (www.roderickc.com) |
|---|---|
| `empirical_step1_extended_2026` | [`four-way-verbosity-stratification.md`](https://www.roderickc.com/babel/research-notes/four-way-verbosity-stratification) — drafted 2026-05-13, published 2026-05-16. Same five-programs-by-three-forms-by-six-tokenizers setup; same 36.2% / 359.9% / per-program −28% numbers; same Inflexión decorrelation finding. |
| `babel_schema_audit_2026` | [`per-artifact-audit-table.md`](https://www.roderickc.com/babel/research-notes/per-artifact-audit-table) (raw scoring data) plus [`design-axes-verified-and-tenth.md`](https://www.roderickc.com/babel/research-notes/design-axes-verified-and-tenth) (verification + the tenth axis recommendation). Drafted 2026-05-17 from the mid-2026 lit pass. |
| `empirical_e4_e7_e9_2026` | *No clean match.* The E4/E7/E9 findings appear in `design-axes-verified-and-tenth.md` but framed as conclusions inherited from "an earlier audit pass." The earlier pass itself was never written up as a standalone note. |

So two of the three artifacts are real and reachable; the third is the
upstream feeder of the second and was not separately published.

## What the citations want from the reader

- `empirical_step1_extended_2026` cited in 07 §8 for the dataset; in 04
  §verbosity (E3) for the SimPy / Inflexión decorrelation numbers. Both
  contexts want a reader to be able to verify the numbers against a
  primary source.
- `babel_schema_audit_2026` cited in 07 §6 for the E1–E10 extension
  list. Wants a reader to verify the extensions came from a real audit.
- `empirical_e4_e7_e9_2026` cited four times in 04 (the E4 set-valued
  finding; the E7 sub-value addition; the E9 decoder-contract and n/a
  values; the recommendation against an environment-driven-nondeterminism
  axis). Each citation wants the reader to verify the recommendation
  came from a real data-gathering pass.

In all three cases, the published research notes deliver what the
citations promise — the numbers, the categorisation, the
recommendations. The mismatch is bibliographic, not evidentiary.

## Recommendation

Replace each `@unpublished` placeholder with a `@misc` entry that points
at the actual published research note, with `howpublished` clarifying
the artifact kind and `url` pointing to www.roderickc.com:

```bibtex
@misc{empirical_step1_extended_2026,
  title        = {The Four-Way Verbosity Stratification},
  author       = {Rodriguez, Ramon},
  year         = {2026},
  howpublished = {{RCI} research note, www.roderickc.com},
  url          = {https://www.roderickc.com/babel/research-notes/four-way-verbosity-stratification},
  note         = {Stage 1 of the empirical cascade defined in Installment 07 §7. Five short programs measured across three surface forms (Python, SimPy-style hand-strip, Inflexión) against six tokenizers (tiktoken's cl100k\_base and o200k\_base; Hugging Face mirrors of Llama-3, Qwen-2.5, Mistral-7B; GPT-2 for historical comparison). Drafted 2026-05-13, published as a standalone note 2026-05-16.},
  keywords     = {lengua, babel}
}

@misc{babel_schema_audit_2026,
  title        = {Per-Artifact Audit Table --- 51 Artifacts Across the (9+1) Axes},
  author       = {Rodriguez, Ramon},
  year         = {2026},
  howpublished = {{RCI} research note, www.roderickc.com},
  url          = {https://www.roderickc.com/babel/research-notes/per-artifact-audit-table},
  note         = {Companion to ``The Nine Design Axes --- Verified, and a Tenth (Enforcement Locus)'' (\url{https://www.roderickc.com/babel/research-notes/design-axes-verified-and-tenth}). Together these comprise the audit data that surfaced the E1--E10 schema extensions referenced in Babel methodology paper §4 and Installment 07 §6. Drafted 2026-05-17.},
  keywords     = {lengua, babel}
}
```

The third entry (`empirical_e4_e7_e9_2026`) is the harder case. Three
options, in order of effort:

1. **Collapse into `design_axes_verified_2026`** (add new bib entry
   pointing at `design-axes-verified-and-tenth.md`; update the four
   citations in 04 to use the new key; retire `empirical_e4_e7_e9_2026`
   from the bib). Cleanest reader experience because every citation
   resolves to a public artifact. ~10 lines of edits.
2. **Re-point at `babel_schema_audit_2026`** (merge: the four citations
   become a second `[@babel_schema_audit_2026]` and the bib has one
   entry covering both). Reasonable because the audit pass that produced
   E1–E10 is structurally the same activity as the data-gathering pass
   that produced E4/E7/E9 findings. Slight loss of precision in the
   citation grain.
3. **Keep as `@unpublished` with an explicit "summarised in" note**
   pointing at `design-axes-verified-and-tenth.md`. Honest but leaves a
   dangling entry forever; the bib never closes the loop.

Option 1 is the cleanest. Option 2 is the lowest-effort. Option 3 is
defensible only if the underlying data-gathering pass might still be
written up separately.

## Independent of the bib decision

The Babel repo's `research-notes/` directory currently contains only
two files (the lit-pass and the interpreter-candidates note). The
substantive research notes referenced from 04 and 07 live in
`www.roderickc.com/src/data/babel/research-notes/`. The
source-of-truth for Babel's working notes is therefore split across
two repos.

That is a separate cleanup with its own trade-offs:

- *Move/copy the notes into the Babel repo.* Restores
  source-of-truth in this repo; means the website pulls from here when
  re-rendering (today the website is the authoritative home).
- *Symlink or document the split.* Lowest-effort; preserves the
  current "website is publish-target, Babel repo is paper-source"
  arrangement but adds explicit documentation so future readers know
  where to look.
- *Leave as is.* Acceptable if the website is the canonical home for
  research notes and the Babel repo's role is paper-source only. Worth
  noting in `plans/00-README.md`.

No recommendation is offered here; this is a workflow decision for the
author rather than a citation-hygiene decision.
