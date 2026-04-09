from fastapi import APIRouter

from docx_validate.api.routes.health import router as health_router
from docx_validate.api.routes.rules import router as rules_router
from docx_validate.api.routes.tasks import router as tasks_router
from docx_validate.api.routes.templates import router as templates_router


api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(rules_router)
api_router.include_router(tasks_router)
api_router.include_router(templates_router)
