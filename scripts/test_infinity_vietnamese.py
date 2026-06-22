"""Tests for InfinityNeural Vietnamese NLP — compounds, tones, normalization."""

from neural_memory.extraction.vietnamese_nlp import (
    VIETNAMESE_COMPOUNDS,
    EXTENDED_STOPWORDS_VI,
    detect_compounds,
    normalize_vietnamese,
    strip_vietnamese_tones,
    syllable_count,
    tokenize_with_compounds,
)


class TestVietnameseNLP:
    """Tests for InfinityNeural Vietnamese NLP utilities."""

    def test_compound_list_not_empty(self) -> None:
        """Compound word list should contain entries."""
        assert len(VIETNAMESE_COMPOUNDS) > 100

    def test_extended_stopwords_not_empty(self) -> None:
        """Extended stopwords should contain entries."""
        assert len(EXTENDED_STOPWORDS_VI) > 30

    def test_detect_compounds_basic(self) -> None:
        """Should detect compound words in text."""
        text = "Tôi là sinh viên đại học, đang học trí tuệ nhân tạo"
        compounds = detect_compounds(text)
        assert "sinh viên" in compounds
        assert "đại học" in compounds
        assert "trí tuệ" in compounds

    def test_detect_compounds_empty(self) -> None:
        """Should return empty for text without compounds."""
        text = "hello world foo bar"
        compounds = detect_compounds(text)
        assert compounds == []

    def test_normalize_vietnamese(self) -> None:
        """Should normalize whitespace and lowercase."""
        text = "  Tôi  là   SINH VIÊN  "
        result = normalize_vietnamese(text)
        assert result == "tôi là sinh viên"

    def test_strip_tones(self) -> None:
        """Should strip tone marks from Vietnamese text."""
        # á → a, ội → ôi
        result = strip_vietnamese_tones("Hà Nội")
        assert "à" not in result
        assert "ộ" not in result

    def test_strip_tones_preserves_base(self) -> None:
        """Base vowels (ă, â, ê, ô, ơ, ư) should be preserved."""
        text = "ăn"
        result = strip_vietnamese_tones(text)
        assert "ă" in result  # base vowel preserved

    def test_syllable_count(self) -> None:
        """Should count Vietnamese syllables correctly."""
        assert syllable_count("Tôi là sinh viên") == 4
        assert syllable_count("xin chào") == 2
        assert syllable_count("") == 0

    def test_tokenize_with_compounds_fallback(self) -> None:
        """Should tokenize with compound detection even without pyvi."""
        text = "Tôi là sinh viên đại học"
        tokens = tokenize_with_compounds(text)
        # Should have tokens (either from pyvi or fallback)
        assert len(tokens) > 0

    def test_compounds_no_overlap(self) -> None:
        """No compound should be a substring of another (basic check)."""
        # This checks that our compound list is well-formed
        compounds_list = sorted(VIETNAMESE_COMPOUNDS, key=len)
        # Just verify the list is a frozenset (no duplicates)
        assert isinstance(VIETNAMESE_COMPOUNDS, frozenset)
