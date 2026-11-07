from dataclasses import dataclass
from typing import Any, Callable

from src.contracts.policy import (
    GovernanceRequest,
    GovernanceDecision,
    PolicyDecision,
)
from src.policy.opa_adapter import evaluate_policy
from src.audit.recorder import AuditRecorder


@dataclass
class EnforcementResult:
    executed: bool
    decision: GovernanceDecision
    result: Any = None


class PolicyEnforcementPoint:

    def __init__(
        self,
        evaluator: Callable[
            [GovernanceRequest], GovernanceDecision
        ] = evaluate_policy,
        audit: AuditRecorder | None = None,
    ):
        self.evaluator = evaluator
        self.audit = audit

    def _deny(self, request, reason):
        return GovernanceDecision(
            request_id=request.request_id,
            decision=PolicyDecision.DENY,
            policy_id="enforcement",
            policy_version="1.0",
            reason=reason,
        )

    def execute(
        self,
        request: GovernanceRequest,
        action: Callable[[], Any],
    ) -> EnforcementResult:

        try:
            decision = self.evaluator(request)

            if decision.request_id != request.request_id:
                raise ValueError("Decision request ID mismatch")

            if not isinstance(decision.decision, PolicyDecision):
                raise ValueError("Invalid decision")

        except Exception:
            decision = self._deny(
                request, "Authorization evaluation failed"
            )

        # Audit the authorization before execution.
        if self.audit is not None:
            try:
                self.audit.record(
                    request,
                    decision,
                    executed=False,
                    execution_status="evaluated",
                    event_type="authorization",
                )
            except Exception:
                return EnforcementResult(
                    executed=False,
                    decision=self._deny(
                        request,
                        "Required authorization audit failed",
                    ),
                )

        # Never execute without explicit permission.
        if (
            decision.decision != PolicyDecision.PERMIT
            or decision.obligations
        ):
            return EnforcementResult(
                executed=False,
                decision=decision,
            )

        try:
            result = action()
        except Exception:
            if self.audit is not None:
                self.audit.record(
                    request,
                    decision,
                    executed=True,
                    execution_status="failed",
                    event_type="execution",
                )
            raise

        if self.audit is not None:
            self.audit.record(
                request,
                decision,
                executed=True,
                execution_status="success",
                event_type="execution",
            )

        return EnforcementResult(
            executed=True,
            decision=decision,
            result=result,
        )
