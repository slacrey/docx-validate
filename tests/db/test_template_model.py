import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from docx_validate.db.base import Base
from docx_validate.models.template import DocumentTemplate


def test_document_template_persists_expected_fields_and_defaults() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        template = DocumentTemplate(
            name="invoice",
            version="v1",
            object_key="templates/invoice/v1/template.docx",
            file_name="invoice.docx",
            file_size=2048,
            content_hash="abc123",
            metadata_json={"placeholders": ["customer_name"]},
        )
        session.add(template)
        session.commit()

        loaded = session.scalar(
            select(DocumentTemplate).where(DocumentTemplate.name == "invoice")
        )

    assert loaded is not None
    assert loaded.name == "invoice"
    assert loaded.version == "v1"
    assert loaded.content_hash == "abc123"
    assert loaded.metadata_json == {"placeholders": ["customer_name"]}
    assert loaded.status == "ACTIVE"


def test_document_template_identity_must_be_unique() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        session.add(
            DocumentTemplate(
                name="invoice",
                version="v1",
                object_key="templates/invoice/v1/template.docx",
                file_name="invoice.docx",
                file_size=2048,
                content_hash="abc123",
                metadata_json={},
            )
        )
        session.commit()

        session.add(
            DocumentTemplate(
                name="invoice",
                version="v1",
                object_key="templates/invoice/v1/template-duplicate.docx",
                file_name="invoice-copy.docx",
                file_size=4096,
                content_hash="def456",
                metadata_json={},
            )
        )

        with pytest.raises(IntegrityError):
            session.commit()
