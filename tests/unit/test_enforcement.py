import pytest

from src.contracts.policy import (
    GovernanceRequest,
    GovernanceDecision,
    PolicyDecision,
)
from src.enforcement.pep import PolicyEnforcementPoint


def request(amount=2500):
    return GovernanceRequest(
        agent_id="finance-agent",
        action="payment.create",
        resource="erp.payments",
        context={
            "amount": amount,
            "currency": "EUR",
        },
    )


def test_authorized_execution():
    executed = []

    def payment_tool():
        executed.append(True)
        return {"payment": "simulated"}

    result = PolicyEnforcementPoint().execute(
        request(2500),
        payment_tool,
    )

    assert result.executed is True
    assert len(executed) == 1


def test_denied_action_never_executes():
    executed = []

    result = PolicyEnforcementPoint().execute(
        request(75000),
        lambda: executed.append(True),
    )

    assert result.executed is False
    assert result.decision.decision == PolicyDecision.DENY
    assert executed == []


def test_approval_required_never_executes():
    executed = []

    result = PolicyEnforcementPoint().execute(
        request(25000),
        lambda: executed.append(True),
    )

    assert result.executed is False
    assert result.decision.decision == PolicyDecision.REQUIRE_APPROVAL
    assert executed == []


def test_policy_failure_fails_closed():
    executed = []

    def broken_evaluator(_):
        raise ConnectionError("OPA unavailable")

    pep = PolicyEnforcementPoint(
        evaluator=broken_evaluator,
    )

    result = pep.execute(
        request(),
        lambda: executed.append(True),
    )

    assert result.executed is False
    assert result.decision.decision == PolicyDecision.DENY
    assert executed == []


def test_mismatched_decision_request_denied():
    executed = []

    def incorrect_evaluator(req):
        other = request()

        return GovernanceDecision(
            request_id=other.request_id,
            decision=PolicyDecision.PERMIT,
            policy_id="test",
            policy_version="1",
            reason="Test permit",
        )

    result = PolicyEnforcementPoint(
        evaluator=incorrect_evaluator,
    ).execute(
        request(),
        lambda: executed.append(True),
    )

    assert result.executed is False
    assert executed == []


def test_execution_failure_propagates():
    def failing_tool():
        raise RuntimeError("Tool failure")

    with pytest.raises(RuntimeError, match="Tool failure"):
        PolicyEnforcementPoint().execute(
            request(2500),
            failing_tool,
        )
