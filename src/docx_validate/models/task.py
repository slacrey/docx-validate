from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from docx_validate.db.base import Base


class DocumentTask(Base):
    __tablename__ = "document_task"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    task_no: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    template_id: Mapped[int] = mapped_column(Integer, nullable=False)
    rule_set_id: Mapped[int] = mapped_column(Integer, nullable=False)
    input_object_key: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="PENDING")
    progress: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )
    finished_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
