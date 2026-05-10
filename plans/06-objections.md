# 06 — Frequently anticipated objections

> *Draft 1, 2026-05-09. Living document. The objections below are anticipations, not reactions to real feedback yet received. As the series publishes installments, this document will be updated with the friction that actually arrives, which may differ from what is anticipated here.*

## What this document is

The Babel / Inflexión series targets a deliberately broad audience — what `01-motivation.md`'s "Direction" section calls *curious minds*, with several distinct natural constituencies: the esolang community, programming-language researchers, computational linguists, generative-AI practitioners, Spanish-speaking developers, and computer-science educators. Each will pick at the project from a different angle, and each will be right that the project does not address every concern they bring.

This document captures the friction we anticipate, with the current best replies. It is not a defensive performance. It is an honest preparation: writing down where we expect pushback forces us to notice whether we have a real defense or whether the pushback names something we should fix before publication. Where we don't have a satisfying answer, that itself is recorded.

The document will evolve. As real readers arrive, real friction will replace anticipated friction; this doc will track the difference.

## Ground truth, before the rest

**"Are these objections real?"**

No. We made them up. They are anticipations of pushback we expect from each named constituency, not transcripts of feedback any reader has actually given. As real reviewers respond to the published installments, real friction will replace anticipated friction here, and the difference between what we expected and what we got will itself be informative. Until that happens, this document is the author talking to himself in five or six voices, in honest preparation for the friction publication will eventually surface. The exercise is worth doing for its own sake — writing down imagined pushback forces us to notice whether we have a real defense — but no reader should mistake the entries below for a record of received feedback.

## From the esolang community

**"Why this when about eight hundred Brainfuck derivatives already exist? Is Babel adding to the noise or actually doing something new?"**

Babel does not add a new esoteric language — it adds the *methodology* that the field has carried implicitly for thirty years. The corpus has the variation axes; nobody we know of has consolidated them into a parameter schema or built a runtime that turns parameter sheets into working artifacts. The field's roughly eight hundred Brainfuck derivatives are the loudest evidence that no template tool exists. Babel is a lever on the next eight hundred attempts, not on the existing eight hundred. If the contribution lands, the same field effort produces more *new* work and less *repeated* work. If it doesn't, Babel is one more entry in a corpus that already contains plenty. The project is an experiment in whether the field's tacit consensus can be made explicit and operable.

**"Is Inflexión just another vocabulary skin in Spanish?"**

Inflexión engages Spanish *grammar*, not Spanish vocabulary, as the source of programming semantics. Mierda, La Weá, and Chespirito are vocabulary skins on Brainfuck — the execution model is unchanged; the surface tokens are renamed. Inflexión maps Spanish mood to evaluation strategy, aspect to eager / lazy, *ser* / *estar* to immutable / mutable bindings, clitic ordering to argument routing, and number agreement to the scalar / collection distinction. These are structural design moves, not theming.

The genre Inflexión joins is small but not empty: Perligata (Latin, 2000), Wenyan (Classical Chinese, 2019), Tampio (Finnish, ~2017–present), and the unimplemented Espro (Esperanto, 2015) are all inflection-driven non-English natural-language esolangs. Inflexión joins this lineage rather than opens it. What's distinctive about Inflexión within the lineage is the language family (Romance, not Italic, Sino-Tibetan, Uralic, or constructed) and the specific feature set (the *ser* / *estar* split + mood + aspect + clitic ordering + diminutive morphology) — none of the four prior precedents engages this combination. The difference between a vocabulary skin and a grammatical engagement is the difference between a costume and a body; Inflexión is a body, in a Romance shape, joining four other bodies in different shapes.

## From programming-language researchers

**"Where's the formal semantics? Where's the novel theoretical contribution?"**

The first installment is deliberately a design paper, not a semantics paper. Operational semantics is the planned subject of the second Inflexión installment, where the abstract machine, evaluation order, and Turing-completeness argument will be made rigorous. The novel contribution this first installment claims is at the design level: a parameter schema for esoteric-language construction (Babel) and a working set of grammatical-feature-to-programming-semantic mappings for a living non-English natural language (Inflexión). Whether either is *theoretically* novel in the strong PLT sense — closed under composition, exhibiting some new categorical structure — is a question the operational-semantics installment will engage. The first installment makes more modest claims and is honest about the modesty.

## From computational linguists

**"You're not a linguist. Are your morphological mappings grounded? Why Rioplatense specifically?"**

The author is not a trained linguist; this is acknowledged in the front matter and in the project's authorship note. The mappings draw on standard reference grammars — Butt and Benjamin's *A New Reference Grammar of Modern Spanish*, the Real Academia's *Nueva gramática de la lengua española* — and on the author's native fluency in Rioplatense Spanish. They are not novel linguistic claims about Spanish; every grammatical feature mapped is well-documented in the standard literature. The novelty is in *what the mappings are used for* (programming semantics), not in *what the mappings observe* (Spanish grammar). The dialect choice is justified in §2 of the Inflexión paper: native authorship, *voseo* as a structural marker not competing with peninsular norms, the cultural anchor of Argentine linguistic ecology, and the precedent of La Weá's Chilean specificity. The series welcomes collaborators whose native dialect differs.

## From generative-AI practitioners

**"BPE tokenization weakens your hypothesis. Where's the empirical data?"**

The BPE tokenization concern is acknowledged explicitly in §5 of the Inflexión paper, with two paragraphs added in revision specifically to engage it. The hypothesis is restated at the prompt level rather than at the per-token level: a prompt written in Inflexión, even after BPE-tokenization, packs more grammatical information into its overall length than the English-keyworded equivalent. Whether this prompt-level density translates to better downstream generation is exactly the question the deferred empirical study is designed to answer. The empirical study itself is named as a future installment, with the prerequisites — a working runtime, a sufficient program corpus to draw test cases from — named honestly. The first installment commits to the hypothesis and to the methodology for testing it; it does not commit to the result.

## From Spanish-speaking developers

**"Why would I program in this when I already use Python? Isn't this performative cultural specificity?"**

Inflexión is not addressing access. Spanish-speaking developers already program comfortably in mainstream languages, and Inflexión is not a localisation. It is an esoteric language that explores what programming becomes when grammatical inflection carries semantic load. A Spanish-speaking developer who already uses Python gains nothing from Inflexión unless they are specifically interested in the design-space question — what programming primitives fall out of Spanish grammar — that the language is exploring. The project is explicit about this in the §"What this is not" section of the Inflexión paper. The cultural specificity is not performative because the language is not *for* a Spanish-speaking audience as a tool; it is *about* what a programming language built on Spanish grammar can be.

## From CS educators

**"Is this teachable? Is the setup cost worth the lesson?"**

Yes, with deliberate framing. Inflexión is a teachable artifact for any course on programming-language design, comparative grammar, or the cultural anchoring of computing systems. A two-hour lecture can walk the six mappings and have students implement a small program. The mappings are deliberately understandable by analogy to features the student already knows: *ser* / *estar* mirrors `const` / `let`; perfective / imperfective mirrors eager / lazy; subjunctive mirrors deferred or reactive evaluation. The setup cost is real but bounded. The student needs no prior Spanish to follow the structural logic, though native Spanish speakers will read the worked examples more fluently. Babel is itself a teaching artifact: walking its parameter schema is a way of seeing what programming-language design choices look like across a corpus, made legible.

## Open

Anticipated objections we do not yet have satisfying replies to:

**"Why this and not nothing? You said yourself it doesn't solve a problem."** The current reply, in `03-position.md`, is the section *"Why 'no problem' is not 'no value'."* Whether that section convinces a reader who came in skeptical is genuinely unknown. The project's stance is that the reader is welcome to disagree; the project is not for them.

**"This is RCI work, not academic. Where is the peer review?"** The series publishes through RCI rather than through traditional academic peer review. The project welcomes academic collaborators and would happily go through peer review at a venue that fits the work. The absence of peer review in the first installment is a feature of the chosen publication path, not a deliberate avoidance, and not a position on whether peer review is desirable.

**"You wrote both the methodology paper and the language that the methodology should generate. Isn't that circular?"** Yes, and acknowledged in §7 of the Babel paper, which explains why Inflexión is hand-built rather than Babel-generated. The future installment that asks whether Babel can express Inflexión will close the loop honestly. Until then, the circularity is real and worth naming.

---

*Last updated 2026-05-09. Additions and anticipated-objection contributions welcome through RCI publication channels.*
