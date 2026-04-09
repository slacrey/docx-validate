from fastapi.testclient import TestClient

from docx_validate.main import create_app


def test_health_endpoint_returns_standard_ok_envelope() -> None:
    client = TestClient(create_app())

    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {
        "code": 0,
        "message": "ok",
        "data": {"status": "ok"},
    }
