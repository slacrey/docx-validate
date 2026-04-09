from docx_validate.models.task import DocumentTask
from docx_validate.services.storage import LocalStorage


class PlaceholderValidator:
    def __init__(self, storage: LocalStorage) -> None:
        self.storage = storage

    def validate(self, task: DocumentTask) -> dict[str, object]:
        summary = {
            "task_no": task.task_no,
            "issue_count": 0,
            "issues": [],
            "report_object_key": f"results/{task.task_no}/report.json",
        }
        self.storage.write_json(summary["report_object_key"], summary)
        return summary
