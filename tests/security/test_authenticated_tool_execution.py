from fastapi.testclient import TestClient

from src.api.main import app

client = TestClient(app)


def execute(token, amount=2500, extra=None):
    payload = {
        "tool_name": "finance.payment.create",
        "parameters": {
            "amount": amount,
            "currency": "EUR",
        },
    }

    if extra:
        payload.update(extra)

    return client.post(
        "/tools/execute",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
    )


def test_authenticated_finance_agent_executes(agent_token):
    response = execute(agent_token())

    assert response.status_code == 200
    assert response.json()["executed"] is True
    assert response.json()["agent_id"] == "finance-agent"
    assert response.json()["decision"] == "PERMIT"


def test_missing_token_rejected():
    response = client.post(
        "/tools/execute",
        json={
            "tool_name": "finance.payment.create",
            "parameters": {
                "amount": 2500,
                "currency": "EUR",
            },
        },
    )

    assert response.status_code == 401


def test_identity_spoofing_rejected(agent_token):
    response = execute(
        agent_token("unknown-agent"),
        extra={"agent_id": "finance-agent"},
    )

    assert response.status_code == 422


def test_unknown_agent_cannot_execute(agent_token):
    response = execute(agent_token("unknown-agent"))

    assert response.status_code == 200
    assert response.json()["executed"] is False
    assert response.json()["decision"] == "DENY"


def test_large_payment_blocked(agent_token):
    response = execute(agent_token(), amount=75000)

    assert response.status_code == 200
    assert response.json()["executed"] is False
    assert response.json()["decision"] == "DENY"


def test_approval_required_blocks_execution(agent_token):
    response = execute(agent_token(), amount=25000)

    assert response.status_code == 200
    assert response.json()["executed"] is False
    assert response.json()["decision"] == "REQUIRE_APPROVAL"
