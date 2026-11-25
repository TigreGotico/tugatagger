"""Example — the core idea: one tagger, one call, (token, tag) pairs.

Run::

    python examples/01_quickstart.py
"""
from tugatagger import TugaTagger


def main() -> None:
    tagger = TugaTagger(engine="dummy")  # zero-dependency engine
    sentence = "O gato preto pulou o muro."

    tags = tagger.tag(sentence)
    print(f"engine: {tagger.engine}")
    for word, pos in tags:
        print(f"  {word:12} -> {pos}")


if __name__ == "__main__":
    main()
