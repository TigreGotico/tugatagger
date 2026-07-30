# TugaTagger

TugaTagger is a wrapper for Portuguese part-of-speech (POS) tagging. It gives you one interface over several backends, so you can swap engines without changing your code. Use it to benchmark different tagging approaches or to keep tagging consistent across multiple services.

## Features

- One `tag()` method works the same way regardless of the backend.
- Supports spaCy, Stanza (neural), a Brill-style tagger, and a lexicon lookup.
- The `auto` engine tries the best available backend first, then falls back to a heuristic tagger if no backend is installed.
- The heuristic tagger has no dependencies, so it always works, even with no NLP models installed.

## Installation

Install the backend you plan to use.

```bash
pip install tugatagger[brill]

# To use spaCy
pip install tugatagger[spacy]
python -m spacy download pt_core_news_lg

# To use Stanza (neural; downloads the pt models on first run)
pip install tugatagger[stanza]
```

## Usage

### Quick start

The `auto` engine is the default. It tries spaCy or Brill first, then falls back to a heuristic tagger if neither is installed.

```python
from tugatagger import TugaTagger

tagger = TugaTagger(engine="auto")
text = "O gato preto pulou o muro."

tags = tagger.tag(text)
for word, pos in tags:
    print(f"{word} -> {pos}")

```

### Choosing a specific engine

Force a specific backend for benchmarking or for production stability.

| Engine | Description                                    | Best for...                                |
| --- |------------------------------------------------|--------------------------------------------|
| `spacy` | Uses `pt_core_news_lg` (or your choice).       | High accuracy and context awareness.       |
| `stanza` | Stanford neural pipeline (downloads pt models). | Highest accuracy; heavier and slower.      |
| `brill` | Transformation-based learning tagger.          | Fast performance with good accuracy.       |
| `lexicon` | Dictionary lookup from `tugalex`.              | Word-lookup tagging.                       |
| `dummy` | Heuristics based on suffixes and common words. | Low-resource or no-dependency environments. |

```python
# Force spaCy with a specific model
tagger = TugaTagger(engine="spacy", spacy_model="pt_core_news_sm")

```

## How the heuristic tagger works

When you use `engine="dummy"`, or when a backend falls back to it, TugaTagger applies a multi-stage guessing rule:

1. Identify punctuation (`PUNCT`) and numbers (`NUM`).
2. Look up common Portuguese functional words (for example, "o", "de", "com", "mas").
3. Analyze word endings (for example, `-mente` maps to `ADV`, `-ar`/`-er`/`-ir` maps to `VERB`, `-ção` maps to `NOUN`).
4. Tag capitalized words as `PROPN` (proper nouns).
5. Tag anything left over as `NOUN`.

## Related projects

- [tugalex](https://github.com/TigreGotico/tugalex) — the Portuguese lexicon used by the `lexicon` backend.
- [tugamorph](https://github.com/TigreGotico/tugamorph) — Portuguese morphological analysis, an optional extra.

## Contributing

To add a new engine (for example, Stanza or NLTK):

1. Add a `tag_newengine` method to the `TugaTagger` class.
2. Update the `engines` dictionary in the `tag()` method.
3. Add the matching loading logic in `__init__`.

## License

MIT.
