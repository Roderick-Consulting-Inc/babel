# 03 — Position

> *Draft 1, 2026-05-08. Author: Roderick C with Claude as scribe. This document takes the precedents and absences identified in `02-inspiration.md` and uses them to state the project's actual position. It is the document `04` and `05` will refer back to whenever a value claim is in question.*

## What this document does

`01-motivation.md` says why the project is being undertaken. `02-inspiration.md` says what is already in the world. This document does the in-between work: it states what the project is *for*, given its motivation and given what the field already contains. It is the answer to the question a sympathetic reader will ask after the first two documents — *and so what?* — and to the related question a less sympathetic reader will ask: *who needs this?*

The answer has to be honest about the project's posture. Babel and Inflexión are not solving a problem. The project does not improve a metric, close a market gap, restore a broken system, or rectify an injustice. To pretend otherwise would damage the project before the first line of its design is written. What the project does instead is harder to name in a single phrase, and worth being precise about.

## The non-problem-fix posture

The project does not solve a problem in the sense that an outage is solved or a bug is fixed. Stating this plainly is not a humility move and not a hedge. It is a posture that shapes everything the project does. The posture rules out feature-creep driven by the urgency of a real failure. It rules out customer-led scope. It rules out the temptation to overclaim what the project's contributions are in order to justify the work to an imagined sceptic. It rules *in* slow work, careful framing, an honest accounting of what the contributions actually are, and the freedom to take an evolutive, recurring publication path rather than a sprint to a definitive release.

The risk of stating this is being read as saying the project is therefore optional, hobbyist, or unimportant. The next two sections answer that.

## What "we are doing" actually is

In the absence of a problem-fix, a project still has a choice of what to do. Three contributions, named cleanly:

**Generalization of esoteric-language construction.** This is Babel's contribution. The esoteric-language field has produced something on the order of 1,500 named languages and roughly 800 Brainfuck derivatives alone, hand-rolled by individual authors who repeated, each time, the same restructuring work. The field has produced a corpus but not a methodology. Babel is the methodology — a parameter schema for the variation axes the field has already mapped, plus a runtime that turns chosen parameters into a working language with an interpreter, a transpiler, and a specification page. The contribution is not a new esolang. It is *a technique for making esolangs* that the field has lacked for thirty years.

**A serious engagement of non-English grammar as programming semantics, in the lineage of Perligata, Wenyan, and Tampio.** This is Inflexión's contribution. The natural-language-themed esolang corpus is overwhelmingly English in its cultural references, and where it engages non-English material it does so most often through vocabulary substitution. Mierda, La Weá, and Chespirito are useful precedents for vocabulary engagement. A small lineage of four esolangs engages non-English grammar as semantic substrate rather than as theme: Perligata (Latin, 2000) uses Latin declension to determine variable type; Wenyan (Classical Chinese, 2019) uses literary particles as syntactic markers; Tampio (Finnish, ~2017–present) uses eight Finnish noun cases and verb conjugation as semantic structure; and Espro (Esperanto, 2015) sketches an analogous design without implementing it. Inflexión targets a different language family from any of the four — Romance — in a deliberately chosen dialect (Rioplatense Argentine), and uses a feature set the prior precedents have not engaged: the *ser* / *estar* copular split, the indicative / subjunctive / imperative mood three-way, the perfective / imperfective aspect contrast, the fixed-order Spanish clitic system, productive diminutive / augmentative morphology, and number agreement as scalar / collection discipline. The contribution is a *new entry* in an established small lineage, not the opening of an empty lane.

**A treatment of the role of culture and language in computing technology.** This is the joint contribution, ongoing across both artifacts and across the planned series of installments. The precedents from `02-inspiration.md` — Kidder, the mushroom theory of information, the rings-of-security architecture, El Pueblo's lexicon-as-design-discipline — collectively establish that programming languages are political artefacts, that vocabulary does real cognitive work, and that information asymmetry and trust boundaries are *parameters* of system design rather than incidental features of it. Babel and Inflexión are an attempt to engage that body of thinking from an underexamined angle: *which natural-language and cultural substrate the programming language is built on*. Most engagements of computing as a cultural artefact ask about the people who use it. This project asks about the language out of which the language is built.

## Three things the project is not

Three common misreadings worth heading off, before they cling to the white papers.

**It is not a commercial product.** There is no customer, no market, no revenue model. If a commercial use emerges later — Babel as an educational tool, perhaps; Inflexión as an LLM-prompting substrate, perhaps — that is a separate decision made under separate constraints, and not the lens through which the current work should be evaluated.

**It is not a problem-fix in the conventional sense.** It does not address a failure, a deficit, an injustice, or an inefficiency. The "absences" in `02`'s field survey are not problems in the world; they are unmapped corners of a design space, which is a different thing. A field can have unmapped corners indefinitely without anyone being harmed. The work of mapping them is worth doing because the map is intrinsically useful, not because the absence of the map is causing a measurable harm.

**It is not a manifesto against English-keyworded programming.** English keywords are not the target. Spanish keywords would not be a substantive improvement. The interesting target is grammatical *structure*, not the choice of vocabulary, and the interesting question is what becomes *possible* in a different grammatical substrate, not what is *wrong* with the existing one. Pre-empting this misreading matters because a manifesto framing would shift the project's centre of gravity from design-space exploration to identity politics — a different and less interesting project, and one that has been done from many adjacent angles already.

## Why "no problem" is not "no value"

Three reasons the project is worth making despite — and partly because of — the explicit non-problem-fix posture.

The first is economic, in the field-effort sense rather than the monetary sense. The roughly eight hundred Brainfuck derivatives in the wiki's category are evidence of a field stuck in a phase where each author repeats the same restructuring work. If Babel reduces the marginal cost of producing a new esolang by an order of magnitude — and the variation axes are simple enough that this is plausible — then the same field effort produces more *new* work and less *repeated* work. The lever is on the next eight hundred attempts, not on the existing eight hundred. This is the same kind of contribution as a good library or a good notation: the field gets faster at thinking the thoughts the tool makes easy, and the next generation of contributors does not have to re-pay the entry tax that the previous generation paid.

The second is intellectual. The lane Inflexión occupies — non-English living-language grammar as programming semantics — is empty not because it has been tried and rejected. It is empty because the path to it crosses two disciplines that few authors have stood in simultaneously, and that one of them (linguistics) does not customarily produce programming languages. To stand at the intersection and produce a working language is itself the contribution; the language does not need to be widely adopted, technically superior, or commercially viable to be a contribution. It needs to be coherent, defensible, and readable. Wenyan, by occupying the analogous lane for Classical Chinese, demonstrated that this kind of contribution can attract attention and make a real intellectual mark without ever becoming a tool that people use to do their day jobs.

The third is contemporary, and it is the LLM-prompting-density hypothesis from `02-inspiration.md`. If the hypothesis bears out — that a programming language whose surface syntax mirrors a more grammatically dense natural language is a denser substrate for LLM prompting than English-keyworded equivalents — then the project's contribution doubles. If it does not bear out, the project's other contributions still hold. The hypothesis is upside, not foundation. `05` will state it as a hypothesis and defend the language design on its other merits, so that the language stands or falls on those.

## What would count as success

Three things that would count as success across the first few installments, taken conservatively.

Babel makes generating a new esolang dramatically faster than hand-rolling one, and the parameter schema it exposes makes the field's variation axes legible to a reader who is not already an esolang author. Inflexión exists as a coherent, working language — with a real interpreter, a small but readable program corpus, and a specification document that can be read straight through. The white papers find an audience among the curious minds identified in `01-motivation.md`'s "Direction" section, and at least some of that audience reads the second installment because they read the first.

Three things that would *not* count as success, equally important to name.

Mass adoption of either artifact would be welcome but is not the bar; if Babel ends up with five active users and Inflexión with one (the author), that is consistent with the project's intent. Empirical proof of the LLM-prompting-density hypothesis is *not* a success criterion for `04` or `05`; that is the work of a separate empirical paper, written when there is something to test. Any specific commercial outcome — a tool used by a paying customer, an academic licensing arrangement, a textbook adoption — is welcome but separate, and `04` and `05` should not be tuned to produce one.

## How `04` and `05` develop this

`04-whitepaper-babel.md` will argue the methodology contribution. It will state Babel's parameter schema, the variation axes it exposes, and the academic and educational value derived from making those axes legible. It will be a methodology paper in essayistic voice, with examples drawn from the existing esolang corpus and forward-pointing to Inflexión as one possible — though hand-built rather than generated — instantiation.

`05-whitepaper-Inflexión.md` will argue the language contribution. It will state the grammatical-semantic mappings that Inflexión uses (number, mood, aspect, ser/estar, clitics, diminutives), the dialect choice (to be made), the surface syntax, a small set of worked examples, and the LLM-prompting-density hypothesis stated as such. It will defend the language on its design merits independently of whether the hypothesis is later validated.

Both papers are installments, not finalities. Each is meant to read as a credible snapshot of where the project is, with explicit hooks for what the next installment can build on. The series is the unit of work; any single paper is a chapter, not a book.

## Open items

- `[TBD]` — Whether `04` should include a worked example of generating a small toy esolang via Babel, or save that for a later installment. Argument for: makes the methodology concrete. Argument against: requires Babel to exist in working form, which adds scope to the first paper.
- `[TBD]` — Whether `05` should describe Inflexión's execution model in full, or save the operational-semantics half for a later installment. Argument for: completeness. Argument against: a single paper that does *both* the linguistic mapping and the operational semantics may be too long for the curious-minds audience.
- `[TBD verify]` — Whether the field-effort argument in §*Why "no problem" is not "no value"* can be tightened with a real estimate of the marginal cost of producing a new BF derivative versus a generated one. The order-of-magnitude claim is plausible but currently unsupported.
- *Resolved 2026-05-09* — A standalone `06-objections.md` was drafted instead of an appendix here, capturing pushback we anticipate from each named constituency (esolang community, PL researchers, computational linguists, generative-AI practitioners, Spanish-speaking developers, CS educators) plus a small *Open* section listing objections we don't yet have satisfying replies to. Treated as a living document; will be expanded as real reviewer feedback arrives.
