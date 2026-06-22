from proextractor.adapters.propresenter.rtf_parser import rtf_to_text


def test_rtf_decodes_cp1252_and_paragraphs() -> None:
    assert rtf_to_text(r"{\rtf1\ansi There\'92s\par niemand}") == "There’s\nniemand"


def test_rtf_ignores_font_table() -> None:
    assert rtf_to_text(r"{\rtf1{\fonttbl{\f0 Futura;}}\f0 Hello}") == "Hello"

