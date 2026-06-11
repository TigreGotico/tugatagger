from typing import List, Optional, Tuple

try:
    from tugamorph import PortugueseMorphAnalyzer as _MorphAnalyzer
    _morph: Optional[_MorphAnalyzer] = None

    def _get_morph() -> _MorphAnalyzer:
        global _morph
        if _morph is None:
            from tugamorph import AnalysisConfig
            _morph = _MorphAnalyzer(config=AnalysisConfig(use_pos_tagger=False))
        return _morph

    _HAS_TUGAMORPH = True
except ImportError:
    _HAS_TUGAMORPH = False

    def _get_morph():  # type: ignore[misc]
        return None


# UPOS tags returned by tugamorph suffix categories → tugatagger UPOS labels
_SUFFIX_CAT_TO_POS = {
    "SuffixCategory.NOUN_ABSTRACT": "NOUN",
    "SuffixCategory.NOUN_ACTION": "NOUN",
    "SuffixCategory.NOUN_AGENT": "NOUN",
    "SuffixCategory.NOUN_PLACE": "NOUN",
    "SuffixCategory.COLLECTIVE": "NOUN",
    "SuffixCategory.DIMINUTIVE": "NOUN",
    "SuffixCategory.AUGMENTATIVE": "NOUN",
    "SuffixCategory.PEJORATIVE": "NOUN",
    "SuffixCategory.ADJECTIVE": "ADJ",
    "SuffixCategory.ADVERB": "ADV",
    "SuffixCategory.SCIENTIFIC": "NOUN",
    "SuffixCategory.GENTILICO": "ADJ",
}

_TENSE_MOOD_TO_POS = {
    "pres_ind": "VERB",
    "pret_perf": "VERB",
    "pret_imperf": "VERB",
    "imperf": "VERB",
    "fut_ind": "VERB",
    "conditional": "VERB",
    "subj_pres": "VERB",
    "subj_imperf": "VERB",
    "subj_fut": "VERB",
    "imperative": "VERB",
    "gerund": "VERB",
    "participle": "VERB",
    "inf_pessoal": "VERB",
    "none": "VERB",
}


class TugaTagger:
    """
    A unified interface for Portuguese Part-of-Speech (POS) tagging.

    Supports multiple backends including spaCy and Brill-style taggers.
    The 'auto' mode provides a fallback mechanism to ensure tagging works
    even if specific dependencies are missing.
    """

    def __init__(self, engine: str = "auto", spacy_model: str = "pt_core_news_lg"):
        """
        Create a TugaTagger configured for the chosen tagging engine and optionally preload backend models.

        Parameters:
            engine (str): Tagging engine to use: "spacy", "brill", "dummy", or "auto".
                - "spacy": preload the spaCy model in strict mode.
                - "brill": preload the Brill tagger in strict mode.
                - "auto": attempt to preload both spaCy and Brill (not strict).
            spacy_model (str): Name of the spaCy Portuguese model to load when using spaCy (default "pt_core_news_lg").

        Notes:
            Load failures for a backend will be propagated when that backend is loaded in strict mode.
        """
        self.engine = engine
        self._spacy = self._brill = self._lexicon = None

        if engine in ["spacy", "auto"]:
            self.load_spacy(spacy_model, strict=(engine == "spacy"))
        if engine in ["brill", "auto"]:
            self.load_brill(strict=(engine == "brill"))
        if engine in ["lexicon", "auto"]:
            self.load_lexicon(strict=(engine == "lexicon"))

    def load_lexicon(self, strict: bool = True):
        try:
            from tugalex import TugaLexicon
            self._lexicon = TugaLexicon()
        except Exception as e:
            if strict:
                raise e

    def load_spacy(self, spacy_model: str = "pt_core_news_lg", strict: bool = True):
        """
        Load and cache a spaCy Portuguese NLP model on the instance.

        Parameters:
            spacy_model (str): Name of the spaCy model to load (e.g., "pt_core_news_lg").
            strict (bool): If True, re-raise any exception encountered while loading; if False, suppress the exception and leave `self._spacy` as None.

        Side effects:
            Assigns the loaded spaCy model to `self._spacy`.
        """
        try:
            import spacy
            self._spacy = spacy.load(spacy_model, disable=["ner", "parser"])
        except Exception as e:
            if strict:
                raise e

    def load_brill(self, strict: bool = True):
        """
        Load and cache a Brill-style Portuguese POS tagger on the instance.

        Parameters:
            strict (bool): If True, re-raise any exception encountered while importing or loading the tagger;
                if False, suppress load errors and leave `self._brill` unset when loading fails.
        """
        try:
            from brill_postaggers import BrillPostagger
            self._brill = BrillPostagger.from_pretrained("pt")
        except Exception as e:
            if strict:
                raise e

    def tag(self, sentence: str) -> List[Tuple[str, str]]:
        """
        Tags a sentence using the configured engine.

        Args:
            sentence (str): The Portuguese text to tag.

        Returns:
            List[Tuple[str, str]]: A list of (word, tag) tuples.
        """
        engines = {
            "auto": self.tag_auto,
            "dummy": self.tag_dummy,
            "brill": self.tag_brill,
            "spacy": self.tag_spacy,
            "lexicon": self.tag_lexicon
        }
        handler = engines.get(self.engine)
        if not handler:
            raise ValueError(f"Invalid engine: '{self.engine}'")
        return handler(sentence)

    def tag_auto(self, sentence: str) -> List[Tuple[str, str]]:
        """
        Tag a sentence by trying spaCy then Brill and using the dummy tagger if both fail.

        Returns:
            List[Tuple[str, str]]: A list of (word, POS-tag) tuples produced by the first successful tagger; if both spaCy and Brill raise exceptions, returns the dummy tagger's output.
        """
        for method in [self.tag_brill, self.tag_spacy, self.tag_lexicon]:
            try:
                return method(sentence)
            except:
                continue
        return self.tag_dummy(sentence)

    def tag_brill(self, sentence: str) -> List[Tuple[str, str]]:
        """
        Tag a sentence using the Brill-style POS tagger.

        If the Brill tagger is not yet loaded, it will be initialized automatically.

        Parameters:
            sentence (str): Raw text sentence to be tagged.

        Returns:
            List[Tuple[str, str]]: List of (token, POS-tag) pairs for the input sentence.
        """
        if self._brill is None:
            self.load_brill(strict=True)
        return self._brill.tag(sentence)

    def tag_spacy(self, sentence: str) -> List[Tuple[str, str]]:
        """
        Tag a sentence using the configured spaCy Portuguese model.

        Returns:
            List[Tuple[str, str]]: A list of (token_text, POS_tag) tuples, one per token. `POS_tag` is spaCy's coarse-grained part-of-speech label.
        """
        if self._spacy is None:
            self.load_spacy(strict=True)
        doc = self._spacy(sentence)
        return [(tok.text, tok.pos_) for tok in doc]

    def tag_lexicon(self, sentence: str) -> List[Tuple[str, str]]:
        tagged = []

        # TODO: improve this
        tokenize = lambda k: k.lower().replace(".", " .").replace("!", " !").replace("?", " ?").split()

        for word in tokenize(sentence):
            if word in self._lexicon.possible_postags:
                possibilities = self._lexicon.possible_postags[word]
                # TODO: how to choose postag? use surrounding context
                tagged.append((word, possibilities[0]))
            else:
                tagged.append((word, self._guess_pos(word)))
        return tagged

    @classmethod
    def tag_dummy(cls, sentence: str) -> List[Tuple[str, str]]:
        """
        Split the sentence on whitespace and tag each token as the noun "NOUN".

        Returns:
            List[Tuple[str, str]]: A list of (word, tag) tuples where each whitespace-separated token from the input is paired with the tag "NOUN".
        """
        return [(word, cls._guess_pos(word)) for word in sentence.split()]

    @staticmethod
    def _guess_pos(word: str) -> str:
        """Heuristic POS guess for a single word.

        Uses tugamorph morphological analysis when available for better coverage of
        verbal forms and derivational suffixes.  Falls back to a compact rule table
        when tugamorph is not installed.
        """
        lower_word = word.lower()

        # Punctuation / numbers — fast path before any morphology
        if not word.isalnum():
            return "PUNCT"
        if word.isdigit():
            return "NUM"

        # Closed-class function words — highest confidence, check first
        _CLOSED = {
            "o": "DET", "a": "DET", "os": "DET", "as": "DET",
            "um": "DET", "uma": "DET", "uns": "DET", "umas": "DET",
            "de": "ADP", "do": "ADP", "da": "ADP", "dos": "ADP", "das": "ADP",
            "em": "ADP", "no": "ADP", "na": "ADP", "nos": "ADP", "nas": "ADP",
            "por": "ADP", "pelo": "ADP", "pela": "ADP", "pelos": "ADP", "pelas": "ADP",
            "para": "ADP", "com": "ADP", "sem": "ADP", "sob": "ADP", "sobre": "ADP",
            "entre": "ADP", "até": "ADP", "após": "ADP", "ante": "ADP",
            "e": "CCONJ", "mas": "CCONJ", "ou": "CCONJ", "nem": "CCONJ", "porém": "CCONJ",
            "que": "SCONJ", "se": "SCONJ", "porque": "SCONJ", "embora": "SCONJ",
            "quando": "SCONJ", "como": "SCONJ",
            "eu": "PRON", "tu": "PRON", "ele": "PRON", "ela": "PRON",
            "nós": "PRON", "vós": "PRON", "eles": "PRON", "elas": "PRON",
            "me": "PRON", "te": "PRON", "se": "PRON", "lhe": "PRON",
            "nos": "PRON", "vos": "PRON", "lhes": "PRON",
            "isso": "PRON", "isto": "PRON", "aquilo": "PRON",
            "este": "PRON", "essa": "PRON", "esse": "PRON", "aquele": "PRON", "aquela": "PRON",
            "é": "AUX", "foi": "AUX", "são": "AUX", "eram": "AUX",
            "está": "AUX", "estar": "AUX", "ser": "AUX",
            "ter": "AUX", "tem": "AUX", "tinha": "AUX", "tido": "AUX",
            "haver": "AUX", "há": "AUX",
            "não": "ADV", "sim": "ADV", "muito": "ADV", "mais": "ADV",
            "já": "ADV", "ainda": "ADV", "sempre": "ADV", "nunca": "ADV",
            "aqui": "ADV", "aí": "ADV", "ali": "ADV", "lá": "ADV",
            "hoje": "ADV", "ontem": "ADV", "amanhã": "ADV",
        }
        if lower_word in _CLOSED:
            return _CLOSED[lower_word]

        # Morphological analysis via tugamorph when available
        if _HAS_TUGAMORPH:
            try:
                morph = _get_morph()
                result = morph.analyze(lower_word)
                if result.verbal is not None:
                    tm = result.verbal.tense_mood or ""
                    # Distinguish auxiliaries / participles used as adjectives
                    if tm == "participle":
                        return "ADJ"
                    if tm in _TENSE_MOOD_TO_POS:
                        return _TENSE_MOOD_TO_POS[tm]
                    return "VERB"
                if result.suffix is not None:
                    sfx_str = str(result.suffix[1])
                    pos = _SUFFIX_CAT_TO_POS.get(sfx_str)
                    if pos:
                        return pos
            except Exception:
                pass  # never let analysis errors break tagging

        # Fallback suffix table — same coverage as before, used when tugamorph absent
        _SUFFIX_RULES = [
            ("mente", "ADV"),
            ("ando", "VERB"), ("endo", "VERB"), ("indo", "VERB"),
            ("aram", "VERB"), ("eram", "VERB"), ("iram", "VERB"),
            ("aram", "VERB"), ("avam", "VERB"), ("iam", "VERB"),
            ("ava", "VERB"), ("ria", "VERB"),
            ("ção", "NOUN"), ("são", "NOUN"), ("dade", "NOUN"),
            ("dor", "NOUN"), ("ismo", "NOUN"), ("ista", "NOUN"),
            ("oso", "ADJ"), ("osa", "ADJ"), ("vel", "ADJ"), ("al", "ADJ"),
            ("ar", "VERB"), ("er", "VERB"), ("ir", "VERB"),
        ]
        for suffix, tag in _SUFFIX_RULES:
            if lower_word.endswith(suffix) and len(lower_word) > len(suffix):
                return tag

        # Capitalised word not at start → likely proper noun
        if word[0].isupper() and len(word) > 1 and word[1:].islower():
            return "PROPN"

        return "NOUN"


def get_verb_tense(word: str) -> Optional[dict]:
    """Return structured verbal morphology for *word*, or None if not a verb.

    Requires tugamorph to be installed.  When it is, returns a dict with the keys:

        tense_mood      str   — e.g. "pres_ind", "pret_perf", "subj_imperf", "gerund",
                                     "participle", "conditional", "fut_ind" …
        person          int|None  — 1, 2, or 3
        number          str|None  — "sg" or "pl"
        conjugation     int|None  — 1 (-ar), 2 (-er), 3 (-ir)
        is_past_participle bool
        lemma           str|None  — infinitive guess, e.g. "cantar"
        is_irregular    bool

    Returns None when:
        - tugamorph is not installed
        - the word is not recognised as a verbal form
        - analysis raises an exception

    Example::

        >>> get_verb_tense("cantavam")
        {'tense_mood': 'imperf', 'person': 3, 'number': 'pl', 'conjugation': 1,
         'is_past_participle': False, 'lemma': 'cantar', 'is_irregular': False}

        >>> get_verb_tense("disseram")
        {'tense_mood': 'pret_perf', 'person': 3, 'number': 'pl', 'conjugation': None,
         'is_past_participle': False, 'lemma': 'dizer', 'is_irregular': True}
    """
    if not _HAS_TUGAMORPH:
        return None
    try:
        morph = _get_morph()
        result = morph.analyze(word.lower())
        v = result.verbal
        if v is None:
            return None
        return {
            "tense_mood": v.tense_mood,
            "person": v.person,
            "number": v.number,
            "conjugation": v.conjugation_class,
            "is_past_participle": v.is_past_participle,
            "lemma": result.lemma_guess,
            "is_irregular": v.is_irregular,
        }
    except Exception:
        return None


if __name__ == "__main__":
    # Initialize with 'auto' to use the best available engine
    tagger = TugaTagger(engine="auto")

    text = "O gato preto pulou o muro."

    print(f"Using engine: {tagger.engine}")
    tags = tagger.tag(text)

    for word, pos in tags:
        print(f"{word:10} -> {pos}")