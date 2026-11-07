import json

import pytest

from src.audit.recorder import AuditRecorder
from src.contracts.policy import (
    GovernanceRequest,
    PolicyDecision,
)
from src.enforcement.pep import PolicyEnforcementPoint


def payment(amount):
    return GovernanceRequest(
        agent_id="finance-agent",
        action="payment.create",
        resource="erp.payments",
        context={"amount": amount, "currency": "EUR"},
    )


def events(path):
    return [
        json.loads(line)
        for line in path.read_text().splitlines()
    ]


def test_permitted_action_is_audited(tmp_path):
    path = tmp_path / "audit.jsonl"
    pep = PolicyEnforcementPoint(audit=AuditRecorder(path))

    result = pep.execute(
        payment(2500),
        lambda: {"status": "simulated"},
    )

    assert result.executed
    assert [e["event_type"] for e in events(path)] == [
        "authorization", "execution"
    ]


def test_denied_action_is_audited(tmp_path):
    path = tmp_path / "audit.jsonl"
    called = []

    result = PolicyEnforcementPoint(
        audit=AuditRecorder(path)
    ).execute(
        payment(75000),
        lambda: called.append(True),
    )

    assert not result.executed
    assert called == []
    assert len(events(path)) == 1
    assert events(path)[0]["decision"] == "DENY"


def test_approval_does_not_execute(tmp_path):
    path = tmp_path / "audit.jsonl"
    called = []

    result = PolicyEnforcementPoint(
        audit=AuditRecorder(path)
    ).execute(
        payment(25000),
        lambda: called.append(True),
    )

    assert not result.executed
    assert called == []
    assert events(path)[0]["decision"] == (
        "REQUIRE_APPROVAL"
    )


def test_audit_failure_blocks_execution():
    class BrokenAudit:
        def record(self, *args, **kwargs):
            raise OSError("Audit unavailable")

    called = []

    result = PolicyEnforcementPoint(
        audit=BrokenAudit()
    ).execute(
        payment(2500),
        lambda: called.append(True),
    )

    assert result.decision.decision == PolicyDecision.DENY
    assert not result.executed
    assert called == []


def test_execution_failure_is_audited(tmp_path):
    path = tmp_path / "audit.jsonl"

    def broken_tool():
        raise RuntimeError("Tool failed")

    with pytest.raises(RuntimeError, match="Tool failed"):
        PolicyEnforcementPoint(
            audit=AuditRecorder(path)
        ).execute(payment(2500), broken_tool)

    assert events(path)[1]["execution_status"] == "failed"
