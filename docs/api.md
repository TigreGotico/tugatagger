# API reference

Everything lives in one class, `TugaTagger`, importable from the package root.

```python
from tugatagger import TugaTagger
```

## `TugaTagger(engine="auto", spacy_model="pt_core_news_lg")`

Construct a tagger bound to a backend.

| Parameter | Type | Default | Meaning |
|---|---|---|---|
| `engine` | `str` | `"auto"` | One of `"auto"`, `"brill"`, `"spacy"`, `"lexicon"`, `"dummy"`. |
| `spacy_model` | `str` | `"pt_core_news_lg"` | spaCy model name, used only when the spaCy backend loads. |

The constructor eagerly loads the backend implied by `engine`:

- `engine="spacy"` loads spaCy in **strict** mode (load failure raises).
- `engine="brill"` loads Brill in strict mode.
- `engine="lexicon"` loads tugalex in strict mode.
- `engine="auto"` loads spaCy, Brill, and tugalex in **non-strict** mode.
  Whichever import succeeds is kept; failures are swallowed.
- `engine="dummy"` loads nothing.

```python
TugaTagger()                              # auto
TugaTagger(engine="brill")
TugaTagger(engine="spacy", spacy_model="pt_core_news_sm")
```

## `tag(sentence: str) -> List[Tuple[str, str]]`

Tag a sentence with the configured engine. Returns a list of `(token, POS_tag)` tuples. Raises `ValueError` if `engine` is not one of the five known names.

```python
tagger = TugaTagger(engine="dummy")
tagger.tag("Lisboa é bonita.")
# [('Lisboa', 'PROPN'), ('é', 'AUX'), ('bonita.', 'PUNCT')]
```

`tag()` dispatches to the per-engine method matching `self.engine`. Those methods are also public. Call them directly to mix engines on one instance.

## Per-engine methods

Each method returns the same `List[Tuple[str, str]]` shape.

### `tag_auto(sentence)`

Tries `tag_brill`, then `tag_spacy`, then `tag_lexicon`, and returns the first result that succeeds. If all three raise, it returns `tag_dummy(sentence)`. Backend exceptions are caught silently, so this method never fails on a missing dependency.

### `tag_brill(sentence)`

Tags with the Brill transformation-based tagger. Loads the `pt` model on first use if not already loaded (strict). Requires the `brill` extra.

### `tag_spacy(sentence)`

Tags with the spaCy model, returning `(token.text, token.pos_)` per token. The model loads with `disable=["ner", "parser"]`. Requires the `spacy` extra and a downloaded model.

### `tag_lexicon(sentence)`

Lowercases and whitespace-tokenizes the sentence, splitting trailing `.`, `!`, `?` into their own tokens, then looks each token up in the tugalex lexicon. Known tokens get their first listed tag. Unknown tokens fall back to the heuristic `_guess_pos`. Requires the `lexicon` extra.

### `tag_dummy(sentence)` — classmethod

Whitespace-tokenizes the sentence and tags each token with the heuristic `_guess_pos`. This method has no dependencies. Because it is a `classmethod`, you can call it without an instance:

```python
TugaTagger.tag_dummy("Ela canta bem.")
# [('Ela', 'PROPN'), ('canta', 'NOUN'), ('bem.', 'PUNCT')]
```

## Loader methods

Call these methods to reload a backend after construction, for example to swap the spaCy model. Each accepts `strict`. `True` re-raises load errors. `False` leaves the backend unloaded on failure.

| Method | Signature |
|---|---|
| `load_spacy` | `load_spacy(spacy_model="pt_core_news_lg", strict=True)` |
| `load_brill` | `load_brill(strict=True)` |
| `load_lexicon` | `load_lexicon(strict=True)` |

```python
tagger = TugaTagger(engine="spacy")
tagger.load_spacy("pt_core_news_sm")     # swap to the small model
```

## The tag set

Tags follow the Universal POS scheme. The heuristic and lexicon backends emit:

`ADJ` `ADP` `ADV` `AUX` `CCONJ` `DET` `NOUN` `NUM` `PRON` `PROPN` `PUNCT`
`SCONJ` `VERB`

The spaCy and Brill backends emit whatever tag set their model was trained on. For the standard Portuguese models, this is also Universal POS.

---
[← Quickstart](quickstart.md) · [Home](../README.md) · [Advanced →](advanced.md)
