# Three Stances Toward a Statement

> *Fifth article in an RCI LinkedIn series on the impact of language in technology. Builds on the predecessor ([Listening to Spanish Again](/babel/articles/listening-to-spanish)), the series-aperture observation ([What Technical Vocabulary Refuses to Carry](/babel/articles/what-technical-vocabulary-refuses-to-carry)), the lineage-discovery story ([I Thought I Was the First](/babel/articles/i-thought-i-was-the-first)), and the first technical deep-dive ([Two Be-Verbs for Two Kinds of Equals](/babel/articles/two-be-verbs-for-two-kinds-of-equals)). First-person voice; the second of the technical articles. Subject: mood, the most novel of Inflexión's six grammatical-semantic mappings.*

> *Not yet syndicated to LinkedIn.*

There is a flip in Spanish that English speakers fall into within the second month, after they have already learned the *ser*/*estar* trap from the first month. It is the indicative-versus-subjunctive flip on negation.

You want to say *I think he's coming tomorrow*. You confidently produce *Creo que viene mañana*. The Spanish-speaker nods. You then want to say *I don't think he's coming tomorrow*. You confidently produce *No creo que viene mañana* — and the Spanish-speaker either smiles or corrects you. You did not say *I don't think he's coming*. You said something the language registers as ill-formed.

The correct form is *No creo que venga mañana*. The verb shifts from *viene* (indicative — third-person singular present of *venir*, *to come*) to *venga* (subjunctive — the form Spanish uses when the embedded clause is not being asserted as fact). The negation of *creer* — believing — flips the embedded verb's mood. The reason: when you affirm a belief, you are committing to the embedded clause as a fact about the world, and Spanish marks asserted reality with the indicative. When you negate the belief, you are no longer committing; the embedded clause is *not* being asserted; Spanish marks unasserted clauses with the subjunctive. The mood marks your *stance toward what you are saying*, not just the literal content.

English does not do this. *I think he's coming* and *I don't think he's coming* both leave the verb form unchanged. The stance distinction exists in English speakers' heads; it is not encoded in the verb. Spanish encodes it.

This is *Inflexión*'s most novel grammatical-semantic mapping. Spanish has three principal moods — indicative, subjunctive, imperative. Each maps to a different evaluation strategy in the language: indicative is eager evaluation, subjunctive is deferred or reactive evaluation, imperative is side effects. The mood you choose at the verb is the choice the runtime makes about *what to do with the statement*.

## The three moods, quickly

**Indicative** is the mood of asserted reality. *El contador está en 0* — the counter is at 0. *La factorial de cinco es ciento veinte* — the factorial of five is one hundred twenty. *Hoy llueve* — it's raining today. Spanish-speakers use indicative for things they're committing to as true.

**Subjunctive** is the mood of unrealised, hypothetical, desired, doubted, or future-conditioned reality. *Quiero que vengas* — I want you to come (the coming hasn't happened yet). *Cuando termine, te aviso* — when I finish, I'll let you know (the finishing is in the future, not yet asserted). *Ojalá llueva mañana* — would that it rain tomorrow (not asserted; only desired). The subjunctive is the verb form of "this is not yet a fact, but it could be / I want it to be / I am uncertain that it is."

**Imperative** is the mood of commands. *Vení* — come (vos imperative). *Decí "hola"* — say "hello." *Hacé que el contador esté en uno* — make it the case that the counter is at one. The imperative is the verb form of *I am asking the world to change*.

A Spanish-speaker uses these without thinking. They do not stop, halfway through a sentence, to consider whether *que viene* or *que venga* is appropriate; the choice falls out of the relationship between what they are saying and how confident they are about it.

## What programming languages do with this

Mainstream programming languages mostly do not encode the stance distinction. In Python, `result = compute(x)` and `if not condition: result = compute(x)` and `event.subscribe(lambda: compute(x))` and `os.system("compute")` are four different things — eager assignment, conditional assignment, deferred subscription, side effect — and they are encoded with different *vocabulary* (`if`, `lambda`, `os.system`) bolted around the same generic verb `compute`.

The verb itself does not tell you which kind of action it is. The reader has to assemble the stance from the surrounding scaffolding.

Spanish has had the verb-marks-the-stance system natively for centuries.

## The Inflexión move

In Inflexión, the three moods map to three evaluation strategies.

**Indicative** statements are evaluated immediately. *El contador está en 0* binds *contador* to 0 the moment the line executes; *la suma es el resultado de sumar los precios* binds *suma* to the result of the summation, computed now.

**Subjunctive** statements are *deferred*. They are evaluated only when the condition that triggers them becomes true; their resulting state is bound to the realisation of that condition. *Cuando el contador esté en diez, decí "listo"* establishes a deferred binding that will fire when *contador* reaches ten. The subjunctive *esté* signals to the runtime that this statement is not yet committed; it is conditional on the realisation of *cuando el contador esté en diez*. The deferred binding is itself a first-class value — it can be passed to other functions, composed with other deferred bindings, and inspected before it fires.

**Imperative** statements perform side effects: I/O, mutation of mutable bindings, communication with the environment. *Decí "hola"* writes "hola" to standard output. *Hacé que el contador esté en uno* mutates the *contador* cell. The imperative is the verb form a Spanish-speaker uses to ask the world to change, and Inflexión maps it to the language construct that asks the runtime to change.

The reader can see, from the verb form alone, whether a line of Inflexión code is *doing* something now, *promising* something for later, or *commanding* the environment. There is no separate `if`, no separate `await`, no separate `IO` monad, no special syntax marking effects. The mood *is* the marking.

## Why mood is the most novel of Inflexión's mappings

*Ser*/*estar* mapped to immutable/mutable bindings — last article's subject — was the cleanest mapping because Spanish-speakers already use the distinction the way the language asks them to use it. *Mood* is harder. A Spanish-speaker does not normally think of subjunctive as *deferred* — they think of it as *unasserted* or *hypothetical*. The Inflexión mapping asks the reader to make a small conceptual shift: an unasserted clause is, in computational terms, a clause whose evaluation is *deferred until something asserts it*.

The shift is small, but it is real. Other inflection-driven natural-language esoteric programming languages — Perligata, Wenyan, Tampio — engage their substrate languages' grammar without reaching for the mood system this way. Mapping mood to evaluation strategy is the move Inflexión makes that the prior art did not.

If the mapping holds for the reader once they make the shift, they get something they cannot get from any mainstream programming language: a verb form that already encodes its own evaluation stance, available throughout everyday natural-language reading and writing, ready to carry programming semantics without learning a new vocabulary.

## What's coming next

The articles in this series are working through Inflexión's six mappings in order of accessibility. *Ser*/*estar* was the easiest. Mood was harder but conceptually contained. Aspect — perfective versus imperfective on the same verb, mapped to eager versus lazy evaluation — is next, and is in some ways the smallest of the mappings: it asks the reader to make a single morphological choice (*-ó* vs *-aba* on the same verb stem) carry an entire semantic distinction. Then come clitics, which are the most syntactically unusual mapping and need worked examples to land. Then diminutive and augmentative scaling, which are the most playful. Then number agreement, the structural type system that runs through everything.

For now: the next time you write `if`, `await`, or `def fire_when(condition):`, notice that you are reaching for English-keyworded scaffolding to encode a stance that Spanish-speakers have been encoding with verb morphology for centuries. *Indicativo* is your eager assignment. *Subjuntivo* is your deferred subscription. *Imperativo* is your side effect. The scaffolding is the part that's new.

---

*Inflexión is a hand-built esoteric programming language whose semantics flow from the grammatical features of Rioplatense Argentine Spanish. The full design paper is at roderickc.com/inflexion. The companion methodology paper, on Babel — the runtime that generates esoteric programming languages from parameter sheets — is at roderickc.com/babel.*
