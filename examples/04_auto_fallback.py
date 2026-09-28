"""Example — the 'auto' engine always returns tags, installed or not.

auto tries brill -> spacy -> lexicon and falls back to the heuristic dummy
tagger if none load, so the same code runs in every environment.

Run::

    python examples/04_auto_fallback.py
"""
from tugatagger import TugaTagger

SENTENCES = [
    "Eu comprei pão na padaria.",
    "Ela canta muito bem.",
    "Os carros vermelhos passaram rapidamente.",
]


def main() -> None:
    tagger = TugaTagger(engine="auto")
    for sentence in SENTENCES:
        print(sentence)
        for word, pos in tagger.tag(sentence):
            print(f"  {word:14} -> {pos}")
        print()


if __name__ == "__main__":
    main()
