from src.contracts.policy import (
    GovernanceRequest,
    GovernanceDecision,
    PolicyDecision,
)


def test_governance_request():
    request = GovernanceRequest(
        agent_id="finance-agent",
        action="payment.create",
        resource="erp.payments",
        context={"amount": 25000, "currency": "EUR"},
    )

    assert request.agent_id == "finance-agent"
    assert request.context["amount"] == 25000


def test_policy_decision_values():
    assert PolicyDecision.PERMIT.value == "PERMIT"
    assert PolicyDecision.DENY.value == "DENY"
    assert PolicyDecision.REQUIRE_APPROVAL.value == "REQUIRE_APPROVAL"


def test_governance_decision():
    request = GovernanceRequest(
        agent_id="finance-agent",
        action="payment.create",
        resource="erp.payments",
    )

    decision = GovernanceDecision(
        request_id=request.request_id,
        decision=PolicyDecision.REQUIRE_APPROVAL,
        policy_id="FIN-003",
        policy_version="1.0",
        reason="Payment exceeds autonomous approval limit",
        obligations=["human_approval"],
    )

    assert decision.decision == PolicyDecision.REQUIRE_APPROVAL
    assert "human_approval" in decision.obligations
    assert decision.request_id == request.request_id
