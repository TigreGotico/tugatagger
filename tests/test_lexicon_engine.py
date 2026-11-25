"""Tests for the lexicon backend of TugaTagger."""
from tugatagger import TugaTagger


def test_a_homograph_takes_its_first_table_tag():
    tagger = TugaTagger(engine="lexicon")
    first_tag = next(iter(tagger._lexicon.homographs["para"]))
    assert tagger.tag("Vou para casa")[1] == ("para", first_tag)
    assert first_tag == "ADP"


def test_a_dictionary_word_gets_a_guessed_tag():
    tagger = TugaTagger(engine="lexicon")
    word, tag = tagger.tag("cantar")[0]
    assert (word, tag) == ("cantar", TugaTagger._guess_pos("cantar"))
    assert tag == "VERB"
