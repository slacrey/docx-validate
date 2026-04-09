from os import getenv
from pathlib import Path

from pydantic import BaseModel


class Settings(BaseModel):
    api_prefix: str = "/api/v1"
    database_url: str = "sqlite+pysqlite:///./docx_validate.db"
    storage_root: Path = Path("./var/storage")


def get_settings() -> Settings:
    return Settings(
        api_prefix=getenv("DOCX_VALIDATE_API_PREFIX", "/api/v1"),
        database_url=getenv(
            "DOCX_VALIDATE_DATABASE_URL",
            "sqlite+pysqlite:///./docx_validate.db",
        ),
        storage_root=Path(getenv("DOCX_VALIDATE_STORAGE_ROOT", "./var/storage")),
    )
