import json
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field

from src.contracts.policy import (
    GovernanceRequest,
    GovernanceDecision,
)

class AuditEvent(BaseModel):
    event_id: str = Field(
        default_factory=lambda: str(uuid4())
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    request_id: str
    agent_id: str
    action: str
    resource: str
    decision: str
    policy_id: str
    policy_version: str
    reason: str
    executed: bool
    execution_status: str
    event_type: str = "execution"


class AuditRecorder:
    def __init__(self, path: Path):
        self.path = Path(path)
        self._lock = Lock()

    def record(
        self,
        request: GovernanceRequest,
        decision: GovernanceDecision,
        executed: bool,
        execution_status: str,
        event_type: str = "execution",
    ) -> AuditEvent:

        event = AuditEvent(
            request_id=str(request.request_id),
            agent_id=request.agent_id,
            action=request.action,
            resource=request.resource,
            decision=decision.decision.value,
            policy_id=decision.policy_id,
            policy_version=decision.policy_version,
            reason=decision.reason,
            executed=executed,
            execution_status=execution_status,
            event_type=event_type,
        )

        with self._lock:
            self.path.parent.mkdir(
                parents=True, exist_ok=True
            )
            with self.path.open("a", encoding="utf-8") as f:
                f.write(event.model_dump_json() + "\n")
                f.flush()

        return event
