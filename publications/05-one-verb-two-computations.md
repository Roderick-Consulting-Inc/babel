# One Verb, Two Computations

> *Sixth article in an RCI LinkedIn series on the impact of language in technology. Builds on the predecessor ([Listening to Spanish Again](/babel/articles/listening-to-spanish)), the series-aperture observation ([What Technical Vocabulary Refuses to Carry](/babel/articles/what-technical-vocabulary-refuses-to-carry)), the lineage-discovery story ([I Thought I Was the First](/babel/articles/i-thought-i-was-the-first)), and the first two technical deep-dives ([Two Be-Verbs for Two Kinds of Equals](/babel/articles/two-be-verbs-for-two-kinds-of-equals) on ser/estar, [Three Stances Toward a Statement](/babel/articles/three-stances-toward-a-statement) on mood). First-person voice; the third of the technical articles. Subject: aspect, the smallest of Inflexión's six grammatical-semantic mappings.*

> *Not yet syndicated to LinkedIn.*

*Cuando llegué, mi madre cocinaba.*

When I arrived, my mother was cooking.

That single Spanish sentence does in seven words what English needs nine to do, and the difference is concentrated in the two verbs. *Llegué* is the preterite of *llegar* — to arrive. The arrival is a *point event*: completed, located at a specific moment, viewed as a whole. *Cocinaba* is the imperfect of *cocinar* — to cook. The cooking is an *ongoing process*: in progress at the time of the arrival, viewed in its duration rather than as a closed event. English needs the auxiliary verb *was* and the present participle *cooking* to convey what Spanish does with a single morpheme on the verb stem.

This is *aspect*, the third of *Inflexión*'s technical mappings and the smallest of the six. The grammatical distinction Spanish marks — perfective versus imperfective in the past tense — maps directly to a programming distinction English-keyworded languages have to assemble from separate keywords: *eager versus lazy evaluation*.

## The two aspects, quickly

Spanish marks aspect in the past tense by choosing between two morphologically distinct forms of the same verb. The choice is not optional and the choice is not arbitrary. The two aspects encode different ways of seeing the same event.

**Preterite (perfective).** Marks an action viewed as a complete, bounded whole. *Comió* — he ate (the meal is over, the eating happened, the event is closed). *Sumó los precios* — summed the prices (the summation ran to completion, here is the result). *Calculó la suma* — calculated the sum (one shot, finished, done). The perfective is the aspect of "this happened, returns a value, is now in the past."

**Imperfect (imperfective).** Marks an action viewed as ongoing, habitual, or unbounded. *Comía* — he was eating, or he used to eat (the eating was in progress, or it was something he did regularly; the action is open, unfinished, characterised by its duration rather than by its completion). *Sumaba los precios* — was summing the prices, or used to sum the prices. *Calculaba la suma* — was calculating the sum.

The perfective and imperfective use the same verb stem — *com-*, *sum-*, *calcul-*. The difference between them is one or two morphemes on the suffix. *Calculó* is six letters; *calculaba* is nine; the eight letters they share are identical. The whole semantic distinction rides on what's at the end.

## What programming languages do with this

Mainstream programming languages encode the eager/lazy distinction with separate vocabulary, often very different vocabulary, around the same operation. *sum(prices)* returns a number; *running_sum(prices)* returns a generator. *map(f, xs)* in Python 2 returned a list; in Python 3 it returns an iterator, and the change of language version changed the aspect of the same word. *result = compute(x)* is eager; *future = compute_async(x)* with an *await* later is lazy; the verbs are named differently to signal the difference.

The reader has to recognise which world they are in from the surrounding scaffolding — the keyword, the import, the type annotation, the function name. The verb itself does not carry the choice.

Spanish has had the verb-marks-the-aspect system natively for centuries. *Cocinó* and *cocinaba* are the same verb in two aspects. So are *sumó* and *sumaba*. So are *calculó* and *calculaba*. A Spanish-speaker reading or writing the verb commits to an aspect with the morpheme; the choice is not a separate concern.

## The Inflexión move

In Inflexión, the perfective form requests eager evaluation. The imperfective form requests lazy evaluation. Same operation, different aspect, different runtime behavior.

```
Sumó los precios.
```

This is the perfective: the runtime computes the sum to completion, the value is the result, the operation returns and is done.

```
Sumaba los precios.
```

This is the imperfective: the runtime returns a stream of partial sums, the consumer pulls them as it needs them, the operation has no inherent endpoint until the consumer stops asking.

Same verb stem, *sum-*. Same arguments, *los precios*. Two morphemes of difference (*-ó* vs *-aba*) carry the entire eager-versus-lazy semantic distinction. There is no separate `lazy` keyword, no `Generator` type annotation, no `Stream<T>` wrapper. The morphology is the choice.

The bare-infinitive shortcut documented in the design paper — *sumar los precios* — defaults to perfective (eager) when the aspect choice does not need to be marked. The explicit forms come out when the choice is the point.

## Why aspect is the smallest of the six mappings

The other five mappings ask the reader to learn a new structural feature of the language: number agreement runs through articles and verbs in lockstep; mood encodes evaluation stance; *ser*/*estar* commits binding to mutability; clitics route arguments by position; diminutive suffixes scale numerics. Each is a system the reader has to internalise.

Aspect is *one morphological choice on a verb you were already going to write*. *-ó* or *-aba*. *-ió* or *-ía*. Two letters or three, one decision, the entire eager-versus-lazy semantic delivered.

It is also the most consistent with how Spanish-speakers already use the distinction. A Spanish-speaker writing *cocinaba* and *cocinó* in the same paragraph already commits to two different temporal framings of the same act. Asking them to commit to two different evaluation strategies of the same call is the same kind of move, in the same morphological space, with the same conceptual distance from baseline. The mapping is, in that sense, the cheapest of the six — it asks the reader to do almost nothing they were not already doing.

## What's coming next

The remaining mappings are the more syntactically novel ones. *Clitic ordering* — the fixed Spanish sequence *se-te-me-lo-le* used as positional argument routing — is the most unusual of the six and gets its own piece next. *Diminutive and augmentative scaling* is the most playful and gets a piece after that. *Number agreement* — the article-and-verb agreement on singular versus plural that maps to scalar versus collection — runs through everything and probably gets a piece that interleaves with the others.

For now: *Cuando llegué, mi madre cocinaba*. The arrival is eager; the cooking is lazy. The verbs already know.

---

*Inflexión is a hand-built esoteric programming language whose semantics flow from the grammatical features of Rioplatense Argentine Spanish. The full design paper is at roderickc.com/inflexion. The companion methodology paper, on Babel — the runtime that generates esoteric programming languages from parameter sheets — is at roderickc.com/babel.*
