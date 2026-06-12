# TugaTagger 🇵🇹

**TugaTagger** is a unified, lightweight wrapper for Portuguese Part-of-Speech (POS) tagging. It provides a standardized interface to swap between different NLP backends, making it ideal for benchmarking different approaches or maintaining consistency across multiple microservices and repositories.

---

## 🚀 Key Features

* **Unified API:** Use the same `tag()` method regardless of the underlying engine.
* **Multiple Backends:** Supports **spaCy**, **Stanza** (neural), **Brill-style** taggers, and **Lexicon-based** lookups.
* **Robust Fallback ("Auto" Mode):** Automatically tries the best available engine, falling back to heuristic-based "guessing" if dependencies are missing.
* **Zero-Dependency Mode:** Includes a built-in rule-based tagger for environments where installing heavy NLP models isn't feasible.

---

## 📦 Installation

*(Note: Install the backends you intend to use)*

```bash
pip install tugatagger[brill]

# To use spaCy
pip install tugatagger[spacy]
python -m spacy download pt_core_news_lg

# To use Stanza (neural; downloads the pt models on first run)
pip install tugatagger[stanza]
```

---

## 🛠 Usage

### Quick Start

The `auto` engine is the default. It attempts to use spaCy or Brill first and falls back to a heuristic "dummy" tagger if they aren't installed.

```python
from tugatagger import TugaTagger

tagger = TugaTagger(engine="auto")
text = "O gato preto pulou o muro."

tags = tagger.tag(text)
for word, pos in tags:
    print(f"{word} -> {pos}")

```

### Choosing a Specific Engine

You can force a specific backend for benchmarking or production stability.

| Engine | Description                                    | Best For...                                |
| --- |------------------------------------------------|--------------------------------------------|
| `spacy` | Uses `pt_core_news_lg` (or your choice).       | High accuracy & context awareness.         |
| `stanza` | Stanford neural pipeline (downloads pt models). | Highest accuracy; heavier & slower.        |
| `brill` | Transformation-based learning tagger.          | Fast performance with good accuracy.       |
| `lexicon` | Dictionary lookup from `tugalex`.              | word-lookup tagging.                       |
| `dummy` | Heuristics based on suffixes and common words. | Low-resource / No-dependency environments. |

```python
# Force spaCy with a specific model
tagger = TugaTagger(engine="spacy", spacy_model="pt_core_news_sm")

```

---

## 🧠 How the Heuristic Tagger Works

When using `engine="dummy"` or as a final fallback, TugaTagger uses a multi-stage guessing logic:

1. **Punctuation/Numbers:** Identifies `PUNCT` and `NUM`.
2. **Closed-class Lookups:** Identifies common Portuguese functional words (e.g., "o", "de", "com", "mas").
3. **Suffix Morphology:** Analyzes word endings (e.g., `-mente` → `ADV`, `-ar/-er/-ir` → `VERB`, `-ção` → `NOUN`).
4. **Capitalization:** Heuristic for `PROPN` (Proper Nouns).
5. **Default:** Falls back to `NOUN`.

---

## 🤝 Contributing

If you'd like to add a new engine (e.g., Stanza or NLTK):

1. Add a `tag_newengine` method to the `TugaTagger` class.
2. Update the `engines` dictionary in the `tag()` method.
3. Add the corresponding loading logic in `__init__`.

