# The Article Already Knows

> *Ninth article in an RCI LinkedIn series on the impact of language in technology. Builds on the predecessor ([Listening to Spanish Again](/babel/articles/listening-to-spanish)), the series-aperture observation ([What Technical Vocabulary Refuses to Carry](/babel/articles/what-technical-vocabulary-refuses-to-carry)), the lineage-discovery story ([I Thought I Was the First](/babel/articles/i-thought-i-was-the-first)), and the five technical deep-dives so far ([Two Be-Verbs for Two Kinds of Equals](/babel/articles/two-be-verbs-for-two-kinds-of-equals) on ser/estar, [Three Stances Toward a Statement](/babel/articles/three-stances-toward-a-statement) on mood, [One Verb, Two Computations](/babel/articles/one-verb-two-computations) on aspect, [When the Verb Carries Its Own Arguments](/babel/articles/when-the-verb-carries-its-own-arguments) on clitics, [A Cafecito Is Not Just a Small Coffee](/babel/articles/a-cafecito-is-not-just-a-small-coffee) on diminutive and augmentative). First-person voice; the sixth and closing technical article. Subject: number agreement, the most pervasive of Inflexión's six grammatical-semantic mappings — and the closing piece of the series's technical curriculum.*

You walk into a small shop in Buenos Aires. You point at one item: *¿Cuánto sale?* — *how much does it cost?* You point at three: *¿Cuánto salen?* — *how much do they cost?* Same verb (*salir*, used colloquially for *to cost*), same question, two endings. The verb reaches back to the implicit subject — singular *esto* (this), plural *estos* (these) — and concords. The shopkeeper does not have to think about which form to use; you do not have to think about which form to interpret. The lockstep is automatic.

This is *number agreement*, the sixth and closing of *Inflexión*'s technical mappings — and the most pervasive of the six. The grammatical distinction Spanish marks across articles, nouns, adjectives, and verbs in lockstep maps directly to a programming distinction English-keyworded languages have to assemble from separate scaffolding: *scalar versus collection*.

## The phenomenon, quickly

Spanish marks number on four parts of speech, and the four parts of speech move in lockstep through every clause:

- **Articles**: *el / los*, *la / las*, *un / unos*, *una / unas*
- **Nouns**: *precio / precios*, *casa / casas*, *vista / vistas*
- **Adjectives**: *alto / altos*, *blanca / blancas*, *rápido / rápidos*
- **Verbs**: *es / son*, *está / están*, *viene / vienen*, *sumó / sumaron*

A clause concords throughout. *El precio alto es justo* — the high price is fair. *Los precios altos son justos* — high prices are fair. Every word in the noun phrase, and every verb that takes the noun phrase as subject, moves to plural together. A Spanish-speaker who writes *los precio alto* (plural article and adjective, singular noun) is making a typo, not a stylistic choice; the language registers it as ill-formed at the syntactic level.

This is *concord* — the inflectional discipline of marking the same feature on every word in a clause that depends on the head noun. Spanish marks both number (singular versus plural) and gender (masculine versus feminine) this way; Inflexión's design engages number, not gender.

## What programming languages do with this

Mainstream programming languages have to assemble the scalar-versus-collection distinction from separate scaffolding:

- **Type annotations**: `int price` versus `List[int] prices`. The type system enforces; the variable name is a reader-facing hint that does not have to match the type.
- **Naming conventions**: `price` versus `prices`. The trailing *s* signals collection-ness by convention, but nothing in the language enforces it. *price = [100, 200, 300]* is legal in Python.
- **Wrapper types**: `Optional[T]`, `List[T]`, `Iterator[T]`, `Stream<T>`. The wrapper is the type-level distinction; the bare *T* and the wrapped *T* live in different parts of the type lattice.
- **Comprehensions and broadcasting**: `[f(x) for x in xs]` lifts a scalar operation over a collection. NumPy and the APL-family languages let `f(xs)` broadcast natively; most mainstream languages do not.

The reader has to recognise, from the annotation, the variable name, or the surrounding code, which world they are in. The reference itself — the moment of writing the variable's name — does not re-assert the type.

Spanish has had the reference-marks-the-number system natively for centuries. *El precio* and *los precios* are the same noun in two grammatical numbers; the article carries the number, the verb agrees, the adjective agrees. A Spanish-speaker reading or writing the noun phrase commits to scalar-or-collection at the article, and every subsequent word in the clause re-asserts that commitment.

## The Inflexión move

In Inflexión, the article marks the type. *El* (or *la*) binds the name to a scalar value. *Los* (or *las*) binds the name to a collection. The verb, the adjective, and any subsequent reference must agree.

```
El precio es 100.
Los precios son 100, 200, 300.
La suma de los precios es 600.
```

Line one binds *precio* to the scalar 100. The article *el* commits the binding to scalar; the verb *es* (third-person singular of *ser*) agrees. Line two binds *precios* to the collection (100, 200, 300). The article *los* commits the binding to collection; the verb *son* (third-person plural of *ser*) agrees. Line three takes the collection-sum of *los precios* and binds the scalar result to *suma*. The article *la* commits *suma* to scalar; the verb *es* agrees. The collection that the *de los precios* phrase points at remains plural-marked at every reference, but the result of summing it is scalar, and the article and the verb at the binding site mark it that way.

*El precio son 100* is a syntax error — singular article, plural verb. *Los precios es 100* is the same kind of error in the other direction. *La suma de los precios son 600* is also an error — the singular *suma* takes a singular verb, even though the collection it summarises is plural; the verb agrees with its grammatical subject, not with the collection mentioned inside the prepositional phrase.

The reader can see, from the article at the binding site and the verb at the predicate, whether they are looking at a scalar or a collection. There is no separate `List[T]` annotation. There is no need to scan the rest of the function for type hints. The morphology is the type discipline.

Operations on collections broadcast naturally:

```
Los precios son 100, 200, 300.
Los precios_finales son los precios multiplicados por 1.21.
```

The multiplication lifts over the collection because the article and the verb mark *precios* as a collection at every reference, and the resulting *precios_finales* is committed to a collection by *los* and *son* at its own binding site. There is no separate `map`, no comprehension syntax, no broadcasting operator; the article and the verb do the work.

A Spanish-speaking programmer reading these lines does not have to learn a new type system. They already enforce concord in every sentence they speak; Inflexión asks them to let the concord they were already enforcing carry the scalar-versus-collection distinction.

## Why number agreement is the closing piece

The other five mappings are *foreground*. *Ser*/*estar* shows up at the moment you bind a value. Mood shows up at the moment you commit to how a statement is to be evaluated. Aspect shows up at the moment you commit to eager or lazy. Clitics show up at the moment you call a function with multiple arguments. Diminutive and augmentative show up at the moment you scale a number or pick a cheap-versus-thorough variant. Each is a feature you reach for at specific moments.

Number is *everywhere*. Every noun in every clause carries it. Every verb with a subject carries it. Every adjective in a noun phrase carries it. The closing-piece position is not arbitrary — number is the *substrate* on which the other five mappings sit. Each of the previous articles' worked examples used scalars and collections without naming them; the article and the verb did the work in the background. *El contador está en 0* is scalar. *Los precios son 100, 200, 300* is collection. *La suma es el resultado de sumar los precios* is the reduction of a collection to a scalar. The number agreement was load-bearing in every example, in every article, and almost always invisible.

It is also the most quietly enforced. *Ser*/*estar* is the trap English speakers fall into in the first month; mood is the trap they fall into in the second; aspect, clitics, and diminutive each have their own moments of confusion. Number agreement is the one Spanish-speakers obey without ever having been told to obey, and the one English-speakers (after the initial period of remembering verb conjugations) internalise quickly because the rule is straightforward. It is the easiest of the six to use, and the most invisible. That is the closing piece's distinguishing quality: it is the mapping you were already using, in every sentence of every other article in this series.

## What's next

This closes the technical curriculum. The series has now worked through *ser*/*estar*, mood, aspect, clitics, diminutive and augmentative, and number — the six mappings *Inflexión* makes load-bearing for programming semantics, in roughly the order I think they are accessible to a reader new to the language.

From here the work shifts. The runtime that allows *Inflexión* code to actually execute is being built; once it is shipped, the project will have something it has not had so far — *real Inflexión code that runs*. What that opens up — empirical questions about morphological density as a substrate for large language models, comparisons across the lineage of inflection-driven non-English natural-language esoteric programming languages, conversations with the four authors who arrived first — is the next phase of the project, rather than the next article in the series. The series may pause for a while; it may shift register; it may hand off some of its energy to formal-paper revision and to the conversations the formal papers are meant to start. The technical curriculum, at least, is closed.

For now: *El precio es 100. Los precios son 100, 200, 300.* The article and the verb already know what kind of thing they are talking about. The type system is the part that's new.

---

*Inflexión is a hand-built esoteric programming language whose semantics flow from the grammatical features of Rioplatense Argentine Spanish. It is the fifth member of a small lineage of inflection-driven non-English natural-language esoteric programming languages — Perligata (Latin, 2000), Espro (Esperanto, 2015, idea-only), Tampio (Finnish, ~2017), Wenyan (Classical Chinese, 2019), Inflexión (2026) — and the first to use a living Romance language. The full design paper is at roderickc.com/inflexion. The companion methodology paper, on Babel — the runtime that generates esoteric programming languages from parameter sheets — is at roderickc.com/babel.*
