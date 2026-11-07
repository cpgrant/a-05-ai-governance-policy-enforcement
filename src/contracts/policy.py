from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class PolicyDecision(str, Enum):
    PERMIT = "PERMIT"
    DENY = "DENY"
    REQUIRE_APPROVAL = "REQUIRE_APPROVAL"


class GovernanceRequest(BaseModel):
    request_id: UUID = Field(default_factory=uuid4)

    agent_id: str = Field(min_length=1)
    action: str = Field(min_length=1)
    resource: str = Field(min_length=1)

    context: dict[str, Any] = Field(default_factory=dict)


class GovernanceDecision(BaseModel):
    request_id: UUID
    decision: PolicyDecision

    policy_id: str
    policy_version: str

    reason: str
    obligations: list[str] = Field(default_factory=list)

    evaluated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
