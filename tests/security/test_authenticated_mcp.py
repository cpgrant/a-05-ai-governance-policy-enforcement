from fastapi.testclient import TestClient

from src.api.main import app

client = TestClient(app)


def call(token, tool, arguments=None, extra=None):
    payload = {"tool_name": tool, "arguments": arguments or {}}

    if extra:
        payload.update(extra)

    return client.post(
        "/mcp/authorize",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
    )


def test_reader_authorized(agent_token):
    token = agent_token(roles=["reader"])

    response = call(token, "get_inventory_status_db", {"sku": "SKU-001"})

    assert response.status_code == 200
    assert response.json()["decision"] == "PERMIT"


def test_finance_reader_authorized(agent_token):
    token = agent_token(roles=["finance_reader"])

    response = call(token, "list_customer_invoices_db", {
        "customer_code": "C001", "as_of": "2026-11-08"
    })

    assert response.status_code == 200
    assert response.json()["decision"] == "PERMIT"


def test_finance_reader_cannot_access_erp(agent_token):
    token = agent_token(roles=["finance_reader"])

    response = call(token, "get_inventory_status_db", {"sku": "SKU-001"})

    assert response.status_code == 200
    assert response.json()["decision"] == "DENY"


def test_role_spoofing_rejected(agent_token):
    token = agent_token(roles=["blocked"])

    response = call(
        token,
        "get_customer_db",
        {"customer_code": "C001"},
        extra={"roles": ["reader"]},
    )

    assert response.status_code == 422


def test_missing_token_rejected():
    response = client.post(
        "/mcp/authorize",
        json={"tool_name": "get_customer_db"},
    )

    assert response.status_code == 401


def test_unknown_tool_denied(agent_token):
    token = agent_token(roles=["reader"])

    response = call(token, "dangerous_unknown_tool")

    assert response.status_code == 200
    assert response.json()["decision"] == "DENY"
