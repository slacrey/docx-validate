from fastapi import APIRouter, Depends, File, Form, Request, UploadFile
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from docx_validate.api.deps import get_db
from docx_validate.repositories.task_repository import TaskRepository
from docx_validate.schemas.task import TaskRead
from docx_validate.services.storage import build_storage
from docx_validate.services.task_service import TaskService


router = APIRouter(prefix="/tasks", tags=["tasks"])


def _error_response(message: str, code: int, status_code: int) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={"code": code, "message": message, "data": None},
    )


@router.post("")
def create_task(
    request: Request,
    template_id: int = Form(...),
    rule_set_id: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> JSONResponse:
    if not file.filename or not file.filename.lower().endswith(".docx"):
        return _error_response(
            "only .docx files are supported",
            code=40001,
            status_code=400,
        )

    storage = build_storage(request)
    service = TaskService(TaskRepository(db), storage)
    task = service.create_task(
        template_id=template_id,
        rule_set_id=rule_set_id,
        filename=file.filename,
        content=file.file.read(),
    )
    payload = TaskRead.model_validate(task).model_dump(mode="json")
    return JSONResponse(
        status_code=201,
        content={"code": 0, "message": "ok", "data": payload},
    )


@router.get("/{task_no}")
def get_task(task_no: str, db: Session = Depends(get_db)) -> JSONResponse:
    task = TaskRepository(db).get_by_task_no(task_no)
    if task is None:
        return _error_response("task not found", code=40404, status_code=404)

    payload = TaskRead.model_validate(task).model_dump(mode="json")
    return JSONResponse(status_code=200, content={"code": 0, "message": "ok", "data": payload})
