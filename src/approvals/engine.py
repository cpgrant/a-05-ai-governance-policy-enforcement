
import json
import hashlib
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from threading import RLock
from typing import Any
from uuid import uuid4


def utcnow():
    return datetime.now(timezone.utc)


def operation_hash(operation: dict[str, Any]) -> str:
    payload = json.dumps(
        operation,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")

    return hashlib.sha256(payload).hexdigest()


@dataclass
class Approval:
    approval_id: str
    requester_id: str
    operation_digest: str
    created_at: datetime
    expires_at: datetime
    status: str = "PENDING"
    approver_id: str | None = None
    consumed_at: datetime | None = None


class ApprovalEngine:
    """
    Prototype in-memory approval state machine.

    Not a production approval service.
    Identity verification and policy authorization
    are responsibilities of trusted upstream services.
    """

    def __init__(self):
        self._approvals: dict[str, Approval] = {}
        self._lock = RLock()

    def create(
        self,
        requester_id: str,
        operation: dict[str, Any],
        ttl_seconds: int = 300,
    ) -> Approval:
        if not requester_id:
            raise ValueError("Requester identity required")

        if not isinstance(ttl_seconds, int) or not (
            1 <= ttl_seconds <= 3600
        ):
            raise ValueError("Invalid approval lifetime")

        if not isinstance(operation, dict) or not operation:
            raise ValueError("Operation required")

        now = utcnow()

        approval = Approval(
            approval_id=str(uuid4()),
            requester_id=requester_id,
            operation_digest=operation_hash(operation),
            created_at=now,
            expires_at=now + timedelta(seconds=ttl_seconds),
        )

        with self._lock:
            self._approvals[approval.approval_id] = approval

        return approval

    def get(self, approval_id: str) -> Approval:
        with self._lock:
            approval = self._approvals.get(approval_id)

            if approval is None:
                raise KeyError("Unknown approval")

            if (
                approval.status in {"PENDING", "APPROVED"}
                and utcnow() >= approval.expires_at
            ):
                approval.status = "EXPIRED"

            return Approval(**vars(approval))

    def decide(
        self,
        approval_id: str,
        approver_id: str,
        approve: bool,
    ) -> Approval:
        if not approver_id:
            raise PermissionError("Approver identity required")

        with self._lock:
            approval = self.get(approval_id)

            if approval.status != "PENDING":
                raise PermissionError(
                    "Approval is no longer pending"
                )

            if approver_id == approval.requester_id:
                raise PermissionError(
                    "Self-approval is prohibited"
                )

            stored = self._approvals[approval_id]
            stored.approver_id = approver_id
            stored.status = (
                "APPROVED" if approve else "REJECTED"
            )

            return Approval(**vars(stored))

    def consume(
        self,
        approval_id: str,
        requester_id: str,
        operation: dict[str, Any],
    ) -> bool:
        """
        Atomically consume a matching approval once.

        Caller must independently verify that the
        operation remains permitted by current policy.
        """

        with self._lock:
            approval = self.get(approval_id)

            if approval.status != "APPROVED":
                return False

            if approval.requester_id != requester_id:
                return False

            if approval.operation_digest != operation_hash(
                operation
            ):
                return False

            stored = self._approvals[approval_id]
            stored.status = "CONSUMED"
            stored.consumed_at = utcnow()

            return True
