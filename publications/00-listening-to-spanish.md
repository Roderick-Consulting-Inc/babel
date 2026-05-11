# Listening to Spanish Again

> *First article in an RCI LinkedIn series on the impact of language in technology. Predecessor to the formal Babel and Inflexión installments. First-person voice, deliberately — the formal papers are written in third-person essayistic register; this series is written in the *I* of someone who experienced something.*

A customer was talking, in Spanish, about using Microsoft Mesh to build their data pipelines. I heard *Mesh* the way you hear a foreign technical term you've slowly become familiar with — and at the same time, half-translated in the back of my head, I heard *malla* (what Spanish would call a mesh) and *velo* (a veil — which a mesh kind of *is*, a covering you can see through). What they were covering, with all this careful technical vocabulary, was a *quilombo*.

*Quilombo* is a Rioplatense word. Its roots are in the Bantu languages of enslaved West Africans brought to colonial Brazil — a *quilombo* was a settlement of escaped slaves, the most famous being the Quilombo dos Palmares. The word migrated through the centuries into Argentine and Uruguayan slang, where it now means a chaotic mess, a complete disaster. The customer, of course, didn't say *quilombo*. They said *Microsoft Mesh*. But what was being covered, by the technical mesh-as-veil, was unambiguously a *quilombo*. The Spanish word would have named the underlying state of the data architecture more precisely than any phrase in the entire technical conversation. And nobody said it.

## The position from which I'm hearing this

I should not have noticed any of this. I grew up speaking Venezuelan Spanish — first language, household language, the language I dreamed in until I was twenty-something. Then twenty years of mostly-English professional life happened, and Spanish quietly receded. Not catastrophically, the way a forgotten skill recedes; more like a room you stopped going into. The furniture was still there.

A few years ago I came back to live not in my native Venezuela but in Argentina. The Spanish I was returning to was *not the Spanish I had grown up with*. It was Rioplatense — Argentine Spanish, with *vos* instead of *tú*, with the Italian-inflected intonation of Buenos Aires, with *lunfardo* lexicon I'd never heard, with the cultural texture of a country I knew abstractly but didn't *speak from*. I was recovering and adopting, at the same time. *Relearning my native language as a different language.*

This double move turns out to be the position from which conscious noticing becomes possible. A Venezuelan who never left wouldn't notice *quilombo*'s historical weight; they'd just use the word. An English-speaker learning Spanish from scratch would notice it but as foreign vocabulary. I'm in the middle, where the morphology is half-recognised and half-new. The textbook is invisible; the patterns are not.

## What I keep noticing

What you start to notice, in this position, is that words *do not stop carrying meaning at the edge of their dictionary definition*. *Quilombo* doesn't mean *mess* the way *mess* means *mess* in English. It carries the colonial Brazilian settlement, the forced migration of its etymology, the Rioplatense slang transformation, the moment the customer didn't say it. All of that is in the word when a native speaker uses it, even if the speaker can't articulate what's there.

A few more examples from what I've been re-learning:

*Garpar* is the *vesre* — the syllable-reversal — of *pagar*, *to pay*. A Buenos Aires word-game culture flips syllables to make new words: *café* becomes *feca*, *tango* becomes *gotán*, *pagar* becomes *garpar*. *Garpar la nube* — to pay the cloud bill — has a register English's *spend* and *pay* don't have. The word carries the practice of vesre itself, the act of being from somewhere where you do this with words.

*Posta* started as a stagecoach relay station — the place information arrived in the colonial-era postal system. Through the centuries, the word *sublimated* from infrastructure to abstraction. *¿posta?* doesn't ask for a place; it asks for the truth. *Es posta* — it's a fact. The word's modern meaning is what was once carried *by* postas: information, certainty, news.

And then — this is the balance the observation needs — there are English words that do something Spanish equivalents can't. *Pipeline* is *graphic*. The word *shows* you industrial infrastructure, fluid moving through connected segments. The Spanish translations (*tubería*, *canalización*, *conducto*) all sand off the visual punch. *Underscore* names a typographic mark by its position relative to the line; the Spanish *piso* — literally *floor* — flattens it into a positional metaphor that loses the descriptive specificity. The information loss runs in *both* directions. Neither language is richer in the abstract; both have *zones of accreted or graphical meaning the other cannot translate cleanly*.

## The thought that came next

It was around this point that I thought, *perhaps this could be leveraged in systems.*

Programming languages are systems for talking about computation. The vocabulary they use — keywords, identifiers, syntactic markers — is overwhelmingly English-derived, and aggressively *strips* the kind of accretion I'd been noticing. *Cookie* in software has lost the bakery; *daemon* has lost the Greek; *pipeline* has, in technical use, mostly lost the industrial weight even in English. The strip-down is a feature, in some ways — code shouldn't depend on a reader knowing the etymology of *fork* — but it also closes off a zone of meaning that natural language is constantly using.

What if a programming language were deliberately built around a substrate language whose grammar and vocabulary *carried* the kind of accreted meaning English-technical-vocabulary refuses? Not just translated keywords — the *grammatical structure itself* doing semantic work. A language where *ser* and *estar* — Spanish's two copulas, distinguishing essential from transient — corresponded to immutable and mutable bindings, because the natural-language distinction was already in the speaker's head. A language where the subjunctive mood — Spanish's marker for hypothetical or deferred reality — corresponded to lazy or conditional evaluation. A language where the diminutive *-ito* did real numeric work, because the cultural register of *cinquito* — *a small five* — was already half-doing it.

## The work this hypothesis became

That hypothesis is now a research project. Two of them, actually.

The first, **Babel**, is a methodology for building esoteric programming languages programmatically: a parameter schema for the variation axes the field has implicitly used for thirty years, and a runtime that turns parameter sheets into working artifacts (interpreter, transpiler, specification page). The second, **Inflexión**, is a hand-built Spanish-grammar esoteric language that makes the *ser* / *estar*, mood-as-evaluation, aspect-as-eager-or-lazy, clitic-as-argument-routing, diminutive-as-scaling moves I just sketched into actual programming-language semantics.

There is prior art in this lane. *Lingua::Romana::Perligata* did it for Latin in 2000 (Damian Conway). *Wenyan-lang* did it for Classical Chinese in 2019 (Lingdong Huang). *Tampio* has been doing it for Finnish since around 2017 (Iiro Sarkkinen). The lane is not empty; Inflexión is the first to take a *living Romance language* and make this specific feature set load-bearing. I've also done one prior, less formal version of the move in *El Pueblo* — the Rioplatense word *posta* is the chosen technical name for a sensor-relay node in an RCI architecture. The natural-language version of the observation predated the formal computational version by some time.

This article is the first in a series. The next ones will go deeper into specific design moves, into what the empirical large-language-model question looks like, into the mechanics of building a programming language whose syntax is Rioplatense Spanish without being a parody. The formal papers (which the series will eventually point at) carry the technical detail; these articles carry the *why*.

---

The customer was talking about Microsoft Mesh. I was hearing *quilombo*. There is a programming language sitting in the gap between those two perceptions, and this series is about why it is worth building.
