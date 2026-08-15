"""Tests for shared/helper_diff.py diff HTML generation."""

import html

from shared.helper_diff import _highlight_chunks, create_diff_html
from shared.texts import LABEL_KI_TEXT, LABEL_MY_TEXT


class TestHighlightChunks:
    """Test the _highlight_chunks helper."""

    def test_equal_text_unchanged(self) -> None:
        """Equal chunks are HTML-escaped without wrapping."""
        opcodes = [("equal", 0, 6, 0, 6)]
        result = _highlight_chunks(
            "h<el>o", opcodes, side=0, change_class="diff-delete"
        )
        assert result == html.escape("h<el>o")
        assert "span" not in result

    def test_replacement_wrapped_in_span(self) -> None:
        """Replaced chunks are wrapped in the change class span."""
        opcodes = [("replace", 0, 2, 0, 3)]
        result = _highlight_chunks("ab", opcodes, side=0, change_class="diff-delete")
        assert result == '<span class="diff-delete">ab</span>'

    def test_insert_uses_side_1_range(self) -> None:
        """Insert opcodes use j1/j2 range when side=1."""
        opcodes = [("insert", 0, 0, 2, 5)]
        result = _highlight_chunks(
            # cspell:disable-next-line-next
            "xyzabc",
            opcodes,
            side=1,
            change_class="diff-insert",
        )
        assert result == '<span class="diff-insert">zab</span>'

    def test_empty_chunks_skipped(self) -> None:
        """Empty chunks produce no output."""
        opcodes = [
            ("equal", 0, 2, 0, 2),
            ("insert", 2, 2, 2, 2),
            ("equal", 2, 3, 2, 3),
        ]
        result = _highlight_chunks("abc", opcodes, side=1, change_class="diff-insert")
        assert result == "ab" + "c"


class TestCreateDiffHtml:
    """Test the create_diff_html entry point."""

    def test_identical_texts_no_spans(self) -> None:
        """Identical texts produce a table without change spans."""
        result = create_diff_html("Hallo Welt", "Hallo Welt")
        assert LABEL_MY_TEXT in result
        assert LABEL_KI_TEXT in result
        assert "Hallo Welt" in result
        assert "diff-delete" not in result
        assert "diff-insert" not in result

    def test_insert_highlighted_in_ai_column(self) -> None:
        """An inserted character is highlighted in the AI column."""
        # cspell:disable-next-line-next
        result = create_diff_html("Korektur", "Korrektur")
        assert '<span class="diff-insert">' in result

    def test_delete_highlighted_in_original_column(self) -> None:
        """A deleted character is highlighted in the original column."""
        result = create_diff_html("abc", "ac")
        assert '<span class="diff-delete">' in result

    def test_html_in_input_escaped(self) -> None:
        """HTML in input text is escaped, not rendered."""
        result = create_diff_html("<script>", "<b>")
        assert "<script>" not in result
        assert "<b>" not in result
        assert "&lt;" in result
        assert "&gt;" in result

    def test_table_structure(self) -> None:
        """Result contains a comparison table with two columns."""
        result = create_diff_html("a", "b")
        assert '<table class="comparison-table">' in result
        assert result.count("<th>") == 2
        assert result.count("<td>") == 2
