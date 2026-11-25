# Quickstart

TugaTagger gives you one Portuguese part-of-speech tagger interface, `TugaTagger`, over several swappable backends. You always call the same `tag()` method and get back the same shape, no matter which engine does the work.

## 1. Install

```bash
pip install tugatagger              # core: the heuristic "dummy" engine only
pip install tugatagger[brill]       # + brill_postaggers backend
pip install tugatagger[lexicon]     # + tugalex dictionary backend
pip install tugatagger[spacy]       # + spaCy; then download a model:
python -m spacy download pt_core_news_lg
```

The core install has no NLP dependencies and always works. It ships a rule-based fallback tagger. Install an extra only for the backend you want.

## 2. The one thing to understand

You configure a `TugaTagger` with an `engine` at construction time. Every call to `tag(sentence)` returns a `List[Tuple[str, str]]`, a list of `(token, POS_tag)` pairs:

```python
from tugatagger import TugaTagger

tagger = TugaTagger(engine="dummy")
tags = tagger.tag("O gato preto pulou o muro.")
for word, pos in tags:
    print(f"{word:12} -> {pos}")
```

```
O            -> DET
gato         -> NOUN
preto        -> NOUN
pulou        -> NOUN
o            -> DET
muro.        -> PUNCT
```

The tags follow the [Universal POS tags](https://universaldependencies.org/u/pos/) scheme:
`DET`, `NOUN`, `VERB`, `ADJ`, `ADV`, `ADP`, `PRON`, `AUX`, `PROPN`, `NUM`,
`PUNCT`, `CCONJ`, `SCONJ`.

## 3. Pick an engine

One setting, `engine`, takes five values. Each value selects a backend that fills in the same `(token, tag)` contract.

```python
TugaTagger(engine="auto")      # default: best available backend, with fallback
TugaTagger(engine="brill")     # transformation-based learning tagger
TugaTagger(engine="spacy")     # pt_core_news_lg statistical model
TugaTagger(engine="lexicon")   # tugalex dictionary lookup
TugaTagger(engine="dummy")     # rule-based heuristic, no dependencies
```

`auto` tries `brill`, then `spacy`, then `lexicon`, and falls back to `dummy` if none of them load. The same code runs whether or not the heavy backends are installed. You get better tags when they are installed.

See [api.md](api.md) for what each engine returns and [advanced.md](advanced.md) for how to choose between them.

## 4. First real call

If you have the Brill backend installed, it disambiguates by context where the heuristic cannot:

```python
from tugatagger import TugaTagger

tagger = TugaTagger(engine="brill")
print(tagger.tag("O gato preto pulou o muro."))
# [('O', 'DET'), ('gato', 'NOUN'), ('preto', 'ADJ'),
#  ('pulou', 'VERB'), ('o', 'DET'), ('muro', 'NOUN'), ('.', 'PUNCT')]
```

If no backend is installed, the `dummy` engine proves the plumbing with no setup:

```python
print(TugaTagger(engine="dummy").tag("Ela correu rapidamente."))
# [('Ela', 'PROPN'), ('correu', 'NOUN'), ('rapidamente.', 'PUNCT')]
```

---
[Home](../README.md) · [API reference →](api.md)
