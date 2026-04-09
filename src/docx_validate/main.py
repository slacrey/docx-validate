from fastapi import FastAPI

from docx_validate.api import api_router
from docx_validate.config import get_settings
from docx_validate.db.base import Base
from docx_validate.db.session import create_session_factory
from docx_validate import models as _models


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title="docx-validate")
    session_factory = create_session_factory(settings.database_url)
    engine = session_factory.kw["bind"]
    Base.metadata.create_all(bind=engine)
    settings.storage_root.mkdir(parents=True, exist_ok=True)
    app.state.session_factory = session_factory
    app.state.storage_root = settings.storage_root
    app.include_router(api_router, prefix=settings.api_prefix)
    return app


app = create_app()
