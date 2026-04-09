from datetime import datetime

from docx_validate.models.task import DocumentTask
from docx_validate.repositories.task_repository import TaskRepository
from docx_validate.services.storage import LocalStorage
from docx_validate.services.validator import PlaceholderValidator


class TaskService:
    def __init__(self, repository: TaskRepository, storage: LocalStorage) -> None:
        self.repository = repository
        self.storage = storage
        self.validator = PlaceholderValidator(storage)

    def create_task(
        self,
        *,
        template_id: int,
        rule_set_id: int,
        filename: str,
        content: bytes,
    ) -> DocumentTask:
        task_no = datetime.utcnow().strftime("TASK-%Y%m%d%H%M%S%f")
        object_key = f"inputs/{task_no}/source.docx"
        self.storage.write_bytes(object_key, content)
        task = DocumentTask(
            task_no=task_no,
            template_id=template_id,
            rule_set_id=rule_set_id,
            input_object_key=object_key,
        )
        return self.repository.create(task)

    def validate_task(self, task_no: str) -> dict[str, object]:
        task = self.repository.get_by_task_no(task_no)
        if task is None:
            raise ValueError(f"task not found: {task_no}")

        task.status = "RUNNING"
        task.progress = 50
        self.repository.save(task)

        summary = self.validator.validate(task)
        task.status = "SUCCESS"
        task.progress = 100
        task.finished_at = datetime.utcnow()
        self.repository.save(task)
        return summary
