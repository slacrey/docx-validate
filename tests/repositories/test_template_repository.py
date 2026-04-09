from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from docx_validate.db.base import Base
from docx_validate.models.template import DocumentTemplate
from docx_validate.repositories.template_repository import TemplateRepository
from docx_validate.schemas.template import TemplateRead


def make_template(
    *,
    id: int | None = None,
    name: str = "invoice",
    version: str = "v1",
    object_key: str = "templates/invoice/v1/template.docx",
    file_name: str = "invoice.docx",
    file_size: int = 2048,
    content_hash: str = "abc123",
    metadata_json: dict[str, object] | None = None,
    status: str = "ACTIVE",
) -> DocumentTemplate:
    return DocumentTemplate(
        id=id,
        name=name,
        version=version,
        object_key=object_key,
        file_name=file_name,
        file_size=file_size,
        content_hash=content_hash,
        metadata_json=metadata_json or {"placeholders": ["customer_name"]},
        status=status,
    )


def test_template_repository_create_and_getters() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        repository = TemplateRepository(session)
        created = repository.create(make_template())

        assert created.id is not None

        by_id = repository.get(created.id)
        by_identity = repository.get_by_identity("invoice", "v1")
        by_hash = repository.get_by_content_hash("abc123")

    assert by_id is not None
    assert by_id.id == created.id
    assert by_identity is not None
    assert by_identity.id == created.id
    assert by_hash is not None
    assert by_hash.id == created.id


def test_template_repository_save_updates_existing_record() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        repository = TemplateRepository(session)
        created = repository.create(make_template())

        created.object_key = "templates/invoice/v1/template-updated.docx"
        created.file_size = 4096
        created.metadata_json = {"placeholders": ["customer_name", "invoice_no"]}

        saved = repository.save(created)
        reloaded = repository.get(created.id)

    assert saved.object_key == "templates/invoice/v1/template-updated.docx"
    assert saved.file_size == 4096
    assert reloaded is not None
    assert reloaded.metadata_json == {
        "placeholders": ["customer_name", "invoice_no"]
    }


def test_template_read_exposes_expected_fields() -> None:
    payload = TemplateRead.model_validate(
        make_template(
            name="invoice",
            version="v1",
            object_key="templates/invoice/v1/template.docx",
            file_name="invoice.docx",
            file_size=2048,
            content_hash="abc123",
            metadata_json={"placeholders": ["customer_name"]},
            id=1,
            status="ACTIVE",
        )
    ).model_dump()

    assert set(payload) == {
        "id",
        "name",
        "version",
        "status",
        "object_key",
        "file_name",
        "file_size",
        "content_hash",
        "metadata_json",
    }
