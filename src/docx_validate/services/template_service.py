from __future__ import annotations

import hashlib
from pathlib import Path

from docx_validate.models.template import DocumentTemplate
from docx_validate.repositories.template_repository import TemplateRepository
from docx_validate.services.storage import LocalStorage
from docx_validate.services.template_metadata import extract_template_metadata


class InvalidTemplateFileError(ValueError):
    pass


class TemplateIdentityConflictError(ValueError):
    pass


class TemplateContentConflictError(ValueError):
    pass


class TemplateService:
    def __init__(self, repository: TemplateRepository, storage: LocalStorage) -> None:
        self.repository = repository
        self.storage = storage

    def create_template(
        self,
        *,
        name: str,
        version: str,
        filename: str,
        content: bytes,
        overwrite: bool = False,
    ) -> DocumentTemplate:
        if not filename.lower().endswith(".docx"):
            raise InvalidTemplateFileError("only .docx files are supported")

        content_hash = hashlib.sha256(content).hexdigest()
        file_size = len(content)
        existing_identity = self.repository.get_by_identity(name, version)
        existing_hash = self.repository.get_by_content_hash(content_hash)

        if existing_identity is None and existing_hash is not None:
            raise TemplateContentConflictError(
                "template content already exists under another identity"
            )

        if existing_identity is not None and not overwrite:
            raise TemplateIdentityConflictError("template identity already exists")

        if (
            existing_identity is not None
            and existing_hash is not None
            and existing_hash.id != existing_identity.id
        ):
            raise TemplateContentConflictError(
                "template content already exists under another identity"
            )

        object_key = self._build_object_key(name=name, version=version, content_hash=content_hash)
        self.storage.write_bytes(object_key, content)
        metadata_json = extract_template_metadata(self.storage.resolve_path(object_key))

        if existing_identity is None:
            template = DocumentTemplate(
                name=name,
                version=version,
                object_key=object_key,
                file_name=filename,
                file_size=file_size,
                content_hash=content_hash,
                metadata_json=metadata_json,
                status="ACTIVE",
            )
            return self.repository.create(template)

        existing_identity.object_key = object_key
        existing_identity.file_name = filename
        existing_identity.file_size = file_size
        existing_identity.content_hash = content_hash
        existing_identity.metadata_json = metadata_json
        existing_identity.status = "ACTIVE"
        return self.repository.save(existing_identity)

    def get_template(self, template_id: int) -> DocumentTemplate | None:
        return self.repository.get(template_id)

    def _build_object_key(self, *, name: str, version: str, content_hash: str) -> str:
        safe_name = self._slugify(name)
        safe_version = self._slugify(version)
        return f"templates/{safe_name}/{safe_version}/{content_hash}.docx"

    @staticmethod
    def _slugify(value: str) -> str:
        normalized = "".join(
            character.lower() if character.isalnum() else "-"
            for character in value.strip()
        )
        collapsed = "-".join(part for part in normalized.split("-") if part)
        return collapsed or "template"
