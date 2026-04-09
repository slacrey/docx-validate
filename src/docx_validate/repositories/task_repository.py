from sqlalchemy import select
from sqlalchemy.orm import Session

from docx_validate.models.task import DocumentTask


class TaskRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create(self, task: DocumentTask) -> DocumentTask:
        self.session.add(task)
        self.session.commit()
        self.session.refresh(task)
        return task

    def get_by_task_no(self, task_no: str) -> DocumentTask | None:
        statement = select(DocumentTask).where(DocumentTask.task_no == task_no)
        return self.session.scalar(statement)

    def save(self, task: DocumentTask) -> DocumentTask:
        self.session.add(task)
        self.session.commit()
        self.session.refresh(task)
        return task
