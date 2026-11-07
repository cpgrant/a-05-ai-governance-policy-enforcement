
"""Identity-aware finance approval service.

Only trusted authentication boundaries may construct
and pass verified AgentIdentity objects.

Development prototype: the approval store remains in memory.
"""

from src.approvals.finance_workflow import FinanceApprovalWorkflow
from src.identity.jwt_verifier import AgentIdentity


class AuthenticatedFinanceService:
    APPROVER_ROLE = "finance_approver"

    def __init__(self):
        self.workflow = FinanceApprovalWorkflow()

    def request_payment(
        self,
        identity: AgentIdentity,
        amount: int | float,
        currency: str = "EUR",
    ) -> dict:
        return self.workflow.request_payment(
            agent_id=identity.agent_id,
            amount=amount,
            currency=currency,
        )

    def decide_approval(
        self,
        identity: AgentIdentity,
        approval_id: str,
        approve: bool,
    ) -> dict:
        if self.APPROVER_ROLE not in identity.roles:
            raise PermissionError(
                "Finance approver role required"
            )

        return self.workflow.decide_approval(
            approval_id=approval_id,
            approver_id=identity.agent_id,
            approve=approve,
        )

    def execute_approved_payment(
        self,
        identity: AgentIdentity,
        approval_id: str,
        amount: int | float,
        currency: str = "EUR",
    ) -> dict:
        return self.workflow.execute_approved_payment(
            approval_id=approval_id,
            agent_id=identity.agent_id,
            amount=amount,
            currency=currency,
        )
