# What Technical Vocabulary Refuses to Carry

> *Second article in an RCI LinkedIn series on the impact of language in technology. Builds on the predecessor [Listening to Spanish Again](/babel/articles/listening-to-spanish). First-person voice; focused on Babel and Inflexión rather than a sweeping multi-thread research programme.*

The first time I noticed it was in Spanish, talking about Microsoft Mesh covering a *quilombo* — a story I told in the previous article. But once you start hearing it, you start hearing it in English too. Probably in every other natural language a careful speaker pays attention to, though I'm not going to make claims about languages I don't know well.

Technical vocabulary is doing a different job from natural-language vocabulary — *it is not supposed to carry the weight*. That is the whole point. But the weight, when you look for it, is everywhere. And the stripping-down is not free.

## The general claim

Technical vocabulary is a *register*, not a neutral channel. It is a deliberate move toward the lowest-context-possible, the most-translatable, the most-context-free version of a word. *Daemon* in computing is not *daimon* in Hesiod; *cookie* in browsers is not the bakery good; *fork* in version control is neither cutlery nor a road. The word is borrowed, stripped of its origin context, redeployed for technical clarity. This works — code does need precise vocabulary — and it costs.

The cost is that the borrowed word's cultural-historical weight stays *available* but *invisible*. A careful reader can recover the weight, but has to do the work consciously. A reader from a different cultural tradition may have no access to the weight at all, because the borrowing happened from a culture they don't share. The technical register's job, in other words, is to *suppress* the parts of meaning that would otherwise flow into the word from elsewhere.

## What the suppression looks like

Some examples from the two languages I have direct access to — Spanish and English. The premise of this series is that the same phenomenon happens in every language, but I only have direct standing to write about the ones I actually know. Examples from other natural languages would be welcome from anyone who reads this and sees their own language doing the same thing.

**English: buried etymology that stays buried.** *Daemon* arrived from Maxwell's nineteenth-century *demon* — the imaginary being that sorted gas molecules — which arrived from the Greek *daimon*, a helpful guiding spirit (distinct from a *kakodaimon*, an evil one). The technical sense (a background process) kept the spelling but stripped almost everything else. A Greek-speaker reading old computer-science papers about daemons gets a faint flicker of recognition that an English-only reader never sees. *Cookie* lost the bakery; *bug* lost the moth in the relay [^bug]; *fork* lost both the cutlery and the road; *pipeline* — as covered in the predecessor article — lost the industrial water-flow image even in English. The losses are routine and almost always invisible to the speakers.

**Spanish: context the technical vocabulary refused to let through.** The example from the previous article. The customer's data architecture was, accurately, a *quilombo* — a Rioplatense word carrying colonial-Brazilian historical weight and contemporary slang force. The customer said *Microsoft Mesh*. The Spanish word would have named the underlying state of the architecture more precisely than any phrase in the entire technical conversation. And nobody said it.

**Spanish: a single diminutive carrying a social history.** *Trapito* — literally *little rag*, formally a diminutive of *trapo* — is the Argentine word for the informal parking attendants who guide drivers into spots on the street in exchange for a few coins. The word names a labour, a class, an economic informality, a particular relationship between drivers and the people who manage public space without official sanction. It carries the affective register of the diminutive — partly affectionate, partly dismissive — and the entire socio-economic structure that produced the role. There is no English word for *trapito*. The technical register doesn't have one because the technical register doesn't see the labour.

These are different kinds of suppression. *Daemon* is buried etymology that no longer surfaces. *Quilombo* is unstripped context the technical register keeps off-limits. *Trapito* is unstripped context that has no English technical equivalent at all. Three signs that natural language carries weight technical vocabulary refuses, and that the refusal is not free.

## Where this series goes

The previous article was the personal beginning — the moment in Spanish that started me looking for this everywhere. This article is the broader observation. The next installments stay focused on the two specific projects the observation produced:

- **Inflexión** — a hand-built esoteric programming language whose semantics flow from the grammatical features of Rioplatense Spanish (*ser* / *estar*, mood, aspect, clitic ordering, diminutive morphology). The first formal paper covers the language design; future articles in this series will take one mapping at a time and walk through what it means in essay form.
- **Babel** — the methodology and runtime for building esoteric programming languages programmatically; how the parameter schema works, what the runtime produces, why the field has needed something like this for thirty years.

Some installments will be technical. Some will be reflective. The series is the unit of work — any single article is a chapter, not a book.

## A working hypothesis I will keep returning to

Technical vocabulary's refusal to carry weight is *useful* — code needs precision, names need to mean the same thing across cultural contexts, the borrowed-and-stripped word *travels* in a way the unstripped word would not. The argument for the technical register is real.

The counter-argument is that the refusal is *partial*. The weight stays available; the speakers just stop noticing it. The choice is not *carry the weight* versus *do not carry the weight*; it is *let the weight be visible* versus *let the weight be invisible*. The first lets the speaker decide what to do with it; the second decides for the speaker, by silence.

A programming language that let the weight be visible — that built grammatical structure or vocabulary so the speaker could not avoid noticing what the word carried — would be doing different cognitive work than one that hid the weight. *That* is the hypothesis Babel and Inflexión, together, are trying to test.

This series is the long way of showing why the test is worth running.

---

*The customer was talking about Microsoft Mesh. I was hearing quilombo. The series is about why the gap between those two perceptions matters — and what programming-language design could do, if the gap were treated as an opportunity rather than a noise floor.*

---

[^bug]: The *moth in the relay* story for *bug* is the canonical Grace-Hopper anecdote. The etymology actually predates the moth (the term *bug* for a defect was already in 19th-century engineering use), but the moth incident in 1947 cemented the computing register.
