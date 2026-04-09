from pathlib import Path


def test_create_task_persists_metadata_and_upload(client) -> None:
    response = client.post(
        "/api/v1/tasks",
        data={"template_id": "1", "rule_set_id": "2"},
        files={
            "file": (
                "sample.docx",
                b"fake-docx-content",
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
        },
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["code"] == 0
    assert payload["message"] == "ok"
    assert payload["data"]["status"] == "PENDING"
    assert payload["data"]["progress"] == 0

    task_no = payload["data"]["task_no"]
    saved_path = Path(client.app.state.storage_root) / "inputs" / task_no / "source.docx"
    assert saved_path.read_bytes() == b"fake-docx-content"

    detail_response = client.get(f"/api/v1/tasks/{task_no}")

    assert detail_response.status_code == 200
    assert detail_response.json()["data"] == payload["data"]


def test_create_task_rejects_non_docx_upload(client) -> None:
    response = client.post(
        "/api/v1/tasks",
        data={"template_id": "1", "rule_set_id": "2"},
        files={"file": ("sample.txt", b"plain-text", "text/plain")},
    )

    assert response.status_code == 400
    assert response.json() == {
        "code": 40001,
        "message": "only .docx files are supported",
        "data": None,
    }
