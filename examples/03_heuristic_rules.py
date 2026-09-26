"""Example — what the zero-dependency heuristic tagger can do.

The dummy engine has no model: it reads punctuation, numbers, a closed-class
word table, suffix morphology and capitalization. These Portuguese words each
trigger a different rule.

Run::

    python examples/03_heuristic_rules.py
"""
from tugatagger import TugaTagger


def main() -> None:
    words = [
        "rapidamente",  # -mente  -> ADV
        "cantando",     # -ando   -> VERB
        "amar",         # -ar     -> VERB
        "ação",         # -ção    -> NOUN
        "cidade",       # -dade   -> NOUN
        "formoso",      # -oso    -> ADJ
        "nacional",     # -al     -> ADJ
        "Lisboa",       # Title   -> PROPN
        "de",           # closed  -> ADP
        "mas",          # closed  -> CCONJ
        "42",           # digits  -> NUM
        "?!",           # symbols -> PUNCT
    ]
    # tag_dummy is a classmethod: callable without an instance.
    tagged = TugaTagger.tag_dummy(" ".join(words))
    for word, pos in tagged:
        print(f"  {word:14} -> {pos}")


if __name__ == "__main__":
    main()
