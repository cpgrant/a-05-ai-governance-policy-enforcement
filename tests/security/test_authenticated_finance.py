
import pytest

from src.approvals.authenticated_finance import (
    AuthenticatedFinanceService,
)
from src.identity.jwt_verifier import AgentIdentity


def identity(agent_id, roles):
    return AgentIdentity(
        agent_id=agent_id,
        roles=tuple(roles),
        issuer="ai-a05-dev-issuer",
        token_id="test-token",
    )


@pytest.fixture
def service():
    return AuthenticatedFinanceService()


@pytest.fixture
def requester():
    return identity("finance-agent", ["finance"])


@pytest.fixture
def manager():
    return identity(
        "finance-manager",
        ["finance_approver"],
    )


def test_finance_manager_can_approve(
    service, requester, manager
):
    request = service.request_payment(
        requester, 12000
    )

    result = service.decide_approval(
        manager,
        request["approval_id"],
        True,
    )

    assert result["status"] == "APPROVED"


def test_ordinary_agent_cannot_approve(
    service, requester
):
    request = service.request_payment(
        requester, 12000
    )

    with pytest.raises(PermissionError):
        service.decide_approval(
            requester,
            request["approval_id"],
            True,
        )


def test_unprivileged_manager_cannot_approve(
    service, requester
):
    request = service.request_payment(
        requester, 12000
    )

    unprivileged = identity(
        "finance-manager",
        ["reader"],
    )

    with pytest.raises(PermissionError):
        service.decide_approval(
            unprivileged,
            request["approval_id"],
            True,
        )


def test_authorized_approval_executes_simulation(
    service, requester, manager
):
    request = service.request_payment(
        requester, 12000
    )

    service.decide_approval(
        manager,
        request["approval_id"],
        True,
    )

    result = service.execute_approved_payment(
        requester,
        request["approval_id"],
        12000,
    )

    assert result["executed"] is True
    assert result["result"]["status"] == "simulated"


def test_other_agent_cannot_consume_approval(
    service, requester, manager
):
    request = service.request_payment(
        requester, 12000
    )

    service.decide_approval(
        manager,
        request["approval_id"],
        True,
    )

    other = identity("other-agent", ["finance"])

    result = service.execute_approved_payment(
        other,
        request["approval_id"],
        12000,
    )

    assert result["executed"] is False


def test_privileged_requester_cannot_self_approve(
    service
):
    privileged = identity(
        "finance-agent",
        ["finance", "finance_approver"],
    )

    request = service.request_payment(
        privileged, 12000
    )

    with pytest.raises(
        PermissionError,
        match="Self-approval",
    ):
        service.decide_approval(
            privileged,
            request["approval_id"],
            True,
        )
