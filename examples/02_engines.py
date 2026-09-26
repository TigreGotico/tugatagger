"""Example — the five engines, all behind the same tag() interface.

Each engine is a swappable backend. Some need optional extras; this script
loads whichever are installed and skips the rest gracefully.

Run::

    python examples/02_engines.py
"""
from tugatagger import TugaTagger

SENTENCE = "O gato preto pulou o muro."


def main() -> None:
    for engine in ("dummy", "lexicon", "brill", "spacy", "auto"):
        try:
            tagger = TugaTagger(engine=engine)
            tags = tagger.tag(SENTENCE)
            print(f"{engine:8} {tags}")
        except Exception as err:
            print(f"{engine:8} (unavailable: {type(err).__name__})")


if __name__ == "__main__":
    main()
