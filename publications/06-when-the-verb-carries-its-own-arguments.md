# When the Verb Carries Its Own Arguments

> *Seventh article in an RCI LinkedIn series on the impact of language in technology. Builds on the predecessor ([Listening to Spanish Again](/babel/articles/listening-to-spanish)), the series-aperture observation ([What Technical Vocabulary Refuses to Carry](/babel/articles/what-technical-vocabulary-refuses-to-carry)), the lineage-discovery story ([I Thought I Was the First](/babel/articles/i-thought-i-was-the-first)), and the three technical deep-dives so far ([Two Be-Verbs for Two Kinds of Equals](/babel/articles/two-be-verbs-for-two-kinds-of-equals) on ser/estar, [Three Stances Toward a Statement](/babel/articles/three-stances-toward-a-statement) on mood, [One Verb, Two Computations](/babel/articles/one-verb-two-computations) on aspect). First-person voice; the fourth of the technical articles. Subject: clitics, the most syntactically novel of Inflexión's six grammatical-semantic mappings.*

> *Not yet syndicated to LinkedIn.*

*Dámelo.*

That is one word in Spanish. The translation is four words in English: *give it to me*. The four English words can be reordered in conversational ways (*give me it* — a little awkward but legal; *to me, give it* — poetic, almost ungrammatical). The Spanish word cannot be reordered in any conversational way. *Lome dá* and *medálo* and *lomedá* are not Spanish; they are typing errors.

The Spanish word *dámelo* is the vos imperative *dá* (from *dar*, "to give") with two object pronouns attached as enclitics: the indirect-object clitic *me* (the recipient), and the direct-object clitic *lo* (the thing). The order is fixed by the grammar: indirect before direct. Substitute the indirect: *dáselo* (*se* replaces *me*, signalling a third-person recipient instead of first-person — "give it to him/her/them"). Substitute again: *dámela* (*la* replaces *lo*, signalling a feminine direct object instead of a masculine one — "give it [feminine] to me"). The morphology of the call IS the structure of the call. The verb carries its own arguments, in a strictly determined order.

This is *Inflexión*'s most syntactically novel mapping — the one with the smallest English-language analogue and the largest payoff if the reader can see what is going on.

## The fixed Spanish clitic order

Spanish object pronouns attach to a verb in a *grammaticalised* sequence. When multiple clitics co-occur, they appear in this order — and only this order:

> *se* before *te* (second person) before *me* (first person) before *lo / la / le / los / las / les* (third person).

Within third person, indirect (*le/les*) comes before direct (*lo/la/los/las*) — except that *le/les* before *lo/la/los/las* triggers a phonological rule that turns *le* into *se* (the *"se-by-le"* rule that Spanish-speakers internalise without naming it). That is why *give it to him* is *dáselo* and not *dálelo*: the *le* that would otherwise appear becomes *se* when followed by *lo*.

The order is not negotiable. *Lome dá* is not a stylistic choice; it is not Spanish. The discipline runs through every speech act in the language — *me lo dio*, *te la mandé*, *se me cayó* — and Spanish-speakers obey it without thinking, the way English-speakers obey *the* before the noun rather than after.

## What programming languages do with arguments

Mainstream programming languages route function arguments by *position* (the order in which they appear at the call site, matched to the order they appear in the function signature) or by *keyword* (`f(name="x", value=5)` — the argument label is in the call). Both work; neither is grammaticalised. Position is just *whatever order the function-definition author wrote*; keyword is just *whatever names the function-definition author chose*. The discipline is enforced by the language's parser, not by an underlying grammar that speakers internalise from infancy.

There is a small adjacent thing in some languages — *currying*, in functional languages, where applying a function to fewer arguments returns a partially-applied version of the function. *Dámelo* and *dáselo* are something like applying *dar* to a sequence of clitics one at a time: each clitic added is one slot filled. But mainstream currying does not have *positional ordering enforced by the language's grammar*; it just goes left-to-right through the formal parameters in whatever order the function was defined.

Spanish has the morphological argument-routing system natively, by virtue of having clitics. Most programming languages do not.

## The Inflexión move

In *Inflexión*, the clitic stack on a verb specifies the routing of arguments through a function call. The verb names the operation; the clitics, in their fixed Spanish order, fill the positional slots of the function in the order Spanish grammaticalises.

The white paper's worked example is a banking transfer:

```
La función transferir, que toma una cuenta_origen, una cuenta_destino y un monto, es ...
Transferíselo.
```

The function *transferir* is defined with three named arguments: *cuenta_origen* (source account), *cuenta_destino* (destination account), *monto* (amount). The call *Transferíselo* is the vos imperative *transferí* (from *transferir*) with two clitics attached, in the fixed Spanish order *se-lo*: *se* is the third-person indirect-object clitic ("to him/her/them"); *lo* is the third-person direct-object clitic ("it"). The argument routing is *positional*, but positional in the *Spanish-grammaticalised* sense: *lo* (the direct object) maps to the direct-object slot of *transferir* — the *monto*, the amount; *se* (the indirect object) maps to the indirect-object slot — the *cuenta_destino*, the destination. The remaining argument (*cuenta_origen*) is bound from context.

A Spanish-speaker reading *Transferíselo* in code does not have to consult a function signature to know what got routed where. The clitic positions encoded the routing; the routing follows the grammar the speaker has been using since childhood.

A non-Spanish-speaker reading the same code is at the largest disadvantage of any of Inflexión's six mappings. The clitic system is the part of the language with the smallest English equivalent. The article you are reading is, frankly, the hardest of this series for the non-Spanish-speaking LinkedIn reader to feel.

## Why this is the most syntactically novel mapping

The other five mappings have analogies. Number agreement maps to scalar versus collection — programmers know lists and scalars. Mood maps to evaluation strategy — programmers know eager, deferred, and effectful. Aspect maps to eager versus lazy — programmers know `map` versus `imap`. Diminutive scaling maps to numeric and cost annotation — programmers know cheap-fast versus expensive-thorough variants of the same operation. *Ser* / *estar* maps to immutable versus mutable — programmers know `const` and `let`.

Clitic ordering does not have the same kind of analogy. Programmers know positional arguments and keyword arguments, but neither captures what clitic morphology does — clitics route arguments *by their grammatical category* (person × role), in *fixed Spanish order*, *attached to the verb itself as part of one phonological word*. This is closer to how some natural languages encode case (Latin, Finnish, Russian) than to how any mainstream programming language encodes argument-passing.

For a Spanish-speaker, this is the easiest of the six mappings to use — the rules are completely automatic. For a non-Spanish-speaker, it is the hardest of the six mappings to learn — the rules are unfamiliar at the syntactic level. Inflexión is, in that sense, *more accessible to its substrate language's native speakers* than to its potential international audience, in this one specific place. That is a feature of the design (the language is meant to read as Spanish) rather than a defect; it is also a fact worth being honest about.

A future installment will address the further dimension of *clitic placement* — whether the clitics appear *before* the verb (proclitic: *me lo dio* — *he gave it to me*) or *after* it (enclitic: *dándomelo*, *dármelo*, *dámelo* — same meanings, different positions). The current mapping covers ordering; placement carries syntactic meaning the current mapping flattens, and a future revision will address it as a separate semantic dimension.

## What's coming next

Two technical articles remain in the immediate plan: *diminutive and augmentative scaling* (the most playful of the six, where the cultural register of *cinquito* and *buscazo* meets numeric and computational scaling), and *number agreement* (the structural type system that runs through articles, nouns, adjectives, and verbs in lockstep, and maps to scalar versus collection).

After the six mapping articles, the series turns to the empirical question hinted at in the formal paper: whether a programming language whose surface syntax is morphologically denser than English actually gives large language models a cleaner substrate to work with. That is a question for a separate article — and a separate experiment — once the runtime exists and there is real Inflexión code for an LLM to read.

For now: *Dámelo*. Three morphemes; one phonological word; one function call; argument routing the verb itself carries.

---

*Inflexión is a hand-built esoteric programming language whose semantics flow from the grammatical features of Rioplatense Argentine Spanish. The full design paper is at roderickc.com/inflexion. The companion methodology paper, on Babel — the runtime that generates esoteric programming languages from parameter sheets — is at roderickc.com/babel.*
