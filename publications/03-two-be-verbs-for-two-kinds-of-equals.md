# Two Be-Verbs for Two Kinds of Equals

> *Fourth article in an RCI LinkedIn series on the impact of language in technology. The first three were narrative — the personal predecessor ([Listening to Spanish Again](/babel/articles/listening-to-spanish)), the series-aperture observation ([What Technical Vocabulary Refuses to Carry](/babel/articles/what-technical-vocabulary-refuses-to-carry)), the lineage-discovery story ([I Thought I Was the First](/babel/articles/i-thought-i-was-the-first)). This one is the first of the technical articles. First-person voice, but the subject is the language.*

> *Published on LinkedIn 2026-05-13 — <https://www.linkedin.com/feed/update/urn:li:ugcPost:7460174040998096896/>.*

There is a trap English speakers learning Spanish fall into within the first month. You want to say *I'm bored*. You reach for the Spanish word for *to be*. The dictionary helpfully gives you two: *ser* and *estar*. You pick one — say, *ser* — and confidently announce *soy aburrido*. The Spanish-speaker you're talking to either suppresses a smile or lets it show.

You did not say *I'm bored*. You said *I am a boring person*.

To say *I'm bored*, you needed *estar*: *estoy aburrido*. The two verbs are not interchangeable. *Ser* attributes essence — what you *are*, by nature, persistently. *Estar* attributes state — how you *happen to be*, right now, in this moment. The trap is built into the design of the language. English collapses both into *to be* and lets context sort it out; Spanish does not.

This is the cleanest of the six grammatical-semantic mappings I make in *Inflexión* — the Spanish-grammar esoteric programming language I'm building, the one I introduced [in a previous article](/babel/articles/i-thought-i-was-the-first) as the fifth member of a small lineage. *Ser* maps to immutable bindings. *Estar* maps to mutable bindings. The analogy is so close it barely needs explaining; the analogy is the whole article.

## The two-copula system, quickly

Spanish has two copular verbs where English has one. The split is everywhere in everyday speech.

*La nieve es blanca* — *snow is white* (essentially, by nature of being snow). *La nieve está sucia* — *the snow is dirty* (it happens to be dirty in its current state, but dirtiness is not what snow is). *Carlos es médico* — *Carlos is a doctor* (it's his profession, his identity). *Carlos está cansado* — *Carlos is tired* (right now; not always). Native Spanish-speakers use the distinction without thinking; non-natives learn it by making the mistake described above and never making it twice.

The distinction is *grammaticalised* — it is built into the verb itself. You cannot say *to be* in Spanish without committing to one of the two readings. The language forces the choice on you at the syntactic level. There is no neutral *be*.

## What programming languages call this

Programming languages discovered a parallel distinction much later, and they had to invent vocabulary for it: *immutable* and *mutable*. *Const* and *let*. *Val* and *var*. *Final* and not-final. The split is the same one Spanish has had for centuries: a binding either fixes the meaning of a name forever, or it allows the meaning to change.

Most mainstream programming languages let you ignore the choice. In Python, `x = 5` does not tell you whether *x* is meant to be reassigned. The reader has to scan the rest of the function — or read your mind — to find out. Even languages that have the distinction (Rust, JavaScript, Kotlin, Scala) require you to spell it out with a separate keyword: `let mut`, `const`, `val`. The keyword is a *retrofit* — bolted on top of the assignment syntax to recover a distinction the language did not have natively.

Spanish, again, has had this natively for centuries. The verb is the type system.

## The Inflexión move

In Inflexión, a binding made with *ser* is immutable. A binding made with *estar* is mutable. That is it. There is no separate keyword. There is no annotation. The verb you choose at the binding site *is* the choice.

Three lines:

```
El total es 100.
El contador está en 0.
Hacé que el contador esté en 1.
```

Line one binds the name *total* to the value 100, immutably — *total* will refer to 100 forever in this scope. The choice of *ser* (*es*) commits the binding to immutability; subsequent code cannot change what *total* means. Line two binds the name *contador* to a cell whose current value is 0, mutably — the cell can be reassigned. The choice of *estar* (*está en*) commits the binding to mutability. Line three is a vos imperative — *hacé* (Rioplatense imperative of *hacer*, "to do") wrapped around a subjunctive clause — and it mutates *contador* from its current state (0) to a new state (1). The mutation is allowed because the binding was made with *estar*; if it had been made with *ser*, line three would be a type error.

The reader can see, from the verb at the binding site, whether they are looking at a defining binding or a current-state binding. There is no separate `const` keyword to scan for. There is no need to read the rest of the function to figure out what *contador* is allowed to do. The morphology *is* the type discipline.

A Spanish-speaking programmer reading these three lines does not have to learn anything new about programming. They already use *ser* and *estar* this way in everyday speech. The distinction Inflexión makes load-bearing for programming semantics is the distinction Spanish makes load-bearing for ordinary description. The mapping does not have to be taught; it has to be *noticed*.

## Why this is the cleanest of the six mappings

Inflexión has six grammatical-semantic mappings — number to scalar-versus-collection, mood to evaluation strategy, aspect to eager-versus-lazy, *ser*/*estar* to immutable/mutable, clitic ordering to argument routing, diminutive morphology to numeric scaling. *Ser*/*estar* is the cleanest of the six because the analogy is *already cognitively available* to the language's natural-language speakers. A Spanish-speaker reading Inflexión code does not have to map a grammatical category onto a programming concept; the grammatical category *already does* the programming work, in the speaker's everyday usage.

The other five mappings are more novel. Mood-as-evaluation-strategy asks the reader to think of subjunctive as *deferred*, which is true to Spanish in some senses (subjunctive is the mood of unrealised reality) but not how a Spanish-speaker normally thinks about it. Aspect-as-eager-versus-lazy is genuinely a stretch — Spanish-speakers do not normally use perfective and imperfective to distinguish *call-by-value* from *streaming*. Each of those mappings will get its own article in this series, and each will be a more interesting argument.

*Ser*/*estar* is the easy mapping — the one the language designer barely had to argue for. I am writing about it first because it is the gentlest entry into the design and because it shows, in three lines of code, why building a programming language on a substrate language that *already has the distinctions you want* is a different kind of move than retrofitting a programming language with new keywords.

## What's coming next

The harder mappings are next. Mood-as-evaluation-strategy is the most novel of the six and gets the next article. Aspect comes after that. Clitics — the most syntactically unusual — come later still, with worked examples that exercise the fixed Spanish clitic-ordering system as positional argument routing. Diminutive morphology gets its own piece. Number agreement gets its own piece. Each is a real argument the language has to make.

For now: the next time you write `let mut x = 0` or `const total = 100`, notice that you are saying something Spanish-speakers have been saying with their verbs for centuries. *Estar* is your `let mut`; *ser* is your `const`. The retrofit is the part that's new.

---

*Inflexión is a hand-built esoteric programming language whose semantics flow from the grammatical features of Rioplatense Argentine Spanish. It is the fifth member of a small lineage of inflection-driven non-English natural-language esoteric programming languages — Perligata (Latin, 2000), Espro (Esperanto, 2015, idea-only), Tampio (Finnish, ~2017), Wenyan (Classical Chinese, 2019), Inflexión (2026) — and the first to use a living Romance language. The full design paper is at roderickc.com/inflexion. The companion methodology paper, on Babel — the runtime that generates esoteric programming languages from parameter sheets — is at roderickc.com/babel.*
