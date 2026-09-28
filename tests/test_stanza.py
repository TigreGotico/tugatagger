"""Tests for the Stanza backend of TugaTagger."""
import importlib.util

import pytest

from tugatagger import TugaTagger

_HAS_STANZA = importlib.util.find_spec("stanza") is not None


def test_stanza_engine_is_registered():
    """The 'stanza' engine must be routable and expose tag_stanza/load_stanza."""
    tagger = TugaTagger.__new__(TugaTagger)  # no model preload
    tagger.engine = "stanza"
    tagger._stanza = None
    tagger._stanza_lang = "pt"
    assert hasattr(tagger, "tag_stanza")
    assert hasattr(tagger, "load_stanza")
    # 'stanza' resolves to a handler in tag()'s engine map
    assert callable(getattr(tagger, "tag_stanza"))


def test_invalid_engine_still_raises():
    tagger = TugaTagger.__new__(TugaTagger)
    tagger.engine = "does-not-exist"
    with pytest.raises(ValueError):
        tagger.tag("O gato dorme.")


@pytest.mark.skipif(not _HAS_STANZA, reason="stanza not installed")
def test_stanza_tagging_smoke():
    """With stanza installed, tagging returns (token, UPOS) tuples."""
    tagger = TugaTagger(engine="stanza")
    tags = tagger.tag("O gato preto dorme.")
    assert tags and all(isinstance(t, tuple) and len(t) == 2 for t in tags)
    words = [w for w, _ in tags]
    assert "gato" in words
    # POS labels are UPOS strings
    assert all(isinstance(pos, str) and pos.isupper() for _, pos in tags)
