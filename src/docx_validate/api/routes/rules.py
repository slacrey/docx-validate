from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from docx_validate.api.deps import get_db
from docx_validate.models.rule_set import DetectionRuleSet
from docx_validate.repositories.rule_set_repository import RuleSetRepository
from docx_validate.schemas.rule_set import RuleSetCreate, RuleSetRead


router = APIRouter(prefix="/rules", tags=["rules"])


def _error_response(message: str, code: int, status_code: int) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={"code": code, "message": message, "data": None},
    )


@router.post("")
def create_rule_set(
    payload: RuleSetCreate,
    db: Session = Depends(get_db),
) -> JSONResponse:
    repository = RuleSetRepository(db)
    rule_set = repository.create(
        DetectionRuleSet(
            name=payload.name,
            version=payload.version,
            rule_json=payload.rule_json,
        )
    )
    content = RuleSetRead.model_validate(rule_set).model_dump(mode="json")
    return JSONResponse(status_code=201, content={"code": 0, "message": "ok", "data": content})


@router.get("/{rule_set_id}")
def get_rule_set(rule_set_id: int, db: Session = Depends(get_db)) -> JSONResponse:
    rule_set = RuleSetRepository(db).get(rule_set_id)
    if rule_set is None:
        return _error_response("rule set not found", code=40404, status_code=404)

    content = RuleSetRead.model_validate(rule_set).model_dump(mode="json")
    return JSONResponse(status_code=200, content={"code": 0, "message": "ok", "data": content})
