# Advanced

## Choosing an engine

All four real backends satisfy the same `(token, tag)` contract, so the choice is about accuracy, speed, and what you can install.

| Engine | Dependency | Context-aware | Notes |
|---|---|---|---|
| `spacy` | `spacy` + model | yes | Highest accuracy. Heaviest install. |
| `brill` | `brill_postaggers` | yes | Fast, good accuracy, small footprint. |
| `lexicon` | `tugalex` | no | Dictionary lookup. First listed tag wins. |
| `dummy` | none | no | Heuristic rules. Always available. |
| `auto` | any of the above | depends | Best installed backend, dummy as floor. |

The same input shows the differences. `preto` is an adjective and `pulou` a verb, but only the context-aware backends recover that:

```python
from tugatagger import TugaTagger

s = "O gato preto pulou o muro."
print(TugaTagger(engine="dummy").tag(s))
# ('preto', 'NOUN') ('pulou', 'NOUN')   <- heuristic can't disambiguate
print(TugaTagger(engine="brill").tag(s))
# ('preto', 'ADJ')  ('pulou', 'VERB')   <- context resolves it
```

## How `auto` falls back

`auto` loads spaCy, Brill, and tugalex non-strictly at construction. At tag time it tries `brill`, then `spacy`, then `lexicon`, then `dummy`, and returns the first result that does not raise. One code path runs in every environment:

```python
tagger = TugaTagger()                 # engine="auto"
tagger.tag("Ela correu rapidamente") # brill if installed, else dummy
```

If you need to know which backend produced the tags, call the engine methods explicitly instead of relying on `auto`.

## The heuristic tagger

The `dummy` engine, the `auto` floor, and the lexicon's unknown-word path all run `_guess_pos`, a context-free rule cascade applied per token:

1. **Punctuation.** A token that is not alphanumeric is `PUNCT`.
2. **Numbers.** An all-digit token is `NUM`.
3. **Closed-class table.** A small dictionary of functional words (articles, prepositions, conjunctions, pronouns, copulas, common adverbs) covers common cases:
   `o/a/os/as` maps to `DET`, `de/em/com/para` maps to `ADP`, `e/mas/ou` maps to `CCONJ`,
   `que/se` maps to `SCONJ`, `eu/ele/ela` maps to `PRON`, `é/foi/ser/ter` maps to `AUX`,
   `não/sim/muito/mais` maps to `ADV`.
4. **Suffix morphology.** Word endings apply, longest first.
   `-mente` maps to `ADV`. `-ando/-endo/-indo`, `-aram/-eram/-iram`, `-ava`,
   `-ria`, `-ar/-er/-ir` map to `VERB`. `-ção/-são/-dade/-ismo/-ista/-dor`
   maps to `NOUN`. `-oso/-osa/-vel/-al` maps to `ADJ`. A suffix only fires if the word is longer than the suffix, so short words like `lar` are not misread.
5. **Capitalization.** A title-case token (`Lisboa`) is `PROPN`.
6. **Fallback.** Anything left over is `NOUN`.

Because the heuristic is context-free, it tags the first word of a sentence as `PROPN` whenever it is capitalized. `O` is in the closed-class table and escapes this, but `Ela` does not. This is expected for a zero-dependency fallback. Use `brill` or `spacy` when you need sentence context.

## The lexicon backend

`tag_lexicon` lowercases the sentence, splits trailing `.`, `!`, `?` into their own tokens, and looks each token up in `tugalex`. The lexicon stores *all* possible tags for a word. This backend takes the **first** one, with no disambiguation:

```python
import tugalex
lex = tugalex.TugaLexicon()
print(lex.possible_postags["o"])   # ['DET', 'PRON']  -> backend picks 'DET'
```

Words absent from the lexicon fall through to `_guess_pos`, so the lexicon backend degrades gracefully on out-of-vocabulary tokens.

## Benchmarking across engines

The shared interface makes engine comparison a loop. Build each tagger you can load, run them on the same sentence, and line up the tags:

```python
from tugatagger import TugaTagger

sentence = "O gato preto pulou o muro."
results = {}
for engine in ("dummy", "lexicon", "brill", "spacy"):
    try:
        results[engine] = TugaTagger(engine=engine).tag(sentence)
    except Exception:
        pass  # backend not installed in this environment

for engine, tags in results.items():
    print(engine, tags)
```

See [examples/05_benchmark_engines.py](../examples/05_benchmark_engines.py) for a runnable version that aligns the columns.

## Adding a backend

To wire in a new tagger (for example, NLTK or Stanza):

1. Add a `tag_<name>` method that returns `List[Tuple[str, str]]`.
2. Add a `load_<name>(strict=True)` loader and call it from `__init__` for the matching `engine` value (and from `auto` non-strictly).
3. Register `tag_<name>` in the `engines` dict inside `tag()`.

---
[← API reference](api.md) · [Home](../README.md)
