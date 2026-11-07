
"""OPA-governed finance approval workflow.

Local prototype using simulated payments only.
"""

from typing import Any

from src.approvals.engine import ApprovalEngine
from src.contracts.policy import (
    GovernanceRequest,
    PolicyDecision,
)
from src.policy.opa_adapter import evaluate_policy
from src.tools.payment import simulated_payment


class FinanceApprovalWorkflow:
    def __init__(self):
        self.approvals = ApprovalEngine()

    @staticmethod
    def _operation(
        amount: int | float,
        currency: str,
    ) -> dict[str, Any]:
        return {
            "action": "payment.create",
            "resource": "erp.payments",
            "amount": amount,
            "currency": currency,
        }

    @staticmethod
    def _evaluate(
        agent_id: str,
        operation: dict[str, Any],
    ):
        request = GovernanceRequest(
            agent_id=agent_id,
            action=operation["action"],
            resource=operation["resource"],
            context={
                "amount": operation["amount"],
                "currency": operation["currency"],
            },
        )

        return evaluate_policy(request)

    def request_payment(
        self,
        agent_id: str,
        amount: int | float,
        currency: str = "EUR",
    ) -> dict[str, Any]:
        operation = self._operation(amount, currency)

        decision = self._evaluate(agent_id, operation)

        if decision.decision == PolicyDecision.DENY:
            return {
                "status": "DENIED",
                "executed": False,
                "reason": decision.reason,
            }

        if decision.decision == PolicyDecision.PERMIT:
            result = simulated_payment(
                {
                    "amount": amount,
                    "currency": currency,
                }
            )

            return {
                "status": "EXECUTED",
                "executed": True,
                "result": result,
            }

        if decision.decision != PolicyDecision.REQUIRE_APPROVAL:
            return {
                "status": "DENIED",
                "executed": False,
                "reason": "Unknown policy decision",
            }

        approval = self.approvals.create(
            requester_id=agent_id,
            operation=operation,
        )

        return {
            "status": "PENDING_APPROVAL",
            "executed": False,
            "approval_id": approval.approval_id,
            "expires_at": approval.expires_at.isoformat(),
        }

    def decide_approval(
        self,
        approval_id: str,
        approver_id: str,
        approve: bool,
    ) -> dict[str, Any]:
        approval = self.approvals.decide(
            approval_id=approval_id,
            approver_id=approver_id,
            approve=approve,
        )

        return {
            "approval_id": approval.approval_id,
            "status": approval.status,
            "approver_id": approval.approver_id,
        }

    def execute_approved_payment(
        self,
        approval_id: str,
        agent_id: str,
        amount: int | float,
        currency: str = "EUR",
    ) -> dict[str, Any]:
        operation = self._operation(amount, currency)

        # Re-evaluate the current policy.
        decision = self._evaluate(agent_id, operation)

        # An approval is valid only while the current policy
        # still requires approval for this operation.
        if decision.decision != PolicyDecision.REQUIRE_APPROVAL:
            return {
                "status": "DENIED",
                "executed": False,
                "reason": "Current policy does not authorize approval-based execution",
            }

        # Checks requester, exact operation, expiry
        # and one-time use.
        authorized = self.approvals.consume(
            approval_id=approval_id,
            requester_id=agent_id,
            operation=operation,
        )

        if not authorized:
            return {
                "status": "DENIED",
                "executed": False,
                "reason": "Approval invalid, expired or consumed",
            }

        # Simulated operation only.
        result = simulated_payment(
            {
                "amount": amount,
                "currency": currency,
            }
        )

        return {
            "status": "EXECUTED",
            "executed": True,
            "approval_id": approval_id,
            "result": result,
        }
