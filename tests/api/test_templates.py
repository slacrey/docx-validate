from pathlib import Path


FIXTURES_DIR = Path(__file__).resolve().parent.parent / "fixtures" / "templates"


def test_create_template_uploads_docx_and_returns_metadata(client) -> None:
    with (FIXTURES_DIR / "basic-template.docx").open("rb") as handle:
        response = client.post(
            "/api/v1/templates",
            data={"name": "invoice", "version": "v1"},
            files={
                "file": (
                    "basic-template.docx",
                    handle.read(),
                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                )
            },
        )

    assert response.status_code == 201
    payload = response.json()
    assert payload["code"] == 0
    assert payload["message"] == "ok"
    assert payload["data"]["name"] == "invoice"
    assert payload["data"]["version"] == "v1"
    assert payload["data"]["status"] == "ACTIVE"
    assert payload["data"]["metadata_json"]["placeholders"] == [
        "customer_name",
        "order_no",
    ]

    template_id = payload["data"]["id"]
    saved_path = Path(client.app.state.storage_root) / payload["data"]["object_key"]
    assert saved_path.exists()

    detail_response = client.get(f"/api/v1/templates/{template_id}")

    assert detail_response.status_code == 200
    assert detail_response.json()["data"] == payload["data"]


def test_create_template_rejects_non_docx_upload(client) -> None:
    response = client.post(
        "/api/v1/templates",
        data={"name": "invoice", "version": "v1"},
        files={"file": ("sample.txt", b"plain-text", "text/plain")},
    )

    assert response.status_code == 400
    assert response.json() == {
        "code": 40001,
        "message": "only .docx files are supported",
        "data": None,
    }


def test_create_template_rejects_duplicate_identity_without_overwrite(client) -> None:
    with (FIXTURES_DIR / "basic-template.docx").open("rb") as handle:
        first = client.post(
            "/api/v1/templates",
            data={"name": "invoice", "version": "v1"},
            files={
                "file": (
                    "basic-template.docx",
                    handle.read(),
                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                )
            },
        )

    assert first.status_code == 201

    with (FIXTURES_DIR / "no-placeholders.docx").open("rb") as handle:
        response = client.post(
            "/api/v1/templates",
            data={"name": "invoice", "version": "v1"},
            files={
                "file": (
                    "no-placeholders.docx",
                    handle.read(),
                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                )
            },
        )

    assert response.status_code == 409
    assert response.json() == {
        "code": 40901,
        "message": "template identity already exists",
        "data": None,
    }


def test_create_template_rejects_duplicate_content_hash_for_other_identity(client) -> None:
    with (FIXTURES_DIR / "basic-template.docx").open("rb") as handle:
        first = client.post(
            "/api/v1/templates",
            data={"name": "invoice", "version": "v1"},
            files={
                "file": (
                    "basic-template.docx",
                    handle.read(),
                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                )
            },
        )

    assert first.status_code == 201

    with (FIXTURES_DIR / "basic-template.docx").open("rb") as handle:
        response = client.post(
            "/api/v1/templates",
            data={"name": "receipt", "version": "v1"},
            files={
                "file": (
                    "basic-template.docx",
                    handle.read(),
                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                )
            },
        )

    assert response.status_code == 409
    assert response.json() == {
        "code": 40902,
        "message": "template content already exists under another identity",
        "data": None,
    }


def test_create_template_overwrite_updates_same_record(client) -> None:
    with (FIXTURES_DIR / "basic-template.docx").open("rb") as handle:
        first = client.post(
            "/api/v1/templates",
            data={"name": "invoice", "version": "v1"},
            files={
                "file": (
                    "basic-template.docx",
                    handle.read(),
                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                )
            },
        )

    assert first.status_code == 201
    first_payload = first.json()["data"]

    with (FIXTURES_DIR / "no-placeholders.docx").open("rb") as handle:
        overwrite = client.post(
            "/api/v1/templates",
            data={"name": "invoice", "version": "v1", "overwrite": "true"},
            files={
                "file": (
                    "no-placeholders.docx",
                    handle.read(),
                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                )
            },
        )

    assert overwrite.status_code == 201
    overwrite_payload = overwrite.json()["data"]
    assert overwrite_payload["id"] == first_payload["id"]
    assert overwrite_payload["content_hash"] != first_payload["content_hash"]
    assert overwrite_payload["metadata_json"]["placeholders"] == []


def test_get_template_returns_not_found_for_missing_record(client) -> None:
    response = client.get("/api/v1/templates/999")

    assert response.status_code == 404
    assert response.json() == {
        "code": 40404,
        "message": "template not found",
        "data": None,
    }
