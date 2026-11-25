"""Value assertions for the default ('auto') engine.

The rest of the suite asserts structure only: a method exists, a bad engine
name raises. The one test that tags text needs the 'stanza' extra, which CI
does not install, so it is skipped on every interpreter. These tests need no
extra, so the CI green covers tagging.

The expected values below are the current answers, not correct answers. Two of
them are wrong: 'preto' is an adjective and is read as a NOUN, and 'dorme.' is
never split, so the verb is lost inside a PUNCT token. They are pinned here so
a fix to either one must change this file on purpose.
"""
import importlib.util

from tugatagger import TugaTagger

_SENTENCE = "O gato preto dorme."

# The answers of the built-in heuristic, with no optional backend installed.
_EXPECTED = [
    ("O", "DET"),
    ("gato", "NOUN"),
    ("preto", "NOUN"),   # wrong: ADJ
    ("dorme.", "PUNCT"),  # wrong: the token is not split, so the VERB is lost
]

_BACKENDS = ("spacy", "stanza", "brill_postagger", "tugalex", "tugamorph")
_HAS_BACKEND = any(importlib.util.find_spec(m) is not None for m in _BACKENDS)


def test_dummy_engine_tags_known_values():
    """The heuristic engine is exact and needs no extra, so assert its values."""
    assert TugaTagger(engine="dummy").tag(_SENTENCE) == _EXPECTED


def test_default_engine_tags_text():
    """The default engine tags text, and falls back to the heuristic."""
    tags = TugaTagger().tag(_SENTENCE)
    assert tags, "the default engine returned nothing"
    assert all(isinstance(t, tuple) and len(t) == 2 for t in tags)
    assert all(isinstance(pos, str) and pos.isupper() for _, pos in tags)
    if not _HAS_BACKEND:
        # This is the environment CI builds: no extras, so the values are fixed.
        assert tags == _EXPECTED
