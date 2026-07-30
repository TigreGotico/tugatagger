"""Example — use the tags: pull nouns and verbs out of a sentence.

A typical downstream task: keep only the content words. The (token, tag)
output drops straight into a list comprehension.

Run::

    python examples/06_pos_filter.py
"""
from collections import Counter

from tugatagger import TugaTagger

TEXT = "O jogador correu rapidamente e marcou um golo na final."


def main() -> None:
    tagger = TugaTagger(engine="auto")
    tagged = tagger.tag(TEXT)

    nouns = [w for w, pos in tagged if pos == "NOUN"]
    verbs = [w for w, pos in tagged if pos == "VERB"]

    print("text :", TEXT)
    print("nouns:", nouns)
    print("verbs:", verbs)

    counts = Counter(pos for _, pos in tagged)
    print("tag counts:", dict(counts))


if __name__ == "__main__":
    main()
