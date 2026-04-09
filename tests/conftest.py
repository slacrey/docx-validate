import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client(tmp_path: pytest.TempPathFactory, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    database_path = tmp_path / "test.db"
    storage_root = tmp_path / "storage"

    monkeypatch.setenv(
        "DOCX_VALIDATE_DATABASE_URL",
        f"sqlite+pysqlite:///{database_path}",
    )
    monkeypatch.setenv("DOCX_VALIDATE_STORAGE_ROOT", str(storage_root))

    from docx_validate.main import create_app

    return TestClient(create_app())
