# 01 — Motivation

> *Draft 1, 2026-05-08. Author: Roderick C with Claude as scribe. Review and revise — this is a first pass, not a final position.*

## What this project is

Two artifacts and one thesis.

The artifacts are **Babel**, a programmatic generator of esoteric programming languages, and **Inflexión**, a hand-crafted Spanish-grammar-based esoteric language. The thesis is that the construction of programming languages — including the deliberately strange ones — can be made *systematic* without becoming generic, and that natural human languages other than English carry grammatical structure that programming has barely touched.

This is not a problem-solving project in the conventional sense. We are not fixing an outage, closing a market gap, or shipping a feature a customer asked for. We are doing what esolangs have always done — exploring what programming *could* look like — but with two deliberate constraints that, taken together, are not represented in the prior art:

1. **Programmatic generation.** Most esolangs are one-off creations. The ~800 Brainfuck derivatives on esolangs.org are the obvious tell: when no template tool exists, every author hand-rolls the same restructuring. Babel is the template tool that should already exist.
2. **Cultural and grammatical specificity outside English.** Most natural-language-themed esolangs are English vocabulary skins (LOLCODE, ArnoldC, Rockstar). A few use English *grammar* in earnest (Inform 7, Rockstar's poetic literals). Almost none use the *grammar* of any other language. Spanish — and the wider Romance family — has structural features (mood, aspect, clitic ordering, ser/estar, number agreement) that English lacks or has weaker forms of. Those features can carry programming semantics. Inflexión is the demonstration.

## Why esolangs at all

Esolangs sit at the intersection of art, pedagogy, and theory. They make the implicit assumptions of mainstream languages visible by violating them. They let students build a working interpreter in a weekend because the surface area is small. They give researchers a sandbox for ideas — concatenative evaluation, fungeoid 2D flow, deliberate self-modification — that would never survive contact with a production language.

What esolangs have *not* done well is consolidate. The wiki is a museum of singletons. There is no widely-used kit for generating new ones, no canonical taxonomy of variation axes, and no agreed vocabulary for talking about what differs between, say, a Brainfuck derivative and a fungeoid. Babel is an attempt to make the field *systematic* — not to replace creativity with a checklist, but to give the next 800 derivatives a shared scaffold.

## Why Spanish, why grammar

Programming has been overwhelmingly Anglophone since FORTRAN. The keywords are English. The error messages are English. The cultural metaphors — `kill`, `daemon`, `parent`, `child`, `master` — come from a specific Anglo-American computing history. Even esolangs that explicitly play with natural language stay within English: cooking instructions, song lyrics, action-movie quotes.

Spanish offers more grammatical density per word than English. A single conjugated verb (`comió`) encodes the action, third-person singular subject, completed (perfective) past tense — three pieces of information English needs three or more words to express (`he/she ate`, with completion only inferable from context). Spanish has two copulas (`ser` for essential properties, `estar` for transient state) where English has one (`be`). Spanish verb mood distinguishes asserted reality (indicative) from hypothetical, desired, or doubted reality (subjunctive) — a distinction English speakers make through verb-helpers and tone, not morphology. Clitic pronoun ordering (`me te se lo le` in fixed sequence) is a fully grammaticalised argument-shuffling system. Number agreement runs through articles, nouns, adjectives, and verbs in lockstep, making the singular-versus-plural distinction structurally enforced rather than merely marked.

These features map onto programming concepts that already exist:

- **Number** (singular vs. plural, with strict agreement through article, noun, adjective, and verb) ↔ scalar vs. collection.
- **Ser vs. estar** ↔ static vs. dynamic / pure vs. effectful.
- **Subjunctive vs. indicative** ↔ deferred / conditional vs. immediate / unconditional evaluation.
- **Perfective vs. imperfective aspect** ↔ eager vs. lazy, completed call vs. ongoing process.
- **Clitic ordering** ↔ argument permutation combinators.
- **Diminutive / augmentative morphology** (`-ito`, `-azo`) ↔ numeric scaling, precision modifiers.

None of these mappings are obviously correct. Whether they make for a *good* programming language is the design question `05` will work through. The motivation here is only that the mappings *exist*, that they are *non-trivial*, and that no existing esolang uses any of them. The lane is empty, and not because it is uninteresting.

## The generative-AI angle

A large language model reading source code is doing the same kind of pattern recognition it does on natural language. Code in a more grammatically dense language gives the model more signal per token. A function name in `Inflexión` that already encodes its argument number, its mood (asserted or hypothetical), and its aspect (one-shot or ongoing) is — by construction — less ambiguous than its English equivalent.

The hypothesis we want `05` to defend is that **a programming language whose surface syntax mirrors Spanish grammar is a denser substrate for LLM prompting and code generation than English-keyworded languages**. We do not yet know whether this hypothesis survives empirical contact. That is a question for after the language exists.

This motivation is sufficient on its own — the language is interesting independent of whether the LLM angle bears out. The LLM angle is the *secondary* reason to care, and the one most likely to interest readers from outside the esolang community.

## Why these are two artifacts and not one

Babel is a generator. Inflexión is a generated thing — but we are explicitly **not** generating it with Babel. The reason is honesty: we do not know yet which of Inflexión's features will be expressible inside Babel's parameter schema. Building Inflexión first, by hand, gives us a concrete target to retroactively check Babel against. If, when Babel is finished, it cannot reproduce Inflexión, that is a signal about Babel's expressiveness, not a problem with Inflexión. The two artifacts inform each other; they do not depend on each other.

## What this project is not

- It is not a commercial product. There is no customer, no market, no revenue model. If one emerges later, that is a separate decision.
- It is not a problem-fix. We are not naming a bug in the world that this resolves.
- It is not a manifesto against English-keyworded programming. English keywords are fine. Spanish keywords would also be fine. The interesting target is *grammar*, not *vocabulary*, and the interesting question is *what becomes possible* in a different grammatical substrate, not *what is wrong with* the existing one.
- It is not, yet, a research paper. The two white papers (`04` and `05`) aim toward academic value, but the audience-fit and venue selection are deliberately deferred until the substance exists.

## Direction

**Audience.** Curious minds. Not a narrow specialist subset. The white papers should be readable by educated non-specialists from any of the natural constituencies (esolang community, language-design researchers, computational linguists, generative-AI practitioners, Spanish-speaking developers, CS educators) without being tuned to satisfy any one of them. This rules out heavy formal notation, in-group jargon, and venue-specific framing. It rules in a clear, essayistic voice that explains its own terms.

**Authorship.** Ramon Rodriguez under the auspices of RCI. Additional authors welcome and desired — the project is open to collaborators who want to extend the language, the generator, or the surrounding research. Licensing and attribution follow RCI conventions; the white papers are RCI publications.

**Time horizon.** Evolutive and recurring. The intent is to make Babel and Inflexión a *recurring theme* in RCI publications, not a single big release. Some installments will be large; some will be small; the series is always the unit of work. Each installment captures the current state of the research and ships when it is coherent on its own — which means coherent in scope, not necessarily quick to produce. This shapes the white papers' tone: confident about framing and current findings, conservative about claims that depend on empirical validation we have not yet done. A white paper in this series should read as a credible snapshot, not as a final word.

This last point matters for `04` and `05` specifically. If we treat them as one-shot definitive documents, we will overclaim or stall. Treating them as installments lets us state hypotheses honestly ("we believe X; the next installment will test it") and lets the project breathe.
