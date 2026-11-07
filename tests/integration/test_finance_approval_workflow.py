
import pytest

from src.approvals.finance_workflow import (
    FinanceApprovalWorkflow,
)
from src.contracts.policy import (
    GovernanceDecision,
    PolicyDecision,
)


@pytest.fixture
def workflow():
    return FinanceApprovalWorkflow()


def approve_payment(workflow, amount=12000):
    request = workflow.request_payment(
        "finance-agent", amount
    )

    assert request["status"] == "PENDING_APPROVAL"

    approval_id = request["approval_id"]

    decision = workflow.decide_approval(
        approval_id,
        "finance-manager",
        True,
    )

    assert decision["status"] == "APPROVED"

    return approval_id


def test_small_payment_executes_automatically(workflow):
    result = workflow.request_payment(
        "finance-agent", 2000
    )

    assert result["status"] == "EXECUTED"
    assert result["executed"] is True
    assert result["result"]["status"] == "simulated"


def test_large_payment_requires_approval(workflow):
    result = workflow.request_payment(
        "finance-agent", 12000
    )

    assert result["status"] == "PENDING_APPROVAL"
    assert result["executed"] is False
    assert result["approval_id"]


def test_payment_above_limit_denied(workflow):
    result = workflow.request_payment(
        "finance-agent", 60000
    )

    assert result["status"] == "DENIED"
    assert result["executed"] is False


def test_approved_payment_executes(workflow):
    approval_id = approve_payment(workflow)

    result = workflow.execute_approved_payment(
        approval_id,
        "finance-agent",
        12000,
    )

    assert result["status"] == "EXECUTED"
    assert result["executed"] is True
    assert result["result"]["amount"] == 12000


def test_approval_cannot_be_reused(workflow):
    approval_id = approve_payment(workflow)

    first = workflow.execute_approved_payment(
        approval_id, "finance-agent", 12000
    )

    second = workflow.execute_approved_payment(
        approval_id, "finance-agent", 12000
    )

    assert first["executed"] is True
    assert second["executed"] is False


def test_changed_amount_blocked(workflow):
    approval_id = approve_payment(workflow)

    result = workflow.execute_approved_payment(
        approval_id,
        "finance-agent",
        25000,
    )

    assert result["executed"] is False


def test_wrong_agent_blocked(workflow):
    approval_id = approve_payment(workflow)

    result = workflow.execute_approved_payment(
        approval_id,
        "another-agent",
        12000,
    )

    assert result["executed"] is False


def test_rejected_payment_blocked(workflow):
    request = workflow.request_payment(
        "finance-agent", 12000
    )

    workflow.decide_approval(
        request["approval_id"],
        "finance-manager",
        False,
    )

    result = workflow.execute_approved_payment(
        request["approval_id"],
        "finance-agent",
        12000,
    )

    assert result["executed"] is False


def test_policy_denial_overrides_approval(
    workflow, monkeypatch
):
    approval_id = approve_payment(workflow)

    def deny_all(request):
        return GovernanceDecision(
            request_id=request.request_id,
            decision=PolicyDecision.DENY,
            policy_id="finance",
            policy_version="2.0",
            reason="Policy revoked",
        )

    monkeypatch.setattr(
        "src.approvals.finance_workflow.evaluate_policy",
        deny_all,
    )

    result = workflow.execute_approved_payment(
        approval_id,
        "finance-agent",
        12000,
    )

    assert result["status"] == "DENIED"
    assert result["executed"] is False


def test_self_approval_blocked(workflow):
    request = workflow.request_payment(
        "finance-agent", 12000
    )

    with pytest.raises(PermissionError):
        workflow.decide_approval(
            request["approval_id"],
            "finance-agent",
            True,
        )
