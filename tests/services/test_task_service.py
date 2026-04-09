from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from docx_validate.db.base import Base
from docx_validate.models.task import DocumentTask
from docx_validate.repositories.task_repository import TaskRepository
from docx_validate.services.storage import LocalStorage
from docx_validate.services.task_service import TaskService


def test_validate_task_marks_success_and_writes_report(tmp_path: Path) -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        repository = TaskRepository(session)
        task = repository.create(
            DocumentTask(
                task_no="TASK-001",
                template_id=1,
                rule_set_id=2,
                input_object_key="inputs/TASK-001/source.docx",
            )
        )

        storage = LocalStorage(tmp_path)
        service = TaskService(repository, storage)

        summary = service.validate_task(task.task_no)

        assert summary["task_no"] == "TASK-001"
        assert summary["issue_count"] == 0

        reloaded = repository.get_by_task_no("TASK-001")
        assert reloaded is not None
        assert reloaded.status == "SUCCESS"
        assert reloaded.progress == 100
        assert reloaded.finished_at is not None

    report_path = tmp_path / "results" / "TASK-001" / "report.json"
    assert report_path.exists()
