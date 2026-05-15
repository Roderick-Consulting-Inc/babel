# 02 — Inspiration

> *Draft 1, 2026-05-08. Author: Roderick C with Claude as scribe. Each source below teaches the project something specific; none of them is the methodology. Marked `[TBD verify]` where claims need a careful pass against primary sources before publication.*

## A note on this document

This is not a literature review and not a list of influences. It is a record of what is already in the world that the project should refuse to redo, and of the specific lessons each precedent contributes. Babel and Inflexión sit at an intersection of several traditions — esoteric programming languages, the obfuscation-contest culture, the literary-technical writing tradition, the political life of computing artefacts, controlled natural languages, Romance linguistics, and the situated reality of how Spanish is actually spoken. None of these has fully grappled with what the others know. The point of this document is to be specific about what we are taking from each.

## The esoteric-language corpus

The wiki at esolangs.org [^esolangs] catalogues something on the order of 1,500 named esoteric programming languages. After cleaning out the aliases, jokes, and stubs, the field still organises into a small set of recurring patterns.

The dominant patterns are well-trodden. **Brainfuck-style tape machines** with eight instructions and a byte tape; **stack-based concatenative languages** in the FALSE / Forth lineage; **one-instruction-set machines** like Subleq; **two-dimensional source grids** (Befunge and the fungeoid family — including hex and 3D variants); **whitespace-only encodings** where tabs, spaces, and newlines are the only tokens; **register-and-jump assembly clones**. Together these account for the majority of the corpus.

Less common but established: **concatenative golfing languages** (J, K, Jelly), **string-rewriting systems** in the Markov / Thue tradition, **combinator-only languages** (Unlambda, Lazy K), **cellular automata as program** (Wireworld), **time-travel and reverse-execution**, **probabilistic or scheduling-nondeterministic languages** (Whenever), **graph-rewriting**.

And the singletons — the ones nobody copied because they weren't really copyable. *Malbolge* (deliberately unlearnable; instruction effect depends on memory address). *Piet* (source is a bitmap; flow follows colour transitions). *Velato* (MIDI as source). *Folders* (program is a directory tree, files empty). *Shakespeare* (five-act plays; characters are integer variables). *Chef* (recipes; ingredients are variables). *Rockstar* (song lyrics; "poetic literals" assign integers via word-letter counts; uses a real parser). *INTERCAL* (the original anti-language; rejects programs that don't say "PLEASE" with the right frequency). *Chicken* (one token, repetition-encoded). *Unary* (the entire program is one giant integer expressed in unary). *Beatnik* (Scrabble word scores determine the instruction). *Taxi* (program is a city map; you drive passengers between locations). *Vigil* (runtime contracts; a function failing its spec deletes its own source file).

Adjacent to the esolang tradition proper, and instructive for it, sit the obfuscation contests. The International Obfuscated C Code Contest (IOCCC) [^ioccc], running annually since 1984, and the Obfuscated Perl Contest [^opc], a shorter-lived event in the late 1990s, accept programs that are formally correct, executable, and incomprehensible without dedicated reading. They are not esoteric languages — the host language is C, or Perl, used straight — but they explore the same gap that esolangs do: the gap between *what compiles* and *what communicates*. A serious programming language usually pretends this gap does not exist. Esolangs and obfuscation contests, between them, make it visible. Babel's parameter axes for verbosity, abstraction, and unpredictability are essentially knobs on this gap.

What this teaches the project:

The variation axes that distinguish esolangs are well-mapped: choice of base machine, instruction count, cell width, memory topology, encoding scheme, I/O model, instruction additions, instruction removals, and surface theming. These are exactly the axes Babel needs as its parameter schema. The field has done the empirical work; nobody has consolidated it.

The corpus is a museum of singletons. There is no widely-used kit for generating new languages; every author hand-rolls the same restructuring. The roughly eight hundred Brainfuck derivatives in the wiki's category [^bf-derivatives] are the loudest evidence — they exist *because* a template tool does not. This is the empty seat Babel takes.

The corpus is also overwhelmingly Anglophone in its cultural references. Cooking, song lyrics, action-movie quotes, Scrabble, fetish erotica, anti-pleasantries — all English. Cultural specificity outside English is rare; *grammar engagement* (rather than vocabulary substitution) of a non-English natural language is rarer still — a small lineage of four (discussed at length below). Inflexión joins that lineage as the first to use a Romance language and the first to engage the specific Spanish feature set its design centres on.

A note about the trajectory of perception. Esoteric languages, on first encounter, read as a joke. Read again, slowly, they are a research programme on what mainstream programming languages quietly assume — about syntax, about state, about how a program is supposed to be read. The two readings are not in conflict: the joke is real, and the research programme is real. Babel takes them as the second thing without disowning the first.

## El Pueblo and the lexicon as design discipline

The work documented at *roderickc.com/pueblo* [^pueblo] — the Three-Ledger Methodology and its instantiation as El Mundo — is the closest local precedent for what we are doing, and the lesson it teaches is about discipline rather than technique.

El Mundo's contribution is a coherent vocabulary, drawn from the imagery of nineteenth-century rural Argentine pueblo life, in which "each name encodes a commitment." The vocabulary is not decorative; it is the design. Choosing to call an attestation a *Testimonio* and a sensor relay a *CCL Posta* is not a flavour decision laid on top of finished architecture. The choice constrains the architecture: a thing called *Testimonio* has to behave as testimony — appendable, signed, never silently revised. The methodology is vocabulary-agnostic; El Mundo is one instantiation of it; the same methodology could be re-instantiated under a different metaphor and produce a recognisably similar architecture with different names and different cultural texture.

What this teaches the project:

The methodology / instantiation split is exactly what Babel needs. Babel is a methodology — the set of variation axes, the parameter schema, the runtime that turns parameters into a working language. Any specific generated language is an instantiation. Inflexión is itself one instantiation of the broader research, even though we are hand-crafting it rather than generating it; the relationship between Inflexión and a future Babel-generated Spanish-grammar language is the same as the relationship between El Mundo and a hypothetical re-instantiation of the Three-Ledger Methodology under a different metaphor.

Cultural specificity without parody is achievable. El Mundo is grounded in a particular place and time and reads as serious work, not as costume. La Weá, by contrast (see below), uses Chilean specificity for comic effect. Both are legitimate; Inflexión needs to pick a register and stay there.

## Technical writing as literary medium

Two precedents from outside the esolang tradition matter for the project's tone, not its mechanism. They establish that the boundary between technical writing and literary writing is permeable, and has been crossed productively before — which has consequences for how the white papers in this series can be voiced.

Bill Cheswick's *An Evening with Berferd* [^berferd], published at USENIX in 1992, narrates an attempted intrusion into a Bell Labs network as a story, with characters, stakes, pacing, and an ending. The paper is rigorous as security research; it loses nothing of its technical content by being told as narrative. It establishes that a technical artefact can be told as a story without compromising on its claims, and that the choice of *how to tell* a piece of work is itself part of the work.

The Jargon File, maintained for decades by hackers at MIT and elsewhere and most fully edited by Eric Raymond as *The New Hacker's Dictionary* [^jargon], is a vocabulary that does real work. Its entries are not decorative. They mark what a community of programmers noticed and how it noticed; the shape of the dictionary is the shape of the community's attention. It demonstrates that a technical vocabulary can be conscious of itself — affectionate, self-mocking, semantically dense — without becoming purely literary, and that a vocabulary curated this way changes what its practitioners can think with. This is the same lesson El Pueblo's lexicon teaches, arrived at from a different direction.

What this teaches the project: white papers in the Babel / Inflexión series can be voiced essayistically, with vocabulary that matters, without any loss of rigour. The reading-as-literature voice and the thinking-carefully voice are the same voice, when the work is done well.

## The machine as political artifact

A separate strand of inspiration treats computing systems as artefacts embedded in human and political structures, rather than as pure technique. Three precedents from this strand are useful here because they speak directly to the substance of what a programming language is: not a neutral channel between intent and execution, but an artefact carrying the stamp of the people who shaped it, the trust boundaries they encoded, and the predictability they chose to allow.

Tracy Kidder's *The Soul of a New Machine* [^kidder] tells the story of Data General's Eclipse MV/8000 — a 32-bit minicomputer designed in the late 1970s — by following the engineers, the project politics, the all-nighters, the personalities, and the rivalries. The technology is not abstracted from the people. It is told as a thing that emerged from a specific human and political situation, and the story would be false if it were told any other way. What this teaches the project: a language design is not a neutral artefact. It carries the stamp of the people who made the design choices and the situation in which they made them. The white papers in this series should engage that fact rather than write around it. Kidder's title is also the title of a question that the project should keep asking — what is the *soul* of an esoteric language, and of a generator for esoteric languages? — without expecting a clean answer.

The *mushroom theory of information* [^mushroom] — the management aphorism that subordinates are kept in the dark and fed manure — names a structural feature of how information moves in human systems: the *deliberate* restriction of what each layer of a system knows. The aphorism is uncharitable in its standard form, but the underlying observation is real and design-relevant. Information asymmetry is not a bug to be eliminated; it is a parameter of a system's design, with consequences. A programming language can choose how much of its execution model to expose to its programmer — Brainfuck exposes everything, an ML-family language exposes a curated subset, a heavily-managed runtime exposes almost nothing. Each is a different theory of what the programmer should know. Babel's parameter schema is, in part, a knob on this same dimension: how much the language tells its user about what it is doing, and how much it withholds. The mushroom-theory framing makes the choice visible as a political one rather than a merely technical one.

The *rings-of-security* architecture — most fully realised in Multics with eight protection rings, surviving today as x86's four [^rings] — is a different but related precedent. Each ring is a trust boundary. Code in a less-privileged ring cannot directly read or write the state of a more-privileged ring; it must go through controlled gates. The architecture admits, structurally, that systems contain components of different trustworthiness, and that the design's job is not to deny this but to model it. The predictability or unpredictability of a programming language's behaviour is itself a layered phenomenon: the processor is mostly predictable, the compiler is occasionally surprising, the runtime is sometimes adversarial, the program is whatever the programmer made of it, and the programmer is human. A serious language design admits all of these layers and decides what to expose at each. Babel's *unpredictability* parameter is the one most directly informed by this. Inflexión's use of subjunctive mood — to mark hypothetical, deferred, or doubted claims — encodes the same insight at the syntactic level: not every sentence in the program is asserted with the same force, and the language can mark the difference.

What this teaches the project, taken together: human effort, politics, technology, and predictability are not adjacent topics that the white papers might or might not address. They are part of the substance of what a programming language is. The Babel / Inflexión research treats them as substance, not as colour.

## Romance grammar — what Spanish kept and what it added

Spanish is a Romance language, which means it descends from Vulgar Latin. The grammatical features that survive into modern Spanish are not all the same age, and they are not all shared across the Romance family. For Inflexión's design choices to be defensible, the doc on the language itself (`05`) will have to be specific about which features are being mobilised and why. This document records the shape of the inheritance.

Latin had a robust case system — five declensions distinguishing nominative, accusative, genitive, dative, ablative, vocative, and (vestigially) locative. **Spanish lost almost all of it.** Modern Spanish nouns and adjectives do not decline for case; word order and prepositions carry the load that case marking once carried. The single live trace of the Latin case system is the personal pronoun: *yo / me / mí / conmigo* preserves nominative / accusative-dative / oblique / comitative distinctions that nouns no longer make. This matters: if Inflexión wants to use "declension" as a programming feature, it cannot use the Latin model directly. It has to use what Spanish actually preserves — pronoun case — or pick from features Spanish gained after Latin.

What Spanish *kept* in robust form:

- **Verb conjugation** by person, number, tense, mood, and aspect. Spanish verbs are richer than English ones in every dimension. A single conjugated form can carry information English would need two or three words to express.
- **Aspect distinction** — preterite (perfective: completed action) vs. imperfect (imperfective: ongoing or habitual past). English collapses both into "ate"; Spanish keeps them apart morphologically.
- **Subjunctive mood** — used for hypothetical, desired, doubted, or unrealised actions. Robust and productive in Spanish in a way it is mostly not in modern English.
- **Imperative mood** — separate forms, often distinct from indicative.

What Spanish *added* or developed after Latin:

- **The ser / estar split** — two copular verbs (both descend from different Latin roots: *esse* and *stare*), distinguishing essential or defining properties (*ser*) from transient or located states (*estar*). This is a Romance innovation; Latin had only *esse*. The split is most fully developed in Spanish and Portuguese; Italian and French have it less sharply.
- **Productive diminutive and augmentative morphology** — *-ito*, *-ita*, *-illo*, *-ón*, *-azo*, *-ote*. Latin had diminutive suffixes but Spanish made them productive across registers and grammatical categories. They carry meaning beyond size: affection, contempt, intensity, casualness.
- **Clitic pronoun system** — object pronouns (*me, te, se, lo, la, le, los, las, les, nos, os*) attach to the verb in fixed orders. The order is grammaticalised: when multiple clitics co-occur, they appear in a strict sequence. This is a syntactic feature with no clean English analogue.
- **Voseo and dialect specificity** — Rioplatense, Mexican, Andean, Caribbean, Chilean, peninsular variants differ in pronoun systems, verb forms, and lexicon. Choosing a dialect is a design choice with cultural weight.

What this teaches the project:

Inflexión should mobilise features that are alive and productive in modern Spanish, not antiquarian survivals from Latin. The features that carry the most semantic load — number, mood, aspect, ser/estar, clitics, diminutives — are the ones to design with. Each one can be mapped to a programming concept; whether the mappings are *good* is the design question for `05`.

A choice of dialect is forced. There is no "neutral" Spanish in the way there is a relatively neutral standard written English. The default options are Rioplatense (Argentine, with *vos*), peninsular standard, or a deliberately constructed register that picks features across dialects. La Weá's example shows that picking a dialect can be a feature, not a limitation.

## Linguistic ecology and the Argentine pockets

The Romance-grammar inheritance is one source of structural material for Inflexión. A separate source is the linguistic ecology in which Spanish is actually spoken — which constrains what kind of Spanish is available to design with, and which has historically been treated as ambient context rather than as a precedent in its own right.

Argentina is, for reasons of geography and immigration history, an unusually concentrated set of linguistic pockets. The country's late-colonial settlement pattern, its waves of European immigration in the late nineteenth and early twentieth centuries, and its physical distance from the principal Spanish-speaking metropoles allowed pockets of Italian, Portuguese, German, Arabic, Chinese, English, and peninsular-Spaniard registers to be maintained alongside Argentine Spanish, often within a single neighbourhood and within the audible range of a single household. The Spanish that resulted — Rioplatense, with *voseo*, with substantial Italian-derived intonation, with the lunfardo lexicon — is itself a pocket: a regionally distinct preservation of features that have eroded elsewhere, alongside features that other Spanish-speaking regions never had.

The relevant observation is general: living languages are not uniform, and natural-language design materials come in pockets. The pockets are produced by isolation, by immigration, by class, by trade, by literary tradition. They are not noise around an idealised standard form; they are where the language is actually preserved.

What this teaches the project: a language design that addresses "Spanish" in the abstract is making a stronger claim than the linguistic situation supports. Inflexión is being designed by an author whose Spanish is Rioplatense; that fact is a constraint to be honest about, not a defect to apologise for. La Weá's choice to be specifically Chilean rather than generically Spanish-speaking is the right precedent at the level of *strategy*, even if its grammatical engagement remains shallow. The dialect choice for Inflexión should be made deliberately and named.

## The Spanish-flavoured esolangs that already exist

Three named languages on the wiki engage Spanish-language identity: Mierda [^mierda], La Weá [^laweá], and Chespirito [^chespirito]. A fourth, Commercial, exists as a stub. A fifth page, *Español*, is a 2020 joke entry — declared "uncomputable" because it claims to solve the halting problem — and is not real prior art.

**Mierda** is a Brainfuck reskin. Its eight instructions are renamed into Spanish words (*Mas*, *Menos*, *Derecha*, *Izquierda*, *Decir*, *Leer*, *Iniciar Bucle*, *Terminar Bucle*). The semantics are Brainfuck's, unmodified. The language engages Spanish at the level of the dictionary, not the grammar.

**La Weá** is Chilean. Its sixteen instructions use Chilean slang (*weón*, *chucha*, *pichula*, *tula*, *perkin*) and its execution model adds a clipboard register to the Brainfuck base. It demonstrates two useful things: a dialect-specific language can hold together as a coherent artifact, and small additions to a base instruction set can give a derivative its own character. The grammatical engagement is still vocabulary-only.

**Chespirito** uses catchphrases of Roberto Gómez Bolaños — the Mexican comedian — as its instructions (*chilindrina*, *chompiras*, *chipote*, *chillón*) over a Brainfuck base, plus one novel instruction *chiripiolca* that introduces randomness. Same pattern: cultural reference at the surface, no engagement with Spanish grammar as a structural feature.

What this teaches the project:

The vocabulary lane is not empty but it is well-served by these three. Adding a fourth language that reskins Brainfuck with Spanish words is not a contribution. The unfilled space is **grammar engagement**: a Spanish-themed language whose execution model uses Spanish grammatical structure to do real work. None of the existing three crosses that threshold.

The dialect-specific lane is open beyond La Weá's Chilean register. Rioplatense, with *voseo* and *lunfardo*, is unclaimed. Peninsular, Mexican, Andean, and Caribbean are unclaimed. Inflexión's dialect choice is a real design decision, not a default.

## Inflection-driven non-English natural-language esolangs

![Inflection-driven non-English natural-language esolangs — horizontal timeline placing Perligata (Latin, 2000), Espro (Esperanto, 2015, idea-only), Tampio (Finnish, ~2017), Wenyan (Classical Chinese, 2019), and Inflexión (Rioplatense Spanish, 2026) along a single axis.](https://diagrams.roderickc.com/api/v1/apps/www/diagrams/inflexion-lineage.svg)

*Mermaid source: [`diagrams/lineage-timeline.mmd`](../diagrams/lineage-timeline.mmd).*

A small but real genre: esoteric programming languages that engage the *grammar* (not just the vocabulary) of a non-English natural language as syntactic structure or semantic substrate. We have found four members of this genre, and Inflexión joins them as the fifth.

**Perligata** [^perligata] — formally *Lingua::Romana::Perligata*, a Perl module written by Damian Conway in 2000. It is the canonical inflection-as-semantics precedent and predates the others by nearly two decades. In Perligata, Latin declension determines variable type — a scalar is a neuter-singular second-declension noun; an array is its plural; a hash takes a different declension — and verb conjugation determines the calling context of a function. Free word order is permitted exactly because Latin's inflectional system carries the syntactic information that English word order would have to carry. Perligata's contribution is the demonstration that a fully inflected natural-language grammar can be made *load-bearing* for programming-language semantics, not merely decorative.

**Wenyan** (文言) [^wenyan] — Lingdong Huang's 2019 Classical Chinese language, developed during a CMU finals week and released the same December [^choi-wenyan]. It uses literary Classical Chinese particles (者, 也, 而, others) as syntactic markers in their literary positions, with a real parser handling real grammatical constructions. It compiles to JavaScript, Python, and Ruby. Wenyan went viral on its release and earned a Guinness World Records entry as the first Classical Chinese programming language; the project has been quiet since 2023 but the codebase is intact.

**Tampio** [^tampio] — Iikka Hauhio's Finnish-grammar language, in active development since approximately 2017. It uses the libvoikko Finnish morphological analyzer to engage eight Finnish noun cases (nominative, genitive, partitive, essive, translative, illative, adessive, inessive / elative), verb conjugation in active and passive voice, imperatives and participles, more than twenty-five postpositions, comparatives, plural inflection, and agreement. Tampio is, of the four, the most directly relevant precedent for Inflexión: a single-author hobbyist project using the grammar of a *living* agglutinative language as semantic substrate.

**Espro** [^espro] — a 2015 idea page on the esolangs.org wiki for an Esperanto-grammar language using accusative *-on* for fields, accusative-adjective *-an* for types, infinitive *-i* for methods, and *-ar-* for arrays. Never implemented, but the design sketch is recognisable as an inflection-as-semantics proposal in the same lineage.

What this teaches the project:

The lane is not empty. Inflexión joins a small genre rather than opening it, and the project's positioning needs to acknowledge the existing inhabitants honestly. Each of the four precedents engages a different language family — Italic (Perligata), Sino-Tibetan (Wenyan), Uralic (Tampio), and the constructed Esperanto (Espro). None engages a Romance language. None engages the specific feature set — the *ser* / *estar* copular split, the indicative / subjunctive / imperative mood three-way, the perfective / imperfective aspect contrast, the fixed-order Spanish clitic system, or productive diminutive / augmentative morphology — that contemporary Spanish makes available. Inflexión's distinctive contribution sits at that intersection: a living Romance language and a feature set that previous inflection-driven esolangs have not engaged.

The discovery of the existing four also vindicates the *honest preparation* stance the project has taken: the lane is more populated than an earlier draft of this document claimed, and revising the doc to acknowledge the inhabitants is exactly the kind of work the planning track should do before publication. The earlier framing — *"Wenyan is the only serious precedent"* — was wrong; the corrected framing is more interesting because Inflexión gains intellectual company.

## Controlled natural languages

A separate tradition deserves its place here. Controlled natural languages — *Attempto Controlled English* (ACE) [^ace], *Inform 7* [^inform7], *Gellish*, others — are projects that *constrain* a natural language to a subset that can be parsed unambiguously. Inform 7 is the most polished and successful, used to write interactive fiction in English-like rule statements that compile to a working game.

These projects are siblings to Inflexión, not ancestors, and the relationship is worth being precise about. A controlled natural language *restricts* its substrate to make it tractable. It says: "Here is a subset of English that we promise to parse." Inflexión does something different. It *uses the existing grammatical structure* of Spanish — number, mood, aspect, clitic ordering — as the source of programming semantics. It is not asking Spanish to become a logical subset; it is asking what programming semantics fall out when the surface form is required to obey Spanish grammar.

What this teaches the project:

There is a real intellectual lineage. Inflexión is not coming from nowhere. It has an answer to "isn't this just controlled natural language?" — *no, the move is different in direction; controlled NL restricts, we exploit*.

## The LLM prompting-density argument

The fourth tradition Inflexión wants to engage with is the youngest and the least settled. Prompt engineering as practiced today is largely about structure (chain-of-thought, few-shot examples, system prompts) and rarely about the intrinsic grammatical density of the natural language used. The literature on linguistic typology, on the other hand, knows that languages differ enormously in how much grammatical information they encode per word. Agglutinative languages — Finnish, Turkish, Quechua, Hungarian — pack many morphemes into a single surface form, each carrying syntactic or semantic load. Analytic languages — English, Mandarin — distribute the same load across multiple words. Spanish is between the two: more synthetic than English, less than Finnish, but rich in mood and aspect distinctions that English does not mark.

The hypothesis Inflexión wants to entertain — and `05` will defend in honest, un-overclaimed form — is that **a programming language whose surface syntax mirrors a more grammatically dense natural language is a denser substrate for LLM prompting and code generation**. A function name in Inflexión that already encodes its argument number, its mood (asserted versus hypothetical), and its aspect (one-shot versus ongoing) is, by construction, less ambiguous than its English equivalent.

This is a hypothesis, not a finding. The relevant empirical work has not been done — at least, not in the form of a controlled comparison between code in a grammatically dense surface syntax and code in an English-keyworded equivalent, evaluated for an LLM's downstream code-generation accuracy. `[TBD verify]` whether any prior empirical work bears on this directly.

What this teaches the project:

The angle is novel enough to be worth developing and defending, and modest enough to be honestly disclaimed as a hypothesis until evidence accrues. It gives the project a contemporary relevance that pure esolang work would lack.

## What the field doesn't have, summarised

Four absences, taken together, define the position we believe Babel and Inflexión take. Each absence is stated as we currently see it; we welcome correction on any of them.

1. We have not found a general-purpose template tool for esolang construction. The variation axes are mapped; the consolidation appears not to have happened.
2. Cultural and grammatical specificity outside English appears rare on the esolangs.org wiki. Vocabulary skins are common; *grammar engagement* — using the morphological structure of a non-English natural language as semantic substrate — is a small lineage of four (Perligata, Wenyan, Tampio, Espro), no Romance language among them, no engagement of the *ser* / *estar* split or productive aspect / mood / clitic systems among them.
3. Controlled natural languages have explored constraining English for tractability, but the inverse move — exploiting an existing language's grammar as a source of programming semantics — has not, to our knowledge, been seriously attempted for any living non-English language.
4. The intersection of grammatical-density linguistics and LLM prompting appears undeveloped. The hypothesis that denser grammatical surface forms make for cleaner LLM substrates is plausible and, as far as we can tell, untested.

These four absences are the lane Babel and Inflexión occupy. The next document, `03-position.md`, says what the project is and is not solving — given that "what we solve" is, deliberately, "nothing in the conventional problem-fix sense."

## Open items for the next pass

- `[TBD verify]` — Specific Wenyan compilation targets, parser approach, current activity. Confirm against the Wenyan repository before publication.
- `[TBD verify]` — Whether any prior empirical work compares LLM downstream performance across natural-language grammatical densities of programming-language surface syntax. If such work exists, cite it. If it does not, say so.
- `[TBD verify]` — Whether *Aymara* or *Quechua* programming-language work exists on the wiki or in academic publication. The agglutinative-language angle would be strengthened or complicated by precedent there.
- `[TBD]` — Dialect choice for Inflexión. Rioplatense (Argentine) is the natural default given authorship; the choice deserves deliberation rather than defaulting.

---

[^esolangs]: Esoteric programming language wiki: <https://esolangs.org/wiki/Main_Page>. Used here as the primary index of the corpus.
[^bf-derivatives]: Category page: <https://esolangs.org/wiki/Category:Brainfuck_derivatives>. Approximate count of ~800 verified at time of drafting.
[^ioccc]: International Obfuscated C Code Contest: <https://www.ioccc.org>. Running annually since 1984.
[^opc]: Obfuscated Perl Contest, archived discussion at <https://www.foo.be/docs/tpj/issues/vol1_3/tpj0103-0001.html> and elsewhere; ran roughly 1996–2000 under the auspices of *The Perl Journal*. CONFIRM exact run-dates and canonical archive URL before publication.
[^berferd]: Cheswick, Bill. 1992. "An Evening with Berferd, in which a Cracker is Lured, Endured, and Studied." *Proceedings of the Winter USENIX Conference*, San Francisco, January 1992. Available at <https://www.cheswick.com/ches/papers/berferd.pdf>.
[^jargon]: Raymond, Eric S., ed. *The New Hacker's Dictionary.* MIT Press. The Jargon File from which this is drawn is maintained online at <http://catb.org/jargon/>; multiple print editions exist.
[^kidder]: Kidder, Tracy. 1981. *The Soul of a New Machine.* Boston: Little, Brown and Company. Pulitzer Prize for General Non-Fiction, 1982.
[^mushroom]: The "mushroom theory" or "mushroom management" is a long-circulating organisational aphorism — *kept in the dark and fed manure* — with no single canonical source. Used here as a folk-theoretical observation rather than a cited claim; for white-paper-grade engagement, the structural concept of information asymmetry is better cited to organisational-theory and information-flow literature (CONFIRM).
[^rings]: The protection-ring architecture was developed for the Multics operating system in the late 1960s. Schroeder and Saltzer's "A Hardware Architecture for Implementing Protection Rings" (*Communications of the ACM*, March 1972) is the canonical paper. Modern x86 implements a four-ring subset (Ring 0–3); most systems use only Ring 0 (kernel) and Ring 3 (user). CONFIRM citation form for white paper.
[^pueblo]: Rodriguez, R. *El Pueblo / Three-Ledger Methodology / Lexicon.* RCI, available at <https://www.roderickc.com/pueblo>. Internal RCI publication.
[^mierda]: <https://esolangs.org/wiki/Mierda>
[^laweá]: <https://esolangs.org/wiki/La_We%C3%A1>
[^chespirito]: <https://esolangs.org/wiki/Chespirito>
[^perligata]: *Lingua::Romana::Perligata* by Damian Conway, 2000. Distribution: <https://metacpan.org/dist/Lingua-Romana-Perligata>. Esolang wiki entry: <https://esolangs.org/wiki/Perligata>. The canonical inflection-as-semantics precedent.
[^wenyan]: Wenyan (文言): <https://wy-lang.org> and <https://github.com/wenyan-lang/wenyan>. Created by Lingdong Huang at CMU, December 2019. Compiles to JavaScript, Python, and Ruby. Last release v0.3.4 (July 2020); repository quiet since 2023.
[^choi-wenyan]: Charles Q. Choi, "World's First Classical Chinese Programming Language," *IEEE Spectrum*, January 31, 2020: <https://spectrum.ieee.org/classical-chinese>.
[^tampio]: *Tampio* by Iikka Hauhio ("fergusq"): <https://github.com/fergusq/tampio>. Esolang wiki entry: <https://esolangs.org/wiki/Tampio>. Active development since ~2017. Uses libvoikko Finnish morphological analyzer to engage eight cases, verb conjugation, postpositions, plural inflection, and agreement.
[^espro]: *Espro*, idea page by "Timwi" (handle), 2015: <https://esolangs.org/wiki/Espro>. Esperanto-grammar esolang concept; never implemented.
[^ace]: Attempto Controlled English: <http://attempto.ifi.uzh.ch>. Fuchs, Kaljurand, and Kuhn at the University of Zurich.
[^inform7]: Inform 7: <https://ganelson.github.io/inform-website/>. Developed primarily by Graham Nelson.
