# I Thought I Was the First. I Was the Fifth.

> *Draft 1, 2026-05-10. Third article in an RCI LinkedIn series on the impact of language in technology. Builds on [Listening to Spanish Again](00-listening-to-spanish.md) and [What Technical Vocabulary Refuses to Carry](01-what-technical-vocabulary-refuses-to-carry.md). First-person voice. Story-form, not a technical deep-dive.*

The two previous articles were the *why* and the *general claim*. This one is the *embarrassment* — and the methodological move that turned out to be more interesting than the embarrassment.

When I started working on Inflexión — a programming language whose semantics flow from the grammatical features of Rioplatense Spanish — I was confident about the novelty claim. *No esoteric programming language exists*, the early draft of the formal paper said, *that uses the grammar of a living non-English language as the source of programming semantics.* I knew about Wenyan — the Classical-Chinese-grammar language Lingdong Huang shipped in 2019 — and I treated it as the closest precedent. Wenyan engages a literary register; Inflexión engages a living one. *Inflexión opens an empty lane.*

I was wrong. Not by a little — by **four other published esolangs** I had not heard of, three of them implemented, two of them in living languages.

## The verification

Before publishing the formal paper, I ran a literature check. Not because I doubted the claim — because the project's documented stance is *honest preparation*: write down where you expect pushback, look for it, fix what you find before review rather than after. The verification was supposed to be a confirmation pass. It was not.

Here is what I found, in chronological order.

## Perligata, 2000

**Damian Conway**, the Perl polymath who has written more clever code in more registers than most language designers manage in a lifetime, published *Lingua::Romana::Perligata* in 2000 — a Perl module that lets you write Perl in Latin. Not Latin keywords; Latin **grammar**. In Perligata, declension determines variable type: a scalar is a neuter-singular second-declension noun; an array is its plural; a hash is a masculine-plural fourth-declension noun. Verb conjugation determines call context. Word order is free, exactly because the inflectional system carries the syntactic information that English word order would have to carry. It is on CPAN. It works. It predates Wenyan by **nineteen years**.

I had not heard of Perligata. The canonical inflection-as-semantics precedent for the project I was claiming to open had been quietly sitting on CPAN for a quarter century. The fact that Conway is also a widely-read author of *Perl Best Practices* makes the miss more embarrassing, not less.

## Espro, 2015

**An esolangs.org wiki contributor known as "Timwi"** posted an idea page in 2015 for *Espro*, an Esperanto-grammar esoteric language. The accusative *-on* would mark fields. The accusative-adjective *-an* would mark types. Infinitive *-i* would mark methods. The marker *-ar-* would denote arrays. The page sketches the design but no implementation followed. Esperanto is constructed, not natural; idea-only, not implemented. But the design move was named in 2015 — *use Esperanto's productive morphology as a programming-language surface* — and there it was on a public wiki, eleven years before I started thinking I was the first to consider this kind of move.

## Tampio, ~2017

**Iiro Sarkkinen**, posting as *fergusq*, has been developing **Tampio** since around 2017. Tampio uses Finnish — a *living* agglutinative language with eight noun cases, verb conjugation across active and passive voice, imperatives and participles, more than twenty-five postpositions, plural inflection, agreement. It uses the libvoikko Finnish morphological analyzer to do the parsing. The Tampio compiler is small, well-engineered, and hobbyist-grade in the best sense — a single author, a clear design, a working artifact, an esolangs.org wiki entry, an active GitHub repository.

Tampio is the precedent that should embarrass me most. *Living non-English natural language, grammar-as-semantics, single hobbyist author, esolangs.org-cataloged* — Tampio is the precedent that does *exactly* what Inflexión proposes to do, except for Finnish instead of Spanish. The "first esolang to use a living non-English natural-language grammar" claim collapses on contact with Tampio.

## Wenyan, December 2019

**Lingdong Huang**, then a CMU senior, built *Wenyan-lang* during finals week in December 2019. It uses Classical Chinese particles (者, 也, 而) in their literary positions as syntactic structure, with a real parser handling real grammatical constructions. It compiles to JavaScript, Python, and Ruby. It went viral on its release. *IEEE Spectrum* covered it. Guinness World Records gave it an entry. The project has been quiet since 2023, but the codebase is intact and the design is studied by anyone who works in this corner of programming-language design.

This was the one I knew about. The other three I did not.

## What the discovery actually means

The honest reframe: Inflexión is not the first inflection-driven natural-language esoteric programming language. It is **the fifth in a small lineage** — Perligata (Latin, 2000), Espro (Esperanto, 2015, idea-only), Tampio (Finnish, ~2017–present), Wenyan (Classical Chinese, 2019), Inflexión (Rioplatense Spanish, 2026). The lineage is small but real. Each member engages a different language family — Italic, constructed, Uralic, Sino-Tibetan, Romance. None engages the specific feature set Inflexión makes load-bearing: the *ser* / *estar* copular split, the indicative-subjunctive-imperative mood three-way, the perfective-imperfective aspect contrast, Spanish clitic ordering, productive diminutive and augmentative morphology. Inflexión's contribution is now, more carefully, *the first Romance-language entry, and the first to engage that specific Spanish feature set jointly*.

This is a more defensible claim than the one I started with. It is also a more interesting one. The original claim — *first ever* — would have been embarrassing under any careful reading and would have collapsed at the first review. The corrected claim — *fifth in a small lineage, distinctive in these specific ways* — is precise enough to defend, modest enough to be believed, and generous enough to credit the four authors who arrived first.

## The piece worth taking forward

Honest preparation works. Writing down the novelty claim and looking for the precedents that would falsify it surfaced four authors who deserved credit, gave the formal paper a more accurate framing, and turned what would have been a post-publication embarrassment into a pre-publication clarification. The piece worth taking forward is not the embarrassment; it is the practice.

The formal paper now opens a section on the lineage rather than a section claiming to open an empty lane. The acknowledgements thank Damian Conway, Lingdong Huang, and Iiro Sarkkinen by name, alongside the existing thanks to the esolangs.org maintainers. Inflexión joins a genre rather than starts one — and a genre with company is a more interesting place to be than a lane with one occupant.

---

*Inflexión is the fifth inflection-driven non-English natural-language esoteric programming language I have been able to find. If you know of a sixth — particularly one in a living language I have missed — I would like to hear about it. The series is the long way of finding out what else is in this corner of the design space.*
