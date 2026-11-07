from fastapi.testclient import TestClient

from src.api.main import app

client = TestClient(app)


def evaluate(agent_token, agent, amount):
    response = client.post(
        "/governance/evaluate",
        json={
            "agent_id": agent,
            "action": "payment.create",
            "resource": "erp.payments",
            "context": {
                "amount": amount,
                "currency": "EUR",
            },
        },
        headers={
            "Authorization": (
                f"Bearer {agent_token(agent)}"
            )
        },
    )

    assert response.status_code == 200
    return response.json()


def test_health():
    response = client.get("/health")
    assert response.status_code == 200


def test_permit(agent_token):
    result = evaluate(agent_token, "finance-agent", 2500)
    assert result["decision"] == "PERMIT"


def test_require_approval(agent_token):
    result = evaluate(agent_token, "finance-agent", 25000)
    assert result["decision"] == "REQUIRE_APPROVAL"
    assert "human_approval" in result["obligations"]


def test_deny_large_payment(agent_token):
    result = evaluate(agent_token, "finance-agent", 75000)
    assert result["decision"] == "DENY"


def test_deny_unknown_agent(agent_token):
    result = evaluate(agent_token, "unknown-agent", 500)
    assert result["decision"] == "DENY"
