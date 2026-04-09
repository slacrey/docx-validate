from sqlalchemy import select
from sqlalchemy.orm import Session

from docx_validate.models.template import DocumentTemplate


class TemplateRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create(self, template: DocumentTemplate) -> DocumentTemplate:
        self.session.add(template)
        self.session.commit()
        self.session.refresh(template)
        return template

    def get(self, template_id: int) -> DocumentTemplate | None:
        return self.session.get(DocumentTemplate, template_id)

    def get_by_identity(self, name: str, version: str) -> DocumentTemplate | None:
        statement = select(DocumentTemplate).where(
            DocumentTemplate.name == name,
            DocumentTemplate.version == version,
        )
        return self.session.scalar(statement)

    def get_by_content_hash(self, content_hash: str) -> DocumentTemplate | None:
        statement = select(DocumentTemplate).where(
            DocumentTemplate.content_hash == content_hash
        )
        return self.session.scalar(statement)

    def save(self, template: DocumentTemplate) -> DocumentTemplate:
        self.session.add(template)
        self.session.commit()
        self.session.refresh(template)
        return template
