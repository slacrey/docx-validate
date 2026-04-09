def test_create_and_get_rule_set(client) -> None:
    create_response = client.post(
        "/api/v1/rules",
        json={
            "name": "default-rules",
            "version": "v1",
            "rule_json": {
                "style_rules": {"body": {"font": "宋体", "size_pt": 12}},
                "tolerance": {"ignore_whitespace": True},
            },
        },
    )

    assert create_response.status_code == 201
    payload = create_response.json()
    assert payload["code"] == 0
    assert payload["data"]["name"] == "default-rules"
    assert payload["data"]["version"] == "v1"
    assert payload["data"]["status"] == "ACTIVE"

    rule_set_id = payload["data"]["id"]
    get_response = client.get(f"/api/v1/rules/{rule_set_id}")

    assert get_response.status_code == 200
    assert get_response.json()["data"] == payload["data"]
