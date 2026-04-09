from fastapi import APIRouter, Depends, File, Form, Request, UploadFile
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from docx_validate.api.deps import get_db
from docx_validate.repositories.template_repository import TemplateRepository
from docx_validate.schemas.template import TemplateRead
from docx_validate.services.storage import build_storage
from docx_validate.services.template_service import (
    InvalidTemplateFileError,
    TemplateContentConflictError,
    TemplateIdentityConflictError,
    TemplateService,
)


router = APIRouter(prefix="/templates", tags=["templates"])


def _error_response(message: str, code: int, status_code: int) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={"code": code, "message": message, "data": None},
    )


@router.post("")
def create_template(
    request: Request,
    name: str = Form(...),
    version: str = Form(...),
    overwrite: bool = Form(False),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> JSONResponse:
    service = TemplateService(TemplateRepository(db), build_storage(request))

    try:
        template = service.create_template(
            name=name,
            version=version,
            filename=file.filename or "",
            content=file.file.read(),
            overwrite=overwrite,
        )
    except InvalidTemplateFileError as exc:
        return _error_response(str(exc), code=40001, status_code=400)
    except TemplateIdentityConflictError as exc:
        return _error_response(str(exc), code=40901, status_code=409)
    except TemplateContentConflictError as exc:
        return _error_response(str(exc), code=40902, status_code=409)

    payload = TemplateRead.model_validate(template).model_dump(mode="json")
    return JSONResponse(
        status_code=201,
        content={"code": 0, "message": "ok", "data": payload},
    )


@router.get("/{template_id}")
def get_template(template_id: int, db: Session = Depends(get_db)) -> JSONResponse:
    template = TemplateRepository(db).get(template_id)
    if template is None:
        return _error_response("template not found", code=40404, status_code=404)

    payload = TemplateRead.model_validate(template).model_dump(mode="json")
    return JSONResponse(status_code=200, content={"code": 0, "message": "ok", "data": payload})
