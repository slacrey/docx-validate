from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from docx_validate.db.base import Base
from docx_validate.models.task import DocumentTask


def test_document_task_persists_with_expected_defaults() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        task = DocumentTask(
            task_no="TASK-001",
            template_id=1,
            rule_set_id=2,
            input_object_key="inputs/TASK-001/source.docx",
        )
        session.add(task)
        session.commit()

        loaded = session.scalar(
            select(DocumentTask).where(DocumentTask.task_no == "TASK-001")
        )

    assert loaded is not None
    assert loaded.task_no == "TASK-001"
    assert loaded.status == "PENDING"
    assert loaded.progress == 0
