
import pytest
from fastapi.testclient import TestClient

from src.api import main as api
from src.approvals.authenticated_finance import (
    AuthenticatedFinanceService,
)


@pytest.fixture
def client(monkeypatch):
    # Isolate approval state between tests.
    monkeypatch.setattr(
        api,
        "finance_service",
        AuthenticatedFinanceService(),
    )
    return TestClient(api.app)


def auth(token):
    return {"Authorization": f"Bearer {token}"}


def request_payment(client, token, amount=12000):
    return client.post(
        "/finance/payments/request",
        json={"amount": amount, "currency": "EUR"},
        headers=auth(token),
    )


def test_missing_authentication_rejected(client):
    response = client.post(
        "/finance/payments/request",
        json={"amount": 12000},
    )

    assert response.status_code == 401


def test_automatic_payment(client, agent_token):
    token = agent_token(
        subject="finance-agent",
        roles=["finance"],
    )

    response = request_payment(
        client, token, 2000
    )

    assert response.status_code == 200
    assert response.json()["executed"] is True
    assert response.json()["result"]["status"] == "simulated"


def test_approval_required(client, agent_token):
    token = agent_token(
        subject="finance-agent",
        roles=["finance"],
    )

    response = request_payment(
        client, token, 12000
    )

    assert response.status_code == 200
    assert response.json()["status"] == "PENDING_APPROVAL"
    assert response.json()["executed"] is False


def test_unprivileged_approver_rejected(
    client, agent_token
):
    requester = agent_token(
        subject="finance-agent",
        roles=["finance"],
    )

    approval = request_payment(
        client, requester
    ).json()["approval_id"]

    unprivileged = agent_token(
        subject="ordinary-agent",
        roles=["reader"],
    )

    response = client.post(
        f"/finance/approvals/{approval}/decide",
        json={"approve": True},
        headers=auth(unprivileged),
    )

    assert response.status_code == 403


def test_authenticated_approval_and_execution(
    client, agent_token
):
    requester = agent_token(
        subject="finance-agent",
        roles=["finance"],
    )

    manager = agent_token(
        subject="finance-manager",
        roles=["finance_approver"],
    )

    payment = request_payment(
        client, requester
    )

    assert payment.status_code == 200

    approval_id = payment.json()["approval_id"]

    decision = client.post(
        f"/finance/approvals/{approval_id}/decide",
        json={"approve": True},
        headers=auth(manager),
    )

    assert decision.status_code == 200
    assert decision.json()["status"] == "APPROVED"

    execution = client.post(
        f"/finance/approvals/{approval_id}/execute",
        json={"amount": 12000, "currency": "EUR"},
        headers=auth(requester),
    )

    assert execution.status_code == 200
    assert execution.json()["executed"] is True
    assert execution.json()["result"]["status"] == "simulated"

    replay = client.post(
        f"/finance/approvals/{approval_id}/execute",
        json={"amount": 12000, "currency": "EUR"},
        headers=auth(requester),
    )

    assert replay.status_code == 200
    assert replay.json()["executed"] is False


def test_role_spoofing_rejected(
    client, agent_token
):
    requester = agent_token(
        subject="finance-agent",
        roles=["finance"],
    )

    approval_id = request_payment(
        client, requester
    ).json()["approval_id"]

    attacker = agent_token(
        subject="ordinary-agent",
        roles=["reader"],
    )

    response = client.post(
        f"/finance/approvals/{approval_id}/decide",
        json={
            "approve": True,
            "roles": ["finance_approver"],
        },
        headers=auth(attacker),
    )

    assert response.status_code == 422
