"""Example — compare every installed engine on the same sentence, aligned.

The shared (token, tag) contract makes engine comparison a simple loop: tag
once per backend, then line the tags up token by token to see where the
context-aware engines disagree with the heuristic.

Run::

    python examples/05_benchmark_engines.py
"""
from tugatagger import TugaTagger

SENTENCE = "O gato preto pulou o muro."


def main() -> None:
    results = {}
    for engine in ("dummy", "lexicon", "brill", "spacy"):
        try:
            results[engine] = TugaTagger(engine=engine).tag(SENTENCE)
        except Exception:
            pass  # backend extra not installed here

    if not results:
        print("no backends available")
        return

    # Use the engine with the most tokens as the row index.
    rows = max(results.values(), key=len)
    header = "token".ljust(12) + "".join(e.ljust(10) for e in results)
    print(header)
    print("-" * len(header))
    for i, (token, _) in enumerate(rows):
        line = token.ljust(12)
        for tags in results.values():
            tag = tags[i][1] if i < len(tags) else ""
            line += tag.ljust(10)
        print(line)


if __name__ == "__main__":
    main()
