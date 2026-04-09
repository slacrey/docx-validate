from pathlib import Path

from docx_validate.services.template_metadata import extract_template_metadata


FIXTURES_DIR = Path(__file__).resolve().parent.parent / "fixtures" / "templates"


def test_extract_template_metadata_returns_expected_structure() -> None:
    metadata = extract_template_metadata(FIXTURES_DIR / "basic-template.docx")

    assert metadata["paragraph_count"] == 2
    assert metadata["table_count"] == 1
    assert metadata["section_count"] == 1
    assert metadata["styles"] == ["Heading 1", "Normal"]
    assert metadata["bookmarks"] == ["CustomerBookmark"]
    assert metadata["placeholders"] == ["customer_name", "order_no"]


def test_extract_template_metadata_returns_empty_placeholders_when_absent() -> None:
    metadata = extract_template_metadata(FIXTURES_DIR / "no-placeholders.docx")

    assert metadata["paragraph_count"] == 1
    assert metadata["table_count"] == 0
    assert metadata["section_count"] == 1
    assert metadata["styles"] == ["Normal"]
    assert metadata["bookmarks"] == []
    assert metadata["placeholders"] == []
